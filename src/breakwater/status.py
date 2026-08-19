"""Bounded operational status records suitable for Git durability."""

from __future__ import annotations

import csv
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HEADERS = ["timestamp_utc", "stage", "mode", "detail"]


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
        "detail": str(detail)[:4000],
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
