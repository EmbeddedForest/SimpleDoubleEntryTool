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
from entry import Line
from entry import Entry
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
 
        df = pd.read_csv(c.JOURNAL_FP, index_col=False)

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

    def FindSuggestedEntry(self, newEntry: Entry):
        '''
        Find the last entry that matches the given desc / amnt / acct.

        Iterate through dataframe in reverse. If match on desc, amnt, and acct,
        load suggested entry with entire entry found.

        If only match on desc and acct, load suggested entry as a simple entry
        (one line) with reversed amount and suggested account in second line.

        If no match on desc and acct, don't load any more lines to suggested
        entry.
        '''
        try:
            df = pd.read_csv(c.JOURNAL_FP)

        except FileNotFoundError:
            return c.BAD, newEntry

        # Grab first line from entry
        l = newEntry.entry[0]

        # Have a go at exact match first
        for index, row in df.iloc[::-1].iterrows():
            jDesc = row[c.JRNL_DSCRP]
            jAmnt = float(row[c.JRNL_AMOUNT])
            jAcct = row[c.JRNL_ACCT_NAME_F]
            jHash = row[c.JRNL_ID]

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF) and (jAmnt == l.amnt):
                # Exact match found, load entry with data
                count = row[c.JRNL_LINE]
                i = 1
                for i in range(count,0,-1):
                    newLine = Line()
                    newLine.date = l.date
                    newLine.hash = l.hash
                    newLine.desc = l.desc
                    newLine.memo = df.loc[index-i, c.JRNL_MEMO]
                    newLine.acctF = df.loc[index-i, c.JRNL_ACCT_NAME_F]
                    newLine.acctS = df.loc[index-i, c.JRNL_ACCT_NAME]
                    newLine.amnt = df.loc[index-i, c.JRNL_AMOUNT]
                    tmpHash = df.loc[index+i+1, c.JRNL_ID]
                    newEntry.AddLine(newLine)
                    i = i + 1

                # Exact match found
                return 'ExactMatch', newEntry

        # Go for simple partial match
        newLine = Line()
        newLine.date = l.date
        newLine.hash = l.hash
        newLine.desc = l.desc
        newLine.acctF = ''
        newLine.acctS = ''

        # Reverse Amount
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
                # Partial match found, suggested acct
                newLine.acctF = df.loc[index+1, c.JRNL_ACCT_NAME_F]
                newLine.acctS = df.loc[index+1, c.JRNL_ACCT_NAME]

                # Append to entry
                newEntry.AddLine(newLine)
                return 'PartialMatch', newEntry

        # No matches found, append only what we know
        newEntry.AddLine(newLine)
        return 'NoMatch', newEntry

    def AddEntryToJournal(self, entry):
        ''' Add current entry to journal '''
        try:
            # Create dataframe using import file data
            df = pd.read_csv(c.JOURNAL_FP)

        except FileNotFoundError:
            return c.BAD

        # Add entry
        lineNum = 0
        for l in entry:
            newData = [lineNum, str(l.date), str(l.hash), str(l.desc), str(l.memo),  \
                       str(l.acctF), str(l.acctS), str(l.amnt)]
            lineNum = lineNum + 1
            
            df.loc[len(df)] = newData

        # Reorder journal
        lineC = c.JRNL_LINE
        dateC = c.JRNL_DATE
        descC = c.JRNL_DSCRP
        hashC = c.JRNL_ID
        df = df.sort_values(by=[dateC, descC, hashC, lineC])

        df.to_csv(c.JOURNAL_FP, index=False)
        return c.GOOD