"""VALR Perps is a retired venue: an unreachable perps API must not block live.

The choke is at the venue (every authenticated /simple-futures call answers
HTTP 401 with a valid, correctly-permissioned key), so "the perps API is down"
is the *expected* state, not a risk condition. Before this, that expected state
raised GuardianHalt in live mode, which made live mode impossible to start - a
permanent, silent block on the whole live path, spot included.
"""

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from breakwater.config import Settings
from breakwater.engine import BreakwaterEngine, GuardianHalt, VALR_PERPS_RETIRED
from breakwater.models import PairType
from breakwater.valr import ValrError


class PerpsChokedClient:
    """A client that behaves like the real account: spot works, perps 401s."""

    def exchange_status(self):
        return {"status": "online"}

    def server_time(self):
        return {"epochTime": int(datetime.now(timezone.utc).timestamp())}

    def pairs(self, pair_type=None):
        from breakwater.models import PairSpec

        return [
            PairSpec(
                "BTCZAR", "BTC", "ZAR", True,
                Decimal("0.00001"), Decimal("10"), Decimal("10"), Decimal("1000000"),
                Decimal("1"), 6, PairType.SPOT,
            ),
            # Needed to value a perp position's USDC margin in ZAR.
            PairSpec(
                "USDCZAR", "USDC", "ZAR", True,
                Decimal("0.01"), Decimal("10"), Decimal("10"), Decimal("1000000"),
                Decimal("1"), 2, PairType.SPOT,
            ),
        ]

    def current_api_key(self):
        return {"permissions": ["view access", "trade"]}

    def balances(self):
        return [
            {
                "currency": "ZAR",
                "total": "500",
                "available": "500",
                "reserved": "0",
            }
        ]

    def open_positions(self):
        return []

    def open_orders(self):
        return []

    def conditional_orders(self):
        return []

    def market_summary(self, pair):
        from breakwater.models import MarketSummary

        return MarketSummary(
            pair, Decimal("1"), Decimal("1"), Decimal("1"), Decimal("1"),
            Decimal("1000000"), datetime.now(timezone.utc),
        )

    def perps_positions(self):
        raise ValrError(
            "VALR authentication rejected request with HTTP 401"
        )


def _mandate():
    from breakwater.risk import RiskPolicy

    return RiskPolicy(
        initial_equity_zar=Decimal("500"),
        absolute_equity_floor_zar=Decimal("450"),
        max_total_loss_zar=Decimal("50"),
        max_drawdown_fraction=Decimal("0.10"),
        risk_per_trade_zar=Decimal("5"),
        daily_loss_limit_zar=Decimal("15"),
        seven_day_loss_limit_zar=Decimal("30"),
        max_aggregate_open_risk_zar=Decimal("10"),
        max_position_notional_zar=Decimal("100"),
        max_effective_leverage=Decimal("1"),
        perp_leverage_cap=Decimal("1"),
        max_positions=1,
    )


def _live_settings(tmp_path):
    return Settings(
        api_key="key",
        api_secret="secret",
        mode="live",
        live_ack="I_ACCEPT_BREAKWATER_LIVE_RISK",
        data_dir=Path(tmp_path),
        mandate=_mandate(),
    )


def test_retired_is_the_default():
    assert VALR_PERPS_RETIRED is True


def test_a_401_perps_probe_does_not_halt_live(tmp_path, monkeypatch):
    """The regression this pins: live mode was unrunnable on this account."""
    import breakwater.engine as engine_module

    monkeypatch.setattr(engine_module, "VALR_PERPS_RETIRED", True)
    engine = BreakwaterEngine(_live_settings(tmp_path), client=PerpsChokedClient())
    result = engine.guardian()
    assert result["perps_api"] == "retired"
    assert result["valr_perps_retired"] is True
    # The evidence is kept, not erased - the choke stays visible.
    assert "401" in result["perp_state_error"]
    assert result["risk_allowed"] in (True, False)  # it got past the perps step


def test_the_switch_restores_the_halt_when_turned_off(tmp_path, monkeypatch):
    """Retirement is a decision, not a deletion: opting out restores the halt."""
    import breakwater.engine as engine_module

    monkeypatch.setattr(engine_module, "VALR_PERPS_RETIRED", False)
    engine = BreakwaterEngine(_live_settings(tmp_path), client=PerpsChokedClient())
    with pytest.raises(GuardianHalt, match="unverifiable"):
        engine.guardian()


def test_readonly_mode_never_halted_on_perps(tmp_path, monkeypatch):
    import breakwater.engine as engine_module

    monkeypatch.setattr(engine_module, "VALR_PERPS_RETIRED", False)
    settings = Settings(
        api_key="key",
        api_secret="secret",
        mode="readonly",
        live_ack="off",
        data_dir=Path(tmp_path),
        mandate=_mandate(),
    )
    engine = BreakwaterEngine(settings, client=PerpsChokedClient())
    result = engine.guardian()
    assert result["perps_api"] == "unavailable"


def test_a_working_perps_api_is_still_used(tmp_path, monkeypatch):
    """If the venue ever answers, the retirement must not hide real exposure."""
    import breakwater.engine as engine_module

    class Working(PerpsChokedClient):
        def perps_positions(self):
            return [{"pair": "BTCUSDC", "margin": "10", "unrealised_pnl": "1"}]

    monkeypatch.setattr(engine_module, "VALR_PERPS_RETIRED", True)
    engine = BreakwaterEngine(_live_settings(tmp_path), client=Working())
    result = engine.guardian()
    assert result["perps_api"] == "available"
    assert result["perp_positions"] == 1
