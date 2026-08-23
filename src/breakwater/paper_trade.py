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
If a position carries `horizon_bars` (>0), a thesis that never reached +1R
exits at the bar close once that many bars have elapsed (stop still wins
intrabar). A trade that has already made +1R (R-gate) is NOT horizon-cut:
the 2R target may fire, and the existing trail ratchets the stop. Horizon
is a loser timer, not a winner cap. Disable with BREAKWATER_PAPER_R_GATE=0.

Migration (IMPORTANT):
Legacy open positions may predate `horizon_bars`/`regime` persistence. Each
cycle we load slice -> horizon from the monitored book (book_path) and
backfill any positions with missing/zero horizon, and any missing regime.

Evidence quality fixes:
- Cooldown feedback is STOP-OUT only: only stop/trail_stop/stale_data passes stopout=True.
- Diversified sampling: prefer under-sampled slices and cap open positions per slice.
- Truth metric: we preserve `outcome` (directional) and log `pnl_outcome` (after fees).
  Lifecycle feedback is based on pnl_outcome.
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
from breakwater.research_lifecycle import (
    apply_signal_feedback,
    read_book,
    reconcile_paper_stats_from_log,
)


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
    "outcome",        # directional label (legacy)
    "bars_held",
    "exit_reason",
    "entry_guard",
    "regime",
    "pnl_outcome",    # NEW: after-fee truth label (appended to avoid misalignment)
    # Stop tightness diagnostics (entry-time, stable even if trailing later changes stop_price).
    "atr",
    "stop_atr_mult",
    "risk_fraction",
]

TARGET_R_MULTIPLE = Decimal("2")
TIME_STOP_BARS = int(os.getenv("BREAKWATER_PAPER_TIME_STOP_BARS", "48"))
MISSING_BARS_EXIT = 24

SPOT_FEE_BPS = Decimal("20")
PERP_FEE_BPS = Decimal("26")
MAX_PAPER_POSITIONS = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS", "6"))
MAX_PAPER_POSITIONS_PER_KIND = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_KIND", "3"))
MAX_PAPER_POSITIONS_PER_SLICE = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_SLICE", "1"))
OLD_PAPER_SEATS = max(0, int(os.getenv("BREAKWATER_PAPER_OLD_SEATS", "5")))
FAT_PAPER_SEATS = max(0, int(os.getenv("BREAKWATER_PAPER_FAT_SEATS", "10")))

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


# Trailing feature flags (OFF by default unless R-gate has already activated).
TRAIL_ENABLE = _env_bool("BREAKWATER_TRAIL_ENABLE", "0")
TRAIL_ACTIVATE_R = _env_decimal("BREAKWATER_TRAIL_ACTIVATE_R", "1.0")
TRAIL_DISTANCE_R = _env_decimal("BREAKWATER_TRAIL_DISTANCE_R", "1.0")
TRAIL_IGNORE_TIME_STOP = _env_bool("BREAKWATER_TRAIL_IGNORE_TIME_STOP", "0")

# Let winners win: horizon is a loser timer. Default ON.
R_GATE_ENABLE = _env_bool("BREAKWATER_PAPER_R_GATE", "1")
R_GATE_SUPPRESS_R = _env_decimal("BREAKWATER_PAPER_R_GATE_R", "1.0")


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


def _paper_size(
    signal: SliceSignal,
    policy,
    usdc_zar: Decimal,
    *,
    risk_zar: Decimal | None = None,
) -> Decimal:
    risk_fraction = abs(signal.entry_price - signal.stop_price) / signal.entry_price
    if risk_fraction <= 0:
        return Decimal(0)
    budget = policy.risk_per_trade_zar if risk_zar is None else risk_zar
    if budget <= 0:
        budget = policy.risk_per_trade_zar
    notional_zar = min(budget / risk_fraction, policy.max_position_notional_zar)
    if signal.kind == "PERP" and usdc_zar > 0 and notional_zar / usdc_zar < Decimal("11"):
        return Decimal(0)
    return notional_zar


def _realised_paper_pnl(log_path: Path) -> Decimal:
    if not log_path.exists():
        return Decimal(0)
    total = Decimal(0)
    try:
        with log_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if str(row.get("outcome") or "") not in {"win", "loss"}:
                    continue
                if str(row.get("exit_reason") or "") in {
                    "regime", "not_book", "no_price", "adverse", "risk_cap", "edge_cap",
                }:
                    continue
                try:
                    total += Decimal(str(row.get("pnl_zar") or 0))
                except (InvalidOperation, ValueError):
                    continue
    except OSError:
        return Decimal(0)
    return total


def _latest_close(frame):
    if frame is None or frame.empty:
        return None
    return Decimal(str(frame.iloc[-1]["close"]))


def _paper_entry_mode() -> str:
    """Entry mode for paper trading.

    aligned (default): enter at the signal close (matches validation semantics).
    premium: apply the legacy winner-capture premium to the reference entry.
    """
    mode = str(os.getenv("BREAKWATER_PAPER_ENTRY_MODE", "aligned")).strip().lower()
    return mode if mode in {"aligned", "premium"} else "aligned"


def _entry_guard(signal: SliceSignal, frame, atr: Decimal) -> tuple[str, Decimal]:
    """Return (guard_verdict, reference_entry_price)."""
    reference = signal.entry_price
    mode = _paper_entry_mode()

    if mode == "premium":
        # Winner-capture premium: conservative reference entry that requires follow-through.
        # (Opt-in now: default paper mode is aligned with validation semantics.)
        premium_frac = min(
            PREMIUM_ATR_MULT * atr / reference,
            PREMIUM_CAP_BPS / Decimal(10000),
        )
        if signal.side.value == "BUY":
            reference = signal.entry_price * (Decimal(1) + premium_frac)
        else:
            reference = signal.entry_price * (Decimal(1) - premium_frac)

    latest = _latest_close(frame)
    if latest is None:
        return "no_price", reference

    adverse_frac = min(
        ADVERSE_ATR_MULT * atr / signal.entry_price,
        ADVERSE_CAP_BPS / Decimal(10000),
    )
    if signal.side.value == "BUY" and latest < signal.entry_price * (Decimal(1) - adverse_frac):
        return "adverse_blocked", reference
    if signal.side.value == "SELL" and latest > signal.entry_price * (Decimal(1) + adverse_frac):
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


def _slice_trade_counts(book_path: Path) -> dict[str, int]:
    """slice_id -> paper_trades from the book (best-effort)."""
    try:
        rows = read_book(book_path)
    except Exception:
        return {}
    counts: dict[str, int] = {}
    for row in rows:
        sid = str(row.get("slice_id") or "")
        if not sid:
            continue
        counts[sid] = _coerce_int(row.get("paper_trades"), 0)
    return counts


def _slice_means(book_path: Path) -> dict[str, float]:
    try:
        rows = read_book(book_path)
    except Exception:
        return {}
    out: dict[str, float] = {}
    for row in rows:
        sid = str(row.get("slice_id") or "")
        if not sid:
            continue
        try:
            out[sid] = float(row.get("mean_ret_costadj") or 0.0)
        except (TypeError, ValueError):
            out[sid] = 0.0
    return out


def _incumbent_slice_ids(book_path: Path) -> set[str]:
    """Slices that have earned a reserved paper seat.

    Concentrated hunt rows, or any row with realised paper profit.
    Untested promotions do not qualify.
    """
    try:
        rows = read_book(book_path)
    except Exception:
        return set()
    out: set[str] = set()
    for row in rows:
        sid = str(row.get("slice_id") or "")
        if not sid:
            continue
        source = str(row.get("source") or "")
        trades = _coerce_int(row.get("paper_trades"), 0)
        try:
            pnl = float(row.get("paper_pnl_zar") or 0.0)
        except (TypeError, ValueError):
            pnl = 0.0
        if source == "validated_concentrated" or (trades >= 1 and pnl > 0.0):
            out.add(sid)
    return out


def _slice_family(slice_id: str) -> str:
    text = str(slice_id)
    base, sep, rest = text.rpartition(":h")
    if sep and rest.isdigit():
        return base
    return text


def _is_rotated_sibling(slice_id: str, book_ids: set[str]) -> bool:
    if slice_id in book_ids:
        return False
    family = _slice_family(slice_id)
    if family == slice_id:
        return False
    return any(_slice_family(other) == family for other in book_ids)


def _slice_paper_pnl(book_path: Path) -> dict[str, float]:
    try:
        rows = read_book(book_path)
    except Exception:
        return {}
    out: dict[str, float] = {}
    for row in rows:
        sid = str(row.get("slice_id") or "")
        if not sid:
            continue
        try:
            out[sid] = float(row.get("paper_pnl_zar") or 0.0)
        except (TypeError, ValueError):
            out[sid] = 0.0
    return out


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
    reconcile_paper_stats_from_log(book_path, log_path)
    open_positions = read_positions(positions_path)
    # Migration: upgrade legacy positions so horizon exits engage.
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
                outcome = "loss"
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
                        "outcome": outcome,
                        "bars_held": str(position.get("bars_held") or 0),
                        "exit_reason": "stale_data",
                        "entry_guard": str(position.get("entry_guard") or ""),
                        "regime": position_regime,
                        "pnl_outcome": pnl_outcome,
                        "atr": str(position.get("atr") or ""),
                        "stop_atr_mult": str(position.get("stop_atr_mult") or ""),
                        "risk_fraction": str(position.get("risk_fraction") or ""),
                    }
                )
                apply_signal_feedback(
                    book_path,
                    str(position["slice_id"]),
                    bar_epoch=int(server_time.timestamp()),
                    outcome=pnl_outcome,
                    pnl_zar=float(pnl_zar),
                    stopout=True,
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
        initial_stop_price = Decimal(str(position.get("initial_stop_price") or stop))
        r_dist = abs(entry - initial_stop_price)
        peak_seen = max(Decimal(str(position.get("peak_price") or entry)), high)
        trough_seen = min(Decimal(str(position.get("trough_price") or entry)), low)
        mfe_r = Decimal(0)
        if r_dist > 0:
            mfe_r = ((peak_seen - entry) / r_dist) if side == "BUY" else ((entry - trough_seen) / r_dist)
        r_gate_on = bool(R_GATE_ENABLE and r_dist > 0 and mfe_r >= R_GATE_SUPPRESS_R)
        target = (
            entry + (entry - initial_stop_price) * TARGET_R_MULTIPLE
            if side == "BUY"
            else entry - (initial_stop_price - entry) * TARGET_R_MULTIPLE
        )

        exit_price = None
        exit_reason = None
        outcome = None
        allow_target = (horizon_bars == 0) or R_GATE_ENABLE
        if side == "BUY":
            if low <= stop:
                exit_price = stop
                outcome = "win" if stop >= entry else "loss"
                exit_reason = "trail_stop" if stop != initial_stop_price else "stop"
            elif allow_target and high >= target:
                exit_price, exit_reason, outcome = target, "target", "win"
        else:
            if high >= stop:
                exit_price = stop
                outcome = "win" if stop <= entry else "loss"
                exit_reason = "trail_stop" if stop != initial_stop_price else "stop"
            elif allow_target and low <= target:
                exit_price, exit_reason, outcome = target, "target", "win"
        if (
            exit_price is None
            and _is_rotated_sibling(str(position.get("slice_id") or ""), book_slice_ids)
            and not r_gate_on
        ):
            # Research replaced this horizon; don't hold the leftover sibling.
            exit_price = close
            exit_reason = "rotated"
            outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
        if (
            exit_price is None
            and horizon_bars > 0
            and bars_held >= horizon_bars
            and not r_gate_on
        ):
            exit_price = close
            exit_reason = "horizon"
            outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
        trail_active = _coerce_bool(position.get("trail_active"))
        if (
            exit_price is None
            and horizon_bars == 0
            and bars_held >= TIME_STOP_BARS
            and not (TRAIL_ENABLE and TRAIL_IGNORE_TIME_STOP and trail_active)
            and not r_gate_on
        ):
            exit_price = close
            exit_reason = "time_stop"
            outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
        if exit_price is None:
            trail_allowed = (TRAIL_ENABLE and horizon_bars == 0) or r_gate_on
            if trail_allowed:
                r = r_dist
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

        fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
        direction = Decimal(1) if side == "BUY" else Decimal(-1)
        gross = (exit_price - entry) / entry * direction * notional_zar
        fees = notional_zar * fee_bps / Decimal(10000)
        pnl_zar = gross - fees

        pnl_outcome = "win" if pnl_zar > 0 else "loss"
        stopout = exit_reason in {"stop", "trail_stop", "stale_data"}
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
                "bars_held": str(bars_held),
                "exit_reason": exit_reason,
                "entry_guard": str(position.get("entry_guard") or ""),
                "regime": position_regime,
                "pnl_outcome": pnl_outcome,
                "atr": str(position.get("atr") or ""),
                "stop_atr_mult": str(position.get("stop_atr_mult") or ""),
                "risk_fraction": str(position.get("risk_fraction") or ""),
            }
        )
        apply_signal_feedback(
            book_path,
            str(position["slice_id"]),
            bar_epoch=int(last["start"].timestamp()),
            outcome=pnl_outcome,
            pnl_zar=float(pnl_zar),
            stopout=stopout,
        )
        if pnl_outcome == "loss" and stopout:
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

    # 2) Open new positions from signals (diversified)
    skipped = 0
    slot_full = 0
    slice_full = 0
    pair_held = 0

    open_pairs = {str(position["pair"]).upper() for position in surviving}
    open_slice_counts: dict[str, int] = {}
    for position in surviving:
        sid = str(position.get("slice_id") or "")
        if sid:
            open_slice_counts[sid] = open_slice_counts.get(sid, 0) + 1

    trade_counts = _slice_trade_counts(book_path)
    paper_pnls = _slice_paper_pnl(book_path)
    incumbents = _incumbent_slice_ids(book_path)
    means = _slice_means(book_path)
    size_from_equity = _env_bool("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "0")
    risk_zar: Decimal | None = None
    if size_from_equity:
        seed = _env_decimal(
            "BREAKWATER_PAPER_EQUITY_SEED",
            str(_env_decimal("BREAKWATER_INITIAL_EQUITY_ZAR", "2000")),
        )
        equity = seed + _realised_paper_pnl(log_path)
        if equity < 0:
            equity = Decimal(0)
        risk_pct = _env_decimal("BREAKWATER_PAPER_RISK_OF_EQUITY", "0.01")
        risk_zar = equity * risk_pct

    selection_mode = str(os.getenv("BREAKWATER_PAPER_SELECTION_MODE", "explore")).strip().lower()
    if selection_mode == "profit":
        def _base_key(sig):
            return (-abs(sig.edge), trade_counts.get(sig.slice_id, 0), sig.pair)
    else:
        def _base_key(sig):
            return (trade_counts.get(sig.slice_id, 0), -abs(sig.edge), sig.pair)

    # Fat first (new high-mean book rows with no paper yet), then old/green
    # incumbents (concentrated or already printing). MAX / PER_SLICE unchanged.
    fat_sigs = sorted(
        [sig for sig in signals if sig.slice_id not in incumbents],
        key=lambda sig: (-means.get(sig.slice_id, 0.0),) + tuple(_base_key(sig)),
    )
    old_sigs = sorted(
        [sig for sig in signals if sig.slice_id in incumbents],
        key=lambda sig: (-paper_pnls.get(sig.slice_id, 0.0),) + tuple(_base_key(sig)),
    )
    candidates = fat_sigs + old_sigs

    for signal in candidates:
        if len(surviving) >= MAX_PAPER_POSITIONS:
            slot_full += 1
            continue

        kind_open = sum(1 for position in surviving if position.get("kind") == signal.kind)
        if kind_open >= MAX_PAPER_POSITIONS_PER_KIND:
            slot_full += 1
            continue
        old_open = sum(
            1
            for position in surviving
            if str(position.get("slice_id") or "") in incumbents
        )
        fat_open = len(surviving) - old_open
        if signal.slice_id in incumbents:
            if OLD_PAPER_SEATS and old_open >= OLD_PAPER_SEATS:
                slot_full += 1
                continue
        elif FAT_PAPER_SEATS and fat_open >= FAT_PAPER_SEATS:
            slot_full += 1
            continue
        if open_slice_counts.get(signal.slice_id, 0) >= MAX_PAPER_POSITIONS_PER_SLICE:
            slice_full += 1
            continue
        if trade_counts.get(signal.slice_id, 0) >= 3 and paper_pnls.get(signal.slice_id, 0.0) < 0:
            skipped += 1
            continue

        if signal.pair.upper() in open_pairs:
            pair_held += 1
            continue

        if _is_rotated_sibling(signal.slice_id, book_slice_ids):
            skipped += 1
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
                    "bars_held": "0",
                    "exit_reason": "not_book",
                    "entry_guard": "not_book",
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(getattr(signal, "atr", "") or ""),
                    "stop_atr_mult": str(getattr(signal, "stop_atr_mult", "") or ""),
                    "risk_fraction": "",
                },
            )
            skipped += 1
            continue

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
                    "bars_held": "0",
                    "exit_reason": "regime",
                    "entry_guard": f"regime_blocked(hostile_unproven={hostile_unproven})",
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(getattr(signal, "atr", "") or ""),
                    "stop_atr_mult": str(getattr(signal, "stop_atr_mult", "") or ""),
                    "risk_fraction": "",
                },
            )
            skipped += 1
            continue

        frame = frames.get(signal.pair.upper())
        guard, reference = _entry_guard(signal, frame, signal.atr)

        if guard == "no_price":
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
                    "bars_held": "0",
                    "exit_reason": "no_price",
                    "entry_guard": "no_price",
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(getattr(signal, "atr", "") or ""),
                    "stop_atr_mult": str(getattr(signal, "stop_atr_mult", "") or ""),
                    "risk_fraction": "",
                },
            )
            skipped += 1
            continue

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
                    "bars_held": "0",
                    "exit_reason": "adverse",
                    "entry_guard": "adverse_blocked",
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(getattr(signal, "atr", "") or ""),
                    "stop_atr_mult": str(getattr(signal, "stop_atr_mult", "") or ""),
                    "risk_fraction": "",
                },
            )
            skipped += 1
            continue

        notional_zar = _paper_size(signal, policy, usdc_zar, risk_zar=risk_zar)
        if notional_zar <= 0:
            continue

        risk_distance = (
            (signal.entry_price - signal.stop_price)
            if signal.side.value == "BUY"
            else (signal.stop_price - signal.entry_price)
        )
        initial_stop_price = (
            reference - risk_distance if signal.side.value == "BUY" else reference + risk_distance
        )
        # Stop tightness diagnostics (entry-time).
        initial_risk_distance = abs(reference - initial_stop_price)
        risk_fraction = (initial_risk_distance / reference) if reference > 0 else Decimal(0)
        stop_atr_mult = (initial_risk_distance / signal.atr) if signal.atr > 0 else Decimal(0)
        risk_cap = _env_decimal("BREAKWATER_PAPER_MAX_RISK_FRACTION", "0.03")
        mean = Decimal(str(means.get(signal.slice_id, 0.0) or 0.0))
        k_mean = _env_decimal("BREAKWATER_PAPER_RISK_TO_MEAN_K", "8")
        edge_cap_hit = mean > 0 and k_mean > 0 and risk_fraction > k_mean * mean
        hard_cap_hit = risk_cap > 0 and risk_fraction > risk_cap
        if edge_cap_hit or hard_cap_hit:
            reason = "edge_cap" if edge_cap_hit and not hard_cap_hit else "risk_cap"
            append_log(
                log_path,
                {
                    "closed_at": server_time.isoformat(),
                    "signal_id": signal.signal_id,
                    "pair": signal.pair,
                    "kind": signal.kind,
                    "slice_id": signal.slice_id,
                    "side": signal.side.value,
                    "entry_price": str(reference),
                    "exit_price": "",
                    "stop_price": str(initial_stop_price),
                    "notional_zar": "0",
                    "pnl_zar": "0",
                    "outcome": "skipped",
                    "bars_held": "0",
                    "exit_reason": reason,
                    "entry_guard": reason,
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(signal.atr),
                    "stop_atr_mult": f"{stop_atr_mult:.6f}" if signal.atr > 0 else "",
                    "risk_fraction": f"{risk_fraction:.8f}",
                },
            )
            skipped += 1
            continue

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
                "atr": str(signal.atr),
                "stop_atr_mult": (f"{stop_atr_mult:.6f}" if signal.atr > 0 else ""),
                "risk_fraction": (f"{risk_fraction:.8f}" if reference > 0 else ""),
            }
        )
        open_pairs.add(signal.pair.upper())
        open_slice_counts[signal.slice_id] = open_slice_counts.get(signal.slice_id, 0) + 1

    write_positions(positions_path, surviving)
    return {
        "closed": len(closed_rows),
        "open": len(surviving),
        "new_signals": len(signals),
        "skipped": skipped,
        "slot_full": slot_full,
        "slice_full": slice_full,
        "pair_held": pair_held,
    }
