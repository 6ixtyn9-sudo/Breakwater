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


def test_commit_state_stages_weekly_rotation_deletions(tmp_path):
    """After a week rolls, the gzipped week must replace the plain file in
    the commit — not sit beside it."""
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-b", "main", str(work)], check=True,
                   capture_output=True)
    _git(work, "remote", "add", "origin", str(origin))

    (work / "scripts").mkdir()
    (work / "scripts" / "commit_state.sh").write_text(SCRIPT.read_text())
    pos = work / "localdata" / "positioning"
    pos.mkdir(parents=True)
    (pos / "2026-W42.csv").write_text("snapshot_hour,coin\n2026-10-18T15:00Z,BTC\n")
    skip = work / "localdata" / "research" / "paper_skip_log"
    skip.mkdir(parents=True)
    (skip / "2026-W42.csv").write_text("closed_at,outcome\n2026-10-18T15:00Z,skipped\n")
    _git(work, "add", "-A")
    _git(work, "-c", "user.name=t", "-c", "user.email=t@example.com",
         "commit", "-m", "init")
    _git(work, "push", "-u", "origin", "main")

    # Simulate the rotation both writers perform: new open week, old week packed.
    import gzip
    for directory in (pos, skip):
        plain = directory / "2026-W42.csv"
        with plain.open("rb") as src, gzip.open(directory / "2026-W42.csv.gz", "wb") as dst:
            dst.write(src.read())
        plain.unlink()
        (directory / "2026-W43.csv").write_text("h\nrow\n")

    env = {k: v for k, v in os.environ.items() if k != "BREAKWATER_HEARTBEAT_URL"}
    result = subprocess.run(
        ["bash", "scripts/commit_state.sh", "paper"],
        cwd=work, env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    changed = dict(
        line.split("\t", 1)[::-1]
        for line in _git(work, "show", "--name-status", "--format=", "HEAD").splitlines()
    )
    assert changed == {
        "localdata/positioning/2026-W42.csv": "D",
        "localdata/positioning/2026-W42.csv.gz": "A",
        "localdata/positioning/2026-W43.csv": "A",
        "localdata/research/paper_skip_log/2026-W42.csv": "D",
        "localdata/research/paper_skip_log/2026-W42.csv.gz": "A",
        "localdata/research/paper_skip_log/2026-W43.csv": "A",
    }
    tracked = set(_git(work, "ls-files").splitlines())
    assert "localdata/positioning/2026-W42.csv" not in tracked
    assert "localdata/research/paper_skip_log/2026-W42.csv" not in tracked


BOOK_HEADER = "slice_id,kind,status,paper_trades,paper_wins,paper_losses,paper_pnl_zar,cooldown_until,mean_ret_costadj\n"


def _init_origin_with_book(tmp_path: Path, book_text: str) -> tuple[Path, Path]:
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "init", "-b", "main", str(work)], check=True, capture_output=True)
    _git(work, "remote", "add", "origin", str(origin))
    (work / "scripts").mkdir()
    (work / "scripts" / "commit_state.sh").write_text(SCRIPT.read_text())
    merge_script = SCRIPT.parent / "merge_book_on_conflict.py"
    (work / "scripts" / "merge_book_on_conflict.py").write_text(merge_script.read_text())
    research = work / "localdata" / "research"
    research.mkdir(parents=True)
    (research / "monitored_slices.csv").write_text(book_text)
    (research / "paper_trade_log.csv").write_text("closed_at,outcome\n")
    _git(work, "add", "-A")
    _git(work, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-m", "init")
    _git(work, "push", "-u", "origin", "main")
    return origin, work


def _push_from_other_clone(tmp_path: Path, origin: Path, rel: str, text: str) -> None:
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", str(origin), str(other)], check=True)
    (other / rel).write_text(text)
    _git(other, "add", "-A")
    _git(other, "-c", "user.name=r", "-c", "user.email=r@example.com", "commit", "-m", "research")
    _git(other, "push", "-q", "origin", "main")


def _run_commit_state(work: Path, role: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "BREAKWATER_HEARTBEAT_URL"}
    return subprocess.run(["bash", "scripts/commit_state.sh", role], cwd=work, env=env,
                          capture_output=True, text=True)


def _book_on_origin(work: Path) -> dict[str, dict]:
    import csv
    import io
    _git(work, "fetch", "-q", "origin", "main")
    text = _git(work, "show", "origin/main:localdata/research/monitored_slices.csv")
    return {r["slice_id"]: r for r in csv.DictReader(io.StringIO(text))}


def test_paper_race_keeps_research_composition_and_paper_counters(tmp_path):
    """Paper job checked out the old book, research pushed a new one meanwhile.
    Result on origin: research's membership, paper's per-slice columns."""
    old = BOOK_HEADER + (
        "A:0:LONG:h24,PERP,monitored,2,1,1,1.5000,,0.001\n"
        "B:0:LONG:h24,PERP,monitored,0,0,0,0.0000,,0.002\n"
        "DROPPED:0:LONG:h24,PERP,monitored,5,1,4,-9.0000,,0.000\n"
    )
    origin, work = _init_origin_with_book(tmp_path, old)

    # Research lands first: drops DROPPED, adds NEW, re-states A and B with
    # stale paper columns (its checkout predates the paper closes below).
    research_book = BOOK_HEADER + (
        "A:0:LONG:h24,PERP,monitored,2,1,1,1.5000,,0.004\n"
        "B:0:LONG:h24,PERP,monitored,0,0,0,0.0000,,0.005\n"
        "NEW:0:SHORT:h12,PERP,monitored,0,0,0,0.0000,,0.009\n"
    )
    _push_from_other_clone(tmp_path, origin, "localdata/research/monitored_slices.csv", research_book)

    # Paper job, on its stale checkout, closes trades: A wins, B stops out into cooldown.
    paper_book = BOOK_HEADER + (
        "A:0:LONG:h24,PERP,monitored,3,2,1,4.2500,,0.001\n"
        "B:0:LONG:h24,PERP,cooldown,1,0,1,-3.9000,1760000000,0.002\n"
        "DROPPED:0:LONG:h24,PERP,monitored,5,1,4,-9.0000,,0.000\n"
    )
    (work / "localdata" / "research" / "monitored_slices.csv").write_text(paper_book)
    with (work / "localdata" / "research" / "paper_trade_log.csv").open("a") as handle:
        handle.write("2026-10-21T01:05:00Z,win\n")

    result = _run_commit_state(work, "paper")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "after conflict resolution" in result.stdout

    book = _book_on_origin(work)
    assert set(book) == {"A:0:LONG:h24", "B:0:LONG:h24", "NEW:0:SHORT:h12"}
    # research's composition fields win
    assert book["A:0:LONG:h24"]["mean_ret_costadj"] == "0.004"
    assert book["NEW:0:SHORT:h12"]["paper_trades"] == "0"
    # paper's per-slice columns win
    assert book["A:0:LONG:h24"]["paper_trades"] == "3"
    assert book["A:0:LONG:h24"]["paper_pnl_zar"] == "4.2500"
    assert book["B:0:LONG:h24"]["status"] == "cooldown"
    assert book["B:0:LONG:h24"]["cooldown_until"] == "1760000000"


def test_research_race_keeps_own_composition_and_takes_paper_counters(tmp_path):
    """Mirror image: research job races a paper push that landed first."""
    old = BOOK_HEADER + "A:0:LONG:h24,PERP,monitored,2,1,1,1.5000,,0.001\n"
    origin, work = _init_origin_with_book(tmp_path, old)

    paper_book = BOOK_HEADER + "A:0:LONG:h24,PERP,cooldown,3,1,2,-2.0000,1760000000,0.001\n"
    _push_from_other_clone(tmp_path, origin, "localdata/research/monitored_slices.csv", paper_book)

    research_book = BOOK_HEADER + (
        "A:0:LONG:h24,PERP,monitored,2,1,1,1.5000,,0.007\n"
        "NEW:0:SHORT:h12,PERP,monitored,0,0,0,0.0000,,0.009\n"
    )
    (work / "localdata" / "research" / "monitored_slices.csv").write_text(research_book)

    result = _run_commit_state(work, "research")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "after conflict resolution" in result.stdout

    book = _book_on_origin(work)
    assert set(book) == {"A:0:LONG:h24", "NEW:0:SHORT:h12"}
    assert book["A:0:LONG:h24"]["mean_ret_costadj"] == "0.007"
    assert book["A:0:LONG:h24"]["paper_trades"] == "3"
    assert book["A:0:LONG:h24"]["status"] == "cooldown"
