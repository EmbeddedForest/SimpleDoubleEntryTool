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


def GetAllDataFileNames():
    ''' Returns all csv file names from Data folder as a list of strings '''

    returnList = list()
    folderPath = 'Data'

    for file in os.listdir(folderPath):
        if (file.lower().endswith(".csv")):
            returnList.append(file)

    return returnList


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

    # Setup import file object to point to correct columns
    retVal, msg = inFile.MapColumns()
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # Find latest uncategorized transaction from import file
    retVal, msg = inFile.LoadLatestTransactionData()
    if (retVal == c.BAD):
        gui.Log(msg)
        return



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
    accountList = acctFile.GetAccountNames(fullName=True)
    gui.LoadAssAcctDropdown(accountList)

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, inFile, acctFile, journalFile))

    # Begin main thread
    gui.root.mainloop()



Main()