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


class JournalFile():

    # Object data
    importIndex = 0
    suggestedAcct = ' '
    active = False

    def SetupFile(self):
        ''' Setup Journal.csv file object '''

        # Cleanup previous data
        self.importIndex = 0
        self.suggestedAcct = ' '
        self.active = False

        # Check if the file actually exists
        retVal, log = self._CheckIfFileExists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Check that file has necessary column headers
        retVal, log = self._CheckIfColumnsExists()
        if (retVal == c.BAD):
            return c.BAD, log

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

        try:
            # Create dataframe using import file data
            df = pd.read_csv('Journal.csv')

            # Create new df that is ordered
            newDf = df.sort_values(by=['Date', 'Description', 'TransactionID', 'Initiator'])

            # Write back reordered data to Journal
            newDf.to_csv('Journal.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Journal csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        # Load 0th line to entry
        self.entry.append(l)

        # pd.set_option("display.max_rows", None)
        # pd.set_option("display.max_columns", None)
        # pd.set_option("display.width", None) 
        # print(newDf)

        # Have a go at exact match first
        for index, row in newDf.iloc[::-1].iterrows():
            jDesc = row['Description']
            jAmnt = row['Amount Num.']
            jAcct = row['Full Account Name']
            jHash = row['TransactionID']

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF) and (jAmnt == l.amnt):
                # Exact match found, load entry data
                tmpHash = jHash
                i = 1
                while (jHash == tmpHash):
                    # print(index+i)
                    newLine = Line()
                    newLine.date = l.date
                    newLine.hash = l.hash
                    newLine.desc = l.desc
                    newLine.memo = newDf.loc[index+i, 'Memo']
                    newLine.acctF = newDf.loc[index+i, 'Full Account Name']
                    newLine.acctS = newDf.loc[index+i, 'Account Name']
                    newLine.amnt = newDf.loc[index+i, 'Amount Num.']
                    tmpHash = newDf.loc[index+i+1, 'TransactionID']
                    self.entry.append(newLine)
                    i = i + 1

        for i in self.entry:
            print(i.date, i.desc, i.hash, i.memo, i.acctF, i.acctS, i.amnt)

        if (len(self.entry) > 1):
            print('exact')
            log = 'Exact match found', 'default'
            return c.GOOD, log

        # Go for partial match
        for index, row in newDf.iloc[::-1].iterrows():
            jDesc = row['Description']
            jAmnt = row['Amount Num.']
            jAcct = row['Full Account Name']
            jHash = row['TransactionID']

            jAmnt = str(round(jAmnt, 2))

            if (jDesc == l.desc) and (jAcct == l.acctF):
                # Partial match found, load reversed amount and suggested acct
                newLine = Line()
                newLine.date = l.date
                newLine.hash = l.hash
                newLine.desc = l.desc

                # Suggested Account
                newLine.acctF = newDf.loc[index+1, 'Full Account Name']
                newLine.acctS = newDf.loc[index+1, 'Account Name']

                # Reversed Amount
                if ('-' in l.amnt):
                    newLine.amnt = l.amnt.replace('-', '')
                else:
                    newLine.amnt = '-' + l.amnt

                # Append to entry
                self.entry.append(newLine)

        for i in self.entry:
            print(i.date, i.desc, i.hash, i.memo, i.acctF, i.acctS, i.amnt)

        if (len(self.entry) > 1):
            print('partial')
            log = 'Partial match found', 'default'
            return c.GOOD, log

        for i in self.entry:
            print(i.date, i.desc, i.hash, i.memo, i.acctF, i.acctS, i.amnt)

        print('none')
        log = 'No match found', 'default'
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
    initiator = ' '


    def Clear(self):
        self.date = []
        self.hash = []
        self.desc = []
        self.memo = []
        self.acct = []
        self.acctShort = []
        self.amnt = []
        self.initiator = []


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