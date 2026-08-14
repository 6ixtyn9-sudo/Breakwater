import json
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from breakwater.models import Side
from breakwater.monitor import SliceSignal
from breakwater.paper_trade import (
    read_positions,
    run_paper_cycle,
)
from breakwater.risk import RiskPolicy


def policy():
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


def frame_with_bar(close, high=None, low=None):
    return pd.DataFrame([{
        "start": pd.Timestamp("2026-08-14T10:00:00Z"),
        "symbol": "BTCUSDC",
        "open": close,
        "high": high if high is not None else close,
        "low": low if low is not None else close,
        "close": close,
        "volume": 100,
    }])


def open_position(side="BUY", entry="100", stop="95", bars="3"):
    return [{
        "signal_id": "sig1",
        "pair": "BTCUSDC",
        "kind": "PERP",
        "slice_id": "feat:0:LONG",
        "side": side,
        "entry_price": entry,
        "stop_price": stop,
        "notional_zar": "150",
        "bars_held": bars,
    }]


def test_open_position_stops_out_and_journals(tmp_path):
    positions_path = tmp_path / "positions.json"
    positions_path.write_text(json.dumps(open_position()))
    signals = []
    result = run_paper_cycle(
        signals=signals,
        frames={"BTCUSDC": frame_with_bar(close=94, low=93)},
        policy=policy(),
        usdc_zar=Decimal("16.29"),
        positions_path=positions_path,
        log_path=tmp_path / "log.csv",
        cooldown_path=tmp_path / "cooldown.json",
        book_path=tmp_path / "book.csv",
        server_time=datetime.now(timezone.utc),
    )
    assert result["closed"] == 1
    assert result["open"] == 0
    journal = json.loads((tmp_path / "cooldown.json").read_text())
    assert journal[0]["slice_id"] == "feat:0:LONG"
    assert journal[0]["pnl_zar"].startswith("-")


def test_open_position_hits_target_and_wins(tmp_path):
    positions_path = tmp_path / "positions.json"
    positions_path.write_text(json.dumps(open_position()))
    result = run_paper_cycle(
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=111, high=111)},
        policy=policy(),
        usdc_zar=Decimal("16.29"),
        positions_path=positions_path,
        log_path=tmp_path / "log.csv",
        cooldown_path=tmp_path / "cooldown.json",
        book_path=tmp_path / "book.csv",
        server_time=datetime.now(timezone.utc),
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "win"
    assert float(log.iloc[0]["pnl_zar"]) > 0


def test_new_signal_opens_position_when_slot_free(tmp_path):
    now = datetime.now(timezone.utc)
    signals = [SliceSignal(
        signal_id="sig2",
        pair="BTCUSDC",
        kind="PERP",
        slice_id="feat:0:LONG",
        feature="feat",
        state=0,
        side=Side.BUY,
        observed_at=now,
        bar_start=now,
        entry_price=Decimal("1500"),
        stop_price=Decimal("1470"),
        atr=Decimal("15"),
        edge=0.001,
    )]
    result = run_paper_cycle(
        signals=signals,
        frames={"BTCUSDC": frame_with_bar(close=1500)},
        policy=policy(),
        usdc_zar=Decimal("16.29"),
        positions_path=tmp_path / "positions.json",
        log_path=tmp_path / "log.csv",
        cooldown_path=tmp_path / "cooldown.json",
        book_path=tmp_path / "book.csv",
        server_time=now,
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert positions[0]["signal_id"] == "sig2"


def test_perp_signal_below_minimum_notional_is_skipped(tmp_path):
    now = datetime.now(timezone.utc)
    signals = [SliceSignal(
        signal_id="sig3",
        pair="TINYUSDC",
        kind="PERP",
        slice_id="feat:0:LONG",
        feature="feat",
        state=0,
        side=Side.BUY,
        observed_at=now,
        bar_start=now,
        entry_price=Decimal("0.001"),
        stop_price=Decimal("0.0009"),
        atr=Decimal("0.0001"),
        edge=0.001,
    )]
    result = run_paper_cycle(
        signals=signals,
        frames={},
        policy=policy(),
        usdc_zar=Decimal("16.29"),
        positions_path=tmp_path / "positions.json",
        log_path=tmp_path / "log.csv",
        cooldown_path=tmp_path / "cooldown.json",
        book_path=tmp_path / "book.csv",
        server_time=now,
    )
    assert result["open"] == 0
