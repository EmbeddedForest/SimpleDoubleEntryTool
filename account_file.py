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

    # Object data
    allAcctsFullName = []
    allAcctsShortName = []
    assetAcctList = []
    incomeAcctList = []
    expenseAcctList = []
    liabilityAcctList = []
    active = False

    def SetupFile(self):
        ''' Setup Account.csv file object '''

        # Cleanup previous data
        self.allAcctsFullName = []
        self.allAcctsShortName = []
        self.assetAcctList = []
        self.incomeAcctList = []
        self.expenseAcctList = []
        self.liabilityAcctList = []
        self.active = False

        # Check if the file actually exists
        retVal, log = self._CheckIfFileExists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Check that file has necessary column headers
        retVal, log = self._CheckIfColumnsExists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Update account lists
        retVal, log = self._UpdateAccountLists()
        if (retVal == c.BAD):
            return c.BAD, log

        # Looks good
        self.active = True
        log = 'Account.csv setup is successful', 'default'
        return c.GOOD, log


    def _CheckIfFileExists(self):
        ''' Check that Accounts.csv file exists '''

        try:
            f = open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig")
            f.close()

        except FileNotFoundError:
            log = 'Accounts.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        log = 'Accounts.csv file does exist', 'default'
        return c.GOOD, log


    def _CheckIfColumnsExists(self):
        ''' Check if necessary column headers exist '''

        try:
            with open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headerList = list(next(reader).keys())

        except FileNotFoundError:
            log = 'Accounts.csv does not exist in current directory.', 'error'
            return c.BAD, log
    
        except:
            log = 'Something bad happened', 'error'
            raise

        if (set(headerList) != set(c.ACCT_HEADERS)):
            log = 'Accounts.csv is not syntactically correct.', 'error'
            return c.BAD, log

        log = 'Account.csv file has necessary columns', 'default'
        return c.GOOD, log


    def _UpdateAccountLists(self):
        ''' Updates all account lists '''

        self.allAcctsFullName = []
        self.allAcctsShortName = []
        self.assetAcctList = []
        self.incomeAcctList = []
        self.expenseAcctList = []
        self.liabilityAcctList = []

        # TODO - Check if it's a "placeholder", if so, don't add
        try:
            with open(c.ACCOUNTS_FP, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if (row[c.ACCT_PLACEHOLDER] == 'T'):
                        continue

                    self.allAcctsShortName.append(row[c.ACCT_NAME])
                    self.allAcctsFullName.append(row[c.ACCT_NAME_FULL])

                    if ('Assets' in row[c.ACCT_NAME_FULL]):
                        self.assetAcctList.append(row[c.ACCT_NAME_FULL])

                    if ('Income' in row[c.ACCT_NAME_FULL]):
                        self.incomeAcctList.append(row[c.ACCT_NAME_FULL])

                    if ('Expenses' in row[c.ACCT_NAME_FULL]):
                        self.expenseAcctList.append(row[c.ACCT_NAME_FULL])

                    if ('Liabilities' in row[c.ACCT_NAME_FULL]):
                        self.liabilityAcctList.append(row[c.ACCT_NAME_FULL])

        except FileNotFoundError:
            log = 'Accounts.csv does not exist in current directory.', 'error'
            return c.BAD, log

        except:
            log = 'Something bad happened', 'error'
            raise

        # All Good
        log = 'Account names read successfully', 'default'
        return c.GOOD, log

    def GetShortHand(self, fullAcctName):
        ''' Returns short hand account name of given full account name '''

        index = self.allAcctsFullName.index(fullAcctName)

        return self.allAcctsShortName[index]