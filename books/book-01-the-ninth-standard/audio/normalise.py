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
    """Everything mechanical. Order matters: longer patterns first."""
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
    return t


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
