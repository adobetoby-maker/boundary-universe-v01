#!/usr/bin/env python3
"""
Prepare manuscript chapters as plain text for ElevenLabs.

ElevenLabs ignores <prosody> and decides its own timing, so unlike the Studio-Q
path there is no pacing map here -- only the job of making sure nothing reaches
the synthesiser that it will read literally or read wrong. That job is shared
with ssmlize.py and lives in normalise.py; this file is only chunking.

Usage:  python3 prep_el.py ../ms-all/ch03.md ...   ->  el_ch03.json
"""
import json, pathlib, re, sys

from normalise import chapter_heading, normalise, strip_markdown

# Not the engine ceiling. 4000 was the ceiling and it was wrong for prose:
# measured on identical text, 1800-char chunks read 6s tighter with half the
# pauses >=0.8s, and Toby could not hear the extra seam. Every chapter from
# ch10 on has used 1800. The ceiling is still ~4000 if something ever needs it.
MAX_CHARS = 1800


def prep(path: str) -> list[str]:
    t = pathlib.Path(path).read_text()
    n = int(re.search(r'ch(\d+)', path).group(1))

    t = re.sub(r'^#\s*Chapter\s*\d+\s*[—–-]\s*(.+)$',
               lambda m: chapter_heading(n, m.group(1)), t, count=1, flags=re.M)
    t = strip_markdown(t)
    t = re.sub(r'(?m)^\s*---\s*$', '', t).replace('⸻', '')
    t = normalise(t)

    # Split on paragraph boundaries only. A mid-paragraph split puts a hard stop
    # where the prose has none, and the seam is audible.
    chunks, cur = [], ''
    for p in (p.strip() for p in t.split('\n\n')):
        if not p:
            continue
        cand = (cur + '\n\n' + p).strip()
        if len(cand) > MAX_CHARS and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    return chunks


if __name__ == '__main__':
    for a in sys.argv[1:]:
        c = prep(a)
        stem = pathlib.Path(a).stem
        json.dump(c, open(f'el_{stem}.json', 'w'))
        # Count everything prep is meant to have removed, not just '**'. The
        # earlier counter looked only for bold and so reported a clean 0 with
        # two backticks sitting in the payload.
        stray = sum(x.count('*') + x.count('`') + x.count('|') + x.count('_') for x in c)
        print(f"{stem}: {len(c)} chunks, {sum(len(x) for x in c):,} chars, stray {stray}")
