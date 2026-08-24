#!/usr/bin/env python3
"""Generate Google SSML and ElevenLabs-ready scripts from canonical Markdown.

Usage:
  python audio/render_audio.py manuscript/chapter-01-the-kid-in-room-four.md

Outputs are written beneath audio/generated/{ssml,elevenlabs}/.
The manuscript remains the sole prose source of truth.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio"

SPECIAL_PAUSES = {
    "REDEFINE": 650,
    "000": 600,
    "SESSION TERMINATED": 500,
    "SECTION COMPLETE": 350,
}

ELEVEN_CUES = {
    "REDEFINE": "[long pause]",
    "000": "[short pause]",
    "SESSION TERMINATED": "[controlled, unsettled]",
}


def clean_markdown(text: str) -> str:
    text = re.sub(r"^#.+$", "", text, flags=re.MULTILINE)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"\n---\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def ssml(text: str) -> str:
    out = ["<speak>"]
    for p in paragraphs(text):
        if p in SPECIAL_PAUSES:
            out.append(f'  <break time="{SPECIAL_PAUSES[p]}ms"/>')
            out.append(f"  <p>{html.escape(p)}</p>")
            out.append('  <break time="250ms"/>')
            continue
        # Avoid over-directing normal prose.
        out.append(f"  <p>{html.escape(p)}</p>")
    out.append("</speak>")
    return "\n".join(out) + "\n"


def eleven(text: str) -> str:
    out: list[str] = []
    for p in paragraphs(text):
        cue = ELEVEN_CUES.get(p)
        if cue:
            out.append(cue)
        out.append(p)
        out.append("")
    return "\n".join(out).strip() + "\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Pass exactly one manuscript Markdown path.")
    src = Path(sys.argv[1])
    if not src.is_absolute():
        src = (ROOT / src).resolve()
    if not src.exists():
        raise SystemExit(f"Missing manuscript: {src}")

    cleaned = clean_markdown(src.read_text(encoding="utf-8"))
    stem = src.stem
    ssml_dir = AUDIO / "generated" / "ssml"
    eleven_dir = AUDIO / "generated" / "elevenlabs"
    ssml_dir.mkdir(parents=True, exist_ok=True)
    eleven_dir.mkdir(parents=True, exist_ok=True)
    (ssml_dir / f"{stem}.ssml").write_text(ssml(cleaned), encoding="utf-8")
    (eleven_dir / f"{stem}.txt").write_text(eleven(cleaned), encoding="utf-8")
    print(f"Rendered {stem}")


if __name__ == "__main__":
    main()
