import os
import csv
from gui import MyGui
from pathlib import Path
from datetime import datetime


GOOD = 'good'
BAD  = 'bad'

ACCOUNTS_FP  = 'Accounts.csv'
JOURNAL_FP   = 'Journal.csv'
DATA_FOLDER  = 'Data/'

ACCT_HEADERS =                                          \
    ['Type', 'Full Account Name', 'Account Name',       \
     'Account Code', 'Description', 'Account Color',    \
     'Notes', 'Symbol', 'Namespace', 'Hidden',          \
     'Tax Info', 'Placeholder']                         \

JRNL_HEADERS =                                          \
    ['Date', 'TransactionID', 'Description', 'Memo',    \
     'Full Account Name', 'Account Name',               \
     'Amount Num.']                                     \

# Add more as needed
ACCEPTED_DATE_NAMES =                                   \
    ['Date', 'Trans. Date', 'Trans Date']               \

# Add more as needed
ACCEPTED_DESCRIPTION_NAMES =                            \
    ['Description', 'Descr.']                           \

# Add more as needed
ACCEPTED_AMOUNT_NAMES =                                 \
    ['Amount', 'Amount Num.', 'Amt']                    \


def InitializationChecks(gui):
    ''' Check Accounts.csv and Journal.csv are legit '''

    # Check that 'Accounts.csv' file exists
    try:
        open(ACCOUNTS_FP, newline="", encoding="utf-8-sig")
    except:
        gui.Log('Accounts.csv does not exist in current directory.', 'error')

    # Check that 'Journal.csv' file exists
    try:
        open(JOURNAL_FP, newline="", encoding="utf-8-sig")
    except:
        gui.Log('Journal.csv does not exist in current directory.', 'error')


    # Check that 'Accounts.csv' file has necessary columns
    try:
        with open(ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headerList = list(next(reader).keys())

        if (set(headerList) != set(ACCT_HEADERS)):
            gui.Log('Accounts.csv is not syntactically correct.', 'error')

    except:
        gui.Log('Something bad happened', 'error')
        raise


    # Check that 'Journal.csv' file has necessary columns
    try:
        with open(JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headerList = list(next(reader).keys())

        if (set(headerList) != set(JRNL_HEADERS)):
            gui.Log('Journal.csv is not syntactically correct.', 'error')

    except:
        gui.Log('Something bad happened', 'error')
        raise


def GetAllDataFileNames():
    ''' Returns all csv file names from Data folder as a list of strings'''
    returnList = list()
    folderPath = 'Data'

    for file in os.listdir(folderPath):
        if (file.lower().endswith(".csv")):
            returnList.append(file)

    return returnList


def GetAllAccountNames(gui, fullName):
    ''' Returns account names as a list of strings '''
    returnList = list()

    if (fullName == True):
        colName = 'Full Account Name'
    else:
        colName = 'Account Name'

    try:
        with open(ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                returnList.append(row[colName])
    except:
        gui.Log('Something bad happened', 'error')
        raise

    return returnList

def CheckImportColmns(gui):
    ''' Checks to see if selected csv import file is legit '''

    # Check that csv file has necessary columns
    try:
        filePath = DATA_FOLDER + gui.selectedImportFile.get()

        with open(filePath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headerList = list(next(reader).keys())

            tmp = any(head in headerList for head in ACCEPTED_DATE_NAMES)
            if (tmp == False):
                gui.Log('Import csv does not have Date column.', 'error')
                return BAD

            tmp = any(head in headerList for head in ACCEPTED_DESCRIPTION_NAMES)
            if (tmp == False):
                gui.Log('Import csv does not have Description column.', 'error')
                return BAD

            tmp = any(head in headerList for head in ACCEPTED_AMOUNT_NAMES)
            if (tmp == False):
                gui.Log('Import csv does not have Amount column.', 'error')
                return BAD

    except:
        gui.Log('Something bad happened', 'error')
        raise

    return GOOD

def ToolStart(gui):
    ''' TODO '''

    # Clear log
    gui.Log(' ', 'default')

    # Check if csv file has valid columns for parsing
    retVal = CheckImportColmns(gui)
    if (retVal == BAD):
        return

    # Map import csv columns
    # Map journal csv columns

    # Loop through all import transactions and compare against journal


def Main():
    gui = MyGui()

    # Initialization Checks
    InitializationChecks(gui)

    # Load import dropdown
    importList = GetAllDataFileNames()
    gui.LoadImportDropdown(importList)

    # Load associated account dropdown
    accountList = GetAllAccountNames(gui, fullName=True)
    gui.LoadAssAcctDropdown(accountList)

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui))

    # Begin main thread
    gui.root.mainloop()


Main()