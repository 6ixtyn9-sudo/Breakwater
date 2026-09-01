"""Intraday short inventory: observe and conditionally arm SHORT slices.

The overnight research pass can promote shorts, but it only runs daily. In a
confirmed bear the system *knows* the regime has flipped intraday, but it has
no booked short to act on. This module closes that gap read-only:

- It reads the already-validated SHORT slices (and, as an explicit and clearly
  marked fallback, discovered SHORT candidates) that the research pass has
  already tested with the same side/cost-correct math.
- On the current frames it checks whether the slice's feature state is active
  right now and builds a SHORT observation (pair, entry, stop, regime, edge).
- It decides whether the observation is **armable**. Arming is deliberate and
  conservative: it requires a *validated* (not merely discovered) SHORT slice,
  mean_ret_costadj above the net-edge floor, no hostile-regime confounding,
  enough breadth, an active state on a current bar, a confirmed bear macro
  shift, and an explicit operator env flag.

With the 2026-08-30 evidence, native research has ZERO validated shorts, so
the inventory is empty and nothing is armed. The value of the hook is that the
moment a validated short exists, it can be surfaced and armed in the same
paper cycle instead of waiting for the next overnight promotion.

It never writes to the monitored book, paper positions, or a venue. It never
lowers a research bar. It never author-authors a slice.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

SHORT_INVENTORY_ENABLED = str(os.getenv("BREAKWATER_SHORT_INVENTORY", "1")).strip().lower() in {
    "1", "true", "yes", "on",
}
SHORT_PROMOTE_ENABLED = str(os.getenv("BREAKWATER_SHORT_OBSERVATION_PROMOTE", "0")).strip().lower() in {
    "1", "true", "yes", "on",
}
SHORT_MIN_EDGE_BPS = int(os.getenv("BREAKWATER_SHORT_MIN_EDGE_BPS", "40"))
SHORT_MIN_N = int(os.getenv("BREAKWATER_SHORT_MIN_N", "300"))
SHORT_MIN_BREADTH = int(os.getenv("BREAKWATER_SHORT_MIN_BREADTH", "6"))
SHORT_USE_PROVISIONAL = str(os.getenv("BREAKWATER_SHORT_USE_PROVISIONAL", "0")).strip().lower() in {
    "1", "true", "yes", "on",
}

SCHEMA = "breakwater.short_inventory.v1"


def _coerce_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _coerce_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def _coerce_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _lane(slice_id: str) -> str:
    return "hip3" if str(slice_id).startswith("hip3_") else "native"


@dataclass(frozen=True)
class ShortCandidate:
    slice_id: str
    kind: str
    feature: str
    state: int
    side: str  # always SHORT
    mean_ret_costadj: float
    edge_bps: float
    n: int
    breadth_symbols: int
    p_value: float
    validated: bool
    provisional: bool
    regime_confounded: bool
    hostile_unproven: bool
    fail_reasons: str
    horizon_bars: int
    stop_atr_mult: float
    source: str


@dataclass(frozen=True)
class ShortObservation:
    slice_id: str
    kind: str
    pair: str
    side: str
    feature: str
    state: int
    entry_price: str
    stop_price: str
    atr: str
    regime: str
    edge_bps: float
    horizon_bars: int
    stop_atr_mult: float
    state_active: bool
    armable: bool
    arm_reason: str


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _candidate_from_validated(row: dict) -> ShortCandidate | None:
    if str(row.get("side") or "").strip().upper() != "SHORT":
        return None
    slice_id = str(row.get("slice_id") or "")
    if not slice_id:
        return None
    mean = _coerce_float(row.get("mean_ret_costadj"))
    return ShortCandidate(
        slice_id=slice_id,
        kind=str(row.get("kind") or _lane(slice_id)),
        feature=str(row.get("feature") or ""),
        state=_coerce_int(row.get("state")),
        side="SHORT",
        mean_ret_costadj=mean,
        edge_bps=mean * 10_000,
        n=_coerce_int(row.get("n")),
        breadth_symbols=_coerce_int(row.get("breadth_symbols_used")),
        p_value=_coerce_float(row.get("p_value"), 1.0),
        validated=_coerce_bool(row.get("validated"), False),
        provisional=False,
        regime_confounded=_coerce_bool(row.get("regime_confounded"), False),
        hostile_unproven=_coerce_bool(row.get("hostile_unproven"), True),
        fail_reasons=str(row.get("fail_reasons") or ""),
        horizon_bars=_coerce_int(row.get("horizon_bars"), 1),
        stop_atr_mult=_coerce_float(row.get("stop_atr_mult"), 2.0),
        source="validated_walk_forward",
    )


def _candidate_from_discovered(row: dict) -> ShortCandidate | None:
    if str(row.get("side") or "").strip().upper() != "SHORT":
        return None
    slice_id = str(row.get("slice_id") or "")
    if not slice_id:
        return None
    mean = _coerce_float(row.get("mean_ret_costadj"))
    return ShortCandidate(
        slice_id=slice_id,
        kind=str(row.get("kind") or _lane(slice_id)),
        feature=str(row.get("feature") or ""),
        state=_coerce_int(row.get("state")),
        side="SHORT",
        mean_ret_costadj=mean,
        edge_bps=mean * 10_000,
        n=_coerce_int(row.get("n")),
        breadth_symbols=0,
        p_value=_coerce_float(row.get("p_value"), 1.0),
        validated=False,
        provisional=True,
        regime_confounded=False,
        hostile_unproven=True,
        fail_reasons="provisional_discovery_fallback",
        horizon_bars=_coerce_int(row.get("horizon_bars"), 1),
        stop_atr_mult=2.0,
        source="discovered_provisional",
    )


def _short_candidates(validated_path: Path, discovered_path: Path) -> list[ShortCandidate]:
    """Candidates from validated research; option to add provisional fallback."""
    candidates: list[ShortCandidate] = []
    seen: set[str] = set()
    for row in _read_csv(validated_path):
        candidate = _candidate_from_validated(row)
        if candidate is None:
            continue
        # Default: only walk-forward validated shorts can become real book
        # inventory. Provisional evidence is explicit and opt-in only.
        if not candidate.validated and not SHORT_USE_PROVISIONAL:
            continue
        candidates.append(candidate)
        seen.add(candidate.slice_id)
    if SHORT_USE_PROVISIONAL:
        for row in _read_csv(discovered_path):
            candidate = _candidate_from_discovered(row)
            if candidate is None or candidate.slice_id in seen:
                continue
            candidates.append(candidate)
            seen.add(candidate.slice_id)
    return candidates


def _display_edge(candidate: ShortCandidate) -> str:
    return f"{candidate.edge_bps:.1f}b"


def _armable(candidate: ShortCandidate, *, confirmed_bear: bool) -> tuple[bool, str]:
    """A short may be armed into paper only when it meets every real bar."""
    if not SHORT_PROMOTE_ENABLED:
        return False, "promote_env_off"
    if not candidate.validated:
        return False, "not_validated"
    if candidate.provisional:
        return False, "provisional_only"
    if candidate.regime_confounded:
        return False, "regime_confounded"
    if candidate.mean_ret_costadj * 10_000 < SHORT_MIN_EDGE_BPS:
        return False, "below_floor"
    if candidate.n < SHORT_MIN_N:
        return False, "too_few_rows"
    if candidate.breadth_symbols < SHORT_MIN_BREADTH:
        return False, "too_few_symbols"
    if not confirmed_bear:
        return False, "not_confirmed_bear"
    return True, "ok"


def _observe_candidates(
    candidates: list[ShortCandidate],
    frames_by_kind: dict[str, dict],
    *,
    server_time: datetime,
    confirmed_bear: bool,
) -> list[ShortObservation]:
    observations: list[ShortObservation] = []
    # Lazy import: monitor is heavy and already imports this module's siblings.
    from breakwater.monitor import _latest_state, regime_of

    for candidate in candidates:
        for kind, pair, frame in _iter_frames(frames_by_kind, candidate.kind):
            if frame is None or getattr(frame, "empty", True):
                continue
            if len(frame) < 60:
                continue
            featured = None
            try:
                from breakwater.features import compute_price_features

                featured = compute_price_features(frame)
            except Exception:
                continue
            latest_state, latest_row = _latest_state(featured, candidate.feature)
            if latest_state != candidate.state:
                continue
            close = Decimal(str(latest_row["close"]))
            regime = regime_of(frame)
            # A bad/tiny/short-only active bar should not produce a huge
            # notional; compute a stop the same way monitor does.
            from breakwater.monitor import _atr

            atr_raw = _atr(featured)
            if close <= 0 or atr_raw <= 0:
                continue
            atr = Decimal(str(atr_raw))
            stop_distance = Decimal(str(candidate.stop_atr_mult)) * atr
            stop = close + stop_distance  # SHORT stop is above entry
            armable, reason = _armable(candidate, confirmed_bear=confirmed_bear)
            observations.append(
                ShortObservation(
                    slice_id=candidate.slice_id,
                    kind=candidate.kind,
                    pair=pair.upper(),
                    side="SHORT",
                    feature=candidate.feature,
                    state=candidate.state,
                    entry_price=str(close),
                    stop_price=str(stop),
                    atr=str(atr),
                    regime=regime,
                    edge_bps=candidate.edge_bps,
                    horizon_bars=candidate.horizon_bars,
                    stop_atr_mult=candidate.stop_atr_mult,
                    state_active=True,
                    armable=armable,
                    arm_reason=reason,
                )
            )
    return observations


def _iter_frames(frames_by_kind: dict[str, dict], kind: str):
    if not kind:
        return
    for pair, frame in (frames_by_kind.get("PERP") or {}).items():
        if kind == "PERP":
            yield "PERP", pair, frame
    for pair, frame in (frames_by_kind.get("SPOT") or {}).items():
        if kind == "SPOT":
            yield "SPOT", pair, frame


def compute_short_inventory(
    *,
    validated_path: Path,
    discovered_path: Path,
    frames_by_kind: dict[str, dict],
    server_time: datetime,
    confirmed_bear: bool,
) -> dict:
    """Observation-only short inventory. Writes no book/paper state."""
    enabled = SHORT_INVENTORY_ENABLED
    if not enabled:
        return {"enabled": False, "candidates": 0, "observations": 0, "armable": 0, "reasons": "disabled"}
    candidates = _short_candidates(validated_path, discovered_path)
    eligible = [
        c
        for c in candidates
        if c.edge_bps >= SHORT_MIN_EDGE_BPS
        and (not c.validated or not c.regime_confounded)
    ]
    observations = _observe_candidates(
        eligible, frames_by_kind, server_time=server_time, confirmed_bear=confirmed_bear
    )
    armable = [o for o in observations if o.armable]
    return {
        "enabled": True,
        "confirmed_bear": confirmed_bear,
        "promote_enabled": SHORT_PROMOTE_ENABLED,
        "candidates": len(candidates),
        "eligible": len(eligible),
        "observations": len(observations),
        "armable": len(armable),
        "armable_slices": sorted({o.slice_id for o in armable}),
        "armable_pairs": sorted({o.pair for o in armable}),
        "candidates_sample": [
            {
                "slice_id": c.slice_id,
                "kind": c.kind,
                "edge_bps": round(c.edge_bps, 1),
                "n": c.n,
                "breadth": c.breadth_symbols,
                "validated": c.validated,
                "provisional": c.provisional,
                "regime_confounded": c.regime_confounded,
                "fail_reasons": c.fail_reasons,
                "armable": _armable(c, confirmed_bear=confirmed_bear),
            }
            for c in sorted(eligible, key=lambda c: c.edge_bps, reverse=True)[:15]
        ],
        "observations_sample": [
            asdict(o) for o in observations[:15]
        ],
        "as_of": server_time.astimezone(timezone.utc).isoformat(),
    }


def write_short_inventory(path: Path, payload: dict) -> None:
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


def read_short_inventory(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}
