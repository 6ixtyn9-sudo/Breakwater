import json
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from breakwater.models import Side
from breakwater.monitor import SliceSignal
from breakwater.paper_trade import (
    append_log,
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
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp("2026-08-14T10:00:00Z"),
                "symbol": "BTCUSDC",
                "open": close,
                "high": high if high is not None else close,
                "low": low if low is not None else close,
                "close": close,
                "volume": 100,
            }
        ]
    )


def open_position(side="BUY", entry="100", stop="95", bars="3"):
    return [
        {
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
        }
    ]


def signal(
    pair="BTCZAR",
    slice_id="feat:0:LONG",
    side=Side.BUY,
    entry="100",
    stop="95",
    atr="1",
    kind="SPOT",
    edge=0.001,
):
    now = datetime.now(timezone.utc)
    return SliceSignal(
        signal_id=f"sig-{slice_id}-{pair}",
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
        edge=float(edge),
        stop_atr_mult=2.0,
        regime="neutral",
    )


def spot_frame(close, high=None, low=None):
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp("2026-08-14T10:00:00Z"),
                "symbol": "BTCZAR",
                "open": close,
                "high": high if high is not None else close,
                "low": low if low is not None else close,
                "close": close,
                "volume": 100,
            }
        ]
    )


def cycle(tmp_path, signals, frames, positions=None, book=BOOK, monkeypatch=None):
    import os
    os.environ.setdefault("BREAKWATER_PAPER_MAX_RISK_FRACTION", "1")
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


def test_horizon_does_not_cut_a_plus_one_r_winner(tmp_path):
    """R-gate: once MFE >= +1R, horizon is a loser timer only."""
    position = open_position(entry="100", stop="95", bars="5")
    position[0]["horizon_bars"] = "6"
    position[0]["initial_stop_price"] = "95"
    position[0]["peak_price"] = "100"
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=106, high=106, low=105)},
        positions=position,
    )
    assert result["closed"] == 0
    assert result["open"] == 1
    held = read_positions(tmp_path / "positions.json")
    assert held[0]["trail_active"] == "1"


def test_horizon_still_cuts_a_thesis_that_never_confirmed(tmp_path):
    position = open_position(entry="100", stop="95", bars="5")
    position[0]["horizon_bars"] = "6"
    position[0]["initial_stop_price"] = "95"
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=101, high=101, low=100)},
        positions=position,
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "horizon"


def test_two_r_target_fires_even_with_horizon(tmp_path):
    position = open_position(entry="100", stop="95", bars="1")
    position[0]["horizon_bars"] = "24"
    position[0]["initial_stop_price"] = "95"
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=110, high=111, low=109)},
        positions=position,
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "target"
    assert float(log.iloc[0]["pnl_zar"]) > 0


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


def test_winner_capture_premium_raises_long_reference(tmp_path, monkeypatch):
    # Premium is opt-in; default mode is aligned.
    monkeypatch.setenv("BREAKWATER_PAPER_ENTRY_MODE", "premium")

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
    assert result["open"] == 0
    assert result["skipped"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "skipped"
    assert log.iloc[0]["entry_guard"] == "no_price"
    assert log.iloc[0]["exit_reason"] == "no_price"


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
    assert str(log.iloc[0]["entry_guard"]).startswith("regime_blocked")


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


def test_one_paper_slot_per_kind(tmp_path):
    """Paper holds up to three positions per kind, so both spot and perp
    evidence accumulate without the spot slot starving perps. Extra spot
    signals after the spot slots are full must not abort the loop before
    perp signals are considered."""
    spot_a = signal(pair="BTCZAR", kind="SPOT", slice_id="feat:0:LONG")
    spot_b = signal(pair="ETHZAR", kind="SPOT", slice_id="feat:1:LONG")
    perp = signal(pair="BTCUSDC", kind="PERP", slice_id="feat:perp:LONG", entry="1500", stop="1485", atr="3")
    result = cycle(
        tmp_path,
        signals=[spot_a, spot_b, perp],
        frames={
            "BTCZAR": spot_frame(close=100),
            "ETHZAR": spot_frame(close=100),
            "BTCUSDC": frame_with_bar(close=1500),
        },
        book={"feat:0:LONG", "feat:1:LONG", "feat:perp:LONG"},
    )
    assert result["open"] == 3
    positions = read_positions(tmp_path / "positions.json")
    kinds = {position["kind"] for position in positions}
    assert kinds == {"SPOT", "PERP"}


def test_per_kind_paper_cap_is_enforced(tmp_path):
    """Three slots per kind: a fourth eligible spot signal must be counted
    as slot_full and not open a position."""
    frames = {
        "BTCZAR": spot_frame(close=100),
        "ETHZAR": spot_frame(close=100),
        "XRPZAR": spot_frame(close=100),
        "SOLZAR": spot_frame(close=100),
    }
    signals = [
        signal(pair=pair, kind="SPOT", slice_id=f"feat:{i}:LONG", edge=0.004 - i * 0.001)
        for i, pair in enumerate(frames)
    ]
    result = cycle(
        tmp_path,
        signals=signals,
        frames=frames,
        book={f"feat:{i}:LONG" for i in range(4)},
    )
    assert result["open"] == 3
    assert result["slot_full"] >= 1


def test_fat_new_slices_fill_before_old_incumbents(tmp_path, monkeypatch):
    """Untested high-mean promotions take free seats before old/green hunt."""
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_POSITIONS", "3")
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_KIND", "3")
    from breakwater.research_lifecycle import _write_book

    hunt_id = "feat_ext_vs_ma_50:2:LONG:h21"
    _write_book(
        tmp_path / "book.csv",
        [
            {
                "slice_id": hunt_id,
                "kind": "PERP",
                "feature": "feat_ext_vs_ma_50",
                "state": "2",
                "side": "LONG",
                "status": "monitored",
                "validated_at": "",
                "last_signal_bar": "",
                "paper_trades": "13",
                "paper_wins": "12",
                "paper_losses": "1",
                "paper_pnl_zar": "114.00",
                "cooldown_until": "",
                "mean_ret_costadj": "0.005465",
                "n": "2282",
                "p_value": "0.65",
                "horizon_bars": "21",
                "stop_atr_mult": "3.500",
                "source": "validated_concentrated",
                "hostile_unproven": "True",
                "edge_is_directional_net": "True",
            }
        ],
    )
    frames = {
        "BTCUSDC": frame_with_bar(close=1500),
        "ETHUSDC": frame_with_bar(close=1500),
        "SOLUSDC": frame_with_bar(close=1500),
        "XRPUSDC": frame_with_bar(close=1500),
    }
    hunt = signal(
        pair="BTCUSDC", kind="PERP", slice_id=hunt_id, entry="1500", stop="1485", atr="3", edge=0.001
    )
    fat = [
        signal(pair=p, kind="PERP", slice_id=f"new:{i}:LONG", entry="1500", stop="1485", atr="3", edge=0.02)
        for i, p in enumerate(["ETHUSDC", "SOLUSDC", "XRPUSDC"])
    ]
    result = cycle(
        tmp_path,
        signals=fat + [hunt],
        frames=frames,
        book={hunt_id, "new:0:LONG", "new:1:LONG", "new:2:LONG"},
    )
    opened = {p["slice_id"] for p in read_positions(tmp_path / "positions.json")}
    assert result["open"] == 3
    assert hunt_id not in opened


def test_weakest_edge_is_excluded_when_slots_are_limited(tmp_path):
    """Selection is by edge strength, not iteration order: the lowest-edge
    candidate loses the slot even if it appears first."""
    frames = {
        "BTCZAR": spot_frame(close=100),
        "ETHZAR": spot_frame(close=100),
        "XRPZAR": spot_frame(close=100),
        "SOLZAR": spot_frame(close=100),
    }
    weakest = signal(pair="SOLZAR", kind="SPOT", slice_id="feat:weak:LONG", edge=0.0001)
    strong = [
        signal(pair=pair, kind="SPOT", slice_id=f"feat:{i}:LONG", edge=0.004 - i * 0.001)
        for i, pair in enumerate(["BTCZAR", "ETHZAR", "XRPZAR"])
    ]
    result = cycle(
        tmp_path,
        signals=[weakest] + strong,
        frames=frames,
        book={signal_.slice_id for signal_ in [weakest] + strong},
    )
    positions = read_positions(tmp_path / "positions.json")
    assert result["open"] == 3
    assert all(position["pair"] != "SOLZAR" for position in positions)


def test_one_position_per_pair(tmp_path):
    """Two signals for the same pair must not open two positions on it."""
    first = signal(pair="BTCZAR", kind="SPOT", slice_id="feat:0:LONG")
    second = signal(pair="BTCZAR", kind="SPOT", slice_id="feat:1:LONG")
    result = cycle(
        tmp_path,
        signals=[first, second],
        frames={"BTCZAR": spot_frame(close=100)},
        book={"feat:0:LONG", "feat:1:LONG"},
    )
    positions = read_positions(tmp_path / "positions.json")
    assert result["pair_held"] >= 1
    assert len(positions) == 1
    assert positions[0]["pair"] == "BTCZAR"


def test_log_header_migration_preserves_audit_columns(tmp_path):
    """A legacy 13-column log must be migrated to the 20-column header with
    no data lost, so exit_reason / entry_guard / regime become readable."""
    legacy_header = (
        "closed_at,signal_id,pair,kind,slice_id,side,entry_price,exit_price,"
        "stop_price,notional_zar,pnl_zar,outcome,bars_held"
    )
    path = tmp_path / "log.csv"
    with path.open("w", newline="") as handle:
        handle.write(legacy_header + "\n")
        handle.write("t0,id1,TRXZAR,SPOT,s:0:LONG,SELL,5,5.5,5.5,200,-1.2,loss,3\n")
        handle.write(
            "t1,id2,SHIBZAR,SPOT,s:1:LONG,SELL,1,1.01,1.01,200,-3.5,loss,2,"
            "stop,passed,bear\n"
        )

    append_log(
        path,
        {
            "closed_at": "t2",
            "signal_id": "id3",
            "pair": "ETHZAR",
            "kind": "SPOT",
            "slice_id": "s:2:LONG",
            "side": "SELL",
            "entry_price": "",
            "exit_price": "",
            "stop_price": "",
            "notional_zar": "0",
            "pnl_zar": "0",
            "outcome": "skipped",
            "bars_held": "0",
            "exit_reason": "regime",
            "entry_guard": "regime_blocked",
            "regime": "bull",
        },
    )

    import csv

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "closed_at",
            "signal_id",
            "pair",
            "kind",
            "slice_id",
            "side",
            "entry_price",
            "exit_price",
            "stop_price",
            "notional_zar",
            "pnl_zar",
            "outcome",
            "bars_held",
            "exit_reason",
            "entry_guard",
            "regime",
            "pnl_outcome",
            "atr",
            "stop_atr_mult",
            "risk_fraction",
        ]
        rows = list(reader)

    assert len(rows) == 3
    assert rows[0]["exit_reason"] == ""
    assert rows[1]["exit_reason"] == "stop"
    assert rows[1]["entry_guard"] == "passed"
    assert rows[1]["regime"] == "bear"
    assert rows[2]["entry_guard"] == "regime_blocked"
    assert rows[2]["regime"] == "bull"


def test_log_header_migration_is_idempotent(tmp_path):
    path = tmp_path / "log.csv"
    append_log(
        path,
        {
            "closed_at": "t0",
            "signal_id": "x",
            "pair": "A",
            "kind": "SPOT",
            "slice_id": "s",
            "side": "SELL",
            "entry_price": "",
            "exit_price": "",
            "stop_price": "",
            "notional_zar": "0",
            "pnl_zar": "0",
            "outcome": "skipped",
            "bars_held": "0",
            "exit_reason": "",
            "entry_guard": "",
            "regime": "",
        },
    )

    import csv

    with path.open(newline="") as handle:
        first = next(csv.reader(handle))

    assert first == [
        "closed_at",
        "signal_id",
        "pair",
        "kind",
        "slice_id",
        "side",
        "entry_price",
        "exit_price",
        "stop_price",
        "notional_zar",
        "pnl_zar",
        "outcome",
        "bars_held",
        "exit_reason",
        "entry_guard",
        "regime",
        "pnl_outcome",
        "atr",
        "stop_atr_mult",
        "risk_fraction",
    ]

    append_log(
        path,
        {
            "closed_at": "t1",
            "signal_id": "y",
            "pair": "B",
            "kind": "PERP",
            "slice_id": "s",
            "side": "SELL",
            "entry_price": "",
            "exit_price": "",
            "stop_price": "",
            "notional_zar": "0",
            "pnl_zar": "0",
            "outcome": "skipped",
            "bars_held": "0",
            "exit_reason": "",
            "entry_guard": "",
            "regime": "",
        },
    )

    with path.open(newline="") as handle:
        lines = handle.read().strip().splitlines()
    assert len(lines) == 3
    assert lines[0].split(",")[0] == "closed_at"


def test_risk_cap_skips_wide_stop(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_RISK_FRACTION", "0.03")
    result = cycle(
        tmp_path,
        signals=[signal(entry="100", stop="95", atr="2")],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 0
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "risk_cap"


def test_rotated_sibling_exits_at_close(tmp_path):
    position = open_position(entry="100", stop="95", bars="2")
    position[0]["slice_id"] = "feat_ret_10:2:LONG:h14"
    position[0]["horizon_bars"] = "14"
    position[0]["initial_stop_price"] = "95"
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=101, high=101, low=100)},
        positions=position,
        book={"feat_ret_10:2:LONG:h15"},
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "rotated"
