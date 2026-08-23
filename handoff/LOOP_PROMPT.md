# LOOP PROMPT

Paste the block below into each agent. It is the same prompt for both — the
`ROLE` line is the only thing that changes.

---

## For the PROSE agent

```
ROLE: prose

You are finishing Book 1 of the Boundary Universe — "The Ninth Standard" —
to the point where it can be recorded as an audiobook. You are running
unattended. Toby is not watching and will not answer questions.

FIRST, before any other action:
  git clone https://github.com/adobetoby-maker/boundary-universe-v01.git
  cd boundary-universe-v01
  git fetch origin --prune
  git checkout main
  git show origin/planning/kanban-automation:handoff/AUTONOMOUS_LOOP.md

Read that file completely. It contains the branch map, the six-pass gate, a
catalogue of fifteen traps that have already cost a day, and the priority
order. Do not begin work until you have read it. In particular: Book 1 lives
on `expand/book1-ch01-10` and NOWHERE ELSE. Every other branch is 41,000
words short.

YOUR LANE: the manuscript on expand/book1-ch01-10 — commit there, not on
main — plus CLUE_LEDGER.md,
STATE_LEDGER.md and CHAPTER_ATTESTATIONS.md. Do not touch anything under
audio/. Do not touch Book 2.

YOUR JOB, in order:
  1. Chapter 32 (Consensus) 2,838 -> ~5,500 words. This is the climax and it
     is at 35% of its architecture target. It is the book's biggest defect.
  2. Chapter 30 (Siege) 2,701 -> ~5,000.
  3. Chapters 13, 21, 26 -> ~4,500 each.
  4. The deadpan-reply tic at the emotional peaks (ch20, 24, 25, 29, 32).
     Chapter 31 has already been repaired this way — read its git history and
     match that approach. Do not strip the tic globally; it is the voice.
  5. The three continuity bugs in section 6 of the manual.

EVERY chapter you touch goes through all six passes before you mark it
attested. Read the pass count from START_HERE.md — it changed three times in
one day. The BSBC checklist is in planning/BSBC_PASS6.md; do not work from
memory.

EACH ITERATION:
  - git fetch origin --prune
  - python3 scripts/generate_status.py     # no args: each book
    defaults to its own branch. Passing --manuscript-ref forces BOTH
    books to one ref and reports the other as zero.
  - do the highest-priority remaining item
  - commit, push
  - if three iterations in a row change nothing, stop and write a report

EXPANSION MEANS SCENES, NOT SENTENCES. If a chapter grows because paragraphs
got longer, you have failed the density pass. Convert summary into scene.
Chapter 31's repair is the reference: it went 2,328 -> 3,650 by giving a
seventeen-year reunion the room to actually happen, and by answering a
question the previous draft deferred to a sequel.

STOP AND REPORT rather than proceeding, if:
  - a destructive git operation would be required
  - a canon decision is needed (character names, cutting a chapter, what a
    countdown counts toward)
  - the same check fails three times with different fixes attempted

Write commit messages that say what you LEARNED, not only what changed.
```

---

## For the AUDIO agent

```
ROLE: audio

You are producing the audiobook for Book 1 of the Boundary Universe — "The
Ninth Standard". You are running unattended. Toby is not watching and will
not answer questions.

FIRST, before any other action:
  git clone https://github.com/adobetoby-maker/boundary-universe-v01.git
  cd boundary-universe-v01
  git fetch origin --prune
  git checkout main
  git show origin/planning/kanban-automation:handoff/AUTONOMOUS_LOOP.md

WORK FROM main. The pipeline scripts and manifest.json exist ONLY on main.
The manuscript exists ONLY on expand/book1-ch01-10. Read chapters across
with git show, e.g.

  git show origin/expand/book1-ch01-10:books/book-01-the-ninth-standard/\
manuscript/chapter-08-the-ladder.md > ms/ch08.md

Do not checkout the expand branch expecting prep_el.py to be there. It is
not. Do not copy the manuscript onto main — that forks the book again.

Read that file completely, then read
books/book-01-the-ninth-standard/audio/AUDIT.md. Between them they contain
the locked voice settings, the pipeline, and fifteen traps that have already
cost a day. Do not render anything until you have read both.

YOUR LANE: everything under audio/ and the pipeline scripts. Do not edit the
manuscript. Do not touch Book 2.

CURRENT STATE: chapters 1-7 are rendered. Chapters 8-33 are not.

THE PIPELINE, per chapter:
  1. Extract from origin/expand/book1-ch01-10 — NOT from any other branch
  2. python3 prep_el.py ../ms/chNN.md
  3. python3 audit_text.py ../ms/chNN.md    <- MUST show zero READ findings
  4. Render each chunk: ElevenLabs, voice Holden
     3c9d6053-6334-592c-8997-4e325286af3f
  5. Decode-validate EVERY downloaded part with ffprobe. Never check size —
     a 111-byte S3 AccessDenied page passes a size check and fails to decode.
  6. python3 assemble_el.py chNN <urls...>
  7. Add to manifest.json with bytes, durationSec, sha256, url
  8. Push, then curl -sI the live URL: must be HTTP 200 and the byte count
     must match the manifest

LOCKED — do not change:
  Chain: highpass=85, -6.5dB@140 Q1.0, -2dB@250 Q1.2, THEN +0.5 st.
  The order is EQ then shift. Reversing it moves the notch 4.1 Hz off the
  narrator already shipped in chapters 1-7, and the book would no longer
  sound like one reader.

THE HANDOFF RULE — this is the one that matters:
  Render a chapter ONLY IF it is attested AND its file hash has been
  unchanged for one full loop iteration. Rendering ahead of the prose agent
  guarantees re-rendering. Chapter 31 changed by 1,290 words forty minutes
  after review.
  DO NOT render chapters 30, 31 or 32 until the prose agent has finished
  expanding them. They are the climax and they are being rewritten.

ORDER: chapters 8, 9, 10, then 11 onward as each becomes eligible.

RATE LIMITS ARE REAL. ElevenLabs 429s at roughly 40% when pushed hard and
recovers when paced. Twelve requests per batch, then wait for completion
before the next batch. Do not retry in a tight loop.

EACH ITERATION:
  - git fetch origin --prune
  - identify eligible chapters (attested + hash stable)
  - render the next one
  - verify live
  - if no chapter is eligible, do nothing and say so in one line
  - if three iterations in a row render nothing, stop and write a report

STOP AND REPORT rather than proceeding, if:
  - audit_text.py shows a READ finding you cannot resolve without changing
    the manuscript (that is the prose agent's lane — file it, don't fix it)
  - a rendered chapter's duration is more than 20% off the expected
    words/9,300-per-hour estimate
  - the same chapter fails to assemble twice

Write commit messages that say what you LEARNED, not only what changed.
```

---

## Notes for whoever starts this

**Both agents can run at once.** The lanes do not overlap: prose owns the
manuscript, audio owns `audio/`. The only coupling is the handoff rule, and it
is one-directional — audio waits on prose, never the reverse.

**The loop ends when all four conditions in §1 of the manual are true.** Not
when the prose is finished. Not when the renders complete.

**Expect the first iteration of each agent to produce nothing but reading.**
That is correct behaviour. The manual is ~350 lines and the trap catalogue is
the highest-value part of this entire handoff.

**If the pairing gets stuck**, the most likely cause is the branch trap: an
agent measuring Book 1 on the wrong branch will conclude the book is half the
size it is, and will either "expand" chapters that are already expanded or
render audio from a manuscript missing 41,000 words. `generate_status.py` flags
this on every run — read its DRIFT output before believing any word count.
