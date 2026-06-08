#------------------------------------------------------------------------------
# Tests for core.importer - style detection, normalisation, hashing.
#------------------------------------------------------------------------------

import os
import tempfile
import unittest

from core.importer import (
    load_transactions, detect_style, ImportStyleError,
)

# Two styles: Chase (no negate) and Discover (negate, with a skip string).
CONFIG = {
    'ImportFileStyles': {
        'ChaseCC': {
            'DateColName': 'Transaction Date',
            'DescColName': 'Description',
            'AmntColName': 'Amount',
            'AmntNegate': False,
            'SkipStrings': ['Payment Thank You'],
            'AssAccts': ['Liabilities:CreditCard:Chase'],
        },
        'DiscoverCC': {
            'DateColName': 'Trans. Date',
            'DescColName': 'Description',
            'AmntColName': 'Amount',
            'AmntNegate': True,
            'SkipStrings': None,
            'AssAccts': ['Liabilities:CreditCard:Discover'],
        },
    }
}


def write_csv(text):
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    return path


class TestDetectStyle(unittest.TestCase):

    def test_detects_by_columns(self):
        name, _ = detect_style(CONFIG, ['Transaction Date', 'Description', 'Amount'])
        self.assertEqual(name, 'ChaseCC')

    def test_unknown_columns_raise(self):
        with self.assertRaises(ImportStyleError):
            detect_style(CONFIG, ['foo', 'bar'])


class TestLoadTransactions(unittest.TestCase):

    def setUp(self):
        self.paths = []

    def tearDown(self):
        for p in self.paths:
            if os.path.exists(p):
                os.remove(p)

    def _csv(self, text):
        p = write_csv(text)
        self.paths.append(p)
        return p

    def test_chase_no_negate_and_skip(self):
        path = self._csv(
            'Transaction Date,Description,Amount\n'
            '1/5/2026,COFFEE SHOP,4.50\n'
            '1/2/2026,GROCERY MART,52.10\n'
            '1/3/2026,Payment Thank You,-100.00\n'   # skipped
        )
        result = load_transactions(path, CONFIG)
        self.assertEqual(result.style, 'ChaseCC')
        self.assertEqual(result.assoc_accts, ['Liabilities:CreditCard:Chase'])
        self.assertEqual(result.count, 2)            # payment row dropped

        # Sorted by date, normalised dates & 2dp amounts, not negated.
        self.assertEqual(result.transactions[0].date, '2026-01-02')
        self.assertEqual(result.transactions[0].amount, '52.10')

    def test_discover_negates_amount(self):
        path = self._csv(
            'Trans. Date,Description,Amount\n'
            '1/4/2026,GAS STATION,40\n'
        )
        result = load_transactions(path, CONFIG)
        self.assertEqual(result.style, 'DiscoverCC')
        self.assertEqual(result.transactions[0].amount, '-40.00')

    def test_trailing_comma_does_not_shift_columns(self):
        # Chase checking exports end each row with a trailing comma, so a row
        # has one more field than the header. Without index_col=False pandas
        # treats the first column as the index and shifts Description onto the
        # Amount numbers, breaking the skip-string filter. This guards that.
        path = self._csv(
            'Transaction Date,Description,Amount,Type\n'
            '1/2/2026,GROCERY MART,52.10,DEBIT,\n'
            '1/5/2026,COFFEE SHOP,4.50,DEBIT,\n'
        )
        result = load_transactions(path, CONFIG)
        self.assertEqual(result.count, 2)
        self.assertEqual([t.desc for t in result.transactions],
                         ['GROCERY MART', 'COFFEE SHOP'])   # date-sorted
        self.assertEqual(result.transactions[0].amount, '52.10')

    def test_hashes_are_unique_and_stable(self):
        text = (
            'Transaction Date,Description,Amount\n'
            '1/2/2026,DUP,10.00\n'
            '1/2/2026,DUP,10.00\n'      # identical -> counter disambiguates
        )
        path = self._csv(text)
        ids = [t.txn_id for t in load_transactions(path, CONFIG).transactions]
        self.assertEqual(len(set(ids)), 2)   # unique despite identical rows

        # Stable: re-importing the same file yields the same ids.
        path2 = self._csv(text)
        ids2 = [t.txn_id for t in load_transactions(path2, CONFIG).transactions]
        self.assertEqual(ids, ids2)


if __name__ == '__main__':
    unittest.main()
