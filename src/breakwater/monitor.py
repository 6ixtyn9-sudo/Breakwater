"""Monitored-slice scanning over the live universe.

Every monitored book row is checked against the latest completed bar of each
target symbol. A match produces a signal carrying the slice identity, side,
entry reference and an ATR stop. Signals are descriptive research outputs;
paper trading consumes them, live execution never fires from here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from breakwater.discovery import bin_states
from breakwater.features import compute_price_features
from breakwater.models import PairType, Side

STOP_ATR_MULT = Decimal("2")


@dataclass(frozen=True)
class SliceSignal:
    signal_id: str
    pair: str
    kind: str
    slice_id: str
    feature: str
    state: int
    side: Side
    observed_at: datetime
    bar_start: datetime
    entry_price: Decimal
    stop_price: Decimal
    atr: Decimal
    edge: float


def _frame(frames: dict[str, pd.DataFrame], pair: str) -> pd.DataFrame | None:
    return frames.get(pair.upper())


def _latest_state(
    frame: pd.DataFrame, feature: str, min_periods: int = 200
) -> tuple[int | None, pd.Series]:
    if len(frame) < min_periods:
        return None, pd.Series(dtype=float)
    binned = bin_states(frame, [feature], min_periods=min_periods)
    state_column = f"state_{feature}"
    latest = binned.dropna(subset=[state_column]).tail(1)
    if latest.empty:
        return None, pd.Series(dtype=float)
    return int(latest[state_column].iloc[-1]), latest.iloc[0]


def monitor_book(
    book_rows: list[dict],
    frames: dict[str, pd.DataFrame],
    *,
    server_time: datetime,
) -> list[SliceSignal]:
    signals: list[SliceSignal] = []
    seen = set()
    for row in book_rows:
        if row.get("status") != "monitored":
            continue
        slice_id = str(row["slice_id"])
        feature = str(row["feature"])
        state = int(row["state"])
        direction = str(row["side"]).upper()
        side = Side.BUY if direction == "LONG" else Side.SELL
        kind = str(row["kind"])
        for pair, frame in frames.items():
            if frame.empty or len(frame) < 60:
                continue
            featured = compute_price_features(frame)
            latest_state, latest_row = _latest_state(featured, feature)
            if latest_state != state:
                continue
            close = Decimal(str(latest_row["close"]))
            atr_raw = _atr(featured)
            if close <= 0 or atr_raw <= 0:
                continue
            atr = Decimal(str(atr_raw))
            stop = close - STOP_ATR_MULT * atr if side is Side.BUY else close + STOP_ATR_MULT * atr
            if stop <= 0:
                continue
            bar_start = latest_row["start"]
            digest = hashlib.sha256(
                f"{pair}|{slice_id}|{bar_start.isoformat()}".encode()
            ).hexdigest()[:16]
            if digest in seen:
                continue
            seen.add(digest)
            signals.append(SliceSignal(
                signal_id=digest,
                pair=pair.upper(),
                kind=kind,
                slice_id=slice_id,
                feature=feature,
                state=state,
                side=side,
                observed_at=server_time.astimezone(timezone.utc),
                bar_start=bar_start,
                entry_price=close,
                stop_price=stop,
                atr=atr,
                edge=float(row.get("mean_ret_costadj") or 0),
            ))
    return signals


def _atr(frame: pd.DataFrame) -> float:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    true_range = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    values = true_range.rolling(14).mean().dropna().to_numpy()
    return float(values[-1]) if len(values) else 0.0


def signal_payload(signal: SliceSignal) -> dict:
    return {
        "signal_id": signal.signal_id,
        "pair": signal.pair,
        "kind": signal.kind,
        "slice_id": signal.slice_id,
        "feature": signal.feature,
        "state": signal.state,
        "side": signal.side.value,
        "observed_at": signal.observed_at.isoformat(),
        "bar_start": signal.bar_start.isoformat(),
        "entry_price": str(signal.entry_price),
        "stop_price": str(signal.stop_price),
        "atr": str(signal.atr),
        "edge": signal.edge,
    }


def signal_pair_type(kind: str) -> PairType:
    return PairType.SPOT if kind == "SPOT" else PairType.FUTURE
