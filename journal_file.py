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
    latestIndex = 0
    suggestedAcct = ' '
    active = False

    def SetupFile(self):
        ''' Setup Journal.csv file object '''

        # Cleanup previous data
        self.latestIndex = 0
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


    def FindLatest(self, dateD, descD, amntD):
        ''' Find latest transaction which doesn't already exist in journal '''

        df = pd.read_csv('Journal.csv')
        sorted_df = df.sort_values(by=['Date']) 
        sorted_df.to_csv('JournalTest.csv', index=False)
        self.latestIndex = 0

        # Reorder Journal data by date (oldest to newest) and Transaction ID (second precedence)

        # Use hash comparisons

        # # Simple first, use date only
        # for i in dateD:
        #     if ()



        log = 'All good', 'default'
        return c.GOOD, log


    def FindLast(self, date, desc, amnt):
        ''' TODO '''

        # Check to see if the transaction was accounted for previously
        # Start with identical description AND amount
        # Next try full description match
        # Next try partial description match
        # Update "suggested account" variable

        self.suggestedAcct = 'Expenses:Shared:Entertainment:Streaming'


        log = 'All good', 'default'
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
