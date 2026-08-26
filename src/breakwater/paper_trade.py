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
import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from breakwater.hip3 import hip3_in_market_session, hip3_slice_market_class
from breakwater.monitor import SliceSignal, regime_blocks, regime_of
from breakwater.paper_counterfactual import (
    advance_counterfactuals,
    append_counterfactual_rows,
    attach_actual_closures,
    counterfactual_summary,
    read_counterfactual_trackers,
    sync_open_positions,
    write_counterfactual_trackers,
)
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
    # Prospective excursion/R diagnostics (legacy rows migrate with blanks).
    "initial_stop_price",
    "peak_price",
    "trough_price",
    "mfe_r",
    "mae_r",
    "gross_r",
    "fee_zar",
    "net_r",
    "excursion_ordering",
    "exit_bar_start",
]

TARGET_R_MULTIPLE = Decimal("2")
TIME_STOP_BARS = int(os.getenv("BREAKWATER_PAPER_TIME_STOP_BARS", "48"))
MISSING_BARS_EXIT = 24

MAX_PAPER_POSITIONS = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS", "6"))
MAX_PAPER_POSITIONS_PER_KIND = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_KIND", "3"))
MAX_PAPER_POSITIONS_PER_SLICE = int(os.getenv("BREAKWATER_PAPER_MAX_POSITIONS_PER_SLICE", "1"))
# The HIP-3 sub-pool (default 6 seats) gets a tighter per-slice cap so one
# edge cannot occupy half the pool: five correlated positions on one slice
# is one bet in six costumes. 0 disables new HIP-3 entries (kill switch).
HIP3_MAX_POSITIONS_PER_SLICE = int(os.getenv("BREAKWATER_HIP3_MAX_POSITIONS_PER_SLICE", "3"))
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


# Round-trip execution cost in bps (entry + exit), charged once per closed
# trade. Fact-based venue schedules (base tier, taker on both sides):
#   VALR spot fiat-quoted (BTCZAR ...): tier 1 taker 0.350% per side, per
#     VALR's published "Spot Fiat Quote" fee table (0.180%/0.350% at
#     zero 30-day volume) -> 70 bps round trip. A paper account has no
#     live volume, so tier 1 is the honest default. Verify the account
#     tier with scripts/fee_audit.py and override if it ever upgrades.
#   Hyperliquid perp (native + HIP-3 builder perps): base tier taker
#     0.045% per side -> 9 bps round trip.
SPOT_FEE_BPS = _env_decimal("BREAKWATER_SPOT_FEE_BPS", "70")
PERP_FEE_BPS = _env_decimal("BREAKWATER_PERP_FEE_BPS", "9")


# Trailing feature flags (OFF by default unless R-gate has already activated).
TRAIL_ENABLE = _env_bool("BREAKWATER_TRAIL_ENABLE", "0")
TRAIL_ACTIVATE_R = _env_decimal("BREAKWATER_TRAIL_ACTIVATE_R", "1.0")
TRAIL_DISTANCE_R = _env_decimal("BREAKWATER_TRAIL_DISTANCE_R", "1.0")
TRAIL_IGNORE_TIME_STOP = _env_bool("BREAKWATER_TRAIL_IGNORE_TIME_STOP", "0")

# Let winners win: horizon is a loser timer. Default ON.
R_GATE_ENABLE = _env_bool("BREAKWATER_PAPER_R_GATE", "1")
R_GATE_SUPPRESS_R = _env_decimal("BREAKWATER_PAPER_R_GATE_R", "1.0")


def _read_positions_with_error(path: Path) -> tuple[list, str | None]:
    if not path.exists():
        return [], None
    try:
        payload = json.loads(path.read_text())
    except OSError:
        return [], "unreadable"
    except json.JSONDecodeError:
        return [], "invalid_json"
    if not isinstance(payload, list):
        return [], "unsupported_schema"
    return payload, None


def read_positions(path: Path) -> list[dict]:
    positions, _ = _read_positions_with_error(path)
    return positions


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


@contextmanager
def _paper_cycle_lock(positions_path: Path):
    """Serialize paper position read/modify/write cycles on this host."""
    positions_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(f"{positions_path}.lock")
    with lock_path.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _serialized_paper_cycle(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        positions_path = kwargs.get("positions_path")
        if positions_path is None:
            raise TypeError("run_paper_cycle requires positions_path")
        with _paper_cycle_lock(Path(positions_path)):
            return function(*args, **kwargs)

    return wrapper


def _position_validation_error(position) -> str | None:
    if not isinstance(position, dict):
        return "not_an_object"
    for key in ("signal_id", "pair", "kind", "slice_id", "side"):
        if not str(position.get(key) or "").strip():
            return f"missing_{key}"
    if str(position["kind"]).upper() not in {"SPOT", "PERP"}:
        return "invalid_kind"
    if str(position["side"]).upper() not in {"BUY", "SELL"}:
        return "invalid_side"

    numeric_fields = ["entry_price", "stop_price", "notional_zar"]
    numeric_fields.extend(
        key
        for key in ("initial_stop_price", "peak_price", "trough_price")
        if position.get(key) is not None and position.get(key) != ""
    )
    parsed: dict[str, Decimal] = {}
    for key in numeric_fields:
        try:
            value = Decimal(str(position[key]))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return f"invalid_{key}"
        if not value.is_finite():
            return f"invalid_{key}"
        parsed[key] = value
    if parsed["entry_price"] <= 0:
        return "nonpositive_entry_price"
    if parsed["stop_price"] <= 0:
        return "nonpositive_stop_price"
    if parsed["notional_zar"] < 0:
        return "negative_notional_zar"
    last_processed = str(position.get("last_processed_bar_start") or "").strip()
    if last_processed:
        try:
            datetime.fromisoformat(last_processed.replace("Z", "+00:00"))
        except ValueError:
            return "invalid_last_processed_bar_start"
    return None


def _quarantine_positions(path: Path, invalid: list[tuple[object, str]], now: datetime) -> None:
    if not invalid:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if path.exists():
        try:
            payload = json.loads(path.read_text())
            if isinstance(payload, list):
                records = payload
        except (OSError, json.JSONDecodeError):
            records = []
    records.extend(
        {
            "quarantined_at": now.isoformat(),
            "reason": reason,
            "position": position,
        }
        for position, reason in invalid
    )
    write_positions(path, records[-100:])


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
    notional_cap_zar: Decimal | None = None,
) -> Decimal:
    risk_fraction = abs(signal.entry_price - signal.stop_price) / signal.entry_price
    if risk_fraction <= 0:
        return Decimal(0)
    budget = policy.risk_per_trade_zar if risk_zar is None else risk_zar
    if budget <= 0:
        budget = policy.risk_per_trade_zar
    # Flat mode is bounded by the mandate's absolute notional cap; equity
    # mode passes a cap that scales with equity so the position compounds.
    cap = notional_cap_zar if notional_cap_zar is not None else policy.max_position_notional_zar
    notional_zar = min(budget / risk_fraction, cap)
    # Hyperliquid's native minimum order value is 10 USDC.
    if signal.kind == "PERP" and usdc_zar > 0 and notional_zar / usdc_zar < Decimal("10"):
        return Decimal(0)
    return notional_zar


def _trade_excursion_diagnostics(
    *,
    side: str,
    entry: Decimal,
    initial_stop: Decimal,
    peak: Decimal,
    trough: Decimal,
    exit_price: Decimal,
    notional_zar: Decimal,
    fee_zar: Decimal,
    pnl_zar: Decimal,
) -> dict:
    risk_distance = abs(entry - initial_stop)
    risk_zar = (
        notional_zar * risk_distance / entry
        if entry > 0 and risk_distance > 0
        else Decimal(0)
    )
    if risk_distance > 0:
        mfe_r = (
            (peak - entry) / risk_distance
            if side == "BUY"
            else (entry - trough) / risk_distance
        )
        mae_r = (
            (entry - trough) / risk_distance
            if side == "BUY"
            else (peak - entry) / risk_distance
        )
        gross_r = (
            (exit_price - entry) / risk_distance
            if side == "BUY"
            else (entry - exit_price) / risk_distance
        )
    else:
        mfe_r = mae_r = gross_r = Decimal(0)
    net_r = pnl_zar / risk_zar if risk_zar > 0 else Decimal(0)
    return {
        "initial_stop_price": str(initial_stop),
        "peak_price": str(peak),
        "trough_price": str(trough),
        "mfe_r": f"{mfe_r:.6f}",
        "mae_r": f"{mae_r:.6f}",
        "gross_r": f"{gross_r:.6f}",
        "fee_zar": f"{fee_zar:.4f}",
        "net_r": f"{net_r:.6f}",
        "excursion_ordering": "ohlc_upper_bound_stop_first_exit",
    }


def _active_stop_risk_zar(position: dict) -> Decimal | None:
    """Return the position's current downside at its active stop.

    The current (possibly trailed) stop is used rather than the initial stop.
    Once a stop has reached or crossed breakeven, the position contributes no
    downside risk.  ``None`` is deliberately fail-closed: a malformed legacy
    position must not allow another entry through the aggregate guard.
    """
    try:
        entry = Decimal(str(position["entry_price"]))
        stop = Decimal(str(position["stop_price"]))
        notional = Decimal(str(position["notional_zar"]))
    except (InvalidOperation, KeyError, TypeError, ValueError):
        return None
    if not entry.is_finite() or not stop.is_finite() or not notional.is_finite():
        return None
    if entry <= 0 or notional < 0:
        return None

    side = str(position.get("side") or "").upper()
    if side == "BUY":
        risk_fraction = max((entry - stop) / entry, Decimal(0))
    elif side == "SELL":
        risk_fraction = max((stop - entry) / entry, Decimal(0))
    else:
        return None
    return notional * risk_fraction


def _aggregate_stop_risk_zar(positions: list[dict]) -> tuple[Decimal, bool]:
    total = Decimal(0)
    unknown = False
    for position in positions:
        risk = _active_stop_risk_zar(position)
        if risk is None:
            unknown = True
        else:
            total += risk
    return total, unknown


def _risk_buffer_zar(position: dict) -> Decimal | None:
    try:
        notional = Decimal(str(position["notional_zar"]))
    except (InvalidOperation, KeyError, TypeError, ValueError):
        return None
    buffer_bps = _env_decimal("BREAKWATER_PAPER_AGGREGATE_RISK_BUFFER_BPS", "25")
    if not notional.is_finite() or not buffer_bps.is_finite() or buffer_bps < 0:
        return None
    return notional * buffer_bps / Decimal(10000)


def _aggregate_risk_buffer_zar(positions: list[dict]) -> tuple[Decimal, bool]:
    total = Decimal(0)
    for position in positions:
        buffer = _risk_buffer_zar(position)
        if buffer is None:
            return total, True
        total += buffer
    return total, False


def _cost_adjusted_risk_zar(positions: list[dict]) -> tuple[Decimal, bool]:
    total = Decimal(0)
    for position in positions:
        stop_risk = _active_stop_risk_zar(position)
        try:
            notional = Decimal(str(position["notional_zar"]))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return total, True
        if stop_risk is None or not notional.is_finite():
            return total, True
        fee_bps = PERP_FEE_BPS if str(position.get("kind")).upper() == "PERP" else SPOT_FEE_BPS
        total += stop_risk + notional * fee_bps / Decimal(10000)
    return total, False


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
                    "regime",
                    "not_book",
                    "no_price",
                    "adverse",
                    "risk_cap",
                    "edge_cap",
                    "below_perp_min_notional",
                }:
                    continue
                try:
                    total += Decimal(str(row.get("pnl_zar") or 0))
                except (InvalidOperation, ValueError):
                    continue
    except OSError:
        return Decimal(0)
    return total


def _entry_session_utc(row: dict) -> str:
    """UTC session of a closed trade's ENTRY bar (exit_bar_start - bars_held).

    Sessions mirror the paper gate's hours: asia 00-07, eu 07-13, us 13-21,
    late 21-24. Unreadable rows are "unknown", never an error.
    """
    try:
        bar_start = str(row.get("exit_bar_start") or "").strip()
        if not bar_start:
            return "unknown"
        ts = datetime.fromisoformat(bar_start.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        entry = ts.astimezone(timezone.utc) - timedelta(
            hours=int(str(row.get("bars_held") or 0))
        )
    except (ValueError, TypeError):
        return "unknown"
    hour = entry.hour
    if hour < 7:
        return "asia"
    if hour < 13:
        return "eu"
    if hour < 21:
        return "us"
    return "late"


def _paper_performance_summary(log_path: Path) -> dict:
    summary = {
        "closed": 0,
        "wins": 0,
        "pnl_zar": Decimal(0),
        "by_side": {},
        "by_exit": {},
        "by_session": {},
    }
    if not log_path.exists():
        return {
            "closed": 0,
            "wins": 0,
            "pnl_zar": "0.0000",
            "by_side": {},
            "by_exit": {},
            "by_session": {},
        }

    def update(mapping: dict, key: str, pnl: Decimal) -> None:
        bucket = mapping.setdefault(key or "unknown", {"trades": 0, "wins": 0, "pnl": Decimal(0)})
        bucket["trades"] += 1
        bucket["wins"] += int(pnl > 0)
        bucket["pnl"] += pnl

    try:
        with log_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if str(row.get("outcome") or "") not in {"win", "loss"}:
                    continue
                try:
                    pnl = Decimal(str(row.get("pnl_zar") or 0))
                except (InvalidOperation, ValueError):
                    continue
                summary["closed"] += 1
                summary["wins"] += int(pnl > 0)
                summary["pnl_zar"] += pnl
                update(summary["by_side"], str(row.get("side") or ""), pnl)
                update(summary["by_exit"], str(row.get("exit_reason") or ""), pnl)
                update(summary["by_session"], _entry_session_utc(row), pnl)
    except OSError:
        return {"closed": 0, "wins": 0, "pnl_zar": "0.0000", "by_side": {}, "by_exit": {}, "by_session": {}, "error": "unreadable"}

    def serialize(mapping: dict) -> dict:
        return {
            key: {
                "trades": value["trades"],
                "wins": value["wins"],
                "pnl_zar": f"{value['pnl']:.4f}",
            }
            for key, value in sorted(mapping.items())
        }

    return {
        "closed": summary["closed"],
        "wins": summary["wins"],
        "pnl_zar": f"{summary['pnl_zar']:.4f}",
        "by_side": serialize(summary["by_side"]),
        "by_exit": serialize(summary["by_exit"]),
        "by_session": serialize(summary["by_session"]),
    }


def _paper_equity_zar(log_path: Path) -> Decimal:
    seed = _env_decimal(
        "BREAKWATER_PAPER_EQUITY_SEED",
        str(_env_decimal("BREAKWATER_INITIAL_EQUITY_ZAR", "2000")),
    )
    return max(seed + _realised_paper_pnl(log_path), Decimal(0))


def _aggregate_risk_cap_zar(log_path: Path) -> Decimal | None:
    """Resolve the paper-only aggregate-risk ceiling.

    An explicit ZAR override takes precedence. Invalid explicit values fail
    closed (``None``) instead of silently falling back to a larger allowance.
    """
    override = os.getenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR")
    if override is not None and str(override).strip():
        try:
            cap = Decimal(str(override))
        except (InvalidOperation, TypeError, ValueError):
            return None
        return cap if cap.is_finite() and cap >= 0 else None

    fraction = _env_decimal("BREAKWATER_PAPER_MAX_AGGREGATE_RISK_OF_EQUITY", "0.05")
    if not fraction.is_finite() or fraction < 0:
        return None
    return _paper_equity_zar(log_path) * fraction


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


def _bkey_book(signal) -> str:
    """Which book a signal belongs to: HIP-3 slices are namespaced."""
    return "hip3" if str(getattr(signal, "slice_id") or "").startswith("hip3_") else "native"


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


def _bar_start_iso(value) -> str:
    timestamp = value.to_pydatetime() if hasattr(value, "to_pydatetime") else value
    if not isinstance(timestamp, datetime):
        timestamp = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    return timestamp.isoformat()


def _unseen_bars(position: dict, frame):
    """Return unseen bars in order; legacy positions process latest once."""
    if frame is None or frame.empty:
        return frame
    ordered = frame.sort_values("start").drop_duplicates("start")
    raw_last = str(position.get("last_processed_bar_start") or "").strip()
    if not raw_last:
        return ordered.tail(1)
    try:
        last_processed = datetime.fromisoformat(raw_last.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("paper position last_processed_bar_start is invalid") from exc
    starts = ordered["start"]
    if getattr(starts.dt, "tz", None) is not None and last_processed.tzinfo is None:
        from datetime import timezone

        last_processed = last_processed.replace(tzinfo=timezone.utc)
    return ordered[starts > last_processed]


def _mark_position_bar(position: dict, last, *, horizon_bars: int, book_slice_ids: set[str], now: datetime):
    side = str(position["side"])
    entry = Decimal(str(position["entry_price"]))
    stop = Decimal(str(position["stop_price"]))
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
        mfe_r = (
            (peak_seen - entry) / r_dist
            if side == "BUY"
            else (entry - trough_seen) / r_dist
        )
    r_gate_on = bool(R_GATE_ENABLE and r_dist > 0 and mfe_r >= R_GATE_SUPPRESS_R)
    target = (
        entry + (entry - initial_stop_price) * TARGET_R_MULTIPLE
        if side == "BUY"
        else entry - (initial_stop_price - entry) * TARGET_R_MULTIPLE
    )
    exit_price = exit_reason = outcome = None
    allow_target = horizon_bars == 0 or R_GATE_ENABLE
    if side == "BUY":
        if low <= stop:
            exit_price, outcome = stop, ("win" if stop >= entry else "loss")
            exit_reason = "trail_stop" if stop != initial_stop_price else "stop"
        elif allow_target and high >= target:
            exit_price, exit_reason, outcome = target, "target", "win"
    else:
        if high >= stop:
            exit_price, outcome = stop, ("win" if stop <= entry else "loss")
            exit_reason = "trail_stop" if stop != initial_stop_price else "stop"
        elif allow_target and low <= target:
            exit_price, exit_reason, outcome = target, "target", "win"
    if (
        exit_price is None
        and _is_rotated_sibling(str(position.get("slice_id") or ""), book_slice_ids)
        and not r_gate_on
    ):
        exit_price, exit_reason = close, "rotated"
        outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
    # HIP-3 calendar assets: PLANNED exits (horizon, time stop) must land on
    # the underlying's live tape. The paper fills at the latest known price:
    # a bar still forming fills at `now`, a completed (replayed) bar fills
    # at its close - so the session is checked at min(now, bar close).
    # If that fill time is outside the session, the planned exit defers to
    # the next bar whose fill time is in-session (bars_held keeps counting;
    # the position simply outlives its original deadline). Protective exits
    # (stop, trail, target, rotated, stale-data) are untouched - protection
    # never sleeps.
    planned_exit_allowed = True
    pos_slice = str(position.get("slice_id") or "")
    if pos_slice.startswith("hip3_"):
        bar_start = last["start"]
        if hasattr(bar_start, "to_pydatetime"):
            bar_start = bar_start.to_pydatetime()
        fill_time = min(now, bar_start + timedelta(hours=1))
        planned_exit_allowed = hip3_in_market_session(
            hip3_slice_market_class(pos_slice), fill_time
        )
    if (
        exit_price is None
        and horizon_bars > 0
        and bars_held >= horizon_bars
        and not r_gate_on
        and planned_exit_allowed
    ):
        exit_price, exit_reason = close, "horizon"
        outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
    trail_active = _coerce_bool(position.get("trail_active"))
    if (
        exit_price is None
        and horizon_bars == 0
        and bars_held >= TIME_STOP_BARS
        and not (TRAIL_ENABLE and TRAIL_IGNORE_TIME_STOP and trail_active)
        and not r_gate_on
        and planned_exit_allowed
    ):
        exit_price, exit_reason = close, "time_stop"
        outcome = "win" if (close > entry if side == "BUY" else close < entry) else "loss"
    if exit_price is None:
        if ((TRAIL_ENABLE and horizon_bars == 0) or r_gate_on) and r_dist > 0:
            if not trail_active:
                trail_active = (
                    peak_seen >= entry + TRAIL_ACTIVATE_R * r_dist
                    if side == "BUY"
                    else trough_seen <= entry - TRAIL_ACTIVATE_R * r_dist
                )
            if trail_active:
                stop = (
                    max(stop, peak_seen - TRAIL_DISTANCE_R * r_dist)
                    if side == "BUY"
                    else min(stop, trough_seen + TRAIL_DISTANCE_R * r_dist)
                )
                position["stop_price"] = str(stop)
            position["initial_stop_price"] = str(initial_stop_price)
            position["peak_price"] = str(peak_seen)
            position["trough_price"] = str(trough_seen)
            position["trail_active"] = "1" if trail_active else "0"
        position["bars_held"] = str(bars_held)
        position["missing_bars"] = "0"
        position["last_processed_bar_start"] = _bar_start_iso(last["start"])
        if horizon_bars > 0:
            position["horizon_bars"] = str(horizon_bars)
        return None
    return {
        "exit_price": exit_price, "exit_reason": exit_reason, "outcome": outcome,
        "bars_held": bars_held, "initial_stop_price": initial_stop_price,
        "peak_seen": peak_seen, "trough_seen": trough_seen, "stop": stop, "bar": last,
    }


@_serialized_paper_cycle
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
    hip3_book_path: Path | None = None,
) -> dict:
    closed_rows: list[dict] = []
    reconcile_paper_stats_from_log(book_path, log_path)
    if hip3_book_path is not None:
        reconcile_paper_stats_from_log(hip3_book_path, log_path)

    def _apply_feedback(slice_id: str, **kwargs) -> None:
        # HIP-3 slices carry their feedback in the HIP-3 book; the shared
        # trade log is the source of truth for both books.
        target = (
            hip3_book_path
            if hip3_book_path is not None and str(slice_id).startswith("hip3_")
            else book_path
        )
        apply_signal_feedback(target, slice_id, **kwargs)
    loaded_positions, positions_load_error = _read_positions_with_error(positions_path)
    invalid_positions: list[tuple[object, str]] = []
    open_positions: list[dict] = []
    for position in loaded_positions:
        error = _position_validation_error(position)
        if error is None:
            open_positions.append(position)
        else:
            invalid_positions.append((position, error))
    quarantine_path = positions_path.with_name("paper_position_quarantine.json")
    _quarantine_positions(quarantine_path, invalid_positions, server_time)
    # Migration: upgrade legacy positions so horizon exits engage.
    book_horizon_map = _load_book_horizon_map(book_path)
    if hip3_book_path is not None:
        # Slice ids are namespaced (hip3_ prefix), so the maps cannot collide.
        book_horizon_map = {**book_horizon_map, **_load_book_horizon_map(hip3_book_path)}
    # HIP-3 seat ring-fence: a dedicated sub-pool inside the shared wallet so
    # the immature lane can neither starve the native book nor flood it.
    # Read per cycle so it is testable and hot-adjustable via env.
    hip3_max_positions = max(
        0, min(50, _coerce_int(os.getenv("BREAKWATER_HIP3_MAX_POSITIONS", "6"), 6))
    )
    if open_positions:
        _migrate_legacy_positions(open_positions, horizon_map=book_horizon_map, frames=frames)

    counterfactual_path = positions_path.with_name("paper_counterfactuals.json")
    counterfactual_log_path = positions_path.with_name("paper_counterfactual_log.csv")
    counterfactual_trackers, counterfactual_state_error = read_counterfactual_trackers(
        counterfactual_path
    )
    if counterfactual_state_error is None:
        try:
            sync_open_positions(
                counterfactual_trackers,
                open_positions,
                server_time=server_time,
                spot_fee_bps=SPOT_FEE_BPS,
                perp_fee_bps=PERP_FEE_BPS,
            )
        except Exception as exc:
            counterfactual_state_error = f"{type(exc).__name__}: {exc}"[:240]

    surviving: list[dict] = []
    replayed_bars = 0
    positions_without_new_bars = 0
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
                initial_stop = Decimal(str(position.get("initial_stop_price") or stop))
                peak = Decimal(str(position.get("peak_price") or entry))
                trough = Decimal(str(position.get("trough_price") or entry))
                diagnostics = _trade_excursion_diagnostics(
                    side=side,
                    entry=entry,
                    initial_stop=initial_stop,
                    peak=peak,
                    trough=trough,
                    exit_price=entry,
                    notional_zar=notional_zar,
                    fee_zar=fees,
                    pnl_zar=pnl_zar,
                )
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
                        **diagnostics,
                    }
                )
                _apply_feedback(
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

        unseen = _unseen_bars(position, frame)
        if unseen is None or unseen.empty:
            positions_without_new_bars += 1
            position["missing_bars"] = "0"
            if horizon_bars > 0:
                position["horizon_bars"] = str(horizon_bars)
            position["regime"] = position_regime
            surviving.append(position)
            continue

        replayed_bars += len(unseen)
        exit_state = None
        for _, bar in unseen.iterrows():
            exit_state = _mark_position_bar(
                position,
                bar,
                horizon_bars=horizon_bars,
                book_slice_ids=book_slice_ids,
                now=server_time,
            )
            if exit_state is not None:
                break
        if exit_state is None:
            position["regime"] = position_regime
            surviving.append(position)
            continue

        last = exit_state["bar"]
        exit_price = exit_state["exit_price"]
        exit_reason = exit_state["exit_reason"]
        outcome = exit_state["outcome"]
        bars_held = exit_state["bars_held"]
        initial_stop_price = exit_state["initial_stop_price"]
        peak_seen = exit_state["peak_seen"]
        trough_seen = exit_state["trough_seen"]
        stop = exit_state["stop"]
        fee_bps = PERP_FEE_BPS if position["kind"] == "PERP" else SPOT_FEE_BPS
        direction = Decimal(1) if side == "BUY" else Decimal(-1)
        gross = (exit_price - entry) / entry * direction * notional_zar
        fees = notional_zar * fee_bps / Decimal(10000)
        pnl_zar = gross - fees
        diagnostics = _trade_excursion_diagnostics(
            side=side,
            entry=entry,
            initial_stop=initial_stop_price,
            peak=peak_seen,
            trough=trough_seen,
            exit_price=exit_price,
            notional_zar=notional_zar,
            fee_zar=fees,
            pnl_zar=pnl_zar,
        )

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
                **diagnostics,
                "exit_bar_start": _bar_start_iso(last["start"]),
            }
        )
        _apply_feedback(
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

    counterfactual_completed_rows: list[dict] = []
    if counterfactual_state_error is None:
        attach_actual_closures(counterfactual_trackers, closed_rows)
        counterfactual_advance = advance_counterfactuals(
            counterfactual_trackers,
            frames=frames,
            server_time=server_time,
            missing_bars_exit=missing_bars_exit,
            time_stop_bars=TIME_STOP_BARS,
        )
        counterfactual_state_error = counterfactual_advance.state_error
        if counterfactual_state_error is None:
            counterfactual_trackers = counterfactual_advance.trackers
            counterfactual_completed_rows = counterfactual_advance.completed_rows
            append_counterfactual_rows(
                counterfactual_log_path, counterfactual_completed_rows
            )

    # 2) Open new positions from signals (diversified)
    skipped = 0
    slot_full = 0
    slice_full = 0
    pair_held = 0
    aggregate_risk_cap_skips = 0
    aggregate_risk_unknown_skips = 0
    aggregate_open_risk_zar, aggregate_position_risk_unknown = _aggregate_stop_risk_zar(
        surviving
    )
    aggregate_risk_buffer_zar, buffer_unknown = _aggregate_risk_buffer_zar(surviving)
    aggregate_position_risk_unknown = (
        aggregate_position_risk_unknown
        or buffer_unknown
        or bool(invalid_positions)
        or positions_load_error is not None
    )
    aggregate_start_risk_zar = aggregate_open_risk_zar
    aggregate_guard_risk_zar = aggregate_open_risk_zar + aggregate_risk_buffer_zar
    aggregate_risk_added_zar = Decimal(0)
    aggregate_risk_cap_zar = _aggregate_risk_cap_zar(log_path)
    paper_equity_zar = _paper_equity_zar(log_path)
    aggregate_cap_source = (
        "explicit_zar"
        if str(os.getenv("BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR") or "").strip()
        else "equity_fraction"
    )

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
    if hip3_book_path is not None:
        # Per-slice stats merge so the losing-slice guard sees each book's own
        # history (slice ids are namespaced, so nothing mixes). Incumbents
        # stay native-only on purpose: HIP-3 runs its own sub-pool and must
        # not interact with the native old/fat split.
        trade_counts.update(_slice_trade_counts(hip3_book_path))
        paper_pnls.update(_slice_paper_pnl(hip3_book_path))
        means.update(_slice_means(hip3_book_path))
    size_from_equity = _env_bool("BREAKWATER_PAPER_SIZE_FROM_EQUITY", "0")
    risk_zar: Decimal | None = None
    notional_cap_zar: Decimal | None = None
    if size_from_equity:
        # Compounding sizing: the per-trade risk budget AND the notional
        # ceiling are both fractions of current equity, so the account takes
        # bigger absolute bets as it grows. The mandate's absolute notional
        # cap is a flat-mode boundary and is deliberately not applied here.
        risk_pct = _env_decimal("BREAKWATER_PAPER_RISK_OF_EQUITY", "0.01")
        risk_zar = paper_equity_zar * risk_pct
        notional_pct = _env_decimal("BREAKWATER_PAPER_MAX_POSITION_NOTIONAL_OF_EQUITY", "0.20")
        notional_cap_zar = paper_equity_zar * notional_pct

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

    # Per-book view of the shared guard counters: which book generated how
    # many signals and how many each guard turned away. This is what makes
    # "how many HIP-3 trades couldn't get a seat?" a number instead of an
    # inference. Shared counters above stay the source of truth.
    book_stats = {
        "native": {"signals": 0, "opened": 0, "slot_full": 0, "slice_full": 0, "pair_held": 0, "skipped": 0},
        "hip3": {"signals": 0, "opened": 0, "slot_full": 0, "slice_full": 0, "pair_held": 0, "skipped": 0},
    }
    for sig in signals:
        book_stats[_bkey_book(sig)]["signals"] += 1

    def _deny(signal, key: str) -> None:
        book_stats[_bkey_book(signal)][key] += 1

    for signal in candidates:
        if len(surviving) >= MAX_PAPER_POSITIONS:
            slot_full += 1
            _deny(signal, "slot_full")
            continue

        kind_open = sum(1 for position in surviving if position.get("kind") == signal.kind)
        if kind_open >= MAX_PAPER_POSITIONS_PER_KIND:
            slot_full += 1
            _deny(signal, "slot_full")
            continue
        old_open = 0
        hip3_open = 0
        for position in surviving:
            sid = str(position.get("slice_id") or "")
            if sid.startswith("hip3_"):
                hip3_open += 1
            elif sid in incumbents:
                old_open += 1
        fat_open = len(surviving) - old_open - hip3_open
        if str(signal.slice_id or "").startswith("hip3_"):
            # HIP-3 runs its own sub-pool: it neither consumes native
            # old/fat seats nor is governed by the native split.
            if hip3_open >= hip3_max_positions:
                slot_full += 1
                _deny(signal, "slot_full")
                continue
        elif signal.slice_id in incumbents:
            if OLD_PAPER_SEATS and old_open >= OLD_PAPER_SEATS:
                slot_full += 1
                _deny(signal, "slot_full")
                continue
        elif FAT_PAPER_SEATS and fat_open >= FAT_PAPER_SEATS:
            slot_full += 1
            _deny(signal, "slot_full")
            continue
        # HIP-3 sub-pool gets its own (tighter) per-slice cap so a single
        # edge cannot occupy half the pool; native keeps the global cap.
        slice_cap = (
            HIP3_MAX_POSITIONS_PER_SLICE
            if str(signal.slice_id or "").startswith("hip3_")
            else MAX_PAPER_POSITIONS_PER_SLICE
        )
        if open_slice_counts.get(signal.slice_id, 0) >= slice_cap:
            slice_full += 1
            _deny(signal, "slice_full")
            continue
        if trade_counts.get(signal.slice_id, 0) >= 3 and paper_pnls.get(signal.slice_id, 0.0) < 0:
            skipped += 1
            _deny(signal, "skipped")
            continue

        if signal.pair.upper() in open_pairs:
            pair_held += 1
            _deny(signal, "pair_held")
            continue

        if _is_rotated_sibling(signal.slice_id, book_slice_ids):
            skipped += 1
            _deny(signal, "skipped")
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
            _deny(signal, "skipped")
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
            _deny(signal, "skipped")
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
            _deny(signal, "skipped")
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
            _deny(signal, "skipped")
            continue

        notional_zar = _paper_size(
            signal, policy, usdc_zar, risk_zar=risk_zar, notional_cap_zar=notional_cap_zar
        )
        if notional_zar <= 0:
            # Hyperliquid 10 USDC floor (or zero risk distance). Same refuse, named.
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
                    "exit_reason": "below_perp_min_notional",
                    "entry_guard": "below_perp_min_notional",
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(getattr(signal, "atr", "") or ""),
                    "stop_atr_mult": str(getattr(signal, "stop_atr_mult", "") or ""),
                    "risk_fraction": "",
                },
            )
            skipped += 1
            _deny(signal, "skipped")
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
            _deny(signal, "skipped")
            continue

        proposed_risk_zar = notional_zar * risk_fraction
        buffer_bps = _env_decimal("BREAKWATER_PAPER_AGGREGATE_RISK_BUFFER_BPS", "25")
        proposed_buffer_zar = notional_zar * max(buffer_bps, Decimal(0)) / Decimal(10000)
        aggregate_reason = None
        if aggregate_position_risk_unknown or aggregate_risk_cap_zar is None:
            aggregate_reason = "aggregate_risk_unknown"
            aggregate_risk_unknown_skips += 1
        elif (
            aggregate_guard_risk_zar + proposed_risk_zar + proposed_buffer_zar
            > aggregate_risk_cap_zar
        ):
            aggregate_reason = "aggregate_risk_cap"
            aggregate_risk_cap_skips += 1
        if aggregate_reason is not None:
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
                    "exit_reason": aggregate_reason,
                    "entry_guard": aggregate_reason,
                    "regime": str(getattr(signal, "regime", "") or ""),
                    "pnl_outcome": "",
                    "atr": str(signal.atr),
                    "stop_atr_mult": f"{stop_atr_mult:.6f}" if signal.atr > 0 else "",
                    "risk_fraction": f"{risk_fraction:.8f}",
                },
            )
            skipped += 1
            _deny(signal, "skipped")
            continue

        signal_horizon = _coerce_int(getattr(signal, "horizon_bars", 0), 0)
        if signal_horizon <= 0:
            signal_horizon = book_horizon_map.get(signal.slice_id, 0)

        book_stats[_bkey_book(signal)]["opened"] += 1
        surviving.append(
            {
                "signal_id": signal.signal_id,
                "pair": signal.pair,
                "kind": signal.kind,
                "slice_id": signal.slice_id,
                "side": signal.side.value,
                "opened_at": server_time.isoformat(),
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
                "last_processed_bar_start": _bar_start_iso(frame.iloc[-1]["start"]),
            }
        )
        aggregate_open_risk_zar += proposed_risk_zar
        aggregate_guard_risk_zar += proposed_risk_zar + proposed_buffer_zar
        aggregate_risk_added_zar += proposed_risk_zar
        open_pairs.add(signal.pair.upper())
        open_slice_counts[signal.slice_id] = open_slice_counts.get(signal.slice_id, 0) + 1

    # Never overwrite an unreadable state file with an empty list. Operators
    # need the original bytes intact for recovery and audit.
    if positions_load_error is None:
        write_positions(positions_path, surviving)
    if counterfactual_state_error is None:
        try:
            sync_open_positions(
                counterfactual_trackers,
                surviving,
                server_time=server_time,
                spot_fee_bps=SPOT_FEE_BPS,
                perp_fee_bps=PERP_FEE_BPS,
            )
            write_counterfactual_trackers(counterfactual_path, counterfactual_trackers)
        except Exception as exc:
            counterfactual_state_error = f"{type(exc).__name__}: {exc}"[:240]
    aggregate_unknown = aggregate_position_risk_unknown or aggregate_risk_cap_zar is None
    remaining_risk = (
        max(aggregate_risk_cap_zar - aggregate_guard_risk_zar, Decimal(0))
        if aggregate_risk_cap_zar is not None and not aggregate_position_risk_unknown
        else None
    )
    cost_adjusted_risk_zar, cost_risk_unknown = _cost_adjusted_risk_zar(surviving)
    if invalid_positions or positions_load_error is not None:
        cost_risk_unknown = True
    position_risks = [
        (risk, position)
        for position in surviving
        if (risk := _active_stop_risk_zar(position)) is not None
    ]
    highest_risk_position = None
    if position_risks:
        highest_risk, highest_position = max(position_risks, key=lambda item: item[0])
        highest_risk_position = {
            "signal_id": str(highest_position.get("signal_id") or ""),
            "pair": str(highest_position.get("pair") or ""),
            "risk_zar": f"{highest_risk:.4f}",
        }
    utilization = None
    if aggregate_risk_cap_zar is not None and aggregate_risk_cap_zar > 0:
        utilization = aggregate_guard_risk_zar / aggregate_risk_cap_zar
    aggregate_over_cap = bool(
        aggregate_risk_cap_zar is not None
        and not aggregate_position_risk_unknown
        and aggregate_guard_risk_zar > aggregate_risk_cap_zar
    )
    if aggregate_unknown:
        aggregate_risk_status = "unknown"
    elif aggregate_over_cap:
        aggregate_risk_status = "over_cap"
    elif utilization is not None and utilization >= Decimal("0.8"):
        aggregate_risk_status = "warning"
    else:
        aggregate_risk_status = "ok"
    performance_summary = _paper_performance_summary(log_path)
    counterfactual_status = counterfactual_summary(counterfactual_log_path)
    counterfactual_status.update(
        {
            "active_trackers": len(counterfactual_trackers),
            "completed_this_cycle": len(counterfactual_completed_rows),
            "state_error": counterfactual_state_error,
            "prospective_only": True,
            "limitations": [
                "funding_not_modeled",
                "slippage_not_modeled",
                "hourly_intrabar_path_unknown",
            ],
        }
    )
    return {
        "closed": len(closed_rows),
        "open": len(surviving),
        "hip3_open": sum(
            1 for p in surviving if str(p.get("slice_id") or "").startswith("hip3_")
        ),
        "book_stats": book_stats,
        "new_signals": len(signals),
        "skipped": skipped,
        "slot_full": slot_full,
        "slice_full": slice_full,
        "pair_held": pair_held,
        "replayed_bars": replayed_bars,
        "positions_without_new_bars": positions_without_new_bars,
        "paper_equity_zar": f"{paper_equity_zar:.4f}",
        "aggregate_risk_start_zar": (
            None if aggregate_position_risk_unknown else f"{aggregate_start_risk_zar:.4f}"
        ),
        "aggregate_open_risk_zar": (
            None if aggregate_position_risk_unknown else f"{aggregate_open_risk_zar:.4f}"
        ),
        "aggregate_cost_adjusted_risk_zar": (
            None if cost_risk_unknown else f"{cost_adjusted_risk_zar:.4f}"
        ),
        "aggregate_risk_buffer_zar": (
            None
            if aggregate_position_risk_unknown
            else f"{aggregate_guard_risk_zar - aggregate_open_risk_zar:.4f}"
        ),
        "aggregate_risk_added_zar": f"{aggregate_risk_added_zar:.4f}",
        "aggregate_risk_cap_zar": (
            None if aggregate_risk_cap_zar is None else f"{aggregate_risk_cap_zar:.4f}"
        ),
        "aggregate_risk_cap_source": aggregate_cap_source,
        "aggregate_risk_remaining_zar": (
            None if remaining_risk is None else f"{remaining_risk:.4f}"
        ),
        "aggregate_risk_utilization": (
            None if utilization is None else f"{utilization:.4f}"
        ),
        "aggregate_risk_unknown": aggregate_unknown,
        "aggregate_risk_over_cap": aggregate_over_cap,
        "aggregate_risk_status": aggregate_risk_status,
        "aggregate_risk_cap_skips": aggregate_risk_cap_skips,
        "aggregate_risk_unknown_skips": aggregate_risk_unknown_skips,
        "positions_state_error": positions_load_error,
        "invalid_positions_quarantined": len(invalid_positions),
        "invalid_position_reasons": sorted({reason for _, reason in invalid_positions}),
        "highest_risk_position": highest_risk_position,
        "performance": performance_summary,
        "counterfactual": counterfactual_status,
    }
