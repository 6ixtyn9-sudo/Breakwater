"""Fail-closed Hyperliquid public and account-state adapter.

This module intentionally contains no private-key handling and no signing.
Supplying a public master/subaccount address permits account reconciliation,
but every write method remains hard blocked. Signed testnet execution belongs
in a separate executor after its native TPSL mechanism canary is implemented.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

import requests

from breakwater.models import Side
from breakwater.perp_venue import (
    PerpAccountSnapshot,
    PerpCoverage,
    PerpInstrument,
    PerpOpenOrder,
    PerpVenueError,
    PerpVenuePosition,
    PerpWriteBlocked,
)
from breakwater.perpdata import fetch_perp_candles

MAINNET_API_URL = "https://api.hyperliquid.xyz"
TESTNET_API_URL = "https://api.hyperliquid-testnet.xyz"
_EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _decimal(value, *, field: str, allow_empty: bool = False) -> Decimal | None:
    if allow_empty and value in {None, ""}:
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PerpVenueError(f"Hyperliquid {field} is not a decimal") from exc
    if not number.is_finite():
        raise PerpVenueError(f"Hyperliquid {field} must be finite")
    return number


def _side(value: str) -> Side:
    normalized = str(value).strip().upper()
    if normalized in {"B", "BUY", "LONG"}:
        return Side.BUY
    if normalized in {"A", "SELL", "SHORT"}:
        return Side.SELL
    raise PerpVenueError(f"Hyperliquid side is unrecognized: {value!r}")


def _symbol(coin: str) -> str:
    return f"{coin.upper()}USDC"


def validate_account_address(address: str) -> str:
    cleaned = str(address).strip()
    if not _EVM_ADDRESS.fullmatch(cleaned):
        raise ValueError("Hyperliquid account address must be 0x followed by 40 hex characters")
    return cleaned


class HyperliquidReadOnlyVenue:
    """Normalized Hyperliquid adapter with an intentionally absent write path."""

    name = "hyperliquid"

    def __init__(
        self,
        *,
        testnet: bool = False,
        session: requests.Session | None = None,
        timeout: int = 20,
    ):
        self.testnet = bool(testnet)
        self.base_url = TESTNET_API_URL if self.testnet else MAINNET_API_URL
        self.info_url = f"{self.base_url}/info"
        self.session = session or requests.Session()
        self.timeout = timeout

    @property
    def network(self) -> str:
        return "testnet" if self.testnet else "mainnet"

    def _post_info(self, payload: dict):
        try:
            response = self.session.post(self.info_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise PerpVenueError(f"Hyperliquid {self.network} info request failed") from exc
        except (TypeError, ValueError) as exc:
            raise PerpVenueError("Hyperliquid info response is not valid JSON") from exc

    def instruments(self) -> tuple[PerpInstrument, ...]:
        payload = self._post_info({"type": "metaAndAssetCtxs"})
        if not isinstance(payload, list) or len(payload) != 2:
            raise PerpVenueError("Hyperliquid metaAndAssetCtxs response is malformed")
        meta, contexts = payload
        universe = meta.get("universe") if isinstance(meta, dict) else None
        if not isinstance(universe, list) or not isinstance(contexts, list):
            raise PerpVenueError("Hyperliquid instrument metadata schema is unrecognized")
        if len(contexts) != len(universe):
            raise PerpVenueError("Hyperliquid instrument metadata and contexts are misaligned")

        instruments: list[PerpInstrument] = []
        for asset_id, (row, context) in enumerate(zip(universe, contexts, strict=True)):
            if not isinstance(row, dict) or not isinstance(context, dict):
                raise PerpVenueError("Hyperliquid instrument row is malformed")
            coin = str(row.get("name") or "").strip()
            if not coin:
                raise PerpVenueError("Hyperliquid instrument is missing its coin")
            # Keep HIP-3 builder assets out of the crypto strategy pool.
            if ":" in coin:
                continue
            try:
                size_decimals = int(row["szDecimals"])
            except (KeyError, TypeError, ValueError) as exc:
                raise PerpVenueError(f"Hyperliquid {coin} size precision is malformed") from exc
            if size_decimals < 0 or size_decimals > 18:
                raise PerpVenueError(f"Hyperliquid {coin} size precision is unsafe")
            mark = _decimal(context.get("markPx"), field=f"{coin}.markPx")
            oracle = _decimal(context.get("oraclePx"), field=f"{coin}.oraclePx")
            leverage = _decimal(row.get("maxLeverage"), field=f"{coin}.maxLeverage")
            if mark is None or oracle is None or leverage is None:
                raise PerpVenueError(f"Hyperliquid {coin} metadata is incomplete")
            instruments.append(
                PerpInstrument(
                    venue=self.name,
                    symbol=_symbol(coin),
                    coin=coin,
                    asset_id=asset_id,
                    size_decimals=size_decimals,
                    max_price_decimals=max(0, 6 - size_decimals),
                    max_significant_figures=5,
                    max_leverage=leverage,
                    min_notional=Decimal("10"),
                    mark_price=mark,
                    oracle_price=oracle,
                    funding_rate=_decimal(
                        context.get("funding") or 0, field=f"{coin}.funding"
                    )
                    or Decimal(0),
                    open_interest=_decimal(
                        context.get("openInterest") or 0, field=f"{coin}.openInterest"
                    )
                    or Decimal(0),
                    day_notional_volume=_decimal(
                        context.get("dayNtlVlm") or 0, field=f"{coin}.dayNtlVlm"
                    )
                    or Decimal(0),
                    active=not bool(row.get("isDelisted", False)),
                )
            )
        return tuple(instruments)

    def candles(self, symbol: str, *, interval: str = "1h", count: int = 220):
        normalized = str(symbol).upper().strip()
        if ":" in normalized:
            raise ValueError("HIP-3 builder instruments are excluded from Breakwater crypto")
        if not normalized.endswith("USDC") or len(normalized) <= 4:
            raise ValueError("Hyperliquid perpetual symbol must end in USDC")
        coin = normalized[:-4]
        return fetch_perp_candles(
            coin,
            interval=interval,
            count=count,
            session=self.session,
            info_url=self.info_url,
        )

    def coverage(self, symbols: list[str]) -> PerpCoverage:
        available = {instrument.symbol for instrument in self.instruments() if instrument.active}
        tradable: list[str] = []
        unavailable: list[str] = []
        excluded: list[str] = []
        for symbol in symbols:
            normalized = str(symbol).upper().strip()
            if ":" in normalized:
                excluded.append(normalized)
            elif normalized in available:
                tradable.append(normalized)
            else:
                unavailable.append(normalized)
        return PerpCoverage(
            tradable=tuple(sorted(set(tradable))),
            unavailable=tuple(sorted(set(unavailable))),
            intentionally_excluded=tuple(sorted(set(excluded))),
        )

    def account_snapshot(self, address: str) -> PerpAccountSnapshot:
        address = validate_account_address(address)
        instruments = {instrument.coin: instrument for instrument in self.instruments()}
        state = self._post_info({"type": "clearinghouseState", "user": address})
        # Frontend orders include native trigger and reduce-only fields needed
        # to prove that every live position is protected.
        orders = self._post_info({"type": "frontendOpenOrders", "user": address})
        if not isinstance(state, dict) or not isinstance(orders, list):
            raise PerpVenueError("Hyperliquid account response is malformed")
        margin = state.get("marginSummary")
        asset_positions = state.get("assetPositions")
        if not isinstance(margin, dict) or not isinstance(asset_positions, list):
            raise PerpVenueError("Hyperliquid clearinghouse state schema is unrecognized")

        positions: list[PerpVenuePosition] = []
        for wrapper in asset_positions:
            position = wrapper.get("position") if isinstance(wrapper, dict) else None
            if not isinstance(position, dict):
                raise PerpVenueError("Hyperliquid position row is malformed")
            coin = str(position.get("coin") or "")
            if ":" in coin:
                continue
            instrument = instruments.get(coin)
            if instrument is None:
                raise PerpVenueError(f"Hyperliquid position coin is absent from metadata: {coin}")
            signed_size = _decimal(position.get("szi"), field=f"{coin}.szi")
            if signed_size is None or signed_size == 0:
                continue
            leverage_row = position.get("leverage") or {}
            leverage = _decimal(
                leverage_row.get("value") if isinstance(leverage_row, dict) else None,
                field=f"{coin}.leverage",
            )
            if leverage is None:
                raise PerpVenueError(f"Hyperliquid {coin} leverage is missing")
            positions.append(
                PerpVenuePosition(
                    symbol=instrument.symbol,
                    coin=coin,
                    side=Side.BUY if signed_size > 0 else Side.SELL,
                    quantity=abs(signed_size),
                    entry_price=_decimal(position.get("entryPx"), field=f"{coin}.entryPx")
                    or Decimal(0),
                    mark_price=instrument.mark_price,
                    notional=abs(
                        _decimal(position.get("positionValue"), field=f"{coin}.positionValue")
                        or Decimal(0)
                    ),
                    unrealised_pnl=_decimal(
                        position.get("unrealizedPnl") or 0,
                        field=f"{coin}.unrealizedPnl",
                    )
                    or Decimal(0),
                    liquidation_price=_decimal(
                        position.get("liquidationPx"),
                        field=f"{coin}.liquidationPx",
                        allow_empty=True,
                    ),
                    leverage=leverage,
                )
            )

        open_orders: list[PerpOpenOrder] = []
        for row in orders:
            if not isinstance(row, dict):
                raise PerpVenueError("Hyperliquid open order row is malformed")
            coin = str(row.get("coin") or "")
            if ":" in coin:
                continue
            if coin not in instruments:
                raise PerpVenueError(f"Hyperliquid order coin is absent from metadata: {coin}")
            try:
                timestamp_ms = int(row.get("timestamp") or 0)
            except (TypeError, ValueError) as exc:
                raise PerpVenueError(f"Hyperliquid {coin} order timestamp is malformed") from exc
            open_orders.append(
                PerpOpenOrder(
                    symbol=instruments[coin].symbol,
                    coin=coin,
                    order_id=str(row.get("oid") or ""),
                    client_order_id=(str(row["cloid"]) if row.get("cloid") else None),
                    side=_side(row.get("side")),
                    price=_decimal(row.get("limitPx"), field=f"{coin}.limitPx") or Decimal(0),
                    quantity=_decimal(row.get("sz"), field=f"{coin}.sz") or Decimal(0),
                    original_quantity=_decimal(
                        row.get("origSz") or row.get("sz"), field=f"{coin}.origSz"
                    )
                    or Decimal(0),
                    reduce_only=bool(row.get("reduceOnly", False)),
                    is_trigger=bool(row.get("isTrigger", False)),
                    is_position_tpsl=bool(row.get("isPositionTpsl", False)),
                    order_type=str(row.get("orderType") or ""),
                    trigger_price=_decimal(
                        row.get("triggerPx"), field=f"{coin}.triggerPx", allow_empty=True
                    ),
                    trigger_condition=(
                        str(row.get("triggerCondition"))
                        if row.get("triggerCondition") not in {None, ""}
                        else None
                    ),
                    timestamp_ms=timestamp_ms,
                )
            )

        def summary_decimal(field: str) -> Decimal:
            value = _decimal(margin.get(field), field=f"marginSummary.{field}")
            if value is None:
                raise PerpVenueError(f"Hyperliquid marginSummary.{field} is missing")
            return value

        withdrawable = _decimal(state.get("withdrawable"), field="withdrawable")
        if withdrawable is None:
            raise PerpVenueError("Hyperliquid withdrawable balance is missing")
        return PerpAccountSnapshot(
            venue=self.name,
            address=address,
            account_value=summary_decimal("accountValue"),
            withdrawable=withdrawable,
            total_margin_used=summary_decimal("totalMarginUsed"),
            total_notional_position=summary_decimal("totalNtlPos"),
            positions=tuple(positions),
            open_orders=tuple(open_orders),
        )

    def health(self) -> dict:
        instruments = self.instruments()
        return {
            "venue": self.name,
            "network": self.network,
            "endpoint": self.base_url,
            "instruments": len(instruments),
            "writes_allowed": False,
            "hip3_included": False,
        }

    @staticmethod
    def _writes_blocked():
        raise PerpWriteBlocked(
            "Hyperliquid writes are locked; this adapter contains no signer or private-key path"
        )

    def place_entry(self, *args, **kwargs):
        self._writes_blocked()

    def place_protective_orders(self, *args, **kwargs):
        self._writes_blocked()

    def cancel_order(self, *args, **kwargs):
        self._writes_blocked()

    def cancel_all(self, *args, **kwargs):
        self._writes_blocked()
