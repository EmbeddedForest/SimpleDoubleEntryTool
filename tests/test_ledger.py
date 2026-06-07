#------------------------------------------------------------------------------
# Tests for core.ledger - the in-memory, file-backed journal.
#
# Each test gets its own temp journal CSV, so the real Journal.csv is never
# touched.
#------------------------------------------------------------------------------

import os
import tempfile
import unittest

from core.models import Line, Entry
from core.ledger import Ledger, JournalNotFoundError
from core.suggest import EXACT, PARTIAL

HEADER = ('Line,Date,TransactionID,Description,Memo,'
          'Full Account Name,Account Name,Amount Num.\n')

# Two simple entries plus one multi-line split, dates/amounts deliberately
# "ugly" (slash dates, trailing-zero amount) to exercise normalisation.
ROWS = (
    '0,1/2/2026,txNETFLIX,NETFLIX,,Liabilities:CreditCard:CC1,CC1,-17.99\n'
    '1,1/2/2026,txNETFLIX,NETFLIX,,Expenses:Entertainment:Streaming,Streaming,17.99\n'
    '0,1/2/2026,txXFER,Brokerage Transfer,,Assets:Bank:Checking,Checking,-200\n'
    '1,1/2/2026,txXFER,Brokerage Transfer,,Assets:Investments:Brokerage,Brokerage,200\n'
    '0,1/6/2026,txPUB,Pub,,Liabilities:CreditCard:CC1,CC1,-54.09\n'
    '1,1/6/2026,txPUB,Pub,,Expenses:Everyday:Restaurants,Restaurants,54.09\n'
)


class LedgerTestBase(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'Journal.csv')
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(HEADER + ROWS)
        self.ledger = Ledger(self.path).load()

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.dir)

    def new_entry(self, desc, acctF, amnt):
        return Entry([Line(date='2026-02-01', hash='newhash', desc=desc,
                           acctF=acctF, acctS=acctF.split(':')[-1], amnt=amnt)])


class TestExistsAndHistory(LedgerTestBase):

    def test_transaction_exists(self):
        self.assertTrue(self.ledger.transaction_exists('txNETFLIX'))
        self.assertFalse(self.ledger.transaction_exists('nope'))

    def test_history_groups_into_entries(self):
        history = self.ledger.history()
        self.assertEqual(len(history), 3)         # 3 transactions
        self.assertTrue(all(e.is_balanced for e in history))

    def test_load_normalises_dates_and_amounts(self):
        history = self.ledger.history()
        for entry in history:
            for line in entry:
                self.assertRegex(line.date, r'^\d{4}-\d{2}-\d{2}$')
                self.assertRegex(line.amnt, r'^-?\d+\.\d{2}$')  # always 2dp


class TestSuggestionThroughLedger(LedgerTestBase):

    def test_exact_match(self):
        flag, entry = self.ledger.find_suggested_entry(
            self.new_entry('NETFLIX', 'Liabilities:CreditCard:CC1', '-17.99'))
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry[1].acctF, 'Expenses:Entertainment:Streaming')

    def test_exact_match_on_trailing_zero_amount(self):
        # Stored as '-200'; new txn as '-200.00'. Must still match exactly.
        flag, entry = self.ledger.find_suggested_entry(
            self.new_entry('Brokerage Transfer', 'Assets:Bank:Checking', '-200.00'))
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry[1].acctF, 'Assets:Investments:Brokerage')


class TestAddAndPersist(LedgerTestBase):

    def test_add_entry_persists_after_save_and_reload(self):
        entry = Entry([
            Line(date='2026-02-01', hash='txNEW', desc='COFFEE',
                 acctF='Liabilities:CreditCard:CC1', acctS='CC1', amnt='-4.50'),
            Line(date='2026-02-01', hash='txNEW', desc='COFFEE',
                 acctF='Expenses:Everyday:Coffee', acctS='Coffee', amnt='4.50'),
        ])
        self.ledger.add_entry(entry)
        self.assertTrue(self.ledger.transaction_exists('txNEW'))

        self.ledger.save()
        reloaded = Ledger(self.path).load()
        self.assertTrue(reloaded.transaction_exists('txNEW'))
        self.assertEqual(len(reloaded.history()), 4)


class TestMissingJournal(unittest.TestCase):

    def test_load_missing_file_raises(self):
        with self.assertRaises(JournalNotFoundError):
            Ledger(os.path.join(tempfile.gettempdir(), 'does_not_exist_xyz.csv')).load()


if __name__ == '__main__':
    unittest.main()
