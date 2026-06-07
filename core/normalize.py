#------------------------------------------------------------------------------
# File:
#   core/normalize.py
#
# Description:
#   Single source of truth for normalising transaction fields. The original
#   code duplicated this logic between import_file.py and journal_file.py, and
#   the two paths disagreed on amount formatting (Decimal '125.50' vs float
#   '125.5'), which silently broke exact-match suggestions for any amount
#   ending in a zero. Routing everything through these helpers keeps the
#   import side and the journal side byte-for-byte comparable.
#------------------------------------------------------------------------------

from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def normalize_date(value):
    ''' Parse any reasonable date into canonical 'YYYY-MM-DD' (month-first). '''
    ts = pd.to_datetime(value, format='mixed', dayfirst=False)
    return ts.strftime('%Y-%m-%d')


def normalize_amount(value):
    '''
    Canonicalise a monetary value to a fixed 2-decimal string:
        '125.5'  -> '125.50'
        200      -> '200.00'
        '7.005'  -> '7.01'   (round half up)
        '-17.99' -> '-17.99'

    str(value) is used before Decimal so that a value that arrived as a float
    is read at its printed precision, not its binary-float artefact.
    '''
    dec = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return str(dec)


def normalize_desc(value, max_len=50):
    ''' Strip surrounding whitespace and clamp the description length. '''
    return str(value).strip()[:max_len]
