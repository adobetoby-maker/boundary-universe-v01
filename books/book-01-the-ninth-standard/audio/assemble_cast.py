#!/usr/bin/env python3
"""
Stitch full-cast runs into one chapter.

Each run arrives as raw ElevenLabs output in its BASE voice. Two things then
happen, in this order and for different reasons:

  1. The per-character pitch shift, applied per run. It has to be per run --
     that is the whole point, each speaker gets a different one.
  2. The Holden EQ, also per run, because the shift and the EQ interact: the
     asetrate/atempo pair moves the spectrum, so EQ'ing before shifting would
     put the -6.5dB notch in the wrong place by the size of the shift.

That is the opposite of the single-voice path, where the chain is applied ONCE
over the finished chapter to avoid compounding resample error. Here the error is
accepted because there is no alternative: one chain cannot serve eight shifts.

Between runs, a gap. A voice change with no gap reads as one person changing
their mind mid-sentence; too long and a quick exchange turns into a standoff.
CAST.md used 420ms in the Chapter 1 cast demo and that is the starting point.
"""
import json, os, subprocess, sys

from cast_split import CAST
from voice_chain import EQ, SAMPLE_RATE, NARRATOR_SEMITONES

TURN_GAP_MS = 380       # voice change mid-scene
SR = SAMPLE_RATE


# Holden's chain is not a house chain. Both halves of it are answers to
# Holden's specific problems, and neither transfers:
#
#   the +0.5 st lift  exists so the narrator has room to go DOWN for Darius.
#   the 140/250 Hz cut kills Holden's low-frequency throb.
#
# Applied to a female voice the first simply pitches her up, and the second
# notches out her fundamental -- 140-250 Hz is Maeve's chest voice, not a
# throb. Together they made Elena thin and high, which is exactly what Toby
# heard. Each base voice now carries its own baseline and its own EQ.
BASE_BASELINE = {'holden': NARRATOR_SEMITONES, 'maeve': 0.00}
BASE_EQ = {
    'holden': EQ,
    'maeve': 'highpass=f=70',   # rumble only; nothing else needs correcting
}


def chain_for(role: str) -> str:
    base, shift = CAST[role]
    semis = BASE_BASELINE[base] + shift
    eq = BASE_EQ[base]
    if abs(semis) < 0.01:
        return eq
    r = 2 ** (semis / 12)
    # EQ BEFORE the shift, matching voice_chain.filter_chain exactly.
    #
    # This was briefly reversed on the reasoning that a shift moves the notch
    # off 140 Hz, so each character would be EQ'd at a different frequency.
    # That is true and it is the correct behaviour: the notch exists to cut
    # Holden's low-frequency resonance, and when Holden is pitched down for
    # Darius that resonance moves down with him. A notch pinned to 140 Hz
    # would drift off the thing it is correcting, by exactly the character's
    # shift. It should track the voice.
    #
    # It also has to match: the narrator here must be bit-comparable to the
    # Holden in the shipped chapters 2-5, and shift-then-EQ put its notch
    # 4.1 Hz low. Caught by Toby asking whether it was the same Holden.
    return f"{eq}, asetrate={SR}*{r:.6f}, aresample={SR}, atempo={1/r:.6f}"


def silence(path, ms):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi',
                    '-i', f'anullsrc=r={SR}:cl=mono', '-t', f'{ms/1000:.3f}',
                    '-b:a', '128k', path], check=True)


def build(runs, urls, out):
    """runs: [(role, [texts], [(line, voice)])]   urls: parallel list of mp3 URLs"""
    d = out + '_parts'
    os.makedirs(d, exist_ok=True)
    gap = f'{d}/gap.mp3'
    silence(gap, TURN_GAP_MS)

    pieces = []
    for i, ((role, texts, src), url) in enumerate(zip(runs, urls), 1):
        raw = f'{d}/{i:03d}_raw.mp3'
        fin = f'{d}/{i:03d}_{role}.mp3'
        if not os.path.exists(raw):
            subprocess.run(['curl', '-sL', '-o', raw, url], check=True)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw,
                        '-af', chain_for(role), '-ar', str(SR), '-ac', '1',
                        '-b:a', '128k', fin], check=True)
        if pieces:
            pieces.append(gap)
        pieces.append(fin)
        print(f"  {i:3} {role:8} line {src[0][0]:>4}  {os.path.getsize(fin)/1000:6.0f} kB", flush=True)

    with open(f'{d}/list.txt', 'w') as fh:
        for p in pieces:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
                    '-i', f'{d}/list.txt', '-b:a', '128k', out], check=True)
    s = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                              'format=duration', '-of', 'csv=p=0', out],
                             capture_output=True, text=True).stdout)
    print(f"-> {out}   {int(s//60)}m {int(s%60):02d}s   {os.path.getsize(out)/1e6:.1f} MB")
