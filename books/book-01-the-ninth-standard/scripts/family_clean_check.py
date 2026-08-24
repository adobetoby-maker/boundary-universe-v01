#!/usr/bin/env python3
"""Simple family-clean lint for manuscript Markdown.

This is intentionally conservative and supplements human review.
Run from Book 1 root:
  python scripts/family_clean_check.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"

# Add terms here if they appear accidentally. Keep entries lowercase.
FORBIDDEN = {
    "damn", "damned", "hell", "crap", "bastard", "ass", "asshole",
    "shit", "bullshit", "fuck", "fucking", "motherfucker", "bitch",
}

# Phrases/gestures that may be family-inappropriate even when token lint misses them.
FORBIDDEN_PHRASES = {
    "gave him the finger",
    "gave her the finger",
    "gave him a finger",
    "gave her a finger",
}


def scan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    findings: list[str] = []
    for word in sorted(FORBIDDEN):
        if re.search(rf"\b{re.escape(word)}\b", lower):
            findings.append(word)
    for phrase in sorted(FORBIDDEN_PHRASES):
        if phrase in lower:
            findings.append(phrase)
    return findings


def main() -> None:
    failed = False
    for path in sorted(MANUSCRIPT.glob("chapter-*.md")):
        findings = scan(path)
        if findings:
            failed = True
            print(f"FAIL {path.name}: {', '.join(findings)}")
        else:
            print(f"PASS {path.name}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
