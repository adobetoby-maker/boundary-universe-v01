#!/usr/bin/env python3
"""Assemble chunks into a chapter, correcting the per-chunk drift on the way.

higgsfield's MCP exposes no request stitching, so every chunk comes back as a
fresh roll of the delivery register. Measured on ch7 that produced a 469 Hz
brightness step at one seam and a chunk reading 1.14s median pauses against
0.78-0.83s elsewhere -- audible as "the voice changed" and "off timing".

We cannot stop the model doing it. We can measure every chunk and pull each one
back to the chapter median before joining:

  1. pause normalisation -- scale every silence by target/actual. Only the gaps
     change length; speech samples are untouched, so no pitch artefact.
  2. spectral matching   -- treble shelf at 2.5kHz. Calibrated at -75 Hz of
     centroid per dB on this material, linear across at least +/-3 dB.

The locked voice chain is applied last, to the assembled whole, so it stays
byte-identical to what shipped in chapters 1-7.

  python3 assemble_fixed.py <chunkdir> <out.mp3>
"""
import glob, os, re, statistics as st, subprocess, sys, tempfile

SR = 44100
NOISE, MIN_SIL = "-38dB", 0.35
HZ_PER_DB = 75.0                      # measured, not assumed
CHAIN = ("highpass=f=85, equalizer=f=140:t=q:w=1.0:g=-6.5, "
         "equalizer=f=250:t=q:w=1.2:g=-2")
SEMIS = 0.5

def run(args): return subprocess.run(args, capture_output=True, text=True)

def centroid(f):
    t = tempfile.mktemp(suffix=".txt")
    run(["ffmpeg","-v","error","-i",f,"-af",
         f"aresample=16000,aspectralstats=win_size=1024:measure=centroid,"
         f"ametadata=mode=print:key=lavfi.aspectralstats.1.centroid:file={t}",
         "-f","null","-"])
    v=[float(m.group(1)) for l in open(t) if (m:=re.search(r'centroid=([\d.]+)',l)) and float(m.group(1))>0]
    os.unlink(t)
    return sum(v)/len(v)

def gaps(f):
    err = run(["ffmpeg","-v","info","-i",f,"-af",
               f"silencedetect=noise={NOISE}:d={MIN_SIL}","-f","null","-"]).stderr
    spans, start = [], None
    for line in err.splitlines():
        s = re.search(r"silence_start: ([\d.]+)", line)
        if s: start = float(s.group(1))
        e = re.search(r"silence_end: ([\d.]+)", line)
        if e and start is not None:
            spans.append((start, float(e.group(1)))); start = None
    return spans

def dur(f):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration",
                      "-of","default=nw=1:nk=1",f]).stdout)

def correct(src, dst, pause_scale, tilt_db):
    """Rescale every silence, then tilt, in one filter pass."""
    sp, total = gaps(src), dur(src)
    filt, concat, cursor, idx = [], [], 0.0, 0
    for a, b in sp:
        if a > cursor:
            filt.append(f"[0:a]atrim={cursor}:{a},asetpts=PTS-STARTPTS[s{idx}]")
            concat.append(f"[s{idx}]"); idx += 1
        g = (b - a) * pause_scale
        filt.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{g:.3f},asetpts=PTS-STARTPTS[s{idx}]")
        concat.append(f"[s{idx}]"); idx += 1
        cursor = b
    if cursor < total:
        filt.append(f"[0:a]atrim={cursor}:{total},asetpts=PTS-STARTPTS[s{idx}]")
        concat.append(f"[s{idx}]"); idx += 1
    graph = ";".join(filt) + ";" + "".join(concat) + f"concat=n={idx}:v=0:a=1"
    if abs(tilt_db) > 0.05:
        graph += f",treble=g={tilt_db:.2f}:f=2500:width_type=q:w=0.7"
    graph += "[out]"
    subprocess.run(["ffmpeg","-v","error","-i",src,"-filter_complex",graph,
                    "-map","[out]","-c:a","libmp3lame","-b:a","192k",dst,"-y"], check=True)

def main(cdir, out):
    files = sorted(glob.glob(os.path.join(cdir, "chunk*.mp3")))
    if not files: sys.exit(f"no chunks in {cdir}")
    prof = []
    for f in files:
        sp = gaps(f)
        prof.append((f, centroid(f), st.median(b-a for a,b in sp) if sp else 0))
    tgt_c = st.median(p[1] for p in prof)
    tgt_p = st.median(p[2] for p in prof)
    print(f"  chapter target: centroid {tgt_c:.0f} Hz, median pause {tgt_p:.2f}s\n")

    tmpd = tempfile.mkdtemp()
    fixed = []
    for f, c, p in prof:
        tilt  = (tgt_c - c) / HZ_PER_DB
        scale = (tgt_p / p) if p else 1.0
        tilt  = max(-6.0, min(6.0, tilt))          # don't over-EQ a real outlier
        scale = max(0.6, min(1.6, scale))
        d = os.path.join(tmpd, os.path.basename(f))
        correct(f, d, scale, tilt)
        fixed.append(d)
        print(f"  {os.path.basename(f)}  centroid {c:6.0f}->{tgt_c:.0f} ({tilt:+.2f}dB)"
              f"   pause {p:.2f}->{tgt_p:.2f} (x{scale:.3f})")

    lst = os.path.join(tmpd, "list.txt")
    open(lst,"w").write("".join(f"file '{f}'\n" for f in fixed))
    joined = os.path.join(tmpd, "joined.mp3")
    subprocess.run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",lst,
                    "-c","copy",joined,"-y"], check=True)

    r = 2 ** (SEMIS/12)
    chain = f"{CHAIN}, asetrate={SR}*{r:.6f}, aresample={SR}, atempo={1/r:.6f}"
    subprocess.run(["ffmpeg","-v","error","-i",joined,"-af",chain,
                    "-c:a","libmp3lame","-b:a","128k",out,"-y"], check=True)
    print(f"\n  wrote {out}  ({dur(out)/60:.1f} min)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
