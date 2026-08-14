from datetime import datetime, timedelta, timezone
from decimal import Decimal

from breakwater.ledger import Ledger
from breakwater.risk_state import RiskStateStore


def test_ledger_events_are_idempotent(tmp_path):
    ledger = Ledger(tmp_path / "ledger.db")
    assert ledger.append(event_id="one", kind="signal", payload={"x": 1}) is True
    assert ledger.append(event_id="one", kind="signal", payload={"x": 2}) is False
    assert len(ledger.recent_events()) == 1


def test_ledger_pnl_windows(tmp_path):
    ledger = Ledger(tmp_path / "ledger.db")
    now = datetime.now(timezone.utc)
    ledger.append(
        event_id="pnl-one", kind="realized_pnl", payload={},
        occurred_at=now, amount_zar=Decimal("-2.5"),
    )
    assert ledger.seven_day_pnl(now) == Decimal("-2.5")


def test_risk_state_high_water_never_moves_down(tmp_path):
    state = RiskStateStore(tmp_path / "risk.json")
    assert state.observe_equity(Decimal("350")) == Decimal("350")
    assert state.observe_equity(Decimal("300")) == Decimal("350")


def test_risk_state_pnl_is_idempotent(tmp_path):
    state = RiskStateStore(tmp_path / "risk.json")
    now = datetime.now(timezone.utc)
    assert state.append_realized_pnl("fill", Decimal("-3"), now) is True
    assert state.append_realized_pnl("fill", Decimal("-3"), now) is False
    assert state.daily_pnl(now) == Decimal("-3")


def test_old_risk_events_are_pruned(tmp_path):
    state = RiskStateStore(tmp_path / "risk.json")
    old = datetime.now(timezone.utc) - timedelta(days=60)
    state.append_realized_pnl("old", Decimal("-3"), old)
    assert state.load()["realized_pnl_events"] == []
