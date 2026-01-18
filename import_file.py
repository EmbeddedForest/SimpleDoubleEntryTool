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

import csv
import constants as c


class ImportFile():

    def CheckFile(self, filePath):
        ''' Checks to see if specified csv import file is legit '''

        # Check that csv file exists
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

        # Check that csv file has necessary column headers
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

        # All good
        log = 'Import file is legit', 'default'
        return c.GOOD, log

    def MapColumns(self, filePath):
        ''' Connects to necessary headers in specified csv file '''

        # Check that csv file exists
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

        self.dateCol = ' '
        self.descriptionCol = ' '
        self.amountCol = ' '

        for dateName in c.ACCEPTED_DATE_NAMES:
            if (dateName in headerList):
                self.dateCol = dateName
                break

        for descriptionName in c.ACCEPTED_DESCRIPTION_NAMES:
            if (descriptionName in headerList):
                self.descriptionCol = descriptionName
                break

        for amountName in c.ACCEPTED_AMOUNT_NAMES:
            if (amountName in headerList):
                self.amountCol = amountName
                break

        if (self.dateCol == ' '):
            log = 'Bad date column in import file', 'error'
            return c.BAD, log

        if (self.descriptionCol == ' '):
            log = 'Bad description column in import file', 'error'
            return c.BAD, log

        if (self.amountCol == ' '):
            log = 'Bad amount column in import file', 'error'
            return c.BAD, log

        # Looks good
        log = 'Import columns mapped successfully'
        return c.GOOD, log