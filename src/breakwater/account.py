"""Account valuation and broker-authoritative protection checks."""

from __future__ import annotations

from decimal import Decimal

from breakwater.costs import quote_of
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
            "VALR API key has forbidden permissions: "
            f"{', '.join(sorted(forbidden))}. "
            "Create a new VALR key with only View access and Trade enabled"
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


def _stop_trigger_price(row: dict) -> Decimal | None:
    """The stop trigger price on a conditional/stop order row, if present."""
    for key in ("stopPrice", "stop_price", "triggerPrice", "trigger_price"):
        value = row.get(key)
        if value in (None, ""):
            continue
        try:
            price = D(value, field=key)
        except Exception:
            continue
        if price > 0:
            return price
    return None


def aggregate_open_stop_risk_zar(
    positions: list[Position],
    open_orders: list[dict],
    conditionals: list[dict],
    *,
    last_price,
    quote_to_zar=None,
) -> tuple[Decimal, list[str]]:
    """Open stop-risk in ZAR, from the LIVE book.

    Each protected position contributes the distance from the current price to
    its resting stop, times quantity: the money genuinely at risk if the stop
    is the next thing that happens. A stop already through the market (a long
    whose stop sits above the last price) contributes zero - that is locked
    gain, not risk - but it must be a stop we could actually find, otherwise
    the position is reported as unpriceable instead of counted as flat.

    Returns ``(risk, unknown_reasons)``. ``unknown_reasons`` being non-empty
    means the number is not trustworthy, and callers must fail closed rather
    than treat it as zero. The guardian already halts on positions with no
    confirmed protection at all; this covers the narrower case of a protected
    position whose stop cannot be priced or converted.
    """
    rows = list(open_orders) + list(conditionals)
    total = Decimal(0)
    unknown: list[str] = []
    for position in positions:
        closing_side = Side.SELL if position.side is Side.BUY else Side.BUY
        stop_price = None
        for row in rows:
            if (
                _conditional_pair(row) == position.pair
                and _conditional_side(row) == closing_side.value
                and _looks_like_stop(row)
            ):
                stop_price = _stop_trigger_price(row)
                if stop_price is not None:
                    break
        if stop_price is None:
            unknown.append(f"{position.pair}: stop price unavailable")
            continue
        try:
            price = D(last_price(position.pair), field=f"{position.pair} last price")
        except Exception:
            unknown.append(f"{position.pair}: last price unavailable")
            continue
        if price <= 0:
            unknown.append(f"{position.pair}: last price is not positive")
            continue
        if position.side is Side.BUY:
            distance = price - stop_price
        else:
            distance = stop_price - price
        if distance <= 0:
            continue
        risk = distance * position.quantity
        if quote_to_zar is not None:
            quote = quote_of(position.pair)
            if not quote:
                unknown.append(f"{position.pair}: quote currency is unknown")
                continue
            try:
                rate = Decimal(str(quote_to_zar(quote)))
            except Exception:
                unknown.append(f"{position.pair}: no conversion path from {quote}")
                continue
            if rate <= 0:
                unknown.append(f"{position.pair}: conversion rate is not positive")
                continue
            risk *= rate
        total += risk
    return total, unknown
