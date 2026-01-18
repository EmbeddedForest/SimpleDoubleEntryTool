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

    def CheckFile(self):
        ''' Checks to see if Journal.csv file is legit '''

        # Check that 'Journal.csv' file exists
        try:
            f = open(c.JOURNAL_FP, newline="", encoding="utf-8-sig")
            f.close()

        except FileNotFoundError:
            log = 'Journal.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise


        # Check that 'Journal.csv' file has necessary columns
        try:
            with open(c.JOURNAL_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except:
            log = 'Something bad happened', 'error'
            raise

        if (set(headerList) != set(c.JRNL_HEADERS)):
            log = 'Journal.csv is not syntactically correct.', 'error'
            return c.BAD, log

        # Looks good
        log = 'Journal.csv is legit', 'default'
        return c.GOOD, log