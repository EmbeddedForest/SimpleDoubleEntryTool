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


def LoadNewTransaction(gui, iFile, aFile, jFile):
    ''' TODO '''

    # Place new data into GUI
    i = jFile.LatestIndex
    date = iFile.dateData[i]
    desc = iFile.descData[i]
    amnt = iFile.amntData[i]
    gui.displayDate.set(date)
    gui.displayDescription.set(desc)
    gui.displayAmount.set(amnt)

    # Find suggested account
    jFile.FindLast(date, desc, amnt)

    # Clear all accounts
    gui.selectionAsset.set(' ')
    gui.selectionIncome.set(' ')
    gui.selectionExpenses.set(' ')
    gui.selectionLiability.set(' ')


    # Load suggested account
    if ('Assets' in jFile.suggestedAcct):
        gui.selectionAsset.set(jFile.suggestedAcct)
    if ('Income' in jFile.suggestedAcct):
        gui.selectionIncome.set(jFile.suggestedAcct)
    if ('Expenses' in jFile.suggestedAcct):
        gui.selectionExpenses.set(jFile.suggestedAcct)
    if ('Liabilities' in jFile.suggestedAcct):
        gui.selectionLiability.set(jFile.suggestedAcct)


def ToolStart(gui, iFile, aFile, jFile):
    ''' TODO '''

    # Clear log
    msg = ' ', 'default'
    gui.Log(msg)

    # Get selected import file path from GUI
    filePath = c.DATA_FOLDER + gui.selectedImportFile.get()

    # Setup the new import file
    retVal, msg = iFile.SetupFile(filePath)
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # Find latest transaction which doesn't already exist in journal
    retVal, msg = jFile.FindLatest(iFile.dateData, iFile.descData, iFile.amntData)
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # Check to see if all transactions accounted for already
    if (jFile.LatestIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # Load new transaction to GUI
    LoadNewTransaction(gui, iFile, aFile, jFile)


def Main():

    # Initialization
    gui = MyGui()
    iFile = ImportFile()
    aFile = AccountFile()
    jFile = JournalFile()

    # Setup Account.csv file
    retVal, msg = aFile.SetupFile()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Setup Journal.csv file
    retVal, msg = jFile.SetupFile()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Load import dropdown
    iFile.LoadAllDataFileNames()
    gui.LoadImportDropdown(iFile.importFileList)

    # Load account dropdowns
    gui.assAcctDropdown['values'] = aFile.allAcctsFullName
    gui.expensesDropdown['values'] = aFile.expenseAcctList
    gui.liabilityDropdown['values'] = aFile.liabilityAcctList
    gui.incomeDropdown['values'] = aFile.incomeAcctList
    gui.assetDropdown['values'] = aFile.assetAcctList

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, iFile, aFile, jFile))

    # Begin main thread
    gui.root.mainloop()


Main()