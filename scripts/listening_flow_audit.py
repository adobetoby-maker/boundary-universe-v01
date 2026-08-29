#!/usr/bin/env python3
"""Audit Markdown fiction manuscripts for one-hearing comprehension risks.

This is a diagnostic, not an automatic prose rewriter. It ranks chapters and
surfaces candidate sentences for human editorial review.
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

BOOKS = {
    "The Ninth Standard": ROOT / "books/book-01-the-ninth-standard/manuscript",
    "Contact Zero": ROOT / "books/book-01-contact-zero/manuscript",
}

TECH_TERMS = {
    "acceleration", "amplitude", "anchor", "architecture", "boundary",
    "calibration", "coherence", "conduit", "constraint", "control",
    "correction", "coupling", "current", "damping", "differential",
    "field", "force", "frequency", "geometry", "gradient", "index",
    "input", "interface", "latency", "load", "manifold", "mass",
    "model", "momentum", "notation", "operator", "output", "pressure",
    "probability", "recursive", "redirection", "resonance", "sensor",
    "sink", "source", "stability", "state", "storage", "structural",
    "tensor", "thermal", "telemetry", "transfer", "variance", "vector",
}

ABSTRACT_SUFFIXES = (
    "tion", "sion", "ment", "ness", "ity", "ance", "ence", "ism", "ship",
)

PLAIN_LANGUAGE_MARKERS = (
    "imagine", "picture", "like a", "like an", "as if", "in other words",
    "plain language", "ordinary version", "means", "basically", "the point is",
)

TIC_PATTERNS = {
    "there_it_was": re.compile(r"\bthere it was\b", re.I),
    "that_was_true": re.compile(r"\bthat was true\b", re.I),
    "also_true": re.compile(r"\balso true\b", re.I),
    "not_because": re.compile(r"^\s*not because\b", re.I),
    "that_sounded": re.compile(r"\bthat sounded\b", re.I),
    "he_noticed": re.compile(r"\bhe noticed\b", re.I),
    "kade_noticed": re.compile(r"\bkade noticed\b", re.I),
}

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MARKDOWN_EMPH_RE = re.compile(r"[*_`]+")
DISPLAY_LINE_RE = re.compile(r"^\s*(#{1,6}\s|---\s*$)")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"”’']+)?\s+(?=[A-Z0-9\"“‘*_])")


@dataclass
class SentenceRisk:
    line: int
    words: int
    tech_terms: int
    abstract_nouns: int
    score: float
    text: str


@dataclass
class ChapterMetrics:
    book: str
    chapter: str
    path: str
    words: int
    sentences: int
    paragraphs: int
    dialogue_ratio: float
    mean_sentence_words: float
    median_sentence_words: float
    p95_sentence_words: float
    long_35: int
    long_45: int
    fragments_4: int
    fragment_bursts: int
    tech_terms: int
    tech_density_per_1000: float
    abstract_nouns: int
    abstract_density_per_1000: float
    technical_paragraphs_without_reset: int
    negative_ladders: int
    tic_hits: dict[str, int]
    auditory_load_score: float
    riskiest_sentences: list[SentenceRisk]


def percentile(values: list[int], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    low = math.floor(index)
    high = math.ceil(index)
    if low == high:
        return float(ordered[low])
    fraction = index - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def clean_markdown(raw: str) -> str:
    raw = HTML_COMMENT_RE.sub("", raw)
    kept: list[str] = []
    for line in raw.splitlines():
        if DISPLAY_LINE_RE.match(line):
            continue
        # Keep displayed text because it must also work in audio, but remove markup.
        kept.append(MARKDOWN_EMPH_RE.sub("", line))
    return "\n".join(kept).strip()


def split_paragraphs(clean: str) -> list[tuple[int, str]]:
    lines = clean.splitlines()
    paragraphs: list[tuple[int, str]] = []
    buffer: list[str] = []
    start = 1
    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            if buffer:
                paragraphs.append((start, " ".join(x.strip() for x in buffer)))
                buffer = []
            continue
        if not buffer:
            start = lineno
        buffer.append(line)
    if buffer:
        paragraphs.append((start, " ".join(x.strip() for x in buffer)))
    return paragraphs


def split_sentences(paragraph: str) -> list[str]:
    parts = SENTENCE_RE.split(paragraph.strip())
    return [part.strip() for part in parts if part.strip()]


def term_count(tokens: Iterable[str]) -> int:
    return sum(1 for token in tokens if token.lower() in TECH_TERMS)


def abstract_count(tokens: Iterable[str]) -> int:
    count = 0
    for token in tokens:
        lower = token.lower()
        if len(lower) > 6 and lower.endswith(ABSTRACT_SUFFIXES):
            count += 1
    return count


def has_plain_reset(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in PLAIN_LANGUAGE_MARKERS)


def is_dialogue(paragraph: str) -> bool:
    stripped = paragraph.lstrip()
    return stripped.startswith(('"', '“', "'", '‘'))


def negative_ladder_count(paragraphs: list[tuple[int, str]]) -> int:
    count = 0
    run = 0
    for _, paragraph in paragraphs:
        starts = paragraph.lstrip().lower()
        if starts.startswith(("not ", "no ", "never ", "without ")):
            run += 1
            if run == 3:
                count += 1
        else:
            run = 0
    return count


def fragment_burst_count(sentence_lengths: list[int]) -> int:
    count = 0
    run = 0
    for length in sentence_lengths:
        if 0 < length <= 4:
            run += 1
            if run == 4:
                count += 1
        else:
            run = 0
    return count


def audit_file(book: str, path: Path) -> ChapterMetrics:
    raw = path.read_text(encoding="utf-8")
    clean = clean_markdown(raw)
    paragraphs = split_paragraphs(clean)

    all_tokens = words(clean)
    sentence_records: list[SentenceRisk] = []
    sentence_lengths: list[int] = []
    technical_without_reset = 0
    dialogue_words = 0

    for line, paragraph in paragraphs:
        p_tokens = words(paragraph)
        if is_dialogue(paragraph):
            dialogue_words += len(p_tokens)
        p_tech = term_count(p_tokens)
        if p_tech >= 4 and not has_plain_reset(paragraph):
            technical_without_reset += 1

        for sentence in split_sentences(paragraph):
            s_tokens = words(sentence)
            length = len(s_tokens)
            if not length:
                continue
            sentence_lengths.append(length)
            tech = term_count(s_tokens)
            abstract = abstract_count(s_tokens)
            # Editorial triage score, intentionally simple and transparent.
            score = (
                max(0, length - 28) * 0.22
                + max(0, length - 40) * 0.35
                + max(0, tech - 2) * 1.4
                + max(0, abstract - 2) * 0.8
                + (1.2 if length >= 30 and tech >= 3 and not has_plain_reset(sentence) else 0)
            )
            if score > 0:
                sentence_records.append(
                    SentenceRisk(
                        line=line,
                        words=length,
                        tech_terms=tech,
                        abstract_nouns=abstract,
                        score=round(score, 2),
                        text=sentence[:500],
                    )
                )

    word_count = len(all_tokens)
    tech_total = term_count(all_tokens)
    abstract_total = abstract_count(all_tokens)
    tic_hits = {
        name: len(pattern.findall(clean)) for name, pattern in TIC_PATTERNS.items()
    }

    long_35 = sum(length >= 35 for length in sentence_lengths)
    long_45 = sum(length >= 45 for length in sentence_lengths)
    fragments = sum(0 < length <= 4 for length in sentence_lengths)
    bursts = fragment_burst_count(sentence_lengths)
    neg_ladders = negative_ladder_count(paragraphs)
    p95 = percentile(sentence_lengths, 0.95)

    # Weight factors associated with audiobook working-memory load. The score
    # ranks chapters against one another; it is not a quality grade.
    auditory_load_score = (
        p95 * 0.45
        + (long_35 / max(1, len(sentence_lengths))) * 120
        + (long_45 / max(1, len(sentence_lengths))) * 180
        + (tech_total / max(1, word_count)) * 1800
        + (technical_without_reset / max(1, len(paragraphs))) * 100
        + bursts * 0.8
        + neg_ladders * 1.2
    )

    return ChapterMetrics(
        book=book,
        chapter=path.stem,
        path=str(path.relative_to(ROOT)),
        words=word_count,
        sentences=len(sentence_lengths),
        paragraphs=len(paragraphs),
        dialogue_ratio=round(dialogue_words / max(1, word_count), 4),
        mean_sentence_words=round(statistics.mean(sentence_lengths), 2)
        if sentence_lengths
        else 0.0,
        median_sentence_words=round(statistics.median(sentence_lengths), 2)
        if sentence_lengths
        else 0.0,
        p95_sentence_words=round(p95, 2),
        long_35=long_35,
        long_45=long_45,
        fragments_4=fragments,
        fragment_bursts=bursts,
        tech_terms=tech_total,
        tech_density_per_1000=round(tech_total * 1000 / max(1, word_count), 2),
        abstract_nouns=abstract_total,
        abstract_density_per_1000=round(
            abstract_total * 1000 / max(1, word_count), 2
        ),
        technical_paragraphs_without_reset=technical_without_reset,
        negative_ladders=neg_ladders,
        tic_hits=tic_hits,
        auditory_load_score=round(auditory_load_score, 2),
        riskiest_sentences=sorted(
            sentence_records, key=lambda item: item.score, reverse=True
        )[:12],
    )


def aggregate(metrics: list[ChapterMetrics]) -> dict[str, object]:
    by_book: dict[str, list[ChapterMetrics]] = {}
    for item in metrics:
        by_book.setdefault(item.book, []).append(item)

    result: dict[str, object] = {}
    for book, rows in by_book.items():
        result[book] = {
            "chapters": len(rows),
            "words": sum(row.words for row in rows),
            "mean_auditory_load": round(
                statistics.mean(row.auditory_load_score for row in rows), 2
            ),
            "mean_p95_sentence_words": round(
                statistics.mean(row.p95_sentence_words for row in rows), 2
            ),
            "long_45": sum(row.long_45 for row in rows),
            "technical_paragraphs_without_reset": sum(
                row.technical_paragraphs_without_reset for row in rows
            ),
            "fragment_bursts": sum(row.fragment_bursts for row in rows),
            "tic_hits": dict(
                sum((Counter(row.tic_hits) for row in rows), Counter())
            ),
        }
    return result


def markdown_report(metrics: list[ChapterMetrics], aggregates: dict[str, object]) -> str:
    lines = [
        "# Listening-Flow Audit",
        "",
        "> Diagnostic only. High score means higher one-hearing working-memory load, not lower literary quality.",
        "",
        "## Cross-book summary",
        "",
        "| Book | Chapters | Words | Mean load | Mean sentence P95 | Sentences 45+ | Technical paragraphs without plain reset | Fragment bursts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for book, data in aggregates.items():
        assert isinstance(data, dict)
        lines.append(
            f"| {book} | {data['chapters']} | {data['words']:,} | {data['mean_auditory_load']} | "
            f"{data['mean_p95_sentence_words']} | {data['long_45']} | "
            f"{data['technical_paragraphs_without_reset']} | {data['fragment_bursts']} |"
        )

    lines.extend([
        "",
        "## Highest-load chapters",
        "",
        "| Rank | Book | Chapter | Words | Load | P95 | 45+ | Tech/1k | Technical paragraphs without reset | Fragment bursts |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    ranked = sorted(metrics, key=lambda row: row.auditory_load_score, reverse=True)
    for rank, row in enumerate(ranked[:20], start=1):
        lines.append(
            f"| {rank} | {row.book} | `{row.chapter}` | {row.words:,} | {row.auditory_load_score} | "
            f"{row.p95_sentence_words} | {row.long_45} | {row.tech_density_per_1000} | "
            f"{row.technical_paragraphs_without_reset} | {row.fragment_bursts} |"
        )

    lines.extend(["", "## Candidate sentences for editorial review", ""])
    for row in ranked[:12]:
        if not row.riskiest_sentences:
            continue
        lines.append(f"### {row.book} — `{row.chapter}`")
        lines.append("")
        for item in row.riskiest_sentences[:6]:
            excerpt = item.text.replace("\n", " ")
            lines.append(
                f"- **Line ~{item.line}; {item.words} words; score {item.score}:** {excerpt}"
            )
        lines.append("")

    lines.extend([
        "## Interpretation guardrails",
        "",
        "- Long sentences are candidates, not automatic errors.",
        "- Short fragments are part of the established voice; only repeated bursts are flagged.",
        "- Technical vocabulary is retained when the listener receives a concrete model first.",
        "- Dialogue-heavy chapters often tolerate more exposition because character voice provides resets.",
        "- The final decision belongs to an editorial read and an actual audio listen.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    metrics: list[ChapterMetrics] = []
    for book, directory in BOOKS.items():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("chapter-*.md")):
            metrics.append(audit_file(book, path))

    aggregates = aggregate(metrics)
    payload = {
        "aggregates": aggregates,
        "chapters": [asdict(item) for item in metrics],
    }

    out_dir = ROOT / "build/listening-flow-audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "listening-flow-audit.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    (out_dir / "listening-flow-audit.md").write_text(
        markdown_report(metrics, aggregates), encoding="utf-8"
    )

    print(f"Audited {len(metrics)} chapters")
    for book, data in aggregates.items():
        print(f"{book}: {data}")


if __name__ == "__main__":
    main()
