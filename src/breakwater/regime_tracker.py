"""Intraday regime-shift tracker and defensive response.

The overnight research pass is the only place new SHORT slices can be promoted
into the book. But the system already has the information to know the game has
changed *before* the next research pass: every paper cycle fetches fresh frames
and computes each symbol's bull/bear/neutral regime.

This module turns that knowledge into a decision the same cycle:

- ``compute_regime_snapshot`` summarises the currently-traded frames (native
  PERPs by default) into bull/bear/neutral breadth.
- ``update_regime_state`` persists a small bounded state file and returns a
  ``RegimeShift`` with ``confirmed_bear`` / ``confirmed_bull`` / ``flip``.
  Confirmation requires ``FLIP_CONFIRM_CYCLES`` consecutive cycles so one noisy
  bar cannot trigger a defensive response.
- ``regime_gate`` is the defensive entry gate. It keeps the existing
  hostile-unproven behaviour, but a *confirmed* macro shift always blocks the
  wrong-direction entries regardless of ``hostile_unproven``. This closes the
  hole where a "proven" LONG slice could keep entering after a bear flip.
- ``defensive_exit`` tells the paper engine to close existing opposite-
  direction positions on a confirmed shift, so longs do not ride a confirmed
  bear to the horizon/stop when the edge was regime-dependent.

This is observation machinery only: it never promotes a strategy, never writes
a venue order, and never adjusts any research quality bar.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCHEMA = "breakwater.regime_shift.v1"

FLIP_CONFIRM_CYCLES = max(1, int(os.getenv("BREAKWATER_REGIME_CONFIRM_CYCLES", "2")))
BEAR_BREADTH = float(os.getenv("BREAKWATER_REGIME_BEAR_BREADTH", "0.50"))
BULL_BREADTH = float(os.getenv("BREAKWATER_REGIME_BULL_BREADTH", "0.50"))
NEUTRAL_BREADTH = float(os.getenv("BREAKWATER_REGIME_NEUTRAL_BREADTH", "0.50"))


@dataclass(frozen=True)
class RegimeShift:
    label: str
    bear_breadth: float
    bull_breadth: float
    neutral_breadth: float
    confirmed_bear: bool
    confirmed_bull: bool
    flip: bool
    flipped_from: str
    consecutive_bear: int
    consecutive_bull: int
    as_of: str


def _bulk_regimes(frames_by_kind: dict[str, dict[str, pd.DataFrame]]) -> dict[str, str]:
    """Return symbol -> regime for every usable frame (native PERP preferred)."""
    # Lazy import: monitor.py imports this module (via regime_gate) inside
    # monitor_book, so importing monitor at module load would be circular.
    from breakwater.monitor import regime_of

    regimes: dict[str, str] = {}
    for kind in ("PERP", "SPOT"):
        for symbol, frame in (frames_by_kind.get(kind) or {}).items():
            if frame is None or getattr(frame, "empty", True):
                continue
            regimes[str(symbol).upper()] = regime_of(frame)
    return regimes


def compute_regime_snapshot(frames_by_kind: dict[str, dict[str, pd.DataFrame]]) -> dict:
    regimes = _bulk_regimes(frames_by_kind)
    total = len(regimes)
    bear = sum(1 for value in regimes.values() if value == "bear")
    bull = sum(1 for value in regimes.values() if value == "bull")
    neutral = sum(1 for value in regimes.values() if value == "neutral")
    breadth = {
        "bear": round(bear / total, 4) if total else 0.0,
        "bull": round(bull / total, 4) if total else 0.0,
        "neutral": round(neutral / total, 4) if total else 0.0,
    }

    # Simple majority rule. Prefer the larger pole; only call it a shift when the
    # pole also clears the configured breadth threshold, otherwise stay neutral.
    if breadth["bear"] >= BEAR_BREADTH and breadth["bear"] > breadth["bull"]:
        label = "bear"
    elif breadth["bull"] >= BULL_BREADTH and breadth["bull"] > breadth["bear"]:
        label = "bull"
    else:
        label = "neutral"

    return {
        "symbols": total,
        "bear": bear,
        "bull": bull,
        "neutral": neutral,
        "breadth": breadth,
        "label": label,
    }


def update_regime_state(
    path: Path,
    snapshot: dict,
    *,
    now: datetime | None = None,
) -> RegimeShift:
    """Merge a fresh snapshot into the bounded state file and return the shift.

    Idempotent per cycle: repeated runs in the same cycle (replayed bars) can
    only advance confirmation once per distinct ``as_of`` minute.
    """
    now = now or datetime.now(timezone.utc)
    as_of = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    previous: dict = {}
    if path.exists():
        try:
            payload = json.loads(path.read_text())
            if payload.get("schema") == SCHEMA:
                previous = payload
        except (OSError, json.JSONDecodeError):
            previous = {}

    prior_label = str(previous.get("label") or "neutral")
    last_as_of = str(previous.get("as_of") or "")
    consecutive = {
        "bear": int(previous.get("consecutive_bear") or 0),
        "bull": int(previous.get("consecutive_bull") or 0),
    }

    label = str(snapshot.get("label") or "neutral")

    # Only advance confirmation when the as-of minute actually changed, so a
    # repeated run inside the same cycle cannot double-count confirmation.
    if last_as_of == as_of:
        confirmed_bear = bool(previous.get("confirmed_bear"))
        confirmed_bull = bool(previous.get("confirmed_bull"))
        flip = bool(previous.get("flip"))
        flipped_from = str(previous.get("flipped_from") or "")
    else:
        if label == "bear":
            consecutive["bear"] += 1
            consecutive["bull"] = 0
        elif label == "bull":
            consecutive["bull"] += 1
            consecutive["bear"] = 0
        else:
            consecutive["bear"] = int(previous.get("consecutive_bear") or 0)
            consecutive["bull"] = int(previous.get("consecutive_bull") or 0)

        confirmed_bear = consecutive["bear"] >= FLIP_CONFIRM_CYCLES
        confirmed_bull = consecutive["bull"] >= FLIP_CONFIRM_CYCLES
        flip = bool(
            (label in {"bear", "bull"} and prior_label in {"bear", "bull", "neutral"})
            and (confirmed_bear or confirmed_bull)
        )
        flipped_from = prior_label if flip else str(previous.get("flipped_from") or "")

    payload = {
        "schema": SCHEMA,
        "label": label,
        "as_of": as_of,
        "bear": int(snapshot.get("bear") or 0),
        "bull": int(snapshot.get("bull") or 0),
        "neutral": int(snapshot.get("neutral") or 0),
        "breadth": snapshot.get("breadth") or {},
        "confirmed_bear": confirmed_bear,
        "confirmed_bull": confirmed_bull,
        "flip": flip,
        "flipped_from": flipped_from,
        "consecutive_bear": consecutive["bear"],
        "consecutive_bull": consecutive["bull"],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise

    return RegimeShift(
        label=label,
        bear_breadth=float((snapshot.get("breadth") or {}).get("bear") or 0.0),
        bull_breadth=float((snapshot.get("breadth") or {}).get("bull") or 0.0),
        neutral_breadth=float((snapshot.get("breadth") or {}).get("neutral") or 0.0),
        confirmed_bear=confirmed_bear,
        confirmed_bull=confirmed_bull,
        flip=flip,
        flipped_from=flipped_from,
        consecutive_bear=consecutive["bear"],
        consecutive_bull=consecutive["bull"],
        as_of=as_of,
    )


def read_regime_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) and payload.get("schema") == SCHEMA else {}


def regime_shift_dict(shift: RegimeShift) -> dict:
    return asdict(shift)


def regime_gate(
    side: str,
    regime: str,
    hostile_unproven: bool,
    shift: RegimeShift | None,
    *,
    asset_status: str = "",
) -> tuple[bool, str]:
    """Defensive entry gate.

    Returns ``(blocked, reason)``. It preserves the existing per-symbol
    ``hostile_unproven`` rule. The *confirmed macro* rule does NOT override
    per-asset evidence: the aggregate regime reading is portfolio-level, and an
    individual asset is decided by its own asset-edge status (green allowed,
    untested allowed so cold-start action is never zeroed, blocked denied at
    the asset layer). A confirmed macro shift is still used for defensive exits
    and for arming validated SHORT inventory observations.
    """
    side = str(side).upper()
    # The macro aggregate is no longer a per-asset hard block. It is portfolio
    # context, not a replacement for an asset's own evidence. A per-asset
    # blocked asset is denied here even if it bypassed the monitor; untested
    # assets are explicitly allowed so a fresh/evidence-less book can build the
    # closes needed for a verdict.
    if asset_status == "blocked":
        return True, "asset_not_green"
    strict = str(os.getenv("BREAKWATER_REGIME_GATE_STRICT", "0")).strip().lower() in {
        "1", "true", "yes", "y", "on",
    }
    if side == "BUY" and regime == "bear":
        return (True, "regime_blocked") if (strict or hostile_unproven) else (False, "")
    if side == "SELL" and regime == "bull":
        return (True, "regime_blocked") if (strict or hostile_unproven) else (False, "")
    return False, ""


def defensive_exit(
    position: dict,
    shift: RegimeShift | None,
    *,
    r_gate_on: bool,
    asset_status: str = "",
) -> bool:
    """Should this position be closed early on a confirmed macro shift?

    The global macro shift is portfolio context, not a license to blanket-close
    every individual asset. A position is defensively exited only when its own
    per-asset verdict is ``blocked``. Green and untested assets ride their own
    stop/horizon and the green-lane freeze, so a sustained global bear reading
    cannot churn every open BUY into a realized loss.
    """
    if shift is None or not (shift.confirmed_bear or shift.confirmed_bull):
        return False
    side = str(position.get("side") or "").upper()
    # Per-asset evidence decides individual assets. No per-asset block means no
    # blanket defensive exit, including legacy positions that predate this field.
    if str(asset_status or "").strip().lower() != "blocked":
        return False
    # Never exit a winner that has already banked its move; R-gate keeps winners.
    if r_gate_on:
        return False
    if side == "BUY" and shift.confirmed_bear:
        return True
    if side == "SELL" and shift.confirmed_bull:
        return True
    return False
