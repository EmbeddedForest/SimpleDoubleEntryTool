#------------------------------------------------------------------------------
# File:
#   core/ledger.py
#
# Description:
#   In-memory model of the journal. The original code re-read Journal.csv on
#   every existence check, suggestion and append - so a single "Start" press
#   re-scanned the whole file once per already-processed transaction (O(n^2)).
#   Ledger loads the file once into a DataFrame, answers all queries from
#   memory, and writes back only on save().
#
#   Derived views (the grouped Entry list, the set of TransactionIDs, and a
#   (desc, account) -> entry index) are built once and cached; any mutation
#   invalidates the caches so they rebuild lazily on next use. The index backs
#   classify(), a cheap exact/partial check used to colour the queue without
#   paying for fuzzy matching on every row.
#------------------------------------------------------------------------------

import pandas as pd

import constants as c
from core.models import Line, Entry
from core.normalize import normalize_date, normalize_amount, normalize_desc
from core.suggest import suggest_entry, EXACT, PARTIAL, NONE


class JournalNotFoundError(FileNotFoundError):
    ''' Raised when the journal CSV cannot be found on disk. '''


class Ledger:
    ''' File-backed, in-memory journal. '''

    SORT_COLS = [c.JRNL_DATE, c.JRNL_DSCRP, c.JRNL_ID, c.JRNL_LINE]

    def __init__(self, path=c.JOURNAL_FP):
        self.path = path
        self.df = None
        self._history = None      # cached list[Entry], oldest-first
        self._ids = None          # cached set of TransactionIDs
        self._index = None        # cached {(desc, acct_full): Entry} most-recent

    # -- load / save ------------------------------------------------------

    def load(self):
        try:
            df = pd.read_csv(self.path)
        except FileNotFoundError as e:
            raise JournalNotFoundError(self.path) from e

        self.df = self._sort(self._normalize_df(df))
        self._invalidate()
        return self

    def save(self):
        ''' Persist the in-memory journal back to disk. '''
        self._ensure_loaded()
        self.df.to_csv(self.path, index=False)

    def _ensure_loaded(self):
        if self.df is None:
            self.load()

    def _normalize_df(self, df):
        if df.empty:
            return df
        df[c.JRNL_DATE]   = df[c.JRNL_DATE].apply(normalize_date)
        df[c.JRNL_AMOUNT] = df[c.JRNL_AMOUNT].apply(normalize_amount)
        df[c.JRNL_DSCRP]  = df[c.JRNL_DSCRP].fillna('').apply(normalize_desc)
        df[c.JRNL_MEMO]   = df[c.JRNL_MEMO].fillna('')
        return df

    def _sort(self, df):
        if df.empty:
            return df
        return df.sort_values(by=self.SORT_COLS).reset_index(drop=True)

    # -- derived-view cache ----------------------------------------------

    def _invalidate(self):
        self._history = self._ids = self._index = None

    # Column order used for the fast itertuples scan below.
    _SCAN_COLS = [c.JRNL_LINE, c.JRNL_DATE, c.JRNL_ID, c.JRNL_DSCRP,
                  c.JRNL_MEMO, c.JRNL_ACCT_NAME_F, c.JRNL_ACCT_NAME, c.JRNL_AMOUNT]

    def _ensure_caches(self):
        ''' Build the grouped history, id set and match index in one pass. '''
        self._ensure_loaded()
        if self._history is not None:
            return

        self._history, self._ids, self._index = [], set(), {}
        if self.df.empty:
            return

        # The df is sorted by (date, desc, id, line), so all lines of an entry
        # are contiguous and line-ordered. A single itertuples scan that breaks
        # on TransactionID change is far faster than groupby + iterrows, which
        # matters because the caches rebuild after every add/edit.
        current_id = None
        lines = []
        for (_ln, date, txn_id, desc, memo, acct_f, acct_s, amount) in \
                self.df[self._SCAN_COLS].itertuples(index=False, name=None):
            txn_id = str(txn_id)
            if lines and txn_id != current_id:
                self._cache_entry(lines)
                lines = []
            current_id = txn_id
            lines.append(Line(
                date=str(date), txn_id=txn_id, desc=str(desc),
                memo='' if pd.isna(memo) else str(memo),
                acct_full=str(acct_f), acct_short=str(acct_s),
                amount=str(amount),          # df amounts are already canonical
            ))
        if lines:
            self._cache_entry(lines)

    def _cache_entry(self, lines):
        entry = Entry(lines)
        first = entry[0]
        self._history.append(entry)
        self._ids.add(first.txn_id)
        self._index[(first.desc, first.acct_full)] = entry

    # -- queries ----------------------------------------------------------

    def transaction_exists(self, txn_id):
        self._ensure_caches()
        return txn_id in self._ids

    def history(self):
        ''' All past entries as list[Entry], oldest-first (cached). '''
        self._ensure_caches()
        return self._history

    def classify(self, first_line):
        '''
        Fast suggestion tier for the new transaction in first_line, using only
        the (desc, account) index - EXACT if a same-amount match exists,
        PARTIAL if same desc+account but different amount, else NONE. Cheap
        enough to run for every queue row; no fuzzy matching (that only runs in
        find_suggested_entry when a row is actually opened).
        '''
        self._ensure_caches()
        entry = self._index.get((first_line.desc, first_line.acct_full))
        if entry is None:
            return NONE
        if normalize_amount(entry[0].amount) == normalize_amount(first_line.amount):
            return EXACT
        return PARTIAL

    def find_suggested_entry(self, entry: Entry):
        ''' Full (incl. fuzzy) suggestion for the transaction in entry[0]. '''
        return suggest_entry(self.history(), entry[0])

    def get_entry(self, txn_id):
        ''' The stored Entry for a TransactionID, or None if not present. '''
        self._ensure_loaded()
        group = self.df[self.df[c.JRNL_ID] == txn_id].sort_values(by=c.JRNL_LINE)
        if group.empty:
            return None
        return Entry([self._row_to_line(row) for _, row in group.iterrows()])

    # -- mutation ---------------------------------------------------------

    def add_entry(self, entry: Entry):
        '''
        Insert (or replace) an entry in the in-memory journal, keyed by
        TransactionID. Any existing rows for the same id are dropped first, so
        the journal can never hold two entries with the same id - an accidental
        double-add overwrites rather than duplicates. Call save() to persist.
        '''
        self._ensure_loaded()
        txn_id = entry[0].txn_id
        self.df = self.df[self.df[c.JRNL_ID] != txn_id]    # upsert by id
        rows = []
        for line_num, line in enumerate(entry):
            rows.append({
                c.JRNL_LINE:        line_num,
                c.JRNL_DATE:        line.date,
                c.JRNL_ID:          line.txn_id,
                c.JRNL_DSCRP:       line.desc,
                c.JRNL_MEMO:        line.memo,
                c.JRNL_ACCT_NAME_F: line.acct_full,
                c.JRNL_ACCT_NAME:   line.acct_short,
                c.JRNL_AMOUNT:      normalize_amount(line.amount) if line.amount != '' else '',
            })
        new = pd.DataFrame(rows, columns=self.df.columns)
        self.df = self._sort(pd.concat([self.df, new], ignore_index=True))
        self._invalidate()

    def delete_entry(self, txn_id):
        ''' Remove every line of the entry with this TransactionID. '''
        self._ensure_loaded()
        self.df = self.df[self.df[c.JRNL_ID] != txn_id].reset_index(drop=True)
        self._invalidate()

    def replace_entry(self, entry: Entry):
        ''' Replace the stored entry sharing entry[0]'s TransactionID with the
            given (edited) entry. add_entry already upserts by id, so this is
            just an alias kept for intent at call sites. Call save() to persist. '''
        self.add_entry(entry)

    # -- helpers ----------------------------------------------------------

    def _row_to_line(self, row):
        memo = row[c.JRNL_MEMO]
        return Line(
            date       = str(row[c.JRNL_DATE]),
            txn_id     = str(row[c.JRNL_ID]),
            desc       = str(row[c.JRNL_DSCRP]),
            memo       = '' if pd.isna(memo) else str(memo),
            acct_full  = str(row[c.JRNL_ACCT_NAME_F]),
            acct_short = str(row[c.JRNL_ACCT_NAME]),
            amount     = normalize_amount(row[c.JRNL_AMOUNT]),
        )
