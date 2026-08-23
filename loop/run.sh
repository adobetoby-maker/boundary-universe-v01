#!/bin/bash
# Self-perpetuating book loop.
#
# Each run does ONE iteration of work and then launches the next run. Nobody
# has to be watching. It stops on its own when the book is finished, when it
# stops making progress, or when a human drops a STOP file.
#
#   ./loop/run.sh prose            start the prose lane
#   ./loop/run.sh audio            start the audio lane
#   touch loop/STOP                halt both lanes after the current iteration
#   tail -f loop/prose.log         watch
#
# The three guards below matter more than the work does, because this thing
# relaunches itself. A loop with no brake is not autonomy, it is a fork bomb
# with good intentions.
#
#   LOCK       one iteration per lane at a time
#   MAX_ITER   hard ceiling regardless of state
#   STALL      three iterations with no commit and the lane stops itself

set -uo pipefail

ROLE="${1:?usage: run.sh <prose|audio>}"
REPO="${REPO:-$HOME/boundary-universe-v01}"
LOOP_DIR="$REPO/loop"
LOG="$LOOP_DIR/$ROLE.log"
STATE="$LOOP_DIR/$ROLE.state"
LOCK="$LOOP_DIR/$ROLE.lock"
MAX_ITER="${MAX_ITER:-200}"
GAP="${GAP:-45}"          # seconds between iterations
STALL_LIMIT=3

# The loop outlives any one session, so it cannot depend on a scratch checkout.
# If the durable clone is missing, make it -- then everything below has a home.
if [ ! -d "$REPO/.git" ]; then
  echo "cloning into $REPO"
  git clone https://github.com/adobetoby-maker/boundary-universe-v01.git "$REPO" \
    || { echo "clone failed -- cannot start"; exit 1; }
fi

mkdir -p "$LOOP_DIR"
cd "$REPO" || { echo "no repo at $REPO"; exit 1; }

say() { printf '%s  [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$ROLE" "$*" | tee -a "$LOG"; }

# ── guard: someone asked us to stop ───────────────────────────────────────────
if [ -f "$LOOP_DIR/STOP" ]; then
  say "STOP file present — not scheduling another run."
  exit 0
fi

# ── guard: one iteration per lane ─────────────────────────────────────────────
# mkdir is atomic on any POSIX filesystem. flock is a GNU tool and is NOT on
# stock macOS -- the first draft of this script used it and would have failed
# on the very first guard. A lock older than two hours is assumed dead, since
# the agent call itself is capped at one hour.
if [ -d "$LOCK" ]; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]; then
    say "clearing stale lock (older than 2h)"
    rmdir "$LOCK" 2>/dev/null
  else
    say "another iteration is still running — skipping this tick."
    exit 0
  fi
fi
mkdir "$LOCK" 2>/dev/null || { say "lost the lock race — skipping."; exit 0; }
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# ── state ─────────────────────────────────────────────────────────────────────
[ -f "$STATE" ] || printf 'iter=0\nstall=0\nlast_sha=\n' > "$STATE"
# shellcheck disable=SC1090
source "$STATE"
iter=$((iter + 1))

if [ "$iter" -gt "$MAX_ITER" ]; then
  say "hit MAX_ITER=$MAX_ITER — stopping. Raise it deliberately if that was wrong."
  exit 0
fi

git fetch origin --prune -q 2>/dev/null

# ── done? ─────────────────────────────────────────────────────────────────────
# Four conditions, not one. See handoff/AUTONOMOUS_LOOP.md section 1.
if bash "$LOOP_DIR/done.sh" >/dev/null 2>&1; then
  say "ALL GATES PASS — book is ready to be listened to. Loop complete after $iter iterations."
  bash "$LOOP_DIR/done.sh" | tee -a "$LOG"
  command -v osascript >/dev/null && osascript -e 'display notification "Book 1 is ready to listen to." with title "Boundary loop complete"' 2>/dev/null
  exit 0
fi

say "iteration $iter starting"

# ── the work ──────────────────────────────────────────────────────────────────
PROMPT_FILE="$LOOP_DIR/$ROLE.prompt"
if [ ! -f "$PROMPT_FILE" ]; then
  say "missing $PROMPT_FILE — cannot run. See handoff/LOOP_PROMPT.md."
  exit 1
fi

# Agent per lane. Override with AGENT=codex|grok|claude.
AGENT="${AGENT:-$( [ "$ROLE" = prose ] && echo codex || echo claude )}"

RUN_OUT="$LOOP_DIR/$ROLE.last-run.txt"
case "$AGENT" in
  codex)  timeout 3600 codex exec --dangerously-bypass-approvals-and-sandbox \
            "$(cat "$PROMPT_FILE")" > "$RUN_OUT" 2>&1 ;;
  grok)   timeout 3600 grok --always-approve -p "$(cat "$PROMPT_FILE")" \
            > "$RUN_OUT" 2>&1 ;;
  claude) timeout 3600 claude -p --dangerously-skip-permissions \
            "$(cat "$PROMPT_FILE")" > "$RUN_OUT" 2>&1 ;;
  *)      say "unknown AGENT=$AGENT"; exit 1 ;;
esac
rc=$?
say "$AGENT exited $rc ($(wc -l < "$RUN_OUT" | tr -d ' ') lines)"

# ── did anything actually happen? ─────────────────────────────────────────────
git fetch origin --prune -q 2>/dev/null
BRANCH=$( [ "$ROLE" = prose ] && echo origin/expand/book1-ch01-10 || echo origin/main )
# --verify makes an unresolvable ref an ERROR. Without it, rev-parse echoes the
# ref name back, which is byte-identical every iteration and therefore reads as
# "no new commits" -- a deleted branch would look like a lazy agent.
if ! new_sha=$(git rev-parse --verify --quiet "$BRANCH^{commit}"); then
  say "cannot resolve $BRANCH — branch missing or fetch failed. Stopping."
  exit 1
fi

if [ "$new_sha" = "$last_sha" ]; then
  stall=$((stall + 1))
  say "no new commit on $BRANCH (stall $stall/$STALL_LIMIT)"
else
  [ -n "$last_sha" ] && say "progress: $(git log --oneline "$last_sha..$new_sha" 2>/dev/null | wc -l | tr -d ' ') new commit(s)"
  stall=0
fi
last_sha="$new_sha"

printf 'iter=%s\nstall=%s\nlast_sha=%s\n' "$iter" "$stall" "$last_sha" > "$STATE"

if [ "$stall" -ge "$STALL_LIMIT" ]; then
  say "STALLED — $STALL_LIMIT iterations with no commit. Stopping so a human can look."
  say "last agent output: $RUN_OUT"
  command -v osascript >/dev/null && osascript -e "display notification \"$ROLE lane stalled\" with title \"Boundary loop\"" 2>/dev/null
  exit 0
fi

# ── launch the next run ───────────────────────────────────────────────────────
# The lock is released when this process exits, so the child must start AFTER
# a short gap or it will find the lock still held and skip its own turn.
say "scheduling next iteration in ${GAP}s"
# setsid is also absent on macOS; nohup + disown is enough to survive the
# parent exiting. The EXIT trap releases the lock as this process ends, and
# the child sleeps past that, so it cannot collide with its own parent.
nohup bash -c "sleep $GAP; exec '$0' '$ROLE'" >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
