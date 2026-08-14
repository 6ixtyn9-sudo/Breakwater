from datetime import datetime, timezone
from pathlib import Path

import pytest

from breakwater.config import Settings
from breakwater.engine import BreakwaterEngine, GuardianHalt
from breakwater.models import PairSpec, PairType


class PublicClient:
    def exchange_status(self):
        return {"status": "online"}

    def server_time(self):
        return {"epochTime": int(datetime.now(timezone.utc).timestamp())}

    def pairs(self, pair_type=None):
        return [PairSpec(
            "ETHZAR", "ETH", "ZAR", True,
            __import__("decimal").Decimal("0.001"),
            __import__("decimal").Decimal("10"),
            __import__("decimal").Decimal("10"),
            __import__("decimal").Decimal("100000"),
            __import__("decimal").Decimal("1"),
            3,
            PairType.SPOT,
        )]


def settings(tmp_path, mode="readonly", ack="off"):
    return Settings(
        api_key=None,
        api_secret=None,
        subaccount_id=None,
        mode=mode,
        live_ack=ack,
        data_dir=Path(tmp_path),
        price_candidates_url=None,
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


def test_exchange_offline_halts(tmp_path):
    client = PublicClient()
    client.exchange_status = lambda: {"status": "offline"}
    engine = BreakwaterEngine(settings(tmp_path), client=client)
    with pytest.raises(GuardianHalt, match="does not report online"):
        engine.guardian()


def test_live_mode_requires_promoted_strategy(tmp_path):
    configured = Settings(
        api_key="key",
        api_secret="secret",
        subaccount_id="42",
        mode="live",
        live_ack="I_ACCEPT_BREAKWATER_LIVE_RISK",
        data_dir=Path(tmp_path),
        price_candidates_url=None,
    )
    engine = BreakwaterEngine(configured, client=PublicClient())
    with pytest.raises(GuardianHalt, match="no strategy"):
        engine.startup_assertions()
