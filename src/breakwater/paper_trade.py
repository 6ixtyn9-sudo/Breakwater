"""Paper trading over monitored-slice signals.

Open paper positions persist between runs. Each run marks positions against
the latest completed bar: an ATR stop, a two-to-one target or a time-stop
closes the position, and the realised result is logged, journaled and fed
back into the slice book so decay gates see honest paper results.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from breakwater.monitor import SliceSignal
from breakwater.research_lifecycle import apply_signal_feedback

PAPER_LOG_HEADERS = [
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
]

TARGET_R_MULTIPLE = Decimal("2")
TIME_STOP_BARS = 48
SPOT_FEE_BPS = Decimal("20")
PERP_FEE_BPS = Decimal("26")
MAX_PAPER_POSITIONS = 1


def read_positions(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
        return payload if isinstance(payload, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def write_positions(path: Path, positions: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w") as handle:
            json.dump(positions, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def append_log(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_LOG_HEADERS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)
        handle.flush()


def append_cooldown(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    journal = []
    if path.exists():
        try:
            journal = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            journal = []
    if not isinstance(journal, list):
        journal = []
    journal.append(entry)
    journal = journal[-200:]
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w") as handle:
            json.dump(journal, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _paper_size(signal: SliceSignal, policy, usdc_zar: Decimal) -> Decimal:
    risk_fraction = abs(signal.entry_price - signal.stop_price) / signal.entry_price
    if risk_fraction <= 0:
        return Decimal(0)
    notional_zar = min(
        policy.risk_per_trade_zar / risk_fraction,
        policy.max_position_notional_zar,
    )
    if signal.kind == "PERP" and notional_zar / usdc_zar < Decimal("11"):
        return Decimal(0)
    return notional_zar


def run_paper_cycle(
    *,
    signals: list[SliceSignal],
    frames: dict,
    policy,
    usdc_zar: Decimal,
    positions_path: Path,
    log_path: Path,
    cooldown_path: Path,
    book_path: Path,
    server_time: datetime,
) -> dict:
    closed_rows: list[dict] = []
    open_positions = read_positions(positions_path)
    surviving = []

    for position in open_positions:
        frame = frames.get(str(position["pair"]).upper())
        if frame is None or frame.empty:
            surviving.append(position)
            continue
        last = frame.iloc[-1]
        close = Decimal(str(last["close"]))
        high = Decimal(str(last["high"]))
        low = Decimal(str(last["low"]))
        side = str(position["side"])
        entry = Decimal(str(position["entry_price"]))
        stop = Decimal(str(position["stop_price"]))
        bars_held = int(position["bars_held"]) + 1
        target = entry + (entry - stop) * TARGET_R_MULTIPLE if side == "BUY" else (
            entry - (stop - entry) * TARGET_R_MULTIPLE
        )
        exit_price = None
        outcome = None
        if side == "BUY":
            if low <= stop:
                exit_price, outcome = stop, "loss"
            elif high >= target:
                exit_price, outcome = target, "win"
        else:
            if high >= stop:
                exit_price, outcome = stop, "loss"
            elif low <= target:
                exit_price, outcome = target, "win"
        if exit_price is None and bars_held >= TIME_STOP_BARS:
            exit_price, outcome = close, "win" if (
                close > entry if side == "BUY" else close < entry
            ) else "loss"
        if exit_price is None:
            position["bars_held"] = str(bars_held)
            surviving.append(position)
            continue

        notional_zar = Decimal(str(position["notional_zar"]))
        fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
        direction = Decimal(1) if side == "BUY" else Decimal(-1)
        gross = (exit_price - entry) / entry * direction * notional_zar
        fees = notional_zar * fee_bps / Decimal(10000)
        pnl_zar = gross - fees
        closed_rows.append({
            "closed_at": server_time.isoformat(),
            "signal_id": str(position["signal_id"]),
            "pair": str(position["pair"]),
            "kind": str(position["kind"]),
            "slice_id": str(position["slice_id"]),
            "side": side,
            "entry_price": str(entry),
            "exit_price": str(exit_price),
            "stop_price": str(stop),
            "notional_zar": str(notional_zar),
            "pnl_zar": f"{pnl_zar:.4f}",
            "outcome": outcome,
            "bars_held": str(bars_held),
        })
        bar_epoch = int(last["start"].timestamp())
        apply_signal_feedback(
            book_path,
            str(position["slice_id"]),
            bar_epoch=bar_epoch,
            outcome=outcome,
            pnl_zar=float(pnl_zar),
        )
        if outcome == "loss":
            append_cooldown(cooldown_path, {
                "stopped_at": server_time.isoformat(),
                "slice_id": str(position["slice_id"]),
                "pair": str(position["pair"]),
                "signal_id": str(position["signal_id"]),
                "pnl_zar": f"{pnl_zar:.4f}",
            })

    for row in closed_rows:
        append_log(log_path, row)

    for signal in signals:
        if len(surviving) >= MAX_PAPER_POSITIONS:
            break
        notional_zar = _paper_size(signal, policy, usdc_zar)
        if notional_zar <= 0:
            continue
        surviving.append({
            "signal_id": signal.signal_id,
            "pair": signal.pair,
            "kind": signal.kind,
            "slice_id": signal.slice_id,
            "side": signal.side.value,
            "entry_price": str(signal.entry_price),
            "stop_price": str(signal.stop_price),
            "notional_zar": str(notional_zar),
            "bars_held": "0",
        })

    write_positions(positions_path, surviving)
    return {
        "closed": len(closed_rows),
        "open": len(surviving),
        "new_signals": len(signals),
    }
