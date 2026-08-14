#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: scripts/install_bundle.sh BUNDLE_PATH BUNDLE_SHA256 COMMIT_SHA"
  exit 2
fi

BUNDLE_PATH="$1"
EXPECTED_BUNDLE_SHA="$2"
EXPECTED_COMMIT_SHA="$3"

git bundle verify "$BUNDLE_PATH"

printf '%s  %s\n' "$EXPECTED_BUNDLE_SHA" "$BUNDLE_PATH" | shasum -a 256 --check

git switch main
git fetch --prune origin
git reset --hard origin/main

git fetch "$BUNDLE_PATH" refs/heads/main:refs/remotes/breakwater-build/main

test "$(git rev-parse refs/remotes/breakwater-build/main)" = "$EXPECTED_COMMIT_SHA"

git -c user.name="6ixtyn9-sudo" -c user.email="6ixtyn9@gmail.com" \
  cherry-pick "$(git rev-parse refs/remotes/breakwater-build/main)"

if ! git push origin main; then
  git -c user.name="6ixtyn9-sudo" -c user.email="6ixtyn9@gmail.com" \
    pull --rebase --autostash origin main
  git push origin main
fi

git update-ref -d refs/remotes/breakwater-build/main

git log -1 --oneline
