# BOOK 2 AUDIO

## Production status

The Book 1 production voice remains ElevenLabs **Holden** with the locked EQ/pitch chain. This folder does not redefine that production voice.

`render_local_audiobook.py` creates a complete, chaptered **local proof/listening copy** using the installed macOS Reed English (US) voice. It exists so the final manuscript can receive an end-to-end audio proof without sending proprietary text to another network service or requiring unavailable cloud credentials.

## Render

```bash
python3 books/book-02-the-twelfth-resonant/audio/render_local_audiobook.py \
  --output /path/to/The-Twelfth-Resonant.local-reed.m4b
```

Defaults:
- voice: `Reed (English (US))`;
- rate: 180 words per minute;
- output: mono AAC at 64 kbps inside a chaptered M4B;
- gain: −2.5 dB at the lossless-to-AAC stage for audiobook-safe headroom;
- source: all 34 canonical manuscript Markdown files in numeric order;
- privacy: local synthesis only; no manuscript text leaves the machine.

The preparation layer strips Markdown, converts full countdown readouts into days/hours/minutes/seconds, resolves Roman Standard labels and key technical abbreviations, applies the canonical pronunciation aliases, and converts the manuscript's paragraph/scene rhythm into explicit silence cues.

## Boundary

The rendered M4B is intentionally not committed to this branch. The branch does not contain the repository's later Git LFS audio infrastructure, and committing a full audiobook as an ordinary Git blob would permanently bloat repository history. The reproducible renderer and checksum audit are committed; the user-facing media file is delivered separately.
