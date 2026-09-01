from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from breakwater.config import Settings
from breakwater.engine import BreakwaterEngine, GuardianHalt
from breakwater.models import PairSpec, PairType
from breakwater.risk import RiskPolicy


def mandate():
    return RiskPolicy(
        initial_equity_zar=Decimal("331.45"),
        absolute_equity_floor_zar=Decimal("222.07"),
        max_total_loss_zar=Decimal("109.38"),
        max_drawdown_fraction=Decimal("0.33"),
        risk_per_trade_zar=Decimal("6.63"),
        daily_loss_limit_zar=Decimal("9.94"),
        seven_day_loss_limit_zar=Decimal("19.89"),
        max_aggregate_open_risk_zar=Decimal("6.63"),
        max_position_notional_zar=Decimal("200.00"),
        max_effective_leverage=Decimal("1"),
        perp_leverage_cap=Decimal("3"),
        max_positions=1,
    )


class PublicClient:
    def exchange_status(self):
        return {"status": "online"}

    def server_time(self):
        return {"epochTime": int(datetime.now(timezone.utc).timestamp())}

    def pairs(self, pair_type=None):
        return [PairSpec(
            "ETHZAR", "ETH", "ZAR", True,
            Decimal("0.001"), Decimal("10"), Decimal("10"), Decimal("100000"),
            Decimal("1"), 3, PairType.SPOT,
        )]


def settings(tmp_path, mode="readonly", ack="off", with_mandate=True):
    return Settings(
        api_key=None,
        api_secret=None,
        mode=mode,
        live_ack=ack,
        data_dir=Path(tmp_path),
        mandate=mandate() if with_mandate else None,
    )


def test_public_guardian_runs_without_credentials(tmp_path):
    engine = BreakwaterEngine(settings(tmp_path), client=PublicClient())
    result = engine.guardian()
    assert result["authenticated"] is False
    assert result["active_spot_pairs"] == 1


def test_live_mode_requires_credentials_and_ack(tmp_path):
    engine = BreakwaterEngine(settings(tmp_path, mode="live"), client=PublicClient())
    with pytest.raises(GuardianHalt, match="not armed"):
        engine.startup_assertions()


def test_live_mode_requires_mandate(tmp_path):
    configured = Settings(
        api_key="key",
        api_secret="secret",
        mode="live",
        live_ack="I_ACCEPT_BREAKWATER_LIVE_RISK",
        data_dir=Path(tmp_path),
        mandate=None,
    )
    engine = BreakwaterEngine(configured, client=PublicClient())
    with pytest.raises(GuardianHalt, match="mandate"):
        engine.startup_assertions()


def test_exchange_offline_halts(tmp_path):
    client = PublicClient()
    client.exchange_status = lambda: {"status": "offline"}
    engine = BreakwaterEngine(settings(tmp_path), client=client)
    with pytest.raises(GuardianHalt, match="does not report online"):
        engine.guardian()


def test_authenticated_guardian_requires_mandate(tmp_path):
    configured = Settings(
        api_key="key",
        api_secret="secret",
        mode="readonly",
        live_ack="off",
        data_dir=Path(tmp_path),
        mandate=None,
    )
    engine = BreakwaterEngine(configured, client=PublicClient())
    with pytest.raises(GuardianHalt, match="mandate"):
        engine.guardian()


def test_live_mode_requires_promoted_strategy(tmp_path):
    configured = Settings(
        api_key="key",
        api_secret="secret",
        mode="live",
        live_ack="I_ACCEPT_BREAKWATER_LIVE_RISK",
        data_dir=Path(tmp_path),
        mandate=mandate(),
    )
    engine = BreakwaterEngine(configured, client=PublicClient())
    with pytest.raises(GuardianHalt, match="no strategy"):
        engine.startup_assertions()


class ResearchClient(PublicClient):
    def market_summaries(self):
        from breakwater.models import MarketSummary

        return [MarketSummary(
            "ETHZAR", Decimal("0.05"), Decimal("0.0501"), Decimal("0.05"),
            Decimal("0.05"), Decimal("100000"), datetime.now(timezone.utc),
        )]

    def perps_symbol_info(self):
        from breakwater.models import PerpSymbol

        return [PerpSymbol(
            pair="BTCUSDC", base_asset="BTC", max_leverage=Decimal("10"),
            min_notional=Decimal("11"), min_margin=Decimal("2"),
            mark_price=Decimal("1500"), price_decimal_places=6,
            volume=Decimal("500000"), open_interest=Decimal("900"),
        )]


def test_research_halts_instead_of_writing_empty_artifacts(tmp_path, monkeypatch):
    engine = BreakwaterEngine(
        settings(tmp_path, mode="readonly"),
        client=ResearchClient(),
    )
    monkeypatch.setattr(engine, "_frames", lambda targets, server_time: ({}, {}))
    with pytest.raises(GuardianHalt, match="no research frames"):
        engine.research_pass()


def test_health_reports_committed_state(tmp_path):
    engine = BreakwaterEngine(
        settings(tmp_path, mode="readonly"),
        client=ResearchClient(),
    )
    report = engine.health()
    assert report["mode"] == "readonly"
    assert report["universe"]["status"] == "missing"
    assert report["book"]["rows"] == 0
    assert report["paper_open_positions"] == 0


def _write_book_row(path, slice_id="feat:0:LONG"):
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "slice_id", "kind", "feature", "state", "side", "status",
                "mean_ret_costadj",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "slice_id": slice_id,
            "kind": "PERP",
            "feature": "feat",
            "state": "0",
            "side": "LONG",
            "status": "monitored",
            "mean_ret_costadj": "0.001",
        })


def _write_green_native_log(path, slice_id="feat:0:LONG", n=10):
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["slice_id", "outcome", "exit_reason", "pnl_zar"],
        )
        writer.writeheader()
        for _ in range(n):
            writer.writerow({
                "slice_id": slice_id,
                "outcome": "win",
                "exit_reason": "target",
                "pnl_zar": "1.0",
            })


def test_shadow_scan_native_only_does_not_require_hip3_asset_edges(tmp_path, monkeypatch):
    """A native-only paper run must not crash just because HIP-3 research has
    not produced its asset_edges.csv yet. Fail-closed applies per active lane.

    Regression guard for the fail-closed change: reading the HIP-3 asset-edge
    file unconditionally would break every native-only run before the HIP-3
    research workflow has generated that file.
    """
    from breakwater.engine import BreakwaterEngine as _Engine
    from breakwater.validation import AssetEdge, write_asset_edges

    engine = _Engine(settings(tmp_path, mode="readonly"), client=PublicClient())

    now = datetime.now(timezone.utc)
    monkeypatch.setattr(engine, "_server_state", lambda: (now, {}))
    monkeypatch.setattr(engine, "_universe", lambda: _FakeUniverse())
    monkeypatch.setattr(engine, "_frames", lambda targets, server_time: ({}, {}))
    monkeypatch.setattr(engine, "_hip3_paper_ready", lambda: False)

    # Give the NATIVE lane enough positive closes that the green gate lets it
    # trade, so the native per-asset lookup is actually read. Leave the HIP-3
    # asset-edge file absent.
    _write_green_native_log(engine.settings.paper_log_path, slice_id="feat:0:LONG")
    _write_book_row(engine.settings.book_path, slice_id="feat:0:LONG")

    write_asset_edges(engine.settings.asset_edges_path, [
        AssetEdge(
            slice_id="feat:0:LONG",
            asset="BTCUSDC",
            kind="PERP",
            feature="feat",
            state=0,
            side="LONG",
            horizon_bars=1,
            n=40,
            mean_ret_costadj=0.001,
            folds_positive=4,
            folds_with_rows=5,
            fold_positive_fraction=0.8,
            asset_status="green",
        )
    ])

    result = engine.shadow_scan(max_pairs=1)
    assert result["hip3_paper"]["active"] is False
    assert result["per_asset_gate"]["native_rows"] >= 1
    assert result["per_asset_gate"]["hip3_rows"] == 0


def test_shadow_scan_active_native_lane_requires_native_asset_edges(tmp_path, monkeypatch):
    """Fail-closed still applies to a lane that IS active: if the native book
    has monitored rows but native asset_edges.csv is missing, shadow_scan raises
    rather than silently trading without the per-asset gate."""
    from breakwater.engine import BreakwaterEngine as _Engine

    engine = _Engine(settings(tmp_path, mode="readonly"), client=PublicClient())

    now = datetime.now(timezone.utc)
    monkeypatch.setattr(engine, "_server_state", lambda: (now, {}))
    monkeypatch.setattr(engine, "_universe", lambda: _FakeUniverse())
    monkeypatch.setattr(engine, "_frames", lambda targets, server_time: ({}, {}))
    monkeypatch.setattr(engine, "_hip3_paper_ready", lambda: False)

    _write_green_native_log(engine.settings.paper_log_path, slice_id="feat:0:LONG")
    _write_book_row(engine.settings.book_path, slice_id="feat:0:LONG")

    with pytest.raises(RuntimeError, match="asset edges file missing"):
        engine.shadow_scan(max_pairs=1)


class _FakeUniverse:
    def ranked(self, kind, max_pairs):
        return []

    def symbols(self, kind):
        return []



def test_universe_reingests_legacy_file_without_perp_volumes(tmp_path):
    from breakwater.universe import UniverseRow, UniverseSnapshot, write_universe

    legacy = UniverseSnapshot(
        rows=(UniverseRow(
            symbol="0GUSDC", kind="PERP", base="0G", quote="USDC", active=True,
            liquidity_rank=1, quote_volume=Decimal(0), mark_price=Decimal("0.1"),
            max_leverage=Decimal("3"), min_notional=Decimal("11"),
            min_margin=Decimal("2"), as_of="2026-08-14T11:00:00+00:00",
        ),),
        as_of="2026-08-14T11:00:00+00:00",
    )
    engine = BreakwaterEngine(settings(tmp_path), client=ResearchClient())
    write_universe(engine.settings.universe_path, legacy)
    snapshot = engine._universe()
    perps = [row for row in snapshot.rows if row.kind == "PERP"]
    assert any(row.quote_volume > 0 for row in perps)


def test_fee_bps_env_falls_back_on_invalid_or_negative(monkeypatch):
    from breakwater import engine

    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "not-a-number")
    assert engine._fee_bps_env("BREAKWATER_SPOT_FEE_BPS", "70") == 70.0
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "-5")
    assert engine._fee_bps_env("BREAKWATER_SPOT_FEE_BPS", "70") == 70.0
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "42")
    assert engine._fee_bps_env("BREAKWATER_SPOT_FEE_BPS", "70") == 42.0
    monkeypatch.delenv("BREAKWATER_SPOT_FEE_BPS", raising=False)
    assert engine._fee_bps_env("BREAKWATER_SPOT_FEE_BPS", "70") == 70.0
