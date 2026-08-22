# TEXT AUDIT — BOOK 1

Every defect in this file was invisible in the manuscript and obvious in the
prepared text. That is the whole finding, and it is why `audit_text.py` runs
`prep()` and inspects the payload rather than reading the `.md`.

Run it before rendering anything:

```bash
python3 audit_text.py ../../../../ms-all/ch*.md
```

Target: **zero READ findings.** DECIDE findings are questions, not errors —
they stay noisy on purpose.

---

## Why we are not automating yet

Thirteen defects, found across five rendered chapters and one static sweep.
Six of them would have been reproduced into all 33 chapters by an unattended
pipeline, and one would have stopped it dead at Chapter 21.

| # | Defect | Found by | Blast radius |
|---|---|---|---|
| 1 | `**bold**` read as "asterisk" | rendering ch01 | 198 spans, every chapter |
| 2 | `` `000` `` backticks never stripped | rendering ch04 | every inline-code span |
| 3 | Spoken-zeros anchored `^0{3}$`, blind mid-sentence | rendering ch04 | every mid-sentence score |
| 4 | Thousands rule handled only `X,000` | rendering ch04 | every rank — the book's motif |
| 5 | `RANK: a / b` → "slash" | rendering ch04 | every screen ratio |
| 6 | **Stray-markdown counter only counted `**`** | rendering ch04 | **hid 2, 3 and 4** |
| 7 | `\b000\b` matched inside `18,000` | rendering ch01 | "eighteen, zero zero zero" |
| 8 | Pause length keyed on line length, inverted | listening to ch01 | whole book read too fast |
| 9 | Studio rejects `<prosody pitch>` | HTTP 400 | every Studio render |
| 10 | `raw.githubusercontent` serves LFS pointers | fetching | every manifest URL |
| 11 | **Chapter-number list stopped at Twenty** | audit | **IndexError, ch21–33** |
| 12 | **Two prep scripts, divergent normalisation** | audit | root cause of 13 |
| 13 | Percentages unhandled on the production path | audit | 14 screen readouts |

Defect 6 is the one to remember. The check that was supposed to catch 2, 3 and 4
counted only `**`, so it printed a clean `0` with two backticks sitting in the
payload. **A check blind to what it guards is worse than no check, because it
converts a defect into a confirmed pass.**

Defect 12 is the one that generates the others. There were two prep scripts —
`ssmlize.py` for Studio-Q, `prep_el.py` for ElevenLabs — each with its own copy
of "turn numerals into words", and they drifted asymmetrically:

```
ssmlize.py had clock + percent handling.   prep_el.py did not.
prep_el.py had the mid-sentence 000 fix.   ssmlize.py did not.
```

The production voice runs through `prep_el.py`. So the production voice was the
one missing percent handling, on a chapter whose climax is a screen reading
`SURVIVAL PROJECTION: +14.7%`. Nobody chose that; it is what two copies of one
idea do over time. Both now import `normalise.py` and cannot drift again.

---

## Current state — 33 chapters, 99,976 words

**READ** (spoken literally): **0** across Book 1 and Book 2 Chapter 1.

## The reading decisions

These were open questions. They are now decided, in `decide()` inside
`normalise.py`, because a decision recorded in code beats a decision remembered.

| Was | Reads as | Why |
|---|---|---|
| `Standard IX` | Standard Nine | It is the title concept of Book 2. `IX` reads "eye ex". |
| `STANDARD IX` | STANDARD NINE | Screen text keeps shouting. |
| `00:271:09:31:46` | two hundred seventy-one days, nine hours, thirty-one minutes, forty-six seconds | A narrator reading a wall display says the units. The leading `00` is always zero and carries nothing. |
| `00:47` on its own line | forty-seven seconds | Chapter 6 is *Forty-Seven Seconds*. These numerals **are** the drama; "zero zero forty-seven" is not. |
| `10:17` mid-sentence | ten seventeen | Time of day. |
| `87:13` | eighty-seven thirteen | Elapsed timer, read as displayed. |
| `4–0` | four to nothing | How a scoreline is actually said. Chapters 21–22. |
| `3–1` | three to one | |
| `#37` | number thirty-seven | Rank marker, not a hash. |
| `0.00` | zero point zero zero | |
| `7,304th` | seven thousand three hundred fourth | |
| `Conduit Theory I` | Conduit Theory One | |
| `labeled VIII` | labeled Eight | |
| `subject/participant` | subject-participant | A compound, not the word "slash". |

**Roman numerals convert only after a designator word** — Standard, Theory,
Level, Class, Rank, Book, Part and so on. A bare `I` is almost always the
pronoun, and converting it would turn "I know." into "One know." somewhere in
dialogue and never be noticed.

**Two countdown rules, deliberately separate.** A bare `00:47` on its own line
is a countdown; `At 10:17` mid-sentence is a time. Same syntax, and no single
rule can serve both, so the bare-line case is matched with an anchor and
everything else falls through to the clock rule.

## What is still left alone

| Count | Category | Why it is fine |
|---|---|---|
| 90 | `Ms.` `Dr.` `Mr.` | Engines handle these; verified by ear across five chapters |
| 37 | `12 meters`, `Age: 17`, `TOP 100` | Bare numerals read correctly |
| 15 | `MERCER, KADE A.`, `J. RAMOS` | Initials should read as letters |
| 4 | trailing `…` | Interrupted dialogue; engine timing is acceptable |

---

## Chapters rendered before these rules

Most were hand-corrected at synthesis time and match. Two spots do not:

| File | Reads | Should read |
|---|---|---|
| `ch02…holden.mp3` | "twenty forty-three", "fifteen thirty" as digits | as words |
| `ch04…holden.mp3` | `OUTPUT: 0.00` as digits | zero point zero zero |

Both are cases where the engine's own normalisation is likely acceptable, so
they are recorded rather than re-rendered. `ch02…cast.mp3`, `ch03`, `ch05` were
hand-corrected and already match.
