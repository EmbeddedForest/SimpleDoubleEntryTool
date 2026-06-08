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
from core.suggest import EXACT, PARTIAL, NONE

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

    def new_entry(self, desc, acct_full, amount):
        return Entry([Line(date='2026-02-01', txn_id='newhash', desc=desc,
                           acct_full=acct_full, acct_short=acct_full.split(':')[-1],
                           amount=amount)])


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
                self.assertRegex(line.amount, r'^-?\d+\.\d{2}$')  # always 2dp


class TestSuggestionThroughLedger(LedgerTestBase):

    def test_exact_match(self):
        flag, entry = self.ledger.find_suggested_entry(
            self.new_entry('NETFLIX', 'Liabilities:CreditCard:CC1', '-17.99'))
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry[1].acct_full, 'Expenses:Entertainment:Streaming')

    def test_exact_match_on_trailing_zero_amount(self):
        # Stored as '-200'; new txn as '-200.00'. Must still match exactly.
        flag, entry = self.ledger.find_suggested_entry(
            self.new_entry('Brokerage Transfer', 'Assets:Bank:Checking', '-200.00'))
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry[1].acct_full, 'Assets:Investments:Brokerage')


class TestAddAndPersist(LedgerTestBase):

    def test_add_entry_persists_after_save_and_reload(self):
        entry = Entry([
            Line(date='2026-02-01', txn_id='txNEW', desc='COFFEE',
                 acct_full='Liabilities:CreditCard:CC1', acct_short='CC1',
                 amount='-4.50'),
            Line(date='2026-02-01', txn_id='txNEW', desc='COFFEE',
                 acct_full='Expenses:Everyday:Coffee', acct_short='Coffee',
                 amount='4.50'),
        ])
        self.ledger.add_entry(entry)
        self.assertTrue(self.ledger.transaction_exists('txNEW'))

        self.ledger.save()
        reloaded = Ledger(self.path).load()
        self.assertTrue(reloaded.transaction_exists('txNEW'))
        self.assertEqual(len(reloaded.history()), 4)


class TestGetDeleteReplace(LedgerTestBase):

    def test_get_entry(self):
        entry = self.ledger.get_entry('txNETFLIX')
        self.assertEqual(entry.size, 2)
        self.assertEqual(entry[1].acct_full, 'Expenses:Entertainment:Streaming')
        self.assertIsNone(self.ledger.get_entry('nope'))

    def test_delete_entry(self):
        self.ledger.delete_entry('txNETFLIX')
        self.assertFalse(self.ledger.transaction_exists('txNETFLIX'))
        self.assertEqual(len(self.ledger.history()), 2)

    def test_add_entry_is_upsert_not_duplicate(self):
        # Re-adding a transaction with an existing TransactionID must overwrite,
        # never create a second copy (the journal-duplication bug).
        entry = Entry([
            Line(date='2026-02-01', txn_id='txDUP', desc='THING',
                 acct_full='Liabilities:CreditCard:CC1', acct_short='CC1',
                 amount='-9.00'),
            Line(date='2026-02-01', txn_id='txDUP', desc='THING',
                 acct_full='Expenses:Everyday:Coffee', acct_short='Coffee',
                 amount='9.00'),
        ])
        self.ledger.add_entry(entry)
        self.ledger.add_entry(entry)             # accidental second add
        self.ledger.add_entry(entry)             # ...and a third
        self.assertEqual(len(self.ledger.history()), 4)   # 3 original + 1
        self.assertEqual(self.ledger.get_entry('txDUP').size, 2)  # not 4 or 6

    def test_replace_entry_recategorises(self):
        entry = self.ledger.get_entry('txPUB')
        entry[1].acct_full = 'Expenses:Entertainment:Bars'
        entry[1].acct_short = 'Bars'
        self.ledger.replace_entry(entry)
        self.ledger.save()

        reloaded = Ledger(self.path).load()
        self.assertEqual(len(reloaded.history()), 3)          # count unchanged
        again = reloaded.get_entry('txPUB')
        self.assertEqual(again[1].acct_full, 'Expenses:Entertainment:Bars')
        self.assertTrue(again.is_balanced)


class TestClassify(LedgerTestBase):

    def _line(self, desc, acct_full, amount):
        return Line(desc=desc, acct_full=acct_full, amount=amount)

    def test_classify_exact(self):
        flag = self.ledger.classify(
            self._line('NETFLIX', 'Liabilities:CreditCard:CC1', '-17.99'))
        self.assertEqual(flag, EXACT)

    def test_classify_exact_ignores_trailing_zero(self):
        flag = self.ledger.classify(
            self._line('Brokerage Transfer', 'Assets:Bank:Checking', '-200.00'))
        self.assertEqual(flag, EXACT)

    def test_classify_partial_when_amount_differs(self):
        flag = self.ledger.classify(
            self._line('NETFLIX', 'Liabilities:CreditCard:CC1', '-19.99'))
        self.assertEqual(flag, PARTIAL)

    def test_classify_none_for_unknown(self):
        flag = self.ledger.classify(
            self._line('BRAND NEW', 'Assets:Bank:Checking', '-5.00'))
        self.assertEqual(flag, NONE)


class TestCacheInvalidation(LedgerTestBase):

    def test_caches_update_after_add(self):
        # Prime the caches.
        self.assertFalse(self.ledger.transaction_exists('txNEW'))
        self.assertEqual(len(self.ledger.history()), 3)

        self.ledger.add_entry(Entry([
            Line(date='2026-02-01', txn_id='txNEW', desc='COFFEE',
                 acct_full='Liabilities:CreditCard:CC1', acct_short='CC1',
                 amount='-4.50'),
            Line(date='2026-02-01', txn_id='txNEW', desc='COFFEE',
                 acct_full='Expenses:Everyday:Coffee', acct_short='Coffee',
                 amount='4.50'),
        ]))

        # Caches must reflect the new entry without an explicit reload.
        self.assertTrue(self.ledger.transaction_exists('txNEW'))
        self.assertEqual(len(self.ledger.history()), 4)
        self.assertEqual(
            self.ledger.classify(Line(desc='COFFEE',
                                      acct_full='Liabilities:CreditCard:CC1',
                                      amount='-4.50')),
            EXACT)

    def test_caches_update_after_delete(self):
        self.ledger.transaction_exists('txNETFLIX')   # prime
        self.ledger.delete_entry('txNETFLIX')
        self.assertFalse(self.ledger.transaction_exists('txNETFLIX'))
        self.assertEqual(
            self.ledger.classify(Line(desc='NETFLIX',
                                      acct_full='Liabilities:CreditCard:CC1',
                                      amount='-17.99')),
            NONE)


class TestMissingJournal(unittest.TestCase):

    def test_load_missing_file_raises(self):
        with self.assertRaises(JournalNotFoundError):
            Ledger(os.path.join(tempfile.gettempdir(), 'does_not_exist_xyz.csv')).load()


if __name__ == '__main__':
    unittest.main()
