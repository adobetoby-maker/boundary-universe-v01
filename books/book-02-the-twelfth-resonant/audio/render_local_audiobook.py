#!/usr/bin/env python3
"""Render Book 2 as a chaptered local proof/listening M4B.

This is deliberately a local fallback render, not a replacement for the
locked ElevenLabs Holden production voice used by Book 1. It sends no
manuscript text to a network service.

Requires macOS ``say``, ffmpeg and ffprobe.

Example:
  python3 audio/render_local_audiobook.py \
    --output /path/to/The-Twelfth-Resonant.local-reed.m4b
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


BOOK = "The Twelfth Resonant"
VOICE = "Reed (English (US))"
RATE = 180
BITRATE = "64k"
GAIN_DB = -2.5
ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"

NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
    12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
    16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen",
    20: "Twenty", 21: "Twenty-One", 22: "Twenty-Two",
    23: "Twenty-Three", 24: "Twenty-Four", 25: "Twenty-Five",
    26: "Twenty-Six", 27: "Twenty-Seven", 28: "Twenty-Eight",
    29: "Twenty-Nine", 30: "Thirty", 31: "Thirty-One",
    32: "Thirty-Two", 33: "Thirty-Three", 34: "Thirty-Four",
}

PRONUNCIATIONS = {
    "Asterion": "as-teer-ee-on",
    "Kiyomizu": "kee-yoh-mee-zoo",
    "Kisiwa": "kee-see-wah",
    "Vahana": "vah-huh-nuh",
    "Aya": "eye-uh",
    "Mara": "mah-ruh",
    "Sera": "sair-uh",
    "Imani": "ee-mah-nee",
    "Mwangi": "mwahn-gee",
    "Mori": "mor-ee",
    "Vey": "vay",
}


@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
    path: Path


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def capture(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def chapters() -> list[Chapter]:
    found: list[Chapter] = []
    for path in MANUSCRIPT.glob("chapter-*.md"):
        first = path.read_text(encoding="utf-8").splitlines()[0]
        match = re.fullmatch(r"# Chapter (\d+) — (.+)", first.strip())
        if not match:
            raise SystemExit(f"Unrecognized chapter heading: {path}: {first!r}")
        found.append(Chapter(int(match.group(1)), match.group(2), path))
    found.sort(key=lambda chapter: chapter.number)
    expected = list(range(1, 35))
    actual = [chapter.number for chapter in found]
    if actual != expected:
        raise SystemExit(f"Expected chapters 1–34, found {actual}")
    return found


def countdown(match: re.Match[str]) -> str:
    days, hours, minutes, seconds = (int(value) for value in match.groups())
    return (
        f"zero zero. {days} days. {hours} hours. "
        f"{minutes} minutes. {seconds} seconds"
    )


def pronunciation_aliases(text: str) -> str:
    for written, spoken in PRONUNCIATIONS.items():
        text = re.sub(rf"\b{re.escape(written)}\b", spoken, text)
    return text


def pause_for(paragraph: str) -> int:
    stripped = paragraph.strip()
    if stripped.startswith(("“", '"', "‘", "'")):
        return 260
    words = len(stripped.split())
    if words <= 4:
        return 480
    if words <= 12:
        return 380
    return 300


def prepare(chapter: Chapter) -> str:
    text = chapter.path.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(
        r"^# Chapter \d+ — .+$",
        f"Chapter {NUMBER_WORDS[chapter.number]}. {chapter.title}.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", "[[slnc 1250]]", text)
    text = text.replace("⸻", "[[slnc 1250]]")
    text = re.sub(r"\b00:(\d{3}):(\d{2}):(\d{2}):(\d{2})\b", countdown, text)
    text = re.sub(r"#(?=\d)", "rank ", text)
    text = re.sub(r"\bStandard IX\b", "Standard Nine", text)
    text = re.sub(r"\bIX\?", "Nine?", text)
    text = re.sub(r"\bVIII\b", "Eight", text)
    text = re.sub(r"\bM-Null\b", "M Null", text)
    text = re.sub(r"\bR-3\b", "R three", text)
    text = re.sub(r"\bSEC\b", "seconds", text)
    text = text.replace("→", " to ").replace("×", " by ").replace("±", " plus or minus ")
    text = text.replace("_", " ").replace("|", " ")
    text = pronunciation_aliases(text)
    text = re.sub(r"[ \t]+", " ", text)

    paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
        if not paragraph:
            continue
        if paragraph == "[[slnc 1250]]":
            paragraphs.append(paragraph)
            continue
        paragraphs.append(paragraph)
        paragraphs.append(f"[[slnc {pause_for(paragraph)}]]")

    prepared = "\n".join(paragraphs).strip() + "\n"
    if chapter.number == 1:
        prepared = f"{BOOK}.\n[[slnc 1500]]\n{prepared}"
    audit_prepared(chapter, prepared)
    return prepared


def audit_prepared(chapter: Chapter, text: str) -> None:
    checks = {
        "markdown heading": r"(?m)^#{1,6}\s",
        "markdown bold": r"\*\*",
        "markdown code": r"`",
        "markdown link": r"\[[^\]]+\]\([^)]+\)",
        "raw full countdown": r"\b00:\d{3}:\d{2}:\d{2}:\d{2}\b",
        "retired name": r"\b(?:Neema|Owen Park|Jun Park|Dr\. Venn)\b",
    }
    failures = [name for name, pattern in checks.items() if re.search(pattern, text)]
    unknown_commands = [
        command for command in re.findall(r"\[\[([^\]]+)\]\]", text)
        if not re.fullmatch(r"slnc \d+", command)
    ]
    if unknown_commands:
        failures.append(f"unknown speech commands: {unknown_commands[:3]}")
    if failures:
        raise SystemExit(f"Prepared-text audit failed for Chapter {chapter.number}: {failures}")


def duration(path: Path) -> float:
    return float(capture([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ]))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metadata(chapter_files: list[tuple[Chapter, Path]], path: Path) -> None:
    start = 0
    rows = [
        ";FFMETADATA1",
        f"title={BOOK}",
        "album=The Boundary Universe",
        "artist=Boundary Universe",
        "comment=Local proof/listening render; Reed English US macOS voice",
    ]
    for chapter, audio in chapter_files:
        end = start + round(duration(audio) * 1000)
        rows.extend([
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={start}",
            f"END={end}",
            f"title=Chapter {chapter.number} — {chapter.title}",
        ])
        start = end
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--voice", default=VOICE)
    parser.add_argument("--rate", type=int, default=RATE)
    parser.add_argument("--bitrate", default=BITRATE)
    parser.add_argument("--gain-db", type=float, default=GAIN_DB)
    parser.add_argument("--prepared-dir", type=Path)
    args = parser.parse_args()

    if not Path("/usr/bin/say").exists():
        raise SystemExit("This local render requires macOS /usr/bin/say")
    for tool in ("ffmpeg", "ffprobe"):
        if not capture(["sh", "-c", f"command -v {tool}"]):
            raise SystemExit(f"Missing required tool: {tool}")

    source_chapters = chapters()
    args.output = args.output.expanduser().resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.prepared_dir:
        args.prepared_dir = args.prepared_dir.expanduser().resolve()
        args.prepared_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="book2-audio-") as temp_name:
        temp = Path(temp_name)
        rendered: list[tuple[Chapter, Path]] = []

        for chapter in source_chapters:
            prepared = prepare(chapter)
            prepared_path = temp / f"ch{chapter.number:02d}.txt"
            prepared_path.write_text(prepared, encoding="utf-8")
            if args.prepared_dir:
                (args.prepared_dir / prepared_path.name).write_text(prepared, encoding="utf-8")

            aiff = temp / f"ch{chapter.number:02d}.aiff"
            m4a = temp / f"ch{chapter.number:02d}.m4a"
            print(f"Chapter {chapter.number:02d}: {chapter.title}", flush=True)
            run([
                "/usr/bin/say", "-v", args.voice, "-r", str(args.rate),
                "-f", str(prepared_path), "-o", str(aiff),
            ])
            run([
                "ffmpeg", "-y", "-v", "error", "-i", str(aiff),
                "-vn", "-ac", "1", "-ar", "44100", "-c:a", "aac",
                "-b:a", args.bitrate, "-af", f"volume={args.gain_db}dB",
                "-metadata", f"title=Chapter {chapter.number} — {chapter.title}",
                str(m4a),
            ])
            aiff.unlink()
            rendered.append((chapter, m4a))
            seconds = duration(m4a)
            print(f"  {seconds / 60:.1f} min", flush=True)

        concat = temp / "concat.txt"
        concat.write_text(
            "".join(f"file '{audio.as_posix()}'\n" for _, audio in rendered),
            encoding="utf-8",
        )
        ffmeta = temp / "chapters.ffmeta"
        metadata(rendered, ffmeta)
        run([
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
            "-i", str(concat), "-i", str(ffmeta), "-map", "0:a", "-map_metadata", "1",
            "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart",
            str(args.output),
        ])

    seconds = duration(args.output)
    print(f"OUTPUT={args.output}")
    print(f"DURATION_SEC={seconds:.3f}")
    print(f"BYTES={args.output.stat().st_size}")
    print(f"SHA256={sha256(args.output)}")


if __name__ == "__main__":
    main()
