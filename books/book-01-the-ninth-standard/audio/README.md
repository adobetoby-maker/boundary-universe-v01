# AUDIO PRODUCTION — BOOK 1

`AUDIO_NARRATION_PROMPT.md` is direction written for a human in a booth. This
folder is the machine layer: the same direction encoded so a synthesiser can
obey it, plus what was learned making it work.

| File | What it is |
|---|---|
| `chapter-01.ssml` | Full Chapter 1 as SSML — 41,344 chars, 697 breaks, 41 prosody spans |
| `ch1_part_{a,b,c,d}.py` | The same markup in four editable movements, with pacing notes |
| `synthesize.py` | Chunks, renders and stitches to a single MP3 |

Rendered length: **31m 10s**. Cost: **$0.66**.

---

## The finding that matters most

**The manuscript's line-breaking is the performance direction, and no TTS engine
can see it.**

Chapter 1 is written in single-line beats:

> Not offline.
>
> Terminated.

A human narrator reads that and knows to leave a gap. Every synthesiser receives
one paragraph and reads it as one breath — the gap vanishes, and with it the
effect the line break was built to create.

So every beat had to be re-encoded explicitly. That is what the 697 `<break>`
tags are. They are not decoration; they are the manuscript's existing rhythm,
made visible to a machine.

This is a direct consequence of Canon Rule 8. If the book is audio-first, the
prose is already carrying performance information that must survive the trip to
audio, and right now it only survives if someone marks it up by hand.

---

## Why en-US-Studio-Q

Google's Studio tier is their long-form narration line. The deciding factor was
not timbre but **control**: Studio accepts SSML. Chirp3-HD sounds more natural
moment to moment but is text-only, so "slow slightly around REDEFINE" becomes a
hope rather than an instruction.

Three voices were auditioned on the same opening. Studio-Q was chosen.

---

## Studio constraints discovered the hard way

**`<prosody>` rejects `pitch` on Studio voices.** The API returns 400:

> `<prosody>` tags do not currently support `pitch` attributes for Studio voices.

Pitch was originally doing the work of marking screen text and dropping the
floor under `REDEFINE` and `000`. With pitch unavailable, that weight moved onto
**rate and surrounding silence**. Screen text now sits at 86–90% rate with a
break either side; the big beats drop to 69–74%.

Practical rule: **on Studio, rate and `<break>` are the only real instruments.**

Other limits:
- 5,000 bytes per request *including tags* — hence the `||` chunk markers
- Splits happen only at those markers; a split mid-passage would drop the break
  carrying the beat and the seam would be audible

---

## Break vocabulary

Kept consistent so the chapter has one rhythm rather than fourteen:

| Duration | Use |
|---|---|
| 180–300ms | Inside a fast exchange, or a rapid list |
| 350–450ms | A normal beat — one manuscript line |
| 600ms | A joke landing. Breathe; do not milk it |
| 800–900ms | Paragraph or topic shift |
| 1200–1600ms | Scene break |

## Pacing arc

The examination tightens by **shortening beats, not speeding speech** — faster
delivery reads as panicked rather than tense. Beats run 500ms early in the exam
and collapse to 180ms by "Heat. Charge. Fluid flow. Collisions."

Against that, `REDEFINE`, `000` and the final paragraphs open back out to
900–1300ms. The contrast is the chapter's shape; if both movements run at one
speed, neither lands.

## Number normalisation

Synthesisers mangle these. All are pre-written as speech:

| Manuscript | Spoken |
|---|---|
| `000` | "Zero. Zero. Zero." at 69–74% rate with 300ms between |
| `27,000 N` | twenty-seven thousand newtons |
| `10:17` | ten seventeen |
| `-8.3%` | minus eight point three percent |
| `99.98%` | ninety-nine point nine eight percent |
| `87:13` | eighty-seven thirteen |

`000` is the chapter's hinge and is the one place worth checking on every
re-render — it must read as three deliberate digits, never as "zero" or "triple
zero."

---

## Engine comparison

| | Google Studio | ElevenLabs |
|---|---|---|
| Timing control | Exact, millisecond `<break>` | `<break>` only, capped ~3s; no `<prosody>` |
| Emotional direction | None — rate only | v3 audio tags (`[whispers]`, `[sighs]`) |
| Determinism | Same input, same output | Re-rolls differ between renders |
| Natural delivery | Competent, slightly flat | Markedly better |
| Cost | ~$16 / million chars | Roughly an order of magnitude more |
| Long-form tooling | None — the pipeline here is bespoke | Studio/Projects, built for books |

**Honest read: Google is the better draft tool, ElevenLabs is likely the better
final tool.** Google gives deterministic rhythm and costs almost nothing, which
is what you want while the prose is still moving. ElevenLabs gives performance
and character separation, which is what you want once it has stopped.

They are not the same instrument. Google's control is *timing*; ElevenLabs'
control is *delivery*. The break map in `chapter-01.ssml` does not transfer —
ElevenLabs ignores `<prosody>` — but the pacing decisions behind it do, and would
be re-expressed as punctuation, paragraphing and v3 tags.

## What no single-voice TTS will give you

Darius, Ms. Alvarez and the proctor as genuinely separate performances. The
writing distinguishes them by cadence and attitude, which is what
`AUDIO_NARRATION_PROMPT.md` asks for, and a single synthetic voice can carry
cadence but not timbre. For an audition tape or a commercial release this is a
draft, not a master.

Its real use is answering the question Canon Rule 8 poses: **does the prose work
aloud?**

---

## Regenerating

```bash
cd books/book-01-the-ninth-standard/audio
python3 synthesize.py --out chapter-01.mp3
```

Requires `gcloud` ADC with a quota project that has the Cloud Text-to-Speech API
enabled, and `ffmpeg`. Audio output is intentionally not committed.
