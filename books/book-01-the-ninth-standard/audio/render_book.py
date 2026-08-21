#!/usr/bin/env python3
"""
Render chapters to MP3 with Google Cloud TTS (en-US-Studio-Q).

Takes manuscript markdown, runs it through ssmlize.py, chunks under the API
ceiling, synthesises, and stitches one MP3 per chapter.

Usage:  python3 render_book.py ms/ch02.md ms/ch03.md ...
"""

import base64
import json
import os
import subprocess
import sys

from ssmlize import ssmlize

VOICE = "en-US-Studio-Q"
PROJECT = "workerbee-494003"
RATE = 0.94
MAX_BYTES = 4300          # API ceiling is 5000 including tags
ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"


def token() -> str:
    out = subprocess.run(["gcloud", "auth", "application-default", "print-access-token"],
                         capture_output=True, text=True)
    t = out.stdout.strip()
    if not t:
        sys.exit("No ADC token available.")
    return t


def chunk(body: str):
    """Split only at line boundaries — a mid-line split would drop the <break>
    carrying that beat and the seam would be audible."""
    packed, cur = [], ""
    for line in body.split("\n"):
        cand = (cur + "\n" + line).strip()
        if len(cand.encode()) > MAX_BYTES and cur:
            packed.append(cur)
            cur = line
        else:
            cur = cand
    if cur:
        packed.append(cur)
    return packed


def synth(ssml: str, path: str, tok: str) -> bool:
    payload = {
        "input": {"ssml": f"<speak>{ssml}</speak>"},
        "voice": {"languageCode": "en-US", "name": VOICE},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": RATE,
                        "pitch": 0.0, "effectsProfileId": ["headphone-class-device"]},
    }
    with open("_b.json", "w") as fh:
        json.dump(payload, fh)
    raw = subprocess.run([
        "curl", "-s", "-X", "POST",
        "-H", f"Authorization: Bearer {tok}",
        "-H", f"x-goog-user-project: {PROJECT}",
        "-H", "Content-Type: application/json; charset=utf-8",
        "--data-binary", "@_b.json", ENDPOINT,
    ], capture_output=True, text=True).stdout
    d = json.loads(raw)
    if "audioContent" not in d:
        print("    FAIL:", json.dumps(d)[:200], flush=True)
        return False
    with open(path, "wb") as fh:
        fh.write(base64.b64decode(d["audioContent"]))
    return True


def dur(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    return float(o) if o else 0.0


def main():
    tok = token()
    os.makedirs("out", exist_ok=True)
    grand_chars = 0

    for src in sys.argv[1:]:
        stem = os.path.splitext(os.path.basename(src))[0]
        out_mp3 = f"out/{stem}.mp3"
        if os.path.exists(out_mp3):
            print(f"{stem}: already rendered ({dur(out_mp3)/60:.1f}m) — skipping", flush=True)
            continue

        with open(src, encoding="utf-8") as fh:
            title, body = ssmlize(fh.read())
        parts = chunk(body)
        grand_chars += len(body)
        print(f"{stem}: {title} — {len(body):,} chars, {len(parts)} chunks", flush=True)

        made = []
        d = f"out/{stem}_parts"
        os.makedirs(d, exist_ok=True)
        for i, c in enumerate(parts, 1):
            p = f"{d}/{i:02d}.mp3"
            if synth(c, p, tok):
                made.append(p)
                print(f"    {i:2}/{len(parts)}  {dur(p):5.1f}s", flush=True)
            else:
                break

        if len(made) != len(parts):
            print(f"  {stem}: {len(made)}/{len(parts)} rendered — NOT stitching a partial chapter", flush=True)
            continue

        with open(f"{d}/list.txt", "w") as fh:
            for p in made:
                fh.write(f"file '{os.path.basename(p)}'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", f"{d}/list.txt", "-c", "copy", out_mp3], check=True)
        s = dur(out_mp3)
        print(f"  -> {out_mp3}  {int(s//60)}m {int(s%60):02d}s", flush=True)

    if grand_chars:
        print(f"\n~${grand_chars/1_000_000*16:.2f} at Studio pricing", flush=True)


if __name__ == "__main__":
    main()
