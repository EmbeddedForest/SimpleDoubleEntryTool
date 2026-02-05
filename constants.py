#------------------------------------------------------------------------------
# File:
#   app.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   Constants used across all project files
#
#------------------------------------------------------------------------------

# Helpful return flags
GOOD = 'good'
BAD  = 'bad'

# Common file names and paths
ACCOUNTS_FP  = 'Accounts.csv'
JOURNAL_FP   = 'Journal.csv'
DATA_FOLDER  = 'Data/'
TEMP_FILE = 'tmp.csv'
CONFIG_FILE = 'config.yaml'

# Journal.csv column headers
JRNL_LINE        = 'Line'
JRNL_DATE        = 'Date'
JRNL_ID          = 'TransactionID'
JRNL_DSCRP       = 'Description'
JRNL_MEMO        = 'Memo'
JRNL_ACCT_NAME_F = 'Full Account Name'
JRNL_ACCT_NAME   = 'Account Name'
JRNL_AMOUNT      = 'Amount Num.'

# WHO Enum
EXPENSES = 'Expenses'
ASSETS = 'Assets'
INCOME = 'Income'
LIABILITIES = 'Liabilities'
MEMO = 'Memo Update Only'

# Size of columns in preview
SIZE_LINE_COL   = 6
SIZE_DATE_COL   = 12
SIZE_ID_COL     = 34
SIZE_DESC_COL   = 64
SIZE_MEMO_COL   = 30
SIZE_ACCTF_COL  = 44
SIZE_ACCTS_COL  = 20
SIZE_AMNT_COL   = 12
SIZE_INIT_COL   = 10