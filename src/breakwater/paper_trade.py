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

Optional trailing (profit-protection) feature (OFF by default):
- A trailing stop can ratchet in the favorable direction once the position
  has moved +ACTIVATE_R in your favor (measured in R = initial risk).
- The trailing stop sits TRAIL_DISTANCE_R behind the best price seen.
- If enabled, a stop can become a profitable exit (so "stop" can be a win).

Horizon alignment (IMPORTANT):
If a position carries `horizon_bars` (>0), paper trading will exit at the bar
close once that many bars have elapsed (while still honoring the stop intrabar).
This aligns paper execution with the horizon the slice edge was researched on.

Migration (IMPORTANT):
Legacy open positions may predate `horizon_bars`/`regime` persistence. Each
cycle we load slice -> horizon from the monitored book (book_path) and
backfill any positions with missing/zero horizon, and any missing regime.

Metrics (fix):
We log two separate outcomes:
- `outcome`: legacy directional label (do not break old semantics)
- `pnl_outcome`: truth after fees (`win` if pnl_zar > 0 else `loss`)
Lifecycle feedback + cooldown uses `pnl_outcome` so slices are judged on realized PnL.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from breakwater.monitor import SliceSignal, regime_blocks, regime_of
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
    "outcome",        # legacy directional label
    "pnl_outcome",    # truth after fees
    "bars_held",
    "exit_reason",
    "entry_guard",
    "regime",
]

TARGET_R_MULTIPLE = Decimal("2")
TIME_STOP_BARS = int(os.getenv("BREAKWATER_PAPER_TIME_STOP_BARS", "48"))
MISSING_BARS_EXIT = 24

SPOT_FEE_BPS = Decimal("20")
PERP_FEE_BPS = Decimal("26")
MAX_PAPER_POSITIONS = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS", "6"))
MAX_PAPER_POSITIONS_PER_KIND = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_KIND", "3"))

ADVERSE_ATR_MULT = Decimal("1.0")
ADVERSE_CAP_BPS = Decimal("200")
PREMIUM_ATR_MULT = Decimal("0.25")
PREMIUM_CAP_BPS = Decimal("100")


def _env_bool(name: str, default: str = "0") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _env_decimal(name: str, default: str) -> Decimal:
    raw = os.getenv(name, default)
    try:
        return Decimal(str(raw))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


# Trailing feature flags (OFF by default).
TRAIL_ENABLE = _env_bool("BREAKWATER_TRAIL_ENABLE", "0")
TRAIL_ACTIVATE_R = _env_decimal("BREAKWATER_TRAIL_ACTIVATE_R", "1.0")
TRAIL_DISTANCE_R = _env_decimal("BREAKWATER_TRAIL_DISTANCE_R", "1.0")
TRAIL_IGNORE_TIME_STOP = _env_bool("BREAKWATER_TRAIL_IGNORE_TIME_STOP", "0")


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
    """Rewrite a log file whose header predates the current columns.

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


def _entry_guard(signal: SliceSignal, frame, atr: Decimal) -> tuple[str, Decimal]:
    """Return (guard_verdict, reference_entry_price)."""
    reference = signal.entry_price
    premium_frac = min(
        PREMIUM_ATR_MULT * atr / reference, PREMIUM_CAP_BPS / Decimal(10000)
    )
    if signal.side.value == "BUY":
        reference = signal.entry_price * (Decimal(1) + premium_frac)
    else:
        reference = signal.entry_price * (Decimal(1) - premium_frac)

    latest = _latest_close(frame)
    if latest is None:
        return "no_price", reference

    adverse_frac = min(
        ADVERSE_ATR_MULT * atr / signal.entry_price, ADVERSE_CAP_BPS / Decimal(10000)
    )
    if signal.side.value == "BUY" and latest < signal.entry_price * (
        Decimal(1) - adverse_frac
    ):
        return "adverse_blocked", reference
    if signal.side.value == "SELL" and latest > signal.entry_price * (
        Decimal(1) + adverse_frac
    ):
        return "adverse_blocked", reference
    return "passed", reference


def _coerce_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on"}


def _coerce_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_book_horizon_map(book_path: Path) -> dict[str, int]:
    if not book_path or not book_path.exists():
        return {}
    try:
        with book_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                return {}
            out: dict[str, int] = {}
            for row in reader:
                sid = row.get("slice_id")
                if not sid:
                    continue
                hb = _coerce_int(row.get("horizon_bars"), 0)
                if hb > 0:
                    out[str(sid)] = hb
            return out
    except OSError:
        return {}


def _migrate_legacy_positions(open_positions: list[dict], *, horizon_map: dict[str, int], frames: dict) -> None:
    for position in open_positions:
        sid = str(position.get("slice_id") or "")
        hb_existing = _coerce_int(position.get("horizon_bars"), 0)

        if hb_existing <= 0 and sid:
            hb_book = horizon_map.get(sid, 0)
            if hb_book > 0:
                position["horizon_bars"] = str(hb_book)

        if not position.get("regime"):
            frame = frames.get(str(position.get("pair") or "").upper())
            if frame is not None and not frame.empty:
                position["regime"] = regime_of(frame)
            else:
                position["regime"] = "unknown"


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

    # Migration: ensure legacy positions pick up book horizon/regime so horizon exits engage.
    book_horizon_map = _load_book_horizon_map(book_path)
    if open_positions:
        _migrate_legacy_positions(open_positions, horizon_map=book_horizon_map, frames=frames)

    surviving: list[dict] = []

    # 1) Mark-to-market and close eligible existing positions
    for position in open_positions:
        frame = frames.get(str(position["pair"]).upper())
        side = str(position["side"])
        entry = Decimal(str(position["entry_price"]))
        stop = Decimal(str(position["stop_price"]))
        notional_zar = Decimal(str(position["notional_zar"]))

        horizon_bars = _coerce_int(position.get("horizon_bars"), 0)
        if horizon_bars < 0:
            horizon_bars = 0
        if horizon_bars <= 0:
            sid = str(position.get("slice_id") or "")
            horizon_bars = book_horizon_map.get(sid, 0)

        position_regime = str(position.get("regime") or "")
        if not position_regime:
            if frame is not None and not frame.empty:
                position_regime = regime_of(frame)
            else:
                position_regime = "unknown"

        if frame is None or frame.empty:
            missing = _coerce_int(position.get("missing_bars"), 0) + 1
            if missing >= missing_bars_exit:
                fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
                fees = notional_zar * fee_bps / Decimal(10000)
                pnl_zar = -fees
                pnl_outcome = "loss"

                closed_rows.append(
                    {
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
                        "pnl_zar": f"{pnl_zar:.4f}",
                        "outcome": "loss",
                        "pnl_outcome": pnl_outcome,
                        "bars_held": str(position.get("bars_held") or 0),
                        "exit_reason": "stale_data",
                        "entry_guard": str(position.get("entry_guard") or ""),
                        "regime": position_regime,
                    }
                )

                apply_signal_feedback(
                    book_path,
                    str(position["slice_id"]),
                    bar_epoch=int(server_time.timestamp()),
                    outcome=pnl_outcome,
                    pnl_zar=float(pnl_zar),
                )

                append_cooldown(
                    cooldown_path,
                    {
                        "stopped_at": server_time.isoformat(),
                        "slice_id": str(position["slice_id"]),
                        "pair": str(position["pair"]),
                        "signal_id": str(position["signal_id"]),
                        "pnl_zar": f"{pnl_zar:.4f}",
                        "reason": "stale_data",
                    },
                )
                continue

            position["missing_bars"] = str(missing)
            if horizon_bars > 0:
                position["horizon_bars"] = str(horizon_bars)
            position["regime"] = position_regime
            surviving.append(position)
            continue

        last = frame.iloc[-1]
        close = Decimal(str(last["close"]))
        high = Decimal(str(last["high"]))
        low = Decimal(str(last["low"]))
        bars_held = _coerce_int(position.get("bars_held"), 0) + 1

        # For legacy (no horizon), we keep the original target/time-stop logic.
        target = (
            entry + (entry - stop) * TARGET_R_MULTIPLE
            if side == "BUY"
            else entry - (stop - entry) * TARGET_R_MULTIPLE
        )

        exit_price = None
        exit_reason = None
        outcome = None  # legacy directional label

        # --- Exit checks using the stop that was in force during this bar ---
        if side == "BUY":
            if low <= stop:
                exit_price = stop
                outcome = "win" if stop >= entry else "loss"
                initial_stop = Decimal(str(position.get("initial_stop_price") or stop))
                exit_reason = "trail_stop" if stop != initial_stop else "stop"
            elif horizon_bars == 0 and high >= target:
                exit_price, exit_reason, outcome = target, "target", "win"
        else:
            if high >= stop:
                exit_price = stop
                outcome = "win" if stop <= entry else "loss"
                initial_stop = Decimal(str(position.get("initial_stop_price") or stop))
                exit_reason = "trail_stop" if stop != initial_stop else "stop"
            elif horizon_bars == 0 and low <= target:
                exit_price, exit_reason, outcome = target, "target", "win"

        # Horizon close exit (only when position has a horizon)
        if exit_price is None and horizon_bars > 0 and bars_held >= horizon_bars:
            exit_price = close
            exit_reason = "horizon"
            outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"

        # Time-stop (legacy only; option to ignore once trailing is active).
        trail_active = _coerce_bool(position.get("trail_active"))
        if (
            exit_price is None
            and horizon_bars == 0
            and bars_held >= TIME_STOP_BARS
            and not (TRAIL_ENABLE and TRAIL_IGNORE_TIME_STOP and trail_active)
        ):
            exit_price = close
            exit_reason = "time_stop"
            outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"

        if exit_price is None:
            # --- Trailing update happens ONLY after the bar closes (no intrabar lookahead). ---
            # Trailing is legacy-only; horizon execution intentionally avoids it.
            if TRAIL_ENABLE and horizon_bars == 0:
                initial_stop_price = Decimal(
                    str(position.get("initial_stop_price") or position["stop_price"])
                )
                r = abs(entry - initial_stop_price)
                if r > 0:
                    peak_price = Decimal(str(position.get("peak_price") or entry))
                    trough_price = Decimal(str(position.get("trough_price") or entry))
                    peak_price = max(peak_price, high)
                    trough_price = min(trough_price, low)

                    if not trail_active:
                        if side == "BUY":
                            trail_active = peak_price >= (entry + TRAIL_ACTIVATE_R * r)
                        else:
                            trail_active = trough_price <= (entry - TRAIL_ACTIVATE_R * r)

                    if trail_active:
                        if side == "BUY":
                            candidate_stop = peak_price - TRAIL_DISTANCE_R * r
                            stop = max(stop, candidate_stop)
                        else:
                            candidate_stop = trough_price + TRAIL_DISTANCE_R * r
                            stop = min(stop, candidate_stop)

                        position["stop_price"] = str(stop)

                    position["initial_stop_price"] = str(initial_stop_price)
                    position["peak_price"] = str(peak_price)
                    position["trough_price"] = str(trough_price)
                    position["trail_active"] = "1" if trail_active else "0"

            position["bars_held"] = str(bars_held)
            position["missing_bars"] = "0"
            if horizon_bars > 0:
                position["horizon_bars"] = str(horizon_bars)
            position["regime"] = position_regime
            surviving.append(position)
            continue

        # Compute realized pnl (after fees)
        fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
        direction = Decimal(1) if side == "BUY" else Decimal(-1)
        gross = (exit_price - entry) / entry * direction * notional_zar
        fees = notional_zar * fee_bps / Decimal(10000)
        pnl_zar = gross - fees

        pnl_outcome = "win" if pnl_zar > 0 else "loss"

        closed_rows.append(
            {
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
                "pnl_outcome": pnl_outcome,
                "bars_held": str(bars_held),
                "exit_reason": exit_reason,
                "entry_guard": str(position.get("entry_guard") or ""),
                "regime": position_regime,
            }
        )

        apply_signal_feedback(
            book_path,
            str(position["slice_id"]),
            bar_epoch=int(last["start"].timestamp()),
            outcome=pnl_outcome,
            pnl_zar=float(pnl_zar),
        )

        if pnl_outcome == "loss":
            append_cooldown(
                cooldown_path,
                {
                    "stopped_at": server_time.isoformat(),
                    "slice_id": str(position["slice_id"]),
                    "pair": str(position["pair"]),
                    "signal_id": str(position["signal_id"]),
                    "pnl_zar": f"{pnl_zar:.4f}",
                    "reason": exit_reason,
                },
            )

    for row in closed_rows:
        append_log(log_path, row)

    # 2) Open new positions from signals
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
            append_log(
                log_path,
                {
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
                    "pnl_outcome": "",
                    "bars_held": "0",
                    "exit_reason": "not_book",
                    "entry_guard": "not_book",
                    "regime": str(getattr(signal, "regime", "") or ""),
                },
            )
            skipped += 1
            continue

        # Regime gating: use evidence-aware hostile_unproven flag when available.
        hostile_unproven = bool(getattr(signal, "hostile_unproven", True))
        if regime_blocks(signal.side, signal.regime, hostile_unproven):
            append_log(
                log_path,
                {
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
                    "pnl_outcome": "",
                    "bars_held": "0",
                    "exit_reason": "regime",
                    "entry_guard": f"regime_blocked(hostile_unproven={hostile_unproven})",
                    "regime": str(getattr(signal, "regime", "") or ""),
                },
            )
            skipped += 1
            continue

        frame = frames.get(signal.pair.upper())
        guard, reference = _entry_guard(signal, frame, signal.atr)

        if guard == "adverse_blocked":
            append_log(
                log_path,
                {
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
                    "pnl_outcome": "",
                    "bars_held": "0",
                    "exit_reason": "adverse",
                    "entry_guard": "adverse_blocked",
                    "regime": str(getattr(signal, "regime", "") or ""),
                },
            )
            skipped += 1
            continue

        notional_zar = _paper_size(signal, policy, usdc_zar)
        if notional_zar <= 0:
            continue

        # Stop at entry uses the original risk distance from the signal.
        risk_distance = (
            (signal.entry_price - signal.stop_price)
            if signal.side.value == "BUY"
            else (signal.stop_price - signal.entry_price)
        )
        initial_stop_price = (
            reference - risk_distance
            if signal.side.value == "BUY"
            else reference + risk_distance
        )

        # Horizon selection: prefer signal.horizon_bars if it exists, else fall back to book.
        signal_horizon = _coerce_int(getattr(signal, "horizon_bars", 0), 0)
        if signal_horizon <= 0:
            signal_horizon = book_horizon_map.get(signal.slice_id, 0)

        surviving.append(
            {
                "signal_id": signal.signal_id,
                "pair": signal.pair,
                "kind": signal.kind,
                "slice_id": signal.slice_id,
                "side": signal.side.value,
                "entry_price": str(reference),
                "stop_price": str(initial_stop_price),
                "initial_stop_price": str(initial_stop_price),
                "peak_price": str(reference),
                "trough_price": str(reference),
                "trail_active": "0",
                "notional_zar": str(notional_zar),
                "bars_held": "0",
                "missing_bars": "0",
                "entry_guard": guard,
                "horizon_bars": str(int(signal_horizon or 0)),
                "regime": str(getattr(signal, "regime", "") or ""),
            }
        )
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
