#!/bin/bash
# The only definition of done that counts.
#
# Exit 0 = the book is ready to be listened to. Exit 1 = it is not.
#
# Four conditions, deliberately. "The prose is finished" is not done. "The
# render completed" is not done. Each check below is something a machine can
# verify without believing a status file.
#
#   ./loop/done.sh          prints the report
#   ./loop/done.sh -q       silent, exit code only

set -uo pipefail
QUIET=false; [ "${1:-}" = "-q" ] && QUIET=true
say() { $QUIET || echo "$@"; }

REPO="${REPO:-$HOME/boundary-universe-v01}"
cd "$REPO" || exit 1
B1=origin/expand/book1-ch01-10
CHAPTERS=33
fail=0

say "── DONE CHECK ─────────────────────────────────────────"

# 1. every chapter at its architecture word target
#    Measured, not declared. Book 1 has no CHAPTER_ATTESTATIONS.md -- that is a
#    Book 2 convention -- so the source of truth is EXPANSION_TRACKER.md, which
#    carries a per-chapter target the agent cannot satisfy by editing a status
#    column. BAR is the fraction of target that counts as done.
BAR="${BAR:-0.90}"
short=$(git show "$B1:books/book-01-the-ninth-standard/EXPANSION_TRACKER.md" 2>/dev/null \
  | BAR="$BAR" B1="$B1" python3 -c '
import re, os, subprocess, sys
bar = float(os.environ["BAR"]); b1 = os.environ["B1"]
targets = {}
for line in sys.stdin:
    m = re.match(r"\|\s*(\d+)\s*\|[^|]*\|\s*([\d,]+)\s*\|", line)
    if m: targets[int(m.group(1))] = int(m.group(2).replace(",", ""))
files = subprocess.run(["git","ls-tree","-r","--name-only",b1],
                       capture_output=True, text=True).stdout.split()
short = []
for f in files:
    m = re.search(r"book-01.*manuscript/chapter-(\d{2})", f)
    if not m: continue
    n = int(m.group(1))
    if n not in targets: continue
    body = subprocess.run(["git","show",f"{b1}:{f}"],
                          capture_output=True, text=True).stdout
    w = len(body.split())
    if w < targets[n] * bar: short.append((n, w, targets[n]))
print(len(short))
for n, w, t in sorted(short, key=lambda r: r[1]/r[2])[:5]:
    print(f"         ch{n:02d} {w:,}/{t:,} ({w/t:.0%})", file=sys.stderr)
' 2>/tmp/bu-short.txt)
short=${short:-999}
if [ "$short" -eq 0 ]; then say "  [pass] word targets    all $CHAPTERS at >=$(echo "$BAR*100" | bc | cut -d. -f1)% of target"
else
  say "  [FAIL] word targets    $short chapter(s) under target — worst:"
  $QUIET || cat /tmp/bu-short.txt
  fail=1
fi

# 2. every chapter has a production render in the manifest
rend=$(python3 - <<'PY' 2>/dev/null || echo 0
import json
m=json.load(open('audio/manifest.json'))
print(sum(1 for c in m['books'][0]['chapters']
          if any(r['render'] in ('holden','elevenlabs','cast') for r in c['renders'])))
PY
)
if [ "$rend" -ge "$CHAPTERS" ]; then say "  [pass] rendered        $rend/$CHAPTERS"
else say "  [FAIL] rendered        $rend/$CHAPTERS"; fail=1; fi

# 3. zero READ findings across the book
#    Extract from the branch that actually holds the book, not the checkout.
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
for f in $(git ls-tree -r --name-only "$B1" | grep -E 'book-01.*manuscript/chapter-[0-9]{2}'); do
  n=$(basename "$f" | grep -oE '^chapter-[0-9]{2}' | grep -oE '[0-9]{2}')
  git show "$B1:$f" > "$TMP/ch$n.md"
done
A=books/book-01-the-ninth-standard/audio
read_findings=$(cd "$A" && python3 audit_text.py "$TMP"/ch*.md 2>/dev/null \
                | sed -n 's/^Would be spoken literally: //p')
read_findings=${read_findings:-999}
if [ "$read_findings" -eq 0 ]; then say "  [pass] READ findings   0"
else say "  [FAIL] READ findings   $read_findings"; fail=1; fi

# 4. every audio URL live, with a byte count matching the manifest
bad=$(python3 - <<'PY' 2>/dev/null || echo 999
import json, subprocess
m=json.load(open('audio/manifest.json')); bad=0
for c in m['books'][0]['chapters']:
    for r in c['renders']:
        u=r.get('url')
        if not u: continue
        out=subprocess.run(['curl','-sIL','--max-time','20',u],
                           capture_output=True,text=True).stdout
        code=[l for l in out.splitlines() if l.startswith('HTTP/')]
        length=[l for l in out.lower().splitlines() if l.startswith('content-length')]
        ok = code and '200' in code[-1] and length and \
             int(length[-1].split(':')[1]) == r['bytes']
        if not ok: bad += 1
print(bad)
PY
)
if [ "$bad" -eq 0 ]; then say "  [pass] live URLs       all 200, bytes match"
else say "  [FAIL] live URLs       $bad broken or size-mismatched"; fail=1; fi

say "───────────────────────────────────────────────────────"
if [ "$fail" -eq 0 ]; then say "  READY TO LISTEN"; else say "  not done"; fi
exit "$fail"
