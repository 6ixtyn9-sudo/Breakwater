"""Slice lifecycle: discovered to validated to monitored, with decay.

The book is the single source of monitored slices. Promotion into the book
requires validated walk-forward evidence, enough rows, and the correct
directional edge. Monitored slices decay out when they stop firing, lose
money on paper, or sit in a post-stopout cooldown.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from breakwater.validation import ValidatedSlice, read_validated

BOOK_HEADERS = [
    "slice_id",
    "kind",
    "feature",
    "state",
    "side",
    "status",
    "validated_at",
    "last_signal_bar",
    "paper_trades",
    "paper_wins",
    "paper_losses",
    "paper_pnl_zar",
    "cooldown_until",
    "mean_ret_costadj",
    "n",
    "p_value",
    "horizon_bars",
]

MONITORED = "monitored"
COOLDOWN = "cooldown"
DECAYED = "decayed"

MIN_BOOK_ROWS = 60
LIVE_DECAY_BARS = 96
PNL_DECAY_MIN_TRADES = 5
STOPOUT_COOLDOWN_BARS = 24
BAR_SECONDS = 3600


def read_book(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != BOOK_HEADERS:
            raise RuntimeError("monitored book has an unsupported schema")
        return list(reader)


def _directional_edge(row: ValidatedSlice) -> bool:
    if row.side == "LONG":
        return row.mean_ret_costadj > 0
    return row.mean_ret_costadj < 0


def sync_book(
    *,
    validated_path: Path,
    book_path: Path,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    now_epoch = int(now.timestamp())
    validated = [row for row in read_validated(validated_path) if row.validated]
    existing = {row["slice_id"]: row for row in read_book(book_path)}
    rows: list[dict] = []
    summary = {"validated": len(validated), "monitored": 0, "decayed": 0, "cooldown": 0}
    for row in validated:
        prior = existing.get(row.slice_id)
        if row.n < MIN_BOOK_ROWS or not _directional_edge(row):
            continue
        cooldown_until = int(prior.get("cooldown_until") or 0) if prior else 0
        if cooldown_until > now_epoch:
            status = COOLDOWN
            summary["cooldown"] += 1
        elif prior and prior.get("status") == MONITORED:
            last_signal = int(prior.get("last_signal_bar") or 0)
            paper_trades = int(prior.get("paper_trades") or 0)
            paper_pnl = float(prior.get("paper_pnl_zar") or 0)
            stale = (
                last_signal > 0
                and now_epoch - last_signal > LIVE_DECAY_BARS * BAR_SECONDS
            )
            losing = paper_trades >= PNL_DECAY_MIN_TRADES and paper_pnl < 0
            if stale or losing:
                status = DECAYED
                summary["decayed"] += 1
            else:
                status = MONITORED
                summary["monitored"] += 1
        else:
            status = MONITORED
            summary["monitored"] += 1
        rows.append({
            "slice_id": row.slice_id,
            "kind": row.kind,
            "feature": row.feature,
            "state": str(row.state),
            "side": row.side,
            "status": status,
            "validated_at": now.isoformat(),
            "last_signal_bar": prior.get("last_signal_bar", "") if prior else "",
            "paper_trades": prior.get("paper_trades", "0") if prior else "0",
            "paper_wins": prior.get("paper_wins", "0") if prior else "0",
            "paper_losses": prior.get("paper_losses", "0") if prior else "0",
            "paper_pnl_zar": prior.get("paper_pnl_zar", "0") if prior else "0",
            "cooldown_until": prior.get("cooldown_until", "") if prior else "",
            "mean_ret_costadj": f"{row.mean_ret_costadj:.6f}",
            "n": str(row.n),
            "p_value": f"{row.p_value:.6f}",
            "horizon_bars": str(row.horizon_bars),
        })
    book_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=book_path.name + ".", suffix=".tmp", dir=book_path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=BOOK_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, book_path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
    return summary


def apply_signal_feedback(
    book_path: Path,
    slice_id: str,
    *,
    bar_epoch: int,
    outcome: str,
    pnl_zar: float,
    now: datetime | None = None,
) -> None:
    now = now or datetime.now(timezone.utc)
    rows = read_book(book_path)
    for row in rows:
        if row["slice_id"] != slice_id:
            continue
        row["last_signal_bar"] = str(bar_epoch)
        trades = int(row.get("paper_trades") or 0) + 1
        row["paper_trades"] = str(trades)
        row["paper_pnl_zar"] = f"{(float(row.get('paper_pnl_zar') or 0) + pnl_zar):.4f}"
        if outcome == "win":
            row["paper_wins"] = str(int(row.get("paper_wins") or 0) + 1)
            row["cooldown_until"] = ""
        else:
            row["paper_losses"] = str(int(row.get("paper_losses") or 0) + 1)
            row["cooldown_until"] = str(bar_epoch + STOPOUT_COOLDOWN_BARS * BAR_SECONDS)
            row["status"] = COOLDOWN
    _write_book(book_path, rows)


def _write_book(path: Path, rows: list[dict]) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=BOOK_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def read_cooldown_journal(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
        if isinstance(payload, list):
            return payload
        return []
    except (OSError, json.JSONDecodeError):
        return []
