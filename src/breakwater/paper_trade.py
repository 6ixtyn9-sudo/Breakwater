"""Paper trading over monitored-slice signals.

Open paper positions persist between runs. Each run marks positions against
the latest completed bar: an MAE-calibrated ATR stop, a two-to-one target or
a time-stop closes the position, and the realised result is logged,
journaled and fed back into the slice book so decay gates see honest paper
results.

Paper is simulation only: it holds at most one position per kind (SPOT,
PERP) so evidence accumulates in both markets. The live-account mandate
(one position) is untouched.

Entry-side guards inherited from the predecessor system's lessons:

- book-only: only slices present in the monitored book are paper-traded;
  unvalidated fallback signals (big-wave) are research-only;
- falling-knife guard: a signal whose latest price has moved adversely
  beyond min(1.0 ATR, 2 percent) of the signal close is skipped;
- winner-capture premium: the reference entry is raised by
  min(0.25 ATR, 1 percent) for longs (lowered for shorts) so modest
  follow-through can fill instead of only adverse moves;
- fail-open visibility: every skipped entry is journaled with its reason
  (adverse / no_price / regime / not_book) instead of vanishing silently;
- immortal-trade guard: positions whose pair data has gone missing for
  more than 24 consecutive bars are closed at entry with fees, so no
  paper position lives forever on vanished data.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from breakwater.monitor import SliceSignal, regime_blocks
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
    "exit_reason",
    "entry_guard",
    "regime",
]

TARGET_R_MULTIPLE = Decimal("2")
TIME_STOP_BARS = 48
MISSING_BARS_EXIT = 24
SPOT_FEE_BPS = Decimal("20")
PERP_FEE_BPS = Decimal("26")
MAX_PAPER_POSITIONS = 6
MAX_PAPER_POSITIONS_PER_KIND = 3

ADVERSE_ATR_MULT = Decimal("1.0")
ADVERSE_CAP_BPS = Decimal("200")
PREMIUM_ATR_MULT = Decimal("0.25")
PREMIUM_CAP_BPS = Decimal("100")


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


def _migrate_log_header(path: Path) -> None:
    """Rewrite a log file whose header predates the audit columns.

    Rows written after the audit columns shipped carry 16 fields while the
    legacy header names only 13, so any csv.DictReader silently drops
    exit_reason, entry_guard and regime. This migration rewrites the file
    with the current header, padding legacy rows with empty strings.
    Idempotent: a file with the current header is left untouched.
    """
    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return
        if header == PAPER_LOG_HEADERS:
            return
        rows = list(reader)
    width = len(PAPER_LOG_HEADERS)
    migrated = [PAPER_LOG_HEADERS]
    for row in rows:
        if len(row) > width:
            row = row[:width]
        migrated.append(row + [""] * (width - len(row)))
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(migrated)
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
    if exists:
        _migrate_log_header(path)
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


def _latest_close(frame):
    if frame is None or frame.empty:
        return None
    return Decimal(str(frame.iloc[-1]["close"]))


def _entry_guard(
    signal: SliceSignal, frame, atr: Decimal
) -> tuple[str, Decimal]:
    """Return (guard_verdict, reference_entry_price)."""
    reference = signal.entry_price
    premium_frac = min(PREMIUM_ATR_MULT * atr / reference, PREMIUM_CAP_BPS / Decimal(10000))
    if signal.side.value == "BUY":
        reference = signal.entry_price * (Decimal(1) + premium_frac)
    else:
        reference = signal.entry_price * (Decimal(1) - premium_frac)
    latest = _latest_close(frame)
    if latest is None:
        return "no_price", reference
    adverse_frac = min(ADVERSE_ATR_MULT * atr / signal.entry_price, ADVERSE_CAP_BPS / Decimal(10000))
    if signal.side.value == "BUY" and latest < signal.entry_price * (Decimal(1) - adverse_frac):
        return "adverse_blocked", reference
    if signal.side.value == "SELL" and latest > signal.entry_price * (Decimal(1) + adverse_frac):
        return "adverse_blocked", reference
    return "passed", reference


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
    book_slice_ids: set[str],
    server_time: datetime,
    missing_bars_exit: int = MISSING_BARS_EXIT,
) -> dict:
    closed_rows: list[dict] = []
    open_positions = read_positions(positions_path)
    surviving = []

    for position in open_positions:
        frame = frames.get(str(position["pair"]).upper())
        side = str(position["side"])
        entry = Decimal(str(position["entry_price"]))
        stop = Decimal(str(position["stop_price"]))
        notional_zar = Decimal(str(position["notional_zar"]))
        if frame is None or frame.empty:
            missing = int(position.get("missing_bars") or 0) + 1
            if missing >= missing_bars_exit:
                fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
                fees = notional_zar * fee_bps / Decimal(10000)
                closed_rows.append({
                    "closed_at": server_time.isoformat(),
                    "signal_id": str(position["signal_id"]),
                    "pair": str(position["pair"]),
                    "kind": str(position["kind"]),
                    "slice_id": str(position["slice_id"]),
                    "side": side,
                    "entry_price": str(entry),
                    "exit_price": str(entry),
                    "stop_price": str(stop),
                    "notional_zar": str(notional_zar),
                    "pnl_zar": f"{-fees:.4f}",
                    "outcome": "loss",
                    "bars_held": str(position.get("bars_held") or 0),
                    "exit_reason": "stale_data",
                    "entry_guard": str(position.get("entry_guard") or ""),
                })
                apply_signal_feedback(
                    book_path,
                    str(position["slice_id"]),
                    bar_epoch=int(server_time.timestamp()),
                    outcome="loss",
                    pnl_zar=float(-fees),
                )
                append_cooldown(cooldown_path, {
                    "stopped_at": server_time.isoformat(),
                    "slice_id": str(position["slice_id"]),
                    "pair": str(position["pair"]),
                    "signal_id": str(position["signal_id"]),
                    "pnl_zar": f"{-fees:.4f}",
                    "reason": "stale_data",
                })
                continue
            position["missing_bars"] = str(missing)
            surviving.append(position)
            continue

        last = frame.iloc[-1]
        close = Decimal(str(last["close"]))
        high = Decimal(str(last["high"]))
        low = Decimal(str(last["low"]))
        bars_held = int(position.get("bars_held") or 0) + 1
        target = entry + (entry - stop) * TARGET_R_MULTIPLE if side == "BUY" else (
            entry - (stop - entry) * TARGET_R_MULTIPLE
        )
        exit_price = None
        exit_reason = None
        outcome = None
        if side == "BUY":
            if low <= stop:
                exit_price, exit_reason, outcome = stop, "stop", "loss"
            elif high >= target:
                exit_price, exit_reason, outcome = target, "target", "win"
        else:
            if high >= stop:
                exit_price, exit_reason, outcome = stop, "stop", "loss"
            elif low <= target:
                exit_price, exit_reason, outcome = target, "target", "win"
        if exit_price is None and bars_held >= TIME_STOP_BARS:
            exit_price = close
            exit_reason = "time_stop"
            outcome = "win" if (
                close > entry if side == "BUY" else close < entry
            ) else "loss"
        if exit_price is None:
            position["bars_held"] = str(bars_held)
            position["missing_bars"] = "0"
            surviving.append(position)
            continue

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
            "exit_reason": exit_reason,
            "entry_guard": str(position.get("entry_guard") or ""),
        })
        apply_signal_feedback(
            book_path,
            str(position["slice_id"]),
            bar_epoch=int(last["start"].timestamp()),
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
                "reason": exit_reason,
            })

    for row in closed_rows:
        append_log(log_path, row)

    skipped = 0
    slot_full = 0
    pair_held = 0
    open_pairs = {str(position["pair"]).upper() for position in surviving}
    candidates = sorted(signals, key=lambda s: (-abs(s.edge), s.pair))
    for signal in candidates:
        if len(surviving) >= MAX_PAPER_POSITIONS:
            slot_full += 1
            continue
        kind_open = sum(1 for position in surviving if position.get("kind") == signal.kind)
        if kind_open >= MAX_PAPER_POSITIONS_PER_KIND:
            slot_full += 1
            continue
        if signal.pair.upper() in open_pairs:
            pair_held += 1
            continue
        if signal.slice_id not in book_slice_ids:
            append_log(log_path, {
                "closed_at": server_time.isoformat(),
                "signal_id": signal.signal_id,
                "pair": signal.pair,
                "kind": signal.kind,
                "slice_id": signal.slice_id,
                "side": signal.side.value,
                "entry_price": str(signal.entry_price),
                "exit_price": "",
                "stop_price": str(signal.stop_price),
                "notional_zar": "0",
                "pnl_zar": "0",
                "outcome": "skipped",
                "bars_held": "0",
                "exit_reason": "not_book",
                "entry_guard": "not_book",
            })
            skipped += 1
            continue
        if regime_blocks(signal.side, signal.regime):
            append_log(log_path, {
                "closed_at": server_time.isoformat(),
                "signal_id": signal.signal_id,
                "pair": signal.pair,
                "kind": signal.kind,
                "slice_id": signal.slice_id,
                "side": signal.side.value,
                "entry_price": str(signal.entry_price),
                "exit_price": "",
                "stop_price": str(signal.stop_price),
                "notional_zar": "0",
                "pnl_zar": "0",
                "outcome": "skipped",
                "bars_held": "0",
                "exit_reason": "regime",
                "entry_guard": "regime_blocked",
            })
            skipped += 1
            continue
        frame = frames.get(signal.pair.upper())
        guard, reference = _entry_guard(signal, frame, signal.atr)
        if guard == "adverse_blocked":
            append_log(log_path, {
                "closed_at": server_time.isoformat(),
                "signal_id": signal.signal_id,
                "pair": signal.pair,
                "kind": signal.kind,
                "slice_id": signal.slice_id,
                "side": signal.side.value,
                "entry_price": str(signal.entry_price),
                "exit_price": "",
                "stop_price": str(signal.stop_price),
                "notional_zar": "0",
                "pnl_zar": "0",
                "outcome": "skipped",
                "bars_held": "0",
                "exit_reason": "adverse",
                "entry_guard": "adverse_blocked",
            })
            skipped += 1
            continue
        notional_zar = _paper_size(signal, policy, usdc_zar)
        if notional_zar <= 0:
            continue
        surviving.append({
            "signal_id": signal.signal_id,
            "pair": signal.pair,
            "kind": signal.kind,
            "slice_id": signal.slice_id,
            "side": signal.side.value,
            "entry_price": str(reference),
            "stop_price": str(
                reference - (signal.entry_price - signal.stop_price)
                if signal.side.value == "BUY"
                else reference + (signal.stop_price - signal.entry_price)
            ),
            "notional_zar": str(notional_zar),
            "bars_held": "0",
            "missing_bars": "0",
            "entry_guard": guard,
        })
        open_pairs.add(signal.pair.upper())

    write_positions(positions_path, surviving)
    return {
        "closed": len(closed_rows),
        "open": len(surviving),
        "new_signals": len(signals),
        "skipped": skipped,
        "slot_full": slot_full,
        "pair_held": pair_held,
    }
