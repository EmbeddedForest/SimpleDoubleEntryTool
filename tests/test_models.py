#------------------------------------------------------------------------------
# Tests for core.models
#------------------------------------------------------------------------------

import unittest

from core.models import Line, Entry


def make_line(amnt, acctF='Acct', desc='Desc'):
    return Line(date='2026-01-02', hash='h', desc=desc, memo='',
                acctF=acctF, acctS='Acct', amnt=amnt)


class TestLine(unittest.TestCase):

    def test_defaults_are_empty_strings(self):
        l = Line()
        self.assertEqual(l.date, '')
        self.assertEqual(l.amnt, '')

    def test_instances_do_not_share_state(self):
        # The original entry.py used class-level attributes with no __init__,
        # so this is the regression guard against shared mutable state.
        a = Line()
        b = Line()
        a.date = '2026-01-01'
        self.assertEqual(b.date, '')


class TestEntry(unittest.TestCase):

    def test_empty_entry(self):
        e = Entry()
        self.assertEqual(e.size, 0)
        self.assertFalse(e.split)

    def test_split_tracks_size(self):
        e = Entry()
        e.AddLine(make_line('-100.00'))
        e.AddLine(make_line('100.00'))
        self.assertEqual(e.size, 2)
        self.assertFalse(e.split)

        e.AddLine(make_line('0.00'))
        self.assertEqual(e.size, 3)
        self.assertTrue(e.split)

        e.RemoveLine(2)
        self.assertEqual(e.size, 2)
        self.assertFalse(e.split)

    def test_remove_out_of_range_is_noop(self):
        e = Entry([make_line('-100.00'), make_line('100.00')])
        e.RemoveLine(5)
        self.assertEqual(e.size, 2)

    def test_constructed_from_lines(self):
        e = Entry([make_line('-100.00'), make_line('100.00')])
        self.assertEqual(e.size, 2)
        self.assertEqual(e[0].amnt, '-100.00')

    def test_balance_and_is_balanced(self):
        e = Entry([make_line('-100.00'), make_line('100.00')])
        self.assertEqual(e.balance, 0)
        self.assertTrue(e.is_balanced)

        e.AddLine(make_line('0.01'))
        self.assertEqual(e.balance, 0.01)
        self.assertFalse(e.is_balanced)

    def test_balance_raises_on_bad_amount(self):
        e = Entry([make_line('')])
        with self.assertRaises(ValueError):
            _ = e.balance

    def test_iteration_and_clear(self):
        e = Entry([make_line('-100.00'), make_line('100.00')])
        self.assertEqual(len(list(e)), 2)
        e.Clear()
        self.assertEqual(e.size, 0)
        self.assertFalse(e.split)


if __name__ == '__main__':
    unittest.main()
