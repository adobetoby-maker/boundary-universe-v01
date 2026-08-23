# Foreman ledger — Apple Pencil / iPad PWA block

**Baseline commit:** `f4afc6b`
**Repo:** isolated clone `scratchpad/main-test-copy`, tracks `origin/main`
**Mode:** Full (Agent tool + real shell). Codex not consented.

## THE KEY FINDING — read before writing any code

Most of the handwriting feature **already exists**. Do not rebuild it.

| Capability | Where it already lives |
|---|---|
| Handwriting → character recognition | `src/fns/handwriting-recognize.functions.ts` (Anthropic vision; returns text + reading + meaning) |
| Drawing surfaces | `src/components/kana/HandwritingCanvas.tsx`, `src/components/kana/writing/CharacterCanvas.tsx` |
| **Draw on top of a character** ("work out my understanding") | `src/components/kana/writing/TraceMode.tsx` |
| Stroke scoring | `src/components/kana/writing/scoring.ts` |
| Pen-pal writing mode | `src/components/kana/writing/PenPalMode.tsx` |
| Reachable already | `kana` + `characters` tabs in `tab-registry.ts` |

## Founder's design intent (2026-08-16)

Wants BOTH modes, with recognition as an explicit act, never a guess:
- Default: **ink stays ink** (annotate / work out understanding).
- Convert to a character on demand — hold-to-convert, or a "script writer" toggle.
- **Draw on top of an existing character** to deconstruct it. This mode must never
  auto-recognise; it is pure ink over a rendered glyph.
- Target device: **iPad + Apple Pencil, installed as a PWA.**

## Tasks

| # | Task | Seat | Write set | Status |
|---|---|---|---|---|
| P1 | Make existing canvases Apple Pencil–native | WORKHORSE | `kana/HandwritingCanvas.tsx`, `kana/writing/CharacterCanvas.tsx` | **DONE** (efa7df6) |
| P2 | SEPARATE Chinese recognition prompt (no overlap with Japanese) | WORKHORSE | `fns/handwriting-recognize.functions.ts`, `kana/HandwritingCanvas.tsx` | **DONE** (eaae5a6) |
| P3 | iPad layout — stop inheriting the desktop `lg` layout | FRONTIER | `styles.css`, `TopNav.tsx`, `AppSidebar.tsx`, `tutor/TutorPanel.tsx` | **DONE** (9e36a5e) |
| P4 | Wire trace / convert into the notes surfaces | WORKHORSE | `notes/*`, `dashboard/NotesCard.tsx`, `reader/NotesPanel.tsx` | **DONE** (f7d2aa8) |

## Why P1 is first

Zero hits for `pointerType`, `pressure`, `getCoalescedEvents` or `touch-action` in the
canvases. So today: no palm rejection (a resting hand draws), no pressure variation, and
strokes coarser than the Pencil actually reports. This is the gap the founder feels first.

## P2 — FOUNDER DIRECTIVE (2026-08-16)

"We will need a separate hard coded prompt for Chinese. That way they do not overlap.
Learning is hard enough let alone when you are given the wrong thing."

Two SEPARATE prompt constants and tool schemas — NOT one parameterised prompt. The
duplication is deliberate; do not "clean it up" later. `language` is required with **no
default**, because a default lets a missed call site silently get Japanese treatment —
the exact failure being designed out. A confidently-wrong reading taught to a learner is
worse than a failed lookup.

First P2 attempt was BLOCKED by a full disk (ENOSPC) and made zero changes. Re-dispatched.

## P2 note — recognition is hardcoded Japanese

`handwriting-recognize.functions.ts:28,43,51,57` all say "Japanese". Chinese hanzi would
come back read as kanji with Japanese readings — confidently wrong, which is worse than
failing. **Pashto is a separate problem**: cursive Arabic, letters change shape by
position; do NOT bolt it onto the CJK recogniser. Surface as its own decision.

## Standing constraints (carried forward — all learned the hard way)

- `npx tsc --noEmit` 0 errors; `npm run lint` 0 errors.
- Local `ANTHROPIC_API_KEY` is **invalid** → AI server fns 401 locally. Verify render
  paths by seeding the component's own localStorage cache. Do not chase the 401.
- Chrome cannot reproduce the iOS path. Playwright **webkit** is installed — use it.
- **Never override native `<ruby>` layout.** WebKit fails `@supports (display:ruby)` but
  renders `<ruby>` correctly; overriding it drops the base off the baseline (fixed 31de475).
  WebKit also ignores `position:absolute` on `<rt>` and clamps `<ruby>` to `display:inline`.
- Any persist effect **must skip its first invocation**, or it writes default state over
  hydrated state. Bug fixed three times now (furigana, romaja, recentWords).
- Safe-area: use `--lt-safe-top`, not raw `env()`.
- The QA screenshot harness captures an unrelated project ("you & I"). Do NOT score
  against it and do NOT fabricate a visual verdict from it.

## Attempts (append-only)

- P1 dispatched. → DONE, verified independently (tsc/build re-run by foreman).
  **Caught a bug in the ticket instruction itself:** `getCoalescedEvents?.() ?? [native]`
  is wrong on WebKit — the method EXISTS and returns an EMPTY ARRAY, so `??` never fires
  and the draw loop ran zero times (no line drawn on move). Fixed to test `length`.
  Surfaced only by driving real PointerEvents and reading canvas pixels.
  Verified: pen draws; touch-after-pen ignored; touch-only still draws; pressure changes
  coverage; the 0.5 default is guarded. NOT verified: no physical iPad/Pencil; dpr math
  only ran at dpr=1.
- P2 DONE (eaae5a6), verified by foreman: no interpolation between the two prompt sets,
  `language` is z.enum with no default, UI + zod both refuse unsupported languages.
  UNVERIFIED: live recognition accuracy either language (local API key invalid). First
  real test should be a character in BOTH scripts (車 / 花) — Chinese must return pinyin.
- P3 DONE (9e36a5e). Approach: @custom-variant desktop = (hover:hover)+(pointer:fine)+1024px.
  iPad with Apple Pencil reports hover:none (primary input is touch), so it never matches
  and always gets the mobile layout regardless of viewport width. 4 files changed:
  styles.css (variant def + 2 media query updates), TopNav, AppSidebar (3 sites), TutorPanel.
  tsc: 0 errors. Build: clean. UNVERIFIED: real iPad (Playwright webkit cannot simulate
  touch-primary pointer capability; must test on physical device).
- P4 DONE (f7d2aa8). Draw-to-convert wired into all three note entry surfaces (NotesCard add form,
  NoteRow edit, NoteCard in NotesPanel). MultilingualNoteInput replaces bare <textarea> everywhere.
  onKeyDown passthrough prop added to MultilingualNoteInput (fires after composition guard).
  autoFocus replaces taRef+useEffect in NoteCard. tsc: 0 errors. Build: clean.
  UNVERIFIED: actual draw→recognize flow on physical iPad (local API key invalid; 401 on recognizeHandwriting).
- "finish draw" DONE (9ac0982). insertLabel="Insert →" passed to all three HandwritingCanvas usages
  in notes surfaces. When insertLabel is set, the result card shows "Insert →" and auto-clears the
  canvas after insert so the user can draw the next character immediately. Kana-tab usage unchanged
  (no insertLabel = original "Use in Converter →" + converter toast). tsc: 0 errors. Build: clean.
  Pushed to origin/main. All P1–P4 commits + draw finish now live on main.
  UNVERIFIED: recognition result auto-clear on physical iPad (local API key invalid).
- (superseded) P2 (recognition beyond Japanese) is the highest-value remaining ticket, and it
  carries a founder decision on Pashto — do not let a worker bolt Arabic script onto the
  CJK recogniser.

---

# THE QUIET WARD — Book 1 of the Refuge Node Trilogy

**Baseline commit:** `e01113c`
**Branch:** `feature/refuge-node-trilogy`
**Repo:** `/Users/drive/boundary-universe-v01`
**Mode:** Full (Agent tool + real shell). Codex not consented.
**LEAD seat:** Sonnet 4.6 (mid-tier — prose workers routed to fable/frontier)
**Mandate:** No human gates until audio complete.

## Build overview

24 chapters × ~4,000 words = ~100,000 words prose
Audio: Google Cloud TTS Studio-Q via existing pipeline (gcloud ADC token confirmed live)

## Chapter dispatch table (append-only)

| Ch | Title | Seat | Target words | Status | Commit |
|---|---|---|---|---|---|
| 01 | The Transfer | FRONTIER | 3,800 | DONE (3,791w) | e01113c |
| 02 | Room Four | FRONTIER | 3,600 | DONE (3,617w) | — |
| 03 | Calibrated | FRONTIER | 3,500 | DONE (3,699w) | — |
| 04 | Differential | FRONTIER | 3,900 | DONE (3,870w) | — |
| 05 | History | FRONTIER | 4,200 | DONE (4,288w) | — |
| 06 | The Shape | FRONTIER | 3,700 | DONE (3,774w) | — |
| 07 | Standard Consult | FRONTIER | 4,100 | DONE (4,296w) | — |
| 08 | Ruan's Good Day | FRONTIER | 3,800 | DONE (4,003w) | — |
| 09 | Records Request | FRONTIER | 3,600 | DONE (3,803w) | — |
| 10 | The License | FRONTIER | 3,900 | DONE (4,081w) | — |
| 11 | Field Mechanics | FRONTIER | 4,300 | DONE (4,186w) | — |
| 12 | Fenn | FRONTIER | 3,500 | DONE (3,703w) | — |
| 13 | The Shape, Continued | FRONTIER | 4,000 | DONE (3,838w) | — |
| 14 | Something Else | FRONTIER | 3,700 | DONE (3,823w) | — |
| 15 | Military Authority | FRONTIER | 4,200 | DONE (4,313w) | — |
| 16 | The Name | FRONTIER | 3,600 | DONE (3,521w) | — |
| 17 | Colm's Question | FRONTIER | 3,800 | DONE (3,699w) | — |
| 18 | Off the Record, Again | FRONTIER | 4,000 | DONE (4,193w) | — |
| 19 | The File | FRONTIER | 3,900 | DONE (4,095w) | — |
| 20 | The Liaison | FRONTIER | 4,300 | DONE (4,407w) | — |
| 21 | After the Liaison | FRONTIER | 3,700 | DONE (3,659w) | — |
| 05 | History | FRONTIER | 4,200 | PENDING | — |
| 06 | The Shape | FRONTIER | 3,700 | PENDING | — |
| 07 | Standard Consult | FRONTIER | 4,100 | PENDING | — |
| 08 | Ruan's Good Day | FRONTIER | 3,800 | PENDING | — |
| 09 | Records Request | FRONTIER | 3,600 | PENDING | — |
| 10 | The License | FRONTIER | 3,900 | PENDING | — |
| 11 | Field Mechanics | FRONTIER | 4,300 | PENDING | — |
| 12 | Fenn | FRONTIER | 3,500 | PENDING | — |
| 13 | The Shape, Continued | FRONTIER | 4,000 | PENDING | — |
| 14 | Something Else | FRONTIER | 3,700 | PENDING | — |
| 15 | Military Authority | FRONTIER | 4,200 | PENDING | — |
| 16 | The Name | FRONTIER | 3,600 | PENDING | — |
| 17 | Colm's Question | FRONTIER | 3,800 | PENDING | — |
| 18 | Off the Record, Again | FRONTIER | 4,000 | PENDING | — |
| 19 | The File | FRONTIER | 3,900 | PENDING | — |
| 20 | The Liaison | FRONTIER | 4,300 | PENDING | — |
| 21 | After the Liaison | FRONTIER | 3,700 | PENDING | — |
| 22 | Absence | FRONTIER | 3,800 | DONE (3,985w) | — |
| 23 | Still Here | FRONTIER | 3,900 | DONE (3,837w) | — |
| 24 | Beginning | FRONTIER | 4,400 | DONE (4,560w) | — |

## Standing constraints

- The words "Refuge Node" do not appear anywhere in the manuscript
- No Kade Mercer in any chapter
- Boundary Medicine = extension of Nine Standards, not new capabilities
- Update STATE_LEDGER.md after every canonical chapter
- Update CLUE_LEDGER.md when a clue is planted

## Attempts (append-only)

- Ch 01 dispatched to frontier worker. Returned 3,791 words. STATE_LEDGER updated. Canonical. DONE.
- Ch 02 returned DONE (3,617w). Both clues planted canonical. STATE_LEDGER + CLUE_LEDGER updated by foreman.
- Ch 03 returned DONE (3,699w). Final line: "carrying the nothing that was not zero, and holding it still." STATE_LEDGER updated by foreman.
- Ch 04 returned DONE (3,870w). Final line echoes Ch 3 register: "carrying the smaller country with her, and holding it still." STATE_LEDGER updated.
- Ch 05 returned DONE (4,288w). Key clue planted verbatim: "Like something very old was trying to be careful with me." Forty-one seconds canonical. STATE_LEDGER + CLUE_LEDGER updated.
- Ch 06 returned DONE (3,774w). ACT I COMPLETE. Field journal clue planted; shape description canonical. STATE_LEDGER + CLUE_LEDGER updated.
- Ch 07 returned DONE (4,296w). Military-closure clue layer 1 planted verbatim. Shape growing: "It's not finished" canonical. STATE_LEDGER + CLUE_LEDGER updated.
- Ch 08 returned DONE (4,003w). "You will" clue + forty-one seconds line planted. Third journal acquisition canonical. STATE_LEDGER + CLUE_LEDGER updated.
- Ch 09 returned DONE (3,803w). GMA letter canonical: reference GMA-BM-2025-0441, letterhead Government Medical Authority / Boundary Medicine Division. New fact: Ruan signed releases at Carrow Bay including clause about medical records; safety review conducted by platform contractor + government safety office. STATE_LEDGER updated.
- Ch 10 returned DONE (4,081w). Platform MO phrase "Field-state incompatible with equipment operation" canonical. Direction-of-causation distinction (instruments can't read him vs. his state affects equipment) established in closing beat. STATE_LEDGER updated.
- Ch 11 returned DONE (4,186w). Null/zero first payoff delivered: "Not a measurement of absence. The absence of a measurement." in private notes (not chart). Ruan's evaluation revelation canonical: "I never had the evaluation. I've wondered, since." Closing note verbatim confirmed. Worker correctly caught ticket error on borrowed-instrument count; followed ledger. CLUE_LEDGER + STATE_LEDGER updated.
- Ch 12 returned DONE (3,703w). Ruan's "She's going to be fine" and Fenn's exchange canonical. Sable's "That's usually a sign something real is happening" canonical. Close third maintained. STATE_LEDGER updated.
- Ch 13 returned DONE (3,838w). Field journal first payoff delivered: "It's not growing. I'm getting access to more of it. It was always this large." Perceptual-event note canonical. "I was glad you could see any" canonical. "frequency" = 0 confirmed. STATE_LEDGER + CLUE_LEDGER updated. Manuscript halfway: 50,949 words / 13 chapters.
- Ch 14 returned DONE (3,823w). Two clue payoffs delivered: "You will" (Ruan's hope, not prediction, canonical); "something large being careful" second layering (word: "careful" arrived afterward). Passive Standard Six perception, clinical register, non-mystical. "I meant it as a hope, not a prediction." verbatim confirmed. CLUE_LEDGER + STATE_LEDGER updated. Running total: 54,772 words / 14 chapters.
- Ch 15 returned DONE (4,313w). BM-null designation Layer 2 planted verbatim. Index entry present: "Classification for field states that exceed the characterization parameters of all certified Boundary Medicine diagnostic modalities." Suffix codes BM-null-1 and BM-null-2 confirmed. BM-null-3 in notebook only (Sable's prediction, not a public code). Ruan's "I thought there might be something like that" canonical. Final line: "BM-null" spoken by Ruan like a name he'd needed for two years. CLUE_LEDGER + STATE_LEDGER updated. Running total: 59,085 words / 15 chapters. Worker noted CHAPTER_ARCHITECTURE discrepancy (public BM-null-3) — ticket was correct, not the architecture sketch.
- Ch 16 returned DONE (3,521w). Listening-station clue planted verbatim: "That's what they told us" appears twice. Qualifier confirmed: Ruan gave honest account, Sable wrote "told it was" not "it was." Two maintenance crew members planted (same transit, medically separated, no contact since) — seed for Ch 24 rotation-companions payoff. "That's the right distinction" canonical. Final line: notebook holds things "exactly as heavy as they had been found, no heavier, until the day they were needed at their true weight." CLUE_LEDGER + STATE_LEDGER updated. Running total: 62,606 words / 16 chapters.
- Ch 17 returned DONE (3,699w). No clue planted (institutional chapter). All six beats confirmed. Worker caught canonical fact: Colm is female (she/her) per Ch 1 — ticket used "he" in error, worker followed manuscript canon correctly. Canonical exchanges: "I've seen this pattern before" (Colm, no elaboration); "I have a specific investigation still pending" (Sable, no name given); "Any movement on Four?" / "extension request" (Fenn); temperature-reading exchange (Ruan, final scene). STATE_LEDGER updated; Colm's pronouns and "does not know" corrected. Running total: 66,305 words / 17 chapters.
- Ch 18 returned DONE (4,193w). No clue planted (acquisition chapter). All six beats confirmed. Worker correctly caught "July" continuity error (admission is August, Ch 7 = Day 8) and rendered as "the first time" — preserving intent. "Be careful" canonical (matches Ch 7). Orlan's pattern ("both cases closed at point of beginning to understand") present, flat delivery, self-qualified as two-data-point pattern. Private note verbatim confirmed. Running total: 70,498 words / 18 chapters.
- Ch 19 returned DONE (4,095w). BM-null Layer 3 DELIVERED: index updated to three suffix codes (BM-null-1, BM-null-2, BM-null-3). Private note verbatim confirmed. Both timing possibilities (causal/coincidental) held equally. Ruan's "how much of it I can hold at once" canonical. She continues working. CLUE_LEDGER + STATE_LEDGER updated. Running total: 74,593 words / 19 chapters.
- Ch 20 returned DONE (4,407w). No clue planted (institutional chapter). All six beats confirmed. Lenne established: professional, unhurried, confirms BM-null-3 by non-contradiction, does not discuss prior cases, not authorized to recommend transfer. "Clinical care remains your responsibility" and "not authorized to recommend clinical disposition" both canonical. Ruan exchange ("does he seem to know" / "knows exactly") canonical. Orlan's pattern held unresolved. STATE_LEDGER updated with Lenne character section. Running total: 78,995 words / 20 chapters.
- Ch 21 returned DONE (3,659w). Liaison's field frequency clue PLANTED verbatim: "The same way you could feel me. But different frequency. Older. More practiced." Private notebook entry verbatim confirmed: "the null is not a null of field presence. It is a null of instrument access. The instruments do not see him. He sees everything." Ruan's perception of Sable's field state ("attended") reached independently without Standard Six vocabulary — confirmed consistent with classification. Ruan's field perception reported as consistent since incident, clearer post-incident. Lenne classification held in Sable's private notes only, not named to Ruan or chart. "frequency" appears 4× at lines 53/81/85/111 — all Lenne field context, never linked to shape. Colm she/her, Lenne he/him. Zero "Refuge Node" / "Kade Mercer" hits. CLUE_LEDGER + STATE_LEDGER updated. Running total: 82,654 words / 21 chapters.
- Ch 22 returned DONE (3,985w). Chart-disappears clue PLANTED. Electronic record administratively transferred to restricted GMA tier (code: GMA-RA-2026-1187, 11:23 PM Day 30); paper chart intact; Osei processes paper orders; Sable does not tell Ruan; takes chart home in bag without ceremony. Both canonical private notes verbatim confirmed. "Frequency": 0 hits (excellent). "Held" used as GMA letter's own verb (callback). Sequence held without causation (Lenne left morning Day 30, transfer 12h later). "Deletion" corrected to "transfer" mid-thought in prose per ticket direction. CLUE_LEDGER + STATE_LEDGER updated. Running total: 86,639 words / 22 chapters.
- Ch 23 returned DONE (3,837w). Chart-payoff delivered: paper record is the only documentation, Ruan administratively invisible but clinically present. Canonical exchange ("You haven't found the edge of it yet" / "Neither have I") verbatim confirmed. "Part that isn't a shape" planted for Ch 24. "Still here" / "Yes" exchange confirmed. Night logs gap noted. Chart taken home again. Zero "frequency" / "Refuge Node" / "Kade Mercer". STATE_LEDGER updated. Running total: 90,476 words / 23 chapters.
- Ch 24 returned DONE (4,560w). MANUSCRIPT COMPLETE. Three payoffs delivered: (1) Frequency reveal — CANONICAL VERBATIM: "What I've been drawing in the journal is not a shape. I've known that since about day ten, and I didn't know how to say it without sounding — I wasn't sure what it would be to you, medically. What I've been drawing is a frequency." (2) Rotation companions — Maren Veld (BM-null-1?) and Soto Parris (BM-null-2?) named; "I've thought about that a great deal." canonical. (3) Full account of forty-one seconds — perception given, quality of care described, Ch 2 consistency preserved ("I don't know what it was"). Six-line final exchange verbatim confirmed. Private note verbatim confirmed. Door open a hand's width confirmed. Final line ends on ward's night sound, sixth channel, frequency transcribed. Zero "Refuge Node" / "Kade Mercer". "frequency" appears connected to shape for the first and only time. CLUE_LEDGER + STATE_LEDGER updated. Running total: 95,036 words / 24 chapters. PROSE COMPLETE. PROCEEDING TO AUDIO.
