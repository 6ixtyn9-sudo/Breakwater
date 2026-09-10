"""Execute scripts/commit_state.sh against a throwaway git repo.

The static sibling test_commit_state_staging.py parses the file arrays; this
test runs the script for real: a dirty owned state file must produce the
state commit and reach the origin, while unrelated paths (including an
unrelated file under localdata/) are never swept into it.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "commit_state.sh"


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return out.stdout.strip()


def test_commit_state_commits_only_owned_paths(tmp_path):
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-b", "main", str(work)], check=True,
                   capture_output=True)
    _git(work, "remote", "add", "origin", str(origin))

    # Seed the repo with the script itself and one owned state file.
    (work / "scripts").mkdir()
    state_dir = work / "localdata"
    state_dir.mkdir()
    (work / "scripts" / "commit_state.sh").write_text(SCRIPT.read_text())
    (state_dir / "status.csv").write_text("timestamp_utc,stage\n2026-09-10T00:00:00Z,seed\n")
    _git(work, "add", "-A")
    _git(work, "-c", "user.name=t", "-c", "user.email=t@example.com",
         "commit", "-m", "init")
    _git(work, "push", "-u", "origin", "main")

    # Dirty an owned file, then add paths the script must never stage.
    with (state_dir / "status.csv").open("a") as handle:
        handle.write("2026-09-10T00:30:00Z,guardian_ok\n")
    (work / "stray.txt").write_text("not mine\n")
    (state_dir / "stray.json").write_text('{"not": "owned"}\n')

    env = {k: v for k, v in os.environ.items() if k != "BREAKWATER_HEARTBEAT_URL"}
    result = subprocess.run(
        ["bash", "scripts/commit_state.sh", "guardian"],
        cwd=work, env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    subject = _git(work, "show", "-s", "--format=%s", "HEAD")
    assert subject == "chore(state): update Breakwater operational records [skip ci]"

    changed = _git(work, "show", "--name-status", "--format=", "HEAD")
    assert changed == "M\tlocaldata/status.csv", changed

    # Strays remain untracked on disk and never reached the pushed history.
    porcelain = _git(work, "status", "--porcelain")
    assert "?? stray.txt" in porcelain
    assert "?? localdata/stray.json" in porcelain
    assert (work / "stray.txt").exists()
    assert (state_dir / "stray.json").exists()
    fetch_ls = subprocess.run(
        ["git", "show", "origin/main:stray.txt"], cwd=work, capture_output=True
    )
    assert fetch_ls.returncode != 0
    fetch_localdata = subprocess.run(
        ["git", "show", "origin/main:localdata/stray.json"], cwd=work, capture_output=True
    )
    assert fetch_localdata.returncode != 0
