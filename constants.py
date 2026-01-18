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

# Accepted header names (add more as needed)
ACCEPTED_DATE_NAMES         = ['Date', 'Trans. Date', 'Trans Date']
ACCEPTED_DESCRIPTION_NAMES  = ['Description', 'Descr.']
ACCEPTED_AMOUNT_NAMES       = ['Amount', 'Amount Num.', 'Amt']

# Common file names and paths
ACCOUNTS_FP  = 'Accounts.csv'
JOURNAL_FP   = 'Journal.csv'
DATA_FOLDER  = 'Data/'

# Account.csv column headers
ACCT_TYPE        = 'Type'
ACCT_NAME_FULL   = 'Full Account Name'
ACCT_NAME        = 'Account Name'
ACCT_CODE        = 'Account Code'
ACCT_DSCRP       = 'Description'
ACCT_COLOR       = 'Account Color'
ACCT_NOTES       = 'Notes'
ACCT_SYMBOL      = 'Symbol'
ACCT_NAMESPACE   = 'Namespace'
ACCT_HIDDEN      = 'Hidden'
ACCT_TAX_INFO    = 'Tax Info'
ACCT_PLACEHOLDER = 'Placeholder'

ACCT_HEADERS =                                                          \
    [ACCT_TYPE,      ACCT_NAME_FULL, ACCT_NAME,     ACCT_CODE,          \
     ACCT_DSCRP,     ACCT_COLOR,     ACCT_NOTES,    ACCT_SYMBOL,        \
     ACCT_NAMESPACE, ACCT_HIDDEN,    ACCT_TAX_INFO, ACCT_PLACEHOLDER]

# Journal.csv column headers
JRNL_DATE        = 'Date'
JRNL_ID          = 'TransactionID'
JRNL_DSCRP       = 'Description'
JRNL_MEMO        = 'Memo'
JRNL_ACCT_NAME_F = 'Full Account Name'
JRNL_ACCT_NAME   = 'Account Name'
JRNL_AMOUNT      = 'Amount Num.'

JRNL_HEADERS =                                                          \
    [JRNL_DATE, JRNL_ID, JRNL_DSCRP, JRNL_MEMO,                         \
     JRNL_ACCT_NAME_F, JRNL_ACCT_NAME, JRNL_AMOUNT]