#!/usr/bin/env python3
"""
Shared text normalisation for both synthesis paths.

WHY THIS FILE EXISTS
--------------------
There were two prep scripts -- ssmlize.py for Google Studio-Q, prep_el.py for
ElevenLabs -- and they each grew their own copy of "turn numerals into words".
They then drifted, and drifted asymmetrically:

    ssmlize.py had clock and percent handling.  prep_el.py did not.
    prep_el.py had the mid-sentence `000` fix.  ssmlize.py did not.

The production voice runs through prep_el.py, so the production voice was the
one missing percent handling on a chapter whose climax is a screen reading
"SURVIVAL PROJECTION: +14.7%".

Nobody chose that. It is what two copies of the same idea do over time. Hence
one module, imported by both.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
Three categories are left alone because they are authorial decisions, not
mechanical ones, and guessing wrong is worse than leaving digits:

  clocks      "09:30" is a time; "00:47" is a countdown; "87:13" is elapsed.
              Same syntax, three readings. See AUDIT.md.
  scores      "4-0" is "four-nil" or "four to nothing" or "four, zero".
  roman       "Conduit Theory I" is "one"; "labeled VIII" is "eight".

audit_text.py reports all three and stays noisy about them on purpose.
"""
import re

ONES = ("zero one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty",
        6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}


def say_two_digit(n: int) -> str:
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + (f"-{ONES[o]}" if o else "")


def say_under_thousand(n: int) -> str:
    if n < 100:
        return say_two_digit(n)
    h, r = divmod(n, 100)
    out = f"{say_two_digit(h)} hundred"
    return f"{out} {say_two_digit(r)}" if r else out


def _thousands(m):
    """Spell comma-grouped numbers.

    Capped at 99,999 rather than extended: above that the manuscript has none,
    and a rule that guesses at magnitudes it has never seen is how "18,000"
    became "eighteen, zero zero zero" the first time.
    """
    th, rest = int(m.group(1)), int(m.group(2))
    if th > 99:
        return m.group(0)
    head = f"{say_two_digit(th)} thousand"
    return f"{head} {say_under_thousand(rest)}" if rest else head


def _signed_percent(m):
    sign = {"-": "minus ", "−": "minus ", "+": "plus "}.get(m.group(1), "")
    whole, frac = m.group(2), m.group(3)
    body = say_under_thousand(int(whole))
    if frac:
        body += " point " + " ".join(ONES[int(d)] for d in frac)
    return f"{sign}{body} percent"


def normalise(t: str) -> str:
    """Everything mechanical, then the reading choices in decide()."""
    # "#" is a rank marker, and it has to be converted BEFORE the thousands
    # rule spells the digits, or the '#' is left stranded in front of words.
    t = re.sub(r'#(?=\s*\d)', 'number ', t)
    # Percentages before bare decimals, signed before unsigned.
    t = re.sub(r"([-−+])?(\d+)(?:\.(\d+))?%", _signed_percent, t)
    # Comma numbers. Must run before any bare-digit rule.
    t = re.sub(r"\b(\d+),(\d{3})\b", _thousands, t)
    # The score. Anchoring this to a bare line missed the one in Chapter 4 that
    # sat mid-sentence; requiring non-digit neighbours keeps it out of 18,000.
    t = re.sub(r"(?<![\d,])0{3}(?![\d,])", "zero zero zero", t)
    # Screen readouts: "RANK: a / b" reads as "slash" otherwise.
    t = re.sub(r"(?m)^(\s*[A-Z][A-Z \-]+:\s*)(.+?)\s*/\s*(.+)$", r"\1\2 of \3", t)
    # Signed deltas outside percentages: "MERIDIAN +5", "+6,255". The percent
    # rule above only fires when a % follows, so score deltas fell through.
    t = re.sub(r"(?<![\w.])([-−+])(?=[\d\w])",
               lambda m: "plus " if m.group(1) == "+" else "minus ", t)
    # Symbols that have no spoken form at all.
    t = t.replace("→", " to ").replace("×", " by ").replace("±", " plus or minus ")
    t = re.sub(r"(?<=\s)=(?=\s)", " equals ", t)
    t = re.sub(r"(?<=\s)<(?=\s)", " less than ", t)
    t = re.sub(r"(?<=\s)>(?=\s)", " greater than ", t)
    return decide(t)


def strip_markdown(t: str) -> str:
    """Remove every construct a synthesiser would pronounce.

    198 bold spans exist across Book 1, used for screen text and phone messages
    -- the dramatic beats. Inline code was the one this originally missed.
    """
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.S)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", t, flags=re.S)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", "---", t)
    return t


def chapter_heading(n: int, title: str) -> str:
    """"# Chapter 21 - Midyear" -> "Chapter Twenty-one. Midyear."

    The literal word-list this replaced stopped at Twenty and was indexed
    directly, so every chapter from 21 on raised IndexError -- a hard stop
    thirteen chapters into any full-book run.
    """
    return f"Chapter {say_two_digit(n).capitalize()}. {title.rstrip('.')}."


if __name__ == "__main__":
    for s in ["-8.3%", "+14.7%", "99.98%", "83.1%", "10,482", "18,000",
              "Not 000.", "FIRST-YEAR RANK: 10,482 / 10,482",
              "nine thousand → 114", "ZERO LASTS < 72 HOURS"]:
        print(f"  {s:<36} -> {normalise(s)}")
    for n in (1, 20, 21, 33):
        print(f"  ch{n:02d} -> {chapter_heading(n, 'Test Title')}")

# ---------------------------------------------------------------------------
# The judgement calls.
#
# Everything below was previously left alone and reported by audit_text.py as a
# DECIDE finding, on the principle that guessing wrong is worse than leaving
# digits. Toby's instruction was "just make them sound good", so these are now
# decided. Each one is a reading choice, and the reasoning is recorded because a
# future reader will otherwise assume it was mechanical.
# ---------------------------------------------------------------------------

ROMAN = {'I': 'One', 'II': 'Two', 'III': 'Three', 'IV': 'Four', 'V': 'Five',
         'VI': 'Six', 'VII': 'Seven', 'VIII': 'Eight', 'IX': 'Nine', 'X': 'Ten',
         'XI': 'Eleven', 'XII': 'Twelve'}

# Words that mark the next token as an ordinal designator rather than a pronoun.
# "Standard IX" is a rank. A bare "I" is almost always the pronoun, so a roman
# numeral is only converted when one of these precedes it -- the alternative is
# turning "I" into "One" somewhere in dialogue and never noticing.
DESIGNATOR = (r'Standard|Theory|Level|Class|Grade|Tier|Rank|Phase|Book|Part|'
              r'Volume|Section|Stage|Mark|Type|Wave|Round')


def _thousands_int(n: int) -> str:
    th, rest = divmod(n, 1000)
    head = f"{say_two_digit(th)} thousand"
    return f"{head} {say_under_thousand(rest)}" if rest else head


def _roman(m):
    word, num = m.group(1), ROMAN[m.group(2).upper()]
    # "STANDARD IX" is screen text; keep it shouting. "Standard IX" is prose.
    return f"{word} {num.upper() if word.isupper() else num}"


def _countdown(m):
    """00:271:09:31:46 -> days, hours, minutes, seconds.

    A narrator reading a wall display says the units. The leading field is
    always 00 in Book 2 and carries no information, so it is dropped rather
    than voiced as a stray zero.
    """
    _, d, h, mi, sec = m.groups()
    parts = []
    for val, unit in ((int(d), 'day'), (int(h), 'hour'),
                      (int(mi), 'minute'), (int(sec), 'second')):
        if val or unit == 'second':
            parts.append(f"{say_under_thousand(val)} {unit}{'' if val == 1 else 's'}")
    return ', '.join(parts)


def _bare_countdown(m):
    """A lone 00:47 on its own line is a countdown, not a time.

    Chapter 6 is titled "Forty-Seven Seconds" and these numerals ARE the drama;
    read as "zero zero forty-seven" they stop being it. Restricted to a bare
    line with a zero hour field so that "At 10:17" is untouched.
    """
    mm, ss = int(m.group(1)), int(m.group(2))
    if mm == 0:
        return f"{say_two_digit(ss)} second{'' if ss == 1 else 's'}"
    return (f"{say_two_digit(mm)} minute{'' if mm == 1 else 's'} "
            f"{say_two_digit(ss)} second{'' if ss == 1 else 's'}")


def _clock(m):
    """Time of day: 10:17 -> "ten seventeen", 09:00 -> "nine o'clock"."""
    h, mm = int(m.group(1)), int(m.group(2))
    if mm == 0:
        return f"{say_two_digit(h)} o'clock"
    if mm < 10:
        return f"{say_two_digit(h)} oh {ONES[mm]}"
    return f"{say_two_digit(h)} {say_two_digit(mm)}"


def _score(m):
    """4-0 -> "four to nothing". Tournament scores, chapters 21-22.

    "to nothing" rather than "to zero" because that is how a scoreline is
    actually said aloud, and these lines are crowd-facing.
    """
    a, b = int(m.group(1)), int(m.group(2))
    return f"{say_two_digit(a)} to {'nothing' if b == 0 else say_two_digit(b)}"


def _decimal(m):
    whole, frac = int(m.group(1)), m.group(2)
    return f"{say_under_thousand(whole)} point " + ' '.join(ONES[int(d)] for d in frac)


def _ordinal(m):
    """7,304th -> spelled, with the final word made ordinal."""
    n = int(m.group(1).replace(',', ''))
    if n > 99999:
        return m.group(0)
    th, rest = divmod(n, 1000)
    words = (f"{say_two_digit(th)} thousand " if th else '') + say_under_thousand(rest)
    tail = {'one': 'first', 'two': 'second', 'three': 'third', 'five': 'fifth',
            'eight': 'eighth', 'nine': 'ninth', 'twelve': 'twelfth'}
    last = words.split()[-1].split('-')[-1]
    if last in tail:
        return words[:len(words) - len(last)] + tail[last]
    if last.endswith('y'):
        return words[:-1] + 'ieth'
    return words + 'th'


def decide(t: str) -> str:
    """The reading choices. Order matters: longest patterns first."""
    # Countdown displays before any other colon rule.
    t = re.sub(r'\b(\d{2}):(\d{3}):(\d{2}):(\d{2}):(\d{2})\b', _countdown, t)
    # A bare countdown on its own line, before the general clock rule.
    t = re.sub(r'(?m)^\s*(\d{2}):(\d{2})\s*$', _bare_countdown, t)
    t = re.sub(r'\b(\d{1,2}):(\d{2})\b', _clock, t)
    # Ordinals before the thousands rule, which would otherwise eat the comma.
    t = re.sub(r'\b(\d{1,3}(?:,\d{3})?)(?:st|nd|rd|th)\b', _ordinal, t)
    # Scores: en/em dash between small numbers.
    t = re.sub(r'\b(\d{1,2})\s*[\u2013\u2014]\s*(\d{1,2})\b', _score, t)
    # Record identifiers built on a roman numeral: "VIII-01" .. "VIII-12".
    # These are the twelve Standard Eight slots -- the clue trail Book 2's
    # title rests on -- and left alone a synthesiser says "vee eye eye eye".
    # Read as a screen readout: "Eight-oh-one" through "Eight-twelve".
    # Requires two or more capitals, which keeps "I-95" out of it: a lone "I"
    # before a number is a highway or a pronoun, never a Standard slot.
    def _record_id(m):
        word = ROMAN[m.group(1)].upper()
        n = int(m.group(2))
        return f"{word} {'oh ' + ONES[n] if n < 10 else say_two_digit(n)}"
    t = re.sub(r'\b(I{2,3}|IV|VI{1,3}|IX|XI{1,2}|X)-(\d{1,2})\b', _record_id, t)
    # Roman numerals, only after a designator word.
    t = re.sub(rf'\b({DESIGNATOR})\s+(I{{1,3}}|IV|VI{{0,3}}|IX|XI{{0,2}}|X)\b',
               _roman, t, flags=re.I)
    t = re.sub(r'\blabeled\s+(I{1,3}|IV|VI{0,3}|IX|X)\b',
               lambda m: f"labeled {ROMAN[m.group(1)]}", t)
    # Decimals that are not percentages (percentages are handled in normalise()).
    t = re.sub(r'\b(\d+)\.(\d+)(?!\d*%)', _decimal, t)
    # "#37" is a rank, not a hash.
    # Bare ranks the thousands rule did not reach: "number 37" -> spelled.
    t = re.sub(r'\bnumber (\d{1,3})\b',
               lambda m: 'number ' + say_under_thousand(int(m.group(1))), t)
    # A slash inside a word is a compound, not the word "slash".
    t = re.sub(r'(?<=[a-z])/(?=[a-z])', '-', t)
    return t
