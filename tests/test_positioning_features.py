"""Positioning inputs as features: sources, alignment, attach, discovery path."""

from __future__ import annotations

import gzip
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from breakwater import positioning_features as pf
from breakwater.discovery import discover_slices
from breakwater.features import FEATURE_COLUMNS, compute_price_features
from breakwater.positioning_features import (
    POSITIONING_FEATURE_COLUMNS,
    SOURCE_COLUMNS,
    PositioningContext,
    attach_sources,
    compute_positioning_features,
    load_tape,
)

T0 = datetime(2026, 10, 19, tzinfo=timezone.utc)


def _candles(n: int, seed: int = 3, start: datetime = T0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 0.5, n))
    return pd.DataFrame(
        {
            "start": pd.date_range(start, periods=n, freq="h", tz="UTC"),
            "open": close - 0.2,
            "high": close + 0.4,
            "low": close - 0.4,
            "close": close,
            "volume": rng.uniform(10, 50, n),
        }
    )


def _tape_row(coin: str, hour: datetime, **over) -> dict:
    row = {
        "snapshot_at": (hour + timedelta(minutes=5)).isoformat(),
        "snapshot_hour": hour.strftime("%Y-%m-%dT%H:00Z"),
        "coin": coin,
        "premium": "0.0010",
        "funding_hourly": "0.0000125",
        "oi_notional_usd": "1000000",
        "imbalance_5": "0.20",
    }
    row.update({k: str(v) for k, v in over.items()})
    return row


def _write_tape(directory, rows: list[dict], name: str, packed: bool = False) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    header = list(rows[0].keys())
    text = ",".join(header) + "\n" + "".join(",".join(r[h] for h in header) + "\n" for r in rows)
    path = directory / name
    if packed:
        with gzip.open(path, "wt", newline="") as handle:
            handle.write(text)
    else:
        path.write_text(text)


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------


def test_load_tape_aligns_funding_forward_and_state_in_place(tmp_path):
    pos = tmp_path / "positioning"
    h0, h1 = T0, T0 + timedelta(hours=1)
    _write_tape(
        pos,
        [_tape_row("BTC", h0, funding_hourly="0.0001", premium="0.002")],
        "2026-W43.csv.gz",
        packed=True,
    )
    _write_tape(
        pos, [_tape_row("BTC", h1, funding_hourly="0.0002", premium="0.003")], "2026-W44.csv"
    )

    tape = load_tape(tmp_path).set_index("start")
    assert list(tape.columns) == ["coin", *SOURCE_COLUMNS]
    # State at H attaches to bar H; the rate captured at H pays at H+1.
    assert tape.loc[pd.Timestamp(h0), "pos_premium"] == 0.002
    assert np.isnan(tape.loc[pd.Timestamp(h0), "pos_funding"])
    assert tape.loc[pd.Timestamp(h1), "pos_funding"] == 0.0001
    assert tape.loc[pd.Timestamp(h1), "pos_premium"] == 0.003
    assert tape.loc[pd.Timestamp(h1 + timedelta(hours=1)), "pos_funding"] == 0.0002


def test_load_tape_prefers_backfilled_history_over_tape(tmp_path):
    pos = tmp_path / "positioning"
    h1 = T0 + timedelta(hours=1)
    _write_tape(
        pos, [_tape_row("BTC", T0, funding_hourly="0.0001", premium="0.002")], "2026-W43.csv"
    )
    (pos / "funding_history.csv").write_text(
        f"coin,time,funding_rate,premium\nBTC,{h1.isoformat()},0.0009,0.0090\n"
    )
    tape = load_tape(tmp_path).set_index("start")
    assert tape.loc[pd.Timestamp(h1), "pos_funding"] == 0.0009
    assert tape.loc[pd.Timestamp(h1), "pos_premium"] == 0.0090


def test_load_tape_without_directory_is_empty(tmp_path):
    tape = load_tape(tmp_path)
    assert tape.empty and list(tape.columns) == ["coin", "start", *SOURCE_COLUMNS]


# --------------------------------------------------------------------------
# Attach + features
# --------------------------------------------------------------------------


def test_attach_and_compute_features_are_finite_with_sources():
    frame = _candles(300)
    sources = pd.DataFrame(
        {
            "start": frame["start"],
            "pos_funding": 0.00001 * np.sin(np.arange(300) / 10),
            "pos_premium": 0.001 * np.cos(np.arange(300) / 7),
            "pos_oi_notional": 1e6 * (1 + 0.001 * np.arange(300)),
            "pos_imbalance_5": np.linspace(-0.5, 0.5, 300),
        }
    )
    attached = attach_sources(frame, sources)
    featured = compute_price_features(attached)
    for column in POSITIONING_FEATURE_COLUMNS:
        assert column in featured.columns and column in FEATURE_COLUMNS
    tail = featured.tail(30)
    assert np.isfinite(tail[POSITIONING_FEATURE_COLUMNS].to_numpy()).all()

    # OI change is a 24-bar ratio; divergence carries the sign of the 24-bar return.
    i = 100
    expected = attached["pos_oi_notional"].iloc[i] / attached["pos_oi_notional"].iloc[i - 24] - 1.0
    assert abs(featured["feat_oi_chg_24"].iloc[i] - expected) < 1e-12
    ret_sign = np.sign(frame["close"].iloc[i] / frame["close"].iloc[i - 24] - 1.0)
    assert featured["feat_oi_ret_div"].iloc[i] == ret_sign * featured["feat_oi_chg_24"].iloc[i]
    assert (
        abs(
            featured["feat_funding_cum_24"].iloc[i]
            - sources["pos_funding"].iloc[i - 23 : i + 1].sum()
        )
        < 1e-15
    )


def test_features_are_nan_without_sources_and_partial_sources_stay_partial():
    bare = compute_positioning_features(_candles(60))
    assert bare[POSITIONING_FEATURE_COLUMNS].isna().all().all()

    frame = _candles(60)
    frame["pos_funding"] = 0.00001
    partial = compute_positioning_features(frame)
    assert partial["feat_funding_rate"].notna().all()
    assert partial["feat_funding_cum_24"].iloc[23:].notna().all()
    assert partial["feat_oi_chg_24"].isna().all()
    assert partial["feat_book_imb_5"].isna().all()


def test_attach_sources_only_fills_matching_bars():
    frame = _candles(10)
    sources = pd.DataFrame({"start": frame["start"].iloc[[2, 5]], "pos_premium": [0.5, 0.7]})
    attached = attach_sources(frame, sources)
    assert attached["pos_premium"].notna().sum() == 2
    assert attached["pos_premium"].iloc[5] == 0.7
    assert attached["pos_funding"].isna().all()


# --------------------------------------------------------------------------
# Context (what the engine's frame loader uses)
# --------------------------------------------------------------------------


def _fake_history(coin, *, start, end, session=None):
    hours = pd.date_range(pd.Timestamp(start).ceil("h"), pd.Timestamp(end).floor("h"), freq="h")
    return [
        {"coin": coin, "time": h.isoformat(), "funding_rate": "0.00005", "premium": "0.0004"}
        for h in hours
    ]


def test_context_attaches_history_and_tape_to_native_perp_only(tmp_path, monkeypatch):
    monkeypatch.setattr(pf._positioning, "fetch_funding_history", _fake_history)
    pos = tmp_path / "positioning"
    rows = [
        _tape_row("BTC", T0 + timedelta(hours=k), oi_notional_usd=str(1_000_000 + k))
        for k in range(48)
    ]
    _write_tape(pos, rows, "2026-W43.csv")

    ctx = PositioningContext(
        tmp_path, enabled=True, fetch_funding=True, now=T0 + timedelta(hours=47)
    )
    frame = _candles(48)

    perp = ctx.attach("BTCUSDC", "PERP", frame)
    assert perp["pos_funding"].notna().all()  # history covers every bar
    assert perp["pos_funding"].iloc[-1] == 0.00005
    assert perp["pos_oi_notional"].iloc[-1] == 1_000_047  # tape row for the last bar
    assert perp["pos_imbalance_5"].iloc[0] == 0.2
    assert ctx.summary()["attached_pairs"] == 1

    spot = ctx.attach("BTCZAR", "SPOT", frame)
    assert spot[SOURCE_COLUMNS].isna().all().all()
    hip3 = ctx.attach("xyz:AAPL", "PERP", frame)
    assert hip3[SOURCE_COLUMNS].isna().all().all()
    assert ctx.summary()["attached_pairs"] == 1


def test_context_history_wins_over_tape_funding_and_tape_fills_gaps(tmp_path, monkeypatch):
    def short_history(coin, *, start, end, session=None):
        # History only covers the first 10 bars; tape must fill the rest.
        return _fake_history(coin, start=start, end=T0 + timedelta(hours=9), session=session)

    monkeypatch.setattr(pf._positioning, "fetch_funding_history", short_history)
    pos = tmp_path / "positioning"
    _write_tape(
        pos,
        [_tape_row("BTC", T0 + timedelta(hours=k), funding_hourly="0.0003") for k in range(30)],
        "2026-W43.csv",
    )
    ctx = PositioningContext(
        tmp_path, enabled=True, fetch_funding=True, now=T0 + timedelta(hours=29)
    )
    out = ctx.attach("BTCUSDC", "PERP", _candles(30))
    assert out["pos_funding"].iloc[5] == 0.00005  # history
    assert out["pos_funding"].iloc[20] == 0.0003  # tape (shifted +1h)


def test_context_fetch_failure_is_recorded_not_raised(tmp_path, monkeypatch):
    def boom(coin, *, start, end, session=None):
        raise RuntimeError("venue down")

    monkeypatch.setattr(pf._positioning, "fetch_funding_history", boom)
    ctx = PositioningContext(tmp_path, enabled=True, fetch_funding=True, now=T0)
    out = ctx.attach("BTCUSDC", "PERP", _candles(20))
    assert out[SOURCE_COLUMNS].isna().all().all()
    assert "BTCUSDC" in ctx.errors


def test_context_kill_switch_skips_everything(tmp_path, monkeypatch):
    calls = []

    def spy(coin, **kwargs):
        calls.append(coin)
        return []

    monkeypatch.setattr(pf._positioning, "fetch_funding_history", spy)
    monkeypatch.setenv("BREAKWATER_POSITIONING_FEATURES", "0")
    ctx = PositioningContext(tmp_path, now=T0)
    out = ctx.attach("BTCUSDC", "PERP", _candles(20))
    assert not ctx.enabled and calls == []
    assert out[SOURCE_COLUMNS].isna().all().all()


def test_context_uses_venue_case_from_tape(tmp_path, monkeypatch):
    seen = []

    def spy(coin, **kwargs):
        seen.append(coin)
        return []

    monkeypatch.setattr(pf._positioning, "fetch_funding_history", spy)
    _write_tape(tmp_path / "positioning", [_tape_row("kBONK", T0)], "2026-W43.csv")
    ctx = PositioningContext(tmp_path, enabled=True, fetch_funding=True, now=T0)
    ctx.attach("KBONKUSDC", "PERP", _candles(5))
    assert seen == ["kBONK"]


# --------------------------------------------------------------------------
# Discovery path: a positioning feature yields slices like any other feature
# --------------------------------------------------------------------------


def test_positioning_feature_reaches_discovery():
    rng = np.random.default_rng(5)
    parts = []
    for k in range(3):
        frame = _candles(400, seed=k)
        frame["symbol"] = f"P{k}USDC"
        funding = rng.normal(0, 1e-5, 400)
        frame["pos_funding"] = funding
        # Plant a relationship so at least one state is non-empty and testable.
        frame["close"] = frame["close"] * (1 + np.where(funding > 0, -0.002, 0.002)).cumprod()
        parts.append(compute_price_features(frame))
    pooled = pd.concat(parts, ignore_index=True)
    columns = ["feat_funding_rate", "feat_ret_1"]
    found = discover_slices(
        pooled, kind="PERP", feature_columns=columns, cost_bps=9.0, horizon_bars=1
    )
    features = {row.feature for row in found}
    assert "feat_funding_rate" in features
    assert any(row.feature == "feat_funding_rate" and row.n > 0 for row in found)
