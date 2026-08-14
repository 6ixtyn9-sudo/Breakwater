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
  if git pull --rebase --autostash origin main && git push origin main; then
    exit 0
  fi
  if [ "$attempt" = "3" ]; then
    exit 1
  fi
  sleep $((attempt * 5))
done
