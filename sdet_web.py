#------------------------------------------------------------------------------
# File:
#   sdet_web.py
#
# Description:
#   NiceGUI front-end for the Simple Double Entry Tool - a thin presentation
#   layer over the pure-logic core/ package (Accounts / Ledger / importer).
#
#   Two tabs:
#     * Categorize - master/detail queue: the left list shows every imported
#       transaction not yet journalled, colour-coded by suggestion confidence;
#       click one to load it into the editor on the right. "Add all exact
#       matches" clears the confident ones in one shot.
#     * Journal - browse recent entries and edit (re-categorise) any of them.
#
#   NiceGUI notes for a tkinter refugee: you create widgets and give them
#   on_click / on_change handlers, just like tkinter. Layout is by creation
#   order inside containers (ui.row / ui.column / ui.card), not a grid.
#   @ui.refreshable marks a block of UI you can rebuild by calling .refresh().
#   .bind_value(obj, 'attr') two-way-binds a widget to an object attribute.
#
#   Run it with:   python sdet_web.py      (then open http://localhost:8080)
#------------------------------------------------------------------------------

import os
import sys

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
    ''' Holds the backend objects and the entry currently being edited.
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

    def valid_assoc(self, assoc):
        return self.accounts.is_account_valid(assoc or '')

    # -- import / queue ---------------------------------------------------

    def select_import(self, filename):
        ''' Load an import file; returns its candidate associated accounts. '''
        path = c.DATA_FOLDER + filename
        self.import_result = load_transactions(path, self.config)
        return self.import_result.assoc_accts

    def _first_line(self, txn, assoc):
        return Line(date=txn.date, txn_id=txn.txn_id, desc=txn.desc, memo='',
                    acct_full=assoc, acct_short=self.accounts.short_name(assoc),
                    amount=txn.amount)

    def pending(self):
        ''' Imported transactions not yet in the journal. '''
        if not self.import_result or not self.ledger:
            return []
        return [t for t in self.import_result.transactions
                if not self.ledger.transaction_exists(t.txn_id)]

    def pending_with_flags(self, assoc):
        ''' [(txn, flag)] for the queue, classified cheaply (index, no fuzzy). '''
        return [(txn, self.ledger.classify(self._first_line(txn, assoc)))
                for txn in self.pending()]

    def load_transaction(self, txn, assoc):
        ''' Load one imported transaction + its full suggestion into the editor. '''
        self.match_flag, self.entry = \
            self.ledger.find_suggested_entry(Entry([self._first_line(txn, assoc)]))

    # -- editing lines ----------------------------------------------------

    def add_blank_line(self):
        first = self.entry[0]
        self.entry.add_line(Line(date=first.date, txn_id=first.txn_id,
                                 desc=first.desc))

    def remove_last_line(self):
        if self.entry.size > 2:
            self.entry.remove_line(self.entry.size - 1)

    def _validate(self):
        ''' Returns an error message, or None if the current entry is good. '''
        if self.entry is None:
            return 'No transaction loaded.'
        for line in self.entry:
            line.acct_short = self.accounts.short_name(line.acct_full or '')
            if not self.accounts.is_account_valid(line.acct_full or ''):
                return f'Invalid account: {line.acct_full or "(blank)"}'
        try:
            if not self.entry.is_balanced:
                return f'Not balanced - off by {self.entry.balance:.2f}'
        except ValueError:
            return 'One or more amounts are not valid numbers.'
        return None

    def commit_new(self):
        ''' Validate + append the current entry. Returns (ok, message). '''
        err = self._validate()
        if err:
            return False, err
        self.ledger.add_entry(self.entry)
        self.ledger.save()
        self.entry = None
        self.match_flag = None
        return True, 'Added to journal.'

    def commit_edit(self):
        ''' Validate + replace the current (existing) entry. Returns (ok, msg). '''
        err = self._validate()
        if err:
            return False, err
        self.ledger.replace_entry(self.entry)
        self.ledger.save()
        return True, 'Saved.'

    # -- journal browsing -------------------------------------------------

    def load_existing(self, txn_id):
        self.entry = self.ledger.get_entry(txn_id)
        self.match_flag = None


state = AppState()


#==============================================================================
# Shared helpers
#==============================================================================
_BADGE = {
    EXACT:   ('Exact match',    'green'),
    PARTIAL: ('Suggestion',     'amber'),
    NONE:    ('No match - new', 'grey'),
}
_FLAG_CSS = {EXACT: '#16a34a', PARTIAL: '#d97706', NONE: '#9ca3af'}


def _safe_balance():
    try:
        return state.entry.balance
    except (ValueError, AttributeError):
        return None


def _balance_label():
    ''' A coloured balance readout for the current entry. '''
    bal = _safe_balance()
    if bal is None:
        return ui.label('Balance: -').classes('text-red-600 font-mono')
    ok = abs(bal) < 0.005
    colour = 'text-green-600' if ok else 'text-red-600'
    return ui.label(f'Balance: {bal:.2f}').classes(colour + ' font-mono')


def _line_headers():
    ''' Column captions aligned to the inputs produced by _render_lines. '''
    with ui.row().classes('items-center w-full gap-2 text-xs uppercase '
                          'tracking-wide text-gray-400'):
        ui.label('#').classes('w-5')
        ui.label('Account').classes('grow')
        ui.label('Memo').classes('w-40')
        ui.label('Amount').classes('w-24 text-right pr-2')


def _render_lines(entry, on_amount_blur):
    ''' Render posting rows aligned to _line_headers(). Line 0 (the associated
        / bank account) is shaded and read-only; lines 1+ get editable
        account / memo / amount inputs. '''
    for i, line in enumerate(entry):
        row = ui.row().classes('items-center w-full gap-2')
        if i == 0:
            row.classes('bg-gray-100 rounded')               # the source account
        with row:
            ui.label(str(i)).classes('w-5 text-gray-400')
            if i == 0:
                ui.label(line.acct_full).classes('grow')
                ui.element('div').classes('w-40')             # memo spacer
                ui.label(line.amount).classes('font-mono w-24 text-right pr-2')
            else:
                ui.select(state.account_options, with_input=True,
                          value=line.acct_full or None) \
                    .bind_value(line, 'acct_full').classes('grow')
                ui.input(placeholder='memo', value=line.memo) \
                    .bind_value(line, 'memo').classes('w-40')
                ui.input(placeholder='0.00', value=line.amount) \
                    .bind_value(line, 'amount') \
                    .on('blur', on_amount_blur).classes('w-24')


def _entry_summary(entry):
    ''' One-line description of an entry's offsetting side, for the list. '''
    if entry.size == 2:
        return f'{entry[1].acct_full}  {entry[1].amount}'
    accts = ', '.join(l.acct_short for l in list(entry)[1:])
    return f'split ({entry.size} lines): {accts}'


#==============================================================================
# Categorize tab - master/detail queue
#==============================================================================
def build_categorize():
    # ---- handlers (reference widgets created just below; resolved at call) --
    def current_assoc():
        return assoc_select.value

    def on_import_change():
        if not import_select.value:
            return
        try:
            accts = state.select_import(import_select.value)
        except ImportStyleError:
            ui.notify('File does not match any known import style', type='negative')
            return
        except FileNotFoundError:
            ui.notify('Import file not found', type='negative')
            return
        assoc_select.set_options(accts, value=accts[0] if accts else None)
        state.entry = None
        refresh_all()

    def on_assoc_change():
        state.entry = None
        refresh_all()

    def on_pick(txn):
        state.load_transaction(txn, current_assoc())
        editor.refresh()
        queue_view.refresh()

    def on_add():
        ok, msg = state.commit_new()
        ui.notify(msg, type='positive' if ok else 'negative')
        if ok:
            pend = state.pending()
            if pend:
                state.load_transaction(pend[0], current_assoc())   # auto-advance
            refresh_all()

    def on_add_line():
        state.add_blank_line()
        editor.refresh()

    def on_remove_line():
        state.remove_last_line()
        editor.refresh()

    def refresh_all():
        queue_view.refresh()
        editor.refresh()
        progress_label.refresh()

    # ---- refreshable pieces --------------------------------------------
    @ui.refreshable
    def progress_label():
        n = len(state.pending())
        ui.label(f'{n} transaction(s) remaining').classes('text-gray-500')

    @ui.refreshable
    def queue_view():
        if not state.import_result:
            ui.label('Pick an import file to see its transactions.') \
                .classes('text-gray-500')
            return
        if not state.valid_assoc(current_assoc()):
            ui.label('Pick a valid associated account.').classes('text-gray-500')
            return

        rows = state.pending_with_flags(current_assoc())
        if not rows:
            ui.label('All transactions accounted for.').classes('text-green-600')
            return

        with ui.scroll_area().classes('h-[28rem] w-full border rounded'):
            for txn, flag in rows:
                selected = (state.entry is not None
                            and state.entry[0].txn_id == txn.txn_id)
                row = ui.row().classes(
                    'items-center w-full gap-2 cursor-pointer px-2 py-1 '
                    + ('bg-blue-100' if selected else 'hover:bg-gray-100'))
                row.style(f'border-left: 4px solid {_FLAG_CSS.get(flag, "#ccc")}')
                row.on('click', lambda t=txn: on_pick(t))
                with row:
                    ui.label(txn.date).classes('font-mono text-xs w-24')
                    ui.label(txn.desc).classes('grow text-sm').style(
                        'overflow:hidden; text-overflow:ellipsis; white-space:nowrap')
                    ui.label(txn.amount).classes('font-mono text-xs w-20 text-right')

    @ui.refreshable
    def editor():
        if state.entry is None:
            ui.label('Select a transaction from the queue.').classes('text-gray-500')
            return

        first = state.entry[0]
        with ui.card().classes('w-full'):
            # -- transaction header: caption + badge, then the headline values
            with ui.row().classes('items-center w-full justify-between'):
                ui.label('TRANSACTION').classes(
                    'text-xs uppercase tracking-wide text-gray-400')
                text, colour = _BADGE.get(state.match_flag, ('', 'grey'))
                ui.badge(text).props(f'color={colour}')
            with ui.row().classes('items-baseline w-full gap-3'):
                ui.label(first.date).classes('font-mono text-sm text-gray-500')
                ui.label(first.desc).classes('text-lg font-bold grow')
                ui.label(first.amount).classes('font-mono text-lg')

            ui.separator().classes('my-2')

            # -- postings: caption, column headers, then the lines
            ui.label('POSTINGS').classes(
                'text-xs uppercase tracking-wide text-gray-400')
            _line_headers()
            _render_lines(state.entry, balance_view.refresh)

            ui.separator().classes('my-2')

            # -- footer: split controls (left), balance, commit (right)
            with ui.row().classes('items-center w-full gap-2'):
                if state.entry.split or state.entry.size > 2:
                    ui.button('+ line', on_click=on_add_line).props('flat dense')
                    ui.button('- line', on_click=on_remove_line).props('flat dense')
                else:
                    ui.button('Split', on_click=on_add_line).props('flat dense')
                balance_view()
                ui.button('Add to journal', on_click=on_add) \
                    .props('color=primary').classes('ml-auto')

    @ui.refreshable
    def balance_view():
        _balance_label()

    # ---- layout ---------------------------------------------------------
    with ui.row().classes('items-center gap-4 w-full'):
        import_select = ui.select(state.import_files(), label='Import file',
                                  with_input=True,
                                  on_change=on_import_change).classes('w-72')
        assoc_select = ui.select([], label='Associated account',
                                 on_change=on_assoc_change).classes('w-72')
        progress_label()

    ui.separator()

    # Current transaction on the LEFT, the live queue on the RIGHT.
    with ui.row().classes('w-full gap-4 no-wrap items-start'):
        with ui.column().classes('grow'):
            editor()
        with ui.column().classes('w-5/12'):
            queue_view()


#==============================================================================
# Journal tab - browse + edit past entries
#==============================================================================
def build_journal():
    columns = [
        {'name': 'date', 'label': 'Date', 'field': 'date',
         'align': 'left', 'sortable': True},
        {'name': 'desc', 'label': 'Description', 'field': 'desc',
         'align': 'left', 'sortable': True},
        {'name': 'summary', 'label': 'Categorisation', 'field': 'summary',
         'align': 'left'},
    ]

    def build_rows():
        ''' Every entry, most-recent first, as plain dicts for the table. '''
        return [{'txn_id': e[0].txn_id, 'date': e[0].date,
                 'desc': e[0].desc, 'summary': _entry_summary(e)}
                for e in reversed(state.ledger.history())]

    def refresh_table():
        table.rows = build_rows()
        table.update()

    def open_edit_dialog(txn_id):
        state.load_existing(txn_id)
        if state.entry is None:
            ui.notify('Entry not found', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('w-[44rem]'):
            ui.label(f'Edit entry - {state.entry[0].desc}').classes('font-bold')
            ui.label(f'{state.entry[0].date}   {state.entry[0].txn_id}') \
                .classes('text-xs text-gray-500 font-mono')
            ui.separator()

            @ui.refreshable
            def dlg_body():
                _line_headers()
                _render_lines(state.entry, dlg_balance.refresh)

            @ui.refreshable
            def dlg_balance():
                _balance_label()

            def dlg_add_line():
                state.add_blank_line()
                dlg_body.refresh()

            def dlg_remove_line():
                state.remove_last_line()
                dlg_body.refresh()

            def on_save():
                ok, msg = state.commit_edit()
                ui.notify(msg, type='positive' if ok else 'negative')
                if ok:
                    dialog.close()
                    refresh_table()

            dlg_body()
            ui.separator()
            with ui.row().classes('items-center w-full gap-2'):
                ui.button('+ line', on_click=dlg_add_line).props('flat dense')
                ui.button('- line', on_click=dlg_remove_line).props('flat dense')
                dlg_balance()
                ui.button('Cancel', on_click=dialog.close).props('flat').classes('ml-auto')
                ui.button('Save', on_click=on_save).props('color=primary')

        dialog.open()

    # ---- layout ---------------------------------------------------------
    # A Quasar table: virtual-scrolled (handles the whole journal), with
    # client-side filtering bound to the search box (instant, no round-trip).
    # Clicking any row opens its edit dialog.
    ui.label('Click a row to edit its categorisation.') \
        .classes('text-gray-500 text-xs')
    filter_input = ui.input('Filter (description / account / date)').classes('w-96')
    table = ui.table(columns=columns, rows=build_rows(), row_key='txn_id',
                     pagination=0).classes('w-full cursor-pointer') \
        .props('flat bordered dense virtual-scroll').style('max-height: 72vh')

    # Quasar row-click args are [event, row, index]; row is our dict.
    table.on('rowClick', lambda e: open_edit_dialog(e.args[1]['txn_id']))
    filter_input.bind_value(table, 'filter')


#==============================================================================
# The page
#==============================================================================
@ui.page('/')
def index():
    if state.error:
        ui.label('Startup error').classes('text-2xl text-red-600')
        ui.label(state.error)
        return

    with ui.header().classes('items-center'):
        ui.label('S-DET').classes('text-xl font-bold')
        ui.label('Simple Double Entry Tool').classes('text-sm opacity-70 ml-2')

    with ui.tabs() as tabs:
        cat_tab = ui.tab('Categorize')
        jrnl_tab = ui.tab('Journal')

    with ui.tab_panels(tabs, value=cat_tab).classes('w-full'):
        with ui.tab_panel(cat_tab):
            build_categorize()
        with ui.tab_panel(jrnl_tab):
            build_journal()


#==============================================================================
# Launch
#==============================================================================
if __name__ in {'__main__', '__mp_main__'}:
    # Auto-open the browser normally; '--no-show' (or SDET_SHOW=0) suppresses
    # it for headless/preview runs.
    show = os.environ.get('SDET_SHOW', '1') == '1' and '--no-show' not in sys.argv
    ui.run(
        title='SDET',
        reload=False,
        show=show,
        port=8080,
    )
