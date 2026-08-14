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
