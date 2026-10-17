#!/usr/bin/env python3
"""Append a ``research_done`` status row built from the MERGED research files.

Why this exists
---------------
Research runs as eight shards (horizon x kind). Each shard's ``research_pass``
appends a ``research_done`` row to its *own* ``localdata/status.csv``, which
is never uploaded; the merge job only receives the four CSV artifacts, so
nothing about the research cycle ever reached the committed ``status.csv``.
The daily print's section 8 therefore had no "Latest research" line and the
operator was blind to discovered / validated counts, the short audit and the
book state unless they opened the CSVs by hand.

This script runs in the merge job (via ``scripts/commit_state.sh research``)
after the shard files have been merged and ``sync_book`` has run. It rebuilds
the payload the engine would have written, from the merged files, and appends
it. Fields that only a shard knows (``frame_errors`` per pair, exact candle
counts fetched) are reported as not propagated rather than guessed.

Idempotent per merged file set: if the newest ``research_done`` row already
describes the current ``validated_slices.csv`` (same mtime fingerprint) the
script exits without writing.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.config import get_settings  # noqa: E402
from breakwater.engine import _short_research_audit  # noqa: E402
from breakwater.status import append_status  # noqa: E402
from breakwater.validation import read_asset_edges, read_validated  # noqa: E402


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _as_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fingerprint(path: Path) -> str:
    if not path.exists():
        return ""
    stat = path.stat()
    return f"{int(stat.st_mtime)}:{stat.st_size}"


def _latest_research_row(status_path: Path) -> dict | None:
    rows = [r for r in _read_rows(status_path) if r.get("stage") == "research_done"]
    return rows[-1] if rows else None


def build_payload(settings, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    research_dir = settings.validated_path.parent
    discovered_path = research_dir / "discovered_slices.csv"
    validated_path = research_dir / "validated_slices.csv"
    asset_edges_path = research_dir / "asset_edges.csv"
    spread_path = research_dir / "spread_slices.csv"
    book_path = research_dir / "monitored_slices.csv"

    discovered_rows = _read_rows(discovered_path)
    discovered = [SimpleNamespace(**row) for row in discovered_rows]
    validated = read_validated(validated_path)
    asset_edges_error = ""
    try:
        asset_edges = read_asset_edges(asset_edges_path) if asset_edges_path.exists() else []
    except RuntimeError as exc:  # summary must not die on one bad file; say so instead
        asset_edges, asset_edges_error = [], str(exc)
    spreads = _read_rows(spread_path)
    book_rows = _read_rows(book_path)

    fail_tokens: Counter = Counter()
    for row in validated:
        for token in str(row.fail_reasons or "").split(","):
            token = token.strip()
            if token:
                fail_tokens[token] += 1

    by_kind_side: Counter = Counter()
    for row in validated:
        if row.validated:
            by_kind_side[f"{row.kind}:{row.side}"] += 1

    assets_by_kind: dict[str, set] = {}
    for edge in asset_edges:
        kind = str(getattr(edge, "kind", "") or "")
        assets_by_kind.setdefault(kind, set()).add(str(getattr(edge, "asset", "") or "").upper())

    horizons = sorted({int(_as_float(getattr(row, "horizon_bars", 0))) for row in validated if getattr(row, "horizon_bars", None)})

    qualifying = [r for r in spreads if str(r.get("qualifies", "")).strip() == "True"]
    spread_best = [
        {
            "spread_id": r.get("spread_id", ""),
            "mean_bps": round(_as_float(r.get("mean_ret_costadj")) * 10000.0, 2),
            "t_nonoverlap": round(_as_float(r.get("t_nonoverlap")), 2),
            "folds": r.get("fold_pattern", ""),
            "market_corr": round(_as_float(r.get("market_corr")), 3),
            "n_nonoverlap": int(_as_float(r.get("n_nonoverlap"))),
            "qualifies": str(r.get("qualifies", "")).strip() == "True",
            "fail_reasons": r.get("fail_reasons", ""),
        }
        for r in spreads[:5]
    ]

    book_status: Counter = Counter(str(r.get("status") or r.get("lifecycle") or "") for r in book_rows)
    validated_ids = {row.slice_id for row in validated if row.validated}
    book_ids = {r.get("slice_id", "") for r in book_rows}

    return {
        "server_time": now.isoformat(),
        "source": "merged_shards",
        "research_horizons": horizons,
        "pairs_with_asset_rows": {kind: len(assets) for kind, assets in sorted(assets_by_kind.items())},
        "frame_errors": "not propagated from shards",
        "pair_errors": "not propagated from shards",
        "spot_candle_count": os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", ""),
        "perp_candle_count": os.getenv("BREAKWATER_PERP_CANDLE_COUNT", ""),
        "discovered_slices": len(discovered),
        "validated_slices": len([row for row in validated if row.validated]),
        "validated_by_kind_side": dict(by_kind_side),
        "regime_confounded_slices": len([row for row in validated if row.regime_confounded]),
        "hostile_unproven_slices": len([row for row in validated if row.hostile_unproven]),
        "top_fail_reasons": fail_tokens.most_common(8),
        "per_asset_edges": {
            "rows": len(asset_edges),
            "green": sum(1 for row in asset_edges if row.asset_status == "green"),
            "blocked": sum(1 for row in asset_edges if row.asset_status == "blocked"),
            "untested": sum(1 for row in asset_edges if row.asset_status == "untested"),
            "error": asset_edges_error,
        },
        "short_audit": _short_research_audit(validated, discovered),
        "spread_research": {
            "rows": len(spreads),
            "qualifying": len(qualifying),
            "best": spread_best,
        },
        "book": {
            "rows": len(book_rows),
            "by_status": dict(book_status),
            "in_validated_pool": len(book_ids & validated_ids),
            "absent_from_pool": len(book_ids - validated_ids),
            "net_edge_floor_enter_bps": os.getenv("BREAKWATER_MIN_NET_EDGE", ""),
        },
        "validated_fingerprint": _fingerprint(validated_path),
    }


def main() -> int:
    settings = get_settings()
    validated_path = settings.validated_path.parent / "validated_slices.csv"
    if not validated_path.exists():
        print("research_summary: no merged validated_slices.csv; nothing to record")
        return 0

    latest = _latest_research_row(settings.status_path)
    if latest:
        try:
            previous = json.loads(latest.get("detail") or "{}")
        except json.JSONDecodeError:
            previous = {}
        if previous.get("validated_fingerprint") == _fingerprint(validated_path):
            print("research_summary: research_done row already current; skipping")
            return 0

    payload = build_payload(settings)
    append_status(settings.status_path, "research_done", os.getenv("BREAKWATER_MODE", "readonly"), json.dumps(payload))
    print(
        "research_summary: appended research_done "
        f"discovered={payload['discovered_slices']} validated={payload['validated_slices']} "
        f"book={payload['book']['rows']} spreads={payload['spread_research']['rows']}/"
        f"{payload['spread_research']['qualifying']} qualifying"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
