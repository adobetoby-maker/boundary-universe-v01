#!/bin/bash
# Contact Zero Trilogy — Book 3 (The Long Silence) prose loop. Final book of the trilogy.
#
# Variant of run-contact-zero.sh targeting Book 3 specifically.
# Uses loop/contact-zero-book3.prompt and monitors draft/contact-zero-book3.
#
#   ./loop/run-contact-zero-book3.sh       start / advance one iteration
#   touch loop/STOP-contact-zero-book3     halt after current iteration
#   tail -f loop/contact-zero-book3.log    watch
#
# Guards: LOCK / MAX_ITER / STALL_LIMIT — same as run-contact-zero.sh
# Fixes baked in from Book 1's post-mortem: agent pushes after every commit,
# and completion check counts DRAFT COMPLETE as well as WRITTEN.

set -uo pipefail

ROLE="contact-zero-book3"
REPO="${REPO:-$HOME/boundary-universe-v01}"
LOOP_DIR="$REPO/loop"
LOG="$LOOP_DIR/$ROLE.log"
STATE="$LOOP_DIR/$ROLE.state"
LOCK="$LOOP_DIR/$ROLE.lock"
MAX_ITER="${MAX_ITER:-200}"
GAP="${GAP:-60}"
STALL_LIMIT=3
BRANCH="origin/draft/contact-zero-book3"
ARCH_FILE="$REPO/books/book-03-the-long-silence/CHAPTER_ARCHITECTURE.md"

if [ ! -d "$REPO/.git" ]; then
  echo "no repo at $REPO — cannot start"
  exit 1
fi

mkdir -p "$LOOP_DIR"
cd "$REPO" || { echo "no repo at $REPO"; exit 1; }

say() { printf '%s  [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$ROLE" "$*" | tee -a "$LOG"; }

# guard: Book3-specific STOP only
if [ -f "$LOOP_DIR/STOP-contact-zero-book3" ]; then
  say "STOP-contact-zero-book3 file present — halting Book 3 lane."
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

# guard: don't start Book 3 until Book 2 is actually complete (all 24 drafted)
BOOK2_ARCH="$REPO/books/book-02-the-first-coupling/CHAPTER_ARCHITECTURE.md"
BOOK2_DONE=$(grep -cE "(✓ WRITTEN|DRAFT COMPLETE)" "$BOOK2_ARCH" 2>/dev/null || echo 0)
if [ "$BOOK2_DONE" -lt 24 ]; then
  say "Book 2 not yet complete ($BOOK2_DONE/24) — refusing to start Book 3. Run Book 2's loop first."
  exit 1
fi

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

# bootstrap: create draft/contact-zero-book3 from book2's tip if it doesn't exist remotely yet
if ! git rev-parse --verify --quiet "$BRANCH^{commit}" >/dev/null; then
  say "branch $BRANCH does not exist yet — creating from draft/contact-zero-book2"
  git checkout -B draft/contact-zero-book3 origin/draft/contact-zero-book2 2>&1 | tee -a "$LOG"
  git push -u origin draft/contact-zero-book3 2>&1 | tee -a "$LOG"
  git fetch origin --prune -q 2>/dev/null
fi

say "iteration $iter starting on $BRANCH"

# check: all 24 chapters done?
DONE_COUNT=$(grep -cE "(✓ WRITTEN|DRAFT COMPLETE)" "$ARCH_FILE" 2>/dev/null || echo 0)
if [ "$DONE_COUNT" -ge 24 ]; then
  say "ALL 24 CHAPTERS DRAFTED — Book 3 prose phase complete. CONTACT ZERO TRILOGY DRAFT COMPLETE."
  say "Next: full trilogy review pass before audio production."
  touch "$LOOP_DIR/STOP-contact-zero-book3"
  command -v osascript >/dev/null && osascript -e 'display notification "Book 3 (The Long Silence): all 24 chapters drafted. Trilogy complete." with title "Boundary loop"' 2>/dev/null
  exit 0
fi

PROMPT_FILE="$LOOP_DIR/contact-zero-book3.prompt"
if [ ! -f "$PROMPT_FILE" ]; then
  say "missing $PROMPT_FILE — cannot run."
  exit 1
fi

AGENT="${AGENT:-codex}"
RUN_OUT="$LOOP_DIR/contact-zero-book3.last-run.txt"

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
  command -v osascript >/dev/null && osascript -e "display notification \"Book 3 stalled at iter $iter\" with title \"Boundary loop\"" 2>/dev/null
  exit 0
fi

# schedule next iteration
say "scheduling next iteration in ${GAP}s"
nohup bash -c "sleep $GAP; exec '$0'" >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
