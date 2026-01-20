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
import constants as c


class ImportFile():

    # def __init__(self):
    #     self._GetAllDataFileNames()


    def SetupFile(self, filePath):
        ''' Set up specified import file '''

        # Cleanup previous data
        self.filePath = ' '
        self.dateCol = ' '
        self.descCol = ' '
        self.amntCol = ' '
        self.dateCur = ' '
        self.descCur = ' '
        self.amntCur = ' '
        self.dateData = []
        self.descData = []
        self.amntData = []
        self.numTrans = 0

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

        # Update transaction data lists
        retVal, log = self._UpdateDataLists()
        if (retVal == c.BAD):
            return c.BAD, log

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

        # Looks good
        log = 'Import columns updated successfully'
        return c.GOOD, log


    def _UpdateDataLists(self):
        ''' Updates data lists with latest transaction data '''

        self.dateData = []
        self.descData = []
        self.amntData = []
        self.numTrans = 0

        try:
            with open(self.filePath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.dateData.append(row[self.dateCol])
                    self.descData.append(row[self.descCol])
                    self.amntData.append(row[self.amntCol])
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

