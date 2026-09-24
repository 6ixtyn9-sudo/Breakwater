"""Bounded operational status records suitable for Git durability."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HEADERS = ["timestamp_utc", "stage", "mode", "detail"]

# Scan payloads are JSON and routinely far larger than the old 4000-char cap
# (the green-gate blocked-slice map alone is thousands of characters). 64 000
# chars holds every real payload whole; past that the bulkiest keys go, named.
DETAIL_CHAR_LIMIT = 64_000
DROPPED_KEYS_SHOWN = 20


def _fit_detail(detail: object) -> str:
    """Serialize ``detail`` to bounded JSON text that names its own loss.

    A payload that fits is stored verbatim. One that does not is stored with
    its bulkiest keys dropped, largest first, and a ``_truncated`` block
    recording the dropped keys (bounded at DROPPED_KEYS_SHOWN names), the
    dropped count and the original length - so the column is always valid
    JSON that says what it left out, never text cut mid-value. Oversized
    non-JSON strings can only be hard-bounded at the limit.
    """
    if isinstance(detail, str):
        text = detail
    else:
        text = json.dumps(detail, sort_keys=True, default=str)
    if len(text) <= DETAIL_CHAR_LIMIT:
        return text
    try:
        payload = json.loads(text)
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        return text[:DETAIL_CHAR_LIMIT]
    original_length = len(text)

    def pair_len(key: object) -> int:
        # Exact rendered length of one "<key>": <value> pair (": " included),
        # so the fit loop can measure without re-rendering the payload.
        return (
            len(json.dumps(str(key)))
            + 2
            + len(json.dumps(payload[key], sort_keys=True, default=str))
        )

    sizes = {key: pair_len(key) for key in payload}
    keys = sorted(payload, key=lambda key: (sizes[key], str(key)))
    total_parts = sum(sizes.values())
    dropped: list[str] = []
    while True:
        summary = {
            "dropped_keys": sorted(dropped)[:DROPPED_KEYS_SHOWN],
            "dropped_count": len(dropped),
            "original_length": original_length,
        }
        summary_part = (
            len(json.dumps("_truncated"))
            + 2
            + len(json.dumps(summary, sort_keys=True, default=str))
        )
        # braces + every pair + ", " between the pairs (kept keys + summary).
        if 2 + total_parts + summary_part + 2 * len(keys) <= DETAIL_CHAR_LIMIT:
            fitted = {key: payload[key] for key in keys}
            fitted["_truncated"] = summary
            rendered = json.dumps(fitted, sort_keys=True, default=str)
            if len(rendered) <= DETAIL_CHAR_LIMIT:
                return rendered
        if not keys:
            # Summary alone always fits: it is a fixed, tiny shape.
            return json.dumps({"_truncated": summary}, sort_keys=True, default=str)[
                :DETAIL_CHAR_LIMIT
            ]
        dropped_key = keys.pop()  # bulkiest remaining key goes first
        dropped.append(dropped_key)
        total_parts -= sizes[dropped_key]


def append_status(path: Path, stage: str, mode: str, detail: str = "", keep: int = 500) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if path.exists():
        try:
            with path.open(newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames != HEADERS:
                    raise RuntimeError("status file has an unsupported schema")
                rows = list(reader)
        except (OSError, csv.Error) as exc:
            raise RuntimeError(f"status file is unreadable: {exc}") from exc
    rows.append({
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": str(stage),
        "mode": str(mode),
        "detail": _fit_detail(detail),
    })
    rows = rows[-keep:]
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
