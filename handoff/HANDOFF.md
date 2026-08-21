# HANDOFF — READ THIS FIRST

**Updated:** 2026-08-21
**Project:** The Boundary Universe / Asterion Trilogy
**Current phase:** Book 1 rapid working-draft production

## Locked project decisions
- Connected universe name (working): **The Boundary Universe**.
- Flagship trilogy: **Asterion Trilogy**.
- Book 1 working title: **The Ninth Standard**.
- Book 1 target: ~187k words / ~20.1 hours audio.
- Book 1 structure: 33 chapters.
- Narration strategy: one male narrator performing restrained character interpretations.
- GitHub repository is the source of truth; website is a viewer.
- Story remains original; no reuse of another franchise's protected setting/mechanics/characters.
- **Family-clean standard is LOCKED:** no real-world profanity/obscene gestures, no explicit sexual content, age-appropriate romance, intense but non-gratuitously-gory action. Serious themes remain allowed.

## Working prose status
- Chapter 1 — **The Kid in Room Four**: canonical foundation; family-clean editorial pass required before next release build because the original draft contains a few legacy phrases now prohibited by Rule 9.
- Chapter 2 — **Zero Protocol**: working draft complete on rapid-draft branch.
- Chapter 3 — **Asterion**: working draft complete.
- Chapter 4 — **Ten Thousand Four Hundred Eighty-Two**: working draft complete.
- Chapter 5 — **House Meridian**: working draft complete.
- Chapter 6 — **Forty-Seven Seconds**: working draft complete.
- Next chapter: Chapter 7 — **The Suppression Order**.

## Key decisions established in Chapters 2–6
- Kade's mother is **Elena Mercer**, an emergency-department nurse at St. Vincent Medical.
- `000` is a Zero Protocol routing/result code, not an ordinary score.
- Zero Protocol's last valid historical route was roughly three decades earlier.
- Asterion can compel classified evaluation under federal Resonance safety authority.
- Kade arrives at Asterion, wants to stay despite himself, then baselines at **0.00 field output** and rank **10,482/10,482**.
- Kade is assigned to House Meridian and meets Eli Navarro, Mara Vey, Sera Vale, and Taren Holt.
- In his first combat assessment against Priya Shah, Kade loses officially but redirects/relocates impact into the arena wall through an unresolved transfer event. Final six seconds are restricted-review data.

## Audio production system
- Clean manuscript remains the only prose source of truth.
- `books/book-01-the-ninth-standard/audio/README.md` defines the pipeline.
- `audio/PRONUNCIATION.md` holds shared spoken canon.
- `audio/ssml/` documents Google SSML policy.
- `audio/elevenlabs/` documents ElevenLabs performance policy.
- `audio/render_audio.py` generates SSML and ElevenLabs-ready derivatives from the same manuscript file, preventing text drift.
- A/B test at least Chapters 1–3 in Google and ElevenLabs before selecting final production engine.

## Quality automation
- `scripts/family_clean_check.py` is the first-pass profanity/gesture lint. Human family-clean review is still required.
- Before promoting a chapter batch, verify continuity and the clue ledger manually.

## Immediate next writing task
Draft Chapter 7, **The Suppression Order**, followed by Chapter 8 if rapid-draft production continues.

Chapter 7 requirement: Sen orders conservative restrictions on Kade's training after the Forty-Seven Second Fight. Kade receives/overhears an incomplete version and interprets the order as institutional suppression or distrust. The public/campus story should move faster than the truth. End Act I with Kade deciding that if Asterion wants him at the bottom, he will climb anyway.

## Open design decisions
- Final universe/brand name.
- Exact final map/geography of Asterion.
- Aaron's ultimate fate.
- Identity of the second Zero in Book 2.
- Whether Taren survives the trilogy.
- Exact nature of the countdown at Book 1 ending.
- Whether Lieutenant Commander Nia Vale and Sera Vale are related; do not imply a relation until decided.

## Authoring guardrails
Do not rush the academy.
Do not make Kade unbeatable.
Do not use mystery as an excuse for irrational behavior.
Do not over-explain physics during emotional peaks.
Do not let the cosmic story erase the school story.
Keep reveals seeded and check them against the clue ledger.
Prioritize clean family co-reading without flattening the emotional or moral stakes.
