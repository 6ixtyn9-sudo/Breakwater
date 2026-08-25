import json
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
import pytest

from breakwater.models import Side
from breakwater.monitor import SliceSignal
from breakwater.paper_trade import (
    PAPER_LOG_HEADERS,
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


def frame_with_bars(rows):
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp(start),
                "symbol": "BTCUSDC",
                "open": close,
                "high": high,
                "low": low,
                "close": close,
                "volume": 100,
            }
            for start, close, high, low in rows
        ]
    )


def frame_with_bar(close, high=None, low=None, start="2026-08-14T10:00:00Z"):
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp(start),
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
    horizon=0,
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
        horizon_bars=int(horizon),
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
    os.environ.setdefault("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "0")
    os.environ.setdefault("BREAKWATER_PAPER_RISK_TO_MEAN_K", "0")
    os.environ.setdefault("BREAKWATER_PAPER_AGGREGATE_RISK_BUFFER_BPS", "0")
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


def test_paper_fee_uses_configured_bps(tmp_path, monkeypatch):
    """The close fee must follow the configured round-trip bps, so the cost
    model is a fact we set, not a number buried in the source."""
    from breakwater import paper_trade

    monkeypatch.setattr(paper_trade, "PERP_FEE_BPS", Decimal("100"))
    # notional 150 @ 100 bps round trip -> 1.50 ZAR fee
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=94, low=93)},
        positions=open_position(),
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert Decimal(str(log.iloc[0]["fee_zar"])) == Decimal("1.50")


def test_replays_unseen_bars_stop_first_after_runner_delay(tmp_path):
    position = open_position(entry="100", stop="95", bars="0")
    position[0]["initial_stop_price"] = "95"
    position[0]["last_processed_bar_start"] = "2026-08-14T08:00:00+00:00"
    result = cycle(
        tmp_path,
        signals=[],
        frames={
            "BTCUSDC": frame_with_bars(
                [
                    ("2026-08-14T09:00:00Z", 96, 101, 94),
                    ("2026-08-14T10:00:00Z", 111, 112, 110),
                ]
            )
        },
        positions=position,
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "stop"
    assert log.iloc[0]["bars_held"] == 1
    assert str(log.iloc[0]["exit_bar_start"]).startswith("2026-08-14T09:00:00")


def test_repeated_same_bar_does_not_increment_holding_time(tmp_path):
    position = open_position(entry="100", stop="95", bars="3")
    position[0]["initial_stop_price"] = "95"
    position[0]["last_processed_bar_start"] = "2026-08-14T10:00:00+00:00"
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame_with_bar(close=100, high=101, low=99)},
        positions=position,
    )
    assert result["closed"] == 0
    held = read_positions(tmp_path / "positions.json")
    assert held[0]["bars_held"] == "3"


def test_replay_ratchets_then_hits_trail_on_next_unseen_bar(tmp_path):
    position = open_position(entry="100", stop="95", bars="0")
    position[0]["initial_stop_price"] = "95"
    position[0]["last_processed_bar_start"] = "2026-08-14T08:00:00+00:00"
    result = cycle(
        tmp_path,
        signals=[],
        frames={
            "BTCUSDC": frame_with_bars(
                [
                    ("2026-08-14T09:00:00Z", 105, 106, 100),
                    ("2026-08-14T10:00:00Z", 100, 102, 100),
                ]
            )
        },
        positions=position,
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "trail_stop"
    assert float(log.iloc[0]["exit_price"]) == 101.0
    assert log.iloc[0]["bars_held"] == 2


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
    assert float(log.iloc[0]["mfe_r"]) == 2.2
    assert float(log.iloc[0]["mae_r"]) == 0.0
    assert float(log.iloc[0]["gross_r"]) == 2.0
    assert log.iloc[0]["excursion_ordering"] == "ohlc_upper_bound_stop_first_exit"
    assert result["counterfactual"]["completed_this_cycle"] == 1
    assert result["counterfactual"]["active_trackers"] == 1
    assert result["counterfactual"]["control"] == {"comparisons": 1, "mismatches": 0}
    assert result["performance"]["by_side"]["BUY"]["trades"] == 1
    assert result["performance"]["by_side"]["BUY"]["wins"] == 1
    counterfactual_log = pd.read_csv(tmp_path / "paper_counterfactual_log.csv")
    assert list(counterfactual_log["policy"]) == ["target_2r_trail_1r"]
    assert counterfactual_log.iloc[0]["actual_exit_reason"] == "target"


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
    assert result["skipped"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["outcome"] == "skipped"
    assert log.iloc[0]["exit_reason"] == "below_perp_min_notional"


@pytest.mark.parametrize(
    ("seed", "expected_notional"),
    [("2000", "400"), ("4000", "800")],
)
def test_equity_mode_notional_cap_tracks_equity(
    tmp_path, monkeypatch, seed, expected_notional
):
    """Compounding sizing: in equity mode the notional ceiling is a fraction
    of equity, so a doubled account doubles the notional it can deploy.
    Stop 97 vs entry 100 -> rf 0.03; the 1% risk budget (20 ZAR on 2000)
    wants 666 ZAR notional, so the 20% equity ceiling binds (400, then 800)."""
    monkeypatch.setenv("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "1")
    monkeypatch.setenv("BREAKWATER_PAPER_EQUITY_SEED", seed)
    monkeypatch.setenv("BREAKWATER_PAPER_RISK_OF_EQUITY", "0.01")
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_POSITION_NOTIONAL_OF_EQUITY", "0.20")
    sig = signal(pair="BTCZAR", kind="SPOT", slice_id="feat:0:LONG", entry="100", stop="97")
    result = cycle(
        tmp_path,
        signals=[sig],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert Decimal(positions[0]["notional_zar"]) == Decimal(expected_notional)


def test_flat_mode_notional_cap_stays_absolute(tmp_path, monkeypatch):
    """Flat mode (SIZE_FROM_EQUITY=0) is untouched by the equity fraction:
    the mandate's absolute 200 ZAR cap still binds. R 6.63 ZAR at rf 0.02
    wants 331.5 ZAR notional, capped at 200 ZAR."""
    monkeypatch.setenv("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "0")
    sig = signal(pair="BTCZAR", kind="SPOT", slice_id="feat:0:LONG", entry="100", stop="98")
    result = cycle(
        tmp_path,
        signals=[sig],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert Decimal(positions[0]["notional_zar"]) == Decimal("200")


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
        assert reader.fieldnames == PAPER_LOG_HEADERS
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

    assert first == PAPER_LOG_HEADERS

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


def test_aggregate_risk_cap_blocks_new_position(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR", "10")
    result = cycle(
        tmp_path,
        signals=[signal(pair="ETHZAR", slice_id="feat:0:SHORT")],
        frames={
            "BTCUSDC": frame_with_bar(close=100, high=101, low=99),
            "ETHZAR": spot_frame(close=100),
        },
        positions=open_position(),
    )
    assert result["open"] == 1
    assert result["aggregate_open_risk_zar"] == "7.5000"
    assert result["aggregate_risk_cap_skips"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "aggregate_risk_cap"


def test_breakeven_trailing_stop_contributes_zero_aggregate_risk(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR", "7")
    position = open_position(stop="100")
    position[0]["initial_stop_price"] = "95"
    position[0]["trail_active"] = "1"
    result = cycle(
        tmp_path,
        signals=[signal(pair="ETHZAR", slice_id="feat:0:SHORT")],
        frames={
            "BTCUSDC": frame_with_bar(close=101, high=101, low=101),
            "ETHZAR": spot_frame(close=100),
        },
        positions=position,
    )
    assert result["open"] == 2
    assert result["aggregate_open_risk_zar"] == "6.6300"
    assert result["aggregate_risk_unknown"] is False


def test_invalid_position_is_quarantined_and_cycle_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR", "100")
    position = open_position(stop="105")
    position[0]["side"] = "UNKNOWN"
    result = cycle(
        tmp_path,
        signals=[signal(pair="ETHZAR", slice_id="feat:0:SHORT")],
        frames={
            "BTCUSDC": frame_with_bar(close=100, high=101, low=99),
            "ETHZAR": spot_frame(close=100),
        },
        positions=position,
    )
    assert result["open"] == 0
    assert result["aggregate_open_risk_zar"] is None
    assert result["aggregate_risk_unknown"] is True
    assert result["aggregate_risk_unknown_skips"] == 1
    assert result["invalid_positions_quarantined"] == 1
    quarantine = json.loads((tmp_path / "paper_position_quarantine.json").read_text())
    assert quarantine[0]["reason"] == "invalid_side"
    assert quarantine[0]["position"]["signal_id"] == "sig1"
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "aggregate_risk_unknown"


def test_aggregate_stress_buffer_can_block_entry(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR", "6.8")
    monkeypatch.setenv("BREAKWATER_PAPER_AGGREGATE_RISK_BUFFER_BPS", "25")
    result = cycle(
        tmp_path,
        signals=[signal()],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 0
    assert result["aggregate_risk_cap_skips"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "aggregate_risk_cap"


def test_unreadable_position_state_is_preserved_and_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR", "100")
    positions_path = tmp_path / "positions.json"
    positions_path.write_text("{broken")
    result = cycle(
        tmp_path,
        signals=[signal()],
        frames={"BTCZAR": spot_frame(close=100)},
    )
    assert result["open"] == 0
    assert result["positions_state_error"] == "invalid_json"
    assert result["aggregate_risk_status"] == "unknown"
    assert positions_path.read_text() == "{broken"


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


HIP3_HEADERS = [
    "slice_id", "kind", "feature", "state", "side", "status", "validated_at",
    "last_signal_bar", "paper_trades", "paper_wins", "paper_losses",
    "paper_pnl_zar", "cooldown_until", "mean_ret_costadj", "n", "p_value",
    "horizon_bars", "stop_atr_mult", "source", "hostile_unproven",
    "edge_is_directional_net",
]


def write_book_row(path, slice_id, *, horizon="5", kind="PERP", side="LONG"):
    row = {header: "" for header in HIP3_HEADERS}
    row.update(
        {
            "slice_id": slice_id,
            "kind": kind,
            "feature": "feat",
            "state": "0",
            "side": side,
            "status": "monitored",
            "validated_at": "2026-08-14T00:00:00+00:00",
            "paper_trades": "0",
            "paper_wins": "0",
            "paper_losses": "0",
            "paper_pnl_zar": "0.0000",
            "mean_ret_costadj": "0.0021",
            "n": "100",
            "p_value": "0.010000",
            "horizon_bars": horizon,
            "stop_atr_mult": "2.000",
            "source": "validated_walk_forward",
            "hostile_unproven": "False",
            "edge_is_directional_net": "True",
        }
    )
    path.write_text(
        ",".join(HIP3_HEADERS) + "\n" + ",".join(row[h] for h in HIP3_HEADERS) + "\n"
    )
    return path


def read_book_rows(path):
    import csv

    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def hip3_cycle(tmp_path, signals, frames, positions=None, hip3_book=None, book=BOOK):
    import os

    os.environ.setdefault("BREAKWATER_PAPER_MAX_RISK_FRACTION", "1")
    os.environ.setdefault("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "0")
    os.environ.setdefault("BREAKWATER_PAPER_RISK_TO_MEAN_K", "0")
    os.environ.setdefault("BREAKWATER_PAPER_AGGREGATE_RISK_BUFFER_BPS", "0")
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
        hip3_book_path=hip3_book,
    )


def test_paper_performance_summary_by_session(tmp_path):
    """The status performance block breaks PnL down by ENTRY session, so
    timing questions ('did EU entries into US equities lose?') are answerable
    from status.csv without a scratch script."""
    import csv

    from breakwater import paper_trade as pt

    log = tmp_path / "log.csv"
    rows = [
        # entry = 11:00 - 2h = 09:00Z -> eu
        {"pnl_zar": "1.0", "side": "BUY", "exit_reason": "horizon",
         "exit_bar_start": "2026-08-25T11:00:00+00:00", "bars_held": "2"},
        # entry = 14:00 - 1h = 13:00Z -> us
        {"pnl_zar": "-2.0", "side": "BUY", "exit_reason": "stop",
         "exit_bar_start": "2026-08-25T14:00:00+00:00", "bars_held": "1"},
        # entry = 05:00 - 1h = 04:00Z -> asia
        {"pnl_zar": "0.5", "side": "SELL", "exit_reason": "horizon",
         "exit_bar_start": "2026-08-25T05:00:00+00:00", "bars_held": "1"},
        # no exit_bar_start -> unknown, never an error
        {"pnl_zar": "0.25", "side": "BUY", "exit_reason": "stale_data",
         "exit_bar_start": "", "bars_held": "0"},
    ]
    with log.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pt.PAPER_LOG_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in pt.PAPER_LOG_HEADERS} | {"outcome": "win" if Decimal(r["pnl_zar"]) > 0 else "loss"})

    s = pt._paper_performance_summary(log)
    assert s["closed"] == 4
    assert s["by_session"]["eu"] == {"trades": 1, "wins": 1, "pnl_zar": "1.0000"}
    assert s["by_session"]["us"] == {"trades": 1, "wins": 0, "pnl_zar": "-2.0000"}
    assert s["by_session"]["asia"] == {"trades": 1, "wins": 1, "pnl_zar": "0.5000"}
    assert s["by_session"]["unknown"] == {"trades": 1, "wins": 1, "pnl_zar": "0.2500"}


def test_hip3_subpool_caps_positions_per_slice(tmp_path, monkeypatch):
    """The HIP-3 sub-pool caps positions per slice (default 3) so one edge
    cannot occupy half the pool with correlated bets."""
    from breakwater import paper_trade

    monkeypatch.setattr(paper_trade, "MAX_PAPER_POSITIONS_PER_KIND", 6)
    hip3_book = write_book_row(tmp_path / "hip3_book.csv", "hip3_xyz_index_c0:feat:0:LONG:h5")
    positions = []
    for i in range(3):
        position = dict(open_position()[0])
        position.update(pair=f"XYZ:TICK{i}", slice_id="hip3_xyz_index_c0:feat:0:LONG:h5")
        positions.append(position)
    sig = signal(
        pair="XYZ:TICK3",
        kind="PERP",
        slice_id="hip3_xyz_index_c0:feat:0:LONG:h5",
        entry="100",
        stop="95",
    )
    result = hip3_cycle(
        tmp_path,
        signals=[sig],
        frames={"XYZ:TICK3": frame_with_bar(close=100)},
        positions=positions,
        hip3_book=hip3_book,
        book={"hip3_xyz_index_c0:feat:0:LONG:h5"},
    )
    # The three incumbents survive; the fourth seat on the same slice is
    # refused at the HIP-3 per-slice cap.
    assert result["open"] == 3
    assert result["slice_full"] == 1


def test_hip3_position_exits_on_hip3_book_horizon(tmp_path):
    hip3_book = write_book_row(tmp_path / "hip3_book.csv", "hip3_xyz_index_c0:feat:0:LONG:h5")
    position = dict(open_position()[0])
    position.update(pair="XYZ:NVDA", slice_id="hip3_xyz_index_c0:feat:0:LONG:h5", bars_held="6")
    # 14:00Z bar closes 15:00Z = 11:00 ET: inside the US session, so the
    # planned horizon exit fires (a pre-market bar would now defer it).
    result = hip3_cycle(
        tmp_path,
        signals=[],
        frames={"XYZ:NVDA": frame_with_bar(close=100, start="2026-08-14T14:00:00Z")},
        positions=[position],
        hip3_book=hip3_book,
        book={"hip3_xyz_index_c0:feat:0:LONG:h5"},
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "horizon"
    # Feedback landed in the HIP-3 book, not the (absent) native book.
    rows = read_book_rows(hip3_book)
    assert rows[0]["paper_trades"] == "1"


def recent_frame(pair, close, high=None, low=None):
    # Bar at the current hour: a stop-out cooldown (24h) must not already be
    # expired when read_book's reactivation pass runs.
    start = pd.Timestamp(datetime.now(timezone.utc).replace(second=0, microsecond=0))
    return pd.DataFrame(
        [
            {
                "start": start,
                "symbol": pair,
                "open": close,
                "high": high if high is not None else close,
                "low": low if low is not None else close,
                "close": close,
                "volume": 100,
            }
        ]
    )


def test_hip3_stop_out_routes_feedback_to_hip3_book_only(tmp_path):
    hip3_book = write_book_row(tmp_path / "hip3_book.csv", "hip3_xyz_index_c0:feat:0:LONG:h5")
    native_book = write_book_row(tmp_path / "book.csv", "feat:0:LONG", horizon="5")
    position = dict(open_position()[0])
    position.update(pair="XYZ:NVDA", slice_id="hip3_xyz_index_c0:feat:0:LONG:h5")
    result = hip3_cycle(
        tmp_path,
        signals=[],
        frames={"XYZ:NVDA": recent_frame("XYZ:NVDA", 94, low=93)},
        positions=[position],
        hip3_book=hip3_book,
        book={"feat:0:LONG", "hip3_xyz_index_c0:feat:0:LONG:h5"},
    )
    assert result["closed"] == 1
    hip3_rows = read_book_rows(hip3_book)
    assert hip3_rows[0]["paper_trades"] == "1"
    assert hip3_rows[0]["status"] == "cooldown"
    native_rows = read_book_rows(native_book)
    assert native_rows[0]["paper_trades"] == "0"
    assert native_rows[0]["status"] == "monitored"


def _frame_for(pair, close):
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp("2026-08-14T10:00:00Z"),
                "symbol": pair,
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 100,
            }
        ]
    )


def test_hip3_positions_respect_dedicated_seat_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_HIP3_MAX_POSITIONS", "1")
    book = {
        "hip3_xyz_equity_c0:feat:0:LONG:h5",
        "feat:0:LONG",
    }
    hip3_a = signal(
        pair="HIP3A",
        slice_id="hip3_xyz_equity_c0:feat:0:LONG:h5",
        kind="PERP",
        entry="100",
        stop="99",
        atr="0.5",
    )
    hip3_b = signal(
        pair="HIP3B",
        slice_id="hip3_xyz_equity_c0:feat:0:LONG:h5",
        kind="PERP",
        entry="100",
        stop="99",
        atr="0.5",
    )
    native = signal(
        pair="BTCZAR",
        slice_id="feat:0:LONG",
        kind="PERP",
        entry="100",
        stop="99",
        atr="0.5",
    )
    frames = {
        "HIP3A": _frame_for("HIP3A", 100),
        "HIP3B": _frame_for("HIP3B", 100),
        "BTCZAR": _frame_for("BTCZAR", 100),
    }
    result = hip3_cycle(
        tmp_path,
        signals=[hip3_a, hip3_b, native],
        frames=frames,
        book=book,
    )
    # One HIP-3 seat: exactly one HIP-3 position opens, the second is
    # slot-full, and the native book is unaffected by the HIP-3 cap.
    assert result["open"] == 2
    assert result["slot_full"] == 1
    assert result["hip3_open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    pairs = {p["pair"] for p in positions}
    assert "BTCZAR" in pairs
    assert len([p for p in positions if p["pair"].startswith("HIP3")]) == 1
    # Per-book breakdown: the denial is attributed to the HIP-3 pool, and
    # each book's signals/opens are counted separately.
    bs = result["book_stats"]
    assert bs["hip3"]["signals"] == 2
    assert bs["hip3"]["opened"] == 1
    assert bs["hip3"]["slot_full"] == 1
    assert bs["native"]["signals"] == 1
    assert bs["native"]["opened"] == 1
    assert bs["native"]["slot_full"] == 0


def test_hip3_signal_opens_position_with_hip3_book_horizon(tmp_path):
    hip3_book = write_book_row(tmp_path / "hip3_book.csv", "hip3_xyz_index_c0:feat:0:LONG:h5")
    sig = signal(
        pair="XYZ:NVDA",
        slice_id="hip3_xyz_index_c0:feat:0:LONG:h5",
        kind="PERP",
        entry="100",
        stop="99",
        atr="0.5",
    )
    result = hip3_cycle(
        tmp_path,
        signals=[sig],
        frames={"XYZ:NVDA": frame_with_bar(close=100)},
        hip3_book=hip3_book,
        book={"hip3_xyz_index_c0:feat:0:LONG:h5"},
    )
    assert result["open"] == 1
    positions = read_positions(tmp_path / "positions.json")
    assert positions[0]["slice_id"] == "hip3_xyz_index_c0:feat:0:LONG:h5"
    assert positions[0]["entry_guard"] == "passed"
    assert positions[0]["horizon_bars"] == "5"


def _hip3_position(**overrides):
    position = dict(open_position()[0])
    position.update(
        {
            "pair": "XYZ:COIN",
            "slice_id": "hip3_xyz_equity_c0:feat:0:LONG:h2",
            "entry_price": "100",
            "stop_price": "97",
            "initial_stop_price": "97",
            "peak_price": "100",
            "trough_price": "100",
            "bars_held": "1",
            "horizon_bars": "2",
            "last_processed_bar_start": "2026-08-25T07:00:00+00:00",
        }
    )
    position.update(overrides)
    return position


def _hour_frame(starts, close=101.0):
    return pd.DataFrame(
        [
            {
                "start": pd.Timestamp(start),
                "symbol": "XYZ:COIN",
                "open": close,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": 100,
            }
            for start in starts
        ]
    )


def test_hip3_planned_exit_defers_to_market_session(tmp_path):
    """A US-equity position whose horizon deadline lands in the pre-market
    must NOT exit there: the planned exit defers to the next in-session
    close (summer dates: 14:00Z close = 10:00 ET)."""
    bars = [f"2026-08-25T{h:02d}:00:00Z" for h in (8, 9, 10, 11, 12, 13)]
    result = cycle(
        tmp_path,
        signals=[],
        frames={"XYZ:COIN": _hour_frame(bars)},
        positions=[_hip3_position()],
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "horizon"
    # Exited on the 13:00 bar (close 14:00Z = in session), NOT on the
    # 09:00 bar where bars_held first reached the horizon (10:00Z close,
    # pre-market).
    assert log.iloc[0]["exit_bar_start"].startswith("2026-08-25T13:00")


def test_hip3_stop_still_fires_outside_session(tmp_path):
    """Protective exits never sleep: a stop during the pre-market still
    closes the position."""
    bars = [
        "2026-08-25T08:00:00Z",
        "2026-08-25T09:00:00Z",
    ]
    frame = _hour_frame(bars)
    frame.loc[frame["start"].astype(str).str.contains("08:00"), "low"] = 96.0
    result = cycle(
        tmp_path,
        signals=[],
        frames={"XYZ:COIN": frame},
        positions=[_hip3_position(horizon_bars="6")],
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "stop"


def test_native_planned_exit_unaffected_by_session(tmp_path):
    """The same timing on a NATIVE (24/7 crypto) slice exits on the
    horizon bar regardless of session - the gate is HIP-3 only."""
    position = dict(open_position()[0])
    position.update(
        {
            "entry_price": "100",
            "stop_price": "97",
            "initial_stop_price": "97",
            "bars_held": "1",
            "horizon_bars": "2",
            "last_processed_bar_start": "2026-08-25T07:00:00+00:00",
        }
    )
    bars = [
        "2026-08-25T08:00:00Z",
        "2026-08-25T09:00:00Z",
        "2026-08-25T10:00:00Z",
    ]
    frame = pd.DataFrame(
        [
            {
                "start": pd.Timestamp(start),
                "symbol": "BTCUSDC",
                "open": 101.0,
                "high": 101.5,
                "low": 100.5,
                "close": 101.0,
                "volume": 100,
            }
            for start in bars
        ]
    )
    result = cycle(
        tmp_path,
        signals=[],
        frames={"BTCUSDC": frame},
        positions=[position],
    )
    assert result["closed"] == 1
    log = pd.read_csv(tmp_path / "log.csv")
    assert log.iloc[0]["exit_reason"] == "horizon"
    # Native exits on the FIRST bar that reaches the horizon (the 08:00
    # bar, whose close at 09:00Z is outside US market hours) - no deferral,
    # unlike the identical HIP-3 position in the test above.
    assert log.iloc[0]["exit_bar_start"].startswith("2026-08-25T08:00")


def _session_tape(end_start, n=220):
    """Hourly tape ending with the bar that STARTS at end_start: flat at
    100, then a steady rise to ~106 so feat_ext_vs_ma_10 is state 2."""
    from datetime import timedelta

    end = pd.Timestamp(end_start)
    rows = []
    for i in range(n):
        start = end - timedelta(hours=n - 1 - i)
        close = 100.0 if i < n - 10 else 100.6 + (i - (n - 10)) * 0.6
        rows.append(
            {
                "start": start,
                "symbol": "XYZ:COIN",
                "open": close,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": 100,
            }
        )
    return pd.DataFrame(rows)


def test_hip3_entry_gated_to_derived_market_session(tmp_path, monkeypatch):
    """HIP-3 equity entries are gated to the underlying's live session,
    DERIVED from the slice's market class - the operator's crypto session
    variable does not apply (a pre-market bar that the 'eu' variable would
    allow is still blocked; an in-market bar signals)."""
    from datetime import datetime, timezone

    from breakwater.monitor import monitor_book

    monkeypatch.setenv("BREAKWATER_PAPER_SESSIONS", "eu")
    monkeypatch.setenv("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", "60")

    row = {
        "slice_id": "hip3_xyz_equity_c0:feat_ext_vs_ma_10:2:LONG",
        "kind": "PERP",
        "feature": "feat_ext_vs_ma_10",
        "state": "2",
        "side": "LONG",
        "status": "monitored",
        "stop_atr_mult": "2.0",
        "horizon_bars": "12",
        "mean_ret_costadj": "0.005",
        "hostile_unproven": "False",
        "edge_is_directional_net": "True",
    }
    server_time = datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc)

    # Bar closes 10:00Z = 06:00 ET: pre-market. The 'eu' variable would
    # allow this bar; the derived class gate blocks and journals it.
    pre = _session_tape("2026-08-25T09:00:00Z")
    signals, blocked = monitor_book([dict(row)], {"PERP": {"XYZ:COIN": pre}}, server_time=server_time)
    assert signals == []
    assert len(blocked) == 1
    assert blocked[0]["guard"] == "session_blocked"
    assert blocked[0]["market_class"] == "equity"

    # Bar closes 15:00Z = 11:00 ET: in session, signals normally.
    intraday = _session_tape("2026-08-25T14:00:00Z")
    signals, blocked = monitor_book([dict(row)], {"PERP": {"XYZ:COIN": intraday}}, server_time=server_time)
    assert len(signals) == 1
    assert blocked == []
