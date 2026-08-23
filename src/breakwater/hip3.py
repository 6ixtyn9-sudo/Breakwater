"""Dedicated Hyperliquid HIP-3 DEX and instrument discovery.

HIP-3 is intentionally isolated from the native crypto PERP universe. This
module discovers builder DEXs and their markets directly from Hyperliquid and
persists a separate snapshot. It performs no strategy promotion or execution.
"""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import requests

from breakwater.hyperliquid import MAINNET_API_URL
from breakwater.perp_venue import PerpVenueError

HIP3_UNIVERSE_HEADERS = [
    "dex",
    "dex_full_name",
    "deployer",
    "oracle_updater",
    "coin",
    "collateral_token",
    "active",
    "liquidity_rank",
    "day_notional_volume",
    "mark_price",
    "oracle_price",
    "previous_day_price",
    "oracle_mark_deviation_fraction",
    "funding_rate",
    "open_interest",
    "max_leverage",
    "size_decimals",
    "margin_mode",
    "growth_mode",
    "as_of",
]


@dataclass(frozen=True)
class Hip3Dex:
    name: str
    full_name: str
    deployer: str
    oracle_updater: str


@dataclass(frozen=True)
class Hip3UniverseRow:
    dex: str
    dex_full_name: str
    deployer: str
    oracle_updater: str
    coin: str
    collateral_token: int
    active: bool
    liquidity_rank: int
    day_notional_volume: Decimal
    mark_price: Decimal
    oracle_price: Decimal
    previous_day_price: Decimal
    oracle_mark_deviation_fraction: Decimal
    funding_rate: Decimal
    open_interest: Decimal
    max_leverage: Decimal
    size_decimals: int
    margin_mode: str
    growth_mode: str
    as_of: str


@dataclass(frozen=True)
class Hip3UniverseSnapshot:
    dexs: tuple[Hip3Dex, ...]
    rows: tuple[Hip3UniverseRow, ...]
    as_of: str


class HyperliquidHip3Discovery:
    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        base_url: str = MAINNET_API_URL,
        timeout: int = 20,
    ):
        self.session = session or requests.Session()
        self.info_url = f"{base_url}/info"
        self.timeout = timeout

    def _post(self, payload: dict):
        try:
            response = self.session.post(self.info_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise PerpVenueError("Hyperliquid HIP-3 info request failed") from exc
        except (TypeError, ValueError) as exc:
            raise PerpVenueError("Hyperliquid HIP-3 response is not valid JSON") from exc

    @staticmethod
    def _decimal(value, field: str) -> Decimal:
        try:
            number = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise PerpVenueError(f"HIP-3 {field} is not a decimal") from exc
        if not number.is_finite():
            raise PerpVenueError(f"HIP-3 {field} must be finite")
        return number

    def dexs(self) -> tuple[Hip3Dex, ...]:
        payload = self._post({"type": "perpDexs"})
        if not isinstance(payload, list):
            raise PerpVenueError("Hyperliquid perpDexs response is malformed")
        dexs: list[Hip3Dex] = []
        for row in payload:
            if row is None:
                continue
            if not isinstance(row, dict):
                raise PerpVenueError("Hyperliquid perpDexs row is malformed")
            name = str(row.get("name") or "").strip()
            if not name or ":" in name:
                raise PerpVenueError("Hyperliquid HIP-3 DEX name is invalid")
            dexs.append(
                Hip3Dex(
                    name=name,
                    full_name=str(row.get("fullName") or name),
                    deployer=str(row.get("deployer") or ""),
                    oracle_updater=str(row.get("oracleUpdater") or row.get("deployer") or ""),
                )
            )
        return tuple(sorted(dexs, key=lambda dex: dex.name))

    def discover(self) -> Hip3UniverseSnapshot:
        observed = datetime.now(timezone.utc).isoformat()
        dexs = self.dexs()
        rows: list[Hip3UniverseRow] = []
        for dex in dexs:
            payload = self._post({"type": "metaAndAssetCtxs", "dex": dex.name})
            if not isinstance(payload, list) or len(payload) != 2:
                raise PerpVenueError(f"HIP-3 metadata is malformed for DEX {dex.name}")
            meta, contexts = payload
            universe = meta.get("universe") if isinstance(meta, dict) else None
            collateral_token = meta.get("collateralToken") if isinstance(meta, dict) else None
            if not isinstance(universe, list) or not isinstance(contexts, list):
                raise PerpVenueError(f"HIP-3 metadata schema is invalid for DEX {dex.name}")
            if len(universe) != len(contexts):
                raise PerpVenueError(f"HIP-3 metadata is misaligned for DEX {dex.name}")
            try:
                collateral_token = int(collateral_token)
            except (TypeError, ValueError) as exc:
                raise PerpVenueError(f"HIP-3 collateral token is invalid for DEX {dex.name}") from exc

            dex_rows: list[Hip3UniverseRow] = []
            for instrument, context in zip(universe, contexts, strict=True):
                if not isinstance(instrument, dict) or not isinstance(context, dict):
                    raise PerpVenueError(f"HIP-3 instrument row is malformed for DEX {dex.name}")
                coin = str(instrument.get("name") or "").strip()
                if not coin.startswith(f"{dex.name}:"):
                    raise PerpVenueError(
                        f"HIP-3 instrument {coin!r} does not preserve DEX prefix {dex.name!r}"
                    )
                mark = self._decimal(context.get("markPx"), f"{coin}.markPx")
                oracle = self._decimal(context.get("oraclePx"), f"{coin}.oraclePx")
                deviation = abs(mark - oracle) / oracle if oracle > 0 else Decimal("Infinity")
                try:
                    size_decimals = int(instrument["szDecimals"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise PerpVenueError(f"HIP-3 size precision is invalid for {coin}") from exc
                dex_rows.append(
                    Hip3UniverseRow(
                        dex=dex.name,
                        dex_full_name=dex.full_name,
                        deployer=dex.deployer,
                        oracle_updater=dex.oracle_updater,
                        coin=coin,
                        collateral_token=collateral_token,
                        active=not bool(instrument.get("isDelisted", False)),
                        liquidity_rank=0,
                        day_notional_volume=self._decimal(
                            context.get("dayNtlVlm") or 0, f"{coin}.dayNtlVlm"
                        ),
                        mark_price=mark,
                        oracle_price=oracle,
                        previous_day_price=self._decimal(
                            context.get("prevDayPx") or 0, f"{coin}.prevDayPx"
                        ),
                        oracle_mark_deviation_fraction=deviation,
                        funding_rate=self._decimal(
                            context.get("funding") or 0, f"{coin}.funding"
                        ),
                        open_interest=self._decimal(
                            context.get("openInterest") or 0, f"{coin}.openInterest"
                        ),
                        max_leverage=self._decimal(
                            instrument.get("maxLeverage") or 1, f"{coin}.maxLeverage"
                        ),
                        size_decimals=size_decimals,
                        margin_mode=str(
                            instrument.get("marginMode")
                            or ("isolated" if instrument.get("onlyIsolated") else "cross")
                        ),
                        growth_mode=str(instrument.get("growthMode") or "disabled"),
                        as_of=observed,
                    )
                )
            dex_rows.sort(key=lambda row: (-row.day_notional_volume, row.coin))
            for rank, row in enumerate(dex_rows, start=1):
                payload_row = asdict(row)
                payload_row["liquidity_rank"] = rank
                rows.append(Hip3UniverseRow(**payload_row))
        return Hip3UniverseSnapshot(dexs=dexs, rows=tuple(rows), as_of=observed)


def read_hip3_universe(path: Path) -> Hip3UniverseSnapshot | None:
    if not path.exists():
        return None
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != HIP3_UNIVERSE_HEADERS:
                raise RuntimeError("HIP-3 universe file has an unsupported schema")
            rows = []
            dexs: dict[str, Hip3Dex] = {}
            for raw in reader:
                row = Hip3UniverseRow(
                    dex=raw["dex"],
                    dex_full_name=raw["dex_full_name"],
                    deployer=raw["deployer"],
                    oracle_updater=raw["oracle_updater"],
                    coin=raw["coin"],
                    collateral_token=int(raw["collateral_token"]),
                    active=raw["active"] == "True",
                    liquidity_rank=int(raw["liquidity_rank"]),
                    day_notional_volume=Decimal(raw["day_notional_volume"]),
                    mark_price=Decimal(raw["mark_price"]),
                    oracle_price=Decimal(raw["oracle_price"]),
                    previous_day_price=Decimal(raw["previous_day_price"]),
                    oracle_mark_deviation_fraction=Decimal(
                        raw["oracle_mark_deviation_fraction"]
                    ),
                    funding_rate=Decimal(raw["funding_rate"]),
                    open_interest=Decimal(raw["open_interest"]),
                    max_leverage=Decimal(raw["max_leverage"]),
                    size_decimals=int(raw["size_decimals"]),
                    margin_mode=raw["margin_mode"],
                    growth_mode=raw["growth_mode"],
                    as_of=raw["as_of"],
                )
                rows.append(row)
                dexs.setdefault(
                    row.dex,
                    Hip3Dex(
                        name=row.dex,
                        full_name=row.dex_full_name,
                        deployer=row.deployer,
                        oracle_updater=row.oracle_updater,
                    ),
                )
            as_of = rows[0].as_of if rows else ""
            return Hip3UniverseSnapshot(
                dexs=tuple(sorted(dexs.values(), key=lambda dex: dex.name)),
                rows=tuple(rows),
                as_of=as_of,
            )
    except (OSError, KeyError, ValueError, InvalidOperation) as exc:
        raise RuntimeError(f"HIP-3 universe file is unreadable: {exc}") from exc


def write_hip3_universe(path: Path, snapshot: Hip3UniverseSnapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HIP3_UNIVERSE_HEADERS)
            writer.writeheader()
            writer.writerows(asdict(row) for row in snapshot.rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
