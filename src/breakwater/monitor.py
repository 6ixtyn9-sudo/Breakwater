"""Monitored-slice scanning over the live universe.

Regime gating (evidence-aware):
- Strict mode blocks longs in bear and shorts in bull.
- Evidence-aware mode blocks only when the slice is hostile-unproven
  (`hostile_unproven=True`).

Environment:
- BREAKWATER_REGIME_GATE_STRICT=1 forces strict gating.
Optional book filters (OFF by default; freeze-friendly):
- BREAKWATER_FILTER_NON_DIRECTIONAL_BOOK=1 (preferred):
    skip rows where edge_is_directional_net != "True"
  Back-compat: if edge_is_directional_net is missing, we fall back to
  edge_semantics_version == "net_v1" (if present).
- BREAKWATER_FILTER_NONPOSITIVE_BOOK=1:
    skip rows where mean_ret_costadj <= 0
These allow you to keep legacy carried rows in the book for visibility while
preventing them from emitting new signals unless you explicitly opt in.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import numpy as np
import pandas as pd

from breakwater.discovery import bin_states
from breakwater.features import compute_price_features
from breakwater.models import Side

DEFAULT_STOP_ATR_MULT = Decimal("2.0")
REGIME_MIN_BARS = 200

EDGE_SEMANTICS_NET_V1 = "net_v1"


def _coerce_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "":
        return default
    return text in {"1", "true", "yes", "y", "on"}


def _env_bool(name: str, default: str = "0") -> bool:
    return _coerce_bool(os.getenv(name, default), default=False)


REGIME_GATE_STRICT = _env_bool("BREAKWATER_REGIME_GATE_STRICT", "0")
FILTER_NON_DIRECTIONAL_BOOK = _env_bool("BREAKWATER_FILTER_NON_DIRECTIONAL_BOOK", "0")
FILTER_NONPOSITIVE_BOOK = _env_bool("BREAKWATER_FILTER_NONPOSITIVE_BOOK", "0")


def _coerce_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _edge_is_directional_net(row: dict) -> bool:
    """True if the row is stamped as directional net-edge.
    Primary: edge_is_directional_net == "True"
    Back-compat: edge_semantics_version == "net_v1"
    """
    flag = row.get("edge_is_directional_net")
    if str(flag).strip() == "True":
        return True
    if str(flag).strip() == "False":
        return False

    version = str(row.get("edge_semantics_version") or "")
    if version == EDGE_SEMANTICS_NET_V1:
        return True

    return False


def regime_of(frame: pd.DataFrame) -> str:
    """Bull / bear / neutral / unknown from the SMA-50/200 crossover prior."""
    if frame is None or len(frame) < REGIME_MIN_BARS:
        return "unknown"
    close = frame["close"].astype(float)
    sma50 = float(close.rolling(50).mean().iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1])
    last = float(close.iloc[-1])
    if not np.isfinite(sma50) or not np.isfinite(sma200):
        return "unknown"
    if sma50 > sma200 and last > sma50:
        return "bull"
    if sma50 < sma200 and last < sma50:
        return "bear"
    return "neutral"


def regime_blocks(side: Side, regime: str, hostile_unproven: bool = True) -> bool:
    """Block side in hostile regime.

    - If strict: always block hostile regime.
    - If not strict: block only when hostile_unproven=True.
    """
    if side is Side.BUY and regime == "bear":
        return True if REGIME_GATE_STRICT else hostile_unproven
    if side is Side.SELL and regime == "bull":
        return True if REGIME_GATE_STRICT else hostile_unproven
    return False


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
    horizon_bars: int = 1
    stop_atr_mult: float = 2.0
    regime: str = "unknown"
    hostile_unproven: bool = True


def _latest_state(
    frame: pd.DataFrame,
    feature: str,
    min_periods: int | None = None,
) -> tuple[int | None, pd.Series]:
    if min_periods is None:
        try:
            min_periods = int(os.getenv("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", "200"))
        except ValueError:
            min_periods = 200

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
    frames_by_kind: dict[str, dict],
    *,
    server_time: datetime,
) -> tuple[list[SliceSignal], list[dict]]:
    signals: list[SliceSignal] = []
    blocked: list[dict] = []
    seen = set()

    for row in book_rows:
        if row.get("status") != "monitored":
            continue

        # Optional: only allow rows we can trust as directional net-edge
        if FILTER_NON_DIRECTIONAL_BOOK and not _edge_is_directional_net(row):
            continue
        # Optional: only allow net-positive book rows
        if FILTER_NONPOSITIVE_BOOK:
            edge_val = _coerce_float(row.get("mean_ret_costadj"), 0.0)
            if edge_val <= 0.0:
                continue

        slice_id = str(row["slice_id"])
        feature = str(row["feature"])
        state = int(row["state"])
        direction = str(row["side"]).upper()
        side = Side.BUY if direction == "LONG" else Side.SELL
        kind = str(row["kind"])
        try:
            stop_atr_mult = float(row.get("stop_atr_mult") or DEFAULT_STOP_ATR_MULT)
        except (TypeError, ValueError):
            stop_atr_mult = float(DEFAULT_STOP_ATR_MULT)
        if stop_atr_mult <= 0:
            stop_atr_mult = float(DEFAULT_STOP_ATR_MULT)

        try:
            horizon_bars = int(row.get("horizon_bars") or 1)
        except (TypeError, ValueError):
            horizon_bars = 1
        if horizon_bars <= 0:
            horizon_bars = 1
        hostile_unproven = _coerce_bool(row.get("hostile_unproven"), default=True)

        for pair, frame in (frames_by_kind.get(kind) or {}).items():
            if frame is None or frame.empty or len(frame) < 60:
                continue

            regime = regime_of(frame)
            featured = compute_price_features(frame)
            latest_state, latest_row = _latest_state(featured, feature)
            if latest_state != state:
                continue

            if regime_blocks(side, regime, hostile_unproven):
                blocked.append(
                    {
                        "pair": pair.upper(),
                        "kind": kind,
                        "slice_id": slice_id,
                        "side": side.value,
                        "regime": regime,
                        "hostile_unproven": hostile_unproven,
                    }
                )
                continue
            close = Decimal(str(latest_row["close"]))
            atr_raw = _atr(featured)
            if close <= 0 or atr_raw <= 0:
                continue

            atr = Decimal(str(atr_raw))
            stop_distance = Decimal(str(stop_atr_mult)) * atr
            stop = close - stop_distance if side is Side.BUY else close + stop_distance
            if stop <= 0:
                continue
            bar_start = latest_row["start"]
            digest = hashlib.sha256(f"{pair}|{slice_id}|{bar_start.isoformat()}".encode()).hexdigest()[:16]
            if digest in seen:
                continue
            seen.add(digest)
            signals.append(
                SliceSignal(
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
                    horizon_bars=horizon_bars,
                    stop_atr_mult=stop_atr_mult,
                    regime=regime,
                    hostile_unproven=hostile_unproven,
                )
            )
    return signals, blocked


def _atr(frame: pd.DataFrame) -> float:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    values = true_range.rolling(14).mean().dropna().to_numpy()
    return float(values[-1]) if len(values) else 0.0


def signal_pair_type(kind: str):
    from breakwater.models import PairType
    return PairType.SPOT if kind == "SPOT" else PairType.FUTURE


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
        "horizon_bars": int(signal.horizon_bars),
        "stop_atr_mult": signal.stop_atr_mult,
        "regime": signal.regime,
        "hostile_unproven": bool(signal.hostile_unproven),
    }
