"""OI-cohort lane (perp_groups.py): identity, assignment, scoping."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from breakwater import perp_groups as pg
from breakwater.config import Settings
from breakwater.engine import BreakwaterEngine
from breakwater.positioning import POSITIONING_DIRNAME
from breakwater.universe import UniverseRow, UniverseSnapshot

NOW = datetime(2026, 10, 27, 9, 0, tzinfo=timezone.utc)


def test_slice_tag_roundtrip_keeps_horizon_suffix_last():
    sid = pg.tag_slice_id("feat_funding_rate:2:SHORT", "oi_hi")
    assert sid == "feat_funding_rate@oi_hi:2:SHORT"
    assert pg.tag_slice_id(sid, "oi_hi") == sid  # idempotent
    assert pg.group_of_slice(sid + ":h24") == "oi_hi"
    assert pg.group_of_slice("feat_funding_rate:2:SHORT:h24") is None
    assert pg.group_of_slice("hip3_xyz_equity_cUSDC:feat_x:1:LONG:h12") is None


def _tape(coins_oi: dict[str, float], hours: int = 48) -> pd.DataFrame:
    rows = []
    for h in range(hours):
        start = NOW - timedelta(hours=hours - h)
        for coin, oi in coins_oi.items():
            rows.append({"coin": coin, "start": start, "pos_oi_notional": oi, "pos_funding": 0.0})
    return pd.DataFrame(rows)


def test_assign_oi_groups_cuts_terciles_and_skips_unmapped_pairs():
    coins = {f"C{i:02d}": float(1000 - i * 10) for i in range(15)}
    pairs = [f"{c}USDC" for c in coins] + ["xyz:TSLA", "NOCOINUSDC"]
    groups = pg.assign_oi_groups(pairs, _tape(coins), now=NOW)
    assert "XYZ:TSLA" not in groups and "NOCOINUSDC" not in groups
    assert {g: sum(1 for v in groups.values() if v == g) for g in pg.GROUP_NAMES} == {
        "oi_hi": 5, "oi_mid": 5, "oi_lo": 5,
    }
    assert groups["C00USDC"] == "oi_hi" and groups["C14USDC"] == "oi_lo"
    # stale OI (outside the window) does not count; too few groupable pairs -> no groups
    old = _tape(coins).assign(start=lambda d: d["start"] - timedelta(days=30))
    assert pg.assign_oi_groups(pairs, old, now=NOW) == {}
    assert pg.assign_oi_groups(pairs[:6], _tape(coins), now=NOW) == {}
    assert pg.assign_oi_groups(pairs, None, now=NOW) == {}


def test_book_split_and_membership_from_asset_edges():
    rows = [
        {"slice_id": "feat_ret_5:0:LONG:h12"},
        {"slice_id": "feat_premium@oi_lo:2:SHORT:h24"},
        {"slice_id": "feat_ret_5@oi_lo:0:LONG:h12"},
        {"slice_id": "feat_cci_20@oi_hi:2:SHORT:h24"},
    ]
    plain, grouped = pg.split_book_rows(rows)
    assert [r["slice_id"] for r in plain] == ["feat_ret_5:0:LONG:h12"]
    assert sorted(grouped) == ["oi_hi", "oi_lo"] and len(grouped["oi_lo"]) == 2
    lookup = {
        ("feat_ret_5:0:LONG:h12", "BTCUSDC"): "green",
        ("feat_premium@oi_lo:2:SHORT:h24", "pepeusdc"): "untested",
        ("feat_premium@oi_lo:2:SHORT:h24", "WIFUSDC"): "blocked",
        ("feat_cci_20@oi_hi:2:SHORT:h24", "BTCUSDC"): "green",
    }
    assert pg.group_members_from_asset_edges(lookup) == {"oi_lo": {"PEPEUSDC", "WIFUSDC"}, "oi_hi": {"BTCUSDC"}}


def test_family_key_keeps_cohort_and_global_slices_apart():
    from breakwater.research_lifecycle import _family_key
    from breakwater.validation import ValidatedSlice

    def row(sid, h):
        return ValidatedSlice(
            slice_id=sid, kind="PERP", feature="feat_premium", state=2, side="SHORT", folds=5,
            walk_forward_pass_pattern="11111", walk_forward_pass_count=5,
            fold_mean_rets="0.001,0.001,0.001,0.001,0.001", fold_sizes="20,20,20,20,20",
            n=500, mean_ret_costadj=0.004, p_value=0.3, validated=True, horizon_bars=h,
        )

    assert _family_key(row("feat_premium:2:SHORT:h12", 12)) == _family_key(row("feat_premium:2:SHORT:h24", 24))
    assert _family_key(row("feat_premium@oi_lo:2:SHORT:h12", 12)) != _family_key(row("feat_premium:2:SHORT:h12", 12))
    assert _family_key(row("feat_premium@oi_lo:2:SHORT:h12", 12)) == _family_key(row("feat_premium@oi_lo:2:SHORT:h24", 24))


# --- research_pass end to end ---------------------------------------------


class _Client:
    def exchange_status(self):
        return {"status": "online"}

    def server_time(self):
        return {"epochTime": int(datetime.now(timezone.utc).timestamp())}

    def pairs(self, pair_type=None):
        from breakwater.models import PairSpec, PairType

        return [PairSpec(
            "ETHZAR", "ETH", "ZAR", True, Decimal("0.001"), Decimal("10"), Decimal("10"),
            Decimal("100000"), Decimal("1"), 3, PairType.SPOT,
        )]


def _frame(seed: int, now: datetime, n: int = 420) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, n)))
    start = pd.date_range(now - timedelta(hours=n), periods=n, freq="h", tz="UTC")
    return pd.DataFrame({
        "start": start, "open": close * 0.999, "high": close * 1.004, "low": close * 0.996,
        "close": close, "volume": rng.uniform(1e5, 5e5, n),
    })


def _write_tape(data_dir: Path, coins_oi: dict[str, float], now: datetime) -> None:
    directory = data_dir / POSITIONING_DIRNAME
    directory.mkdir(parents=True)
    with (directory / "2026-W44.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["snapshot_at", "snapshot_hour", "coin", "oi_notional_usd", "funding_hourly", "premium", "imbalance_5"])
        writer.writeheader()
        for h in range(30):
            hour = now - timedelta(hours=30 - h)
            for coin, oi in coins_oi.items():
                writer.writerow({
                    "snapshot_at": hour.isoformat(), "snapshot_hour": hour.strftime("%Y-%m-%dT%H:00Z"),
                    "coin": coin, "oi_notional_usd": oi, "funding_hourly": 1e-5, "premium": 0.0001, "imbalance_5": 0.0,
                })


def test_research_pass_adds_cohort_slices_scoped_to_their_members(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_RESEARCH_HORIZONS", "12")
    monkeypatch.setenv("BREAKWATER_RESEARCH_SHARD", "h12_PERP")  # production always shards -> :h suffix
    monkeypatch.setenv("BREAKWATER_POSITIONING_FUNDING_FETCH", "0")
    monkeypatch.setenv("BREAKWATER_PERP_GROUP_OI_DAYS", "7")
    # Keep the pass small: four price features are enough to prove the plumbing.
    import breakwater.engine as eng

    monkeypatch.setattr(eng, "FEATURE_COLUMNS", ["feat_ret_5", "feat_ret_20", "feat_rsi_14", "feat_cci_20"])
    # the lane defaults to positioning features; the fake frames carry none, so scope it explicitly
    monkeypatch.setenv("BREAKWATER_PERP_GROUP_FEATURES", "feat_ret_5,feat_rsi_14")

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    coins = {f"C{i:02d}": float(5_000_000 - i * 100_000) for i in range(15)}
    pairs = [f"{c}USDC" for c in coins]
    _write_tape(tmp_path, coins, now)

    settings = Settings(api_key=None, api_secret=None, mode="readonly", live_ack="off", data_dir=tmp_path, mandate=None)
    engine = BreakwaterEngine(settings, client=_Client())
    def urow(p, kind, i):
        return UniverseRow(symbol=p, kind=kind, base=p[:-4], quote=p[-4:], active=True, liquidity_rank=i + 1,
                           quote_volume=Decimal("1"), mark_price=Decimal("1"), max_leverage=Decimal("10"),
                           min_notional=Decimal("10"), min_margin=Decimal("1"), as_of=now.isoformat(), venue="hyperliquid")

    rows = (urow("ETHUSDC", "SPOT", 0), *(urow(p, "PERP", i) for i, p in enumerate(pairs)))
    monkeypatch.setattr(engine, "_universe", lambda: UniverseSnapshot(rows=rows, as_of=now.isoformat()))
    frames = {p: _frame(i, now).assign(symbol=p) for i, p in enumerate(["ETHUSDC", *pairs])}
    monkeypatch.setattr(engine, "_frames", lambda targets, server_time: (dict(frames), {}))

    result = engine.research_pass(max_pairs=50)

    assert result["perp_groups"]["pairs"] == {"oi_hi": 5, "oi_mid": 5, "oi_lo": 5}
    discovered = list(csv.DictReader(settings.discovered_path.open()))
    cohort = [r for r in discovered if "@" in r["slice_id"]]
    glob = [r for r in discovered if "@" not in r["slice_id"]]
    assert cohort and glob
    assert all(r["feature"].startswith("feat_") and "@" not in r["feature"] for r in cohort)
    assert all(r["slice_id"].endswith(":h12") for r in cohort)
    assert {r["feature"] for r in cohort} <= {"feat_ret_5", "feat_rsi_14"}
    assert {r["feature"] for r in glob} == {"feat_ret_5", "feat_ret_20", "feat_rsi_14", "feat_cci_20"}
    assert result["perp_groups"]["features"] == 2

    members = {"oi_hi": set(pairs[:5]), "oi_mid": set(pairs[5:10]), "oi_lo": set(pairs[10:])}
    edges = list(csv.DictReader(settings.asset_edges_path.open()))
    seen = {}
    for e in edges:
        group = pg.group_of_slice(e["slice_id"])
        if group is not None:
            seen.setdefault(group, set()).add(e["asset"])
    assert seen and all(seen[g] <= members[g] for g in seen)
    # and the global slices still see the whole pool
    assert {e["asset"] for e in edges if e["kind"] == "PERP" and pg.group_of_slice(e["slice_id"]) is None} == set(pairs)

    # kill switch: no cohort rows at all
    monkeypatch.setenv("BREAKWATER_PERP_GROUPS", "0")
    result = engine.research_pass(max_pairs=50)
    assert result["perp_groups"] == {"enabled": False}
    assert not any("@" in r["slice_id"] for r in csv.DictReader(settings.discovered_path.open()))


def test_feature_scope_defaults_to_positioning_columns(monkeypatch):
    from breakwater.positioning_features import POSITIONING_FEATURE_COLUMNS

    available = ["feat_ret_5", *POSITIONING_FEATURE_COLUMNS, "feat_rsi_14"]
    monkeypatch.delenv("BREAKWATER_PERP_GROUP_FEATURES", raising=False)
    assert pg.feature_columns(available) == list(POSITIONING_FEATURE_COLUMNS)
    monkeypatch.setenv("BREAKWATER_PERP_GROUP_FEATURES", "feat_rsi_14, feat_missing")
    assert pg.feature_columns(available) == ["feat_rsi_14"]


def test_shadow_scan_monitors_cohort_rows_on_member_frames_only(tmp_path, monkeypatch):
    """A cohort row must never see a frame research did not judge it on."""
    import breakwater.engine as eng
    from breakwater.validation import AssetEdge, write_asset_edges

    settings = Settings(api_key=None, api_secret=None, mode="readonly", live_ack="off", data_dir=tmp_path, mandate=None)
    engine = BreakwaterEngine(settings, client=_Client())
    now = datetime.now(timezone.utc)

    class Universe:
        def ranked(self, kind, max_pairs):
            return ["BTCUSDC", "ETHUSDC"] if kind == "PERP" else []

        def symbols(self, kind):
            return self.ranked(kind, 10)

    frames = {p: _frame(i, now).assign(symbol=p) for i, p in enumerate(["BTCUSDC", "ETHUSDC"])}
    monkeypatch.setattr(engine, "_server_state", lambda: (now, {}))
    monkeypatch.setattr(engine, "_universe", lambda: Universe())
    monkeypatch.setattr(engine, "_frames", lambda targets, server_time: (dict(frames), {}))
    monkeypatch.setattr(engine, "_hip3_paper_ready", lambda: False)
    monkeypatch.setattr(engine, "_run_engines", lambda *a, **k: [])

    # book: one global row, one oi_hi cohort row; both slices green in paper
    book = settings.book_path
    book.parent.mkdir(parents=True, exist_ok=True)
    fields = ["slice_id", "kind", "feature", "state", "side", "status", "mean_ret_costadj"]
    with book.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for sid in ("feat_ret_5:0:LONG:h12", "feat_ret_5@oi_hi:0:LONG:h12"):
            writer.writerow({"slice_id": sid, "kind": "PERP", "feature": "feat_ret_5", "state": "0", "side": "LONG",
                             "status": "monitored", "mean_ret_costadj": "0.001"})
    with settings.paper_log_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["slice_id", "outcome", "exit_reason", "pnl_zar"])
        writer.writeheader()
        for _ in range(10):
            writer.writerow({"slice_id": "feat_ret_5:0:LONG:h12", "outcome": "win", "exit_reason": "target", "pnl_zar": "1.0"})

    def edge(sid, asset):
        return AssetEdge(slice_id=sid, asset=asset, kind="PERP", feature="feat_ret_5", state=0, side="LONG",
                         horizon_bars=12, n=40, mean_ret_costadj=0.001, folds_positive=4, folds_with_rows=5,
                         fold_positive_fraction=0.8, asset_status="green")

    write_asset_edges(settings.asset_edges_path, [
        edge("feat_ret_5:0:LONG:h12", "BTCUSDC"), edge("feat_ret_5:0:LONG:h12", "ETHUSDC"),
        edge("feat_ret_5@oi_hi:0:LONG:h12", "BTCUSDC"),  # ETH was not in oi_hi when this was validated
    ])

    calls = []

    def fake_monitor(rows, frames_by_kind, **kwargs):
        calls.append(([r["slice_id"] for r in rows], sorted(frames_by_kind.get("PERP", {}))))
        return [], []

    monkeypatch.setattr(eng, "monitor_book", fake_monitor)
    engine.shadow_scan(max_pairs=5)

    assert calls == [
        (["feat_ret_5:0:LONG:h12"], ["BTCUSDC", "ETHUSDC"]),
        (["feat_ret_5@oi_hi:0:LONG:h12"], ["BTCUSDC"]),
    ]
