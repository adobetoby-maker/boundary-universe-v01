#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "books" / "book-01-the-ninth-standard" / "manuscript"
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)

rows = []
total = 0
for path in sorted(MANUSCRIPT.glob("chapter-*.md")):
    text = path.read_text(encoding="utf-8")
    count = len(WORD_RE.findall(text))
    rows.append((path.name, count))
    total += count

print("Book 1 — The Ninth Standard")
print("=" * 40)
for name, count in rows:
    print(f"{name:<58} {count:>7,}")
print("-" * 68)
print(f"TOTAL{'':<53} {total:>7,}")
print(f"Estimated audio @ 9,300 words/hour: {total / 9300:.2f} hours")
print(f"Gap to 187,000-word target: {187000 - total:+,}")
