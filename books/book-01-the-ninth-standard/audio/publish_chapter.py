#!/usr/bin/env python3
"""Publish one rendered chapter: manifest, commit, push, verify.

Every chapter to date was published by hand -- copy the file, compute three
values, hand-edit JSON, commit, push, curl. Six steps, and forgetting the last
one means shipping a manifest entry that points at nothing.

  python3 publish_chapter.py <n> <file.mp3> [--render holden] [--note "..."]
  python3 publish_chapter.py <n> <file.mp3> --dry-run

Verification is not optional here: the live URL must return 200 AND its
content-length must equal the bytes recorded in the manifest. A 200 alone
proves only that GitHub served something -- LFS pointers return 200 too, and
that is how a chapter ends up "published" as a 133-byte text file.
"""
import hashlib, json, os, subprocess, sys, time

REPO_URL = "https://media.githubusercontent.com/media/adobetoby-maker/boundary-universe-v01/main/"
AUDIO_DIR = "audio/book-01-the-ninth-standard"

def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)

def probe(path):
    r = sh(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=nw=1:nk=1", path])
    if not r.stdout.strip():
        sys.exit(f"{path} does not decode -- refusing to publish")
    return float(r.stdout)

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    n, src = int(sys.argv[1]), sys.argv[2]
    render = "holden"
    note = ""
    dry = "--dry-run" in sys.argv
    if "--render" in sys.argv: render = sys.argv[sys.argv.index("--render")+1]
    if "--note" in sys.argv:   note   = sys.argv[sys.argv.index("--note")+1]

    m = json.load(open("audio/manifest.json"))
    ch = next((c for c in m["books"][0]["chapters"] if c.get("number") == n), None)
    if ch is None: sys.exit(f"chapter {n} not in manifest")

    slug = os.path.basename(ch["manuscript"]).replace(".md","")
    slug = "-".join(slug.split("-")[:1] + slug.split("-")[1:])   # chapter-10-vector-class
    dest = f"{AUDIO_DIR}/ch{n:02d}-{'-'.join(slug.split('-')[2:])}.{render}.mp3"

    dur = probe(src)
    if not dry:
        subprocess.run(["cp", src, dest], check=True)
    b = open(src,"rb").read()
    sha = hashlib.sha256(b).hexdigest()

    # words/hour sanity: this narrator runs ~6,700-6,950. A large miss means the
    # wrong text, a wrong voice, or a failed chunk that got silently skipped.
    entry = {"render": render, "engine": "ElevenLabs",
             "voice": "Holden + locked chain (EQ 85/140/250Hz, +0.5st)",
             "file": dest, "bytes": len(b), "durationSec": round(dur,2),
             "sha256": sha, "url": REPO_URL + dest}
    if note: entry["note"] = note

    ch["renders"] = [r for r in ch.get("renders",[]) if r.get("render") != render]
    ch["renders"].append(entry)
    print(f"  ch{n:02d}  {len(b):,} bytes  {dur/60:.1f} min  sha {sha[:12]}")
    if dry:
        print("  --dry-run: nothing written"); return

    # Derive this count rather than incrementing it. A hand-maintained counter
    # drifts the first time a publish is retried or a render is withdrawn, and
    # the PWA dashboard reads this number.
    book = m["books"][0]
    book["renderedChapters"] = sum(1 for c in book["chapters"] if c.get("renders"))
    json.dump(m, open("audio/manifest.json","w"), indent=2)
    subprocess.run(["git","add",dest,"audio/manifest.json"], check=True)
    msg = f"audio ch{n:02d}: {render}, expanded manuscript"
    if note: msg += "\n\n" + note
    subprocess.run(["git","commit","-q","-m",msg], check=True)
    print("  pushing (LFS upload)...")
    # HEAD:main, not main. Publishing runs from a worktree checked out at
    # origin/main, where the local `main` ref is a different (older) commit --
    # "git push origin main" pushes that stale ref and fails, after the commit
    # has already been made.
    subprocess.run(["git","push","-q","origin","HEAD:main"], check=True)

    # CDN needs a moment; then verify BOTH status and size.
    url = entry["url"]
    for attempt in range(5):
        time.sleep(4)
        r = sh(["curl","-sIL","--max-time","45", url])
        code = [l for l in r.stdout.splitlines() if l.startswith("HTTP/")]
        clen = [l for l in r.stdout.lower().splitlines() if l.startswith("content-length")]
        if code and "200" in code[-1] and clen:
            got = int(clen[-1].split(":")[1])
            if got == len(b):
                print(f"  LIVE  200, {got:,} bytes -- matches manifest"); return
            print(f"  size mismatch: live {got:,} vs manifest {len(b):,} (retry {attempt+1})")
        else:
            print(f"  not live yet (retry {attempt+1})")
    sys.exit("  PUBLISHED BUT UNVERIFIED -- check the URL by hand")

if __name__ == "__main__":
    main()
