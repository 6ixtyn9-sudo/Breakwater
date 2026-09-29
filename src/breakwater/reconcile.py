"""Turn terminal live protection orders into realized-P&L events.

Why this module exists
----------------------
``RiskPolicy`` carries a ``daily_loss_limit_zar`` and a
``seven_day_loss_limit_zar``. ``RiskManager.check_account`` tests both, and
``Engine.guardian`` feeds it ``risk_state.daily_pnl(...)`` /
``risk_state.seven_day_pnl(...)``. Every part of that chain worked except the
first one: **nothing ever called** ``RiskStateStore.append_realized_pnl``.
Outside ``tests/test_ledger.py`` it had no call sites at all, so
``realized_pnl_events`` stayed ``[]``, both figures were permanently ``0``,
and neither loss limit could ever fire. They were configured, printed and
inert - the same failure mode the aggregate-risk leash had before it was
measured from the live book (see the note in ``Engine.guardian``).

This closes that loop. A live spot entry leaves a resting protection order.
When that order goes terminal the position is closed and the money is real,
so the P&L is booked into both durable stores:

- ``Ledger`` as a ``realized_pnl`` event (which ``Ledger.pnl_since`` already
  queries, and which was equally unfed);
- ``RiskStateStore``, which is what the guardian's risk gate actually reads.

Both writes are idempotent - the ledger on its ``event_id`` primary key, the
risk state on its own ``event_id`` scan - so re-running a cycle cannot
double-count a loss, and a crash between the two writes self-heals on the
next pass.

Scope and honesty
-----------------
- **Spot cash longs only.** That is the only live path ``TradeExecutor``
  supports today (perps raise ``PerpetualActivationBlocked``; margin shorts
  need a two-key gate). A SELL entry is reported as unsupported rather than
  mispriced.
- **Fees are modelled, not read back.** VALR's completed-order payload is
  consumed here only for fields the executor already depends on
  (``orderStatusType``, ``totalExecutedQuantity``, ``averagePrice``). Rather
  than guess at fee field names that have never been observed in a real
  response, the round trip is charged from ``breakwater.costs`` using the
  same both-legs convention as the paper engine. Realized P&L is therefore
  accurate on price and modelled on cost; it will differ slightly from the
  broker's own figure, and the broker stays authoritative for balances.
- **A protection order that goes terminal WITHOUT filling is not P&L.** It is
  an unprotected position, which is a safety event, so it is surfaced as
  ``unprotected`` rather than silently booked as a flat trade.
- On current committed state there are no ``live_entry`` events, so this is a
  no-op. It only starts doing work once something actually trades live.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from breakwater.costs import spot_round_trip_decimal

# Terminal states that mean "this protection order is done". Matches the set
# TradeExecutor._completed already treats as terminal.
_FILLED = {"filled"}
_TERMINAL_UNFILLED = {"cancelled", "canceled", "failed", "expired"}


@dataclass
class ReconcileReport:
    """What one reconciliation pass did. Advisory, but fail-loud."""

    checked: int = 0
    booked: int = 0
    still_open: int = 0
    unprotected: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    booked_zar: Decimal = Decimal(0)

    def as_dict(self) -> dict:
        return {
            "checked": self.checked,
            "booked": self.booked,
            "still_open": self.still_open,
            "unprotected": self.unprotected,
            "unsupported": self.unsupported,
            "errors": self.errors,
            "booked_zar": str(self.booked_zar),
        }


def _decimal(value, field_name: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} is not a number: {value!r}") from exc
    if not number.is_finite():
        raise ValueError(f"{field_name} must be finite: {value!r}")
    return number


def realized_pnl_zar(
    *,
    side: str,
    entry_price: Decimal,
    exit_price: Decimal,
    quantity: Decimal,
    pair: str,
    quote_to_zar: Decimal,
) -> Decimal:
    """Net realized P&L in ZAR for one closed spot round trip.

    Fees are charged on both legs at half the pair's round-trip rate, the
    same convention ``paper_trade`` uses, so live and paper P&L stay
    comparable instead of quietly using different cost models.
    """
    direction = Decimal(1) if str(side).upper() == "BUY" else Decimal(-1)
    gross_quote = (exit_price - entry_price) * quantity * direction
    round_trip_bps = spot_round_trip_decimal(pair)
    entry_notional = entry_price * quantity
    exit_notional = exit_price * quantity
    fee_quote = (entry_notional + exit_notional) * (round_trip_bps / Decimal(2)) / Decimal(10000)
    return (gross_quote - fee_quote) * quote_to_zar


def reconcile_realized_pnl(
    *,
    client,
    ledger,
    risk_state,
    server_time: datetime,
    quote_to_zar,
) -> ReconcileReport:
    """Book every newly-closed live position into the risk state.

    ``quote_to_zar`` is a callable taking a quote currency and returning its
    ZAR rate (``EquityValuator.rate_to_zar``). ``client`` need only provide
    ``completed_order``.

    Never raises: a reconciliation failure must not take down the guardian,
    because the guardian is also what reports the failure. Anything that goes
    wrong lands in ``report.errors`` and leaves the event unbooked, so the
    next pass retries it.
    """
    report = ReconcileReport()
    try:
        entries = ledger.events_of_kind("live_entry")
        already = {
            str(row["payload"].get("protection_order_id") or "")
            for row in ledger.events_of_kind("realized_pnl")
        }
    except Exception as exc:  # noqa: BLE001 - reconciliation must not throw
        report.errors.append(f"ledger unreadable: {type(exc).__name__}: {exc}"[:200])
        return report

    for row in entries:
        payload = row.get("payload") or {}
        protection_id = str(payload.get("protection_order_id") or "")
        if not protection_id or protection_id in already:
            continue
        report.checked += 1
        pair = str(payload.get("pair") or "")
        try:
            # Side was not always recorded on live_entry rows. Absent a side
            # we cannot sign the P&L, and guessing "probably a long" on a
            # money number is exactly the kind of quiet assumption this
            # system is supposed to refuse.
            side = str(payload.get("side") or "").upper()
            if side not in {"BUY", "SELL"}:
                report.unsupported.append(f"{protection_id}: side not recorded")
                continue
            if side == "SELL":
                report.unsupported.append(
                    f"{protection_id}: margin short reconciliation not implemented"
                )
                continue

            state = client.completed_order(protection_id)
            status = str(state.get("orderStatusType") or "").strip().lower()
            if status in _TERMINAL_UNFILLED:
                # The stop is gone but no exit was executed: whatever the
                # entry bought is sitting there unhedged.
                report.unprotected.append(f"{protection_id}: protection {status}")
                continue
            if status not in _FILLED:
                report.still_open += 1
                continue

            exit_quantity = _decimal(
                state.get("totalExecutedQuantity"), "totalExecutedQuantity"
            )
            exit_price = _decimal(state.get("averagePrice"), "averagePrice")
            entry_price = _decimal(payload.get("average_price"), "average_price")
            entry_quantity = _decimal(payload.get("filled_quantity"), "filled_quantity")
            if exit_quantity <= 0 or exit_price <= 0 or entry_price <= 0:
                report.errors.append(f"{protection_id}: non-positive fill values")
                continue
            if exit_quantity < entry_quantity:
                # Partial exit: the rest is still exposed. Book nothing and
                # keep the event open so the next pass sees the final state.
                report.still_open += 1
                continue

            quote_currency = str(payload.get("quote_currency") or "").upper()
            if not quote_currency:
                quote_currency = "ZAR" if pair.endswith("ZAR") else ""
            if not quote_currency:
                report.errors.append(f"{protection_id}: quote currency unknown for {pair}")
                continue
            rate = _decimal(quote_to_zar(quote_currency), "quote_to_zar")
            if rate <= 0:
                report.errors.append(f"{protection_id}: non-positive ZAR rate")
                continue

            amount_zar = realized_pnl_zar(
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=exit_quantity,
                pair=pair,
                quote_to_zar=rate,
            )
        except Exception as exc:  # noqa: BLE001 - one bad row must not stop the rest
            report.errors.append(f"{protection_id}: {type(exc).__name__}: {exc}"[:200])
            continue

        event_id = f"exit-{protection_id}"
        booked_payload = {
            "protection_order_id": protection_id,
            "entry_order_id": str(payload.get("entry_order_id") or ""),
            "pair": pair,
            "side": side,
            "entry_price": str(entry_price),
            "exit_price": str(exit_price),
            "quantity": str(exit_quantity),
            "amount_zar": str(amount_zar),
            "fee_model": "breakwater.costs.spot_round_trip_decimal (both legs)",
        }
        try:
            # Ledger first: its primary key is the idempotency anchor. If the
            # process dies between the two writes the next pass sees the
            # ledger row, skips re-pricing, and the risk-state append (also
            # keyed on event_id) completes.
            ledger.append(
                event_id=event_id,
                kind="realized_pnl",
                payload=booked_payload,
                occurred_at=server_time,
                strategy_id=str(payload.get("strategy_id") or "") or None,
                pair=pair or None,
                amount_zar=amount_zar,
            )
            risk_state.append_realized_pnl(event_id, amount_zar, server_time)
        except Exception as exc:  # noqa: BLE001
            report.errors.append(f"{protection_id}: booking failed: {type(exc).__name__}"[:200])
            continue
        report.booked += 1
        report.booked_zar += amount_zar
        already.add(protection_id)

    return report
