"""
Voice chain — Book 1, single narrator.

LOCKED SETTINGS. Changing the baseline after recording begins costs a re-record
of everything, so these numbers are treated as canon, not preference.

Base voice: Holden (ElevenLabs preset 3c9d6053-6334-592c-8997-4e325286af3f).

Holden as delivered has more low-frequency weight than a thirty-minute close
third on a seventeen-year-old can carry. Two separate corrections, and it
matters that they are separate:

  1. EQ removes the throb. This is the fix that actually addresses the
     complaint — "throbbing bass" is low-frequency energy, not pitch.
  2. A small pitch lift moves the baseline off the floor of the range. This is
     NOT about tone. It exists so the narrator has somewhere to go DOWN when he
     voices Darius. With the baseline on the floor, every character has to go
     up, and the one character who most needs weight is the one you cannot
     give it to.

Auditioned 0 / +0.5 / +0.75 / +1.0 / +1.5 / +3 / +3.86 semitones.
Chosen: +0.5 — the smallest lift that still buys downward room.
"""

SAMPLE_RATE = 44100

# Applied to every render, before any per-character shift.
EQ = "highpass=f=85, equalizer=f=140:t=q:w=1.0:g=-6.5, equalizer=f=250:t=q:w=1.2:g=-2"

NARRATOR_SEMITONES = 0.5

# Offsets from the narrator baseline, not from raw Holden.
# Deliberately small: AUDIO_NARRATION_PROMPT.md asks for distinction through
# cadence and attitude rather than caricature, and past about 2 semitones a
# shading becomes an impression.
CHARACTER_SHIFT = {
    "narrator": 0.0,     # Kade — the narrator IS his interiority
    "kade": 0.0,         # spoken dialogue sits at the same place as the narration
    "darius": -1.25,     # weight without becoming a different actor
    "alvarez": 0.0,      # dry and level; separated by attitude, not pitch
    "proctor": -0.75,    # tightens rather than drops as he loses composure
    "tessa": 1.25,
}

# ~5 semitones of usable room sits below the baseline before delivery strains.
# Darius uses a quarter of it, which leaves headroom for whoever turns up later
# and needs to be the heaviest voice in the room.
USABLE_RANGE_BELOW = 5.0


def filter_chain(role: str = "narrator") -> str:
    """ffmpeg -af chain for a given speaker."""
    semis = NARRATOR_SEMITONES + CHARACTER_SHIFT.get(role, 0.0)
    if abs(semis) < 0.01:
        return EQ
    ratio = 2 ** (semis / 12)
    # asetrate shifts pitch and speed together; atempo puts the speed back.
    return (
        f"{EQ}, asetrate={SAMPLE_RATE}*{ratio:.6f}, "
        f"aresample={SAMPLE_RATE}, atempo={1/ratio:.6f}"
    )


if __name__ == "__main__":
    for role in CHARACTER_SHIFT:
        total = NARRATOR_SEMITONES + CHARACTER_SHIFT[role]
        print(f"{role:10} {CHARACTER_SHIFT[role]:+.2f} from baseline  ->  {total:+.2f} absolute")
