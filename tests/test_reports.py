#------------------------------------------------------------------------------
# Tests for core.reports - pure report aggregations.
#------------------------------------------------------------------------------

import unittest

from core.models import Line, Entry
from core.reports import (
    available_months, monthly_cash_flow, expenses_by_category, sankey_flows,
    income_allocation, allocation_totals,
)


def L(date, acct_full, amount):
    return Line(date=date, txn_id='t', desc='d', acct_full=acct_full,
                acct_short=acct_full.split(':')[-1], amount=amount)


def sample_entries():
    # Jan: a paycheck split (income -1000; checking +800; fed tax +200)
    paycheck = Entry([
        L('2026-01-07', 'Assets:Bank:Checking', '800.00'),
        L('2026-01-07', 'Income:Salary:Paycheck', '-1000.00'),
        L('2026-01-07', 'Expenses:Taxes:Federal', '200.00'),
    ])
    # Jan: a simple groceries expense (CC -50; groceries +50)
    groceries = Entry([
        L('2026-01-09', 'Liabilities:CreditCard:CC1', '-50.00'),
        L('2026-01-09', 'Expenses:Everyday:Groceries', '50.00'),
    ])
    # Feb: a restaurant expense (CC -30; restaurants +30)
    dining = Entry([
        L('2026-02-03', 'Liabilities:CreditCard:CC1', '-30.00'),
        L('2026-02-03', 'Expenses:Everyday:Restaurants', '30.00'),
    ])
    return [paycheck, groceries, dining]


class TestAvailableMonths(unittest.TestCase):

    def test_months_most_recent_first(self):
        self.assertEqual(available_months(sample_entries()), ['2026-02', '2026-01'])


class TestCashFlow(unittest.TestCase):

    def test_monthly_income_expenses_net(self):
        flow = monthly_cash_flow(sample_entries())
        jan = next(r for r in flow if r['month'] == '2026-01')
        self.assertEqual(jan['income'], 1000.00)        # -(-1000)
        self.assertEqual(jan['expenses'], 250.00)       # 200 tax + 50 groceries
        self.assertEqual(jan['net'], 750.00)

        feb = next(r for r in flow if r['month'] == '2026-02')
        self.assertEqual(feb['income'], 0.00)
        self.assertEqual(feb['expenses'], 30.00)
        self.assertEqual(feb['net'], -30.00)

    def test_ordered_oldest_first(self):
        self.assertEqual([r['month'] for r in monthly_cash_flow(sample_entries())],
                         ['2026-01', '2026-02'])


class TestExpensesByCategory(unittest.TestCase):

    def test_grouped_and_sorted(self):
        cats = expenses_by_category(sample_entries(), month='2026-01', depth=2)
        self.assertEqual(cats[0], {'category': 'Expenses:Taxes', 'amount': 200.00})
        self.assertEqual(cats[1], {'category': 'Expenses:Everyday', 'amount': 50.00})

    def test_all_time(self):
        cats = expenses_by_category(sample_entries(), month=None, depth=2)
        everyday = next(c for c in cats if c['category'] == 'Expenses:Everyday')
        self.assertEqual(everyday['amount'], 80.00)     # 50 jan + 30 feb


class TestIncomeAllocation(unittest.TestCase):

    def _entries(self):
        return [
            # paycheck: net to checking + gross income + tax
            Entry([L('2026-01-07', 'Assets:Bank:Checking', '800.00'),
                   L('2026-01-07', 'Income:Salary:Paycheck', '-1000.00'),
                   L('2026-01-07', 'Expenses:Taxes:Federal', '200.00')]),
            # brokerage contribution (investing)
            Entry([L('2026-01-02', 'Assets:Bank:Checking', '-200.00'),
                   L('2026-01-02', 'Assets:Investments:Brokerage', '200.00')]),
            # mortgage: principal (debt) + interest (expense)
            Entry([L('2026-01-03', 'Assets:Bank:Checking', '-1162.47'),
                   L('2026-01-03', 'Liabilities:Mortgages:Home', '262.47'),
                   L('2026-01-03', 'Expenses:Escrow:Interest', '900.00')]),
            # netflix on the credit card (expense)
            Entry([L('2026-01-05', 'Liabilities:CreditCard:CC1', '-17.99'),
                   L('2026-01-05', 'Expenses:Entertainment:Streaming', '17.99')]),
            # paying the credit-card bill (internal settlement - must NOT count)
            Entry([L('2026-01-20', 'Assets:Bank:Checking', '-17.99'),
                   L('2026-01-20', 'Liabilities:CreditCard:CC1', '17.99')]),
        ]

    def test_buckets(self):
        jan = income_allocation(self._entries())[0]
        self.assertEqual(jan['income'], 1000.00)
        self.assertEqual(jan['expenses'], 1117.99)        # 200 tax + 900 interest + 17.99 netflix
        self.assertEqual(jan['taxes'], 200.00)
        self.assertEqual(jan['investing'], 200.00)
        self.assertEqual(jan['living'], 917.99)           # expenses - taxes (900 + 17.99)
        self.assertEqual(jan['cost_of_living'], 1180.46)  # living + principal (917.99 + 262.47)
        self.assertEqual(jan['take_home'], 800.00)        # income - taxes - benefits
        self.assertEqual(jan['saved'], -580.46)           # income - exp - debt - investing

    def test_credit_card_payment_not_counted_as_debt(self):
        # Only the mortgage principal (262.47) is debt; the +17.99 CC payment
        # must be ignored, or the netflix spend would be double-counted.
        jan = income_allocation(self._entries())[0]
        self.assertEqual(jan['debt_principal'], 262.47)

    def test_taxes_benefits_wedding_excluded_from_living(self):
        entries = [
            Entry([L('2026-01-01', 'Liabilities:CreditCard:CC1', '-500.00'),
                   L('2026-01-01', 'Expenses:Other:Wedding', '500.00')]),
            Entry([L('2026-01-07', 'Assets:Bank:Checking', '900.00'),
                   L('2026-01-07', 'Income:Salary:Paycheck', '-1000.00'),
                   L('2026-01-07', 'Expenses:Taxes:Federal', '60.00'),
                   L('2026-01-07', 'Expenses:Benefits:Health', '40.00')]),
        ]
        jan = income_allocation(entries)[0]
        self.assertEqual(jan['taxes'], 60.00)
        self.assertEqual(jan['benefits'], 40.00)
        self.assertEqual(jan['wedding'], 500.00)
        self.assertEqual(jan['living'], 0.00)         # 600 expenses - 60 - 40 - 500
        self.assertEqual(jan['cost_of_living'], 0.00)
        self.assertEqual(jan['take_home'], 900.00)
        self.assertEqual(jan['saved'], 400.00)        # 1000 - 600 expenses

    def test_allocation_totals_matches_single_month(self):
        entries = self._entries()
        totals = allocation_totals(entries)            # only Jan present
        self.assertEqual(totals['cost_of_living'],
                         income_allocation(entries)[0]['cost_of_living'])
        # month filter with no data -> zeros
        self.assertEqual(allocation_totals(entries, month='2099-01')['income'], 0.0)


class TestSankeyFlows(unittest.TestCase):

    def test_direct_flow_without_expansion(self):
        flows = sankey_flows(sample_entries(), month='2026-01', expand_prefixes=())
        edges = dict(zip(zip((flows['labels'][s] for s in flows['source']),
                             (flows['labels'][t] for t in flows['target'])),
                         flows['value']))
        # CC -> Groceries should be a direct 50.00 edge
        self.assertEqual(edges[('Liabilities:CreditCard:CC1',
                                'Expenses:Everyday:Groceries')], 50.00)

    def test_expansion_adds_parent_edges(self):
        flows = sankey_flows(sample_entries(), month='2026-01',
                             expand_prefixes=('Expenses',))
        edges = set(zip((flows['labels'][s] for s in flows['source']),
                        (flows['labels'][t] for t in flows['target'])))
        self.assertIn(('Expenses', 'Expenses:Everyday'), edges)
        self.assertIn(('Expenses:Everyday', 'Expenses:Everyday:Groceries'), edges)

    def test_skips_unbalanced(self):
        bad = [Entry([L('2026-01-01', 'Assets:Bank:Checking', '100.00'),
                      L('2026-01-01', 'Income:Other:Misc', '-90.00')])]
        flows = sankey_flows(bad, expand_prefixes=())
        self.assertEqual(flows['value'], [])


if __name__ == '__main__':
    unittest.main()
