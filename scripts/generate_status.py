#!/usr/bin/env python3
"""
Generate dashboard/status.json from the repository instead of by hand.

WHY
---
The hand-maintained status.json listed 5 chapters with Chapter 5 at "PASS 1
COMPLETE". The manuscript branch had 11 chapters with 5 through 10 attested.
It also reported Book 2 at 12% when 11 of 34 chapters is 32%. Nobody did
anything wrong; a file that has to be remembered eventually isn't.

Everything below is derived. If the dashboard is wrong now, the repository is
wrong, which is a much easier thing to notice.

WHAT IT READS
-------------
  manuscript/chapter-NN-*.md   chapter numbers, titles, real word counts
  CHAPTER_ATTESTATIONS.md      per-chapter status and architecture target
  START_HERE.md                the CURRENT pass count

The pass count is read rather than hardcoded on purpose. The protocol moved
from four passes to five while this script was being written, and a generator
carrying "4" in a constant would have quietly disagreed with the book from its
first run.

DRIFT
-----
Where two sources disagree the script does not pick a winner. It records the
disagreement in status.json under `drift` and exits non-zero with --strict, so
CI can fail on it. A dashboard that hides a contradiction is worse than no
dashboard, because it looks like agreement.

Usage:
    python3 scripts/generate_status.py --manuscript-ref origin/draft/book-02-four-pass
    python3 scripts/generate_status.py --strict          # non-zero exit on drift
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

BOOK2 = "books/book-02-the-twelfth-resonant"
BOOK1 = "books/book-01-the-ninth-standard"


def read(path: str, ref: str | None) -> str | None:
    """Read a file from a git ref, or from the working tree when ref is None."""
    if ref:
        r = subprocess.run(["git", "show", f"{ref}:{path}"],
                           capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    p = pathlib.Path(path)
    return p.read_text() if p.exists() else None


def list_files(prefix: str, ref: str | None) -> list[str]:
    if ref:
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref],
                           capture_output=True, text=True)
        names = r.stdout.splitlines()
    else:
        names = [str(p) for p in pathlib.Path().rglob("*") if p.is_file()]
    return sorted(n for n in names if n.startswith(prefix))


def chapters(book: str, ref: str | None) -> list[dict]:
    """Chapter number, title and ACTUAL word count, straight from the prose."""
    out = []
    for f in list_files(f"{book}/manuscript/chapter-", ref):
        m = re.search(r"chapter-(\d+)-(.+)\.md$", f)
        if not m:
            continue
        text = read(f, ref) or ""
        heading = re.search(r"^#\s*Chapter\s*\d+\s*[—–-]\s*(.+)$", text, re.M)
        out.append({
            "n": int(m.group(1)),
            "title": heading.group(1).strip() if heading else
                     m.group(2).replace("-", " ").title(),
            "words": len(text.split()),
        })
    return out


def pass_protocol(ref: str | None) -> tuple[int, str]:
    """How many passes the book currently requires, per START_HERE."""
    text = read(f"{BOOK2}/START_HERE.md", ref) or ""
    m = re.search(r"protocol\s*[—–-]\s*(FOUR|FIVE|SIX|SEVEN)\s+PASSES", text, re.I)
    if m:
        word = m.group(1).upper()
        return {"FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7}[word], "START_HERE.md"
    m = re.search(r"(\w+)\s+manuscript passes", text, re.I)
    return 0, "unknown"


def attestations(ref: str | None) -> tuple[dict[int, dict], int | None]:
    """Per-chapter status from CHAPTER_ATTESTATIONS.md, plus the pass count
    that document believes in (which may differ from START_HERE)."""
    text = read(f"{BOOK2}/CHAPTER_ATTESTATIONS.md", ref) or ""
    doc_passes = None
    m = re.search(r"completed (four|five|six) manuscript passes", text, re.I)
    if m:
        doc_passes = {"four": 4, "five": 5, "six": 6}[m.group(1).lower()]

    found = {}
    for block in re.split(r"^## Chapter ", text, flags=re.M)[1:]:
        num = re.match(r"(\d+)", block)
        if not num:
            continue
        n = int(num.group(1))
        status = re.search(r"\*\*Status:\*\*\s*\*\*(.+?)\*\*", block)
        target = re.search(r"expected production count:\*\*\s*~?([\d,]+)", block)
        done = len(re.findall(r"^- Pass \d+", block, re.M))
        found[n] = {
            "status": status.group(1).strip() if status else "UNKNOWN",
            "target": int(target.group(1).replace(",", "")) if target else None,
            "passesRecorded": done,
        }
    return found, doc_passes


def richest_branch(book: str) -> tuple[str, int]:
    """Find the branch holding the most manuscript prose for a book.

    This check exists because of a specific, expensive mistake: twice in one
    session someone concluded Book 1 was barely written, having looked only at
    `main`. The real manuscript was on a feature branch. Worse, the expanded
    Book 1 and the branch Book 2 is drafted from diverged by 41,000 words --
    including the clue trail that sets up Book 2's own title.

    A dashboard that reports whichever branch it happened to be handed is not
    reporting the book. So: look everywhere, and say where the most is.
    """
    r = subprocess.run(["git", "branch", "-r", "--format=%(refname:short)"],
                       capture_output=True, text=True)
    best, best_words = "", 0
    for br in r.stdout.split():
        if br.endswith("/HEAD"):
            continue
        words = sum(len((read(f, br) or "").split())
                    for f in list_files(f"{book}/manuscript/chapter-", br))
        if words > best_words:
            best, best_words = br, words
    return best, best_words


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-ref", default=None,
                    help="fallback ref for both books (default: working tree)")
    ap.add_argument("--book1-ref", default="origin/expand/book1-ch01-10",
                    help="ref holding Book 1 -- it lives on its own branch")
    ap.add_argument("--book2-ref", default="origin/draft/book-02-four-pass",
                    help="ref holding Book 2 -- also its own branch")
    ap.add_argument("--out", default="dashboard/status.json")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any source disagrees with another")
    a = ap.parse_args()
    # An explicit --manuscript-ref overrides both, for measuring one branch.
    ref1 = a.manuscript_ref or a.book1_ref
    ref2 = a.manuscript_ref or a.book2_ref
    ref = ref2  # Book 2 owns the planning documents

    b1 = chapters(BOOK1, ref1)
    b2 = chapters(BOOK2, ref2)
    att, doc_passes = attestations(ref2)
    required, protocol_src = pass_protocol(ref2)

    drift: list[str] = []
    if doc_passes and required and doc_passes != required:
        drift.append(
            f"pass protocol disagrees: {protocol_src} says {required}, "
            f"CHAPTER_ATTESTATIONS.md says {doc_passes}")

    rows = []
    for c in b2:
        a_ = att.get(c["n"], {})
        rows.append({**c,
                     "status": a_.get("status", "DRAFTED — NOT ATTESTED"),
                     "target": a_.get("target"),
                     "passesRecorded": a_.get("passesRecorded", 0)})
        if c["n"] not in att:
            drift.append(f"ch{c['n']:02d} has prose but no entry in CHAPTER_ATTESTATIONS.md")
    for n in att:
        if not any(c["n"] == n for c in b2):
            drift.append(f"ch{n:02d} is attested but has no manuscript file")

    # Is there more of either book somewhere else?
    for label, book, used_words, used_ref in (
            ("book1", BOOK1, sum(c["words"] for c in b1), ref1),
            ("book2", BOOK2, sum(c["words"] for c in b2), ref2)):
        br, words = richest_branch(book)
        if words > used_words * 1.05:
            drift.append(
                f"{label}: {br} holds {words:,} words, "
                f"{words - used_words:,} more than the ref being reported "
                f"({used_ref or 'working tree'})")

    # Some of status.json is editorial and cannot be derived from the tree:
    # the epic list, the origin portfolio, the reader contract. Those are kept
    # exactly as written. Only the parts the repository can answer for itself
    # are replaced. A generator that flattened the curated sections would make
    # itself unusable the first time someone wanted to say something the tree
    # does not know.
    CURATED = ("loop", "portfolio", "origins", "readerContract")
    existing = {}
    if pathlib.Path(a.out).exists():
        try:
            existing = json.loads(pathlib.Path(a.out).read_text())
        except json.JSONDecodeError:
            drift.append(f"{a.out} was not valid JSON; curated sections lost")

    total = 34
    attested = sum(1 for r in rows if r["status"].startswith("ATTESTED"))
    status = {
        "generatedBy": "scripts/generate_status.py",
        "book1Ref": ref1 or "working tree",
        "book2Ref": ref2 or "working tree",
        "universe": {
            "title": "The Boundary Universe",
            "scope": "5 origin trilogies + discovery prequels + 10-book ensemble saga",
        },
        "protocol": {"passesRequired": required, "source": protocol_src},
        "book1": {
            "title": "The Ninth Standard",
            "chapters": len(b1),
            "words": sum(c["words"] for c in b1),
        },
        "book2": {
            "title": "The Twelfth Resonant",
            "chaptersTotal": total,
            "chaptersDrafted": len(rows),
            "chaptersAttested": attested,
            "words": sum(r["words"] for r in rows),
            "percentDrafted": round(100 * len(rows) / total),
            "percentAttested": round(100 * attested / total),
            "chapters": rows,
        },
        "drift": drift,
    }
    for key in CURATED:
        if key in existing:
            status[key] = existing[key]
    # universe.status is a human judgement ("DESIGN + O1 IN PRODUCTION").
    if isinstance(existing.get("universe"), dict) and "status" in existing["universe"]:
        status["universe"]["status"] = existing["universe"]["status"]

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=2) + "\n")

    b = status["book2"]
    print(f"book 1: {status['book1']['chapters']} chapters, {status['book1']['words']:,} words")
    print(f"book 2: {b['chaptersDrafted']}/{total} drafted ({b['percentDrafted']}%), "
          f"{b['chaptersAttested']} attested, {b['words']:,} words")
    print(f"protocol: {required} passes (per {protocol_src})")
    if drift:
        print(f"\nDRIFT ({len(drift)}):")
        for d in drift:
            print(f"  - {d}")
        if a.strict:
            return 1
    else:
        print("no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
