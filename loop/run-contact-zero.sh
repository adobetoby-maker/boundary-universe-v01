#!/bin/bash
# Contact Zero prose loop.
#
# Variant of run.sh targeting the Contact Zero trilogy specifically.
# Uses loop/contact-zero.prompt and monitors draft/contact-zero-book1.
#
#   ./loop/run-contact-zero.sh            start / advance one iteration
#   touch loop/STOP                       halt after current iteration
#   tail -f loop/contact-zero.log         watch
#
# Guards: LOCK / MAX_ITER / STALL_LIMIT — same as run.sh

set -uo pipefail

ROLE="contact-zero"
REPO="${REPO:-$HOME/boundary-universe-v01}"
LOOP_DIR="$REPO/loop"
LOG="$LOOP_DIR/$ROLE.log"
STATE="$LOOP_DIR/$ROLE.state"
LOCK="$LOOP_DIR/$ROLE.lock"
MAX_ITER="${MAX_ITER:-200}"
GAP="${GAP:-60}"          # seconds between iterations (slightly longer for prose quality)
STALL_LIMIT=3
BRANCH="origin/draft/contact-zero-book1"

if [ ! -d "$REPO/.git" ]; then
  echo "no repo at $REPO — cannot start"
  exit 1
fi

mkdir -p "$LOOP_DIR"
cd "$REPO" || { echo "no repo at $REPO"; exit 1; }

say() { printf '%s  [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$ROLE" "$*" | tee -a "$LOG"; }

# guard: STOP file
if [ -f "$LOOP_DIR/STOP" ]; then
  say "STOP file present — not scheduling another run."
  exit 0
fi

# guard: CZ-specific STOP
if [ -f "$LOOP_DIR/STOP-contact-zero" ]; then
  say "STOP-contact-zero file present — halting Contact Zero lane."
  exit 0
fi

# guard: one iteration at a time
if [ -d "$LOCK" ]; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]; then
    say "clearing stale lock (older than 2h)"
    rmdir "$LOCK" 2>/dev/null
  else
    say "another iteration is still running — skipping."
    exit 0
  fi
fi
mkdir "$LOCK" 2>/dev/null || { say "lost the lock race — skipping."; exit 0; }
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# state
[ -f "$STATE" ] || printf 'iter=0\nstall=0\nlast_sha=\n' > "$STATE"
# shellcheck disable=SC1090
source "$STATE"
iter=$((iter + 1))

if [ "$iter" -gt "$MAX_ITER" ]; then
  say "hit MAX_ITER=$MAX_ITER — stopping."
  exit 0
fi

git fetch origin --prune -q 2>/dev/null
say "iteration $iter starting on $BRANCH"

# check: all 24 chapters done?
DONE_COUNT=$(grep -c "✓ WRITTEN" "$REPO/books/book-01-contact-zero/CHAPTER_ARCHITECTURE.md" 2>/dev/null || echo 0)
if [ "$DONE_COUNT" -ge 24 ]; then
  say "ALL 24 CHAPTERS WRITTEN — prose phase complete. Switching to expansion phase."
  say "Run expansion via BSBC system in loop/prose.prompt."
  touch "$LOOP_DIR/STOP-contact-zero"
  command -v osascript >/dev/null && osascript -e 'display notification "Contact Zero: all 24 chapters drafted." with title "Boundary loop"' 2>/dev/null
  exit 0
fi

PROMPT_FILE="$LOOP_DIR/contact-zero.prompt"
if [ ! -f "$PROMPT_FILE" ]; then
  say "missing $PROMPT_FILE — cannot run."
  exit 1
fi

AGENT="${AGENT:-codex}"
RUN_OUT="$LOOP_DIR/contact-zero.last-run.txt"

say "running $AGENT ($DONE_COUNT/24 chapters done)"
case "$AGENT" in
  codex)  timeout 3600 codex exec --dangerously-bypass-approvals-and-sandbox \
            "$(cat "$PROMPT_FILE")" > "$RUN_OUT" 2>&1 ;;
  claude) timeout 3600 claude -p --dangerously-skip-permissions \
            "$(cat "$PROMPT_FILE")" > "$RUN_OUT" 2>&1 ;;
  *)      say "unknown AGENT=$AGENT"; exit 1 ;;
esac
rc=$?
say "$AGENT exited $rc ($(wc -l < "$RUN_OUT" | tr -d ' ') lines)"

# did anything commit?
git fetch origin --prune -q 2>/dev/null
if ! new_sha=$(git rev-parse --verify --quiet "$BRANCH^{commit}"); then
  say "cannot resolve $BRANCH — fetch failed. Stopping."
  exit 1
fi

if [ "$new_sha" = "$last_sha" ]; then
  stall=$((stall + 1))
  say "no new commit on $BRANCH (stall $stall/$STALL_LIMIT)"
else
  say "progress: $(git log --oneline "$last_sha..$new_sha" 2>/dev/null | wc -l | tr -d ' ') new commit(s)"
  stall=0
fi
last_sha="$new_sha"

printf 'iter=%s\nstall=%s\nlast_sha=%s\n' "$iter" "$stall" "$last_sha" > "$STATE"

if [ "$stall" -ge "$STALL_LIMIT" ]; then
  say "STALLED — $STALL_LIMIT iterations with no commit. Stopping for human review."
  say "last agent output: $RUN_OUT"
  command -v osascript >/dev/null && osascript -e "display notification \"Contact Zero stalled at iter $iter\" with title \"Boundary loop\"" 2>/dev/null
  exit 0
fi

# schedule next iteration
say "scheduling next iteration in ${GAP}s"
nohup bash -c "sleep $GAP; exec '$0'" >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
