#!/usr/bin/env python3
"""Normalise pause lengths within a span so its median gap matches a target.

Why this exists: higgsfield's MCP gives no request stitching, so each rendered
chunk is a fresh roll of the delivery register -- ch7's chunk 5 came back with a
1.14s median pause against 0.78-0.83s in chunks 1/2/4, and 36 pauses over 1.2s
where they had one each. That reads as "off timing".

We cannot stop the model producing it, but the fix is deterministic at assembly:
scale every silence by target/actual. Speech samples are never touched -- only
the gaps between them change length -- so there is no pitch or formant artefact.

  python3 pace.py <in.mp3> <out.mp3> <target_median_s>
"""
import re, subprocess, sys, statistics as st

NOISE = "-38dB"     # matches the threshold used for all measurement in this project
MIN_SIL = 0.35      # below this is intra-phrase breath, not a pause; leave alone

def silences(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", path, "-af",
         f"silencedetect=noise={NOISE}:d={MIN_SIL}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    spans, start = [], None
    for line in out.splitlines():
        s = re.search(r"silence_start: ([\d.]+)", line)
        if s: start = float(s.group(1))
        e = re.search(r"silence_end: ([\d.]+)", line)
        if e and start is not None:
            spans.append((start, float(e.group(1)))); start = None
    return spans

def duration(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path], capture_output=True, text=True).stdout)

def main(src, dst, target):
    sp = silences(src)
    if not sp:
        subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-c", "copy", dst, "-y"]); return
    med = st.median(b - a for a, b in sp)
    scale = target / med
    print(f"  median pause {med:.2f}s -> target {target:.2f}s  (scale {scale:.3f}, {len(sp)} pauses)")
    if abs(scale - 1) < 0.03:
        print("  already within 3% — copying unchanged")
        subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-c", "copy", dst, "-y"]); return

    # Build a filter that keeps every speech segment and rescales every gap.
    total, parts, cursor, idx = duration(src), [], 0.0, 0
    filt, concat = [], []
    for a, b in sp:
        if a > cursor:                                    # speech before this gap
            filt.append(f"[0:a]atrim={cursor}:{a},asetpts=PTS-STARTPTS[s{idx}]")
            concat.append(f"[s{idx}]"); idx += 1
        gap = (b - a) * scale                             # the rescaled silence
        filt.append(f"anullsrc=r=44100:cl=mono,atrim=0:{gap:.3f},asetpts=PTS-STARTPTS[s{idx}]")
        concat.append(f"[s{idx}]"); idx += 1
        cursor = b
    if cursor < total:
        filt.append(f"[0:a]atrim={cursor}:{total},asetpts=PTS-STARTPTS[s{idx}]")
        concat.append(f"[s{idx}]"); idx += 1

    graph = ";".join(filt) + ";" + "".join(concat) + f"concat=n={idx}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-filter_complex", graph,
                    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", dst, "-y"],
                   check=True)
    print(f"  wrote {dst}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
