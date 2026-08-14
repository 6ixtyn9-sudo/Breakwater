"""Account valuation and broker-authoritative protection checks."""

from __future__ import annotations

from decimal import Decimal

from breakwater.decimal_utils import D
from breakwater.models import PairSpec, Position, Side
from breakwater.valr import ValrClient


class AccountStateError(RuntimeError):
    pass


def validate_api_key_permissions(key_info: dict, *, live: bool) -> set[str]:
    raw = key_info.get("permissions")
    if not isinstance(raw, list):
        raise AccountStateError("VALR API key permissions are unavailable")
    permissions = {str(value).strip().lower() for value in raw}
    if "view access" not in permissions:
        raise AccountStateError("VALR API key lacks View access")
    forbidden = permissions & {"withdraw", "internal transfer", "link bank account"}
    if forbidden:
        raise AccountStateError(
            f"VALR API key has forbidden permissions: {', '.join(sorted(forbidden))}"
        )
    if live and permissions != {"view access", "trade"}:
        raise AccountStateError("live key must have exactly View access and Trade")
    return permissions


def _balance_total(row: dict) -> Decimal:
    if "total" in row:
        return D(row["total"], field="balance total")
    return (
        D(row.get("available") or 0, field="available")
        + D(row.get("reserved") or 0, field="reserved")
        - D(row.get("borrowedAmount") or 0, field="borrowedAmount")
    )


class EquityValuator:
    def __init__(self, client: ValrClient, specs: dict[str, PairSpec]):
        self.client = client
        self.specs = specs
        self._rates: dict[str, Decimal] = {"ZAR": Decimal(1)}

    def rate_to_zar(self, currency: str) -> Decimal:
        currency = currency.upper()
        if currency in self._rates:
            return self._rates[currency]
        direct = next((
            spec for spec in self.specs.values()
            if spec.active and spec.base_currency == currency and spec.quote_currency == "ZAR"
        ), None)
        inverse = next((
            spec for spec in self.specs.values()
            if spec.active and spec.base_currency == "ZAR" and spec.quote_currency == currency
        ), None)
        if direct:
            rate = self.client.market_summary(direct.symbol).last
        elif inverse:
            price = self.client.market_summary(inverse.symbol).last
            if price <= 0:
                raise AccountStateError(f"invalid conversion price for {currency}")
            rate = Decimal(1) / price
        else:
            raise AccountStateError(f"no active VALR conversion path from {currency} to ZAR")
        self._rates[currency] = rate
        return rate

    def equity_zar(self, balances: list[dict], positions: list[Position]) -> Decimal:
        total = Decimal(0)
        for row in balances:
            currency = str(row.get("currency", "")).upper().strip()
            if not currency:
                raise AccountStateError("balance row is missing currency")
            amount = _balance_total(row)
            if amount == 0:
                continue
            total += amount * self.rate_to_zar(currency)
        for position in positions:
            spec = self.specs.get(position.pair)
            if spec is None:
                raise AccountStateError(f"missing pair metadata for {position.pair}")
            total += position.unrealised_pnl * self.rate_to_zar(spec.quote_currency)
        return total


def _conditional_pair(row: dict) -> str:
    return str(
        row.get("currencyPair") or row.get("pair") or row.get("pairSymbol") or ""
    ).upper()


def _conditional_side(row: dict) -> str:
    return str(row.get("side") or row.get("orderSide") or "").upper()


def _looks_like_stop(row: dict) -> bool:
    text = " ".join(str(value) for value in row.values()).upper()
    return "STOP" in text and str(row.get("status", "ACTIVE")).upper() not in {
        "CANCELLED", "CANCELED", "FAILED", "FILLED", "TRIGGERED",
    }


def unprotected_positions(
    positions: list[Position],
    open_orders: list[dict],
    conditionals: list[dict],
) -> list[Position]:
    rows = list(open_orders) + list(conditionals)
    missing = []
    for position in positions:
        closing_side = Side.SELL if position.side is Side.BUY else Side.BUY
        protected = any(
            _conditional_pair(row) == position.pair
            and _conditional_side(row) == closing_side.value
            and _looks_like_stop(row)
            for row in rows
        )
        if not protected:
            missing.append(position)
    return missing
