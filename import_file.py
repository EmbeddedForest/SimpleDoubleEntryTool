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
