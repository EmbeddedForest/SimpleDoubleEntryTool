#------------------------------------------------------------------------------
# File:
#   core/suggest.py
#
# Description:
#   The suggestion engine: given the history of past entries and the first
#   line of a new transaction, propose how to categorise it.
#
#   This is the same three-tier strategy as the original
#   JournalFile.FindSuggestedEntry, but it operates on grouped Entry objects
#   instead of walking raw DataFrame row labels, and it routes every amount
#   through normalize_amount so exact matches no longer break on trailing
#   zeros. The three near-identical reverse-iteration loops of the original
#   are collapsed into one pass per tier with shared replay helpers.
#------------------------------------------------------------------------------

from difflib import SequenceMatcher

from core.models import Line, Entry
from core.normalize import normalize_amount

FUZZY_THRESHOLD = 0.60

EXACT   = 'ExactMatch'
PARTIAL = 'PartialMatch'
NONE    = 'NoMatch'


def _reverse_amount(amount):
    ''' Flip the sign of a canonical amount string ('' stays ''). '''
    if amount == '':
        return ''
    if amount.startswith('-'):
        return amount[1:]
    return '-' + amount


def _offset_line(src_line, first, amount):
    ''' Build a follow-on line, taking identity fields from the new txn
        (first) and account/memo from a historical line. '''
    return Line(date=first.date, txn_id=first.txn_id, desc=first.desc,
                memo=src_line.memo, acct_full=src_line.acct_full,
                acct_short=src_line.acct_short, amount=amount)


def _replay_exact(hist, first):
    ''' Exact match: replay every follow-on line verbatim. '''
    entry = Entry([first])
    for hline in hist[1:]:
        entry.add_line(_offset_line(hline, first, normalize_amount(hline.amount)))
    return entry


def _replay_partial(hist, first):
    ''' Partial match: keep accounts/memos, but the first offset line gets
        the reversed transaction amount and the rest are left blank for the
        user to fill. '''
    entry = Entry([first])
    rev = _reverse_amount(normalize_amount(first.amount))
    for idx, hline in enumerate(hist[1:], start=1):
        entry.add_line(_offset_line(hline, first, rev if idx == 1 else ''))
    return entry


def suggest_entry(history, first_line):
    '''
    history    : list[Entry], oldest-first (as stored on disk).
    first_line : the associated-account Line of the new transaction.

    Returns (result_flag, Entry) where the returned Entry always begins with
    first_line. result_flag is one of EXACT / PARTIAL / NONE.
    '''
    first = first_line
    target = normalize_amount(first.amount) if first.amount != '' else ''

    # Tier 1 - exact: same description, account and amount.
    for hist in reversed(history):
        h0 = hist[0]
        if (h0.desc == first.desc and h0.acct_full == first.acct_full
                and normalize_amount(h0.amount) == target):
            return EXACT, _replay_exact(hist, first)

    # Tier 2 - partial: same description and account, any amount.
    for hist in reversed(history):
        h0 = hist[0]
        if h0.desc == first.desc and h0.acct_full == first.acct_full:
            return PARTIAL, _replay_partial(hist, first)

    # Tier 3 - fuzzy: closest description above the similarity threshold.
    rev = _reverse_amount(target)
    for hist in reversed(history):
        for hline in reversed(list(hist)):
            ratio = SequenceMatcher(None, hline.desc, first.desc).ratio()
            if ratio > FUZZY_THRESHOLD:
                entry = Entry([first])
                entry.add_line(_offset_line(hline, first, rev))
                return PARTIAL, entry

    # No match: hand back only what we know, with the reversed amount.
    entry = Entry([first])
    entry.add_line(Line(date=first.date, txn_id=first.txn_id, desc=first.desc,
                        acct_full='', acct_short='', amount=rev))
    return NONE, entry
