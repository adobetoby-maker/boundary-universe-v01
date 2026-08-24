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

---

# FINDINGS — 2026-08-23

Five things measured today. Three of them mean earlier work is wrong.

## 1. The pitch chain cancels itself — affects the shipped ch2 cast

`voice_chain.py` shifts pitch with `asetrate` followed by `atempo` to restore
duration. The `atempo` also undoes most of the spectral lift. Measured on a
Peter render:

| shift requested | centroid before | after |
|---|---|---|
| +2.00 st | 1333 Hz | **1291 Hz** (went DOWN) |
| +3.00 st | 1333 Hz | 1287 Hz |

Every per-character shift in `cast_split.py` is therefore doing less than its
number says. The code already worries that Renn at -1.35 sits only 0.20 st from
Darius and "may not separate"; in reality they are closer than that.

`sox pitch <cents>` shifts correctly and preserves duration exactly. It is
installed. Use it instead. Re-audition the ch2 cast shifts before re-rendering
that chapter -- the numbers there were chosen by ear against a broken chain.

## 2. EQ must come BEFORE pitch, not after

The 140Hz notch is aimed at the low-frequency throb. Shift the audio up first
and the throb moves with it -- at +5 st it sits near 187Hz and walks out from
under the notch. Applying EQ first and pitching second took Elena's sub-220Hz
energy from about -4dB to -8.0dB, twice as clean as the untreated tones.

## 3. Spectral centroid does NOT measure pitch

It tracks the spectral envelope, which `sox pitch` deliberately preserves. A
full octave shift moved centroid only 15%; a -3 st shift moved it UP. Centroid
is valid for comparing two renders of the SAME voice with NO pitch shift (that
is what makes it a good chunk-to-chunk drift metric) and useless for "is this
the right voice" or "how far apart are these characters". Toby's ear was
correct every time this metric disagreed with it.

## 4. Smaller chunks read better

Identical text, one 3600-char chunk vs two 1800-char chunks:

| | length | median pause | pauses >=0.8s | silence |
|---|---|---|---|---|
| one 3600 | 111.4s | 0.84s | 22 | 26.0% |
| two 1800 | 105.2s | **0.75s** | **12** | **22.6%** |

Six seconds tighter on the same words, half the long pauses. The seam was
inaudible on listening. Long chunks droop as they go.

## 5. The narrator workflow's delivery phrase HURTS a long-form read

`get_workflow_instructions('narrator')` prescribes one delivery phrase repeated
verbatim on every chunk to hold timbre. Measured on identical text:

| delivery phrase | median pause | pauses >=0.8s |
|---|---|---|
| "...unhurried pace" | 0.99s | 31 |
| "...steady forward momentum" | 0.91s | 28 |
| **none** | **0.80s** | **23** |

The bracket is written for fixed-window video takes. For continuous prose the
model performs it as extra deliberation. Omit it.

Not tested: whether the phrase helps timbre across chunks as claimed. It might
trade timbre for pacing. Pacing was the reported defect, so pacing won.

## 6. Truncation gate (new, required)

The workflow documents a 2048-char TTS limit; chapters 1-9 were rendered at
4000. Checked for silently dropped text by comparing chars/second across chunks:
every long chunk renders at 11.9-13.3 c/s and the short chunks (1488 and 2626
chars, under any limit) land at 11.9 and 12.6. Truncation at 2048 would show as
~6 c/s. No text was lost -- the 2048 limit applies to `seed_audio`, not to
`text2speech_v2`.

Keep the check. Any chunk whose chars/second falls outside its neighbours' band
means dropped text, a silent engine swap, or a failed render. It is cheap and
the drift analysis cannot see any of those.

## Scripts added

- `render_stitched.py` -- direct ElevenLabs API with request stitching
  (`previous_request_ids` + `previous_text`/`next_text`, fixed seed). Measured
  142 Hz chunk-to-chunk spread vs 374 Hz unstitched on the same chapter.
  Not usable with Holden: he is a higgsfield voice, not an ElevenLabs one.
- `assemble_fixed.py` -- measures every chunk and pulls it to the chapter
  median before joining. Used for the ch8 and ch9 renders now live.
- `pace.py` -- scales silences to a target median. NOTE: the narrator workflow
  says never time-stretch; prefer regenerating a bad take. Kept because the MCP
  route cannot prevent the drift at source.
