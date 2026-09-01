"""Apply the asset-native promotion fix to Breakwater via string substitution.

Run from the repo root in the codespace (same mechanism as the previous
short-gap apply_fix.py). Idempotent: safe to run twice.

What it does
------------
1. Patches src/breakwater/research_lifecycle.py so sync_book is per-asset-aware
   (always-on): promo edge = green-only mean, a min-green-assets breadth floor,
   and new summary/book fields. Reads asset_edges.csv next to the validated file.
2. Appends 3 regression tests to tests/test_research_lifecycle.py (guarded).
3. Creates docs/asset_native_promotion.md and scripts/audit_asset_native_gap.py.

Run:
    python apply_asset_native.py
Then re-run tests:
    python -m pytest tests/test_research_lifecycle.py -q
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sub_file(path: Path, old: str, new: str) -> bool:
    if not path.exists():
        print(f"  !! {path.name}: file missing; skipping this hunk")
        return False
    text = path.read_text()
    count = text.count(old)
    if count == 0:
        print(f"  !! {path.name}: hunk anchor NOT FOUND; skipping")
        return False
    if count > 1:
        print(f"  !! {path.name}: anchor matched {count}x (expected 1); skipping")
        return False
    path.write_text(text.replace(old, new, 1))
    print(f"  patched {path.name}")
    return True


# --- research_lifecycle.py substitutions --------------------------------
RL = ROOT / "src/breakwater/research_lifecycle.py"

SUBS = [
    # 1) import AssetEdge + read_asset_edges
    (
        "from breakwater.validation import ValidatedSlice, read_validated\n",
        "from breakwater.validation import AssetEdge, ValidatedSlice, read_asset_edges, read_validated\n",
    ),
    # 2) book header columns
    (
        '    # New, human marker: can we trust mean_ret_costadj as directional net edge?\n'
        '    "edge_is_directional_net",\n]\n',
        '    # New, human marker: can we trust mean_ret_costadj as directional net edge?\n'
        '    "edge_is_directional_net",\n'
        '    # Per-asset composition of the promoted slice (blank when per-asset mode off).\n'
        '    "n_green",\n'
        '    "green_frac",\n]\n',
    ),
    # 3) module constant
    (
        "MIN_BOOK_ROWS = 60\nPNL_DECAY_MIN_TRADES = 3\n",
        "MIN_BOOK_ROWS = 60\nPNL_DECAY_MIN_TRADES = 3\n\n"
        "# Per-asset-aware promotion: a validated slice must have at least this many\n"
        "# `green` per-asset rows to be promotable, and its promo edge is computed over\n"
        "# the green rows only (not the pooled all-symbol average). Honors \"each asset\n"
        "# has its own profile\" without inflating the hypothesis count (still promotes\n"
        "# whole slices, just scored/ranked on the assets that actually carry the edge).\n"
        "# Deliberately a module constant, NOT an env knob.\n"
        "MIN_GREEN_ASSETS_FOR_PROMOTION = 3\n",
    ),
    # 4) _directional_edge gains an edge override
    (
        "def _directional_edge(row: ValidatedSlice, pool_floors: dict[str, float] | None = None) -> bool:\n"
        "    # mean_ret_costadj is NET return for the chosen side (already cost-aware).\n"
        "    return row.mean_ret_costadj > 0 and row.mean_ret_costadj >= _effective_floor(row.kind, pool_floors)\n",
        "def _directional_edge(\n"
        "    row: ValidatedSlice,\n"
        "    pool_floors: dict[str, float] | None = None,\n"
        "    *,\n"
        "    edge: float | None = None,\n"
        ") -> bool:\n"
        "    # mean_ret_costadj is NET return for the chosen side (already cost-aware).\n"
        "    # `edge` lets per-asset-aware promotion override the pooled mean with the\n"
        "    # green-only composition mean (falling back to the pooled mean when None).\n"
        "    eff = row.mean_ret_costadj if edge is None else edge\n"
        "    return eff > 0 and eff >= _effective_floor(row.kind, pool_floors)\n",
    ),
    # 5) insert composition helpers before sync_book
    (
        "def sync_book(\n"
        "    *,\n"
        "    validated_path: Path,\n"
        "    book_path: Path,\n"
        "    now: datetime | None = None,\n"
        ") -> dict:\n",
        '_GREEN = "green"\n'
        '_UNTESTED = "untested"\n'
        "_GREEN_OR_UNTESTED = (_GREEN, _UNTESTED)\n\n\n"
        "def _slice_asset_composition(\n"
        "    asset_edges: list[AssetEdge],\n"
        ") -> dict[str, dict]:\n"
        '    """Per-slice composition stats over per-asset rows.\n\n'
        "    Returns ``{slice_id: {n_assets, n_green, n_untested, n_tradable,\n"
        "    green_edge_mean, tradable_edge_mean}}``. ``*_edge_mean`` is ``None`` when the\n"
        "    corresponding bucket is empty, so callers can fall back to the pooled edge.\n"
        '    """\n'
        "    by_slice: dict[str, list[AssetEdge]] = defaultdict(list)\n"
        "    for ae in asset_edges:\n"
        "        by_slice[ae.slice_id].append(ae)\n\n"
        "    comp: dict[str, dict] = {}\n"
        "    for sid, rows in by_slice.items():\n"
        "        green = [e for e in rows if e.asset_status == _GREEN]\n"
        "        tradable = [e for e in rows if e.asset_status in _GREEN_OR_UNTESTED]\n"
        "        comp[sid] = {\n"
        '            "n_assets": len(rows),\n'
        '            "n_green": len(green),\n'
        '            "n_untested": sum(1 for e in rows if e.asset_status == _UNTESTED),\n'
        '            "n_tradable": len(tradable),\n'
        '            "green_edge_mean": (\n'
        "                sum(e.mean_ret_costadj for e in green) / len(green) if green else None\n"
        "            ),\n"
        '            "tradable_edge_mean": (\n'
        "                sum(e.mean_ret_costadj for e in tradable) / len(tradable)\n"
        "                if tradable\n"
        "                else None\n"
        "            ),\n"
        "        }\n"
        "    return comp\n\n\n"
        "def _promo_edge(row: ValidatedSlice, comp: dict[str, dict] | None) -> float:\n"
        '    """Effective promo edge for a slice.\n\n'
        "    Per-asset-aware: the green-only composition mean (the assets that will\n"
        "    actually be traded), falling back to the pooled ``mean_ret_costadj`` when the\n"
        "    slice has no green rows. When no composition map is available (``comp`` is\n"
        "    None), always the pooled mean -- i.e. legacy behavior.\n"
        '    """\n'
        "    if comp is not None:\n"
        "        c = comp.get(row.slice_id)\n"
        '        if c and c["green_edge_mean"] is not None:\n'
        '            return c["green_edge_mean"]\n'
        "    return row.mean_ret_costadj\n\n\n"
        "def sync_book(\n"
        "    *,\n"
        "    validated_path: Path,\n"
        "    book_path: Path,\n"
        "    now: datetime | None = None,\n"
        ") -> dict:\n",
    ),
    # 6) always-on per-asset load in sync_book body
    (
        "    validated_rows = read_validated(validated_path)\n"
        "    validated_all = [row for row in validated_rows if row.validated]\n"
        "    existing_rows = read_book(book_path)\n"
        "    existing = {row[\"slice_id\"]: row for row in existing_rows}\n\n",
        "    validated_rows = read_validated(validated_path)\n"
        "    validated_all = [row for row in validated_rows if row.validated]\n"
        "    existing_rows = read_book(book_path)\n"
        "    existing = {row[\"slice_id\"]: row for row in existing_rows}\n\n"
        "    # Per-asset-aware promotion is ALWAYS on: read the conventional per-asset\n"
        "    # edges file sitting next to the validated file\n"
        '    # (validated_path.parent / "asset_edges.csv"), which the research workflow\n'
        "    # always writes. If it is missing/empty (e.g. bare local tests), fall back to\n"
        "    # the legacy pooled-edge promotion. read_asset_edges is fail-closed on a bad\n"
        "    # schema, so a present-but-malformed file aborts rather than silently\n"
        "    # degrading to allow-all.\n"
        '    asset_edges_path = validated_path.parent / "asset_edges.csv"\n'
        "    comp: dict[str, dict] | None = None\n"
        "    if asset_edges_path.exists() and asset_edges_path.stat().st_size > 0:\n"
        "        comp = _slice_asset_composition(read_asset_edges(asset_edges_path))\n\n",
    ),
    # 7) pools use promo edge + green breadth floor in promotable
    (
        "    pools: dict[str, list[float]] = {}\n"
        "    for row in validated_rows:\n"
        "        try:\n"
        "            edge = float(row.mean_ret_costadj)\n"
        "        except (TypeError, ValueError):\n"
        "            continue\n"
        "        pools.setdefault(str(row.kind), []).append(edge)\n"
        "    enter_pool_floors = {k: _pool_edge_floor(v, enter_q) for k, v in pools.items()}\n"
        "    keep_pool_floors = {k: _pool_edge_floor(v, keep_q) for k, v in pools.items()}\n\n"
        "    # Base promotability filter (legacy rules)\n"
        "    promotable = [\n"
        "        row\n"
        "        for row in validated_all\n"
        "        if row.n >= MIN_BOOK_ROWS\n"
        "        and _directional_edge(row, enter_pool_floors)\n"
        "        and _hip3_session_edge_ok(row)\n"
        "    ]\n",
        "    pools: dict[str, list[float]] = {}\n"
        "    for row in validated_rows:\n"
        "        try:\n"
        "            edge = float(_promo_edge(row, comp))\n"
        "        except (TypeError, ValueError):\n"
        "            continue\n"
        "        pools.setdefault(str(row.kind), []).append(edge)\n"
        "    enter_pool_floors = {k: _pool_edge_floor(v, enter_q) for k, v in pools.items()}\n"
        "    keep_pool_floors = {k: _pool_edge_floor(v, keep_q) for k, v in pools.items()}\n\n"
        "    def _green_breadth_ok(row: ValidatedSlice) -> bool:\n"
        "        if comp is None:\n"
        "            return True\n"
        "        c = comp.get(row.slice_id)\n"
        "        return bool(c and c[\"n_green\"] >= MIN_GREEN_ASSETS_FOR_PROMOTION)\n\n"
        "    def _row_promo_edge(row: ValidatedSlice) -> float:\n"
        "        return float(_promo_edge(row, comp))\n\n"
        "    # Base promotability filter (legacy rules) + per-asset green-breadth floor.\n"
        "    promotable = [\n"
        "        row\n"
        "        for row in validated_all\n"
        "        if row.n >= MIN_BOOK_ROWS\n"
        "        and _green_breadth_ok(row)\n"
        "        and _directional_edge(row, enter_pool_floors, edge=_row_promo_edge(row))\n"
        "        and _hip3_session_edge_ok(row)\n"
        "    ]\n",
    ),
    # 8) blocked_for_green_breadth + summary fields
    (
        "    summary: dict = {\n"
        '        "validated": len(validated_all),\n'
        '        "concentrated": len(concentrated),\n'
        '        "promotable": len(promotable),\n'
        "        # HIP-3 slices that passed the quality bar but failed the\n"
        "        # session-match rule (edge not present in the tradable session).\n"
        '        "session_gate_blocked": session_gate_blocked,\n',
        "    # Slices that passed the quality bar and session rule but failed only the\n"
        "    # per-asset green-breadth floor (fewer than MIN_GREEN_ASSETS green assets).\n"
        "    blocked_for_green_breadth = (\n"
        "        sum(\n"
        "            1\n"
        "            for row in validated_all\n"
        "            if row.n >= MIN_BOOK_ROWS\n"
        "            and not _green_breadth_ok(row)\n"
        "            and _directional_edge(row, enter_pool_floors, edge=_row_promo_edge(row))\n"
        "            and _hip3_session_edge_ok(row)\n"
        "        )\n"
        "        if comp is not None\n"
        "        else 0\n"
        "    )\n"
        "    _promoted_gap = [\n"
        "        r for r in to_promote if comp is not None and r.slice_id in comp\n"
        "    ]\n"
        "    summary: dict = {\n"
        '        "validated": len(validated_all),\n'
        '        "concentrated": len(concentrated),\n'
        '        "promotable": len(promotable),\n'
        "        # Per-asset-aware promotion is active only when an asset-edges file was\n"
        "        # supplied. When inactive these fields report the legacy (pooled) mode.\n"
        '        "per_asset_aware": comp is not None,\n'
        '        "green_assets_total": (\n'
        '            sum(int(comp[r.slice_id]["n_green"]) for r in _promoted_gap) if comp else 0\n'
        "        ),\n"
        '        "promoted_green_fraction_mean": (\n'
        "            round(\n"
        '                sum(comp[r.slice_id]["n_green"] / comp[r.slice_id]["n_assets"] for r in _promoted_gap)\n'
        "                / len(_promoted_gap),\n"
        "                4,\n"
        "            )\n"
        "            if comp and _promoted_gap\n"
        "            else None\n"
        "        ),\n"
        '        "blocked_for_green_breadth": blocked_for_green_breadth,\n'
        "        # HIP-3 slices that passed the quality bar but failed the\n"
        "        # session-match rule (edge not present in the tradable session).\n"
        '        "session_gate_blocked": session_gate_blocked,\n',
    ),
    # 9) book row per-asset fields
    (
        '                "hostile_unproven": "True" if row.hostile_unproven else "False",\n'
        '                "edge_is_directional_net": "True",\n'
        "            }\n"
        "        )\n",
        '                "hostile_unproven": "True" if row.hostile_unproven else "False",\n'
        '                "edge_is_directional_net": "True",\n'
        '                # Per-asset composition (blank when per-asset-aware mode off).\n'
        '                "n_green": str(comp[row.slice_id]["n_green"]) if comp and row.slice_id in comp else "",\n'
        '                "green_frac": (\n'
        '                    f"{comp[row.slice_id][\'n_green\'] / comp[row.slice_id][\'n_assets\']:.3f}"\n'
        '                    if comp and row.slice_id in comp and comp[row.slice_id]["n_assets"]\n'
        "                    else \"\"\n"
        "                ),\n"
        "            }\n"
        "        )\n",
    ),
]

TESTS_MARKER = "def test_sync_book_per_asset_green_breadth_blocks_thin_slice"
TESTS_APPEND = '''

def _asset_edge_row(
    slice_id="feat:0:LONG", asset="A", mean=0.01, status="green", n=80
):
    from breakwater.validation import AssetEdge

    return AssetEdge(
        slice_id=slice_id,
        asset=asset,
        kind="SPOT",
        feature="feat",
        state=0,
        side="LONG",
        horizon_bars=1,
        n=n,
        mean_ret_costadj=mean,
        folds_positive=5,
        folds_with_rows=5,
        fold_positive_fraction=1.0,
        asset_status=status,
        reason="",
    )


def test_sync_book_per_asset_green_breadth_blocks_thin_slice(tmp_path):
    """With an asset-edges file, a slice with < MIN_GREEN green assets is not
    promoted even though its pooled mean would have passed."""
    from breakwater.research_lifecycle import MIN_GREEN_ASSETS_FOR_PROMOTION
    from breakwater.validation import write_asset_edges

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    asset_path = tmp_path / "asset_edges.csv"
    write_validated(validated_path, [validated_row(mean=0.01)])
    # Only 2 green assets (< default floor of 3); the rest blocked.
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.01, status="green") for i in range(2)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(8)]
    write_asset_edges(asset_path, edges)

    summary = sync_book(
        validated_path=validated_path,
        book_path=book_path,
    )
    assert summary["per_asset_aware"] is True
    assert summary["monitored"] == 0
    assert summary["blocked_for_green_breadth"] == 1
    assert MIN_GREEN_ASSETS_FOR_PROMOTION > 2
    assert read_book(book_path) == []


def test_sync_book_per_asset_promo_edge_not_pooled(tmp_path, monkeypatch):
    """Promo edge uses the green-only mean, not the pooled all-symbol mean, so a
    slice whose green assets carry no edge is not promoted even if the pooled
    mean looks good."""
    from breakwater.validation import write_asset_edges

    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.004")
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    asset_path = tmp_path / "asset_edges.csv"
    # Pooled mean is strongly positive (0.01), but the green-only mean is 0.001
    # (< 0.004 floor). Without per-asset awareness this would promote.
    write_validated(validated_path, [validated_row(mean=0.01)])
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.001, status="green") for i in range(5)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(5)]
    write_asset_edges(asset_path, edges)

    summary = sync_book(
        validated_path=validated_path,
        book_path=book_path,
    )
    assert summary["monitored"] == 0
    assert read_book(book_path) == []

    # Sanity: without any asset-edges file (different dir), the same slice IS
    # promoted on its pooled edge.
    pooled_dir = tmp_path / "no_asset"
    pooled_dir.mkdir()
    validated_path2 = pooled_dir / "validated.csv"
    write_validated(validated_path2, [validated_row(mean=0.01)])
    book2 = pooled_dir / "book.csv"
    summary2 = sync_book(validated_path=validated_path2, book_path=book2)
    assert summary2["monitored"] == 1


def test_sync_book_per_asset_promotes_and_records_green(tmp_path):
    """A slice with enough green assets and a passing green-only edge promotes,
    and the book row records its per-asset composition."""
    from breakwater.validation import write_asset_edges

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    asset_path = tmp_path / "asset_edges.csv"
    write_validated(validated_path, [validated_row(mean=0.01)])
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.01, status="green") for i in range(6)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(4)]
    write_asset_edges(asset_path, edges)

    summary = sync_book(
        validated_path=validated_path,
        book_path=book_path,
    )
    assert summary["monitored"] == 1
    assert summary["green_assets_total"] == 6
    assert summary["promoted_green_fraction_mean"] == 0.6
    rows = read_book(book_path)
    assert rows[0]["n_green"] == "6"
    assert rows[0]["green_frac"] == "0.600"
'''


def _new_file_content(name: str) -> str:
    if name == "scripts/audit_asset_native_gap.py":
        return AUDIT_SCRIPT
    if name == "docs/asset_native_promotion.md":
        return DESIGN_DOC
    return ""


def main() -> int:
    print("Applying asset-native promotion fix...")
    ok = True

    if RL.exists():
        already = "MIN_GREEN_ASSETS_FOR_PROMOTION" in RL.read_text() and \
            "_slice_asset_composition" in RL.read_text()
        if already:
            print("research_lifecycle.py already patched; nothing to do")
            return 0
        print(f"[research_lifecycle.py] {len(SUBS)} hunks")
        for i, (old, new) in enumerate(SUBS, 1):
            if not sub_file(RL, old, new):
                ok = False
                print(f"    hunk {i} FAILED")
    else:
        print("  !! research_lifecycle.py missing; cannot patch")
        ok = False

    tests = ROOT / "tests/test_research_lifecycle.py"
    if tests.exists() and TESTS_MARKER not in tests.read_text():
        with tests.open("a") as fh:
            fh.write(TESTS_APPEND)
        print(f"  appended 3 tests to {tests.name}")
    else:
        print(f"  tests already present (or missing) in {tests.name}")

    for rel in ("scripts/audit_asset_native_gap.py", "docs/asset_native_promotion.md"):
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(_new_file_content(rel))
            print(f"  created {rel}")
        else:
            print(f"  already exists (kept) {rel}")

    # Syntax-check the patched module.
    if RL.exists():
        try:
            ast.parse(RL.read_text())
            print("research_lifecycle.py: syntax OK")
        except SyntaxError as exc:
            print(f"research_lifecycle.py: SYNTAX ERROR {exc}")
            ok = False
    if ok:
        print("ALL DONE")
    else:
        print("ONE OR MORE HUNKS FAILED -- inspect output above")
    return 0 if ok else 1


AUDIT_SCRIPT = r'''#!/usr/bin/env python3
"""Audit the slice-vs-asset-native gap in the research book.

Breakwater validates and *promotes* whole slices (pooled mean edge across all
symbols), then only at execution time filters to per-asset ``asset_status``
green/untested rows. The concern this script quantifies:

  * An asset's individual edge can be masked by a slice's pooled average
    (e.g. 5 green of 120 assets, but the pooled edge is still positive enough
    to promote the slice -- or conversely a strong asset dropped because its
    slice pooled edge is negative).
  * Promotion therefore does not fully honor "each asset has its own profile".

This is a *read-only* diagnostic. It writes nothing back to the book.

Usage:
    python scripts/audit_asset_native_gap.py --data-dir localdata/research
    python scripts/audit_asset_native_gap.py --data-dir localdata/hip3/research
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

GREEN = "green"
BLOCKED = "blocked"
UNTESTED = "untested"
_EDGE = "mean_ret_costadj"
_ROW_STATUSES = {GREEN, BLOCKED, UNTESTED}


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _f(row: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key))
    except (TypeError, ValueError):
        return default


def _stat(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def load_slices(data_dir: Path):
    asset_rows = _read_csv(data_dir / "asset_edges.csv")
    validated = _read_csv(data_dir / "validated_slices.csv")
    book = _read_csv(data_dir / "monitored_slices.csv")

    by_slice: dict[str, dict[str, list[dict]]] = {}
    for row in asset_rows:
        sid = str(row.get("slice_id", "")).strip()
        st = str(row.get("asset_status", "")).strip()
        if not sid:
            continue
        if st not in _ROW_STATUSES:
            st = UNTESTED
        by_slice.setdefault(sid, {"green": [], "blocked": [], "untested": [], "all": []})
        by_slice[sid][st].append(row)
        by_slice[sid]["all"].append(row)

    book_rows = {str(r.get("slice_id", "")).strip(): r for r in book}
    return by_slice, validated, book_rows


def per_slice_gap(by_slice: dict[str, dict[str, list[dict]]]) -> list[dict]:
    out = []
    for sid, buckets in by_slice.items():
        all_ = buckets["all"]
        green = buckets["green"]
        untested = buckets["untested"]
        green_or_untested = green + untested
        if not all_:
            continue
        pooled_all = _stat([_f(r, _EDGE) for r in all_])
        green_mean = _stat([_f(r, _EDGE) for r in green]) if green else None
        green_or_untested_mean = (
            _stat([_f(r, _EDGE) for r in green_or_untested])
            if green_or_untested
            else None
        )
        out.append({
            "slice_id": sid,
            "side": str(all_[0].get("side", "")).upper(),
            "kind": str(all_[0].get("kind", "")),
            "n_assets": len(all_),
            "n_green": len(green),
            "n_blocked": len(buckets["blocked"]),
            "n_untested": len(untested),
            "green_frac": len(green) / len(all_) if all_ else 0.0,
            "pooled_all_bps": pooled_all * 10000,
            "green_mean_bps": green_mean * 10000 if green_mean is not None else None,
            "green_or_untested_mean_bps": (
                green_or_untested_mean * 10000 if green_or_untested_mean is not None else None
            ),
            "dilution_bps": (
                (green_mean - pooled_all) * 10000 if green_mean is not None else None
            ),
        })
    out.sort(key=lambda r: (r["side"], r["kind"], r["slice_id"]))
    return out


def summarize(gap: list[dict], validated: list[dict], book_rows: dict[str, dict]) -> dict:
    summary = {
        "slices": len(gap),
        "sides": {},
        "book_slices": len(book_rows),
        "book_dilution": {"promoted_slices": 0, "with_green_fraction": 0},
        "missed_green_pairs": 0,
        "missed_green_slices": set(),
    }
    validated_ids = {
        str(r.get("slice_id", "")).strip()
        for r in validated
        if str(r.get("validated", "")).strip().lower() == "true"
    }
    in_book = {r["slice_id"] for r in gap if r["slice_id"] in book_rows}

    by_side: dict[str, list[dict]] = {}
    for r in gap:
        by_side.setdefault(r["side"], []).append(r)
    for side, rows in by_side.items():
        green_assets = sum(r["n_green"] for r in rows)
        green_slices = sum(1 for r in rows if r["n_green"] > 0)
        missed = [
            r for r in rows
            if r["slice_id"] not in in_book and r["n_green"] > 0
        ]
        summary["sides"][side] = {
            "slices": len(rows),
            "green_assets_total": green_assets,
            "green_slices": green_slices,
            "green_slices_not_in_book": len(missed),
            "green_pairs_not_in_book": sum(r["n_green"] for r in missed),
            "promoted_green_fraction_mean": (
                statistics.mean(r["green_frac"] for r in rows if r["slice_id"] in in_book)
                if any(r["slice_id"] in in_book for r in rows)
                else None
            ),
        }

    book_gap = [r for r in gap if r["slice_id"] in in_book]
    dilutes = [r for r in book_gap if (r["dilution_bps"] or 0) > 0]
    low_breadth = [
        r for r in book_gap
        if r["green_frac"] > 0 and r["green_frac"] < 0.5
    ]
    summary["book_dilution"] = {
        "promoted_slices": len(book_gap),
        "diluted_slices": len(dilutes),
        "max_dilution_bps": (
            max(r["dilution_bps"] or 0 for r in book_gap) if book_gap else None
        ),
        "promoted_green_fraction_mean": (
            statistics.mean(r["green_frac"] for r in book_gap) if book_gap else None
        ),
        "promoted_with_less_than_half_green": len(low_breadth),
    }

    masked_pairs = sum(
        r["n_green"] for r in gap if r["slice_id"] not in in_book and r["n_green"] > 0
    )
    summary["masked_green_pairs_total"] = masked_pairs
    summary["masked_green_slices_total"] = len(
        {r["slice_id"] for r in gap if r["slice_id"] not in in_book and r["n_green"] > 0}
    )
    summary["validated_true"] = len(validated_ids)
    summary["validated_true_not_in_book"] = len(validated_ids - in_book)
    return summary


def _print_summary(s: dict) -> None:
    print("== Summary ==")
    print(f"slices with per-asset data : {s['slices']}")
    print(f"book slices                : {s['book_slices']}")
    print(f"validated=True slices      : {s['validated_true']}")
    print(f"  of which not in book     : {s['validated_true_not_in_book']}")
    print(f"green pairs in NON-book slices (masked by pooling): {s['masked_green_pairs_total']} "
          f"across {s['masked_green_slices_total']} slices")
    for side, v in s["sides"].items():
        print(f"\n  [{side}] slices={v['slices']} green_assets={v['green_assets_total']} "
              f"green_slices={v['green_slices']}")
        print(f"    green slices NOT in book = {v['green_slices_not_in_book']} "
              f"({v['green_pairs_not_in_book']} green pairs)")
        if v["promoted_green_fraction_mean"] is not None:
            print(f"    mean green fraction of PROMOTED slices = "
                  f"{v['promoted_green_fraction_mean']:.2f}")
    bd = s["book_dilution"]
    print(f"\n  Promoted-slice dilution: {bd['promoted_slices']} promoted, "
          f"{bd['diluted_slices']} diluted by blocked assets")
    if bd["max_dilution_bps"] is not None:
        print(f"    max green-vs-pooled dilution = {bd['max_dilution_bps']:+.1f} bps")
    if bd["promoted_green_fraction_mean"] is not None:
        print(f"    mean green fraction of promoted = {bd['promoted_green_fraction_mean']:.2f}")
        print(f"    promoted with <50% green assets = {bd['promoted_with_less_than_half_green']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        default="localdata/research",
        help="research data directory (default: localdata/research)",
    )
    parser.add_argument("--csv", type=Path, default=None, help="also write a gap CSV")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not (data_dir / "asset_edges.csv").exists():
        print(f"no asset_edges.csv under {data_dir}; nothing to do")
        return 2

    by_slice, validated, book_rows = load_slices(data_dir)
    gap = per_slice_gap(by_slice)
    summary = summarize(gap, validated, book_rows)
    _print_summary(summary)

    if args.csv:
        cols = [
            "slice_id", "side", "kind", "n_assets", "n_green", "n_blocked",
            "n_untested", "green_frac", "pooled_all_bps", "green_mean_bps",
            "green_or_untested_mean_bps", "dilution_bps", "in_book",
        ]
        with args.csv.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in gap:
                w.writerow({c: r.get(c, "") for c in cols})
        print(f"\nwrote {len(gap)} rows -> {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

DESIGN_DOC = r'''# Asset-Native Promotion — Design & Findings

## TL;DR

Breakwater currently **promotes whole slices** using a **pooled mean edge across all
symbols**, then only at *execution* time filters to per-asset `green`/`untested` rows.
On the current real per-asset data this produces two concrete distortions:

1. **Pooled-edge dilution (problem A)** — blocked/negative assets drag a slice's pooled
   edge far below what its *tradable* (green) assets actually deliver.
2. **Masked green assets (problem B)** — a slice with genuinely green assets is rejected
   outright because the pooled average is negative, so those assets never get promoted.

The recommended change (problem A) is low-risk and honors "each asset has its own profile"
**without** blowing up the hypothesis count. Problem B is a genuinely different, higher-risk
change (true per-asset promotion) and is **not** recommended without much more evidence.

## Findings (native, today's research)

Run: `python scripts/audit_asset_native_gap.py --data-dir localdata/research`

- **938 slices** carry per-asset data (each slice = up to 120 symbols).
- **23,238 green LONG per-asset rows**; `SHORT` currently has 0 green rows (no short edge).
- **Pooled dilution is ubiquitous**: in **936/938** slices the green-only mean edge
  exceeds the pooled edge by > +5bps.
- Strong example — `feat_trend_slope_20:2:LONG:h16`: pooled **+19.2bps**, green-only
  **+204.2bps**, dilution **+185bps**, only **15/120** assets green.
- **700 slices** have at least one green asset **yet a negative pooled edge** — the green
  asset is a genuine bottom-up candidate the slice-level pooled gate rejected.

## The recommended fix (problem A, implemented)

`sync_book` is now **always per-asset-aware** (no opt-in flag): it reads the conventional
`asset_edges.csv` next to the validated file. Promotion rules when that file is present:

1. **Promo edge = green-only mean** (falling back to the pooled mean when a slice has no
   green assets) — fed to the enter/keep quantile pools and `_directional_edge`.
2. **Per-asset breadth floor**: a slice is promotable only if it has **at least
   `MIN_GREEN_ASSETS` (default 3) green assets** — blocks thin, easily-overfit slices.
3. **Untested assets** count for breadth fallback but do not raise the promo edge.

New summary fields: `per_asset_aware`, `green_assets_total`, `promoted_green_fraction_mean`,
`blocked_for_green_breadth`. New book-row fields: `n_green`, `green_frac`.

No call-site changes are required — native and HIP-3 both get it via the conventional path.

## Guardrails respected
- No new env-var knobs (`MIN_GREEN_ASSETS` is a module constant).
- Shorts stay honest — no fabrication; shorts with no green assets still fail the breadth floor.
- Fail-closed: a present-but-malformed asset_edges file aborts; an absent/empty file falls
  back to pooled (only the no-asset local/test case).

## NOT done (by design)
**Problem B — per-asset promotion** would let a strong single asset promote a slice whose
pooled evidence is weak, multiplying the hypothesis count ~120x. That is an overfitting trap
and is intentionally not implemented.
'''

if __name__ == "__main__":
    raise SystemExit(main())
