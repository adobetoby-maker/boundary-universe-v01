# VOICE CAST — BOOK 1

Casting decisions and the reasoning behind them. Voice IDs are higgsfield preset
IDs, routed to ElevenLabs via `text2speech_v2` with `variant: elevenlabs`.

---

## The governing principle

**Chapter 1 is close third on Kade. The narrator is not a neutral observer —
it is Kade's interiority.**

> *It was a stupid question.*
>
> *Not mathematically. Mathematically it was almost insulting.*

Nobody is saying that aloud. That is a seventeen-year-old thinking, and the
narrator has to sound like the person doing the thinking. A middle-aged bass
narrating "I don't have enough facial muscles for that" puts an adult between
the reader and the boy, and the joke dies on the way across.

So: **narrator voice = Kade's voice.** Everything else is cast around it.

---

## Cast

| Role | Voice | Why |
|---|---|---|
| **Narrator / Kade Mercer** | `Cody` — `1ffcdbb3-078b-5491-959d-359e3021e917` | Lighter, younger. Must carry dry interiority without sounding like a man remembering being a boy. |
| *(alternate)* | `Miles` — `e18664a7-ee4f-5273-acf8-533eb24cd366` | Second light-male option, auditioned on the same passage. |
| **Darius Bell** | `Holden` — `3c9d6053-6334-592c-8997-4e325286af3f` | The bass that was wrong for Kade is right here. Sixteen, two inches taller, built like a linebacker in remedial geometry. |
| **Ms. Alvarez** | `Quinn` — `80914268-dfae-4f76-8306-36f2d55f58f8` | Calm, competent, dry. Never maternal — the direction is explicit about this. |
| **District proctor** | *uncast* | Needs an arc: relaxed and amused, then controlled, then frightened. Wants a voice that can lose composure without shouting. |

`Holden` was auditioned first as narrator and rejected — correctly. The note was
that the bass would eventually grate. It would have, over thirty-one minutes of
close-third from a teenager. Recast rather than discarded.

---

## Two production models

**Single narrator** (`el-cody-light-male.mp3`) — one voice does everything,
separating characters by cadence and attitude, exactly as
`AUDIO_NARRATION_PROMPT.md` specifies. This is the conventional audiobook and
the format a publisher expects.

**Full cast** (`el-cast-multivoice.mp3`) — each speaker rendered in their own
voice and stitched. Demonstrated across the Room Four exchange: narration in
Cody, Darius in Holden, Ms. Alvarez in Quinn, with 420ms between turns.

Trade-offs worth being clear about:

- Full cast makes character distinction effortless and removes the single
  biggest weakness of synthetic narration.
- It also multiplies production work by the number of speaking parts, and every
  dialogue tag — *"Darius said"* — has to be split off into the narrator's voice
  or it will be spoken in the character's.
- Full-cast audio is a genuine format, not a compromise. It is not what most
  progression fiction ships as.

---

## Why the dialogue tags are the hard part

In the cast demo the line

> "Bathroom," Darius said.

had to be cut into two segments — `"Bathroom."` in Holden, `Darius said.` in
Cody — because a single render would have Darius announcing his own attribution.

That split is invisible on the page and unavoidable in audio. Any full-cast
pipeline for this book needs a speaker-attribution pass over the manuscript
before synthesis. It is mechanical, but it is not free, and it is the reason
full-cast costs more than "same text, more voices."

---

## Engine note

Cast work is ElevenLabs, not Google Studio. Studio gives millisecond timing
control (see `README.md`) but a flatter read; ElevenLabs gives markedly better
delivery and, critically, a wider palette of usable character voices. The
break-level pacing map in `chapter-01.ssml` does not transfer — ElevenLabs
ignores `<prosody>` — so pacing has to be re-expressed through punctuation and
segment gaps.

## Open

- The proctor's shift is set at −0.75 but his *arc* — relaxed, then controlled,
  then frightened — is a delivery problem, not a pitch one, and is unsolved.
- Tessa is provisional; she has few lines in Chapter 1.

---

## LOCKED — production model and voice chain

**Single narrator.** Decided. Characters are separated by cadence, attitude and
a small pitch shading, all performed by one voice.

**Base voice:** Holden — `3c9d6053-6334-592c-8997-4e325286af3f` (ElevenLabs).

Holden as delivered carries more low end than thirty minutes of close third on
a seventeen-year-old can take. Two corrections, and they solve different
problems:

| | Setting | What it fixes |
|---|---|---|
| EQ | `highpass 85Hz`, `-6.5dB @ 140Hz`, `-2dB @ 250Hz` | The throb. This is the real fix — "throbbing bass" is low-frequency energy, not pitch. |
| Pitch | **+0.5 semitones** | Not tone. It lifts the baseline off the floor so the narrator has room to go *down* for Darius. |

Auditioned 0 / +0.5 / +0.75 / +1.0 / +1.5 / +3 / +3.86 st. **+0.5 chosen** — the
smallest lift that still buys downward room.

### Range map

Offsets are from the narrator baseline, not from raw Holden.

| Role | Shift | Note |
|---|---|---|
| Tessa | +1.25 | |
| **Narrator / Kade** | **0.00** | the narrator *is* Kade's interiority |
| Ms. Alvarez | 0.00 | dry and level — separated by attitude, not pitch |
| District proctor | −0.75 | tightens rather than drops as he loses composure |
| **Darius Bell** | **−1.25** | weight without becoming a different actor |

−2.5 was auditioned for Darius and rejected as too much: it read as an
impression rather than a shading, against the direction's own instruction to
avoid caricature. −1.25 separates him audibly and stays inside one performance.

About **5 semitones** of usable room sits below the baseline before delivery
strains. Darius uses a quarter of it. The rest is deliberate headroom for
whoever arrives later and needs to be the heaviest voice in the room — which is
the whole reason the baseline was lifted at all.

### Why this is treated as canon

Kade's voice is the one casting decision that compounds. If the series runs,
changing the baseline after recording begins costs a re-record of every chapter
in every book. The numbers above are locked, and `voice_chain.py` is the single
source for them.

```python
from voice_chain import filter_chain
filter_chain("narrator")   # EQ only
filter_chain("darius")     # EQ + -1.25 st
```
