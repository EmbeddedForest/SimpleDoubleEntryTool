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
import constants as c


class JournalFile():

    def SetupFile(self):
        ''' Setup Journal.csv file object '''

        # Cleanup previous data
        # TODO

        # Check if the file actually exists
        retVal, log = self._CheckIfFileExists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Check that file has necessary column headers
        retVal, log = self._CheckIfColumnsExists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Looks good
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
        ''' TODO '''

        # Find latest transaction which doesn't already exist in journal

        self.LatestIndex = 2
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