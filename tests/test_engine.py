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
