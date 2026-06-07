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
#------------------------------------------------------------------------------

import pandas as pd

import constants as c
from core.models import Line, Entry
from core.normalize import normalize_date, normalize_amount, normalize_desc
from core.suggest import suggest_entry


class JournalNotFoundError(FileNotFoundError):
    ''' Raised when the journal CSV cannot be found on disk. '''


class Ledger:
    ''' File-backed, in-memory journal. '''

    SORT_COLS = [c.JRNL_DATE, c.JRNL_DSCRP, c.JRNL_ID, c.JRNL_LINE]

    def __init__(self, path=c.JOURNAL_FP):
        self.path = path
        self.df = None

    # -- load / save ------------------------------------------------------

    def load(self):
        try:
            df = pd.read_csv(self.path)
        except FileNotFoundError as e:
            raise JournalNotFoundError(self.path) from e

        self.df = self._sort(self._normalize_df(df))
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

    # -- queries ----------------------------------------------------------

    def transaction_exists(self, txn_id):
        self._ensure_loaded()
        return txn_id in self.df[c.JRNL_ID].values

    def history(self):
        ''' All past entries as list[Entry], oldest-first. '''
        self._ensure_loaded()
        entries = []
        if self.df.empty:
            return entries

        # sort=False preserves the date-sorted order so reversed(history)
        # yields the most recent entries first.
        for _, group in self.df.groupby(c.JRNL_ID, sort=False):
            group = group.sort_values(by=c.JRNL_LINE)
            lines = [self._row_to_line(row) for _, row in group.iterrows()]
            entries.append(Entry(lines))
        return entries

    def find_suggested_entry(self, entry: Entry):
        ''' Suggest a categorisation for the new transaction in entry[0]. '''
        return suggest_entry(self.history(), entry[0])

    # -- mutation ---------------------------------------------------------

    def add_entry(self, entry: Entry):
        ''' Append an entry to the in-memory journal. Call save() to persist. '''
        self._ensure_loaded()
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
