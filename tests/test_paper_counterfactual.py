from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from breakwater.paper_counterfactual import (
    advance_counterfactuals,
    attach_actual_closures,
    counterfactual_summary,
    sync_open_positions,
)

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def position(side="BUY", entry="100", stop="95"):
    return {
        "signal_id": "sig-1",
        "pair": "BTCUSDC",
        "kind": "PERP",
        "slice_id": "slice:LONG:h6",
        "side": side,
        "entry_price": entry,
        "stop_price": stop,
        "initial_stop_price": stop,
        "peak_price": entry,
        "trough_price": entry,
        "notional_zar": "100",
        "bars_held": "0",
        "horizon_bars": "6",
    }


def frame(close, high, low, start="2026-08-23T09:00:00Z"):
    return pd.DataFrame(
        [{"start": pd.Timestamp(start), "close": close, "high": high, "low": low}]
    )


def trackers_for(pos):
    return sync_open_positions(
        [],
        [pos],
        server_time=NOW,
        spot_fee_bps=Decimal(0),
        perp_fee_bps=Decimal(0),
    )


def test_target_exit_continues_as_ghost_under_wider_policies():
    trackers = trackers_for(position())
    attach_actual_closures(
        trackers,
        [
            {
                "signal_id": "sig-1",
                "exit_reason": "target",
                "exit_price": "110",
                "pnl_zar": "10.0000",
            }
        ],
    )
    first = advance_counterfactuals(
        trackers,
        frames={"BTCUSDC": frame(109, 110, 99)},
        server_time=NOW,
        missing_bars_exit=24,
    )
    assert first.state_error is None
    assert [row["policy"] for row in first.completed_rows] == ["target_2r_trail_1r"]
    assert first.completed_rows[0]["delta_vs_actual_zar"] == "0.0000"
    assert len(first.trackers) == 1

    second = advance_counterfactuals(
        first.trackers,
        frames={"BTCUSDC": frame(114, 116, 106, "2026-08-23T10:00:00Z")},
        server_time=NOW,
        missing_bars_exit=24,
    )
    target3 = [row for row in second.completed_rows if row["policy"] == "target_3r_trail_1r"]
    assert target3[0]["exit_price"] == "115"
    assert target3[0]["delta_vs_actual_zar"] == "5.0000"

    third = advance_counterfactuals(
        second.trackers,
        frames={"BTCUSDC": frame(112, 117, 110, "2026-08-23T11:00:00Z")},
        server_time=NOW,
        missing_bars_exit=24,
    )
    completed = {row["policy"]: row for row in third.completed_rows}
    assert completed["target_4r_trail_1r"]["exit_reason"] == "trail_stop"
    assert completed["no_target_trail_1r"]["exit_price"] == "111"
    assert completed["no_target_trail_1r"]["mfe_r"] == "3.400000"

    fourth = advance_counterfactuals(
        third.trackers,
        frames={"BTCUSDC": frame(107, 118, 106, "2026-08-23T12:00:00Z")},
        server_time=NOW,
        missing_bars_exit=24,
    )
    assert fourth.trackers == []
    assert fourth.completed_rows[0]["policy"] == "no_target_trail_2r"
    assert fourth.completed_rows[0]["exit_price"] == "107"


def test_short_is_direction_not_losing_outcome():
    trackers = trackers_for(position(side="SELL", stop="105"))
    result = advance_counterfactuals(
        trackers,
        frames={"BTCUSDC": frame(91, 101, 90)},
        server_time=NOW,
        missing_bars_exit=24,
    )
    target2 = [row for row in result.completed_rows if row["policy"] == "target_2r_trail_1r"]
    assert target2[0]["side"] == "SELL"
    assert target2[0]["pnl_outcome"] == "win"
    assert target2[0]["pnl_zar"] == "10.0000"


def test_counterfactuals_replay_each_unseen_bar_in_order():
    pos = position()
    pos["last_processed_bar_start"] = "2026-08-23T08:00:00+00:00"
    trackers = trackers_for(pos)
    replay = pd.DataFrame(
        [
            {
                "start": pd.Timestamp("2026-08-23T09:00:00Z"),
                "close": 105,
                "high": 106,
                "low": 100,
            },
            {
                "start": pd.Timestamp("2026-08-23T10:00:00Z"),
                "close": 100,
                "high": 102,
                "low": 100,
            },
        ]
    )
    result = advance_counterfactuals(
        trackers,
        frames={"BTCUSDC": replay},
        server_time=NOW,
        missing_bars_exit=24,
    )
    completed = {row["policy"]: row for row in result.completed_rows}
    assert completed["target_2r_trail_1r"]["exit_reason"] == "trail_stop"
    assert completed["target_2r_trail_1r"]["exit_price"] == "101"
    assert completed["target_2r_trail_1r"]["bars_held"] == "2"
    assert completed["target_2r_trail_1r"]["exit_bar_start"].startswith(
        "2026-08-23T10:00:00"
    )
    assert result.trackers[0]["last_processed_bar_start"].startswith(
        "2026-08-23T10:00:00"
    )


def test_strategy_rotation_closes_all_exit_policies():
    trackers = trackers_for(position())
    attach_actual_closures(
        trackers,
        [
            {
                "signal_id": "sig-1",
                "exit_reason": "rotated",
                "exit_price": "101",
                "pnl_zar": "1.0000",
            }
        ],
    )
    result = advance_counterfactuals(
        trackers,
        frames={"BTCUSDC": frame(101, 102, 99)},
        server_time=NOW,
        missing_bars_exit=24,
    )
    assert result.trackers == []
    assert len(result.completed_rows) == 5
    assert {row["exit_reason"] for row in result.completed_rows} == {"rotated"}


def test_counterfactual_summary_keeps_policy_results_separate(tmp_path):
    path = tmp_path / "missing.csv"
    assert counterfactual_summary(path) == {
        "completed": 0,
        "by_policy": {},
        "by_policy_and_side": {},
        "control": {"comparisons": 0, "mismatches": 0},
    }
