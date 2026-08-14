"""Transactional local event ledger; VALR remains account-state authority."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from breakwater.config import INITIAL_EQUITY_ZAR
from breakwater.decimal_utils import D


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=15)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    occurred_at_utc TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    strategy_id TEXT,
                    pair TEXT,
                    amount_zar TEXT,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_kind_time
                    ON events(kind, occurred_at_utc);
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO metadata(key, value) VALUES('high_water_zar', ?)",
                (str(INITIAL_EQUITY_ZAR),),
            )

    def append(
        self,
        *,
        event_id: str,
        kind: str,
        payload: dict,
        occurred_at: datetime | None = None,
        strategy_id: str | None = None,
        pair: str | None = None,
        amount_zar: Decimal | None = None,
    ) -> bool:
        if not event_id or not kind:
            raise ValueError("event_id and kind are required")
        timestamp = occurred_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO events(
                        event_id, occurred_at_utc, kind, strategy_id,
                        pair, amount_zar, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        timestamp.astimezone(timezone.utc).isoformat(),
                        kind,
                        strategy_id,
                        pair.upper() if pair else None,
                        str(amount_zar) if amount_zar is not None else None,
                        json.dumps(payload, separators=(",", ":"), sort_keys=True),
                    ),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def pnl_since(self, since: datetime) -> Decimal:
        if since.tzinfo is None:
            raise ValueError("since must be timezone-aware")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT amount_zar FROM events
                WHERE kind = 'realized_pnl'
                  AND occurred_at_utc >= ?
                  AND amount_zar IS NOT NULL
                """,
                (since.astimezone(timezone.utc).isoformat(),),
            ).fetchall()
        return sum((D(row[0]) for row in rows), Decimal(0))

    def daily_pnl(self, now: datetime | None = None) -> Decimal:
        current = now or datetime.now(timezone.utc)
        start = current.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return self.pnl_since(start)

    def seven_day_pnl(self, now: datetime | None = None) -> Decimal:
        current = now or datetime.now(timezone.utc)
        return self.pnl_since(current.astimezone(timezone.utc) - timedelta(days=7))

    def high_water(self) -> Decimal:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key = 'high_water_zar'"
            ).fetchone()
        if row is None:
            raise RuntimeError("ledger high-water metadata is missing")
        return D(row[0])

    def observe_equity(self, equity_zar: Decimal) -> Decimal:
        if equity_zar <= 0:
            raise ValueError("equity must be positive")
        high_water = max(self.high_water(), equity_zar)
        with self._connect() as connection:
            connection.execute(
                "UPDATE metadata SET value = ? WHERE key = 'high_water_zar'",
                (str(high_water),),
            )
        return high_water

    def recent_events(self, limit: int = 100) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, occurred_at_utc, kind, strategy_id,
                       pair, amount_zar, payload_json
                FROM events ORDER BY occurred_at_utc DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "event_id": row[0],
                "occurred_at_utc": row[1],
                "kind": row[2],
                "strategy_id": row[3],
                "pair": row[4],
                "amount_zar": row[5],
                "payload": json.loads(row[6]),
            }
            for row in rows
        ]
