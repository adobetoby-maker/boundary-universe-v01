# PUBLICATION ROADMAP — Boundary Universe

Single source of truth for series state and sequencing. Supersedes the status
claims in HANDOFF.md and the archived audit snapshots (see Archive Index).
Numbers below were measured from the manuscripts on 2026-08-25, not copied
from older docs. When this file and an older doc disagree, this file wins;
when this file and the manuscripts disagree, the manuscripts win — fix this
file.

---

## Universe status snapshot (measured 2026-08-25)

| Work | Chapters | Words | Branch | State | Audio |
|---|---|---|---|---|---|
| B1 The Ninth Standard | 33 | 189,588 | main | COMPLETE — expanded, reviewed, continuity-fixed | 13/33 published |
| B2 The Twelfth Resonant | 34 | 87,680 | draft/book-02-four-pass | COMPLETE at treatment density (43% of target) | none |
| B3 The Final Boundary | 1 file | — | draft/book-03-six-pass | not started | none |
| Contact Zero bk 1 | 24 | 108,754 | draft/contact-zero-book1 | COMPLETE draft, pre-polish | none |
| The Quiet Ward (Refuge Node) | 24 | 95,036 | feature/refuge-node-trilogy | COMPLETE with full audio — **uncanonized** | complete |

An editorial review (six independent readers, 2026-08-25) covered every word
of B1, B2, and Contact Zero. Findings drove the punch lists below.

---

## Canon hierarchy

1. **Law** — CANON_RULES.md and the LOCKED sections of canon/UNIVERSE_BIBLE.md.
2. **Living trackers** — per-book STATE_LEDGER.md, CLUE_LEDGER.md,
   RULE_6_REVEAL_AUDIT.md. Updated as text changes.
3. **This roadmap** — sequencing and status. Not a lore source.
4. **Historical artifacts** — everything in the Archive Index. Never cite them
   for current state.

site/data.json is a *viewer* of this hierarchy, never a source. It invented a
series (see Decision 3) because nothing enforced that.

---

## Book 1 — The Ninth Standard — COMPLETE, in audio production

- Manuscript: 33 ch / 189,588 words on main. Density expansion merged
  (58,703 → 189,588). Five continuity defects from the editorial review fixed
  (Darius Bell surname, kitchen-fire placement, Open-thread color, Eli's
  96-hour timeline, 128-entrant bracket math) — commit 64a0f50.
- Review verdict: the book sticks the landing. Reveal architecture passed an
  independent fair-play re-audit; ch32's climax repair held; clue-planting
  discipline in ch1–11 was found exceptional.
- **Remaining gates before print-ready:**
  1. Copyedit pass for systemic tics (one ticket, whole book): "jaw tightened"
     as universal tell, "laughed without humor," "stomach tightened,"
     "He noticed." beat-enders, "There it was." reveal-punctuation, the
     "That was true / Also true" triad, "That sounded almost X" scene-closers.
  2. Surname de-collision decision (Decision 5): three Bells, two Okafors,
     two Parks, two Coles, two Devs, two Chens in one chapter.
  3. Family-clean re-lint post-expansion (CANON_RULES Rule 9) — the recorded
     pass predates the expansion. scripts/family_clean_check.py exists.
  4. Trim pass (optional): ch14/15/16/20 each carry 300–600 words of stacked
     closing beats; ch20's bag-notice beat repeats 5×.
- Audio: 13/33 published (Holden, ElevenLabs; 128 kbps ch1–13, 64 kbps from
  ch14). Chapters 4–7 were rendered from pre-expansion text and must be
  re-rendered (same condition ch1–3 were in; w/hr vs expanded text proves it).
  Render order interleaves new chapters with those four.

## Book 2 — The Twelfth Resonant — next major writing effort

- 34 ch / 87,680 words, treatment density, 43% of the 190–205k target.
- Cross-book continuity is CLEAN — review found zero contradictions with
  Book 1; countdown arithmetic reconciles to the day. The Lian Zhou/Park
  "collision" from an earlier session **does not exist** (verified against
  full git history); B2's own sweep already fixed its three real collisions.
- **Expansion pass, in priority order (from the review's triage):**
  EXPAND-CRITICAL: ch27 (21% density, Zhou intro + Rule-6 payoff as pure
  exposition) → ch24 → ch21 → ch33 → ch26 → ch22 → ch23 → ch17 → ch10.
  Then 19 EXPAND-STANDARD chapters. Six are NEAR-TARGET (1, 2, 3, 5, 18, 20).
- The highest-leverage craft fix is mechanical and findable: the book
  *reports* scenes instead of dramatizing them ("Kade heard about it later").
  Hunting that pattern converts summary to scene exactly where density is
  thinnest.
- Methodology: Book 1's EXPANSION_TRACKER rules apply (add scenes not filler,
  two jobs per scene, preserve reveal order, family-clean) **plus** B2
  additions per Decision 4. Distrust B2's self-attestation docs — they
  declare "production-lock" at 43% density.
- Punch list (small): ch13 "heated two percent" missing "by"; verify B2's
  "Owen Park→Calder" rename doesn't contradict B1 ch10's Owen Park (same
  student or different?).

## Book 3 — The Final Boundary — not started

One manuscript file exists. Not a scheduling item until B2 expansion is done.
B2's ending (30 days on the countdown) hard-constrains B3's opening.

## Contact Zero — complete draft, needs one structural fix

- 24 ch / 108,754 words. Review verdict: unusually disciplined; close to
  ready for density/polish. Prose held up even in the late-burst chapters.
- **Structural surgery (one item):** ch17/18 chronological inversion — ch17
  shows Aaron nine days *after* the acceptance that ch18 then narrates as
  live scene. Swap them or give ch17 an explicit temporal marker. (Decision 2
  covers which.)
- Punch list: ch24 "fourth session" reference (no fourth session exists —
  correct target depends on whether Aaron counts unauthorized sessions);
  ch5 "Day 32" header breaks the absolute-day convention; Rhys vanishes for
  ch19–24 (bible's own checklist calls for a closing beat); planned Yuki
  gut-punch beat from BOOK_BIBLE never written; CLUE_LEDGER CZ-15 planted in
  ledger but absent from ch22; "He held this." tic (15+ verbatim uses).
- ch24's ending inverts the bible's planned final image (secret TRUE account
  vs public lie-document) — arguably stronger, but confirm intentional.

## The Quiet Ward / Refuge Node Trilogy — awaiting canonization decision

Complete book (95,036 words) with complete audio, on an unmerged branch,
absent from every canon doc, publicly named after a LOCKED-lore secret.
Blocked entirely on Decisions 1 and 3.

---

## DECISIONS NEEDED (author calls — nothing below proceeds without them)

1. **Canonize The Quiet Ward?** Merge + add to FUTURE_SERIES_MAP (it fills
   the "Boundary Medicine" slot), rename, or shelve.
2. **Contact Zero ch17/18:** swap chapters, or add a temporal marker to ch17.
3. **The "Refuge Node Trilogy" public name** leaks the Asterion endgame:
   UNIVERSE_BIBLE defines the Refuge Node as the concealed entity, and the
   site copy even lists book 3 as "Refuge Node named." Recommend renaming the
   public series (The Quiet Ward already carries the better title) and
   keeping "Refuge Node" out of all reader-facing copy until B3.
4. **Contact Zero's timeline slot:** the bible puts the Resonance Discovery
   31 years before B1; Aaron's containment is ~17 years before B1; CZ gives
   Aaron a 15-year prior career using mature Standards infrastructure. This
   reconciles ONLY if CZ's event is a *second* contact, not the Discovery —
   but the series docs frame CZ as the origin. One line must change: either
   the bible's framing of what CZ is, or CZ gets a retcon line. Decide which.
5. **Surname policy:** rename B1's colliding minor characters (worst: three
   Bells in a House whose symbol is a bell) or accept as texture. If renaming,
   do it before ch14+ audio renders bake the names in. Create a NAME_REGISTRY
   in canon/ either way — both books minted duplicate names because none
   existed.
6. **Book 2 audio voice:** Holden is Kade's book. B2 is still Kade POV
   (Holden carries), but Contact Zero is Aaron POV — same voice aged, or a
   new voice? Decide before any CZ rendering.
7. **Release order:** B2 → CZ or CZ → B2? CZ is closer to done; B2 continues
   the momentum. (Quiet Ward could slot anywhere once Decision 1 lands.)

---

## Archive index

Historical snapshots — superseded, kept for the record, never cite for
current state: BOOK_ONE_DRAFT_AUDIT.md, FIRST_HALF_AUDIT.md,
FIRST_HALF_POLISH_AUDIT.md, CLAUDE_BSBC_FINAL_REVIEW.md (its Tier-1 repair
list WAS completed — ch30/31/32 hit their floors), CHAPTER_ARCHITECTURE.md
(original outline; "PROVISIONAL 187k" header is pre-expansion),
EXPANSION_TRACKER.md (CLOSED — complete; its 33 rows sum to exactly 189,588
and it is the reconciliation record for how the total was reached).
