#!/usr/bin/env python3
"""
Turn a manuscript chapter into SSML for Google Studio voices.

Chapter 1 was marked up by hand, which is not repeatable across 33 chapters.
This encodes the conventions that hand pass established, so every chapter gets
the same rhythm without the same labour.

The governing observation, from Chapter 1:

    The manuscript is written in single-line beats, and that line-breaking IS
    the performance direction. TTS sees a paragraph and reads it as one breath.
    Every beat must be re-encoded as an explicit <break> or the rhythm is lost.

Rules derived from the hand pass:

  short line, ends in a full stop      a beat            400ms
  dialogue line (opens with a quote)   fast exchange     350ms
  multi-sentence prose paragraph       a thought         650ms
  ALL-CAPS line                        screen text       88% rate, breaks either side
  scene break (--- or ⸻)               new location      1400ms

Studio constraint discovered by 400: <prosody> rejects `pitch` on Studio
voices, so rate and silence are the only instruments available.
"""

import html
import re
import sys

# Numbers a synthesiser reliably mangles. Order matters — the longer, more
# specific patterns must fire before the general ones, or "18,000" becomes
# "eighteen, zero zero zero".
NUMBER_SUBS = [
    (r"\b(\d{1,2}):(\d{2})\b", None),          # clock times, handled in code
    (r"\b(\d+),(\d{3})\b", None),              # thousands, handled in code
    (r"(?m)^0{3}$", "Zero. Zero. Zero."),      # the score — its own line only
    (r"([-−])(\d+)\.(\d+)%", r"minus \2 point \3 percent"),
    (r"\+(\d+)\.(\d+)%", r"plus \1 point \2 percent"),
    (r"\b(\d+)\.(\d+)%", r"\1 point \2 percent"),
]

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}


def say_two_digit(n: int) -> str:
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + (f"-{ONES[o]}" if o else "")


def say_clock(m):
    h, mm = int(m.group(1)), int(m.group(2))
    if mm == 0:
        return f"{say_two_digit(h)} o'clock"
    if mm < 10:
        return f"{say_two_digit(h)} oh {ONES[mm]}"
    return f"{say_two_digit(h)} {say_two_digit(mm)}"


def say_thousands(m):
    th, rest = int(m.group(1)), m.group(2)
    head = say_two_digit(th) if th < 100 else str(th)
    if rest == "000":
        return f"{head} thousand"
    return f"{head} thousand {say_two_digit(int(rest))}" if int(rest) < 100 else m.group(0)


def normalise_numbers(t: str) -> str:
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", say_clock, t)
    t = re.sub(r"\b(\d+),(\d{3})\b", say_thousands, t)
    for pat, rep in NUMBER_SUBS:
        if rep is not None:
            t = re.sub(pat, rep, t)
    return t


DIALOGUE_OPEN = ('"', "“", "'", "‘")


def classify(line: str):
    """Return (ssml_for_line, break_ms).

    Calibrated against the hand-marked Chapter 1, whose 697 breaks average
    580ms. An earlier version keyed pause length on line length and got it
    exactly backwards: a short line is usually an EMPHASIS beat and wants MORE
    air, not less. "Darius did not smile." was given 700ms by hand and 400ms by
    the generator, and doing that 498 times made the read both fast and
    monotonous. Variation is the rhythm; a uniform value reads mechanical even
    at the right average.
    """
    stripped = line.strip()
    esc = html.escape(stripped, quote=False)

    letters = [c for c in stripped if c.isalpha()]
    if letters and all(c.isupper() for c in letters) and len(stripped) > 2:
        return f'<break time="450ms"/><prosody rate="88%">{esc}</prosody>', 800

    words = len(stripped.split())
    sentences = len(re.findall(r"[.!?][\"\u201d]?(\s|$)", stripped))
    question = stripped.rstrip('"\u201d').endswith("?")

    if stripped.startswith(DIALOGUE_OPEN):
        # Exchanges stay quick; a question still gets a touch more room.
        gap = 450 if question else 400
        if words > 25:
            gap = 550
        return esc, gap

    if sentences >= 2 or len(stripped) > 180:
        return esc, 750                      # a thought, not a beat

    if words <= 4:
        return esc, 650                      # emphasis beat — the landing
    if words <= 12:
        return esc, 550
    return esc, 600


def ssmlize(markdown: str) -> tuple[str, str]:
    """Return (title, ssml_body)."""
    lines = markdown.replace("\r\n", "\n").split("\n")

    title = "Chapter"
    out = []
    for raw in lines:
        s = raw.strip()
        if not s:
            continue

        if s.startswith("#"):
            heading = s.lstrip("#").strip()
            # "Chapter 2 — Zero Protocol" -> "Chapter Two. Zero Protocol."
            m = re.match(r"Chapter\s+(\d+)\s*[—–-]\s*(.+)", heading)
            if m:
                n = int(m.group(1))
                words = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve "
                         "Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty "
                         "Twenty-One Twenty-Two Twenty-Three Twenty-Four Twenty-Five Twenty-Six "
                         "Twenty-Seven Twenty-Eight Twenty-Nine Thirty Thirty-One Thirty-Two "
                         "Thirty-Three").split()
                heading = f"Chapter {words[n] if n < len(words) else n}. {m.group(2).rstrip('.')}."
            title = heading
            out.append(f'{html.escape(heading, quote=False)}<break time="1200ms"/>')
            continue

        if s in {"---", "***", "⸻", "* * *"}:
            out.append('<break time="1400ms"/>')
            continue

        s = normalise_numbers(s)
        body, gap = classify(s)
        out.append(f'{body}<break time="{gap}ms"/>')

    return title, "\n".join(out)


if __name__ == "__main__":
    src = sys.argv[1]
    with open(src, encoding="utf-8") as fh:
        t, body = ssmlize(fh.read())
    print(f"# {t}", file=sys.stderr)
    print(f"# {len(body):,} chars, {body.count('<break')} breaks, "
          f"{body.count('<prosody')} screen-text spans", file=sys.stderr)
    sys.stdout.write(f"<speak>\n{body}\n</speak>\n")
