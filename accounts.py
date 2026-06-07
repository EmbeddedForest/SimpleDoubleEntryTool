#------------------------------------------------------------------------------
# File:
#   accounts.py
#
# Description:
#   Manages the chart of accounts defined in config.yaml. Reworked to keep all
#   state on the instance, to read config via core.config, and to raise on a
#   missing config rather than returning string flags.
#------------------------------------------------------------------------------

import constants as c
from core.config import load_config


class Accounts():
    ''' The chart of accounts, grouped by type and category. '''

    def __init__(self, config_path=c.CONFIG_FILE):
        self.config_path = config_path
        self._reset()

    def _reset(self):
        self.full_list = []
        self.all_full_names = []
        self.all_short_names = []
        self.asset_accts = []
        self.income_accts = []
        self.expense_accts = []
        self.liability_accts = []
        self.asset_dic = {}
        self.income_dic = {}
        self.liability_dic = {}
        self.expense_dic = {}
        self.active = False

    def setup(self, config=None):
        ''' Load and index the accounts. Pass a config dict to skip file IO
            (used by tests); otherwise it is read from config_path. '''
        self._reset()
        if config is None:
            config = load_config(self.config_path)

        accounts = config['Accounts']
        for group in (c.ASSETS, c.LIABILITIES, c.INCOME, c.EXPENSES):
            self.full_list.extend(accounts.get(group, []))

        for full in self.full_list:
            # Keep only leaf accounts of the form Group:Category:Account;
            # the Group and Group:Category placeholders are skipped.
            if full.count(':') != 2:
                continue

            category = full.split(':')[1]
            short = full.rpartition(':')[-1]

            self.all_full_names.append(full)
            self.all_short_names.append(short)

            if full.startswith(c.ASSETS):
                self.asset_accts.append(full)
                self.asset_dic.setdefault(category, []).append(short)
            elif full.startswith(c.LIABILITIES):
                self.liability_accts.append(full)
                self.liability_dic.setdefault(category, []).append(short)
            elif full.startswith(c.INCOME):
                self.income_accts.append(full)
                self.income_dic.setdefault(category, []).append(short)
            elif full.startswith(c.EXPENSES):
                self.expense_accts.append(full)
                self.expense_dic.setdefault(category, []).append(short)

        self.active = True
        return self

    def is_account_valid(self, full_name):
        ''' True if full_name is a known leaf account. '''
        return full_name in self.all_full_names

    def short_name(self, full_name):
        ''' Short (leaf) name for a full account name, or '' if unknown. '''
        try:
            index = self.all_full_names.index(full_name)
        except ValueError:
            return ''
        return self.all_short_names[index]
