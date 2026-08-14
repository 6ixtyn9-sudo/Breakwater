"""Dynamic full-universe ingestion from VALR.

Every active VALR spot pair and every VALR Perps symbol is ingested on each
research pass and ranked by liquidity where the venue exposes it. No symbol
list is compiled into this repository: the venue defines the universe.
"""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from breakwater.market import MarketStateError
from breakwater.valr import ValrClient

STABLE_BASES = {
    "USDT", "USDC", "TUSD", "DAI", "BUSD", "FDUSD", "USDP", "PYUSD", "EURS", "EURT",
}


UNIVERSE_HEADERS = [
    "symbol",
    "kind",
    "base",
    "quote",
    "active",
    "liquidity_rank",
    "quote_volume",
    "mark_price",
    "max_leverage",
    "min_notional",
    "min_margin",
    "as_of",
]


@dataclass(frozen=True)
class UniverseRow:
    symbol: str
    kind: str
    base: str
    quote: str
    active: bool
    liquidity_rank: int
    quote_volume: Decimal
    mark_price: Decimal
    max_leverage: Decimal
    min_notional: Decimal
    min_margin: Decimal
    as_of: str


@dataclass(frozen=True)
class UniverseSnapshot:
    rows: tuple[UniverseRow, ...]
    as_of: str

    def symbols(self, kind: str | None = None) -> list[str]:
        return [
            row.symbol for row in self.rows
            if kind is None or row.kind == kind
        ]

    def ranked(self, kind: str, limit: int) -> list[str]:
        return [
            row.symbol
            for row in sorted(self.rows, key=lambda row: row.liquidity_rank)
            if row.kind == kind
        ][:limit]

    def top(self, limit_per_kind: int) -> list[str]:
        picked = []
        for kind in ("SPOT", "PERP"):
            picked.extend(self.ranked(kind, limit_per_kind))
        return picked


def _volume_sort_key(row: UniverseRow) -> Decimal:
    return row.quote_volume


def ingest_universe(client: ValrClient) -> UniverseSnapshot:
    as_of = datetime.now(timezone.utc).isoformat()
    spot_rows: list[UniverseRow] = []
    perp_rows: list[UniverseRow] = []
    try:
        spot_specs = [
            spec for spec in client.pairs() if spec.active and spec.pair_type.value == "SPOT"
        ]
    except Exception as exc:
        raise MarketStateError(f"VALR spot pair metadata is unavailable: {exc}") from exc
    if not spot_specs:
        raise MarketStateError("VALR returned no active spot pairs")

    volume_by_symbol: dict[str, Decimal] = {}
    try:
        for summary in client.market_summaries():
            volume_by_symbol[summary.pair] = summary.quote_volume
    except Exception:
        volume_by_symbol = {}

    for spec in spot_specs:
        if spec.base_currency in STABLE_BASES:
            continue
        volume = volume_by_symbol.get(spec.symbol, Decimal(0))
        spot_rows.append(UniverseRow(
            symbol=spec.symbol,
            kind="SPOT",
            base=spec.base_currency,
            quote=spec.quote_currency,
            active=True,
            liquidity_rank=0,
            quote_volume=volume,
            mark_price=Decimal(0),
            max_leverage=Decimal(0),
            min_notional=spec.min_quote,
            min_margin=Decimal(0),
            as_of=as_of,
        ))
    spot_rows.sort(key=lambda row: (-row.quote_volume, row.symbol))
    for index, row in enumerate(spot_rows, start=1):
        spot_rows[index - 1] = UniverseRow(
            symbol=row.symbol,
            kind=row.kind,
            base=row.base,
            quote=row.quote,
            active=row.active,
            liquidity_rank=index,
            quote_volume=row.quote_volume,
            mark_price=row.mark_price,
            max_leverage=row.max_leverage,
            min_notional=row.min_notional,
            min_margin=row.min_margin,
            as_of=row.as_of,
        )

    try:
        perp_symbols = client.perps_symbol_info()
    except Exception as exc:
        raise MarketStateError(f"VALR perps symbol metadata is unavailable: {exc}") from exc
    for symbol in perp_symbols:
        perp_rows.append(UniverseRow(
            symbol=symbol.pair,
            kind="PERP",
            base=symbol.base_asset,
            quote="USDC",
            active=True,
            liquidity_rank=0,
            quote_volume=Decimal(0),
            mark_price=symbol.mark_price,
            max_leverage=symbol.max_leverage,
            min_notional=symbol.min_notional,
            min_margin=symbol.min_margin,
            as_of=as_of,
        ))
    perp_rows.sort(key=lambda row: row.symbol)
    for index, row in enumerate(perp_rows, start=1):
        perp_rows[index - 1] = UniverseRow(
            symbol=row.symbol,
            kind=row.kind,
            base=row.base,
            quote=row.quote,
            active=row.active,
            liquidity_rank=index,
            quote_volume=row.quote_volume,
            mark_price=row.mark_price,
            max_leverage=row.max_leverage,
            min_notional=row.min_notional,
            min_margin=row.min_margin,
            as_of=row.as_of,
        )

    snapshot = UniverseSnapshot(rows=tuple(spot_rows + perp_rows), as_of=as_of)
    if not snapshot.rows:
        raise MarketStateError("universe snapshot is empty")
    return snapshot


def write_universe(path: Path, snapshot: UniverseSnapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(
        (asdict(row) for row in snapshot.rows),
        key=lambda row: (row["kind"], row["liquidity_rank"]),
    )
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=UNIVERSE_HEADERS)
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


def read_universe(path: Path) -> UniverseSnapshot | None:
    if not path.exists():
        return None
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != UNIVERSE_HEADERS:
                raise RuntimeError("universe file has an unsupported schema")
            rows = []
            for row in reader:
                rows.append(UniverseRow(
                    symbol=str(row["symbol"]),
                    kind=str(row["kind"]),
                    base=str(row["base"]),
                    quote=str(row["quote"]),
                    active=row["active"] == "True",
                    liquidity_rank=int(row["liquidity_rank"]),
                    quote_volume=Decimal(row["quote_volume"]),
                    mark_price=Decimal(row["mark_price"]),
                    max_leverage=Decimal(row["max_leverage"]),
                    min_notional=Decimal(row["min_notional"]),
                    min_margin=Decimal(row["min_margin"]),
                    as_of=str(row["as_of"]),
                ))
            return UniverseSnapshot(rows=tuple(rows), as_of=rows[0].as_of if rows else "")
    except (OSError, KeyError, ValueError) as exc:
        raise RuntimeError(f"universe file is unreadable: {exc}") from exc
