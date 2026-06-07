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
    date:  str = ''
    hash:  str = ''   # TransactionID shared by every line of the entry
    desc:  str = ''
    memo:  str = ''
    acctF: str = ''   # Full account name, e.g. 'Expenses:Everyday:Groceries'
    acctS: str = ''   # Short account name, e.g. 'Groceries'
    amnt:  str = ''   # Signed amount as a canonical 2-decimal string


class Entry:
    ''' An ordered collection of Lines that together form one transaction. '''

    def __init__(self, lines=None):
        self.entry = []
        self.split = False
        for line in (lines or []):
            self.AddLine(line)

    # -- size / split -----------------------------------------------------

    @property
    def size(self):
        return len(self.entry)

    def _refresh_split(self):
        # split auto-tracks size. Callers may still force it True for a
        # 2-line entry being edited in the split view; the next Add/Remove
        # recomputes it, matching the original entry.py behaviour.
        self.split = self.size > 2

    # -- mutation ---------------------------------------------------------

    def AddLine(self, line: Line):
        self.entry.append(line)
        self._refresh_split()

    def RemoveLine(self, index):
        if index >= self.size:
            return
        self.entry.pop(index)
        self._refresh_split()

    def Clear(self):
        self.entry = []
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
        for line in self.entry:
            total += float(line.amnt)
        return round(total, 2)

    @property
    def is_balanced(self):
        return self.balance == 0

    # -- container protocol ----------------------------------------------

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.entry)

    def __getitem__(self, key):
        return self.entry[key]
