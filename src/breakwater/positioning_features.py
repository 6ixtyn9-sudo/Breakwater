"""Positioning inputs (funding, basis, open interest, book imbalance) as features.

Why
---
Seven days of the frozen pipeline (2026-10-18 → 10-25) showed the price-state
feature set validates whatever the regime label favours and the book turns
over ~85% a night. The positioning tape (``positioning.py``) and Hyperliquid's
``fundingHistory`` carry information that is not a function of the candle:
who is paying whom to hold, how much is positioned, and which way the book
leans. This module turns them into ``feat_*`` columns on the per-pair candle
frame so they go through the *same* discovery → validation → book → paper
path as every other feature. Nothing downstream changes; the test is the one
that matters — whether a positioning slice stays in the book.

Sources and alignment (one bar = one UTC hour, ``start`` = bar open)
---------------------------------------------------------------------
``fundingHistory`` (primary for funding and premium, deep history):
  ``time`` is the payment time T. The rate paid at T is attached to the bar
  that opens at T. The forming bar in the hourly scan therefore carries the
  rate just paid, which is available minutes after the hour.
Positioning tape (OI, book; fallback for funding/premium, ~7 days so far):
  ``snapshot_hour`` H is captured at H:0x. ``funding_hourly`` there is the
  rate that *will* be paid at H+1, so it is attached to bar H+1 to match the
  history semantics; ``premium``, OI and book are states at H and attach to
  bar H.

Spot frames and HIP-3 frames never get the source columns; every positioning
feature is NaN there, which ``bin_states`` treats as "no state".

Kill switch: ``BREAKWATER_POSITIONING_FEATURES=0`` skips the attach entirely
(all positioning features NaN). ``BREAKWATER_POSITIONING_FUNDING_FETCH=0``
skips the ``fundingHistory`` call and relies on the tape alone.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from breakwater import positioning as _positioning
from breakwater.perpdata import pair_to_coin
from breakwater.positioning import FUNDING_HISTORY_FILENAME, positioning_dir, read_snapshots

# Feature name -> comment, kept in the same style as features.FEATURE_COLUMNS.
POSITIONING_FEATURE_COLUMNS = [
    "feat_funding_rate",  # hourly funding paid at bar open: >0 longs pay (crowded long), <0 shorts pay
    "feat_funding_cum_24",  # 24-bar sum of funding: persistent crowding, not a one-hour blip
    "feat_premium",  # mark vs oracle premium at bar open: basis proxy
    "feat_oi_chg_24",  # open-interest notional / 24 bars ago - 1: positioning build or unwind
    "feat_oi_ret_div",  # sign(ret_24) * oi_chg_24: trend on new positions (>0) vs on closing (<0)
    "feat_book_imb_5",  # (bid depth - ask depth)/(bid + ask) over 5 levels: resting-order lean
]

# Raw inputs carried on the frame; prefixed so they never collide with a feature.
SOURCE_COLUMNS = ["pos_funding", "pos_premium", "pos_oi_notional", "pos_imbalance_5"]


def _env_on(name: str, default: str = "1") -> bool:
    return str(os.getenv(name, default)).strip().lower() not in {"0", "false", "no", "off", ""}


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _hour(ts: pd.Series) -> pd.Series:
    return pd.to_datetime(ts, utc=True, errors="coerce", format="mixed").dt.floor("h")


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------


def load_tape(data_dir: Path) -> pd.DataFrame:
    """Tape + any back-filled funding history as one long frame.

    Columns: ``coin, start, pos_funding, pos_premium, pos_oi_notional,
    pos_imbalance_5`` — one row per (coin, bar). Funding from the tape is
    shifted forward one hour (see module docstring).
    """
    directory = positioning_dir(data_dir)
    parts: list[pd.DataFrame] = []

    rows = read_snapshots(directory) if directory.exists() else []
    if rows:
        tape = pd.DataFrame(rows)
        hour = _hour(tape["snapshot_hour"])

        def col(name: str) -> pd.Series:
            if name in tape.columns:
                return _num(tape[name])
            return pd.Series(np.nan, index=tape.index, dtype=float)

        state = pd.DataFrame(
            {
                "coin": tape["coin"].astype(str),
                "start": hour,
                "pos_premium": col("premium"),
                "pos_oi_notional": col("oi_notional_usd"),
                "pos_imbalance_5": col("imbalance_5"),
            }
        )
        funding = pd.DataFrame(
            {
                "coin": tape["coin"].astype(str),
                "start": hour + pd.Timedelta(hours=1),
                "pos_funding": col("funding_hourly"),
            }
        )
        parts.append(state)
        parts.append(funding)

    history_path = directory / FUNDING_HISTORY_FILENAME
    if history_path.exists():
        hist = pd.read_csv(history_path)
        if not hist.empty:
            parts.append(
                pd.DataFrame(
                    {
                        "coin": hist["coin"].astype(str),
                        "start": _hour(hist["time"]),
                        "pos_funding": _num(hist["funding_rate"]),
                        "pos_premium": _num(hist["premium"]),
                        # History is the primary source: sort it first so it wins.
                        "_rank": 0,
                    }
                )
            )

    if not parts:
        return pd.DataFrame(columns=["coin", "start", *SOURCE_COLUMNS])
    long = pd.concat(parts, ignore_index=True)
    if "_rank" not in long.columns:
        long["_rank"] = 1
    long["_rank"] = long["_rank"].fillna(1)
    long = long.dropna(subset=["start"]).sort_values(["coin", "start", "_rank"])
    # First non-null per column wins within a (coin, start) — history before tape.
    merged = long.groupby(["coin", "start"], sort=True).first().reset_index()
    for column in SOURCE_COLUMNS:
        if column not in merged.columns:
            merged[column] = np.nan
    return merged[["coin", "start", *SOURCE_COLUMNS]]


def funding_history_frame(
    coin: str,
    *,
    start: datetime,
    end: datetime,
    session=None,
) -> pd.DataFrame:
    """``coin, start, pos_funding, pos_premium`` from ``fundingHistory``."""
    rows = _positioning.fetch_funding_history(coin, start=start, end=end, session=session)
    if not rows:
        return pd.DataFrame(columns=["coin", "start", "pos_funding", "pos_premium"])
    frame = pd.DataFrame(rows)
    return pd.DataFrame(
        {
            "coin": coin,
            "start": _hour(frame["time"]),
            "pos_funding": _num(frame["funding_rate"]),
            "pos_premium": _num(frame["premium"]),
        }
    ).dropna(subset=["start"])


# --------------------------------------------------------------------------
# Attach + features
# --------------------------------------------------------------------------


def attach_sources(frame: pd.DataFrame, sources: pd.DataFrame | None) -> pd.DataFrame:
    """Left-join ``sources`` (one coin's rows) onto the candle frame by bar."""
    df = frame.copy()
    for column in SOURCE_COLUMNS:
        if column not in df.columns:
            df[column] = np.nan
    if df.empty or sources is None or sources.empty or "start" not in df.columns:
        return df
    src = sources.copy()
    src["start"] = pd.to_datetime(src["start"], utc=True)
    src = src.drop_duplicates("start").set_index("start")
    starts = pd.to_datetime(df["start"], utc=True)
    for column in SOURCE_COLUMNS:
        if column in src.columns:
            pulled = starts.map(src[column]).astype(float)
            df[column] = df[column].astype(float).where(df[column].notna(), pulled)
    return df


def compute_positioning_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the positioning ``feat_*`` columns; NaN wherever a source is absent."""
    if df.empty:
        for column in POSITIONING_FEATURE_COLUMNS:
            df[column] = pd.Series(dtype=float)
        return df
    n = len(df)
    nan = pd.Series(np.nan, index=df.index, dtype=float)

    funding = _num(df["pos_funding"]) if "pos_funding" in df.columns else nan
    premium = _num(df["pos_premium"]) if "pos_premium" in df.columns else nan
    oi = _num(df["pos_oi_notional"]) if "pos_oi_notional" in df.columns else nan
    imbalance = _num(df["pos_imbalance_5"]) if "pos_imbalance_5" in df.columns else nan

    df["feat_funding_rate"] = funding
    # min_periods=24: a 24-hour sum means nothing with three hours in it.
    df["feat_funding_cum_24"] = funding.rolling(24, min_periods=24).sum()
    df["feat_premium"] = premium

    oi_prev = oi.shift(24)
    oi_chg = (oi / oi_prev.where(oi_prev > 0)) - 1.0
    df["feat_oi_chg_24"] = oi_chg

    close = _num(df["close"]) if "close" in df.columns else pd.Series(np.nan, index=df.index)
    ret_24 = close.pct_change(24) if n > 24 else pd.Series(np.nan, index=df.index)
    df["feat_oi_ret_div"] = np.sign(ret_24) * oi_chg

    df["feat_book_imb_5"] = imbalance
    return df


class PositioningContext:
    """Per-run holder: the tape loaded once, funding fetched per pair on demand."""

    def __init__(
        self,
        data_dir: Path | None,
        *,
        enabled: bool | None = None,
        fetch_funding: bool | None = None,
        session=None,
        now: datetime | None = None,
        lookback_hours: int = 1000,
    ) -> None:
        self.enabled = _env_on("BREAKWATER_POSITIONING_FEATURES") if enabled is None else enabled
        self.fetch_funding = (
            _env_on("BREAKWATER_POSITIONING_FUNDING_FETCH")
            if fetch_funding is None
            else fetch_funding
        )
        self.session = session
        self.now = now or datetime.now(timezone.utc)
        self.lookback_hours = max(48, int(lookback_hours))
        self.errors: dict[str, str] = {}
        self.attached: list[str] = []
        self._tape = pd.DataFrame(columns=["coin", "start", *SOURCE_COLUMNS])
        if self.enabled and data_dir is not None:
            try:
                self._tape = load_tape(Path(data_dir))
            except Exception as exc:  # the tape is advisory; never fail a scan over it
                self.errors["tape"] = f"{type(exc).__name__}: {exc}"[:140]
        self._venue_names = (
            {str(c).upper(): str(c) for c in self._tape["coin"].unique()} if len(self._tape) else {}
        )

    def venue_coin(self, pair: str) -> str | None:
        coin = pair_to_coin(pair)
        if coin is None:
            return None
        return self._venue_names.get(coin.upper(), coin)

    def sources_for(self, pair: str, frame: pd.DataFrame) -> pd.DataFrame | None:
        coin = self.venue_coin(pair)
        if coin is None:
            return None
        parts: list[pd.DataFrame] = []
        if len(self._tape):
            own = self._tape[self._tape["coin"].astype(str).str.upper() == coin.upper()]
            if len(own):
                parts.append(own)
        if self.fetch_funding and not frame.empty and "start" in frame.columns:
            starts = pd.to_datetime(frame["start"], utc=True)
            start = min(
                starts.min().to_pydatetime(), self.now - timedelta(hours=self.lookback_hours)
            )
            end = self.now + timedelta(hours=1)
            try:
                hist = funding_history_frame(coin, start=start, end=end, session=self.session)
                if len(hist):
                    parts.insert(0, hist)  # history first: it wins on overlap
            except Exception as exc:
                self.errors[pair.upper()] = f"{type(exc).__name__}: {exc}"[:140]
        if not parts:
            return None
        if len(parts) == 1:
            return parts[0]
        long = pd.concat(parts, ignore_index=True).sort_values("start", kind="stable")
        return long.groupby("start", sort=True).first().reset_index()

    def attach(self, pair: str, kind: str, frame: pd.DataFrame) -> pd.DataFrame:
        """Return ``frame`` with ``pos_*`` columns (NaN unless a native perp with data)."""
        if not self.enabled or kind != "PERP" or ":" in pair or frame is None or frame.empty:
            return attach_sources(frame, None) if frame is not None else frame
        sources = self.sources_for(pair, frame)
        out = attach_sources(frame, sources)
        if sources is not None and len(sources):
            self.attached.append(pair.upper())
        return out

    def summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "fetch_funding": self.fetch_funding,
            "tape_rows": int(len(self._tape)),
            "tape_coins": int(self._tape["coin"].nunique()) if len(self._tape) else 0,
            "attached_pairs": len(self.attached),
            "errors": dict(list(self.errors.items())[:10]),
        }
