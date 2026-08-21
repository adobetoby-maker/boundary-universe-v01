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

- Cast the proctor. His arc across the chapter is the subtlest performance ask
  in it.
- Decide single-narrator versus full cast before Book 2 is drafted; it changes
  how dialogue tags should be written.
- Kade's voice is the one casting decision that compounds. If the series runs,
  changing it later costs a re-record of everything.
