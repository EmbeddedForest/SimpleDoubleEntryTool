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
import hashlib
import pandas as pd
import constants as c
from decimal import Decimal, ROUND_HALF_UP

class JournalFile():

    # Object data
    importIndex = 0
    suggestedAcct = ' '
    active = False
    simple = True

    def SetupFile(self):
        ''' Setup Journal.csv file object '''

        #----------------------------------------------------------------------
        # Cleanup previous data
        #----------------------------------------------------------------------
        self.importIndex = 0
        self.suggestedAcct = ' '
        self.active = False
        self.simple = True

        #----------------------------------------------------------------------
        # Make sure journal file exists
        #----------------------------------------------------------------------
        try:
            with open(c.JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                cols = list(next(reader).keys())

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
        df[dateC] = pd.to_datetime(df[dateC], format='%Y-%m-%d')
        # df[dateC] = pd.to_datetime(df[dateC], format='%d/%m/%Y')
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


    def _CheckIfFileExists(self):
        ''' Check that Journal.csv file exists '''

        try:
            f = open(c.JOURNAL_FP, newline="", encoding="utf-8-sig")
            f.close()

        except FileNotFoundError:
            log = 'Journal.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        log = 'Journal.csv file does exist', 'default'
        return c.GOOD, log


    def _CheckIfColumnsExists(self):
        ''' Check if necessary column headers exist '''

        try:
            with open(c.JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except FileNotFoundError:
            log = 'Journal.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        if (set(headerList) != set(c.JRNL_HEADERS)):
            log = 'Journal.csv is not syntactically correct.', 'error'
            return c.BAD, log

        # Looks good
        log = 'Journal.csv is legit', 'default'
        return c.GOOD, log


    def DoesTransactionExist(self, hash):
        ''' Check if given hash already exists in journal '''

        try:
            # Create dataframe using import file data
            df = pd.read_csv('Journal.csv')

            # Create new df that is ordered by date and description
            newDf = df.sort_values(by=['Date', 'Description'])

            # Write back reordered data to Journal
            newDf.to_csv('Journal.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        if (hash in newDf['TransactionID'].values):
            return True
        else:
            return False


    def FindSuggestedAccount(self, iDesc, iAmnt):
        '''
        Find the last account used that matches the given description and
        amount.

        If description and amount match, use that account but if no account
        found for exact amount and description, used description match only.

        Note: The Journal is reordered by date/description everytime this
        function executes.
        '''

        try:
            # Create dataframe using import file data
            df = pd.read_csv('Journal.csv')

            # Make sure date is in correct format before sorting
            # df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

            # Create new df that is ordered by date and description
            newDf = df.sort_values(by=['Date', 'Description', 'TransactionID', 'Initiator'])

            # Write back reordered data to Journal
            newDf.to_csv('Journal.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        self.suggestedAcct = ' '

        for index, row in newDf.iterrows():
            jDesc = row['Description']
            jAmnt = row['Amount Num.']
            jAcct = row['Full Account Name']

            jAmnt = round(jAmnt, 2)

            if (jDesc == iDesc) and (str(jAmnt) == iAmnt):
                self.suggestedAcct = jAcct
            elif (self.suggestedAcct == ' ') and (jDesc == iDesc):
                self.suggestedAcct = jAcct

        log = 'All good', 'default'
        return c.GOOD, log


    def FindSuggestedEntry(self, l):
        '''
        Find the last entry that matches the given desc / amnt / acct.

        Iterate through dataframe in reverse. If match on desc, amnt, and acct,
        load suggested entry with entire entry found.

        If only match on desc and acct, load suggested entry as a simple entry
        (one line) with reversed amount and suggested account in second line.

        If no match on desc and acct, don't load any more lines to suggested
        entry.

        Note: The Journal is reordered by date/description everytime this
        function executes.
        '''

        # Clear current entry
        self.entry = []
        self.simple = True

        try:
            # Create dataframe using import file data
            df = pd.read_csv('Journal.csv')

            # # Create new df that is ordered
            # newDf = df.sort_values(by=['Date', 'Description', 'TransactionID', 'Initiator'])

            # # Write back reordered data to Journal
            # newDf.to_csv('Journal.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        # Load 0th line to entry
        self.entry.append(l)

        # Have a go at exact match first
        for index, row in df.iloc[::-1].iterrows():
            jDesc = row['Description']
            jAmnt = float(row['Amount Num.'])
            jAcct = row['Full Account Name']
            jHash = row['TransactionID']

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF) and (jAmnt == l.amnt):
                # Exact match found, load entry data
                count = row['Line']
                i = 1
                for i in range(count,0,-1):
                    print(index-i)
                    newLine = Line()
                    newLine.date = l.date
                    newLine.hash = l.hash
                    newLine.desc = l.desc
                    newLine.memo = df.loc[index-i, 'Memo']
                    newLine.acctF = df.loc[index-i, 'Full Account Name']
                    newLine.acctS = df.loc[index-i, 'Account Name']
                    newLine.amnt = df.loc[index-i, 'Amount Num.']
                    tmpHash = df.loc[index+i+1, 'TransactionID']
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
            jDesc = row['Description']
            jAmnt = row['Amount Num.']
            jAcct = row['Full Account Name']
            jHash = row['TransactionID']

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF):
                # Partial match found, load reversed amount and suggested acct
                newLine.acctF = df.loc[index+1, 'Full Account Name']
                newLine.acctS = df.loc[index+1, 'Account Name']

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
            df = pd.read_csv('Journal.csv')

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        lineNum = 0
        for l in self.entry:
            newData = [lineNum, str(l.date), str(l.hash), str(l.desc), str(l.memo),  \
                       str(l.acctF), str(l.acctS), str(l.amnt)]
            lineNum = lineNum + 1
            
            df.loc[len(df)] = newData

        df.to_csv('Journal.csv', index=False)
        log = 'Added to journal successfully', 'default'
        return c.GOOD, log


    def _AddHashes(self):
        '''
        ONE TIME USE

        Adds hashes to journal without TransactionIDs.

        If newEntry == True, create new hash, set newEntry to False
        If newEntry == False, use previous hash
            # If sum == 0, set newEntry to True
            # If sum != 0, do nothing
        '''

        try:
            # Create dataframe using import file data
            df = pd.read_csv('Journal.csv')

            # Make sure date is in correct format before sorting
            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

            # Create new df that is ordered by date and description
            newDf = df.sort_values(by=['Date', 'Description'])

            # Create temp file with ordered data
            newDf.to_csv('JournalTemp.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        # Give each transaction unique hash
        sum = 0
        count = 0
        hashList = []
        prevHash = ' '
        newEntry = True

        for index, row in newDf.iterrows():
            date = row['Date']
            desc = row['Description']
            amnt = row['Amount Num.']

            sum = sum + round(amnt, 2)

            if (newEntry == True):
                newEntry = False

                idString = str(date) + desc + str(amnt) + str(count)
                encodedString = idString.encode('utf-8')
                newHash = hashlib.md5(encodedString).hexdigest()

                if (newHash == prevHash):
                    count = count + 1
                    idString = str(date) + desc + str(amnt) + str(count)
                    encodedString = idString.encode('utf-8')
                    newHash = hashlib.md5(encodedString).hexdigest()
                else:
                    count = 0
                    idString = str(date) + desc + str(amnt) + str(count)
                    encodedString = idString.encode('utf-8')
                    newHash = hashlib.md5(encodedString).hexdigest()
            else:
                newHash = prevHash

                if (round(sum, 2) == 0):
                    newEntry = True

            print(round(sum, 2))

            hashList.append(newHash)
            prevHash = newHash

        # Insert hashes into temp file
        newDf['TransactionID'] = hashList
        newDf.to_csv('JournalTemp.csv', index=False)



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


class Entry():
    ''' Represents a full entry in the journal '''

    lines = []
    sum = 0
    index = 0

    def Clear(self):
        self.lines = []
        self.sum = 0
        self.index = 0

    def AddFirstLine(self, line):
        self.lines.insert(0, line)
        self.index = 1
        self.sum = float(line.amnt)

        # print(self.lines[0].date, self.lines[0].hash, self.lines[0].desc, self.lines[0].memo, self.lines[0].acctF, self.lines[0].acctS, self.lines[0].amnt, self.sum)

    def AddSimpleLine(self, line):
        # Remove existing splits
        for i in range(self.index, 0, -1):
            self.lines.pop(self.index)

        # Add in simple line
        self.index = 1
        self.lines.insert(self.index, line)

        # Reset sum
        self.sum = 0
        self.sum = float(self.lines[0].amnt) + float(self.lines[1].amnt)

    def AddSplitLine(self, line):
        self.lines.insert(self.index, line)
        self.index = self.index + 1
        self.sum = self.sum + float(line.amnt)

    def RemoveSplitLine(self):
        self.sum = self.sum - float(self.lines[self.index].amnt)
        self.lines.pop(self.index)
        self.index = self.index - 1