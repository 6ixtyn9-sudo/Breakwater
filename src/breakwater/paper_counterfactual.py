"""Prospective counterfactual exit tracking for paper positions.

A single real paper position is mirrored into several shadow exit policies.
The shadows never create orders, consume seats, alter the monitored book, or
feed lifecycle outcomes. They answer what happened after the real 2R exit
without changing the live paper sample midstream.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

COUNTERFACTUAL_HEADERS = [
    "closed_at",
    "signal_id",
    "pair",
    "kind",
    "slice_id",
    "side",
    "policy",
    "entry_price",
    "exit_price",
    "initial_stop_price",
    "final_stop_price",
    "notional_zar",
    "pnl_zar",
    "pnl_outcome",
    "bars_held",
    "exit_reason",
    "mfe_r",
    "mae_r",
    "peak_giveback_r",
    "actual_exit_reason",
    "actual_exit_price",
    "actual_pnl_zar",
    "delta_vs_actual_zar",
    "exit_bar_start",
]

POLICIES = {
    "target_2r_trail_1r": {"target_r": Decimal("2"), "trail_distance_r": Decimal("1")},
    "target_3r_trail_1r": {"target_r": Decimal("3"), "trail_distance_r": Decimal("1")},
    "target_4r_trail_1r": {"target_r": Decimal("4"), "trail_distance_r": Decimal("1")},
    "no_target_trail_1r": {"target_r": None, "trail_distance_r": Decimal("1")},
    "no_target_trail_2r": {"target_r": None, "trail_distance_r": Decimal("2")},
}


@dataclass(frozen=True)
class CounterfactualAdvance:
    trackers: list[dict]
    completed_rows: list[dict]
    state_error: str | None


def read_counterfactual_trackers(path: Path) -> tuple[list[dict], str | None]:
    if not path.exists():
        return [], None
    try:
        payload = json.loads(path.read_text())
    except OSError:
        return [], "unreadable"
    except json.JSONDecodeError:
        return [], "invalid_json"
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        return [], "unsupported_schema"
    return payload, None


def write_counterfactual_trackers(path: Path, trackers: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(trackers, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def append_counterfactual_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    if exists:
        with path.open(newline="") as handle:
            header = next(csv.reader(handle), [])
        if header != COUNTERFACTUAL_HEADERS:
            raise RuntimeError("paper counterfactual log has an unsupported schema")
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COUNTERFACTUAL_HEADERS)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())


def _decimal(value, field: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(f"counterfactual {field} is invalid") from exc
    if not number.is_finite():
        raise RuntimeError(f"counterfactual {field} must be finite")
    return number


def _initial_policy_stop(
    *,
    side: str,
    entry: Decimal,
    initial_stop: Decimal,
    peak: Decimal,
    trough: Decimal,
    trail_distance_r: Decimal,
    actual_stop: Decimal,
) -> Decimal:
    risk = abs(entry - initial_stop)
    if risk <= 0:
        return actual_stop
    if trail_distance_r == 1:
        return actual_stop
    if side == "BUY":
        return max(initial_stop, peak - trail_distance_r * risk)
    return min(initial_stop, trough + trail_distance_r * risk)


def sync_open_positions(
    trackers: list[dict],
    positions: list[dict],
    *,
    server_time: datetime,
    spot_fee_bps: Decimal,
    perp_fee_bps: Decimal,
) -> list[dict]:
    by_signal = {str(row.get("signal_id") or ""): row for row in trackers}
    for position in positions:
        signal_id = str(position.get("signal_id") or "")
        if not signal_id or signal_id in by_signal:
            continue
        entry = _decimal(position.get("entry_price"), "entry_price")
        actual_stop = _decimal(position.get("stop_price"), "stop_price")
        initial_stop = _decimal(
            position.get("initial_stop_price") or actual_stop, "initial_stop_price"
        )
        peak = _decimal(position.get("peak_price") or entry, "peak_price")
        trough = _decimal(position.get("trough_price") or entry, "trough_price")
        side = str(position.get("side") or "").upper()
        if side not in {"BUY", "SELL"}:
            continue
        policies = {}
        for name, spec in POLICIES.items():
            policies[name] = {
                "active": True,
                "bars_held": int(position.get("bars_held") or 0),
                "stop_price": str(
                    _initial_policy_stop(
                        side=side,
                        entry=entry,
                        initial_stop=initial_stop,
                        peak=peak,
                        trough=trough,
                        trail_distance_r=spec["trail_distance_r"],
                        actual_stop=actual_stop,
                    )
                ),
            }
        tracker = {
            "tracked_at": server_time.isoformat(),
            "signal_id": signal_id,
            "pair": str(position.get("pair") or ""),
            "kind": str(position.get("kind") or ""),
            "slice_id": str(position.get("slice_id") or ""),
            "side": side,
            "entry_price": str(entry),
            "initial_stop_price": str(initial_stop),
            "notional_zar": str(position.get("notional_zar") or "0"),
            "fee_bps": str(perp_fee_bps if position.get("kind") == "PERP" else spot_fee_bps),
            "horizon_bars": int(position.get("horizon_bars") or 0),
            "peak_price": str(peak),
            "trough_price": str(trough),
            "missing_bars": int(position.get("missing_bars") or 0),
            "last_processed_bar_start": str(position.get("last_processed_bar_start") or ""),
            "actual_exit_reason": "",
            "actual_exit_price": "",
            "actual_pnl_zar": "",
            "actual_exit_bar_start": "",
            "policies": policies,
        }
        trackers.append(tracker)
        by_signal[signal_id] = tracker
    return trackers


def attach_actual_closures(trackers: list[dict], closed_rows: list[dict]) -> None:
    by_signal = {str(row.get("signal_id") or ""): row for row in trackers}
    for closed in closed_rows:
        tracker = by_signal.get(str(closed.get("signal_id") or ""))
        if tracker is None:
            continue
        tracker["actual_exit_reason"] = str(closed.get("exit_reason") or "")
        tracker["actual_exit_price"] = str(closed.get("exit_price") or "")
        tracker["actual_pnl_zar"] = str(closed.get("pnl_zar") or "")
        tracker["actual_exit_bar_start"] = str(closed.get("exit_bar_start") or "")


def _pnl(
    *, side: str, entry: Decimal, exit_price: Decimal, notional: Decimal, fee_bps: Decimal
) -> Decimal:
    direction = Decimal(1) if side == "BUY" else Decimal(-1)
    gross = (exit_price - entry) / entry * direction * notional
    return gross - notional * fee_bps / Decimal(10000)


def _completion_row(
    tracker: dict,
    policy_name: str,
    policy: dict,
    *,
    exit_price: Decimal,
    exit_reason: str,
    server_time: datetime,
    mfe_r: Decimal,
    mae_r: Decimal,
    peak: Decimal,
    trough: Decimal,
    exit_bar_start: str = "",
) -> dict:
    entry = _decimal(tracker["entry_price"], "entry_price")
    initial_stop = _decimal(tracker["initial_stop_price"], "initial_stop_price")
    notional = _decimal(tracker["notional_zar"], "notional_zar")
    fee_bps = _decimal(tracker["fee_bps"], "fee_bps")
    pnl = _pnl(
        side=tracker["side"],
        entry=entry,
        exit_price=exit_price,
        notional=notional,
        fee_bps=fee_bps,
    )
    risk = abs(entry - initial_stop)
    giveback = Decimal(0)
    if risk > 0:
        giveback = (
            (peak - exit_price) / risk
            if tracker["side"] == "BUY"
            else (exit_price - trough) / risk
        )
    actual_pnl_text = str(tracker.get("actual_pnl_zar") or "")
    actual_pnl = _decimal(actual_pnl_text, "actual_pnl_zar") if actual_pnl_text else None
    delta = pnl - actual_pnl if actual_pnl is not None else None
    return {
        "closed_at": server_time.isoformat(),
        "signal_id": tracker["signal_id"],
        "pair": tracker["pair"],
        "kind": tracker["kind"],
        "slice_id": tracker["slice_id"],
        "side": tracker["side"],
        "policy": policy_name,
        "entry_price": str(entry),
        "exit_price": str(exit_price),
        "initial_stop_price": str(initial_stop),
        "final_stop_price": str(policy["stop_price"]),
        "notional_zar": str(notional),
        "pnl_zar": f"{pnl:.4f}",
        "pnl_outcome": "win" if pnl > 0 else "loss",
        "bars_held": str(policy["bars_held"]),
        "exit_reason": exit_reason,
        "mfe_r": f"{mfe_r:.6f}",
        "mae_r": f"{mae_r:.6f}",
        "peak_giveback_r": f"{giveback:.6f}",
        "actual_exit_reason": str(tracker.get("actual_exit_reason") or ""),
        "actual_exit_price": str(tracker.get("actual_exit_price") or ""),
        "actual_pnl_zar": actual_pnl_text,
        "delta_vs_actual_zar": f"{delta:.4f}" if delta is not None else "",
        "exit_bar_start": exit_bar_start,
    }


def _tracker_unseen_bars(tracker: dict, frame):
    ordered = frame.sort_values("start").drop_duplicates("start")
    raw_last = str(tracker.get("last_processed_bar_start") or "").strip()
    if not raw_last:
        return ordered.tail(1)
    try:
        last_processed = datetime.fromisoformat(raw_last.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("counterfactual last_processed_bar_start is invalid") from exc
    starts = ordered["start"]
    if getattr(starts.dt, "tz", None) is not None and last_processed.tzinfo is None:
        from datetime import timezone

        last_processed = last_processed.replace(tzinfo=timezone.utc)
    return ordered[starts > last_processed]


def _tracker_bar_iso(value) -> str:
    timestamp = value.to_pydatetime() if hasattr(value, "to_pydatetime") else value
    if not isinstance(timestamp, datetime):
        timestamp = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    return timestamp.isoformat()


def advance_counterfactuals(
    trackers: list[dict],
    *,
    frames: dict,
    server_time: datetime,
    missing_bars_exit: int,
    time_stop_bars: int = 48,
    max_bars: int = 240,
) -> CounterfactualAdvance:
    completed_rows: list[dict] = []
    surviving_trackers: list[dict] = []
    try:
        for tracker in trackers:
            active_policies = {
                name: policy
                for name, policy in tracker.get("policies", {}).items()
                if policy.get("active")
            }
            if not active_policies:
                continue
            frame = frames.get(str(tracker["pair"]).upper())
            entry = _decimal(tracker["entry_price"], "entry_price")
            initial_stop = _decimal(tracker["initial_stop_price"], "initial_stop_price")
            risk = abs(entry - initial_stop)
            if risk <= 0:
                raise RuntimeError("counterfactual initial risk must be positive")
            if tracker.get("actual_exit_reason") == "rotated":
                exit_price = _decimal(tracker["actual_exit_price"], "actual_exit_price")
                peak = _decimal(tracker["peak_price"], "peak_price")
                trough = _decimal(tracker["trough_price"], "trough_price")
                mfe_r = (
                    (peak - entry) / risk
                    if tracker["side"] == "BUY"
                    else (entry - trough) / risk
                )
                mae_r = (
                    (entry - trough) / risk
                    if tracker["side"] == "BUY"
                    else (peak - entry) / risk
                )
                for name, policy in active_policies.items():
                    policy["active"] = False
                    completed_rows.append(
                        _completion_row(
                            tracker,
                            name,
                            policy,
                            exit_price=exit_price,
                            exit_reason="rotated",
                            server_time=server_time,
                            mfe_r=mfe_r,
                            mae_r=mae_r,
                            peak=peak,
                            trough=trough,
                            exit_bar_start=str(tracker.get("actual_exit_bar_start") or ""),
                        )
                    )
                continue
            if frame is None or frame.empty:
                tracker["missing_bars"] = int(tracker.get("missing_bars") or 0) + 1
                if tracker["missing_bars"] >= missing_bars_exit:
                    peak = _decimal(tracker["peak_price"], "peak_price")
                    trough = _decimal(tracker["trough_price"], "trough_price")
                    mfe_r = (
                        (peak - entry) / risk
                        if tracker["side"] == "BUY"
                        else (entry - trough) / risk
                    )
                    mae_r = (
                        (entry - trough) / risk
                        if tracker["side"] == "BUY"
                        else (peak - entry) / risk
                    )
                    for name, policy in active_policies.items():
                        policy["active"] = False
                        completed_rows.append(
                            _completion_row(
                                tracker,
                                name,
                                policy,
                                exit_price=entry,
                                exit_reason="stale_data",
                                server_time=server_time,
                                mfe_r=mfe_r,
                                mae_r=mae_r,
                                peak=peak,
                                trough=trough,
                            )
                        )
                if any(policy.get("active") for policy in tracker["policies"].values()):
                    surviving_trackers.append(tracker)
                continue

            tracker["missing_bars"] = 0
            unseen = _tracker_unseen_bars(tracker, frame)
            if unseen.empty:
                surviving_trackers.append(tracker)
                continue
            for _, last in unseen.iterrows():
                active_policies = {
                    name: policy
                    for name, policy in tracker.get("policies", {}).items()
                    if policy.get("active")
                }
                if not active_policies:
                    break
                close = _decimal(last["close"], "close")
                high = _decimal(last["high"], "high")
                low = _decimal(last["low"], "low")
                peak = max(_decimal(tracker["peak_price"], "peak_price"), high)
                trough = min(_decimal(tracker["trough_price"], "trough_price"), low)
                tracker["peak_price"] = str(peak)
                tracker["trough_price"] = str(trough)
                mfe_r = (
                    (peak - entry) / risk
                    if tracker["side"] == "BUY"
                    else (entry - trough) / risk
                )
                mae_r = (
                    (entry - trough) / risk
                    if tracker["side"] == "BUY"
                    else (peak - entry) / risk
                )
                r_gate = mfe_r >= Decimal(1)

                for name, policy in active_policies.items():
                    policy["bars_held"] = int(policy.get("bars_held") or 0) + 1
                    stop = _decimal(policy["stop_price"], "policy.stop_price")
                    spec = POLICIES[name]
                    target_r = spec["target_r"]
                    target = (
                        entry + target_r * risk
                        if target_r is not None and tracker["side"] == "BUY"
                        else entry - target_r * risk
                        if target_r is not None
                        else None
                    )
                    exit_price = None
                    exit_reason = ""
                    if tracker["side"] == "BUY":
                        if low <= stop:
                            exit_price, exit_reason = stop, (
                                "trail_stop" if stop != initial_stop else "stop"
                            )
                        elif target is not None and high >= target:
                            exit_price, exit_reason = target, "target"
                    else:
                        if high >= stop:
                            exit_price, exit_reason = stop, (
                                "trail_stop" if stop != initial_stop else "stop"
                            )
                        elif target is not None and low <= target:
                            exit_price, exit_reason = target, "target"

                    horizon = int(tracker.get("horizon_bars") or 0)
                    if (
                        exit_price is None
                        and horizon > 0
                        and policy["bars_held"] >= horizon
                        and not r_gate
                    ):
                        exit_price, exit_reason = close, "horizon"
                    if (
                        exit_price is None
                        and horizon == 0
                        and policy["bars_held"] >= time_stop_bars
                        and not r_gate
                    ):
                        exit_price, exit_reason = close, "time_stop"
                    if exit_price is None and policy["bars_held"] >= max_bars:
                        exit_price, exit_reason = close, "counterfactual_max_bars"

                    if exit_price is None and r_gate:
                        distance = spec["trail_distance_r"]
                        if tracker["side"] == "BUY":
                            stop = max(stop, peak - distance * risk)
                        else:
                            stop = min(stop, trough + distance * risk)
                        policy["stop_price"] = str(stop)
                    if exit_price is not None:
                        policy["active"] = False
                        completed_rows.append(
                            _completion_row(
                                tracker,
                                name,
                                policy,
                                exit_price=exit_price,
                                exit_reason=exit_reason,
                                server_time=server_time,
                                mfe_r=mfe_r,
                                mae_r=mae_r,
                                peak=peak,
                                trough=trough,
                                exit_bar_start=_tracker_bar_iso(last["start"]),
                            )
                        )
                tracker["last_processed_bar_start"] = _tracker_bar_iso(last["start"])
            if any(policy.get("active") for policy in tracker["policies"].values()):
                surviving_trackers.append(tracker)
    except Exception as exc:
        return CounterfactualAdvance(
            trackers=trackers,
            completed_rows=[],
            state_error=f"{type(exc).__name__}: {exc}"[:240],
        )
    return CounterfactualAdvance(
        trackers=surviving_trackers,
        completed_rows=completed_rows,
        state_error=None,
    )


def counterfactual_summary(log_path: Path) -> dict:
    if not log_path.exists():
        return {
            "completed": 0,
            "by_policy": {},
            "by_policy_and_side": {},
            "control": {"comparisons": 0, "mismatches": 0},
        }
    by_policy: dict[str, dict] = {}
    by_policy_and_side: dict[str, dict] = {}
    control = {"comparisons": 0, "mismatches": 0}
    completed = 0

    def bucket_for(mapping: dict[str, dict], key: str) -> dict:
        return mapping.setdefault(
            key,
            {
                "trades": 0,
                "wins": 0,
                "pnl_zar": Decimal(0),
                "delta_zar": Decimal(0),
                "comparisons": 0,
            },
        )

    def update_bucket(bucket: dict, row: dict, pnl: Decimal) -> None:
        bucket["trades"] += 1
        bucket["wins"] += int(pnl > 0)
        bucket["pnl_zar"] += pnl
        if row.get("delta_vs_actual_zar") not in {None, ""}:
            bucket["delta_zar"] += _decimal(
                row["delta_vs_actual_zar"], "delta_vs_actual_zar"
            )
            bucket["comparisons"] += 1

    try:
        with log_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                completed += 1
                policy = str(row.get("policy") or "")
                side = str(row.get("side") or "UNKNOWN")
                pnl = _decimal(row.get("pnl_zar") or 0, "pnl_zar")
                update_bucket(bucket_for(by_policy, policy), row, pnl)
                update_bucket(bucket_for(by_policy_and_side, f"{policy}:{side}"), row, pnl)
                if policy == "target_2r_trail_1r" and row.get("actual_pnl_zar") not in {
                    None,
                    "",
                }:
                    control["comparisons"] += 1
                    delta = abs(_decimal(row.get("delta_vs_actual_zar") or 0, "control_delta"))
                    if (
                        delta > Decimal("0.01")
                        or str(row.get("exit_reason") or "")
                        != str(row.get("actual_exit_reason") or "")
                    ):
                        control["mismatches"] += 1
    except (OSError, RuntimeError):
        return {
            "completed": 0,
            "by_policy": {},
            "by_policy_and_side": {},
            "control": {"comparisons": 0, "mismatches": 0},
            "error": "unreadable",
        }
    def serialize(mapping: dict[str, dict]) -> dict:
        output = {}
        for key, bucket in sorted(mapping.items()):
            output[key] = {
                "trades": bucket["trades"],
                "wins": bucket["wins"],
                "pnl_zar": f"{bucket['pnl_zar']:.4f}",
                "comparisons": bucket["comparisons"],
                "delta_vs_actual_zar": f"{bucket['delta_zar']:.4f}",
            }
        return output

    return {
        "completed": completed,
        "by_policy": serialize(by_policy),
        "by_policy_and_side": serialize(by_policy_and_side),
        "control": control,
    }
