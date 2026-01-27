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
# TODO - Add checkbox to setup box to flip amount sign
#------------------------------------------------------------------------------

import constants as c
from gui import MyGui
from journal_file import Line
from import_file import ImportFile
from account_file import AccountFile
from journal_file import JournalFile


def LoadNewTransaction(gui, iFile, aFile, jFile):
    ''' TODO '''

    l = Line()

    # Place new data into GUI
    i = jFile.importIndex
    date = iFile.dateData[i]
    desc = iFile.descData[i]
    amnt = iFile.amntData[i]
    hash = iFile.hashData[i]
    gui.displayDate.set(date)
    gui.displayDescription.set(desc)
    gui.displayAmount.set(amnt)

    # Create initial line in entry
    l.date = date
    l.hash = hash
    l.desc = desc
    l.memo = ' '
    l.acctF = gui.selectedAssAcct.get()
    l.acctS = aFile.GetShortHand(gui.selectedAssAcct.get())
    l.amnt = amnt

    # Find suggested entry based on first line
    jFile.FindSuggestedEntry(l)

    # Clear all accounts
    gui.selectedAsset.set(' ')
    gui.selectedIncome.set(' ')
    gui.selectedExpense.set(' ')
    gui.selectedLiability.set(' ')

    # Load suggested account (for simple entries only)
    if ('Assets' in jFile.entry[1].acctF):
        gui.selectedAsset.set(jFile.entry[1].acctF)
    if ('Income' in jFile.entry[1].acctF):
        gui.selectedIncome.set(jFile.entry[1].acctF)
    if ('Expenses' in jFile.entry[1].acctF):
        gui.selectedExpense.set(jFile.entry[1].acctF)
    if ('Liabilities' in jFile.entry[1].acctF):
        gui.selectedLiability.set(jFile.entry[1].acctF)

    # # Update preview box with journal entry inputs
    # UpdatePreview(gui, entry)


def AddToLedger(gui, iFile, aFile, jFile):
    ''' TODO '''

    # Make sure import file is active
    if (iFile.active != True):
        msg = 'Import file is not active', 'error'
        gui.Log(msg)
        return

    # Make sure journal file is active
    if (jFile.active != True):
        msg = 'Journal file is not active', 'error'
        gui.Log(msg)
        return

    # Make sure account file is active
    if (aFile.active != True):
        msg = 'Account file is not active', 'error'
        gui.Log(msg)
        return

    # Make sure to check if transaction list already completed
    if (jFile.importIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # Check that a valid account was selected
    valid = False
    acct = gui.selectedExpense.get()
    if (acct != ' '):
        if (acct in aFile.allAcctsFullName):
            valid = True

    acct = gui.selectedAsset.get()
    if (acct != ' '):
        if (acct in aFile.allAcctsFullName):
            valid = True

    acct = gui.selectedIncome.get()
    if (acct != ' '):
        if (acct in aFile.allAcctsFullName):
            valid = True

    acct = gui.selectedLiability.get()
    if (acct != ' '):
        if (acct in aFile.allAcctsFullName):
            valid = True

    if (valid != True):
        msg = 'Selected account does not exist', 'error'
        gui.Log(msg)
        return

    # jFile.AddTransactionToJournal()

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

    # Check that associated account is valid
    retVal, msg = aFile.CheckIfValid(gui.selectedAssAcct.get())
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # Find starting transaction from import list
    flag = False
    iFile.importIndex = 0
    for id in iFile.hashData:
        flag = jFile.DoesTransactionExist(id)
        if (flag == False):
            break
        else:
            iFile.importIndex = iFile.importIndex + 1

    # Check to see if all transactions accounted for already
    if (jFile.importIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # Load new transaction to GUI
    LoadNewTransaction(gui, iFile, aFile, jFile)


def UpdatePreview(gui):
    ''' TODO '''

    # # Clear log
    # msg = ' ', 'default'
    # gui.Log(msg)

    # payload = []
    # date = gui.displayDate.get()
    # desc = gui.displayDescription.get()
    # amnt = gui.displayAmount.get()
    # fullAcct = selectedAcct
    # shortAcct = aFile.GetShortHand(selectedAcct) 

    # msg =       'Date:    Description:    Amount:    Account: \n'
    # msg = msg + date + '      ' + desc + '      ' + amnt + '      ' + fullAcct + '      ' + shortAcct

    # payload = msg, 'default'
    # gui.Log(payload)


def UpdateAccounts(event, gui, iFile, aFile, jFile, who):
    ''' TODO '''

    selectedAcct = ' '

    # Clear out account boxes that weren't selected - Brute force for now
    if (who == c.EXPENSES):
        gui.selectedAsset.set(' ')
        gui.selectedIncome.set(' ')
        gui.selectedLiability.set(' ')
        selectedAcct = gui.selectedExpense.get()
    if (who == c.LIABILITIES):
        gui.selectedAsset.set(' ')
        gui.selectedIncome.set(' ')
        gui.selectedExpense.set(' ')
        selectedAcct = gui.selectedLiability.get()
    if (who == c.INCOME):
        gui.selectedAsset.set(' ')
        gui.selectedExpense.set(' ')
        gui.selectedLiability.set(' ')
        selectedAcct = gui.selectedIncome.get()
    if (who == c.ASSETS):
        gui.selectedIncome.set(' ')
        gui.selectedExpense.set(' ')
        gui.selectedLiability.set(' ')
        selectedAcct = gui.selectedAssets.get()

    if (selectedAcct == ' '):
        return

    # UpdatePreview(gui, iFile, aFile, jFile, selectedAcct)


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
    gui.expenseDropdown['values'] = aFile.expenseAcctList
    gui.liabilityDropdown['values'] = aFile.liabilityAcctList
    gui.incomeDropdown['values'] = aFile.incomeAcctList
    gui.assetDropdown['values'] = aFile.assetAcctList

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, iFile, aFile, jFile))
    gui.addEntryButton.configure(command=lambda:AddToLedger(gui, iFile, aFile, jFile))
    gui.expenseDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.EXPENSES))
    gui.liabilityDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.LIABILITIES))
    gui.incomeDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.INCOME))
    gui.assetDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.ASSETS))

    # Begin main thread
    gui.root.mainloop()


Main()