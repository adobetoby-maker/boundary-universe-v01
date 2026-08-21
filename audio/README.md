# AUDIO LIBRARY

Rendered narration, and the manifest a player reads.

`manifest.json` is the contract. A player should never crawl this directory —
it reads the manifest, gets chapter order, titles, durations and file paths, and
never needs to know how any of it was made.

```
audio/
  manifest.json                       ← the only file a player parses
  book-01-the-ninth-standard/
    ch01-the-kid-in-room-four.studio-q.mp3
    ch01-the-kid-in-room-four.elevenlabs.mp3
```

Production lives elsewhere: `books/book-01-the-ninth-standard/audio/` holds the
SSML, the voice chain and the render scripts. **How it is made** and **what was
made** stay separate.

## Naming

```
ch<NN>-<slug>.<render>.mp3
```

`render` identifies the engine and settings, not a version number. Multiple
renders of the same chapter coexist so they can be compared — which is exactly
what the two Chapter 1 files are for.

## Manifest shape

```jsonc
{
  "schemaVersion": 1,
  "books": [{
    "id": "book-01-the-ninth-standard",
    "title": "The Ninth Standard",
    "chapters": [{
      "number": 1,
      "title": "The Kid in Room Four",
      "manuscript": "books/.../chapter-01-....md",   // for a read-along view
      "renders": [{
        "render": "studio-q",
        "engine": "Google Cloud TTS",
        "voice": "en-US-Studio-Q",
        "file": "audio/.../ch01-....studio-q.mp3",
        "bytes": 15007744,
        "durationSec": 1870.44,
        "sha256": "4eb565d7...",       // cache invalidation without re-download
        "note": "…"
      }]
    }]
  }]
}
```

`durationSec` lets a player draw the scrubber before fetching a byte.
`sha256` lets a service worker decide whether a cached file is still current
without downloading it again — which matters when the whole point is offline.

## Storage: read this before adding Book 2

These files are tracked with **Git LFS** (`.gitattributes` at the repo root).
Without LFS, every clone would pull every version of every MP3 ever committed,
permanently.

The arithmetic, so the decision is made with open eyes:

| | Size |
|---|---|
| Chapter 1, both renders | 43 MB |
| Book 1 at 11 chapters, one engine | ~319 MB |
| Book 1 at 11 chapters, both engines | ~473 MB |
| Each re-render | adds a full copy to history, forever |

GitHub LFS gives 1 GB storage and **1 GB/month bandwidth** free. Book 1 alone
approaches half the storage, and the bandwidth ceiling is the sharper limit: a
PWA serving audio out of LFS would exhaust a month's quota in roughly twenty
full-book listens.

**LFS is right for trialling and wrong for serving.** When the player becomes
real, audio should move to object storage — Cloudflare R2 is the obvious pick
because it charges no egress, which is the entire cost of streaming audio — and
the manifest gains a `url` field beside `file`. Nothing else in the schema
changes, which is why the manifest indirection exists now rather than later.

## Current contents

| Chapter | Render | Length | Size |
|---|---|---|---|
| 1 — The Kid in Room Four | `studio-q` | 31m 10s | 14.3 MB |
| 1 — The Kid in Room Four | `elevenlabs` | 36m 08s | 29.2 MB |

The five-minute gap is the whole comparison. Studio-Q runs to a hand-written
pacing map — 697 breaks, tightening through the examination, opening out at
REDEFINE, `000` and the final line. ElevenLabs decides its own timing and lands
five minutes slower with better moment-to-moment delivery.

Chapters 2–4 are titled in `CHAPTER_ARCHITECTURE.md` but not yet written, so
there is nothing to render.

## For the player

Minimum an offline audiobook PWA needs beyond the manifest:

- **Service worker** caching MP3s via the Cache API, keyed on `sha256`
- **Media Session API** for lock-screen controls and artwork — without it, iOS
  gives you a silent tab rather than a player
- **Position persistence** per chapter, written on `pause` and `visibilitychange`
  rather than on an interval; iOS suspends timers when the screen locks
- **`playsinline` and a user-gesture start** — iOS will not autoplay audio
- Background playback needs the audio element alive; a PWA added to the Home
  Screen keeps playing with the screen off, a Safari tab often will not
