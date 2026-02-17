#------------------------------------------------------------------------------
# File:
#   accounts.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file creates a class which manages the accounts listed in config.yaml
#
#------------------------------------------------------------------------------

import yaml
import constants as c


class Accounts():
    ''' Class which manages the account information from config.yaml '''

    allAcctsFullName = []
    allAcctsShortName = []
    assetAcctList = []
    incomeAcctList = []
    expenseAcctList = []
    liabilityAcctList = []
    assetDic = {}
    incomeDic = {}
    liabilityDic = {}
    expenseDic = {}
    active = False

    def Setup(self):
        ''' Setup the accounts which are stored in config.yaml '''
        self._ResetData()

        # Make sure config is present
        try:
            with open(c.CONFIG_FILE) as f:
                config = yaml.safe_load(f)

        except FileNotFoundError:
            log = 'Config file does not exist', 'error'
            return c.BAD, log

        # Put all accounts listed in config file into single full list
        fullList = []
        fullList.extend(config['Accounts']['Assets'])
        fullList.extend(config['Accounts']['Liabilities'])
        fullList.extend(config['Accounts']['Income'])
        fullList.extend(config['Accounts']['Expenses'])
        self.fullList = fullList

        for acctF in fullList:
            # Strip out all placeholder accounts
            if (acctF.count(':') != 2):
                continue

            # Get category
            tmp = acctF.split(':')
            cat = tmp[1]

            # Get short hand account name
            acctS = acctF.rpartition(':')[-1]

            self.allAcctsFullName.append(acctF)
            self.allAcctsShortName.append(acctS)

            if ('Assets' in acctF):
                self.assetAcctList.append(acctF)
                self.assetDic.setdefault(cat, []).append(acctS)
            if ('Liabilities' in acctF):
                self.liabilityAcctList.append(acctF)
                self.liabilityDic.setdefault(cat, []).append(acctS)
            if ('Income' in acctF):
                self.incomeAcctList.append(acctF)
                self.incomeDic.setdefault(cat, []).append(acctS)
            if ('Expenses' in acctF):
                self.expenseAcctList.append(acctF)
                self.expenseDic.setdefault(cat, []).append(acctS)

        # Looks good
        self.active = True
        log = 'Account setup is successful', 'default'
        return c.GOOD, log

    def _ResetData(self):
        self.fullList = []
        self.allAcctsFullName = []
        self.allAcctsShortName = []
        self.assetAcctList = []
        self.incomeAcctList = []
        self.expenseAcctList = []
        self.liabilityAcctList = []
        self.assetDic = {}
        self.incomeDic = {}
        self.liabilityDic = {}
        self.expenseDic = {}
        self.active = False

    def GetShortHand(self, fullAcctName):
        '''
        Returns short hand account name of given full account name.
        Returns blank string if no match is found
        '''
        try:
            index = self.allAcctsFullName.index(fullAcctName)

        except ValueError:
            return ''

        return self.allAcctsShortName[index]

    def IsValid(self, fullAcctName):
        '''
        Checks whether or not given account is valid or not
        Returns 'good' if valid, 'bad' if not.
        '''
        try:
            index = self.allAcctsFullName.index(fullAcctName)

        except ValueError:
            log = 'Associated account does not exist.', 'error'
            return c.BAD, log

        # All Good
        log = 'Associated account exists', 'default'
        return c.GOOD, log