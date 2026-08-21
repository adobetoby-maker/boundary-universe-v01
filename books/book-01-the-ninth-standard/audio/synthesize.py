#!/usr/bin/env python3
"""
Render Chapter 1 to audio with Google Cloud TTS (en-US-Studio-Q).

Studio voices are Google's long-form narration tier and, unlike Chirp3-HD,
accept SSML — which is the whole reason for this pipeline. The direction in
AUDIO_NARRATION_PROMPT.md is written for a human in a booth; this turns it
into markup a synthesiser can actually obey.

The manuscript is written in single-line beats. That line-breaking IS the
performance direction, and TTS cannot see it — a paragraph is a paragraph.
Every beat is therefore re-encoded as an explicit <break>.

Requires: gcloud ADC, ffmpeg.
Usage:    python3 synthesize.py [--out chapter-01.mp3]
"""

import base64
import json
import os
import subprocess
import sys

from ch1_part_a import PART_A
from ch1_part_b import PART_B
from ch1_part_c import PART_C
from ch1_part_d import PART_D

VOICE = "en-US-Studio-Q"
PROJECT = "workerbee-494003"
RATE = 0.94          # baseline; per-passage <prosody> overrides ride on top
MAX_BYTES = 4300     # API ceiling is 5000 incl. tags — leave room for <speak>

ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"


def token() -> str:
    out = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True, text=True,
    )
    t = out.stdout.strip()
    if not t:
        sys.exit(f"No ADC token. {out.stderr.strip()[:200]}")
    return t


def chunks():
    """Split on '||' markers, then greedily pack under MAX_BYTES.

    Splitting only at author-placed markers matters: a split mid-passage would
    drop the <break> that carries the beat, and the seam would be audible.
    """
    blocks = []
    for part in (PART_A, PART_B, PART_C, PART_D):
        blocks.extend(b.strip() for b in part.split("||") if b.strip())

    packed, cur = [], ""
    for b in blocks:
        candidate = (cur + "\n" + b).strip()
        if len(candidate.encode()) > MAX_BYTES and cur:
            packed.append(cur)
            cur = b
        else:
            cur = candidate
    if cur:
        packed.append(cur)
    return packed


def synth(ssml_body: str, path: str, tok: str) -> bool:
    payload = {
        "input": {"ssml": f"<speak>{ssml_body}</speak>"},
        "voice": {"languageCode": "en-US", "name": VOICE},
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": RATE,
            "pitch": 0.0,
            "effectsProfileId": ["headphone-class-device"],
        },
    }
    with open("_body.json", "w") as fh:
        json.dump(payload, fh)

    raw = subprocess.run([
        "curl", "-s", "-X", "POST",
        "-H", f"Authorization: Bearer {tok}",
        "-H", f"x-goog-user-project: {PROJECT}",
        "-H", "Content-Type: application/json; charset=utf-8",
        "--data-binary", "@_body.json", ENDPOINT,
    ], capture_output=True, text=True).stdout

    data = json.loads(raw)
    if "audioContent" not in data:
        print("  FAILED:", json.dumps(data)[:300])
        return False
    with open(path, "wb") as fh:
        fh.write(base64.b64decode(data["audioContent"]))
    return True


def duration(path: str) -> float:
    out = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path,
    ], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def main():
    out_name = "chapter-01.mp3"
    if "--out" in sys.argv:
        out_name = sys.argv[sys.argv.index("--out") + 1]

    os.makedirs("parts", exist_ok=True)
    tok = token()
    cs = chunks()
    total_chars = sum(len(c) for c in cs)
    print(f"{len(cs)} chunks, {total_chars:,} chars of SSML")

    made = []
    for i, c in enumerate(cs, 1):
        path = f"parts/{i:02d}.mp3"
        print(f"  [{i:2}/{len(cs)}] {len(c.encode()):>5}b ...", end=" ", flush=True)
        if synth(c, path, tok):
            made.append(path)
            print(f"{duration(path):5.1f}s")

    if len(made) != len(cs):
        sys.exit(f"\nOnly {len(made)}/{len(cs)} chunks rendered — not stitching a partial chapter.")

    with open("parts/list.txt", "w") as fh:
        for p in made:
            fh.write(f"file '{os.path.basename(p)}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", "parts/list.txt", "-c", "copy", out_name,
    ], check=True)

    secs = duration(out_name)
    print(f"\n{out_name} — {int(secs // 60)}m {int(secs % 60)}s")
    # Studio is billed per character; the estimate keeps the cost honest.
    print(f"~${total_chars / 1_000_000 * 16:.2f} at Studio pricing")


if __name__ == "__main__":
    main()
