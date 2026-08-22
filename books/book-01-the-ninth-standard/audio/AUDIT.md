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

**READ** (spoken literally — must be zero before a full-book run): **1**

| Where | Text | Question |
|---|---|---|
| ch19 | `Research status: subject/participant.` | "subject-participant", or is "slash" the intended dossier reading? |

**DECIDE** (legitimate text needing an authorial call — not defects):

| Count | Category | The question |
|---|---|---|
| 86 | abbreviation | `Ms. Alvarez`, `Dr. Park` — engines usually handle these; verify by ear once |
| 49 | clock | **see below — three different readings share one syntax** |
| 42 | bare numeral | `12 meters`, `Age: 17`, `TOP 100` — leave as digits? |
| 16 | initial | `MERCER, KADE A.` fine; `Conduit Theory I.` reads "eye" not "one"; `labeled VIII` reads letter-by-letter |
| 9 | score | `4–0`, `3–1` — "four-nil"? "four to nothing"? "four, zero"? All of ch21–22 |
| 4 | ellipsis | trailing `…` on interrupted dialogue |
| 3 | decimal | `OUTPUT: 0.00`, `1.7`, `0.83 seconds` |
| 1 | ordinal | `7,304th` |

### The clock problem

49 instances, one syntax, three meanings. No rule can separate them:

| Form | Example | Should read |
|---|---|---|
| time of day | `At 10:17 every morning` | "ten seventeen" |
| countdown | `00:03` `00:09` `00:47` (ch06, on their own lines) | "three seconds"? or as displayed? |
| elapsed | `A timer in the corner showed 87:13` | "eighty-seven thirteen" |

The countdowns are the load-bearing ones. Chapter 6 is titled *Forty-Seven
Seconds* and those bare numerals **are** the drama. Getting them wrong is not a
pronunciation slip, it is the chapter losing its spine. This is a decision for
the author and it is deliberately not encoded.

---

## What `normalise.py` will not do

Three categories are left alone because guessing wrong is worse than leaving
digits: **clocks**, **scores**, **roman numerals**. The audit stays loud about
all three so they are decided, not defaulted.
