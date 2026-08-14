"""Git-durable bounded risk state; broker snapshots remain authoritative."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from breakwater.config import INITIAL_EQUITY_ZAR
from breakwater.decimal_utils import D

SCHEMA = "breakwater.risk.v1"


class RiskStateStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict:
        if not self.path.exists():
            return {
                "schema_version": SCHEMA,
                "high_water_zar": str(INITIAL_EQUITY_ZAR),
                "realized_pnl_events": [],
            }
        try:
            payload = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"risk state is unreadable: {exc}") from exc
        if payload.get("schema_version") != SCHEMA:
            raise RuntimeError("risk state schema is unsupported")
        if not isinstance(payload.get("realized_pnl_events"), list):
            raise RuntimeError("risk state P&L events must be a list")
        D(payload.get("high_water_zar"), field="high_water_zar")
        return payload

    def _write(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.path)

    def observe_equity(self, equity_zar: Decimal) -> Decimal:
        payload = self.load()
        high_water = max(D(payload["high_water_zar"]), equity_zar)
        payload["high_water_zar"] = str(high_water)
        self._write(payload)
        return high_water

    def append_realized_pnl(
        self, event_id: str, amount_zar: Decimal, occurred_at: datetime
    ) -> bool:
        if occurred_at.tzinfo is None:
            raise ValueError("realized P&L timestamp must be timezone-aware")
        payload = self.load()
        events = payload["realized_pnl_events"]
        if any(str(row.get("event_id")) == event_id for row in events):
            return False
        events.append({
            "event_id": event_id,
            "amount_zar": str(amount_zar),
            "occurred_at_utc": occurred_at.astimezone(timezone.utc).isoformat(),
        })
        cutoff = datetime.now(timezone.utc) - timedelta(days=35)
        payload["realized_pnl_events"] = [
            row for row in events
            if datetime.fromisoformat(
                str(row["occurred_at_utc"]).replace("Z", "+00:00")
            ) >= cutoff
        ]
        self._write(payload)
        return True

    def pnl_since(self, since: datetime) -> Decimal:
        total = Decimal(0)
        for row in self.load()["realized_pnl_events"]:
            stamp = datetime.fromisoformat(
                str(row["occurred_at_utc"]).replace("Z", "+00:00")
            )
            if stamp >= since:
                total += D(row["amount_zar"])
        return total

    def daily_pnl(self, now: datetime) -> Decimal:
        start = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return self.pnl_since(start)

    def seven_day_pnl(self, now: datetime) -> Decimal:
        return self.pnl_since(now.astimezone(timezone.utc) - timedelta(days=7))
