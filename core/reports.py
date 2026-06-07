#------------------------------------------------------------------------------
# File:
#   core/reports.py
#
# Description:
#   Pure report aggregations over a list of journal Entry objects (typically
#   Ledger.history()). No plotting here - each function returns plain data
#   structures that the UI turns into Plotly figures, so the maths stays unit
#   testable.
#
#   Sign convention (as stored): Income accounts carry negative amounts
#   (credits), Expense accounts carry positive amounts (debits). So "money in"
#   is the negated sum of Income lines and "money out" is the sum of Expense
#   lines.
#------------------------------------------------------------------------------

from collections import defaultdict

ASSETS = 'Assets'
INCOME = 'Income'
EXPENSES = 'Expenses'
LIABILITIES = 'Liabilities'
CREDIT_CARD = 'Liabilities:CreditCard'   # a spending vehicle, not amortised debt
INVESTMENTS = 'Assets:Investments'

# Expense groups carved out of "true cost of living": involuntary payroll
# deductions (taxes, benefits) and one-off events (wedding).
TAXES = 'Expenses:Taxes'
BENEFITS = 'Expenses:Benefits'
WEDDING = 'Expenses:Other:Wedding'


def _month(date_str):
    ''' 'YYYY-MM-DD' -> 'YYYY-MM'. '''
    return str(date_str)[:7]


def _amount(line):
    try:
        return float(line.amount)
    except (ValueError, TypeError):
        return 0.0


def available_months(entries):
    ''' All YYYY-MM present in the entries, most-recent first. '''
    return sorted({_month(l.date) for e in entries for l in e}, reverse=True)


def monthly_cash_flow(entries):
    '''
    Per-month income, expenses and net (income - expenses), oldest month first:
        [{'month': '2026-01', 'income': 4342.64,
          'expenses': 3100.10, 'net': 1242.54}, ...]
    '''
    income = defaultdict(float)
    expenses = defaultdict(float)
    for entry in entries:
        for line in entry:
            month = _month(line.date)
            if line.acct_full.startswith(INCOME):
                income[month] += -_amount(line)        # income stored negative
            elif line.acct_full.startswith(EXPENSES):
                expenses[month] += _amount(line)
    months = sorted(set(income) | set(expenses))
    return [{'month': m,
             'income': round(income[m], 2),
             'expenses': round(expenses[m], 2),
             'net': round(income[m] - expenses[m], 2)}
            for m in months]


def _new_buckets():
    return dict(income=0.0, expenses=0.0, taxes=0.0, benefits=0.0,
                wedding=0.0, debt_principal=0.0, investing=0.0)


def _accumulate(buckets, line):
    ''' Add one posting leg into the raw buckets. '''
    acct = line.acct_full
    amt = _amount(line)
    if acct.startswith(INCOME):
        buckets['income'] += -amt
    elif acct.startswith(EXPENSES):
        buckets['expenses'] += amt
        if acct.startswith(TAXES):
            buckets['taxes'] += amt
        elif acct.startswith(BENEFITS):
            buckets['benefits'] += amt
        elif acct.startswith(WEDDING):
            buckets['wedding'] += amt
    elif acct.startswith(INVESTMENTS):
        buckets['investing'] += amt
    elif acct.startswith(LIABILITIES) and not acct.startswith(CREDIT_CARD):
        buckets['debt_principal'] += amt


def _finalize(b):
    '''
    Turn raw buckets into a report row. "True cost of living" excludes
    involuntary payroll deductions (taxes, benefits) and one-off wedding costs:
        living         = expenses - taxes - benefits - wedding
        cost_of_living = living + debt_principal
        take_home      = income - taxes - benefits
        saved          = income - expenses - debt_principal - investing
    '''
    income = round(b['income'], 2)
    expenses = round(b['expenses'], 2)
    taxes = round(b['taxes'], 2)
    benefits = round(b['benefits'], 2)
    wedding = round(b['wedding'], 2)
    debt = round(b['debt_principal'], 2)
    investing = round(b['investing'], 2)
    living = round(expenses - taxes - benefits - wedding, 2)
    return {
        'income': income, 'expenses': expenses, 'taxes': taxes,
        'benefits': benefits, 'wedding': wedding, 'debt_principal': debt,
        'investing': investing, 'living': living,
        'cost_of_living': round(living + debt, 2),
        'take_home': round(income - taxes - benefits, 2),
        'saved': round(income - expenses - debt - investing, 2),
    }


def income_allocation(entries):
    '''
    Per-month allocation rows (oldest first), each a _finalize() dict plus
    'month'. Credit-card legs are excluded (charges already counted as
    expenses; payments are internal settlement), so nothing double-counts.
    '''
    per_month = defaultdict(_new_buckets)
    for entry in entries:
        for line in entry:
            _accumulate(per_month[_month(line.date)], line)
    return [dict(month=m, **_finalize(per_month[m])) for m in sorted(per_month)]


def allocation_totals(entries, month=None):
    ''' A single _finalize() dict summed over the period (month=None = all). '''
    buckets = _new_buckets()
    for entry in entries:
        for line in entry:
            if month and _month(line.date) != month:
                continue
            _accumulate(buckets, line)
    return _finalize(buckets)


def expenses_by_category(entries, month=None, depth=2):
    '''
    Total expense spend grouped by category, largest first. depth=2 groups at
    the top expense category (e.g. 'Expenses:Everyday'); month=None is all-time:
        [{'category': 'Expenses:Everyday', 'amount': 812.55}, ...]
    '''
    totals = defaultdict(float)
    for entry in entries:
        for line in entry:
            if not line.acct_full.startswith(EXPENSES):
                continue
            if month and _month(line.date) != month:
                continue
            parts = line.acct_full.split(':')
            category = ':'.join(parts[:depth]) if len(parts) >= depth else line.acct_full
            totals[category] += _amount(line)
    return sorted(({'category': k, 'amount': round(v, 2)} for k, v in totals.items()),
                  key=lambda d: d['amount'], reverse=True)


def _expand_hierarchy(flows, prefixes):
    '''
    For flows whose target sits under one of prefixes, cascade the flow down
    the account hierarchy so e.g. CC -> Expenses -> Expenses:Everyday ->
    Expenses:Everyday:Groceries instead of a single edge. Other flows pass
    through unchanged.
    '''
    out = defaultdict(float)
    for (src, tgt), amt in flows.items():
        if not any(tgt.startswith(p) for p in prefixes):
            out[(src, tgt)] += amt
            continue
        parts = tgt.split(':')
        chain = [':'.join(parts[:i]) for i in range(1, len(parts) + 1)]
        out[(src, chain[0])] += amt
        for a, b in zip(chain, chain[1:]):
            out[(a, b)] += amt
    return out


def sankey_flows(entries, month=None, expand_prefixes=('Expenses', 'Assets:Investments')):
    '''
    Build money-flow links (credit account -> debit account) for a Sankey
    diagram, matching each balanced transaction's credits against its debits.
    Returns {'labels', 'source', 'target', 'value'} with source/target as
    indices into labels. Unbalanced transactions are skipped.
    '''
    flows = defaultdict(float)
    for entry in entries:
        if month and _month(entry[0].date) != month:
            continue

        debits, credits = [], []
        for line in entry:
            amt = _amount(line)
            if amt > 0:
                debits.append([line.acct_full, amt])
            elif amt < 0:
                credits.append([line.acct_full, -amt])

        if round(sum(d[1] for d in debits), 2) != round(sum(cr[1] for cr in credits), 2):
            continue

        # Iterative clearing: pour each credit into debits until both run out.
        i = j = 0
        while i < len(credits) and j < len(debits):
            amt = min(credits[i][1], debits[j][1])
            flows[(credits[i][0], debits[j][0])] += amt
            credits[i][1] -= amt
            debits[j][1] -= amt
            if credits[i][1] < 0.005:
                i += 1
            if debits[j][1] < 0.005:
                j += 1

    if expand_prefixes:
        flows = _expand_hierarchy(flows, expand_prefixes)

    labels = sorted({a for pair in flows for a in pair})
    index = {name: k for k, name in enumerate(labels)}
    source, target, value = [], [], []
    for (src, tgt), amt in flows.items():
        source.append(index[src])
        target.append(index[tgt])
        value.append(round(amt, 2))
    return {'labels': labels, 'source': source, 'target': target, 'value': value}
