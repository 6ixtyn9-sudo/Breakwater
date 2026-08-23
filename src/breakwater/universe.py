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
    "venue",
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
    venue: str = ""


@dataclass(frozen=True)
class UniverseSnapshot:
    rows: tuple[UniverseRow, ...]
    as_of: str

    def symbols(self, kind: str | None = None) -> list[str]:
        return [
            row.symbol for row in self.rows
            if kind is None or row.kind == kind
        ]

    def ranked(self, kind: str, limit: int, *, mappable_only: bool = True) -> list[str]:
        """Return symbols of ``kind`` inside the top-``limit`` volume window.

        Rank window (not tail-fill): take the first ``limit`` names by
        liquidity_rank, then drop unmappable PERPs (HIP-3 ``xyz:``).
        ``max_pairs=60`` means the venue's top 60, minus builder names —
        typically ~36 crypto — not 60 crypto dug from rank 80 dust.
        """
        window = [
            row.symbol
            for row in sorted(self.rows, key=lambda row: row.liquidity_rank)
            if row.kind == kind
        ][:limit]
        if not (kind == "PERP" and mappable_only):
            return window
        from breakwater.perpdata import pair_to_coin

        return [symbol for symbol in window if pair_to_coin(symbol) is not None]

    def top(self, limit_per_kind: int) -> list[str]:
        picked = []
        for kind in ("SPOT", "PERP"):
            picked.extend(self.ranked(kind, limit_per_kind))
        return picked


def ingest_universe(client: ValrClient, *, perp_venue=None) -> UniverseSnapshot:
    """Build VALR spot plus direct-Hyperliquid native PERP universe.

    ``perp_venue`` is injected to keep tests and offline tools deterministic.
    Production passes ``HyperliquidReadOnlyVenue``; the VALR symbol endpoint is
    retained only as a compatibility fallback for callers that omit it.
    """
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
            venue="VALR",
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
            venue=row.venue,
        )

    if perp_venue is not None:
        try:
            perp_instruments = perp_venue.instruments()
        except Exception as exc:
            raise MarketStateError(
                f"Hyperliquid native perp metadata is unavailable: {exc}"
            ) from exc
        for instrument in perp_instruments:
            if not instrument.active or ":" in instrument.coin:
                continue
            perp_rows.append(UniverseRow(
                symbol=instrument.symbol,
                kind="PERP",
                base=instrument.coin.upper(),
                quote="USDC",
                active=True,
                liquidity_rank=0,
                quote_volume=instrument.day_notional_volume,
                mark_price=instrument.mark_price,
                max_leverage=instrument.max_leverage,
                min_notional=instrument.min_notional,
                min_margin=(
                    instrument.min_notional / instrument.max_leverage
                    if instrument.max_leverage > 0 else instrument.min_notional
                ),
                as_of=as_of,
                venue="HYPERLIQUID",
            ))
    else:
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
                quote_volume=symbol.volume,
                mark_price=symbol.mark_price,
                max_leverage=symbol.max_leverage,
                min_notional=symbol.min_notional,
                min_margin=symbol.min_margin,
                as_of=as_of,
                venue="VALR",
            ))
    perp_rows.sort(key=lambda row: (-row.quote_volume, row.symbol))
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
            venue=row.venue,
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
            legacy_headers = UNIVERSE_HEADERS[:-1]
            fields = tuple(reader.fieldnames or ())
            if fields not in {tuple(UNIVERSE_HEADERS), tuple(legacy_headers)}:
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
                    venue=str(row.get("venue") or "LEGACY"),
                ))
            return UniverseSnapshot(rows=tuple(rows), as_of=rows[0].as_of if rows else "")
    except (OSError, KeyError, ValueError) as exc:
        raise RuntimeError(f"universe file is unreadable: {exc}") from exc


def has_direct_hyperliquid_perps(snapshot: UniverseSnapshot) -> bool:
    perps = [row for row in snapshot.rows if row.kind == "PERP"]
    return bool(perps) and all(row.venue == "HYPERLIQUID" for row in perps)


def is_legacy_universe(snapshot: UniverseSnapshot) -> bool:
    """Detect a universe file written before perp-volume capture.

    Such files rank the perp universe alphabetically instead of by venue
    volume, silently degrading research targets. Any snapshot whose perp
    rows all carry zero volume is treated as legacy and re-ingested.
    """
    perps = [row for row in snapshot.rows if row.kind == "PERP"]
    return bool(perps) and all(row.quote_volume == 0 for row in perps)

