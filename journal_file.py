#------------------------------------------------------------------------------
# File:
#   journal_file.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file creates a class which represents the Journal.csv file
#
#------------------------------------------------------------------------------

import csv
import pandas as pd
import constants as c
from decimal import Decimal, ROUND_HALF_UP

class JournalFile():
    ''' Class which manages the journal file. '''

    active = False
    simple = True

    def Setup(self):
        ''' Setup Journal.csv file object '''
        self._ResetData()

        #----------------------------------------------------------------------
        # Make sure journal file exists
        #----------------------------------------------------------------------
        try:
            with open(c.JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

        except FileNotFoundError:
            log = 'Journal.csv does not exist in current directory', 'error'
            return c.BAD, log

        except PermissionError:
            log = 'Journal.csv needs to be closed', 'error'
            return c.BAD, log

        #----------------------------------------------------------------------
        # Normalize data
        #----------------------------------------------------------------------
        lineC = c.JRNL_LINE
        dateC = c.JRNL_DATE
        descC = c.JRNL_DSCRP
        amntC = c.JRNL_AMOUNT
        hashC = c.JRNL_ID
 
        df = pd.read_csv(c.JOURNAL_FP)

        # Date data (yyyy-mm-dd)
        df[dateC] = pd.to_datetime(df[dateC], format='mixed', dayfirst=False)
        df[dateC] = df[dateC].dt.strftime('%Y-%m-%d')

        # Amount data (decimal to 2 places then convert to string)
        tmpAmnts = []
        for value in df[amntC]:
            dec = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            tmpAmnts.append(dec)

        df[amntC] = tmpAmnts
        df[amntC] = df[amntC].astype(str)

        # Description data (only take first 50 characters)
        df[descC] = df[descC].str.strip().str[:50]

        # Order by date and description
        df = df.sort_values(by=[dateC, descC, hashC, lineC])

        # Write back normalized data
        df.to_csv(c.JOURNAL_FP, index=False)

        # Looks good
        self.active = True
        log = 'Journal.csv setup is successful', 'default'
        return c.GOOD, log

    def _ResetData(self):
        self.active = False
        self.simple = True

    def DoesTransactionExist(self, hash):
        ''' Check if given hash already exists in journal '''
        try:
            # Create dataframe using import file data
            df = pd.read_csv(c.JOURNAL_FP)

        except FileNotFoundError:
            raise

        if (hash in df[c.JRNL_ID].values):
            return True
        else:
            return False

    def FindSuggestedEntry(self, l):
        '''
        Find the last entry that matches the given desc / amnt / acct.

        Iterate through dataframe in reverse. If match on desc, amnt, and acct,
        load suggested entry with entire entry found.

        If only match on desc and acct, load suggested entry as a simple entry
        (one line) with reversed amount and suggested account in second line.

        If no match on desc and acct, don't load any more lines to suggested
        entry.
        '''
        # Reset current entry
        self.entry = []
        self.simple = True

        try:
            df = pd.read_csv(c.JOURNAL_FP)

        except FileNotFoundError:
            log = 'Journal.csv does not exist', 'error'
            return c.BAD, log

        # Load 0th line to entry
        self.entry.append(l)

        # Have a go at exact match first
        for index, row in df.iloc[::-1].iterrows():
            jDesc = row[c.JRNL_DSCRP]
            jAmnt = float(row[c.JRNL_AMOUNT])
            jAcct = row[c.JRNL_ACCT_NAME_F]
            jHash = row[c.JRNL_ID]

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF) and (jAmnt == l.amnt):
                # Exact match found, load entry data
                count = row[c.JRNL_LINE]
                i = 1
                for i in range(count,0,-1):
                    print(index-i)
                    newLine = Line()
                    newLine.date = l.date
                    newLine.hash = l.hash
                    newLine.desc = l.desc
                    newLine.memo = df.loc[index-i, c.JRNL_MEMO]
                    newLine.acctF = df.loc[index-i, c.JRNL_ACCT_NAME_F]
                    newLine.acctS = df.loc[index-i, c.JRNL_ACCT_NAME]
                    newLine.amnt = df.loc[index-i, c.JRNL_AMOUNT]
                    tmpHash = df.loc[index+i+1, c.JRNL_ID]
                    self.entry.append(newLine)
                    i = i + 1

        if (len(self.entry) > 1):
            if (len(self.entry) > 2):
                self.simple = False

            log = 'Exact match found', 'default'
            return c.GOOD, log

        # Go for partial match
        newLine = Line()
        newLine.date = l.date
        newLine.hash = l.hash
        newLine.desc = l.desc

        # Reversed Amount
        if ('-' in l.amnt):
            newLine.amnt = l.amnt.replace('-', '')
        else:
            newLine.amnt = '-' + l.amnt

        for index, row in df.iloc[::-1].iterrows():
            jDesc = row[c.JRNL_DSCRP]
            jAmnt = row[c.JRNL_AMOUNT]
            jAcct = row[c.JRNL_ACCT_NAME_F]
            jHash = row[c.JRNL_ID]

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF):
                # Partial match found, load reversed amount and suggested acct
                newLine.acctF = df.loc[index+1, c.JRNL_ACCT_NAME_F]
                newLine.acctS = df.loc[index+1, c.JRNL_ACCT_NAME]

        # Append to entry
        self.entry.append(newLine)

        if (len(self.entry) > 1):
            log = 'Partial match found', 'default'
            return c.GOOD, log

        log = 'No match found', 'default'
        return c.GOOD, log

    def AddEntryToJournal(self):
        ''' Add current entry to journal '''
        try:
            # Create dataframe using import file data
            df = pd.read_csv(c.JOURNAL_FP)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        lineNum = 0
        for l in self.entry:
            newData = [lineNum, str(l.date), str(l.hash), str(l.desc), str(l.memo),  \
                       str(l.acctF), str(l.acctS), str(l.amnt)]
            lineNum = lineNum + 1
            
            df.loc[len(df)] = newData

        df.to_csv(c.JOURNAL_FP, index=False)
        log = 'Added to journal successfully', 'default'
        return c.GOOD, log


class Line():
    ''' Represents a single line of an entry in the journal '''

    date = ' '
    hash = ' '
    desc = ' '
    memo = ' '
    acctF = ' '
    acctS = ' '
    amnt = ' '

    def __str__(self):
        return "date=%s, hash=%s, desc=%s, memo=%s, acctF=%s, acctS=%s, "   \
            "amnt=%s" % (self.date, self.hash, self.desc, self.memo,        \
                         self.acctF, self.acctS, self.amnt)