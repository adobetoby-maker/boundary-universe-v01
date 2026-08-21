# BOOK 1 AUDIO PIPELINE

The manuscript remains clean prose. Audio markup is derived from it and never becomes story canon.

## Layers

- `../manuscript/` — canonical novel prose only.
- `ssml/` — Google-style SSML production scripts.
- `elevenlabs/` — ElevenLabs performance scripts with sparse natural-language/audio cues.
- `PRONUNCIATION.md` — canonical spoken-name and terminology guidance.

## Single-narrator philosophy

One primary narrator performs every character through cadence, placement, attitude and restrained vocal differentiation. Do not turn the book into a radio drama. Avoid extreme pitch changes, caricature accents or excessive sound effects.

## Production comparison

For each test chapter, render the same final manuscript through:
1. Google TTS/SSML — deterministic pacing and pronunciation control.
2. ElevenLabs long-form narration — natural performance and emotional continuity.

Evaluate blind when possible on:
- listener fatigue after 30–60 minutes
- intelligibility at normal playback speed
- character differentiation
- emotional authenticity
- consistency of names/terms
- regeneration/editing friction

## Markup discipline

Use fewer cues than instinct suggests. If punctuation and prose already create the performance, do not add a tag.

Never change story wording solely to compensate for a weak synthetic voice until at least two engines have been tested.
