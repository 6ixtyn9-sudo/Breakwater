import pandas as pd
import pytest

from breakwater.models import Side
from breakwater.price_bridge import candidate_pairs, parse_candidates


def frame(side="short"):
    return pd.DataFrame([{
        "symbol": "XRP/USD",
        "timeframe": "1d",
        "slice_combination": "state_ext=neutral + state_vol=mid_vol",
        "side": side,
        "bin_mode": "rolling",
        "valid_n": 25,
        "valid_mean_ret_costadj": "0.03",
        "valid_p_value_nw": "0.001",
        "walk_forward_pass_pattern": 3,
        "search_wide_bh_pass": True,
        "search_wide_bonferroni_pass": False,
    }])


def test_price_short_maps_only_to_active_perpetual():
    candidate = parse_candidates(frame())[0]
    assert candidate.side is Side.SELL
    assert candidate_pairs(
        candidate,
        active_spot={"XRPZAR"},
        active_futures={"XRPUSDTPERP"},
    ) == ["XRPUSDTPERP"]


def test_price_long_prefers_native_spot_and_can_include_perpetual():
    candidate = parse_candidates(frame("long"))[0]
    assert candidate_pairs(
        candidate,
        active_spot={"XRPZAR", "XRPUSDT"},
        active_futures={"XRPUSDTPERP"},
    ) == ["XRPZAR", "XRPUSDT", "XRPUSDTPERP"]


def test_missing_price_columns_fail_closed():
    with pytest.raises(RuntimeError, match="missing columns"):
        parse_candidates(pd.DataFrame([{"symbol": "XRP/USD"}]))
