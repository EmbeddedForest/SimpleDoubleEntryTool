#------------------------------------------------------------------------------
# File:
#   import_file.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file creates a class which represents the current import csv file
#
#------------------------------------------------------------------------------

import os
import csv
import hashlib
import pandas as pd
import constants as c


class ImportFile():

    # Object data
    filePath = ' '
    dateCol = ' '
    descCol = ' '
    amntCol = ' '
    hashCol = ' '
    dateCur = ' '
    descCur = ' '
    amntCur = ' '
    dateData = []
    descData = []
    amntData = []
    hashData = []
    numTrans = 0
    importIndex = 0
    active = False

    def SetupFile(self, filePath):
        ''' Set up specified import file '''

        # Cleanup previous data
        self.filePath = ' '
        self.dateCol = ' '
        self.descCol = ' '
        self.amntCol = ' '
        self.hashCol = ' '
        self.dateCur = ' '
        self.descCur = ' '
        self.amntCur = ' '
        self.dateData = []
        self.descData = []
        self.amntData = []
        self.hashData = []
        self.numTrans = 0
        self.importIndex = 0
        self.active = False

        # Check if the file actually exists
        retVal, log = self._CheckIfFileExists(filePath)
        if (retVal == c.BAD):
            return c.BAD, log

        # Check that csv file has necessary column headers
        retVal, log = self._CheckIfColumnsExists(filePath)
        if (retVal == c.BAD):
            return c.BAD, log

        # Map and update column headers
        retVal, log = self._UpdateColumnHeaders()
        if (retVal == c.BAD):
            return c.BAD, log

        # Create new temp csv
        retVal, log = self._CreateTempFile()
        if (retVal == c.BAD):
            return c.BAD, log

        # Update transaction data lists
        retVal, log = self._UpdateDataLists()
        if (retVal == c.BAD):
            return c.BAD, log

        self.active = True
        log = 'Import file setup is successful', 'default'
        return c.GOOD, log


    def _CheckIfFileExists(self, filePath):
        ''' Check that specified csv file exists '''

        if (filePath == 'Data/'):
            log = 'Selected Import csv file empty', 'error'
            return c.BAD, log

        try:
            f = open(filePath, newline="", encoding="utf-8-sig")
            f.close()

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        log = 'Import file does exist', 'default'
        return c.GOOD, log


    def _CheckIfColumnsExists(self, filePath):
        ''' Check if necessary column headers exist '''

        self.filePath = ' '

        try:
            with open(filePath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        tmp = any(head in headerList for head in c.ACCEPTED_DATE_NAMES)
        if (tmp == False):
            log = 'Import csv does not have Date column.', 'error'
            return c.BAD, log

        tmp = any(head in headerList for head in c.ACCEPTED_DESCRIPTION_NAMES)
        if (tmp == False):
            log = 'Import csv does not have Description column.', 'error'
            return c.BAD, log

        tmp = any(head in headerList for head in c.ACCEPTED_AMOUNT_NAMES)
        if (tmp == False):
            log = 'Import csv does not have Amount column.', 'error'
            return c.BAD, log

        # Safe to update filePath
        self.filePath = filePath

        log = 'Import file has necessary columns', 'default'
        return c.GOOD, log


    def _UpdateColumnHeaders(self):
        ''' Links object to necessary headers in current csv file '''

        self.dateCol = ' '
        self.descCol = ' '
        self.amntCol = ' '
        self.hashCol = ' '

        try:
            with open(self.filePath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        for dateName in c.ACCEPTED_DATE_NAMES:
            if (dateName in headerList):
                self.dateCol = dateName
                break

        for descriptionName in c.ACCEPTED_DESCRIPTION_NAMES:
            if (descriptionName in headerList):
                self.descCol = descriptionName
                break

        for amountName in c.ACCEPTED_AMOUNT_NAMES:
            if (amountName in headerList):
                self.amntCol = amountName
                break

        if (self.dateCol == ' '):
            log = 'Bad date column in import file', 'error'
            return c.BAD, log

        if (self.descCol == ' '):
            log = 'Bad description column in import file', 'error'
            return c.BAD, log

        if (self.amntCol == ' '):
            log = 'Bad amount column in import file', 'error'
            return c.BAD, log

        self.hashCol = 'TransactionID'

        # Looks good
        log = 'Import columns updated successfully'
        return c.GOOD, log


    def _CreateTempFile(self):
        '''
        Creates a temp csv file with all transactions from import file. Adds a
        unique hash for each transaction to more easily compare against entries
        in Journal.csv.

        Go row by row, create a hash using date, desc, amnt, and count.
        If previous hash is same as new hash, increment count and rehash.
        If previous hash is not same as new hash, make count = 0. Add hashes to
        TransactionID column (inserted into temp csv file).
        '''

        try:
            # Create dataframe using import file data
            df = pd.read_csv(self.filePath)

            # Make sure date is in correct format before sorting
            df[self.dateCol] = pd.to_datetime(df[self.dateCol], format='%m/%d/%Y')

            # Create new df that is ordered by date and description
            newDf = df.sort_values(by=[self.dateCol, self.descCol])

            # Create temp file with ordered data
            newDf.to_csv('ImportTemp.csv', index=False)

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        # Give each transaction unique hash
        count = 0
        prevId = ' '
        idList = []

        for index, row in newDf.iterrows():
            date = row[self.dateCol]
            desc = row[self.descCol]
            amnt = row[self.amntCol]

            idString = str(date) + desc + str(amnt) + str(count)
            encodedString = idString.encode('utf-8')
            fullHash = hashlib.md5(encodedString).hexdigest()

            if (fullHash == prevId):
                count = count + 1
                idString = str(date) + desc + str(amnt) + str(count)
                encodedString = idString.encode('utf-8')
                fullHash = hashlib.md5(encodedString).hexdigest()
            else:
                count = 0
                idString = str(date) + desc + str(amnt) + str(count)
                encodedString = idString.encode('utf-8')
                fullHash = hashlib.md5(encodedString).hexdigest()

            idList.append(fullHash)
            prevId = fullHash

        # Insert hashes into temp file
        newDf[self.hashCol] = idList
        newDf.to_csv('ImportTemp.csv', index=False)

        # Looks good
        log = 'Hashes created successfully successfully'
        return c.GOOD, log


    def _UpdateDataLists(self):
        ''' Updates data lists with latest transaction data '''

        self.dateData = []
        self.descData = []
        self.amntData = []
        self.hashData = []
        self.numTrans = 0

        try:
            with open('ImportTemp.csv', newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.dateData.append(row[self.dateCol])
                    self.descData.append(row[self.descCol])
                    self.amntData.append(row[self.amntCol])
                    self.hashData.append(row[self.hashCol])
                    self.numTrans = self.numTrans + 1

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        log = 'Import data updated successfully'
        return c.GOOD, log


    def LoadAllDataFileNames(self):
        ''' Load all csv file names from Data folder into list '''

        self.importFileList = []

        for file in os.listdir(c.DATA_FOLDER):
            if (file.lower().endswith(".csv")):
                self.importFileList.append(file)

        log = 'Import data files captured successfully'
        return c.GOOD, log

