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
    l.amnt = str(amnt)
    l.initiator = '1'

    # Find suggested entry based on first line
    retVal, msg = jFile.FindSuggestedEntry(l)
    gui.Log(msg)

    # Clear all accounts
    gui.selectedAsset.set(' ')
    gui.selectedIncome.set(' ')
    gui.selectedExpense.set(' ')
    gui.selectedLiability.set(' ')

    # Load suggested account (for simple entries only)
    if (len(jFile.entry) >= 2):
        if ('Assets' in jFile.entry[1].acctF):
            gui.selectedAsset.set(jFile.entry[1].acctF)
        if ('Income' in jFile.entry[1].acctF):
            gui.selectedIncome.set(jFile.entry[1].acctF)
        if ('Expenses' in jFile.entry[1].acctF):
            gui.selectedExpense.set(jFile.entry[1].acctF)
        if ('Liabilities' in jFile.entry[1].acctF):
            gui.selectedLiability.set(jFile.entry[1].acctF)

    # Update preview box with current entry info
    UpdatePreview(gui, iFile, aFile, jFile)


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

    retVal = jFile.AddEntryToJournal()
    if (retVal == c.BAD):
        gui.Log(msg)
        return

def ToolStart(gui, iFile, aFile, jFile, full):
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

    # Load associated account box with options
    gui.assAcctDropdown['values'] = iFile.assAccts

    # Load first option automatically
    gui.selectedAssAcct.set(iFile.assAccts[0])

    if(full != True):
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


def AddSplit(gui, iFile, aFile, jFile):
    ''' TODO '''

    # If it was previously a simple transaction, it isn't now
    jFile.simple = False

    # Create new line item for entry
    l = Line()

    try:
        l.date = jFile.entry[0].date
        l.hash = jFile.entry[0].hash
        l.desc = jFile.entry[0].desc
    except IndexError:
        msg = 'Entry not valid', 'default'
        gui.Log(msg)
        return
    except AttributeError:
        msg = 'Entry not valid', 'default'
        gui.Log(msg)
        return

    l.acctF = gui.selectedSplitAcct.get()
    l.acctS = aFile.GetShortHand(gui.selectedSplitAcct.get())
    l.memo = gui.splitMemo.get()
    l.amnt = str(gui.splitAmnt.get())

    # Load line to entry
    jFile.entry.append(l)

    UpdatePreview(gui, iFile, aFile, jFile)

    return


def UndoSplit(gui, iFile, aFile, jFile):
    ''' TODO '''

    # If it is a simple transaction, ignore
    if (jFile.simple == True):
        return

    # If there is only 2 items in list, ignore
    if (len(jFile.entry) < 2):
        return

    # Remove last line from entry
    index = len(jFile.entry) - 1
    jFile.entry.pop(index)

    UpdatePreview(gui, iFile, aFile, jFile)

    return


def UpdatePreview(gui, iFile, aFile, jFile):
    ''' TODO '''

    # Clear log
    log = ' ', 'default'
    gui.Log(log)

    # Build Header
    msg = c.JRNL_DATE
    for i in range(c.SIZE_DATE_COL-len(c.JRNL_DATE)):
        msg = msg + ' '
    msg = msg + c.JRNL_ID
    for i in range(c.SIZE_ID_COL-len(c.JRNL_ID)):
        msg = msg + ' '
    msg = msg + c.JRNL_DSCRP
    for i in range(c.SIZE_DESC_COL-len(c.JRNL_DSCRP)):
        msg = msg + ' '
    msg = msg + c.JRNL_MEMO
    for i in range(c.SIZE_MEMO_COL-len(c.JRNL_MEMO)):
        msg = msg + ' '
    msg = msg + c.JRNL_ACCT_NAME_F
    for i in range(c.SIZE_ACCTF_COL-len(c.JRNL_ACCT_NAME_F)):
        msg = msg + ' '
    msg = msg + c.JRNL_AMOUNT
    for i in range(c.SIZE_AMNT_COL-len(c.JRNL_AMOUNT)):
        msg = msg + ' '

    log = msg, 'header'
    gui.Log(log)

    # Build entry
    msg = ''
    for j in jFile.entry:
        msg = msg + str(j.date)
        for i in range(c.SIZE_DATE_COL-len(str(j.date))):
            msg = msg + ' '
        msg = msg + str(j.hash)
        for i in range(c.SIZE_ID_COL-len(str(j.hash))):
            msg = msg + ' '
        msg = msg + str(j.desc)
        for i in range(c.SIZE_DESC_COL-len(str(j.desc))):
            msg = msg + ' '
        msg = msg + str(j.memo)
        for i in range(c.SIZE_MEMO_COL-len(str(j.memo))):
            msg = msg + ' '
        msg = msg + str(j.acctF)
        for i in range(c.SIZE_ACCTF_COL-len(str(j.acctF))):
            msg = msg + ' '
        msg = msg + str(j.amnt)
        for i in range(c.SIZE_AMNT_COL-len(str(j.amnt))):
            msg = msg + ' '
        msg = msg + '\n'

    log = msg, 'default'
    gui.Log(log)


def UpdateAccounts(event, gui, iFile, aFile, jFile, who):
    ''' TODO '''

    # Memo update
    if (who == c.MEMO):
        try:
            if (jFile.simple == True):
                jFile.entry[1].memo = gui.memo.get()
        except IndexError:
            return
        except AttributeError:
            return

        UpdatePreview(gui, iFile, aFile, jFile)
        return

    # Account update
    selectedAcct = ' '
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

    print(selectedAcct)
    if (selectedAcct == ' '):
        return

    try:
        if (jFile.simple == True):
            jFile.entry[1].acctF = selectedAcct
    except IndexError:
        return
    except AttributeError:
        return

    print(selectedAcct)
    UpdatePreview(gui, iFile, aFile, jFile)


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
    gui.splitAcctDropdown['values'] = aFile.allAcctsFullName
    gui.expenseDropdown['values'] = aFile.expenseAcctList
    gui.liabilityDropdown['values'] = aFile.liabilityAcctList
    gui.incomeDropdown['values'] = aFile.incomeAcctList
    gui.assetDropdown['values'] = aFile.assetAcctList

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, iFile, aFile, jFile, True))
    gui.addEntryButton.configure(command=lambda:AddToLedger(gui, iFile, aFile, jFile))
    gui.addSplitButton.configure(command=lambda:AddSplit(gui, iFile, aFile, jFile))
    gui.undoSplitButton.configure(command=lambda:UndoSplit(gui, iFile, aFile, jFile))
    gui.expenseDropdown.bind('<<ComboboxSelected>>', lambda event:UpdateAccounts(event, gui, iFile, aFile, jFile, c.EXPENSES))
    gui.liabilityDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.LIABILITIES))
    gui.incomeDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.INCOME))
    gui.assetDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.ASSETS))
    gui.importDropdown.bind('<<ComboboxSelected>>', lambda event: ToolStart(gui, iFile, aFile, jFile, False))
    gui.root.bind('<Return>', lambda event: UpdateAccounts(event, gui, iFile, aFile, jFile, c.MEMO))

    # Begin main thread
    gui.root.mainloop()


Main()