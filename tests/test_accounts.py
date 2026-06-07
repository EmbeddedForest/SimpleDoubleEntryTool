#------------------------------------------------------------------------------
# Tests for accounts.Accounts - chart-of-accounts indexing.
#------------------------------------------------------------------------------

import unittest

from accounts import Accounts

CONFIG = {
    'Accounts': {
        'Assets': [
            'Assets',                       # group placeholder - skipped
            'Assets:Bank',                  # category placeholder - skipped
            'Assets:Bank:Checking',         # leaf
            'Assets:Investments:Brokerage', # leaf
        ],
        'Liabilities': [
            'Liabilities:CreditCard:Chase',
        ],
        'Income': [
            'Income:Salary:Paycheck',
        ],
        'Expenses': [
            'Expenses:Everyday:Coffee',
            'Expenses:Everyday:Groceries',
        ],
    }
}


class TestAccounts(unittest.TestCase):

    def setUp(self):
        self.accts = Accounts().setup(CONFIG)

    def test_placeholders_are_skipped(self):
        self.assertNotIn('Assets', self.accts.all_full_names)
        self.assertNotIn('Assets:Bank', self.accts.all_full_names)
        self.assertIn('Assets:Bank:Checking', self.accts.all_full_names)

    def test_is_account_valid(self):
        self.assertTrue(self.accts.is_account_valid('Expenses:Everyday:Coffee'))
        self.assertFalse(self.accts.is_account_valid('Expenses:Nope'))

    def test_short_name(self):
        self.assertEqual(
            self.accts.short_name('Assets:Investments:Brokerage'), 'Brokerage')
        self.assertEqual(self.accts.short_name('not a real account'), '')

    def test_category_dictionaries(self):
        self.assertEqual(self.accts.asset_dic['Bank'], ['Checking'])
        self.assertEqual(
            sorted(self.accts.expense_dic['Everyday']), ['Coffee', 'Groceries'])
        self.assertEqual(self.accts.liability_dic['CreditCard'], ['Chase'])


if __name__ == '__main__':
    unittest.main()
