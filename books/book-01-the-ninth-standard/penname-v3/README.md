# The Ninth Standard — Pen Name V3 Rewrite

This directory is the production workspace for the full Book One rewrite on
the `rewrite-1` branch. The existing `../manuscript/` edition is frozen evidence
until the rewritten book passes the chapter, act, and book gates.

## Locked seats

- Author: Claude Fable 5 (`fable` / `claude-fable-5`)
- Editor: GPT-5.6 Sol (`gpt-5.6-sol`), fresh context for every review
- Finding verifier: GPT-5.6 Sol, separate fresh context
- Pen name: `fantasy-author-a`
- Protocol: Penname Codex V3.1 at commit
  `e3d6829b7c64fc4f78dfcba8f06363773be4c7fc`

## Authority order

1. `../../../CANON_RULES.md`
2. `../BOOK_BIBLE.md`, `../STATE_LEDGER.md`, and `../CLUE_LEDGER.md`
3. `../CHAPTER_ARCHITECTURE.md`
4. `../../../canon/UNIVERSE_BIBLE.md`
5. `../../../canon/NAME_REGISTRY.md` for spelling and collision control only
6. The matching source chapter as scene-level evidence

When a lower artifact conflicts with a higher one, the higher artifact wins.
In particular, role descriptions in the name registry are not story authority.

## Layout

- `packets/` — validated chapter work orders
- `manuscript/` — rewritten prose, one chapter per file
- `reports/current/` — latest author, editor, and verifier reports
- `runs/` — immutable per-cycle evidence snapshots
- `prompts/` — compiled prompt hashes and optional retained prompts
- `loop-state.json` — V3.1 state-machine record

Run `scripts/prepare_book1_penname_v3.py` once, then
`scripts/run_book1_penname_v3.py`. The runner never edits the frozen source
manuscript. Promotion happens only after the book gate passes.

