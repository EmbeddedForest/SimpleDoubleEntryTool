#------------------------------------------------------------------------------
# Tests for core.normalize
#------------------------------------------------------------------------------

import unittest

from core.normalize import normalize_amount, normalize_date, normalize_desc


class TestNormalizeAmount(unittest.TestCase):

    def test_pads_to_two_decimals(self):
        self.assertEqual(normalize_amount('125.5'), '125.50')
        self.assertEqual(normalize_amount(200), '200.00')

    def test_already_two_decimals_unchanged(self):
        self.assertEqual(normalize_amount('125.50'), '125.50')
        self.assertEqual(normalize_amount('-17.99'), '-17.99')

    def test_rounds_half_up(self):
        # str() first, so we round the printed value (7.005), not a float
        # artefact (7.00499...).
        self.assertEqual(normalize_amount('7.005'), '7.01')

    def test_regression_trailing_zero_compares_equal(self):
        # The original bug: import produced '125.50' while the matcher
        # produced '125.5', so exact-match silently failed. After
        # normalisation the two representations are identical.
        self.assertEqual(normalize_amount('125.50'), normalize_amount('125.5'))


class TestNormalizeDate(unittest.TestCase):

    def test_us_slash_format(self):
        self.assertEqual(normalize_date('1/2/2026'), '2026-01-02')

    def test_iso_passthrough(self):
        self.assertEqual(normalize_date('2026-01-02'), '2026-01-02')


class TestNormalizeDesc(unittest.TestCase):

    def test_strips_whitespace(self):
        self.assertEqual(normalize_desc('  Hello World  '), 'Hello World')

    def test_clamps_length(self):
        self.assertEqual(len(normalize_desc('x' * 60)), 50)


if __name__ == '__main__':
    unittest.main()
