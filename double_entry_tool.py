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
from accounts import Accounts
from journal_file import JournalFile


def LoadNewTransaction(gui, iFile, accts, jFile):
    '''
    Loads and displays the latest transaction info from import file into GUI.
    Creates new entry and loads it with known data. Runs the "FindSuggestedAcct"
    algorithm and loads GUI with suggested acct if it is "simple".
    '''
    l = Line()

    # Place new data into GUI
    i = iFile.importIndex
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
    l.memo = ''
    l.acctF = gui.selectedAssAcct.get()
    l.acctS = accts.GetShortHand(gui.selectedAssAcct.get())
    l.amnt = str(amnt)

    # Find suggested entry based on first line
    retVal, msg = jFile.FindSuggestedEntry(l)
    gui.Log(msg)

    # Clear all accounts
    gui.selectedAsset.set('')
    gui.selectedIncome.set('')
    gui.selectedExpense.set('')
    gui.selectedLiability.set('')
    gui.memo.set('')

    # Load suggested account (for simple entries only)
    if (jFile.simple == True):
        if ('Assets' in jFile.entry[1].acctF):
            gui.selectedAsset.set(jFile.entry[1].acctF)
        if ('Income' in jFile.entry[1].acctF):
            gui.selectedIncome.set(jFile.entry[1].acctF)
        if ('Expenses' in jFile.entry[1].acctF):
            gui.selectedExpense.set(jFile.entry[1].acctF)
        if ('Liabilities' in jFile.entry[1].acctF):
            gui.selectedLiability.set(jFile.entry[1].acctF)

def AddToJournal(gui, iFile, accts, jFile):
    '''
    Does a bunch of checks. If all checks pass, the entry is added to the
    journal and the next transaction is loaded.
    '''

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

    # Make sure accounts are loaded
    if (accts.active != True):
        msg = 'Accounts not loaded', 'error'
        gui.Log(msg)
        return

    # Make sure to check if transaction list already completed
    if (iFile.importIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # If simple transaction, check that selected account is valid
    retVal, msg = accts.IsValid(jFile.entry[1].acctF)
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    retVal = jFile.AddEntryToJournal()
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
    if (iFile.importIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # Load new transaction to GUI
    LoadNewTransaction(gui, iFile, accts, jFile)

    # Update preview box with current entry info
    UpdatePreview(gui, iFile, accts, jFile)

def UpdateImportFile(gui, iFile):
    '''
    When new import file is selected, setup the selected import file
    and update the associated account dropdown list.
    '''
    # Clear log
    msg = ' ', 'default'
    gui.Log(msg)

    # Get selected import file path from GUI
    filePath = c.DATA_FOLDER + gui.selectedImportFile.get()

    # Setup the new import file
    retVal, msg = iFile.Setup(filePath)
    if (retVal == c.BAD):
        gui.Log(msg)
        return

    # Load associated account box with options
    gui.assAcctDropdown['values'] = iFile.assAccts

    # Load first option automatically
    gui.selectedAssAcct.set(iFile.assAccts[0])

def ToolStart(gui, iFile, accts, jFile):
    '''
    Finds the starting transaction from import file and loads it into
    the GUI. Then updates the log box preview window.
    '''

    # Clear log
    msg = ' ', 'default'
    gui.Log(msg)

    # Check that import file is ready
    if (iFile.active != True):
        msg = 'No valid import file selected', 'error'
        gui.Log(msg)
        return

    # Check that associated account is valid
    retVal, msg = accts.IsValid(gui.selectedAssAcct.get())
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
    if (iFile.importIndex >= iFile.numTrans):
        msg = 'All transactions accounted for already', 'default'
        gui.Log(msg)
        return

    # Load new transaction to GUI
    LoadNewTransaction(gui, iFile, accts, jFile)

    # Update preview box with current entry info
    UpdatePreview(gui, iFile, accts, jFile)

def AddSplit(gui, iFile, accts, jFile):
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
    l.acctS = accts.GetShortHand(gui.selectedSplitAcct.get())
    l.memo = gui.splitMemo.get()
    l.amnt = str(gui.splitAmnt.get())

    # Load line to entry
    jFile.entry.append(l)

    UpdatePreview(gui, iFile, accts, jFile)

    return

def UndoSplit(gui, iFile, accts, jFile):
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

    UpdatePreview(gui, iFile, accts, jFile)

    return

def UpdatePreview(gui, iFile, accts, jFile):
    '''
    Updates the log box preview with latest information collected from user.
    Displays data in a way which reflects actual entry into journal.
    '''
    # Clear log
    log = ' ', 'default'
    gui.Log(log)

    # Build Header
    msg = c.JRNL_LINE
    for i in range(c.SIZE_LINE_COL-len(c.JRNL_LINE)):
        msg = msg + ' '
    msg = msg + c.JRNL_DATE
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
    lineNum = 0
    for j in jFile.entry:
        msg = msg + str(lineNum)
        for i in range(c.SIZE_LINE_COL-len(str(lineNum))):
            msg = msg + ' '
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
        lineNum = lineNum + 1

    log = msg, 'default'
    gui.Log(log)

def UpdateAccounts(event, gui, iFile, accts, jFile, who):
    '''
    When an account box is changed, we want to zero out the others. When
    a memo is input, we want to load it into the entry.
    '''
    # Memo update for simple transaction
    if (who == c.MEMO):
        if (jFile.simple == True):
            jFile.entry[1].memo = gui.memo.get()

        UpdatePreview(gui, iFile, accts, jFile)
        return

    # Account update
    selectedAcct = ''
    if (who == c.EXPENSES):
        gui.selectedAsset.set('')
        gui.selectedIncome.set('')
        gui.selectedLiability.set('')
        selectedAcct = gui.selectedExpense.get()
    if (who == c.LIABILITIES):
        gui.selectedAsset.set('')
        gui.selectedIncome.set('')
        gui.selectedExpense.set('')
        selectedAcct = gui.selectedLiability.get()
    if (who == c.INCOME):
        gui.selectedAsset.set('')
        gui.selectedExpense.set('')
        gui.selectedLiability.set('')
        selectedAcct = gui.selectedIncome.get()
    if (who == c.ASSETS):
        gui.selectedIncome.set('')
        gui.selectedExpense.set('')
        gui.selectedLiability.set('')
        selectedAcct = gui.selectedAssets.get()

    if (selectedAcct == ''):
        return

    # Update account info in entry for simple transaction
    if (jFile.simple == True):
        jFile.entry[1].acctF = selectedAcct
        jFile.entry[1].acctS = accts.GetShortHand(selectedAcct)

    UpdatePreview(gui, iFile, accts, jFile)

def Main():
    # Initialization
    gui = MyGui()
    accts = Accounts()
    iFile = ImportFile()
    jFile = JournalFile()

    # Setup Accounts
    retVal, msg = accts.Setup()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Setup Journal.csv file
    retVal, msg = jFile.SetupFile()
    if (retVal == c.BAD):
        gui.Log(msg)

    # Load dropdowns
    gui.importDropdown['values'] = iFile.importFileList
    gui.assAcctDropdown['values'] = accts.allAcctsFullName
    gui.splitAcctDropdown['values'] = accts.allAcctsFullName
    gui.expenseDropdown['values'] = accts.expenseAcctList
    gui.liabilityDropdown['values'] = accts.liabilityAcctList
    gui.incomeDropdown['values'] = accts.incomeAcctList
    gui.assetDropdown['values'] = accts.assetAcctList

    # Bind buttons
    gui.startButton.configure(command=lambda:ToolStart(gui, iFile, accts, jFile))
    gui.addEntryButton.configure(command=lambda:AddToJournal(gui, iFile, accts, jFile))
    gui.addSplitButton.configure(command=lambda:AddSplit(gui, iFile, accts, jFile))
    gui.undoSplitButton.configure(command=lambda:UndoSplit(gui, iFile, accts, jFile))

    # Setup events
    gui.expenseDropdown.bind('<<ComboboxSelected>>', lambda event:UpdateAccounts(event, gui, iFile, accts, jFile, c.EXPENSES))
    gui.liabilityDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, accts, jFile, c.LIABILITIES))
    gui.incomeDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, accts, jFile, c.INCOME))
    gui.assetDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateAccounts(event, gui, iFile, accts, jFile, c.ASSETS))
    gui.importDropdown.bind('<<ComboboxSelected>>', lambda event: UpdateImportFile(gui, iFile))
    gui.root.bind('<Return>', lambda event: UpdateAccounts(event, gui, iFile, accts, jFile, c.MEMO))

    # Begin main thread
    gui.root.mainloop()


Main()