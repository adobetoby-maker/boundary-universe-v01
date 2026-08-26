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
| B1 The Ninth Standard | 33 | 189,799 | main | COMPLETE — Pass 8 copyedit begun | 13/33 published |
| B2 The Twelfth Resonant | 34 | 93,037 | main | Pass 8 expansion in progress (~47% of target) | local proof complete; Holden pending |
| B3 The Final Boundary | 2 | ~5,287 | draft/book-03-six-pass | active six-pass draft | none |
| Contact Zero bk 1 | 24 | 109,135 | main | COMPLETE draft — Pass 8 findings reconciled | none |
| The Quiet Ward | 24 | 95,036 | feature/refuge-node-trilogy | COMPLETE with audio — CANON, review-gated pre-merge | complete |

An editorial review (six independent readers, 2026-08-25) covered every word
of B1, B2, and Contact Zero. Findings drove the punch lists below.

Pass 8 integration on `main` consolidates the reviewed manuscripts that had
previously lived on separate source branches. Source commits: Book 1
`610cd2e`, Book 2 Pass 7/8 `fe4b41d` + `ee04287` (plus audio-proof commit
`8b7a2d6`), and Contact Zero `ae5a2bf`. The per-book
`PASS_08_EXTERNAL_READER_RECONCILIATION.md` files are the audit records.

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

- Manuscript: 33 ch / 189,799 words on main. Density expansion merged
  (58,703 → 189,588), followed by the first Pass 8 copyedit batch. Five
  continuity defects from the editorial review fixed
  (Darius Bell surname, kitchen-fire placement, Open-thread color, Eli's
  96-hour timeline, 128-entrant bracket math) — commit 64a0f50.
- Review verdict: the book sticks the landing. Reveal architecture passed an
  independent fair-play re-audit; ch32's climax repair held; clue-planting
  discipline in ch1–11 was found exceptional.
- **Remaining gates before print-ready:**
  1. Copyedit pass for systemic tics (IN PROGRESS; first batch applied, 40
     regex candidates remain for editorial judgment): "jaw tightened"
     as universal tell, "laughed without humor," "stomach tightened,"
     "He noticed." beat-enders, "There it was." reveal-punctuation, the
     "That was true / Also true" triad, "That sounded almost X" scene-closers.
  2. Surname de-collision decision (Decision 5): three Bells, two Okafors,
     two Parks, two Coles, two Devs, two Chens in one chapter.
  3. Family-clean re-lint post-expansion (CANON_RULES Rule 9) — the recorded
     pass predates the expansion. scripts/family_clean_check.py exists.
  4. Trim pass (optional): ch14/15/16/20 each carry 300–600 words of stacked
     closing beats; ch20's bag-notice beat repeats 5×.
- Audio: 14/33 published (Holden, ElevenLabs; 128 kbps ch1–13, 64 kbps from
  ch14 — ch14 landed at 25.1 MB / 52.3 min, half the old size). Chapters 4–7 were rendered from pre-expansion text and must be
  re-rendered (same condition ch1–3 were in; w/hr vs expanded text proves it).
  Render order interleaves new chapters with those four.

## Book 2 — The Twelfth Resonant — next major writing effort

- 34 ch / 93,037 words after Pass 7 and the first Pass 8 critical-density
  batch, approximately 47% of the 190–205k target.
- Cross-book continuity is CLEAN — review found zero contradictions with
  Book 1; countdown arithmetic reconciles to the day. The Lian Zhou/Park
  "collision" from an earlier session **does not exist** (verified against
  full git history); B2's own sweep already fixed its three real collisions.
- **Expansion pass, in priority order (from the review's triage):**
  EXPAND-CRITICAL: ch27 and ch22 have received their first Pass 8 scene
  expansions; continue/verify ch27 → ch24 → ch21 → ch33 → ch26 → ch22 →
  ch23 → ch17 → ch10.
  Then 19 EXPAND-STANDARD chapters. Six are NEAR-TARGET (1, 2, 3, 5, 18, 20).
- The highest-leverage craft fix is mechanical and findable: the book
  *reports* scenes instead of dramatizing them ("Kade heard about it later").
  Hunting that pattern converts summary to scene exactly where density is
  thinnest.
- Tic pass DONE ahead of expansion (commit c7ae4d6): 7 families reduced
  book-wide. Deliberately done FIRST so the expansion writer reads clean prose
  and does not multiply the patterns 2.5x. The self-aware "Cruel."/"Accurate."
  runner was thinned in its densest stretches (ch23, ch29) rather than
  removed — the text lampshades it, so it is a joke, not only a tic.
- Methodology: Book 1's EXPANSION_TRACKER rules apply (add scenes not filler,
  two jobs per scene, preserve reveal order, family-clean) **plus** B2
  additions per Decision 4. Distrust B2's self-attestation docs — they
  declare "production-lock" at 43% density.
- Punch list (small): ch13 "heated two percent" missing "by". RESOLVED by
  census: B2's Calder IS B1 ch10's Owen Park ("Owen Calder again") — B1
  adopts Calder at pre-print (re-renders ch10/27/28). During expansion,
  resolve two same-person-or-collision questions the census flagged:
  Captain Ortiz (B1) vs Commander Ortiz (B2), Ms. Rook (B1) vs Dean Rook
  (B2) — promotions if same people, renames if not (canon/NAME_REGISTRY.md).

## Book 3 — The Final Boundary — active draft

Two chapters are drafted and attested on `draft/book-03-six-pass`. The draft
remains branch-scoped while it is actively changing. B2's ending (30 days on
the countdown) hard-constrains B3's opening.

## Contact Zero — complete draft, Pass 8 findings reconciled on main

- 24 ch / 109,135 words. Review verdict: unusually disciplined; close to
  ready for density/polish. Prose held up even in the late-burst chapters.
- **Structural surgery (one item):** ch17-19 chronology. ch17 "The Encoding"
  (Day ~1,200) sits before the acceptance it postdates; "Yes" and "Amara
  Again" (both Day 1,190, continuous morning) follow it. Fix per Decision 2:
  rotate to Yes → Amara Again → The Encoding.
- Punch list: ch5 day header FIXED (private Day 32 = absolute Day 1,158;
  commit 643d6eb). ch24 "fourth session" RESOLVED AS NOT A DEFECT — a real
  fourth authorized session exists off-page (ch15 "four coupling sessions...
  in authorized configurations", ch17 "the four authorized sessions"); the
  reviewer's session tally missed it. Pass 8 restored Rhys's closing
  institutional shadow, wrote Yuki into Aaron's true account, planted CZ-15
  in ch22, and reduced the exact "He held this." tic. Eight exact instances
  remain for contextual polish.
- ch24's ending inverts the bible's planned final image (secret TRUE account
  vs public lie-document) — arguably stronger, but confirm intentional.

## The Quiet Ward Trilogy — CANONIZED (Decision 1), renamed (Decision 3)

Complete book (95,041 words) with complete audio on feature/refuge-node-trilogy
(branch name historical). REVIEW GATE PASSED 2026-08-25: avg 8.7/10, finale
rated 10/10; lore-leak sweep fully clean; clue ledger verified verbatim.
Outcomes: D1 timeline drift (eighteen months vs two years) FIXED on branch per
bible (re-render of 7 chapters' audio queued for its production pass); D2
Standards-taxonomy conflict resolved by bible ruling (civilian BM scale is a
distinct system — doc-only); Osei + Vey collisions DEFERRED to docket; ch12
POV exception sanctioned in its bible. Merge when its audio re-render lands.

---

## DECISIONS — made 2026-08-25 (1 and 3 author-ratified; rest editor's selections, standing unless overruled)

1. **DECIDED — CANONIZED (author-ratified).** The Quiet Ward fills the
   Boundary Medicine slot as book 1 of The Quiet Ward Trilogy. Gate: it gets
   the same full editorial review before its branch merges — it was not in
   this review's scope.
2. **DECIDED — ROTATION (revised from swap after seam check).** A straight
   17/18 swap breaks the 18→19 seam: "Amara Again" is a same-morning
   continuation of "Yes" and closes Act II-B. Correct order: Yes → Amara
   Again → The Encoding (old 18, 19, 17). The Yes/Amara adjacency is
   preserved byte-identical. APPLIED: both new seams verified clean (ch20
   itself dates the encoding to Days 1,190-1,197, corroborating the order);
   files rotated, headings renumbered, architecture + ledgers updated —
   commits 6a46222 + f936aac on draft/contact-zero-book1.
3. **DECIDED — RENAMED (author-ratified).** Public series is The Quiet Ward
   Trilogy. "Refuge Node" is banned from all reader-facing copy until the
   Asterion trilogy reveals it; site/data.json scrubbed to zero occurrences.
4. **DECIDED — SECOND CONTACT.** The manuscript already votes this way
   (15-year career, mature Standards from ch1). Resonance Discovery stays 31
   years pre-B1; CZ is Aaron's later contact, ~two decades pre-B1. Bible and
   series map carry the clarification; CZ needs no retcon line.
5. **DECIDED — STAGED RENAMES.** Collisions living only in ch14-33 rename
   now (the ch18 librarian). Collisions with occurrences in ch1-13 are
   recorded in canon/NAME_REGISTRY.md with renames scheduled for the
   pre-print pass, because they invalidate published audio (each triggers a
   re-render, listed per name). Owen Park adopts B2's "Calder" if the census
   confirms same character. Darius Bell keeps his name.
6. **DECIDED — HOLDEN THROUGH THE ASTERION TRILOGY; CZ GETS ITS OWN VOICE.**
   Holden is Kade's interiority and carries B2/B3. Aaron is a different man
   in a different register — audition CZ narrators when its rendering starts.
   Quiet Ward keeps its existing completed audio.
7. **DECIDED — CZ RELEASES BETWEEN B1 AND B2.** CZ is weeks from done
   (surgery applied; polish pass remains); B2's expansion is months. CZ
   deepens Aaron exactly when B1 readers want him, and holds the audience
   while B2 expands. Production order: finish CZ, then B2 expansion.
   Quiet Ward slots after its review gate clears.

---

## Archive index

Historical snapshots — superseded, kept for the record, never cite for
current state: BOOK_ONE_DRAFT_AUDIT.md, FIRST_HALF_AUDIT.md,
FIRST_HALF_POLISH_AUDIT.md, CLAUDE_BSBC_FINAL_REVIEW.md (its Tier-1 repair
list WAS completed — ch30/31/32 hit their floors), CHAPTER_ARCHITECTURE.md
(original outline; "PROVISIONAL 187k" header is pre-expansion),
EXPANSION_TRACKER.md (CLOSED — complete; its 33 rows sum to exactly 189,588
and it is the reconciliation record for how the total was reached).
