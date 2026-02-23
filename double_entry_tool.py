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
#------------------------------------------------------------------------------

import constants as c
from gui import MyGui
from import_file import ImportFile
from accounts import Accounts
from entry import Line
from entry import Entry
from journal_file import JournalFile



class Sdet():
    ''' Class to manage the Simple Double Entry Tool application '''

    importIndex = 0
    entry = Entry()
    splitActive = False

    # -------------------------------------------------------------------------
    def Run(self):
        '''
        Execution holds here until GUI is closed.
        
        Note - The entire app is event based.

        '''
        # Initialization
        self.gui = MyGui()
        self.accts = Accounts()
        self.iFile = ImportFile()
        self.jFile = JournalFile()

        # Load shorthands for non-mutable objects
        gui = self.gui
        accts = self.accts
        iFile = self.iFile
        jFile = self.jFile

        # Setup Accounts
        retVal, msg = accts.Setup()
        if (retVal == c.BAD):
            gui.Log(msg)

        # Setup Journal
        retVal, msg = jFile.Setup()
        if (retVal == c.BAD):
            gui.Log(msg)

        # Load dropdowns in GUI
        gui.LoadImportDropdown(iFile.importFileList)
        gui.LoadSplitAcctDropdowns(accts.allAcctsFullName)

        # Load account boxes in GUI
        gui.LoadAssets(accts.assetDic)
        gui.LoadIncome(accts.incomeDic)
        gui.LoadLiabilities(accts.liabilityDic)
        gui.LoadExpenses(accts.expenseDic)

        # Bind GUI buttons
        gui.startButton.configure(command=self._PrepareForNewTransaction)
        gui.addEntryButton.configure(command=self._AddToJournal)

        # Setup GUI events
        gui.root.bind('<Return>', self._UpdateEntry)
        gui.root.bind('<<NotebookTabChanged>>', self._TabChanged)
        gui.assSelBox.bind('<ButtonRelease-1>', self._UpdateEntry, add='+')
        gui.incSelBox.bind('<ButtonRelease-1>', self._UpdateEntry, add='+')
        gui.liaSelBox.bind('<ButtonRelease-1>', self._UpdateEntry, add='+')
        gui.expSelBox.bind('<ButtonRelease-1>', self._UpdateEntry, add='+')
        gui.importDropdown.bind('<<ComboboxSelected>>', self._UpdateImportFile)

        # Begin main thread
        gui.root.mainloop()

    # -------------------------------------------------------------------------
    def _PrepareForNewTransaction(self):
        '''
        Handler for the "Start" button press

        '''
        gui   = self.gui
        accts = self.accts
        iFile = self.iFile
        jFile = self.jFile

        # Clear GUI log
        gui.Log(' ')

        # Check that import file is ready
        if (iFile.active != True):
            gui.Log('No valid import file selected!', 'error')
            return

        # Check that associated account is valid
        retVal = accts.IsAccountValid(gui.selectedAssAcct.get())
        if (retVal == c.BAD):
            gui.Log('Associated account is not valid', 'error')
            return

        # Find next valid transaction from import list
        self.importIndex = self._FindNextTransactionIndex()

        # Check to see if all transactions accounted for already
        if (self.importIndex >= iFile.numTrans):
            gui.Log('All transactions accounted for', 'default')
            return

        # Load new transaction data into GUI
        self._LoadNewTransaction(self.importIndex)

        # Load entry object with new transaction data
        entry = self._CreateNewEntry(self.importIndex)

        # Attempt to find and load suggested entry
        retVal, entry = jFile.FindSuggestedEntry(entry)
        if (retVal == c.BAD):
            gui.Log('Journal does not exist', 'error')
            return

        # Update self entry
        self.entry = entry

        if ((self.splitActive == True) or (self.entry.split == True)):
            # Open split tab and update
            gui.notebook.select(1)
            self._UpdateSplitGuiFromEntry()
        else:
            # Open simple tab
            gui.notebook.select(0)

        # Update GUI
        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _FindNextTransactionIndex(self):
        '''
        Finds next transaction from import list that isn't already in Journal.

        Returns the index to the transaction in the import file.

        '''
        iFile = self.iFile
        jFile = self.jFile

        index = 0
        flag = False

        for id in iFile.hashData:
            flag = jFile.DoesTransactionExist(id)

            if (flag == False):
                break
            else:
                index = index + 1

        return index

    # -------------------------------------------------------------------------
    def _LoadNewTransaction(self, i):
        '''
        Gets latest transaction data and loads it into GUI

        '''
        gui   = self.gui
        iFile = self.iFile

        # Get new transaction data
        date = iFile.dateData[i]
        desc = iFile.descData[i]
        amnt = iFile.amntData[i]

        # Place new data into GUI
        gui.displayDate.set(date)
        gui.displayDescription.set(desc)
        gui.displayAmount.set(amnt)

    # -------------------------------------------------------------------------
    def _CreateNewEntry(self, i):
        '''
        Gets latest transaction data and loads it as the first line into an new
        entry object. That object is then returned.

        '''
        gui   = self.gui
        accts = self.accts
        iFile = self.iFile

        l = Line()
        entry = Entry()

        # Get new transaction data
        date = iFile.dateData[i]
        desc = iFile.descData[i]
        amnt = iFile.amntData[i]
        hash = iFile.hashData[i]

        # Create initial line in entry
        l.date = date
        l.hash = hash
        l.desc = desc
        l.memo = ''
        l.acctF = gui.selectedAssAcct.get()
        l.acctS = accts.GetShortHand(gui.selectedAssAcct.get())
        l.amnt = str(amnt)

        entry.AddLine(l)
        return entry

    # -------------------------------------------------------------------------
    def _UpdateSimpleEntryFromGui(self, event=None):
        '''
        Handler to update memo and account data for a simple entry. If entry is
        more than 2 lines, the extra lines are deleted. (Forces a transition
        from split to simple)

        '''
        gui   = self.gui
        accts = self.accts

        if (self.entry.size != 2):
            # Not a simple entry
            return

        # Update memo
        self.entry[1].memo = gui.memo.get()

        # Validate new account info
        acctF = gui.selectedAcct
        retVal = accts.IsAccountValid(acctF)
        if (retVal == c.BAD):
            # Silent return, don't update GUI
            return

        # Update account info in entry
        self.entry[1].acctF = acctF
        self.entry[1].acctS = accts.GetShortHand(acctF)

        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _UpdateSplitEntryFromGui(self, event):
        '''
        Handler to update acct, memo, and amount data in entry using data in
        split tab input boxes.

        '''
        gui   = self.gui
        entry = self.entry
        accts = self.accts

        # Force transition of entry to split
        self.entry.split = True

        if (self.entry.size == 0):
            # Entry is not active, do nothing
            return

        # Reset old entry data (keep original line)
        for i in range(1, entry.size, 1):
            entry.RemoveLine(i)

        # Load entry with data from GUI
        for i in range(1, len(gui.rows), 1):
            l, acctF, acctB, memo, mB, amnt, amntB = gui.rows[i]
            try:
                entry[i].date = entry[i-1].date
                entry[i].hash = entry[i-1].hash
                entry[i].desc = entry[i-1].desc
                entry[i].memo = memo.get()
                entry[i].acctF = acctF.get()
                entry[i].acctS = accts.GetShortHand(acctF.get())
                entry[i].amnt = amnt.get()
            except IndexError:
                # Entry needs new line
                newLine = Line()
                newLine.date = entry[i-1].date
                newLine.hash = entry[i-1].hash
                newLine.desc = entry[i-1].desc
                newLine.memo = memo.get()
                newLine.acctF = acctF.get()
                newLine.acctS = accts.GetShortHand(acctF.get())
                newLine.amnt = amnt.get()
                entry.AddLine(newLine)

        # Validate accounts
        for l in entry:
            retVal = accts.IsAccountValid(l.acctF)
            if (retVal == c.BAD):
                gui.Log('One or more accounts are not valid', 'error')
                return

        # Update balance
        balance = 0
        for l in entry:
            try:
                balance =  balance + float(l.amnt)
            except ValueError:
                gui.Log('One or more amounts are not valid', 'error')
                return

        balance = round(balance, 2)
        gui.balanceStr.set(str(balance))

        if (balance != 0):
            gui.Log('Entry is not balanced', 'error')
            return

        self.entry = entry
        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _UpdateEntry(self, event):
        '''
        Handler to update entry/preview for either simple or split entry

        '''
        if (self.splitActive == False):
            # Do a simple entry update
            self._UpdateSimpleEntryFromGui(event)
        else:
            # Do a split entry update
            self._UpdateSplitEntryFromGui(event)

    # -------------------------------------------------------------------------
    def _TabChanged(self, event):
        '''
        When tab is changed, and the new tab is the split tab, check if entry
        has valid first line, if so, update the GUI with the latest entry data.

        '''
        gui = self.gui

        tabIndex = gui.notebook.index('current')
        if (tabIndex == 1):
            self.splitActive = True
            self._UpdateSplitGuiFromEntry()
        else:
            self.splitActive = False
            self._UpdateSimpleGuiFromEntry()

    # -------------------------------------------------------------------------
    def _UpdateSimpleGuiFromEntry(self):
        '''
        Update the GUI with the latest entry data for simple entry.

        '''
        gui   = self.gui
        accts = self.accts

        if (self.entry.size > 2):
            # Not a simple entry, force from split to simple entry

            # Remove extra lines
            while (self.entry.size != 2):
                self.entry.RemoveLine(2)

            # Update amount
            amnt = self.entry[0].amnt
            if ('-' in amnt):
                self.entry[1].amnt = amnt.replace('-', '')
            else:
                self.entry[1].amnt = '-' + amnt

        if (self.entry.size == 0):
            # Do nothing, no entry data
            return

        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _UpdateSplitGuiFromEntry(self):
        '''
        Update the GUI with the latest entry data for split entry.

        '''
        gui = self.gui

        # Load GUI with existing current entry data
        i = 0
        gui.ResetSplitRows()
        for line in self.entry:
            # Add new row if need be
            if (i >= len(gui.rows)):
                gui._AddSplitRow()

            # Update data boxes
            l, acctS, acctB, mS, mB, amntS, amntB = gui.rows[i]
            acctS.set(line.acctF)
            mS.set(line.memo)
            amntS.set(line.amnt)

            i = i + 1

        gui.LoadSplitAcctDropdowns()


    # -------------------------------------------------------------------------
    def _UpdateImportFile(self, event):
        '''
        When new import file is selected, setup the selected import file
        and update the associated account dropdown list.

        '''
        gui   = self.gui
        iFile = self.iFile

        # Clear log
        gui.Log(' ')

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

    # -------------------------------------------------------------------------
    def _AddToJournal(self):
        '''
        Does a bunch of checks. If all checks pass, the entry is added to the
        journal and the next transaction is loaded.

        '''
        gui   = self.gui
        accts = self.accts
        iFile = self.iFile
        jFile = self.jFile

        # Clear log
        gui.Log(' ')

        # Make sure import file is active
        if (iFile.active != True):
            gui.Log('Import file is not active', 'error')
            return

        # Make sure journal file is active
        if (jFile.active != True):
            gui.Log('Journal file is not active', 'error')
            return

        # Make sure accounts are loaded
        if (accts.active != True):
            gui.Log('Accounts not loaded', 'error')
            return

        # Make sure to check if transaction list already completed
        if (self.importIndex >= iFile.numTrans):
            gui.Log('All transactions accounted for already', 'default')
            return

        # If simple transaction, check that selected account is valid
        if (self.entry.split == False):
            acct = self.entry[1].acctF
            retVal = accts.IsAccountValid(acct)
            if (retVal == c.BAD):
                gui.Log('Selected account is not valid', 'error')
                return

        retVal = jFile.AddEntryToJournal(self.entry)
        if (retVal == c.BAD):
            gui.Log('Selected Journal csv file does not exist', 'error')
            return

        # Get memo
        self.entry[1].memo = gui.memo.get()

        # Clear memo box
        gui.memo.set('')

        self._PrepareForNewTransaction()


def Main():
    sdetApp = Sdet()
    sdetApp.Run()


Main()