# AUTONOMOUS LOOP — OPERATING MANUAL

**For:** an agent pairing (Codex + Claude Code, or equivalent) running unattended
until Book 1 is ready to be listened to.

**Written:** 2026-08-22, after a full working day on this repository. Everything
below is either measured or was learned by breaking it. Read the whole file
before the first commit. The traps section will save you more time than the
protocol section.

---

## 1. THE GOAL

**Book 1 — *The Ninth Standard* — finished to audio.**

"Ready to be listened to" means all four of these, not three:

1. All 33 chapters pass the six-pass gate and are attested.
2. All 33 chapters have a `holden` render in `audio/manifest.json`.
3. `audit_text.py` reports **zero READ findings** across the book.
4. Every audio URL returns HTTP 200 with a byte count matching the manifest.

Nothing else counts as done. Not "the prose is finished." Not "the render
completed." The four checks above are the contract.

---

## 2. WHERE THINGS ACTUALLY ARE

### The branch trap — read this before anything else

Book 1 exists in two materially different versions:

| Branch | Book 1 words | Use it? |
|---|---|---|
| `expand/book1-ch01-10` | **101,298** | **YES — this is the book** |
| `draft/book-02-four-pass` | 58,672 | No — pre-expansion, 41k words short |
| `main` | 1 chapter | No |
| everything else | ≤58,672 | No |

Twice in one session someone concluded Book 1 was barely written, having looked
only at `main`. The expanded manuscript — including the twelve-slot clue trail
that Book 2's title depends on — lives on `expand/book1-ch01-10` **and nowhere
else**. Book 2 is being drafted from a branch that cannot see those clues. That
is a live continuity risk, not a tooling detail.

`scripts/generate_status.py` scans every branch and reports this automatically.
Run it before trusting any word count.

### No single branch has everything you need

This caught the author of this document while writing it. Three branches hold
three different halves of the job:

| What | Lives on | Nowhere else |
|---|---|---|
| Book 1 manuscript (101k words) | `expand/book1-ch01-10` | ✔ |
| Audio pipeline scripts + `manifest.json` | `main` | ✔ |
| Planning, dashboard, `generate_status.py`, this file | `planning/kanban-automation` | ✔ |
| Book 2 manuscript | `draft/book-02-four-pass` | ✔ |

So: work from `main` (it has the scripts and the manifest), and read the
manuscript out of the expand branch with `git show`:

```bash
git checkout main
git show origin/expand/book1-ch01-10:books/book-01-the-ninth-standard/manuscript/chapter-08-the-ladder.md > ms/ch08.md
```

Do not `git checkout expand/book1-ch01-10` and expect `prep_el.py` to be there.
It is not. Do not copy the manuscript onto `main` either — that would fork the
book a second time, which is the problem this table exists to prevent.

### Current state (2026-08-22 19:20 MDT)

| | |
|---|---|
| Book 1 prose | 101,298 / 187,000 target = **54%** |
| Book 1 audio | **7 of 33** chapters rendered (ch1–7) |
| Book 2 prose | 30 of 34 chapters, 77,608 words |
| Book 2 audio | none, and none should be attempted |

**Book 1's shortfall is concentrated in the climax**, which is the single most
important fact in this document:

| Chapter | Have / Target | |
|---|---|---|
| 32 Consensus | 2,838 / 8,200 | **35%** ← the climax |
| 30 Siege of Asterion | 2,701 / 7,800 | **35%** |
| 13 Cross Examination | 2,183 / 5,700 | 38% |
| 31 Aaron | 3,650 / 6,200 | 59% (was 38%, repaired 2026-08-22) |

Chapters 1–2 sit at 86% and 77%. The book is fully dramatised where it
establishes and compressed where it pays off. Fix that order of operations.

### The shipped audio is provisional — all seven chapters (added 19:40)

`loop/done.sh` measures every chapter against its `EXPANSION_TRACKER.md`
target. All 33 are under it, **including the seven already rendered**:

| ch | have / target | | ch | have / target | |
|---|---|---|---|---|---|
| 01 | 4,572 / 5,300 | 86% | 05 | 3,143 / 5,400 | 58% |
| 02 | 3,920 / 5,100 | 77% | 06 | 3,728 / 5,600 | 67% |
| 03 | 3,494 / 5,700 | 61% | 07 | 3,072 / 4,900 | 63% |
| 04 | 3,088 / 5,300 | 58% | | | |

Consequence: when the prose lane brings any of ch1–7 to target, that chapter's
audio is stale and must be withdrawn from `manifest.renders[]` and re-rendered.
"Already rendered" is not "done". Budget for re-rendering all seven.

Consequence for eligibility: **hash-stability is not eligibility.** A chapter is
stable while the prose agent simply has not reached it. The audio lane's gate is
the word target, and by that gate **zero chapters are currently eligible** —
early audio iterations correctly render nothing.

### Book 1 is not Book 2 — three files do not exist (added 19:40)

Three separate corrections were needed because a Book 2 filename was assumed to
apply to Book 1. Verify with `git ls-tree -r --name-only <branch> | grep -i X`
before referencing any tracking file.

| File | Reality |
|---|---|
| `START_HERE.md` | Book 2 only. Book 1 has no equivalent. |
| `CHAPTER_ATTESTATIONS.md` | Book 2 only. Book 1 uses `EXPANSION_TRACKER.md`. |
| `planning/BSBC_PASS6.md` | Exists, but only on `planning/*` — not main, not expand. Read it with `git show`. |

---

## 3. THE SIX-PASS GATE

Defined in `planning/BSBC_PASS6.md` and `books/book-02-the-twelfth-resonant/START_HERE.md`.

```
PLANNED → 1 STRUCTURE → 2 DENSITY → 3 CHARACTER/CLUE → 4 AUDIO
        → 5 STORY COMPLETENESS → 6 BSBC → ATTESTED → AUDIO QC → LOCKED
```

Pass 6 (BSBC) is a craft lens, not imitation of any author. The checklist is in
that file; do not paraphrase it from memory.

**Two gates that bite hardest on this material:**

- *No conflict repeats without changing capability, knowledge, relationship,
  status, strategy or cost.*
- *End-state delta can be stated in one sentence.* A chapter that ends on
  "tomorrow they would begin designing exactly that" has no delta.

**Read the pass count from `START_HERE.md`. Never hardcode it.** It moved from
four to five to six inside a single day. `generate_status.py` reads it and will
flag when two documents disagree.

---

## 4. THE AUDIO PIPELINE

All scripts live in `books/book-01-the-ninth-standard/audio/`.

```
manuscript.md
  → prep_el.py       chunking + normalise.py            → el_chNN.json
  → audit_text.py    MUST report zero READ findings
  → ElevenLabs       voice Holden, ~4000-char chunks
  → assemble_el.py   concat + locked chain              → chNN.holden.mp3
  → manifest.json    + push (Git LFS)
  → curl -sI         must be HTTP 200, bytes must match
```

### LOCKED voice settings — do not change without an explicit instruction

**Single narrator (production):**
- Voice: **Holden**, preset `3c9d6053-6334-592c-8997-4e325286af3f`
- Chain: `highpass=85, -6.5dB@140 Q1.0, -2dB@250 Q1.2, then +0.5 st`
- **Order is EQ → shift.** Not the reverse. See trap #9.

**Full cast (alternative, ch2 only):**

| | Holden | | Maeve `64cf4f1a-…` |
|---|---|---|---|
| Russell | +1.00 | Vale | 0.00 |
| narrator / Kade | +0.50 | Elena | −1.00 |
| Darius | −0.65 | Alvarez | −1.75 |
| Renn | −0.85 | | |

Makeup gain: Holden **+2.0 dB**, Maeve **−1.9 dB**. Turn gap **380 ms**.
Each base voice has its own baseline and its own EQ — see trap #8.

### Why `holden` stays first in `renders[]`

A player taking `renders[0]` must get the production narrator. `cast` is an
alternative presentation, not a replacement. Studio-Q renders for ch2–10 were
withdrawn from the contract entirely (trap #11).

---

## 5. THE TRAP CATALOGUE

Every one of these was found the expensive way. Do not rediscover them.

| # | Trap | What happens |
|---|---|---|
| 1 | `**bold**` reaches the synthesiser | reads "asterisk"; 198 spans in Book 1 |
| 2 | Inline code `` `000` `` not stripped | reads "backtick" |
| 3 | Spoken-zeros rule anchored `^0{3}$` | misses mid-sentence scores |
| 4 | Thousands rule only handles `X,000` | `10,482` goes out as digits |
| 5 | `RANK: a / b` | reads "slash" |
| 6 | **A check that counts only `**`** | reported clean with backticks in the payload |
| 7 | `\b000\b` inside `18,000` | "eighteen, zero zero zero" |
| 8 | One EQ chain for two voices | Holden's bass cut hollows out a female voice |
| 9 | Chain order shift→EQ | notch drifts 4.1 Hz off the shipped narrator |
| 10 | Size check on a downloaded file | a 111-byte S3 `AccessDenied` XML passes it |
| 11 | Rendering from a stale branch | ch8 audio was missing 57% of its chapter |
| 12 | Two prep scripts, divergent rules | the production path had the weaker one |
| 13 | Chapter-word list stopping at "Twenty" | `IndexError` at chapter 21 |
| 14 | `VIII-01` record IDs | reads "vee eye eye eye" — and these are the twelve-slot clue |
| 15 | Inferring a URL timestamp from a batch pattern | right 238 times of 239 |

**The pattern behind half of them:** a check that cannot see the failure it
guards reports a pass, which is worse than no check. When you add a validator,
prove it fails on a known-bad input before trusting it.

**Two standing rules that follow:**
- Validate downloaded audio by **decoding it** (`ffprobe`), never by size.
- Read the **prepared text**, not the manuscript. Every text defect above was
  invisible in the `.md` and obvious in the payload.

---

## 6. OUTSTANDING CONTINUITY BUGS

Small, real, and none of them fixed. All are first-name/surname reuse inside a
small cast.

| Where | Bug | Fix |
|---|---|---|
| B2 ch2 line 103 | `Dr. Amara Park` | Amara is **Sen's** first name; Park is **Lian** Park |
| B2 ch13 / ch14 | `Leela Sen` vs `Leela Nair` | pick **Nair**; `Sen` collides with the Director |
| B2 ch27 | `Dr. Lian Zhou` | collides with Book 1's `Dr. Lian Park` |

---

## 7. DIVISION OF LABOUR

Two agents, two lanes, one shared contract.

**Prose agent** owns the manuscript on `expand/book1-ch01-10`:
- expansion toward architecture targets, six-pass gate, attestations,
  `CLUE_LEDGER.md`, `STATE_LEDGER.md`, `CHAPTER_ATTESTATIONS.md`.

**Audio agent** owns everything under `audio/` and the pipeline scripts:
- prep, audit, render, assemble, manifest, push, verify.

**The handoff rule:** the audio agent renders a chapter **only** after that
chapter is attested and its file hash has been stable for one full loop
iteration. Rendering ahead of the prose guarantees re-rendering. Ch31 changed by
1,290 words forty minutes after being reviewed; had it been rendered first, that
work would have been thrown away.

**Never render chapters 30, 31 or 32 until their expansion is complete.**

---

## 8. THE LOOP

Each iteration:

1. `git fetch origin --prune`
2. `python3 scripts/generate_status.py` — no arguments. Each book defaults
   to its own branch; forcing one ref reports the other book as zero.
3. Act on the highest-priority item (§9).
4. Commit with a message that says what was *learned*, not only what changed.
5. Push. Verify. Record.
6. If three consecutive iterations produce no state change, stop and report.

**Loop-breaking conditions — stop and surface to Toby:**
- Any destructive git operation would be required.
- The same check fails three times with different fixes attempted.
- A decision is needed that changes canon (voice casting, character names,
  what a countdown means, whether a chapter is cut).
- Spend on any single action would exceed $20.

---

## 9. PRIORITY ORDER

Work top-down. Do not skip to audio because it is more satisfying.

1. **Ch32 Consensus → ~5,500 words.** The climax at 35% is the book's single
   biggest defect. Add the *between*: six people each get a beat of what shared
   state feels like from inside their own competence. Currently only Sera and
   Mara get one.
2. **Ch30 Siege → ~5,000.** Establish the island's geography *before* it comes
   apart. Currently the west academic bridge, north shelter and House Sol
   transit arrive as names in dialogue with no spatial anchor.
3. **Ch13, 21, 26 → ~4,500 each.** Promise chapters under 45%.
4. **The deadpan tic.** 360 bare one-word replies across the book (`"Yes."`
   ×196, `"No."` ×164). It is the voice and should survive — but break the run
   at the emotional peaks: ch20, 24, 25, 29, 32. Ch31 has already been repaired
   this way, 10.3 → 1.9 per 1,000 words. Use that as the reference.
5. **Continuity bugs** (§6).
6. **Audio ch8–33**, in order, gated on attestation.

---

## 10. WHAT NOT TO DO

- Do not render Book 2. It is 30/34 drafted and chapters 21–28 are 1,400-word
  skeletons at ~26% of target.
- Do not change locked voice settings.
- Do not "fix" the deadpan replies globally. It is the book's voice.
- Do not merge branches without being asked. `expand/book1-ch01-10` and
  `draft/book-02-four-pass` have diverged deliberately.
- Do not mark a chapter attested to satisfy the dashboard.
- Do not trust `.claude/qa/` screenshots — that harness captures whatever is on
  port 3000, which is a different project.

---

## 11. FILES THAT MATTER

| Path | What |
|---|---|
| `books/book-01-.../audio/normalise.py` | shared text normalisation, both engines |
| `books/book-01-.../audio/prep_el.py` | chunking for ElevenLabs |
| `books/book-01-.../audio/audit_text.py` | the gate — zero READ findings required |
| `books/book-01-.../audio/assemble_el.py` | concat + locked chain |
| `books/book-01-.../audio/cast_split.py` | attribution + cast map (ch2 only) |
| `books/book-01-.../audio/AUDIT.md` | every reading decision and why |
| `scripts/generate_status.py` | derives the dashboard; flags drift and branch divergence |
| `planning/BSBC_PASS6.md` | the pass-6 checklist |
| `audio/manifest.json` | the player contract |

---

## 12. THE ONE-LINE VERSION

Expand the climax, gate every chapter through six passes, render only what is
attested and stable, validate by decoding rather than by size, and read the
prepared text rather than the manuscript.
