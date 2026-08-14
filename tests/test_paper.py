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

BOOK = {"feat:0:LONG", "feat:0:SHORT"}


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
        "missing_bars": "0",
        "entry_guard": "passed",
    }]


def signal(pair="BTCZAR", slice_id="feat:0:LONG", side=Side.BUY, entry="100", stop="95", atr="1", kind="SPOT"):
    now = datetime.now(timezone.utc)
    return SliceSignal(
        signal_id=f"sig-{slice_id}",
        pair=pair,
        kind=kind,
        slice_id=slice_id,
        feature="feat",
        state=0,
        side=side,
        observed_at=now,
        bar_start=now,
        entry_price=Decimal(entry),
        stop_price=Decimal(stop),
        atr=Decimal(atr),
        edge=0.001,
        stop_atr_mult=2.0,
        regime="neutral",
    )


def spot_frame(close, high=None, low=None):
    return pd.DataFrame([{
        "start": pd.Timestamp("2026-08-14T10:00:00Z"),
        "symbol": "BTCZAR",
        "open": close,
        "high": high if high is not None else close,
        "low": low if low is not None else close,
        "close": close,
        "volume": 100,
    }])


def cycle(tmp_path, signals, frames, positions=None, book=BOOK):
    positions_path = tmp_path / "positions.json"
    if positions is not None:
        positions_path.write_text(json.dumps(positions))
    return run_paper_cycle(
        signals=signals,
        frames=frames,
        policy=policy(),
        usdc_zar=Decimal("16.29"),
        positions_path=positions_path,
        log_path=tmp_path / "log.csv",
        cooldown_path=tmp_path / "cooldown.json",
        book_path=tmp_path / "book.csv",
        book_slice_ids=book,
        server_time=datetime.now(timezone.utc),
    )


def test_open_position_stops_out_and_journals(tmp_path):
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=94, low=93)},
        positions=open_position(),
    )
    assert result["closed"] == 1
    assert result["open"] == 0
    journal = json.loads((tmp_path / "cooldown.json").read_text())
    assert journal[0]["slice_id"] == "feat:0:LONG"
    assert journal[0]["pnl_zar"].startswith("-")


def test_open_position_hits_target_and_wins(tmp_path):
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=111, high=111)},
        positions=open_position(),
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "win"
    assert log.iloc[0]["exit_reason"] == "target"
    assert float(log.iloc[0]["pnl_zar"]) > 0


def test_new_book_signal_opens_position_when_slot_free(tmp_path):
    result = cycle(
        tmp_path,
        signals=[signal()],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert positions[0]["slice_id"] == "feat:0:LONG"
    assert positions[0]["entry_guard"] == "passed"


def test_winner_capture_premium_raises_long_reference(tmp_path):
    cycle(
        tmp_path,
        signals=[signal(entry="100", stop="95", atr="1")],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    positions = read_positions(tmp_path / "positions.json")
    reference = Decimal(positions[0]["entry_price"])
    assert reference > Decimal("100")
    assert reference <= Decimal("100.25") + Decimal("0.001")
    stop = Decimal(positions[0]["stop_price"])
    assert stop > Decimal("95")


def test_falling_knife_entry_is_blocked_and_visible(tmp_path):
    result = cycle(
        tmp_path,
        signals=[signal(entry="100", stop="95", atr="1")],
        frames={"BTCZAR": spot_frame(close=95)},
    )
    assert result["open"] == 0
    assert result["skipped"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "skipped"
    assert log.iloc[0]["entry_guard"] == "adverse_blocked"


def test_missing_price_fails_open_with_visible_guard(tmp_path):
    result = cycle(
        tmp_path,
        signals=[signal()],
        frames={},
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert positions[0]["entry_guard"] == "no_price"


def test_unvalidated_signal_is_not_paper_traded(tmp_path):
    result = cycle(
        tmp_path,
        signals=[signal(slice_id="big-wave", side=Side.BUY)],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 0
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "skipped"
    assert log.iloc[0]["exit_reason"] == "not_book"


def test_hostile_regime_entry_is_blocked_and_visible(tmp_path):
    bearish = signal(side=Side.BUY)
    bearish = SliceSignal(**{**bearish.__dict__, "regime": "bear"})
    result = cycle(
        tmp_path,
        signals=[bearish],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 0
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["entry_guard"] == "regime_blocked"


def test_stale_data_exits_instead_of_living_forever(tmp_path):
    position = open_position(bars="5")
    position[0]["missing_bars"] = "23"
    result = cycle(
        tmp_path,
        signals=[],
        frames={},
        positions=position,
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "stale_data"
    assert float(log.iloc[0]["pnl_zar"]) < 0


def test_perp_signal_below_minimum_notional_is_skipped(tmp_path):
    tiny = signal(pair="TINYUSDC", entry="0.001", stop="0.0009", atr="0.0001", kind="PERP")
    result = cycle(
        tmp_path,
        signals=[tiny],
        frames={"TINYUSDC": frame_with_bar(close=Decimal("0.001"))},
    )
    assert result["open"] == 0
