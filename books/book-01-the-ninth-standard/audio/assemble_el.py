#!/usr/bin/env python3
"""
Stitch a chapter's ElevenLabs chunks into one MP3 and apply the locked Holden chain.

Usage:  python3 assemble_el.py ch03 <url1> <url2> ...

The chain is applied ONCE over the whole chapter rather than per chunk. Applying
an asetrate/atempo pair six times would compound six rounds of resampling error
on a file that is already lossy, and any per-chunk difference in the EQ tail
would be audible at the seams.
"""
import os, subprocess, sys
from voice_chain import filter_chain

stem, urls = sys.argv[1], sys.argv[2:]
d = f"el_{stem}"
os.makedirs(d, exist_ok=True)

parts = []
for i, u in enumerate(urls, 1):
    p = f"{d}/{i:02d}.mp3"
    if not os.path.exists(p):
        subprocess.run(["curl", "-sL", "-o", p, u], check=True)
    parts.append(p)
    print(f"  {i:2}  {os.path.getsize(p)/1e6:5.2f} MB", flush=True)

with open(f"{d}/list.txt", "w") as fh:
    for p in parts:
        fh.write(f"file '{os.path.basename(p)}'\n")

raw = f"{d}/raw.mp3"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", f"{d}/list.txt", "-c", "copy", raw], check=True)

out = f"out/{stem}.holden.mp3"
os.makedirs("out", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw,
                "-af", filter_chain("narrator"), "-b:a", "128k", out], check=True)

s = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
print(f"-> {out}   {int(s//60)}m {int(s%60):02d}s   {os.path.getsize(out)/1e6:.1f} MB")
