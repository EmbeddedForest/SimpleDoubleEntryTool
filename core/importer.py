#------------------------------------------------------------------------------
# File:
#   core/importer.py
#
# Description:
#   Reads a bank/card CSV export and turns it into a list of normalised,
#   uniquely-hashed transactions, ready to be journalled.
#
#   This replaces the data-handling half of the old import_file.py. The GUI
#   concerns (file dropdown, "associated account" selection) stay in the
#   controller; everything here is pure and unit testable. Normalisation is
#   shared with the journal via core.normalize, and the intermediate tmp.csv
#   the original wrote (and never read back) is gone.
#------------------------------------------------------------------------------

import os
import hashlib
from dataclasses import dataclass

import pandas as pd

from core.normalize import normalize_date, normalize_amount, normalize_desc


class ImportStyleError(Exception):
    ''' Raised when a CSV matches no configured ImportFileStyle. '''


@dataclass
class ImportTransaction:
    ''' One normalised transaction from an import file. '''
    date:   str
    desc:   str
    amount: str   # canonical signed 2-decimal string
    txn_id: str   # stable md5 hash, unique within the import file


@dataclass
class ImportResult:
    ''' The outcome of importing one CSV. '''
    style:        str
    assoc_accts:  list          # candidate associated accounts for this style
    transactions: list          # list[ImportTransaction], date/desc sorted

    @property
    def count(self):
        return len(self.transactions)


def list_import_files(folder):
    ''' All CSV file names in the given folder. '''
    return [f for f in os.listdir(folder) if f.lower().endswith('.csv')]


def detect_style(config, columns):
    '''
    Return (style_name, style_cfg) for the first configured style whose
    date/desc/amount columns are all present, else raise ImportStyleError.
    '''
    for name, cfg in (config.get('ImportFileStyles') or {}).items():
        cols = (cfg.get('DateColName'), cfg.get('DescColName'),
                cfg.get('AmntColName'))
        if all(col in columns for col in cols):
            return name, cfg
    raise ImportStyleError('Import file does not match any known styles')


def _assign_hashes(records):
    '''
    Give each transaction a stable md5 hash. A running counter disambiguates
    back-to-back identical transactions (same date/desc/amount), matching the
    original scheme so existing journals keep the same TransactionIDs.
    '''
    hashes = []
    prev_key = None
    count = 0
    for r in records:
        key = (r['date'], r['desc'], r['amount'])
        count = count + 1 if key == prev_key else 0
        raw = f"{r['date']}{r['desc']}{r['amount']}{count}"
        hashes.append(hashlib.md5(raw.encode('utf-8')).hexdigest())
        prev_key = key
    return hashes


def load_transactions(file_path, config):
    '''
    Read file_path, auto-detect its style from config, and return an
    ImportResult of normalised, hashed, date/desc-sorted transactions.
    '''
    # index_col=False stops pandas from treating the first column as the index
    # when a row has more fields than headers - e.g. Chase checking exports add
    # a trailing comma, which would otherwise shift every column left.
    df = pd.read_csv(file_path, index_col=False)

    style, cfg = detect_style(config, list(df.columns))
    date_c = cfg['DateColName']
    desc_c = cfg['DescColName']
    amnt_c = cfg['AmntColName']
    negate = bool(cfg.get('AmntNegate'))
    skip_list = cfg.get('SkipStrings') or []
    assoc_accts = cfg.get('AssAccts') or []

    # Drop rows whose description matches any skip string (case-insensitive).
    for skip in skip_list:
        df = df[~df[desc_c].str.contains(skip, na=False, case=False)]

    # Normalise each surviving row.
    records = []
    for _, row in df.iterrows():
        value = row[amnt_c]
        if negate:
            value = -1 * value
        records.append({
            'date':   normalize_date(row[date_c]),
            'desc':   normalize_desc(row[desc_c]),
            'amount': normalize_amount(value),
        })

    # Stable order so the hash counter is deterministic across re-imports.
    records.sort(key=lambda r: (r['date'], r['desc']))

    hashes = _assign_hashes(records)
    transactions = [
        ImportTransaction(date=r['date'], desc=r['desc'],
                          amount=r['amount'], txn_id=h)
        for r, h in zip(records, hashes)
    ]
    return ImportResult(style=style, assoc_accts=assoc_accts,
                        transactions=transactions)
