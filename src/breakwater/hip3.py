"""Dedicated Hyperliquid HIP-3 DEX and instrument discovery.

HIP-3 is intentionally isolated from the native crypto PERP universe. This
module discovers builder DEXs and their markets directly from Hyperliquid and
persists a separate snapshot. It performs no strategy promotion or execution.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from datetime import time as _dt_time
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
    "annotation_category",
    "annotation_keywords",
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
    annotation_category: str = ""
    annotation_keywords: str = ""


@dataclass(frozen=True)
class Hip3UniverseSnapshot:
    dexs: tuple[Hip3Dex, ...]
    rows: tuple[Hip3UniverseRow, ...]
    as_of: str
    # Raw perpDexs rows (feeRecipient, funding multipliers, OI caps, ...).
    # Empty when a snapshot is rebuilt from the universe CSV alone.
    dex_metadata: tuple[dict, ...] = ()


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

    def _perp_dexs_payload(self) -> list[dict]:
        payload = self._post({"type": "perpDexs"})
        if not isinstance(payload, list):
            raise PerpVenueError("Hyperliquid perpDexs response is malformed")
        rows: list[dict] = []
        for row in payload:
            if row is None:
                continue
            if not isinstance(row, dict):
                raise PerpVenueError("Hyperliquid perpDexs row is malformed")
            name = str(row.get("name") or "").strip()
            if not name or ":" in name:
                raise PerpVenueError("Hyperliquid HIP-3 DEX name is invalid")
            rows.append(row)
        return rows

    @staticmethod
    def _dex_from_row(row: dict) -> Hip3Dex:
        name = str(row.get("name") or "").strip()
        return Hip3Dex(
            name=name,
            full_name=str(row.get("fullName") or name),
            deployer=str(row.get("deployer") or ""),
            oracle_updater=str(row.get("oracleUpdater") or row.get("deployer") or ""),
        )

    def dexs(self) -> tuple[Hip3Dex, ...]:
        return tuple(
            sorted(
                (self._dex_from_row(row) for row in self._perp_dexs_payload()),
                key=lambda dex: dex.name,
            )
        )

    def annotations(self) -> dict[str, tuple[str, str]]:
        payload = self._post({"type": "perpConciseAnnotations"})
        if not isinstance(payload, list):
            raise PerpVenueError("Hyperliquid perpConciseAnnotations response is malformed")
        annotations: dict[str, tuple[str, str]] = {}
        for row in payload:
            if not isinstance(row, list) or len(row) != 2 or not isinstance(row[1], dict):
                raise PerpVenueError("Hyperliquid concise annotation row is malformed")
            coin = str(row[0] or "").strip()
            if not coin:
                raise PerpVenueError("Hyperliquid concise annotation coin is missing")
            detail = row[1]
            category = str(detail.get("category") or "").strip()
            keywords_raw = detail.get("keywords") or []
            if not isinstance(keywords_raw, list):
                raise PerpVenueError(f"Hyperliquid annotation keywords are malformed for {coin}")
            keywords = ",".join(str(value).strip() for value in keywords_raw if str(value).strip())
            annotations[coin] = (category, keywords)
        return annotations

    def discover(self) -> Hip3UniverseSnapshot:
        observed = datetime.now(timezone.utc).isoformat()
        # Fetch perpDexs once and reuse the raw rows: dex identity for the
        # snapshot plus the full operator metadata persisted for evidence.
        raw_dex_rows = self._perp_dexs_payload()
        dexs = tuple(
            sorted((self._dex_from_row(row) for row in raw_dex_rows), key=lambda dex: dex.name)
        )
        annotations = self.annotations()
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
                        annotation_category=annotations.get(coin, ("", ""))[0],
                        annotation_keywords=annotations.get(coin, ("", ""))[1],
                    )
                )
            dex_rows.sort(key=lambda row: (-row.day_notional_volume, row.coin))
            for rank, row in enumerate(dex_rows, start=1):
                payload_row = asdict(row)
                payload_row["liquidity_rank"] = rank
                rows.append(Hip3UniverseRow(**payload_row))
        return Hip3UniverseSnapshot(
            dexs=dexs,
            rows=tuple(rows),
            as_of=observed,
            dex_metadata=tuple(raw_dex_rows),
        )


def read_hip3_universe(path: Path) -> Hip3UniverseSnapshot | None:
    if not path.exists():
        return None
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            legacy_headers = [
                name
                for name in HIP3_UNIVERSE_HEADERS
                if name not in {"annotation_category", "annotation_keywords"}
            ]
            fields = tuple(reader.fieldnames or ())
            if fields not in {tuple(HIP3_UNIVERSE_HEADERS), tuple(legacy_headers)}:
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
                    annotation_category=raw.get("annotation_category") or "",
                    annotation_keywords=raw.get("annotation_keywords") or "",
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


def write_hip3_dexs(path: Path, snapshot: Hip3UniverseSnapshot) -> None:
    """Persist the raw perpDexs operator metadata as a committed artifact.

    The universe CSV only carries the identity fields research needs; the full
    response (feeRecipient, per-asset funding multipliers, streaming OI caps,
    margin table ids) is evidence for the HIP-3 cost/oracle blockers and is
    stored verbatim so no field is lost to schema drift.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(
                {"as_of": snapshot.as_of, "dexs": list(snapshot.dex_metadata)},
                handle,
                indent=1,
                sort_keys=True,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


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


# --- Market-session doctrine (25 Aug) -------------------------------------
# Sessions are DERIVED from the market class, never from operator hour
# variables. Equity-like classes trade on their underlying exchange's live
# session (NYSE regular hours: 09:30-16:00 America/New_York, Mon-Fri,
# DST-aware). 24/7 classes are ungated. Unknown classes fail closed.
# This governs BOTH entry timing and planned (voluntary) exits - protective
# exits (stops, stale-data) are unaffected and run 24/7.

_SESSION_24_7_CLASSES = {"builder_crypto", "crypto", "fx", "commodity"}
_SESSION_RESTRICTED_CLASSES = {"equity", "provisional_equity", "index", "preipo"}


def hip3_slice_market_class(slice_id: str) -> str | None:
    """Market class encoded in an HIP-3 slice id.

    Slice ids are namespaced ``hip3_{dex}_{class}_c{N}:feature:...`` where
    the group is built as ``{dex}_{market_class}_c{collateral_token}``.
    Non-HIP-3 ids return None.
    """
    head = str(slice_id or "").split(":", 1)[0]
    if not head.startswith("hip3_"):
        return None
    base = head[len("hip3_"):].rsplit("_c", 1)[0]
    # base is "{dex}_{class}"; the class may itself contain underscores
    # (provisional_equity), so split on the FIRST underscore only.
    _, _, cls = base.partition("_")
    return cls or None


def _as_utc(ts) -> datetime | None:
    try:
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        if not isinstance(ts, datetime):
            ts = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def hip3_session_restricted(market_class: str | None) -> bool:
    """True when the class trades on a calendar session (needs the
    underlying's live tape). 24/7 classes and unknown classes return
    False here - unknowns are handled by failing closed at the entry
    gate (hip3_in_market_session), not by promotion rules."""
    return market_class in _SESSION_RESTRICTED_CLASSES


def hip3_in_market_session(market_class: str | None, bar_end) -> bool:
    """True when a fill at ``bar_end`` (the bar's close time) happens inside
    the class's live session.

    24/7 classes always pass. Restricted classes must be inside NYSE regular
    hours (Mon-Fri 09:30-16:00 America/New_York via zoneinfo; when tzdata is
    unavailable the winter UTC window 14:30-20:00 is used as a conservative
    fallback - it can delay summer entries by an hour but never admits a
    pre-open fill). Unknown or missing classes fail closed.
    """
    if market_class in _SESSION_24_7_CLASSES:
        return True
    if market_class not in _SESSION_RESTRICTED_CLASSES:
        return False
    stamp = _as_utc(bar_end)
    if stamp is None:
        return False
    try:
        from zoneinfo import ZoneInfo

        local = stamp.astimezone(ZoneInfo("America/New_York"))
        return (
            local.weekday() < 5
            and local.time() >= _dt_time(9, 30)
            and local.time() < _dt_time(16, 0)
        )
    except Exception:
        return (
            stamp.weekday() < 5
            and stamp.time() >= _dt_time(14, 30)
            and stamp.time() < _dt_time(20, 0)
        )
