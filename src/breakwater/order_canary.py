"""Prove the VALR spot order path works, without taking a position.

Not to be confused with `breakwater.canary`, which is the capped *risk
mandate* a first live run would trade under. That module answers "how much
may we lose"; this one answers "does placing an order work at all". They are
independent gates and both must pass.

`TradeExecutor.execute` has never run against the real VALR API. Every part
of it — request signing, the `/v2/orders/limit` body shape, order-id parsing,
the `_completed` polling loop, status vocabulary, `active_order` confirmation,
cancellation — is currently believed-correct rather than known-correct. The
first time we find out is otherwise the first time real money is at risk,
during a signal-driven entry we did not choose the timing of.

This module chooses the timing instead.

## How an order proves the path without risking a fill

The live entry is a **FOK limit BUY**. Two properties make that safe to
rehearse:

1. A BUY priced far *below* the best bid cannot cross the spread, so it
   cannot fill at a price we did not name.
2. Fill-or-kill means it cannot rest on the book either — VALR kills it
   immediately. There is nothing left behind to forget about.

So a deep-below-market FOK BUY exercises placement, the response shape, the
polling loop and terminal-status parsing, and then evaporates. That is step
`fok_kill`.

What it does not exercise is the resting/confirm/cancel path, which
`_execute_spot_long` relies on to verify the protective stop went live. Step
`rest_confirm_cancel` covers that with a **post-only GTC** BUY at the same
deep price: post-only cannot take liquidity (VALR rejects it outright if it
would cross), so it rests, gets confirmed via `active_order`, and is
cancelled.

## What this deliberately cannot prove

- A real fill. `averagePrice` and `totalExecutedQuantity` on a genuine
  execution are still unverified, because verifying them means owning the
  asset.
- `place_spot_stop_limit`. A STOP_LOSS_LIMIT SELL requires holding the base
  currency, which requires a real fill first.

Those two remain open after a green canary, and the report says so rather
than implying full coverage. They are the content of a later, funded canary.

## Why this does not require arming the engine

`Settings.writes_allowed` is true only when `BREAKWATER_MODE=live` and the
live acknowledgement is set — the same switch that lets the guardian place
signal-driven orders. Requiring it here would mean the only way to test the
order path is to arm the whole system, which is exactly backwards.

So the canary builds its own client with `allow_writes=True` behind its own
separate acknowledgement (`BREAKWATER_CANARY_ACK`). Proving the plumbing and
arming the strategy are different decisions and take different keys.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from breakwater.decimal_utils import ceil_to_step, floor_to_step, plain
from breakwater.execution import TradeExecutor
from breakwater.models import PairType
from breakwater.valr import ValrClient, ValrError

CANARY_ACKNOWLEDGEMENT = "I_ACCEPT_BREAKWATER_CANARY_ORDERS"

# The canary bid sits at this fraction of the best bid. Far enough below that
# no plausible tick-rounding or stale-quote error brings it near the spread.
PRICE_SAFETY_FRACTION = Decimal("0.5")

# Hard ceiling on what a canary order may be worth. Belt-and-braces against a
# minimum-size calculation going wrong: even if everything else failed and the
# order filled at its own limit price, this bounds the loss.
MAX_NOTIONAL_ZAR = Decimal("30")

# How long to wait for a resting order to show up as active before giving up.
CONFIRM_TIMEOUT_SECONDS = 15.0

# Marks every order this module places, so the residual sweep can recognise
# its own litter without touching anything else on the account.
ORDER_TAG = "bw-canary"


class CanaryAborted(RuntimeError):
    """A precondition failed. No order was placed."""


class CanaryResidual(RuntimeError):
    """An order may still be resting. Requires human eyes immediately."""


@dataclass(frozen=True)
class CanaryStep:
    name: str
    ok: bool
    detail: str

    def render(self) -> str:
        return f"{'PASS' if self.ok else 'FAIL'} | {self.name} — {self.detail}"


@dataclass
class CanaryReport:
    pair: str
    armed: bool
    # The plan actually used, so callers display the order that was sent
    # rather than re-deriving one from a book that has since moved.
    plan: "CanaryPlan | None" = None
    steps: list[CanaryStep] = field(default_factory=list)
    placed_order_ids: list[str] = field(default_factory=list)
    residual_order_ids: list[str] = field(default_factory=list)
    proven: list[str] = field(default_factory=list)
    still_unproven: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(step.ok for step in self.steps) and not self.residual_order_ids

    def add(self, name: str, ok: bool, detail: str) -> CanaryStep:
        step = CanaryStep(name, ok, detail)
        self.steps.append(step)
        return step

    def to_receipt(self) -> dict:
        return {
            "schema": 1,
            "pair": self.pair,
            "armed": self.armed,
            "ok": self.ok,
            "ran_at": datetime.now(UTC).isoformat(),
            "plan": (
                {
                    "price": plain(self.plan.price),
                    "quantity": plain(self.plan.quantity),
                    "notional_zar": f"{self.plan.notional:.2f}",
                    "best_bid": plain(self.plan.best_bid),
                }
                if self.plan
                else None
            ),
            "steps": [
                {"name": s.name, "ok": s.ok, "detail": s.detail} for s in self.steps
            ],
            "placed_order_ids": self.placed_order_ids,
            "residual_order_ids": self.residual_order_ids,
            "proven": self.proven,
            "still_unproven": self.still_unproven,
        }


def canary_ack_ok() -> bool:
    return os.getenv("BREAKWATER_CANARY_ACK", "off") == CANARY_ACKNOWLEDGEMENT


@dataclass(frozen=True)
class CanaryPlan:
    """The exact order the canary would place, and the arithmetic behind it."""

    pair: str
    price: Decimal
    quantity: Decimal
    notional: Decimal
    best_bid: Decimal
    best_ask: Decimal
    tick_size: Decimal
    min_base: Decimal
    min_quote: Decimal

    def render(self) -> list[str]:
        discount = (Decimal(1) - self.price / self.best_bid) * 100
        return [
            f"pair            {self.pair}",
            f"book            bid {plain(self.best_bid)} / ask {plain(self.best_ask)}",
            f"canary bid      {plain(self.price)}  ({discount:.1f}% below best bid)",
            f"quantity        {plain(self.quantity)}  (min base {plain(self.min_base)})",
            f"notional        {plain(self.notional)} ZAR  (min quote {plain(self.min_quote)},"
            f" cap {plain(MAX_NOTIONAL_ZAR)})",
        ]


def build_plan(client: ValrClient, pair: str) -> CanaryPlan:
    """Compute a deep-below-market order, or refuse to.

    Every guard here is a reason not to send anything. The function returns a
    plan only when placing it cannot plausibly result in a fill.
    """
    pair = pair.upper()

    specs = {spec.symbol: spec for spec in client.pairs()}
    spec = specs.get(pair)
    if spec is None:
        raise CanaryAborted(f"{pair} is not listed on VALR")
    if spec.pair_type is not PairType.SPOT:
        raise CanaryAborted(f"{pair} is {spec.pair_type.value}, not SPOT")
    if not spec.active:
        raise CanaryAborted(f"{pair} is not active for trading")
    if spec.quote_currency != "ZAR":
        raise CanaryAborted(f"{pair} settles in {spec.quote_currency}, not ZAR")

    summary = client.market_summary(pair)
    best_bid = summary.bid
    best_ask = summary.ask
    if best_bid <= 0 or best_ask <= 0:
        raise CanaryAborted(f"{pair} has no two-sided market right now")
    if best_ask <= best_bid:
        raise CanaryAborted(
            f"{pair} book is crossed or locked (bid {best_bid} >= ask {best_ask})"
        )

    price = floor_to_step(best_bid * PRICE_SAFETY_FRACTION, spec.tick_size)
    if price <= 0:
        raise CanaryAborted(
            f"tick size {spec.tick_size} rounds the canary price to zero for {pair}"
        )

    # The invariant the whole design rests on, re-checked after rounding.
    if price >= best_bid:
        raise CanaryAborted(
            f"refusing to bid {price} at or above the best bid {best_bid}"
        )

    base_step = Decimal(10) ** -spec.base_decimal_places
    quantity = ceil_to_step(max(spec.min_base, spec.min_quote / price), base_step)
    if quantity <= 0:
        raise CanaryAborted(f"computed a non-positive quantity for {pair}")
    if spec.max_base and quantity > spec.max_base:
        raise CanaryAborted(
            f"minimum order size {quantity} exceeds the maximum {spec.max_base}"
        )

    notional = quantity * price
    if notional > MAX_NOTIONAL_ZAR:
        raise CanaryAborted(
            f"canary notional {notional:.2f} ZAR exceeds the {MAX_NOTIONAL_ZAR} ZAR cap; "
            f"pick a pair with a smaller minimum"
        )

    return CanaryPlan(
        pair=pair,
        price=price,
        quantity=quantity,
        notional=notional,
        best_bid=best_bid,
        best_ask=best_ask,
        tick_size=spec.tick_size,
        min_base=spec.min_base,
        min_quote=spec.min_quote,
    )


def _order_id(response: object, what: str) -> str:
    if not isinstance(response, dict):
        raise ValrError(f"{what} response was not an object: {type(response).__name__}")
    order_id = str(response.get("id") or "")
    if not order_id:
        raise ValrError(f"{what} response did not include an order id")
    return order_id


def _sweep(client: ValrClient, tag: str) -> list[str]:
    """Order ids still open that carry our tag. Should always be empty."""
    try:
        rows = client.open_orders()
    except ValrError:
        # Unknown beats a confident empty list: an unreadable book is exactly
        # when a stray order is most likely to be missed.
        raise CanaryResidual(
            "could not read open orders to confirm nothing was left resting; "
            "check the VALR web UI by hand"
        ) from None
    return [
        str(row.get("orderId") or row.get("id") or "")
        for row in rows
        if tag in str(row.get("customerOrderId") or "")
    ]


def preflight(client: ValrClient, pair: str, report: CanaryReport) -> CanaryPlan:
    """Read-only checks. Everything that can fail without sending an order."""
    key = client.current_api_key()
    permissions = [str(p).strip().lower() for p in (key.get("permissions") or [])]
    can_trade = any("trade" in p for p in permissions)
    report.add(
        "auth",
        can_trade,
        f"key authenticated, permissions {permissions or ['(none reported)']}"
        + ("" if can_trade else " — no trade permission, orders will be rejected"),
    )
    if not can_trade:
        raise CanaryAborted("API key lacks trade permission")

    types = client.order_types(pair)
    required = {"LIMIT", "STOP_LOSS_LIMIT"}
    missing = required - types
    report.add(
        "order_types",
        not missing,
        f"{pair} supports {sorted(types)}"
        + (f" — missing {sorted(missing)}" if missing else ""),
    )
    if missing:
        # Same precondition _execute_spot_long enforces; failing here means the
        # live path would have failed too, which is worth knowing now.
        raise CanaryAborted(f"{pair} lacks required order types {sorted(missing)}")

    plan = build_plan(client, pair)
    report.plan = plan
    report.add(
        "plan",
        True,
        f"bid {plain(plan.price)} x {plain(plan.quantity)} = {plan.notional:.2f} ZAR, "
        f"{(Decimal(1) - plan.price / plan.best_bid) * 100:.1f}% below best bid",
    )

    stale = _sweep(client, ORDER_TAG)
    report.add(
        "clean_slate",
        not stale,
        "no canary orders left over from a previous run"
        if not stale
        else f"previous canary orders still open: {stale}",
    )
    if stale:
        raise CanaryAborted(
            f"canary orders from a previous run are still open: {stale}; "
            f"cancel them before running again"
        )
    return plan


def _fok_kill(client: ValrClient, plan: CanaryPlan, tag: str, report: CanaryReport) -> None:
    """Place a FOK bid that cannot cross. VALR must kill it immediately."""
    executor = TradeExecutor(client)
    response = client.place_limit(
        {
            "side": "BUY",
            "quantity": plain(plan.quantity),
            "price": plain(plan.price),
            "pair": plan.pair,
            "postOnly": False,
            "timeInForce": "FOK",
            "customerOrderId": f"{tag}-fok"[:50],
        }
    )
    order_id = _order_id(response, "FOK entry")
    report.placed_order_ids.append(order_id)

    # Deliberately the production polling loop, not a reimplementation: the
    # point is to prove that code, including its status vocabulary.
    state = executor._completed(order_id)
    status = str(state.get("orderStatusType") or "").lower()
    filled = Decimal(str(state.get("totalExecutedQuantity") or 0))

    if filled > 0:
        raise CanaryResidual(
            f"FOK canary FILLED {filled} {plan.pair} at or below {plan.price} — "
            f"this should be impossible; you now hold a position, close it by hand"
        )
    report.add(
        "fok_kill",
        status in {"failed", "cancelled", "canceled", "expired"},
        f"order {order_id} reached terminal status '{status}' with zero fill "
        f"(placement, id parsing, polling loop and status vocabulary all exercised)",
    )


def _rest_confirm_cancel(
    client: ValrClient, plan: CanaryPlan, tag: str, report: CanaryReport
) -> None:
    """Rest a post-only bid, confirm it is live, then cancel it."""
    order_id = ""
    try:
        response = client.place_limit(
            {
                "side": "BUY",
                "quantity": plain(plan.quantity),
                "price": plain(plan.price),
                "pair": plan.pair,
                # Post-only is the safety net: VALR rejects the order outright
                # rather than let it take liquidity at an unintended price.
                "postOnly": True,
                "timeInForce": "GTC",
                "customerOrderId": f"{tag}-rest"[:50],
            }
        )
        order_id = _order_id(response, "resting entry")
        report.placed_order_ids.append(order_id)

        active_status = ""
        deadline = time.monotonic() + CONFIRM_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            try:
                active = client.active_order(plan.pair, order_id)
            except ValrError:
                time.sleep(0.5)
                continue
            active_status = str(active.get("orderStatusType") or "").lower()
            if active_status:
                break
            time.sleep(0.5)

        report.add(
            "rest_confirm",
            active_status in {"active", "placed"},
            f"order {order_id} confirmed on the book as '{active_status or 'unknown'}' "
            f"(this is the call that verifies a protective stop went live)",
        )
    finally:
        # Runs even if confirmation failed or raised: an order we placed and
        # cannot account for is the one outcome worse than a failed test.
        if order_id:
            cancelled = False
            detail = ""
            for attempt in range(3):
                try:
                    client.cancel_order(plan.pair, order_id)
                    cancelled = True
                    break
                except ValrError as exc:
                    detail = str(exc)
                    time.sleep(0.5 * (2**attempt))
            report.add(
                "cancel",
                cancelled,
                f"order {order_id} cancelled"
                if cancelled
                else f"CANCEL FAILED after 3 attempts: {detail}",
            )


def run_canary(
    client: ValrClient,
    pair: str,
    *,
    armed: bool,
    receipt_path: Path | None = None,
) -> CanaryReport:
    """Run the canary. With `armed=False` nothing is sent to the exchange."""
    report = CanaryReport(pair=pair.upper(), armed=armed)
    tag = f"{ORDER_TAG}-{int(time.time())}"

    plan = preflight(client, pair, report)

    if not armed:
        report.add(
            "dry_run",
            True,
            "preflight only; no order was sent. Re-run with --arm to place "
            "and cancel the two canary orders described above.",
        )
        report.still_unproven = [
            "order placement against the real API",
            "the _completed polling loop and status vocabulary",
            "active_order confirmation and cancellation",
            "a real fill (averagePrice, totalExecutedQuantity)",
            "place_spot_stop_limit (needs base currency, so needs a real fill)",
        ]
        _write_receipt(report, receipt_path)
        return report

    try:
        _fok_kill(client, plan, tag, report)
        _rest_confirm_cancel(client, plan, tag, report)
    finally:
        # Final accounting, always. This is the check that matters most.
        try:
            residual = _sweep(client, ORDER_TAG)
        except CanaryResidual as exc:
            report.add("no_residual", False, str(exc))
        else:
            report.residual_order_ids = residual
            report.add(
                "no_residual",
                not residual,
                "nothing left resting on the book"
                if not residual
                else f"ORDERS STILL OPEN: {residual} — cancel them in the VALR UI now",
            )

    report.proven = [
        "request signing and authentication against the live API",
        "the /v2/orders/limit body shape VALR actually accepts",
        "order-id parsing from a real response",
        "the _completed polling loop and its terminal-status vocabulary",
        "active_order confirmation of a resting order",
        "cancel_order, and that we leave nothing behind",
    ]
    report.still_unproven = [
        "a real fill (averagePrice, totalExecutedQuantity on an execution)",
        "place_spot_stop_limit (needs base currency, so needs a real fill)",
        "the emergency-close path (place_market)",
    ]
    _write_receipt(report, receipt_path)
    return report


def _write_receipt(report: CanaryReport, receipt_path: Path | None) -> None:
    if receipt_path is None:
        return
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(report.to_receipt(), indent=2) + "\n")
