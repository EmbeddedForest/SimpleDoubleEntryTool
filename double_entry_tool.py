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
from journal_file import Line
from journal_file import Entry
from journal_file import JournalFile



class Sdet():
    ''' Class to manage the Simple Double Entry Tool application '''

    importIndex = 0
    curEntry = Entry()

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

        # Load import dropdown in GUI
        gui.LoadImportDropdown(iFile.importFileList)

        # Load account boxes in GUI
        gui.LoadAssets(accts.assetDic)
        gui.LoadIncome(accts.incomeDic)
        gui.LoadLiabilities(accts.liabilityDic)
        gui.LoadExpenses(accts.expenseDic)

        # Bind GUI buttons
        gui.startButton.configure(command=self._PrepareForNewTransaction)
        gui.addEntryButton.configure(command=self.AddToJournal)

        # Setup GUI events
        gui.root.bind('<Return>', self._UpdateSimple)
        gui.assSelBox.bind('<ButtonRelease-1>', self._UpdateSimple, add='+')
        gui.incSelBox.bind('<ButtonRelease-1>', self._UpdateSimple, add='+')
        gui.liaSelBox.bind('<ButtonRelease-1>', self._UpdateSimple, add='+')
        gui.expSelBox.bind('<ButtonRelease-1>', self._UpdateSimple, add='+')
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

        # Create new entry object with new transaction data
        newEntry = self._CreateNewEntry(self.importIndex)

        # Attempt to find and load suggested entry
        retVal, self.curEntry = jFile.FindSuggestedEntry(newEntry)
        if (retVal == c.BAD):
            gui.Log('Journal does not exist', 'error')
            return

        # Update GUI
        gui.Update(self.curEntry)

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
        Gets latest transaction data and loads it as the first lin into an new
        entry object. That object is then saved as object attribute 'curEntry'.

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
    def _UpdateSimple(self, event):
        '''
        Handler to update memo and account data for a simple entry

        '''
        gui   = self.gui
        accts = self.accts

        if (self.curEntry.size != 2):
            # Not a simple entry
            return

        # Update memo
        self.curEntry.entry[1].memo = gui.memo.get()

        # Validate new account info
        acctF = gui.selectedAcct
        retVal = accts.IsAccountValid(acctF)
        if (retVal == c.BAD):
            # Silent return, don't update GUI
            return

        # Update account info in entry
        self.curEntry.entry[1].acctF = acctF
        self.curEntry.entry[1].acctS = accts.GetShortHand(acctF)

        gui.Update(self.curEntry)

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
    def AddToJournal(self):
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
        if (self.curEntry.split == False):
            acct = self.curEntry.entry[1].acctF
            retVal = accts.IsAccountValid(acct)
            if (retVal == c.BAD):
                gui.Log('Selected account is not valid', 'error')
                return

        retVal = jFile.AddEntryToJournal(self.curEntry)
        if (retVal == c.BAD):
            gui.Log('Selected Journal csv file does not exist', 'error')
            return
        
        self._PrepareForNewTransaction()


def Main():
    sdetApp = Sdet()
    sdetApp.Run()


Main()