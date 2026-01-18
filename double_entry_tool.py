#------------------------------------------------------------------------------
# File:
#   double_entry_tool.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file executes the "Simple Double Entry Tool". It interfaces with the
#   GUI and associated csv files to help categorize and balance financial
#   transactions and accounts using double entry bookkeeping.
#
# TODO:
#   - Break the tool down into different classes to better organize code
#
#------------------------------------------------------------------------------

import os
import csv
import constants as c
from gui import MyGui
from import_file import ImportFile
from account_file import AccountFile
from journal_file import JournalFile



# def InitializationChecks(gui):
#     ''' Check Accounts.csv and Journal.csv are legit '''

#     # Check that 'Accounts.csv' file exists
#     try:
#         open(ACCOUNTS_FP, newline="", encoding="utf-8-sig")
#     except:
#         gui.Log('Accounts.csv does not exist in current directory.', 'error')

#     # Check that 'Journal.csv' file exists
#     try:
#         open(JOURNAL_FP, newline="", encoding="utf-8-sig")
#     except:
#         gui.Log('Journal.csv does not exist in current directory.', 'error')


#     # Check that 'Accounts.csv' file has necessary columns
#     try:
#         with open(ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
#             reader = csv.DictReader(f)
#             headerList = list(next(reader).keys())

#         if (set(headerList) != set(ACCT_HEADERS)):
#             gui.Log('Accounts.csv is not syntactically correct.', 'error')

#     except:
#         gui.Log('Something bad happened', 'error')
#         raise


#     # Check that 'Journal.csv' file has necessary columns
#     try:
#         with open(JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
#             reader = csv.DictReader(f)
#             headerList = list(next(reader).keys())

#         if (set(headerList) != set(JRNL_HEADERS)):
#             gui.Log('Journal.csv is not syntactically correct.', 'error')

#     except:
#         gui.Log('Something bad happened', 'error')
#         raise



def GetAllDataFileNames():
    ''' Returns all csv file names from Data folder as a list of strings '''

    returnList = list()
    folderPath = 'Data'

    for file in os.listdir(folderPath):
        if (file.lower().endswith(".csv")):
            returnList.append(file)

    return returnList



# def GetAllAccountNames(gui, fullName):
#     ''' Returns account names as a list of strings '''

#     returnList = list()

#     if (fullName == True):
#         colName = 'Full Account Name'
#     else:
#         colName = 'Account Name'

#     try:
#         with open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 returnList.append(row[colName])
#     except:
#         gui.Log('Something bad happened', 'error')
#         raise

#     return returnList



# def CheckImportColmns(gui):
#     ''' Checks to see if selected csv import file is legit '''

#     # Check that csv file has necessary columns
#     try:
#         filePath = DATA_FOLDER + 'balls.csv'

#         with open(filePath, newline="", encoding="utf-8-sig") as f:
#             reader = csv.DictReader(f)
#             headerList = list(next(reader).keys())

#             tmp = any(head in headerList for head in ACCEPTED_DATE_NAMES)
#             if (tmp == False):
#                 gui.Log('Import csv does not have Date column.', 'error')
#                 return BAD

#             tmp = any(head in headerList for head in ACCEPTED_DESCRIPTION_NAMES)
#             if (tmp == False):
#                 gui.Log('Import csv does not have Description column.', 'error')
#                 return BAD

#             tmp = any(head in headerList for head in ACCEPTED_AMOUNT_NAMES)
#             if (tmp == False):
#                 gui.Log('Import csv does not have Amount column.', 'error')
#                 return BAD

#     except FileNotFoundError:
#         gui.Log('Selected Import csv file does not exist', 'error')

#     except:
#         gui.Log('Something bad happened', 'error')
#         raise

#     return GOOD



def ToolStart(gui, inFile, acctFile, journalFile):
    ''' TODO '''

    # Clear log
    msg = ' ', 'default'
    gui.Log(msg)

    # Check if csv file has valid columns for parsing
    filePath = c.DATA_FOLDER + gui.selectedImportFile.get()
    retVal, msg = inFile.CheckFile(filePath)
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # # Map import csv columns
    # retVal = MapImportColmns(gui)
    # if (retVal == BAD):
    #     return

    # Map journal csv columns

    # Loop through all import transactions and compare against journal



def Main():

    # Initialization
    gui = MyGui()
    inFile = ImportFile()
    acctFile = AccountFile()
    journalFile = JournalFile()

    # Check that Account.csv is legit
    retVal, msg = acctFile.CheckFile()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Check that Account.csv is legit
    retVal, msg = journalFile.CheckFile()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Load import dropdown
    importList = GetAllDataFileNames()
    gui.LoadImportDropdown(importList)

    # Load associated account dropdown
    accountList = acctFile._GetAccountNames(fullName=True)
    gui.LoadAssAcctDropdown(accountList)

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, inFile, acctFile, journalFile))

    # Begin main thread
    gui.root.mainloop()



Main()