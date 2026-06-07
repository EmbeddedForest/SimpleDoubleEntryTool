#------------------------------------------------------------------------------
# Tests for core.suggest - the three-tier suggestion engine, no files needed.
#------------------------------------------------------------------------------

import unittest

from core.models import Line, Entry
from core.suggest import suggest_entry, EXACT, PARTIAL, NONE


def first_line(desc, acctF, amnt):
    ''' The associated-account line of a brand new transaction. '''
    return Line(date='2026-02-01', hash='newhash', desc=desc, memo='',
                acctF=acctF, acctS=acctF.split(':')[-1], amnt=amnt)


def netflix_history():
    ''' One past 2-line entry: CC1 -> Streaming for NETFLIX, -17.99. '''
    e = Entry([
        Line(date='2026-01-02', hash='h1', desc='NETFLIX', memo='',
             acctF='Liabilities:CreditCard:CC1', acctS='CC1', amnt='-17.99'),
        Line(date='2026-01-02', hash='h1', desc='NETFLIX', memo='',
             acctF='Expenses:Entertainment:Streaming', acctS='Streaming',
             amnt='17.99'),
    ])
    return [e]


class TestExactMatch(unittest.TestCase):

    def test_exact_replays_offset_account(self):
        flag, entry = suggest_entry(
            netflix_history(),
            first_line('NETFLIX', 'Liabilities:CreditCard:CC1', '-17.99'),
        )
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry.size, 2)
        self.assertEqual(entry[1].acctF, 'Expenses:Entertainment:Streaming')
        self.assertEqual(entry[1].amnt, '17.99')
        self.assertTrue(entry.is_balanced)

    def test_exact_match_survives_trailing_zero(self):
        # Regression: history amount '200' vs new amount '-200.00' style
        # mismatch used to fall through to a weaker partial match.
        hist = [Entry([
            Line(date='2026-01-02', hash='h', desc='Transfer', memo='',
                 acctF='Assets:Bank:Checking', acctS='Checking', amnt='-200'),
            Line(date='2026-01-02', hash='h', desc='Transfer', memo='',
                 acctF='Assets:Investments:Brokerage', acctS='Brokerage',
                 amnt='200'),
        ])]
        flag, entry = suggest_entry(
            hist, first_line('Transfer', 'Assets:Bank:Checking', '-200.00'))
        self.assertEqual(flag, EXACT)
        self.assertEqual(entry[1].acctF, 'Assets:Investments:Brokerage')


class TestPartialMatch(unittest.TestCase):

    def test_partial_reverses_amount_when_amount_differs(self):
        flag, entry = suggest_entry(
            netflix_history(),
            first_line('NETFLIX', 'Liabilities:CreditCard:CC1', '-19.99'),
        )
        self.assertEqual(flag, PARTIAL)
        self.assertEqual(entry[1].acctF, 'Expenses:Entertainment:Streaming')
        self.assertEqual(entry[1].amnt, '19.99')  # reversed new amount


class TestFuzzyMatch(unittest.TestCase):

    def test_fuzzy_suggests_account_for_similar_description(self):
        flag, entry = suggest_entry(
            netflix_history(),
            # different account so tiers 1 & 2 cannot fire; description close
            first_line('NETFLIX.COM', 'Assets:Bank:Checking', '-17.99'),
        )
        self.assertEqual(flag, PARTIAL)
        self.assertEqual(entry[1].acctF, 'Expenses:Entertainment:Streaming')
        self.assertEqual(entry[1].amnt, '17.99')


class TestNoMatch(unittest.TestCase):

    def test_empty_history_returns_nomatch(self):
        flag, entry = suggest_entry(
            [], first_line('BRAND NEW VENDOR', 'Assets:Bank:Checking', '-5.00'))
        self.assertEqual(flag, NONE)
        self.assertEqual(entry.size, 2)
        self.assertEqual(entry[1].acctF, '')
        self.assertEqual(entry[1].amnt, '5.00')  # reversed, awaiting a category


if __name__ == '__main__':
    unittest.main()
