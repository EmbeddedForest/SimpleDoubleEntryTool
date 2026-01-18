#------------------------------------------------------------------------------
# File:
#   account_file.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file creates a class which represents the Account.csv file
#
#------------------------------------------------------------------------------

import csv
import constants as c


class AccountFile():

    def CheckFile(self):
        ''' Checks to see if Account.csv file is legit '''

        # Check that 'Accounts.csv' file exists
        try:
            f = open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig")
            f.close()

        except FileNotFoundError:
            log = 'Accounts.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise


        # Check that 'Accounts.csv' file has necessary columns
        try:
            with open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except:
            log = 'Something bad happened', 'error'
            raise

        if (set(headerList) != set(c.ACCT_HEADERS)):
            log = 'Accounts.csv is not syntactically correct.', 'error'
            return c.BAD, log

        # Looks good
        log = 'Account.csv is legit', 'default'
        return c.GOOD, log

    def _GetAccountNames(self, fullName):
        ''' Returns all account names as a list of strings '''

        returnList = list()

        if (fullName == True):
            colName = c.ACCT_NAME_FULL
        else:
            colName = c.ACCT_NAME

        try:
            with open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    returnList.append(row[colName])
        except:
            log = 'Something bad happened', 'error'
            raise

        # All Good
        log = 'Account names read successfully', 'default'
        return returnList, log