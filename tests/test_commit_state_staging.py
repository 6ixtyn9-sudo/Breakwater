"""commit_state.sh must only stage paths that exist as regular files.

The role file arrays feed `if [ -f "$file" ]`, so a bare directory entry
(e.g. `localdata/daily/`) is silently never staged: the digest generator runs,
its output is left unstaged, and the artifact never reaches main. That is a
silent observability failure -- no CI annotation fires for it -- so it is
asserted here.
"""

from __future__ import annotations

import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "commit_state.sh"
ROOT = SCRIPT.parent.parent
ARRAY = re.compile(r"^(\w+)=\(([^)]*)\)", re.MULTILINE | re.DOTALL)


def _entries() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name, body in ARRAY.findall(SCRIPT.read_text(encoding="utf-8")):
        out[name] = [tok for tok in body.split() if not tok.startswith("#")]
    return out


def _staged(patterns: list[str]) -> set[Path]:
    """Mirror the script: expand globs, then keep only entries `[ -f ]` accepts."""
    kept: set[Path] = set()
    for pat in patterns:
        hits = sorted(ROOT.glob(pat)) if any(c in pat for c in "*?[") else [ROOT / pat]
        kept.update(h for h in hits if h.is_file())
    return kept


def test_arrays_parse() -> None:
    entries = _entries()
    assert {"status_files", "daily_files", "research_files", "paper_files"} <= set(entries)
    assert any(
        "monitored_slices.csv" in tok
        for toks in entries.values()
        for tok in toks
    ), "multi-line arrays must parse too"


def test_no_directory_entries() -> None:
    offenders = [
        f"{name}: {pat}"
        for name, pats in _entries().items()
        for pat in pats
        if not any(c in pat for c in "*?[") and (ROOT / pat).is_dir()
    ]
    assert not offenders, "directory entries are never staged by [ -f ]:\n" + "\n".join(offenders)


def test_digest_reaches_the_index() -> None:
    entries = _entries()
    staged = _staged(entries["status_files"]) | _staged(entries.get("daily_files", []))
    latest = ROOT / "localdata" / "daily" / "latest.md"
    assert latest in staged, (
        "localdata/daily/latest.md is not staged by status_files/daily_files; "
        "the regenerated digest is dropped on the happy path"
    )
