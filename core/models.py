#------------------------------------------------------------------------------
# File:
#   core/models.py
#
# Description:
#   Pure data models for the Simple Double Entry Tool. A Line is a single
#   account posting; an Entry is the ordered set of Lines that make up one
#   balanced transaction.
#
#   Unlike the original entry.py, all state lives on the instance (via the
#   dataclass __init__ / Entry.__init__), so two objects can never silently
#   share a mutable list the way class-level attributes did.
#------------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class Line:
    ''' A single line of a journal entry (one account posting). '''
    date:       str = ''
    txn_id:     str = ''   # TransactionID shared by every line of the entry
    desc:       str = ''
    memo:       str = ''
    acct_full:  str = ''   # e.g. 'Expenses:Everyday:Groceries'
    acct_short: str = ''   # e.g. 'Groceries'
    amount:     str = ''   # signed amount as a canonical 2-decimal string


class Entry:
    ''' An ordered collection of Lines that together form one transaction. '''

    def __init__(self, lines=None):
        self.lines = []
        self.split = False
        for line in (lines or []):
            self.add_line(line)

    # -- size / split -----------------------------------------------------

    @property
    def size(self):
        return len(self.lines)

    def _refresh_split(self):
        # split auto-tracks size. Callers may still force it True for a
        # 2-line entry being edited in the split view; the next add/remove
        # recomputes it, matching the original entry.py behaviour.
        self.split = self.size > 2

    # -- mutation ---------------------------------------------------------

    def add_line(self, line: Line):
        self.lines.append(line)
        self._refresh_split()

    def remove_line(self, index):
        if index >= self.size:
            return
        self.lines.pop(index)
        self._refresh_split()

    def clear(self):
        self.lines = []
        self.split = False

    # -- balance ----------------------------------------------------------

    @property
    def balance(self):
        '''
        Signed sum of all line amounts, rounded to cents. A balanced
        double-entry transaction sums to 0.00. Raises ValueError if any
        line amount is not a valid number (callers decide how to surface
        that, rather than a silently-wrong "balanced" result).
        '''
        total = 0.0
        for line in self.lines:
            total += float(line.amount)
        return round(total, 2)

    @property
    def is_balanced(self):
        return self.balance == 0

    # -- container protocol ----------------------------------------------

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.lines)

    def __getitem__(self, key):
        return self.lines[key]
