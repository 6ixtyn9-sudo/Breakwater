#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

files=(
  localdata/status.csv
  localdata/universe.csv
  localdata/research/discovered_slices.csv
  localdata/research/validated_slices.csv
  localdata/research/monitored_slices.csv
  localdata/research/paper_trade_log.csv
  localdata/research/paper_positions.json
  localdata/research/cooldown_journal.json
  localdata/promotion_registry.json
  localdata/risk_state.json
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    git add "$file"
  fi
done

if git diff --cached --quiet; then
  echo "No Breakwater state changes"
  exit 0
fi

git commit -m "chore(state): update Breakwater operational records [skip ci]"

for attempt in 1 2 3; do
  if git pull --rebase --autostash origin main 2>/dev/null && git push origin main; then
    echo "Breakwater state committed and pushed"
    exit 0
  fi
  echo "State push raced another workflow; resolving deterministically (attempt $attempt)"

  git rebase --abort 2>/dev/null || true
  git fetch origin main

  BACKUP_DIR="$(mktemp -d)"
  for file in "${files[@]}"; do
    if [ -f "$file" ]; then
      mkdir -p "$BACKUP_DIR/$(dirname "$file")"
      cp "$file" "$BACKUP_DIR/$file"
    fi
  done

  git reset --hard origin/main

  for file in "${files[@]}"; do
    if [ ! -f "$BACKUP_DIR/$file" ]; then
      continue
    fi
    if [ "$file" = "localdata/status.csv" ] && git show origin/main:"$file" > "$BACKUP_DIR/orig_status.csv" 2>/dev/null; then
      # status.csv is an append-only log: union origin's rows with our
      # new rows, deduplicated by full line, ours last.
      {
        cat "$BACKUP_DIR/orig_status.csv"
        tail -n +2 "$BACKUP_DIR/$file"
      } | awk '!seen[$0]++' > "$file"
    else
      # All other state files are regenerated wholesale or last-writer-
      # wins; this run is the later writer.
      cp "$BACKUP_DIR/$file" "$file"
    fi
  done
  rm -rf "$BACKUP_DIR"

  git add -A localdata
  if ! git diff --cached --quiet; then
    git commit -m "chore(state): update Breakwater operational records [skip ci]"
  fi
  if git push origin main; then
    echo "Breakwater state committed and pushed after conflict resolution"
    exit 0
  fi
  sleep $((attempt * 5))
done

echo "Could not push Breakwater state after retries"
exit 1
