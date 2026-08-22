#!/usr/bin/env python3
"""
Audit every chapter's PREPARED text for anything a synthesiser reads wrong.

The whole reason this file exists: every defect found so far was invisible in
the manuscript and obvious in the payload. Bold markers, backticked scores, raw
comma numbers -- all of them looked fine in the .md and only became audible
after prep. So this runs prep() and inspects the output, never the source.

It reports, it does not fix. A finding is a question ("how should this be
read?"), and several categories below are legitimate text that merely needs a
decision. Silence is the goal; a clean run means the book can be rendered
without listening for surprises.

Usage:  python3 audit_text.py ../ms-all/ch*.md
"""
import collections, pathlib, re, sys, unicodedata

from prep_el import prep

# (id, severity, regex, why it matters)
# READ = will be spoken literally.  DECIDE = ambiguous, a human picks.
CHECKS = [
    ('markdown-bold',   'READ',   r'\*\*',                       'reads as "asterisk asterisk"'),
    ('markdown-star',   'READ',   r'(?<!\*)\*(?!\*)',            'reads as "asterisk"'),
    ('markdown-code',   'READ',   r'`',                          'reads as "backtick"'),
    ('markdown-head',   'READ',   r'(?m)^#{1,6}\s',              'reads as "hash"'),
    ('markdown-quote',  'READ',   r'(?m)^>\s',                   'reads as "greater than"'),
    ('markdown-link',   'READ',   r'\[[^\]]+\]\([^)]+\)',        'reads the URL aloud'),
    ('markdown-rule',   'READ',   r'(?m)^\s*[-*_]{3,}\s*$',      'reads as "dash dash dash"'),
    ('underscore',      'READ',   r'_',                          'reads as "underscore"'),
    ('pipe-table',      'READ',   r'\|',                         'reads as "vertical bar"'),
    ('symbol-math',     'READ',   r'[=<>~^\\@&+×÷±°%]',          'spoken as a symbol name'),
    ('slash',           'READ',   r'\S/\S',                      'reads as "slash"'),
    ('comma-number',    'DECIDE', r'\b\d+,\d{3}\b',              'digits, not words'),
    ('decimal',         'DECIDE', r'\b\d+\.\d+\b',               '"0.00" -> "zero point zero zero"?'),
    ('clock',           'DECIDE', r'\b\d{1,2}:\d{2}\b',          'colon time'),
    ('numeric-range',   'DECIDE', r'\b\d+\s*[-–—]\s*\d+\b',      'dash between numbers'),
    ('ordinal',         'DECIDE', r'\b\d+(st|nd|rd|th)\b',       '"1st"'),
    ('bare-number',     'DECIDE', r'(?<![\d,.:])\b\d{2,}\b(?![\d,.:])', 'unspelled numeral'),
    # "No." matched the word, not the abbreviation, and inflated this check
    # to 294 -- noise loud enough that a real finding would hide inside it. A
    # check nobody reads is as useless as a check that cannot see.
    ('abbrev-period',   'DECIDE', r'\b(Dr|Mr|Mrs|Ms|Prof|Sgt|Capt|Lt|Jr|Sr)\.\s+[A-Z]|\bNo\.\s*\d|\bvs\.',
                                                                 'period may read as a full stop'),
    ('initial',         'DECIDE', r'\b[A-Z]\.\s',                'single-letter initial'),
    ('dotted-caps',     'DECIDE', r'\b(?:[A-Z]\.){2,}',          'U.S. / Ph.D.'),
    ('ellipsis',        'DECIDE', r'\.{3}|…',                    'pause length is engine-dependent'),
]

ALLOWED_UNICODE = set('‘’“”—–… ')

def context(text, m, pad=46):
    a, b = max(0, m.start()-pad), min(len(text), m.end()+pad)
    return ('…' if a else '') + text[a:b].replace('\n', ' ⏎ ') + ('…' if b < len(text) else '')

totals = collections.Counter()
by_check = collections.defaultdict(list)
caps_lines = 0
chapters = 0

for path in sys.argv[1:]:
    chapters += 1
    ch = pathlib.Path(path).stem
    text = '\n\n'.join(prep(path))

    for name, sev, pat, _ in CHECKS:
        for m in re.finditer(pat, text):
            totals[name] += 1
            if len(by_check[name]) < 4:
                by_check[name].append((ch, context(text, m)))

    for line in text.split('\n'):
        s = line.strip()
        letters = [c for c in s if c.isalpha()]
        if len(letters) > 2 and all(c.isupper() for c in letters):
            caps_lines += 1

    for c in set(text):
        if ord(c) > 127 and c not in ALLOWED_UNICODE:
            totals[f'unicode {c!r} ({unicodedata.name(c, "?")})'] += 1

print(f'{chapters} chapters audited\n')
sev_of = {n: s for n, s, _, _ in CHECKS}
why_of = {n: w for n, _, _, w in CHECKS}

for sev in ('READ', 'DECIDE'):
    rows = [(n, c) for n, c in totals.items() if sev_of.get(n) == sev]
    print(f'--- {sev} ' + '-'*56)
    if not rows:
        print('  (clean)\n')
        continue
    for name, count in sorted(rows, key=lambda r: -r[1]):
        print(f'  {count:5}  {name:<16} {why_of[name]}')
        for chap, ctx in by_check[name]:
            print(f'         {chap}: {ctx}')
    print()

uni = {n: c for n, c in totals.items() if n.startswith('unicode ')}
print('--- UNEXPECTED UNICODE ' + '-'*42)
print('  (clean)' if not uni else
      '\n'.join(f'  {c:5}  {n[8:]}' for n, c in sorted(uni.items(), key=lambda r: -r[1])))

print(f'\n--- INFO {"-"*57}\n  {caps_lines:5}  all-caps lines (screen text; expected, not a defect)')
read_total = sum(c for n, c in totals.items() if sev_of.get(n) == 'READ')
print(f'\nWould be spoken literally: {read_total}')
