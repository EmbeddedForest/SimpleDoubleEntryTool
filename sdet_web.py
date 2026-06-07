#------------------------------------------------------------------------------
# File:
#   sdet_web.py
#
# Description:
#   NiceGUI front-end for the Simple Double Entry Tool. This is a thin
#   presentation layer over the pure-logic core/ package - it owns no
#   accounting rules, it just wires widgets to Accounts / Ledger / importer.
#
#   Mental model if you are coming from tkinter: you still create widgets and
#   give them event handlers (on_click / on_change). The differences are:
#     * elements are laid out by *creation order* inside a container
#       (ui.row / ui.column / ui.card), not a grid of row/column numbers;
#     * @ui.refreshable marks a chunk of UI you can rebuild on demand by
#       calling its .refresh();
#     * .bind_value(obj, 'attr') two-way-binds a widget to an object attribute.
#
#   Run it with:   python sdet_web.py
#   Then open the URL it prints (default http://localhost:8080).
#------------------------------------------------------------------------------

import os

from nicegui import ui

import constants as c
from accounts import Accounts
from core.models import Line, Entry
from core.config import load_config, ConfigNotFoundError
from core.importer import load_transactions, list_import_files, ImportStyleError
from core.ledger import Ledger, JournalNotFoundError
from core.suggest import EXACT, PARTIAL, NONE


#==============================================================================
# Application state - one instance for this single-user local tool.
#==============================================================================
class AppState:
    ''' Holds the backend objects and the transaction currently being edited.
        Knows nothing about widgets. '''

    def __init__(self):
        self.error = None
        self.config = None
        self.accounts = Accounts()
        self.ledger = None
        self.import_result = None     # ImportResult for the selected file
        self.entry = None             # Entry currently being edited
        self.match_flag = None        # EXACT / PARTIAL / NONE for that entry

        try:
            self.config = load_config()
            self.accounts.setup(self.config)
            self.ledger = Ledger().load()
        except ConfigNotFoundError:
            self.error = 'config.yaml not found in the project directory.'
        except JournalNotFoundError:
            self.error = 'Journal.csv not found in the project directory.'

    # -- options ----------------------------------------------------------

    @property
    def account_options(self):
        return self.accounts.all_full_names

    def import_files(self):
        return list_import_files(c.DATA_FOLDER)

    # -- workflow ---------------------------------------------------------

    def select_import(self, filename):
        ''' Load an import file. Returns its candidate associated accounts.
            Raises ImportStyleError / FileNotFoundError on failure. '''
        path = c.DATA_FOLDER + filename
        self.import_result = load_transactions(path, self.config)
        return self.import_result.assoc_accts

    def remaining_count(self):
        ''' How many imported transactions are not yet in the journal. '''
        if not self.import_result or not self.ledger:
            return 0
        return sum(1 for t in self.import_result.transactions
                   if not self.ledger.transaction_exists(t.txn_id))

    def load_next(self, assoc_acct):
        ''' Seed self.entry with the next un-journalled transaction and its
            suggested categorisation. Returns True if one was loaded. '''
        self.entry = None
        self.match_flag = None
        if not self.import_result or not self.ledger:
            return False

        for txn in self.import_result.transactions:
            if self.ledger.transaction_exists(txn.txn_id):
                continue
            first = Line(
                date=txn.date, txn_id=txn.txn_id, desc=txn.desc, memo='',
                acct_full=assoc_acct,
                acct_short=self.accounts.short_name(assoc_acct),
                amount=txn.amount,
            )
            self.match_flag, self.entry = \
                self.ledger.find_suggested_entry(Entry([first]))
            return True
        return False

    def add_blank_line(self):
        ''' Add an empty posting line (turns a simple entry into a split). '''
        first = self.entry[0]
        self.entry.add_line(Line(date=first.date, txn_id=first.txn_id,
                                 desc=first.desc))

    def remove_last_line(self):
        if self.entry.size > 2:
            self.entry.remove_line(self.entry.size - 1)

    def validate_and_add(self):
        ''' Validate the current entry; if good, append + persist it.
            Returns (ok: bool, message: str). '''
        if self.entry is None:
            return False, 'No transaction loaded.'

        for line in self.entry:
            line.acct_short = self.accounts.short_name(line.acct_full or '')
            if not self.accounts.is_account_valid(line.acct_full or ''):
                return False, f'Invalid account: {line.acct_full or "(blank)"}'

        try:
            if not self.entry.is_balanced:
                return False, f'Not balanced - off by {self.entry.balance:.2f}'
        except ValueError:
            return False, 'One or more amounts are not valid numbers.'

        self.ledger.add_entry(self.entry)
        self.ledger.save()
        self.entry = None
        self.match_flag = None
        return True, 'Added to journal.'


state = AppState()


#==============================================================================
# UI helpers
#==============================================================================
_BADGE = {
    EXACT:   ('Exact match',   'green'),
    PARTIAL: ('Suggestion',    'amber'),
    NONE:    ('No match - new', 'grey'),
}


def _safe_balance():
    ''' Current entry balance as a float, or None if any amount is invalid. '''
    try:
        return state.entry.balance
    except (ValueError, AttributeError):
        return None


#==============================================================================
# The page
#==============================================================================
@ui.page('/')
def index():
    if state.error:
        ui.label('Startup error').classes('text-2xl text-red-600')
        ui.label(state.error)
        return

    ui.label('S-DET').classes('text-3xl font-bold')
    ui.label('A Simple Double Entry Tool').classes('text-sm text-gray-500 -mt-2')

    # ---- forward declarations so handlers can reference widgets ----------
    # (Python resolves these names when the handlers actually run, by which
    # time the widgets below have been created.)

    def on_import_change():
        try:
            accts = state.select_import(import_select.value)
        except ImportStyleError:
            ui.notify('File does not match any known import style', type='negative')
            return
        except FileNotFoundError:
            ui.notify('Import file not found', type='negative')
            return
        assoc_select.set_options(accts, value=accts[0] if accts else None)
        update_progress()

    def on_start():
        if not state.accounts.is_account_valid(assoc_select.value or ''):
            ui.notify('Pick a valid associated account first', type='warning')
            return
        if not state.load_next(assoc_select.value):
            ui.notify('All transactions accounted for', type='positive')
        editor.refresh()
        update_progress()

    def on_add():
        ok, msg = state.validate_and_add()
        ui.notify(msg, type='positive' if ok else 'negative')
        if ok:
            if not state.load_next(assoc_select.value):
                ui.notify('All transactions accounted for', type='positive')
            editor.refresh()
            update_progress()

    def on_add_line():
        state.add_blank_line()
        editor.refresh()

    def on_remove_line():
        state.remove_last_line()
        editor.refresh()

    def update_progress():
        progress_label.text = f'{state.remaining_count()} transaction(s) remaining'

    # ---- a refreshable balance readout (rebuilt on amount change) --------
    @ui.refreshable
    def balance_view():
        bal = _safe_balance()
        if bal is None:
            ui.label('Balance: -').classes('text-red-600 font-mono')
        else:
            ok = abs(bal) < 0.005
            ui.label(f'Balance: {bal:.2f}').classes(
                ('text-green-600' if ok else 'text-red-600') + ' font-mono')

    # ---- the main editor, rebuilt whenever the entry changes -------------
    @ui.refreshable
    def editor():
        if state.entry is None:
            ui.label('Pick an import file and press Start.').classes('text-gray-500')
            return

        first = state.entry[0]
        with ui.card().classes('w-full max-w-4xl'):
            # transaction header
            with ui.row().classes('items-center w-full gap-4'):
                ui.label(first.date).classes('font-mono')
                ui.label(first.desc).classes('font-bold grow')
                ui.label(first.amount).classes('font-mono')
                text, color = _BADGE.get(state.match_flag, ('', 'grey'))
                ui.badge(text).props(f'color={color}')

            ui.separator()

            # posting lines (line 0 = the associated account, shown read-only)
            for i, line in enumerate(state.entry):
                with ui.row().classes('items-center w-full gap-2'):
                    ui.label(str(i)).classes('w-5 text-gray-400')
                    if i == 0:
                        ui.label(line.acct_full).classes('grow')
                        ui.label(line.amount).classes('font-mono w-28 text-right')
                    else:
                        ui.select(state.account_options, with_input=True,
                                  value=line.acct_full or None) \
                            .bind_value(line, 'acct_full').classes('grow')
                        ui.input(placeholder='memo', value=line.memo) \
                            .bind_value(line, 'memo').classes('w-44')
                        ui.input(placeholder='0.00', value=line.amount) \
                            .bind_value(line, 'amount') \
                            .on('blur', balance_view.refresh).classes('w-28')

            ui.separator()

            # actions
            with ui.row().classes('items-center w-full gap-2'):
                if state.entry.split or state.entry.size > 2:
                    ui.button('+ line', on_click=on_add_line).props('outline')
                    ui.button('- line', on_click=on_remove_line).props('outline')
                else:
                    ui.button('Split', on_click=on_add_line).props('outline')
                balance_view()
                ui.button('Add to journal', on_click=on_add).classes('ml-auto')

    # ---- build the setup controls ---------------------------------------
    with ui.row().classes('items-center gap-4'):
        import_select = ui.select(state.import_files(), label='Import file',
                                  with_input=True,
                                  on_change=on_import_change).classes('w-72')
        assoc_select = ui.select([], label='Associated account').classes('w-72')
        ui.button('Start', on_click=on_start)
        progress_label = ui.label('').classes('text-gray-500 ml-4')

    ui.separator()
    editor()


#==============================================================================
# Launch
#==============================================================================
if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='SDET',
        reload=False,
        show=os.environ.get('SDET_SHOW', '1') == '1',
        port=8080,
    )
