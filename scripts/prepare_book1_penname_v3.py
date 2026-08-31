#!/usr/bin/env python3
"""Prepare validated Penname V3.1 packets for The Ninth Standard rewrite."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK = REPO_ROOT / "books" / "book-01-the-ninth-standard"
WORK = BOOK / "penname-v3"
SOURCE = BOOK / "manuscript"
ARCHITECTURE = BOOK / "CHAPTER_ARCHITECTURE.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def architecture_cards() -> list[dict[str, object]]:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^## (\d+)\. (.+?)\n\*\*Target:\*\* ([\d,]+) words\n\n(.*?)(?=\n## \d+\.|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    cards = []
    for match in pattern.finditer(text):
        cards.append(
            {
                "number": int(match.group(1)),
                "title": match.group(2).strip(),
                "target": int(match.group(3).replace(",", "")),
                "summary": " ".join(match.group(4).strip().split()),
            }
        )
    if len(cards) != 33:
        raise RuntimeError(f"expected 33 architecture cards, found {len(cards)}")
    return cards


def source_files() -> list[Path]:
    files = sorted(SOURCE.glob("chapter-*.md"))
    if len(files) != 33:
        raise RuntimeError(f"expected 33 source chapters, found {len(files)}")
    return files


def chapter_modules(number: int) -> list[str]:
    modules = ["progression", "moral-choice"]
    if number in {6, 8, 11, 13, 14, 15, 21, 22, 25, 26, 29, 30, 31, 32}:
        modules.insert(0, "combat")
    if number in {1, 4, 5, 8, 9, 10, 11, 14, 15, 16, 21, 22, 33}:
        modules.append("litrpg")
    return modules


def packet_for(card: dict[str, object], source: Path, head: str) -> dict:
    number = int(card["number"])
    chapter_id = f"book1-ch{number:02d}"
    source_rel = source.relative_to(BOOK).as_posix()
    draft_rel = f"penname-v3/manuscript/{source.name}"
    prior = None
    if number > 1:
        prior_source = source_files()[number - 2]
        prior = f"penname-v3/manuscript/{prior_source.name}"

    context = [
        {"kind": "canon", "label": "Locked universe rules", "path": "penname-v3/context/CANON_RULES.md", "required": True},
        {"kind": "arc", "label": "Book and chapter architecture", "path": "CHAPTER_ARCHITECTURE.md", "required": True},
        {"kind": "state", "label": "Book One state ledger", "path": "STATE_LEDGER.md", "required": True},
        {"kind": "registry", "label": "Canonical name registry", "path": "penname-v3/context/NAME_REGISTRY.md", "required": True},
        {"kind": "canon", "label": "Book One bible", "path": "BOOK_BIBLE.md", "required": True},
        {"kind": "canon", "label": "Universe bible", "path": "penname-v3/context/UNIVERSE_BIBLE.md", "required": True},
        {"kind": "reference", "label": "Mystery and reveal ledger", "path": "CLUE_LEDGER.md", "required": True},
        {"kind": "reference", "label": "Rewrite production specification", "path": "penname-v3/PRODUCTION_SPEC.md", "required": True},
        {"kind": "reference", "label": "Frozen source chapter; preserve facts, not sentences", "path": source_rel, "required": True},
    ]
    if prior:
        context.append(
            {"kind": "previous_scene", "label": "Previous rewritten chapter seam", "path": prior, "required": True}
        )

    summary = str(card["summary"])
    return {
        "schema_version": "3.1",
        "scene_id": chapter_id,
        "project": "boundary-universe/the-ninth-standard/rewrite-1",
        "pen_name": "fantasy-author-a",
        "job": "draft",
        "revisions": {
            "input_commit": head,
            "canon": sha256(REPO_ROOT / "CANON_RULES.md"),
            "arc": sha256(ARCHITECTURE),
            "state": sha256(BOOK / "STATE_LEDGER.md"),
            "registry": sha256(REPO_ROOT / "canon" / "NAME_REGISTRY.md"),
        },
        "modules": chapter_modules(number),
        "pov": {
            "character": "Kade Mercer unless the locked chapter evidence explicitly assigns Mara or Sen",
            "mode": "close third person, past tense",
            "knowledge_boundary": [
                "Reveal only what the viewpoint character knows at this point in the locked reveal order.",
                "No villain viewpoint and no omniscient explanation of concealed motives.",
                "Treat registry role descriptions as naming aids, not story authority.",
            ],
        },
        "purpose": f"Freshly re-author Chapter {number}, {card['title']}. Locked chapter function: {summary}",
        "scene_shape": {
            "opening_state": "Preserve the incoming physical, relational, rank, and knowledge state established by the prior chapter and ledgers.",
            "pov_goal": f"Give the viewpoint character an immediate, concrete objective that delivers this chapter function: {summary}",
            "opposition": "Use the source chapter's causal obstacles and social pressures; make resistance active rather than summarized.",
            "turn": "Preserve the locked decisive reversal or discovery, but stage it freshly with visible cause and consequence.",
            "choice": "Make the viewpoint character choose under pressure; do not let power, coincidence, or an authority figure make the emotional decision for them.",
            "outcome": "Fulfill the architecture card and all plants/payoffs without spending a later reveal.",
            "closing_state": "Match the source chapter's durable state delta and end on changed pressure that pulls into the next chapter.",
        },
        "obligations": {
            "must_include": [
                summary,
                "Write a genuinely fresh chapter, not a line-by-line paraphrase or abbreviated recap.",
                "Preserve every durable fact, rank, relationship movement, clue, power cost, and chapter-end state required by the frozen evidence.",
                "Use Fantasy Author A voice: propulsive, emotionally grounded, rule-bound wonder, victories with receipts, and practical close-viewpoint attention.",
                "Pass family-clean and audio-readability requirements in the production specification.",
            ],
            "plants": ["Preserve all chapter-assigned plants in CLUE_LEDGER.md and the source chapter."],
            "payoffs": ["Deliver all chapter-assigned payoffs without advancing later-book answers."],
            "prohibited_outcomes": [
                "Do not change canon, reveal order, chapter outcome, rank arithmetic, or downstream Book Two facts.",
                "Do not make Kade effortlessly dominant or remove the physical and relational cost of Boundary use.",
                "Do not add profanity, explicit sexual material, lingering gore, or a new named character.",
                "Do not include drafting notes, reports, word counts, or metadata in manuscript prose.",
            ],
        },
        "invention_budget": {
            "allowed": [
                "Fresh sensory detail, physical business, clean humor, transitions, and dialogue consistent with established character voices.",
                "Unnamed background texture that does not create a continuity obligation.",
                "Scene-level staging improvements that preserve all locked causes and outcomes.",
            ],
            "approval_required": [],
            "forbidden": [
                "New named characters, powers, factions, relationships, backstory, rules, ranks, clues, or future answers.",
                "Changes to a locked ledger, architecture card, or source manuscript.",
            ],
        },
        "context_files": context,
        "verified_findings": [],
        "exceptions": [],
        "output": {
            "draft_path": draft_rel,
            "report_path": f"penname-v3/reports/current/{chapter_id}-author.json",
            "editor_report_path": f"penname-v3/reports/current/{chapter_id}-editor.json",
            "verifier_report_path": f"penname-v3/reports/current/{chapter_id}-verifier.json",
            "target_words": int(card["target"]),
            "tolerance_percent": 12,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace existing packets and state")
    args = parser.parse_args()

    packets = WORK / "packets"
    context_dir = WORK / "context"
    manuscript = WORK / "manuscript"
    reports = WORK / "reports" / "current"
    runs = WORK / "runs"
    prompts = WORK / "prompts"
    for directory in (packets, context_dir, manuscript, reports, runs, prompts):
        directory.mkdir(parents=True, exist_ok=True)

    snapshots = {
        REPO_ROOT / "CANON_RULES.md": context_dir / "CANON_RULES.md",
        REPO_ROOT / "canon" / "UNIVERSE_BIBLE.md": context_dir / "UNIVERSE_BIBLE.md",
        REPO_ROOT / "canon" / "NAME_REGISTRY.md": context_dir / "NAME_REGISTRY.md",
    }
    for source_path, destination in snapshots.items():
        shutil.copyfile(source_path, destination)

    head = git_head()
    for card, source in zip(architecture_cards(), source_files(), strict=True):
        destination = packets / f"chapter-{int(card['number']):02d}.json"
        if destination.exists() and not args.force:
            continue
        destination.write_text(
            json.dumps(packet_for(card, source, head), indent=2) + "\n", encoding="utf-8"
        )

    state_path = WORK / "loop-state.json"
    if args.force or not state_path.exists():
        state = {
            "schema_version": "3.1",
            "loop_id": "the-ninth-standard-rewrite-1",
            "project": "boundary-universe/the-ninth-standard/rewrite-1",
            "pen_name": "fantasy-author-a",
            "scope": "book",
            "phase": "PROJECT_READY",
            "max_repair_cycles": 3,
            "repair_cycle": 0,
            "scenes_total": 33,
            "scenes_closed": 0,
            "active_scene_id": None,
            "last_finding_fingerprint": None,
            "repeat_count": 0,
            "blocker": None,
            "repair_origin": None,
            "human_gate": None,
            "history": [],
        }
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(f"prepared 33 chapter packets under {WORK.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
