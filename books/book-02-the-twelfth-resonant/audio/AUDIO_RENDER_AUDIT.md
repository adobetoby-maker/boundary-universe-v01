# BOOK 2 — LOCAL AUDIO RENDER AUDIT

**Status:** COMPLETE / VALIDATED  
**Rendered:** 2026-08-23  
**Manuscript source commit:** `9aa1f79c4a3dddc6328a2da73f7cc96ef08e6380`  
**Source branch:** `draft/book-02-four-pass`

## Artifact

- **Filename:** `The-Twelfth-Resonant.local-reed.m4b`
- **Purpose:** complete local proof/listening copy, not the final Holden commercial-production render
- **Voice:** macOS `Reed (English (US))`
- **Rate:** 180 words per minute
- **Privacy:** local synthesis; no manuscript text sent to a network service
- **Duration:** 37,455.843628 seconds — 10:24:15.84
- **Size:** 310,748,313 bytes — 296 MiB displayed
- **SHA-256:** `92d181157b946aaeaa4a003d7fc1282c93e9674c1b23f531e867a55338b5a1b9`

## Media validation

- Container: chaptered M4B / MP4
- Audio: AAC-LC
- Sample rate: 44,100 Hz
- Channels: mono
- Audio bitrate: 64,990 bps
- Embedded chapter markers: 34
- First marker: `Chapter 1 — The Countdown`
- Final marker: `Chapter 34 — Twelve`
- Full decode: PASS; no invalid-frame or decode errors
- Mean volume: −19.3 dB
- Maximum sample peak: −3.0 dB

The −2.5 dB render-stage gain was selected after the first proof pass measured −16.8 dB mean / −0.7 dB peak. The final pass was regenerated from the lossless `say` output so the level correction did not require a second lossy transcode.

## Prepared-text validation

- Canonical chapter files found: 34
- Prepared chapter payloads produced: 34
- Raw Markdown heading/bold/code/link hits: 0
- Raw five-field countdown hits: 0
- Retired audio-collision name hits: 0
- Unknown embedded speech commands: 0

Full countdown displays are spoken as days, hours, minutes and seconds. `Standard IX`, M-Null, R-3 and the canonical academy/character pronunciation aliases are normalized only in the audio derivative; the manuscript remains unchanged.

## Storage decision

The M4B is delivered outside Git. This branch does not contain the repository's later Git LFS audio infrastructure, and committing a 296 MiB audiobook as an ordinary blob would permanently bloat repository history. The reproducible renderer, pronunciation file and this checksum/provenance audit are committed instead.

## Remaining distinction

This artifact completes the requested rendered listening copy. It does not supersede the locked Book 1 production voice decision: a commercial Book 2 render should still use ElevenLabs Holden with the established EQ/pitch chain when credentials, budget and appropriate media storage are available.
