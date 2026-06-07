#------------------------------------------------------------------------------
# File:
#   double_entry_tool.py
#
# Author:
#   EmbeddedForest
#
# Description:
#   Entry point and event controller for the "Simple Double Entry Tool". It
#   wires the GUI to the pure-logic core (accounts, importer, ledger). All
#   journal state lives in an in-memory Ledger that is loaded once and written
#   back only when an entry is added.
#
#------------------------------------------------------------------------------

import constants as c
from gui import MyGui
from accounts import Accounts
from core.models import Line, Entry
from core.config import load_config, ConfigNotFoundError
from core.importer import load_transactions, list_import_files, ImportStyleError
from core.ledger import Ledger, JournalNotFoundError


class Sdet():
    ''' Controller for the Simple Double Entry Tool. The whole app is event
        driven; execution holds in the GUI main loop until the window closes. '''

    def __init__(self):
        self.gui = None
        self.accts = None
        self.ledger = None
        self.config = None
        self.import_result = None     # ImportResult for the selected file
        self.import_index = 0
        self.entry = Entry()
        self.split_active = False

    # -------------------------------------------------------------------------
    def run(self):
        gui = self.gui = MyGui()
        self.accts = Accounts()

        # Load config + accounts.
        try:
            self.config = load_config()
            self.accts.setup(self.config)
        except ConfigNotFoundError:
            gui.Log('Config file does not exist', 'error')

        # Load the journal once into memory.
        try:
            self.ledger = Ledger().load()
        except JournalNotFoundError:
            gui.Log('Journal.csv does not exist in current directory', 'error')

        # Populate GUI dropdowns / account boxes.
        gui.LoadImportDropdown(list_import_files(c.DATA_FOLDER))
        gui.LoadSplitAcctDropdowns(self.accts.all_full_names)
        gui.LoadAssets(self.accts.asset_dic)
        gui.LoadIncome(self.accts.income_dic)
        gui.LoadLiabilities(self.accts.liability_dic)
        gui.LoadExpenses(self.accts.expense_dic)

        # Bind buttons.
        gui.startButton.configure(command=self._prepare_for_new_transaction)
        gui.addEntryButton.configure(command=self._add_to_journal)
        gui.redoButton.configure(command=self._prepare_for_new_transaction)

        # Bind events.
        gui.root.bind('<Return>', self._update_entry)
        gui.root.bind('<<NotebookTabChanged>>', self._tab_changed)
        gui.assSelBox.bind('<ButtonRelease-1>', self._update_entry, add='+')
        gui.incSelBox.bind('<ButtonRelease-1>', self._update_entry, add='+')
        gui.liaSelBox.bind('<ButtonRelease-1>', self._update_entry, add='+')
        gui.expSelBox.bind('<ButtonRelease-1>', self._update_entry, add='+')
        gui.importDropdown.bind('<<ComboboxSelected>>', self._update_import_file)

        gui.root.mainloop()

    # -------------------------------------------------------------------------
    def _prepare_for_new_transaction(self):
        ''' Handler for the "Start" and "Redo Entry" buttons: load the next
            un-journalled transaction and its suggested categorisation. '''
        gui = self.gui
        gui.Log(' ')

        if self.import_result is None:
            gui.Log('No valid import file selected!', 'error')
            return

        if self.ledger is None:
            gui.Log('Journal not loaded', 'error')
            return

        if not self.accts.is_account_valid(gui.selectedAssAcct.get()):
            gui.Log('Associated account is not valid', 'error')
            return

        self.import_index = self._find_next_transaction_index()
        if self.import_index >= self.import_result.count:
            gui.Log('All transactions accounted for', 'default')
            return

        self._load_new_transaction(self.import_index)
        new_entry = self._create_new_entry(self.import_index)

        _flag, self.entry = self.ledger.find_suggested_entry(new_entry)

        if self.split_active or self.entry.split:
            gui.notebook.select(1)
            self._update_split_gui_from_entry()
        else:
            gui.notebook.select(0)

        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _find_next_transaction_index(self):
        ''' Index of the first imported transaction not already in the journal
            (or count, if every transaction is accounted for). '''
        for i, txn in enumerate(self.import_result.transactions):
            if not self.ledger.transaction_exists(txn.txn_id):
                return i
        return self.import_result.count

    # -------------------------------------------------------------------------
    def _load_new_transaction(self, i):
        ''' Show the imported transaction at index i in the GUI data boxes. '''
        gui = self.gui
        txn = self.import_result.transactions[i]
        gui.displayDate.set(txn.date)
        gui.displayDescription.set(txn.desc)
        gui.displayAmount.set(txn.amount)

    # -------------------------------------------------------------------------
    def _create_new_entry(self, i):
        ''' Build a one-line Entry seeded with the imported transaction and the
            selected associated account. '''
        gui = self.gui
        txn = self.import_result.transactions[i]
        assoc = gui.selectedAssAcct.get()

        line = Line(
            date=txn.date,
            txn_id=txn.txn_id,
            desc=txn.desc,
            memo='',
            acct_full=assoc,
            acct_short=self.accts.short_name(assoc),
            amount=txn.amount,
        )
        return Entry([line])

    # -------------------------------------------------------------------------
    def _update_simple_entry_from_gui(self, event=None):
        ''' Update memo and offsetting account for a simple (2-line) entry. '''
        gui = self.gui

        if self.entry.size != 2:
            return

        self.entry[1].memo = gui.memo.get()

        acct = gui.selectedAcct
        if not self.accts.is_account_valid(acct):
            return  # silent: don't clobber the preview with a half-typed acct

        self.entry[1].acct_full = acct
        self.entry[1].acct_short = self.accts.short_name(acct)
        gui.Update(self.entry)

    # -------------------------------------------------------------------------
    def _update_split_entry_from_gui(self, event):
        ''' Rebuild the entry from the split-tab rows, validate and balance. '''
        gui = self.gui
        entry = self.entry

        entry.split = True
        if entry.size == 0:
            return

        # Keep the original associated line; rebuild the rest from the rows.
        while entry.size > 1:
            entry.remove_line(entry.size - 1)

        first = entry[0]
        for i in range(1, len(gui.rows)):
            _label, acct_var, _acct_box, memo_var, _memo_box, amnt_var, _amnt_box = gui.rows[i]
            entry.add_line(Line(
                date=first.date,
                txn_id=first.txn_id,
                desc=first.desc,
                memo=memo_var.get(),
                acct_full=acct_var.get(),
                acct_short=self.accts.short_name(acct_var.get()),
                amount=amnt_var.get(),
            ))

        for line in entry:
            if not self.accts.is_account_valid(line.acct_full):
                gui.Log('One or more accounts are not valid', 'error')
                return

        try:
            balance = entry.balance
        except ValueError:
            gui.Log('One or more amounts are not valid', 'error')
            return

        gui.balanceStr.set(str(balance))
        if balance != 0:
            gui.Log('Entry is not balanced', 'error')
            return

        gui.Update(entry)

    # -------------------------------------------------------------------------
    def _update_entry(self, event):
        ''' Route Return / selection events to the active tab's updater. '''
        if not self.split_active:
            self._update_simple_entry_from_gui(event)
        else:
            self._update_split_entry_from_gui(event)

    # -------------------------------------------------------------------------
    def _tab_changed(self, event):
        ''' Sync the newly selected tab with the current entry. '''
        if self.gui.notebook.index('current') == 1:
            self.split_active = True
            self._update_split_gui_from_entry()
        else:
            self.split_active = False
            self._update_simple_gui_from_entry()

    # -------------------------------------------------------------------------
    def _update_simple_gui_from_entry(self):
        ''' Force a split entry back down to a simple 2-line entry, if needed,
            then refresh the GUI. '''
        entry = self.entry

        if entry.size > 2:
            while entry.size != 2:
                entry.remove_line(2)

            amount = entry[0].amount
            entry[1].amount = amount[1:] if amount.startswith('-') else '-' + amount

        if entry.size == 0:
            return

        self.gui.Update(entry)

    # -------------------------------------------------------------------------
    def _update_split_gui_from_entry(self):
        ''' Load the current entry into the split-tab rows. '''
        gui = self.gui
        gui.ResetSplitRows()

        for i, line in enumerate(self.entry):
            if i >= len(gui.rows):
                gui._AddSplitRow()
            _label, acct_var, _acct_box, memo_var, _memo_box, amnt_var, _amnt_box = gui.rows[i]
            acct_var.set(line.acct_full)
            memo_var.set(line.memo)
            amnt_var.set(line.amount)

        gui.LoadSplitAcctDropdowns()

    # -------------------------------------------------------------------------
    def _update_import_file(self, event):
        ''' Load the selected import file and refresh the associated-account
            dropdown. '''
        gui = self.gui
        gui.Log(' ')

        file_path = c.DATA_FOLDER + gui.selectedImportFile.get()

        try:
            result = load_transactions(file_path, self.config)
        except ImportStyleError:
            gui.Log('Import file does not match any known styles', 'error')
            return
        except FileNotFoundError:
            gui.Log('Selected import csv file does not exist', 'error')
            return
        except PermissionError:
            gui.Log('Selected import csv needs to be closed', 'error')
            return

        self.import_result = result
        gui.assAcctDropdown['values'] = result.assoc_accts
        if result.assoc_accts:
            gui.selectedAssAcct.set(result.assoc_accts[0])

    # -------------------------------------------------------------------------
    def _add_to_journal(self):
        ''' Validate the current entry and, if it passes, append it to the
            journal and advance to the next transaction. '''
        gui = self.gui
        gui.Log(' ')

        if self.import_result is None:
            gui.Log('Import file is not active', 'error')
            return
        if self.ledger is None:
            gui.Log('Journal file is not active', 'error')
            return
        if not self.accts.active:
            gui.Log('Accounts not loaded', 'error')
            return
        if self.import_index >= self.import_result.count:
            gui.Log('All transactions accounted for already', 'default')
            return

        # Capture the memo BEFORE writing (the original wrote the entry first,
        # so a memo typed without pressing Enter never reached disk).
        if not self.entry.split and self.entry.size >= 2:
            self.entry[1].memo = gui.memo.get()

        if not self.entry.split:
            acct = self.entry[1].acct_full
            if not self.accts.is_account_valid(acct):
                gui.Log('Selected account is not valid', 'error')
                return
        else:
            try:
                if not self.entry.is_balanced:
                    gui.Log('Entry is not balanced', 'error')
                    return
            except ValueError:
                gui.Log('One or more amounts are not valid', 'error')
                return

        self.ledger.add_entry(self.entry)
        self.ledger.save()

        gui.memo.set('')
        self._prepare_for_new_transaction()


def main():
    Sdet().run()


if __name__ == '__main__':
    main()
