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


def _reverse_amount(amnt):
    ''' Flip the sign of a canonical amount string ('' stays ''). '''
    if amnt == '':
        return ''
    if amnt.startswith('-'):
        return amnt[1:]
    return '-' + amnt


def _offset_line(src_line, l, amnt):
    ''' Build a follow-on line, taking identity fields from the new txn (l)
        and account/memo from a historical line. '''
    return Line(date=l.date, hash=l.hash, desc=l.desc,
                memo=src_line.memo, acctF=src_line.acctF,
                acctS=src_line.acctS, amnt=amnt)


def _replay_exact(hist, l):
    ''' Exact match: replay every follow-on line verbatim. '''
    entry = Entry([l])
    for hline in hist[1:]:
        entry.AddLine(_offset_line(hline, l, normalize_amount(hline.amnt)))
    return entry


def _replay_partial(hist, l):
    ''' Partial match: keep accounts/memos, but the first offset line gets
        the reversed transaction amount and the rest are left blank for the
        user to fill. '''
    entry = Entry([l])
    rev = _reverse_amount(normalize_amount(l.amnt))
    for idx, hline in enumerate(hist[1:], start=1):
        entry.AddLine(_offset_line(hline, l, rev if idx == 1 else ''))
    return entry


def suggest_entry(history, first_line):
    '''
    history    : list[Entry], oldest-first (as stored on disk).
    first_line : the associated-account Line of the new transaction.

    Returns (result_flag, Entry) where the returned Entry always begins with
    first_line. result_flag is one of EXACT / PARTIAL / NONE.
    '''
    l = first_line
    target_amnt = normalize_amount(l.amnt) if l.amnt != '' else ''

    # Tier 1 - exact: same description, account and amount.
    for hist in reversed(history):
        h0 = hist[0]
        if (h0.desc == l.desc and h0.acctF == l.acctF
                and normalize_amount(h0.amnt) == target_amnt):
            return EXACT, _replay_exact(hist, l)

    # Tier 2 - partial: same description and account, any amount.
    for hist in reversed(history):
        h0 = hist[0]
        if h0.desc == l.desc and h0.acctF == l.acctF:
            return PARTIAL, _replay_partial(hist, l)

    # Tier 3 - fuzzy: closest description above the similarity threshold.
    rev = _reverse_amount(target_amnt)
    for hist in reversed(history):
        for hline in reversed(list(hist)):
            ratio = SequenceMatcher(None, hline.desc, l.desc).ratio()
            if ratio > FUZZY_THRESHOLD:
                entry = Entry([l])
                entry.AddLine(_offset_line(hline, l, rev))
                return PARTIAL, entry

    # No match: hand back only what we know, with the reversed amount.
    entry = Entry([l])
    entry.AddLine(Line(date=l.date, hash=l.hash, desc=l.desc,
                       acctF='', acctS='', amnt=rev))
    return NONE, entry
