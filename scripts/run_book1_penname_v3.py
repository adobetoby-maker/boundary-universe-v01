#!/usr/bin/env python3
"""Run Fable-author/Sol-editor completion loops for The Ninth Standard."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK = REPO_ROOT / "books" / "book-01-the-ninth-standard"
WORK = BOOK / "penname-v3"
STATE = WORK / "loop-state.json"
DEFAULT_PENNAME = Path(
    "/Users/adobetoby/Documents/Codex/2026-08-30/i-wa/work/penname/pennamecodexv3"
)


class LoopError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def claude_schema(path: Path) -> dict:
    """Remove annotation metadata unsupported by Claude CLI's schema adapter."""
    schema = load_json(path)
    for key in ("$schema", "$id", "title"):
        schema.pop(key, None)
    return schema


def codex_schema_node(value: object) -> object:
    """Normalize a Penname schema for the stricter OpenAI response transport."""
    if isinstance(value, list):
        return [codex_schema_node(item) for item in value]
    if not isinstance(value, dict):
        return value
    normalized = {
        ("anyOf" if key == "oneOf" else key): codex_schema_node(item)
        for key, item in value.items()
        if key not in {"$schema", "$id", "title"}
    }
    if "const" in normalized and "type" not in normalized:
        constant = normalized["const"]
        if isinstance(constant, str):
            normalized["type"] = "string"
        elif isinstance(constant, bool):
            normalized["type"] = "boolean"
        elif isinstance(constant, int):
            normalized["type"] = "integer"
        elif constant is None:
            normalized["type"] = "null"
    return normalized


def run_id(scene_id: str, seat: str, cycle: int) -> str:
    return f"{scene_id}-{seat}-c{cycle}-{int(time.time())}"


def normalize_report_word_count(report_path: Path, actual: int) -> dict:
    report = load_json(report_path)
    reported = report.get("word_count")
    if reported != actual:
        report["word_count"] = actual
        note = f"Adapter normalized whitespace word count from {reported} to {actual}."
        if note not in report.get("deviations", []):
            report.setdefault("deviations", []).append(note)
        write_json(report_path, report)
    return report


def synthesize_interrupted_author_report(
    packet_path: Path, report_path: Path, actual: int, cycle: int, reason: str
) -> dict:
    """Create transparent navigation metadata when prose survives a seat interruption."""
    packet = load_json(packet_path)
    obligations = []
    for obligation in (
        packet["obligations"]["must_include"]
        + packet["obligations"]["plants"]
        + packet["obligations"]["payoffs"]
    ):
        obligations.append(
            {
                "obligation": obligation,
                "status": "NOT_APPLICABLE",
                "evidence": (
                    "Author self-report was interrupted after prose write; Sol editor must "
                    "verify this obligation directly from the manuscript."
                ),
            }
        )
    report = {
        "schema_version": "3.1",
        "run_id": run_id(packet["scene_id"], "author-interrupted", cycle),
        "scene_id": packet["scene_id"],
        "status": "DONE",
        "draft_path": packet["output"]["draft_path"],
        "word_count": actual,
        "obligations": obligations,
        "inventions": [],
        "state_change_proposals": [],
        "deviations": [reason],
        "blockers": [],
    }
    write_json(report_path, report)
    return report


class Runner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.penname = args.penname_root.resolve()
        self.scripts = self.penname / "scripts"
        self.contracts = self.penname / "contracts"
        required = [
            self.scripts / "build_prompt.py",
            self.scripts / "advance_loop.py",
            self.scripts / "validate.py",
            self.contracts / "author-report.schema.json",
            self.contracts / "editor-report.schema.json",
            self.contracts / "verification-report.schema.json",
        ]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise LoopError("Penname V3 is incomplete:\n" + "\n".join(missing))
        if not STATE.exists():
            raise LoopError("run prepare_book1_penname_v3.py before the loop")

    def command(
        self,
        argv: list[str],
        *,
        stdin: str | None = None,
        cwd: Path = BOOK,
        log_path: Path | None = None,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            argv,
            input=stdin,
            text=True,
            cwd=cwd,
            capture_output=True,
            timeout=timeout or self.args.timeout,
            env={**os.environ, "NO_COLOR": "1"},
        )
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"COMMAND: {' '.join(argv)}\nEXIT: {result.returncode}\n\n"
                f"STDOUT\n{result.stdout}\n\nSTDERR\n{result.stderr}\n",
                encoding="utf-8",
            )
        if result.returncode:
            tail = (result.stderr or result.stdout)[-4000:]
            raise LoopError(f"command failed ({result.returncode}): {' '.join(argv)}\n{tail}")
        return result

    def validate(self, schema: str, artifact: Path) -> None:
        self.command(
            [
                sys.executable,
                str(self.scripts / "validate.py"),
                str(self.contracts / schema),
                str(artifact),
            ],
            timeout=120,
        )

    def advance(
        self,
        event: str,
        *,
        scene_id: str | None = None,
        fingerprint: str | None = None,
        note: str = "",
    ) -> None:
        argv = [
            sys.executable,
            str(self.scripts / "advance_loop.py"),
            str(STATE),
            "--event",
            event,
            "--note",
            note,
        ]
        if scene_id:
            argv.extend(["--scene-id", scene_id])
        if fingerprint:
            argv.extend(["--finding-fingerprint", fingerprint])
        result = self.command(argv, timeout=120)
        print(result.stdout.strip(), flush=True)

    def compile_prompt(self, role: str, packet: Path, cycle: int, report: Path | None = None) -> str:
        compile_packet = packet
        if role == "author":
            author_packet = load_json(packet)
            author_packet["context_files"] = [
                item
                for item in author_packet["context_files"]
                if item["label"] != "Frozen source chapter; preserve facts, not sentences"
            ]
            author_packet_dir = WORK / "author-packets"
            author_packet_dir.mkdir(parents=True, exist_ok=True)
            compile_packet = author_packet_dir / packet.name
            write_json(compile_packet, author_packet)
        argv = [
            sys.executable,
            str(self.scripts / "build_prompt.py"),
            role,
            "--packet",
            str(compile_packet),
            "--root",
            str(BOOK),
        ]
        if report:
            argv.extend(["--report", report.relative_to(BOOK).as_posix()])
        result = self.command(argv, timeout=180)
        digest = hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
        scene_id = load_json(packet)["scene_id"]
        hash_path = WORK / "prompts" / f"{scene_id}-{role}-c{cycle}.sha256"
        hash_path.write_text(digest + "\n", encoding="utf-8")
        return result.stdout

    def archive(self, packet: dict, cycle: int) -> Path:
        destination = WORK / "runs" / packet["scene_id"] / f"cycle-{cycle}"
        destination.mkdir(parents=True, exist_ok=True)
        for key in ("report_path", "editor_report_path", "verifier_report_path"):
            source = BOOK / packet["output"][key]
            if source.exists():
                shutil.copy2(source, destination / source.name)
        draft = BOOK / packet["output"]["draft_path"]
        if draft.exists():
            shutil.copy2(draft, destination / draft.name)
        return destination

    def author(self, packet_path: Path, cycle: int, repair: bool = False) -> dict:
        packet = load_json(packet_path)
        scene_id = packet["scene_id"]
        draft = BOOK / packet["output"]["draft_path"]
        report = BOOK / packet["output"]["report_path"]
        if draft.exists() and not report.exists() and not repair:
            return self.recover_author_report(packet_path, cycle)
        prompt = self.compile_prompt("author", packet_path, cycle)
        prompt += (
            "\n\n---\n\n# ADAPTER TRANSPORT\n\n"
            "Write only the manuscript with file tools. Return the author report as your "
            "final structured JSON response; the orchestrator will write it to the declared "
            "report path. Do not use a file tool for the report.\n"
        )
        log = WORK / "runs" / scene_id / f"cycle-{cycle}" / "fable-author.log"
        print(f"[{scene_id}] Fable 5 author cycle {cycle}", flush=True)
        try:
            result = self.command(
                [
                "claude",
                "--print",
                "--model",
                self.args.author_model,
                "--effort",
                "high",
                "--no-session-persistence",
                "--safe-mode",
                "--restricted",
                "--permission-mode",
                "acceptEdits",
                "--allowedTools",
                "Read,Write,Edit",
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(claude_schema(self.contracts / "author-report.schema.json")),
                ],
                stdin=prompt,
                log_path=log,
                timeout=self.args.author_timeout,
            )
        except subprocess.TimeoutExpired:
            if draft.exists():
                return self.recover_author_report(packet_path, cycle)
            raise
        envelope = json.loads(result.stdout)
        structured = envelope.get("structured_output")
        if not isinstance(structured, dict):
            raise LoopError(f"{scene_id}: Fable returned no structured author report")
        write_json(report, structured)
        if not draft.exists() or not report.exists():
            raise LoopError(f"{scene_id}: Fable did not create both declared artifacts")
        self.validate("author-report.schema.json", report)
        data = load_json(report)
        if data["scene_id"] != scene_id or data["draft_path"] != packet["output"]["draft_path"]:
            raise LoopError(f"{scene_id}: author report identity mismatch")
        actual = word_count(draft)
        data = normalize_report_word_count(report, actual)
        self.validate("author-report.schema.json", report)
        if data["status"] != "DONE":
            raise LoopError(f"{scene_id}: author reported BLOCKED: {data['blockers']}")
        print(f"[{scene_id}] draft ready: {actual:,} words", flush=True)
        return data

    def recover_author_report(self, packet_path: Path, cycle: int) -> dict:
        packet = load_json(packet_path)
        scene_id = packet["scene_id"]
        draft = BOOK / packet["output"]["draft_path"]
        report = BOOK / packet["output"]["report_path"]
        recovery_prompt = f"""# Penname V3 author-report recovery

You are the Fable 5 author seat that just completed the manuscript. The prose is
already written. Do not edit any file. Read these two files:

- Packet: {packet_path.relative_to(BOOK).as_posix()}
- Draft: {draft.relative_to(BOOK).as_posix()}

Return an honest author report conforming to the supplied JSON schema. Use
run_id `{run_id(scene_id, 'author-recovery', cycle)}`, scene_id `{scene_id}`,
and the packet's exact draft_path. Count words by whitespace exactly. Assess
each must-include obligation and disclose inventions, state proposals,
deviations, and blockers. The editor will independently verify everything.
"""
        log = WORK / "runs" / scene_id / f"cycle-{cycle}" / "fable-report-recovery.log"
        print(f"[{scene_id}] recovering structured Fable author report", flush=True)
        result = self.command(
            [
                "claude",
                "--print",
                "--model",
                self.args.author_model,
                "--effort",
                "high",
                "--no-session-persistence",
                "--safe-mode",
                "--restricted",
                "--permission-mode",
                "dontAsk",
                "--allowedTools",
                "Read",
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(claude_schema(self.contracts / "author-report.schema.json")),
            ],
            stdin=recovery_prompt,
            log_path=log,
        )
        envelope = json.loads(result.stdout)
        structured = envelope.get("structured_output")
        if not isinstance(structured, dict):
            raise LoopError(f"{scene_id}: Fable report recovery returned no structured output")
        write_json(report, structured)
        self.validate("author-report.schema.json", report)
        data = load_json(report)
        actual = word_count(draft)
        if data["scene_id"] != scene_id or data["draft_path"] != packet["output"]["draft_path"]:
            raise LoopError(f"{scene_id}: recovered author report identity mismatch")
        data = normalize_report_word_count(report, actual)
        self.validate("author-report.schema.json", report)
        if data["status"] != "DONE":
            raise LoopError(f"{scene_id}: recovered author report is BLOCKED: {data['blockers']}")
        print(f"[{scene_id}] recovered report for {actual:,}-word draft", flush=True)
        return data

    def structured_sol(
        self,
        role: str,
        prompt: str,
        schema_name: str,
        output: Path,
        log: Path,
    ) -> dict:
        output.unlink(missing_ok=True)
        transport_dir = WORK / "transport-schemas"
        transport_dir.mkdir(parents=True, exist_ok=True)
        transport_schema = transport_dir / schema_name
        write_json(
            transport_schema,
            codex_schema_node(load_json(self.contracts / schema_name)),
        )
        result = self.command(
            [
                "codex",
                "exec",
                "--model",
                self.args.editor_model,
                "--sandbox",
                "read-only",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--color",
                "never",
                "--cd",
                str(BOOK),
                "--output-schema",
                str(transport_schema),
                "--output-last-message",
                str(output),
                "-",
            ],
            stdin=prompt,
            log_path=log,
        )
        if not output.exists():
            raise LoopError(f"Sol {role} produced no structured report: {result.stdout[-1000:]}")
        self.validate(schema_name, output)
        return load_json(output)

    def edit(self, packet_path: Path, cycle: int) -> dict:
        packet = load_json(packet_path)
        scene_id = packet["scene_id"]
        prompt = self.compile_prompt("editor", packet_path, cycle)
        output = BOOK / packet["output"]["editor_report_path"]
        log = WORK / "runs" / scene_id / f"cycle-{cycle}" / "sol-editor.log"
        print(f"[{scene_id}] Sol independent edit cycle {cycle}", flush=True)
        report = self.structured_sol(
            "editor", prompt, "editor-report.schema.json", output, log
        )
        if report["scene_id"] != scene_id:
            raise LoopError(f"{scene_id}: editor report identity mismatch")
        print(
            f"[{scene_id}] editor verdict {report['verdict']} "
            f"({len(report['findings'])} proposed findings)",
            flush=True,
        )
        return report

    def verify(self, packet_path: Path, cycle: int, editor_report: Path) -> dict:
        packet = load_json(packet_path)
        scene_id = packet["scene_id"]
        prompt = self.compile_prompt("verifier", packet_path, cycle, editor_report)
        output = BOOK / packet["output"]["verifier_report_path"]
        log = WORK / "runs" / scene_id / f"cycle-{cycle}" / "sol-verifier.log"
        print(f"[{scene_id}] Sol evidence verification cycle {cycle}", flush=True)
        report = self.structured_sol(
            "verifier", prompt, "verification-report.schema.json", output, log
        )
        if report["scene_id"] != scene_id:
            raise LoopError(f"{scene_id}: verifier report identity mismatch")
        return report

    @staticmethod
    def verified_findings(editor: dict, verifier: dict) -> list[dict]:
        decisions = {item["finding_id"]: item for item in verifier["decisions"]}
        accepted = []
        for finding in editor["findings"]:
            decision = decisions.get(finding["id"])
            if not decision or decision["decision"] == "REJECTED":
                continue
            evidence = finding["draft_evidence"]
            accepted.append(
                {
                    "id": finding["id"],
                    "severity": finding["severity"],
                    "gate": finding["gate"],
                    "evidence": (
                        f"{evidence['path']}:{evidence['line_start']}-{evidence['line_end']}: "
                        f"{evidence['quote']} Verification: {decision['reason']}"
                    ),
                    "consequence": finding["consequence"],
                    "repair_target": finding["repair_target"],
                }
            )
        return accepted

    @staticmethod
    def fingerprint(findings: list[dict]) -> str:
        stable = [
            {key: finding[key] for key in ("severity", "gate", "consequence", "repair_target")}
            for finding in findings
        ]
        return hashlib.sha256(
            json.dumps(stable, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def set_repair_packet(self, packet_path: Path, findings: list[dict]) -> None:
        packet = load_json(packet_path)
        packet["job"] = (
            "structural_repair"
            if any(item["severity"] in {"BLOCKER", "HIGH"} for item in findings)
            else "line_edit"
        )
        packet["verified_findings"] = findings
        current_draft = packet["output"]["draft_path"]
        if not any(
            item["path"] == current_draft and item["label"] == "Current rewrite to repair"
            for item in packet["context_files"]
        ):
            packet["context_files"].append(
                {
                    "kind": "reference",
                    "label": "Current rewrite to repair",
                    "path": current_draft,
                    "required": True,
                }
            )
        write_json(packet_path, packet)

    def reset_packet_after_close(self, packet_path: Path) -> None:
        packet = load_json(packet_path)
        packet["job"] = "draft"
        packet["verified_findings"] = []
        packet["context_files"] = [
            item for item in packet["context_files"] if item["label"] != "Current rewrite to repair"
        ]
        write_json(packet_path, packet)

    def run_chapter(self, number: int) -> None:
        packet_path = WORK / "packets" / f"chapter-{number:02d}.json"
        packet = load_json(packet_path)
        scene_id = packet["scene_id"]
        state = load_json(STATE)
        if state["phase"] == "PROJECT_READY":
            self.advance("start_scene", scene_id=scene_id, note=f"Begin Chapter {number}")
        elif state["phase"] == "SCENE_CLOSED":
            self.advance("next_scene", scene_id=scene_id, note=f"Begin Chapter {number}")
        elif state["active_scene_id"] != scene_id:
            raise LoopError(
                f"state is {state['phase']} on {state['active_scene_id']}, cannot start {scene_id}"
            )

        state = load_json(STATE)
        if state["phase"] == "REPAIRING":
            report_path = BOOK / packet["output"]["report_path"]
            report_words = load_json(report_path).get("word_count", -1) if report_path.exists() else -1
            draft_words = word_count(BOOK / packet["output"]["draft_path"])
            if report_words != draft_words:
                existing = load_json(report_path) if report_path.exists() else {}
                if (
                    existing.get("scene_id") == scene_id
                    and existing.get("draft_path") == packet["output"]["draft_path"]
                    and existing.get("status") == "DONE"
                    and report_path.stat().st_mtime >= (BOOK / packet["output"]["draft_path"]).stat().st_mtime
                ):
                    normalize_report_word_count(report_path, draft_words)
                    self.validate("author-report.schema.json", report_path)
                else:
                    synthesize_interrupted_author_report(
                        packet_path,
                        report_path,
                        draft_words,
                        state["repair_cycle"],
                        "Fable session limit interrupted the structured self-report after the prose write; acceptance is delegated to independent Sol review.",
                    )
                    self.validate("author-report.schema.json", report_path)
                self.advance("repair_done", note="Recovered report for completed Fable repair")
            else:
                self.author(packet_path, state["repair_cycle"], repair=True)
                self.advance("repair_done", note="Fable completed verified repair after resume")
            state = load_json(STATE)
        if state["phase"] == "PACKET_READY":
            self.validate("scene-packet.schema.json", packet_path)
            self.advance("packet_validated", note="Packet and frozen contexts validated")

        state = load_json(STATE)
        if state["phase"] == "AUTHORING":
            self.author(packet_path, 0)
            self.advance("author_done", note="Fable produced validated draft and author report")

        cycle = load_json(STATE)["repair_cycle"]
        while True:
            state = load_json(STATE)
            if state["phase"] != "EDITING":
                raise LoopError(f"{scene_id}: unexpected phase {state['phase']}")
            editor = self.edit(packet_path, cycle)
            editor_path = BOOK / packet["output"]["editor_report_path"]
            if editor["verdict"] == "PASS" and not editor["findings"]:
                self.archive(load_json(packet_path), cycle)
                self.advance("editor_pass", note="Sol editor found no repairable defect")
                self.reset_packet_after_close(packet_path)
                print(f"[{scene_id}] CLOSED", flush=True)
                return

            self.advance("editor_findings", note="Proposed findings require evidence verification")
            verifier = self.verify(packet_path, cycle, editor_path)
            findings = self.verified_findings(editor, verifier)
            if not findings:
                self.archive(load_json(packet_path), cycle)
                self.advance("verification_clear", note="No proposed finding survived verification")
                self.reset_packet_after_close(packet_path)
                print(f"[{scene_id}] CLOSED after verification", flush=True)
                return

            fingerprint = self.fingerprint(findings)
            self.advance(
                "verification_repair",
                fingerprint=fingerprint,
                note=f"{len(findings)} verified findings require repair",
            )
            if load_json(STATE)["phase"] == "BLOCKED":
                raise LoopError(f"{scene_id}: bounded repair ceiling reached")
            cycle = load_json(STATE)["repair_cycle"]
            self.archive(load_json(packet_path), cycle - 1)
            self.set_repair_packet(packet_path, findings)
            self.validate("scene-packet.schema.json", packet_path)
            self.author(packet_path, cycle, repair=True)
            self.advance("repair_done", note="Fable repaired only verified findings")

    def run(self) -> None:
        state = load_json(STATE)
        start = self.args.start
        if state["scenes_closed"] and start == 1:
            start = state["scenes_closed"] + 1
        for number in range(start, self.args.through + 1):
            self.run_chapter(number)
        print(
            f"chapter loop stopped at {load_json(STATE)['scenes_closed']}/33 closed; "
            f"phase={load_json(STATE)['phase']}",
            flush=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--penname-root", type=Path, default=DEFAULT_PENNAME)
    parser.add_argument("--author-model", default="fable")
    parser.add_argument("--editor-model", default="gpt-5.6-sol")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--through", type=int, default=33)
    parser.add_argument("--timeout", type=int, default=3600, help="seconds per model call")
    parser.add_argument(
        "--author-timeout",
        type=int,
        default=720,
        help="seconds before preserving Fable prose and recovering its report",
    )
    args = parser.parse_args()
    if not 1 <= args.start <= args.through <= 33:
        parser.error("require 1 <= --start <= --through <= 33")
    return args


def main() -> int:
    try:
        Runner(parse_args()).run()
    except (LoopError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
