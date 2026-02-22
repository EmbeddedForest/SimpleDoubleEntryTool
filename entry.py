#------------------------------------------------------------------------------
# File:
#   entry.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   02/19/2026
#
# Description:
#   This file creates a class which represents an entry in the journal/ledger.
#
#------------------------------------------------------------------------------

import constants as c

class Entry():
    ''' Class to represent the entry in the Journal '''

    entry = []
    size = 0
    split = False

    def __init__(self):
        self.entry = []
        self.size = 0
        self.split = False

    def __str__(self):
        msg = self.GetHeader()
        msg = msg + self.GetDataAsText()
        return msg

    def __iter__(self):
        for line in self.entry:
            yield line

    def __getitem__(self, key):
        if isinstance(key, int):
            # Handle integer indexing
            return self.entry[key]
        elif isinstance(key, slice):
            # Handle slice objects (e.g., my_object[1:4])
            return self.entry[key]
        else:
            raise TypeError(f"Index not supported for type: {type(key)}")

    def AddLine(self, l: Line):
        self.entry.append(l)
        self.size = self.size + 1

        if (self.size > 2):
            self.split = True
        else:
            self.split = False

    def RemoveLine(self, index):
        if (index >= self.size):
            return

        self.entry.pop(index)
        self.size = self.size - 1

        if (self.size > 2):
            self.split = True
        else:
            self.split = False

    def Clear(self):
        self.entry = []
        self.size = 0
        self.split = False

    def GetHeader(self):
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

        return msg

    def GetDataAsText(self):
        # Build entry
        msg = ''
        lineNum = 0
        for j in self.entry:
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

        return msg


class Line():
    ''' Represents a single line of an entry in the journal '''

    date  = ''
    hash  = ''
    desc  = ''
    memo  = ''
    acctF = ''
    acctS = ''
    amnt  = ''

    def __str__(self):
        return "date=%s, hash=%s, desc=%s, memo=%s, acctF=%s, acctS=%s, "   \
            "amnt=%s" % (self.date, self.hash, self.desc, self.memo,        \
                         self.acctF, self.acctS, self.amnt)