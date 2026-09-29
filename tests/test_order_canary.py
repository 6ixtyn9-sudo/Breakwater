"""The canary's whole value is that it cannot fill. These tests hold it to that.

Every guard in build_plan is a reason not to send an order, so each one gets a
test that proves it refuses. The fake client raises if a write endpoint is
touched during a dry run, which is the assertion that matters most: a "safe"
mode that quietly places orders would be worse than no canary at all.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from breakwater import order_canary
from breakwater.models import MarketSummary, PairSpec, PairType
from breakwater.order_canary import (
    MAX_NOTIONAL_ZAR,
    ORDER_TAG,
    CanaryAborted,
    CanaryResidual,
    build_plan,
    canary_ack_ok,
    run_canary,
)
from breakwater.valr import ValrError


def spec(
    symbol="XRPZAR",
    *,
    pair_type=PairType.SPOT,
    active=True,
    quote="ZAR",
    min_base="1",
    max_base="100000",
    min_quote="10",
    tick="0.01",
    decimals=2,
):
    return PairSpec(
        symbol=symbol,
        base_currency=symbol.replace(quote, ""),
        quote_currency=quote,
        active=active,
        min_base=Decimal(min_base),
        max_base=Decimal(max_base),
        min_quote=Decimal(min_quote),
        max_quote=Decimal("1000000"),
        tick_size=Decimal(tick),
        base_decimal_places=decimals,
        pair_type=pair_type,
    )


def summary(pair="XRPZAR", bid="40.00", ask="40.10"):
    return MarketSummary(
        pair=pair,
        bid=Decimal(bid),
        ask=Decimal(ask),
        last=Decimal(bid),
        mark=Decimal(bid),
        quote_volume=Decimal("1000"),
        timestamp=datetime.now(UTC),
    )


class FakeClient:
    """Records calls; refuses writes unless the test explicitly allows them."""

    def __init__(
        self,
        *,
        specs=None,
        market=None,
        types=None,
        permissions=("Trade", "View access"),
        allow_writes=False,
        open_rows=None,
        completed_status="Failed",
        completed_filled="0",
        active_status="Active",
        cancel_error=None,
    ):
        self.specs = specs if specs is not None else [spec()]
        self.market = market or summary()
        self.types = types if types is not None else {"LIMIT", "STOP_LOSS_LIMIT", "MARKET"}
        self.permissions = list(permissions)
        self.allow_writes = allow_writes
        self.open_rows = list(open_rows or [])
        self.completed_status = completed_status
        self.completed_filled = completed_filled
        self.active_status = active_status
        self.cancel_error = cancel_error
        self.placed: list[dict] = []
        self.cancelled: list[str] = []

    # -- reads ---------------------------------------------------------
    def pairs(self, pair_type=None):
        return self.specs

    def market_summary(self, pair):
        return self.market

    def order_types(self, pair):
        return set(self.types)

    def current_api_key(self):
        return {"permissions": self.permissions}

    def open_orders(self):
        return list(self.open_rows)

    def completed_order(self, order_id):
        return {
            "orderStatusType": self.completed_status,
            "totalExecutedQuantity": self.completed_filled,
            "averagePrice": "0",
        }

    def active_order(self, pair, order_id):
        return {"orderStatusType": self.active_status}

    # -- writes --------------------------------------------------------
    def _write(self, what):
        if not self.allow_writes:
            raise AssertionError(f"canary touched a write endpoint ({what}) unexpectedly")

    def place_limit(self, body):
        self._write("place_limit")
        self.placed.append(body)
        order_id = f"order-{len(self.placed)}"
        # Fill-or-kill never rests on the book; only GTC orders do. Modelling
        # that is the difference between this fake and a misleading one.
        if str(body.get("timeInForce")).upper() != "FOK":
            self.open_rows.append(
                {"orderId": order_id, "customerOrderId": body.get("customerOrderId")}
            )
        return {"id": order_id}

    def cancel_order(self, pair, order_id):
        self._write("cancel_order")
        if self.cancel_error:
            raise ValrError(self.cancel_error)
        self.cancelled.append(order_id)
        self.open_rows = [
            row for row in self.open_rows if row.get("orderId") != order_id
        ]
        return {}


# ── The invariant the design rests on ──────────────────────────────────────


def test_the_canary_bid_sits_far_below_the_best_bid():
    plan = build_plan(FakeClient(), "XRPZAR")
    assert plan.price < plan.best_bid
    assert plan.price <= plan.best_bid * Decimal("0.5")
    # ...and therefore nowhere near the ask it would have to cross to fill.
    assert plan.price < plan.best_ask


def test_price_is_rounded_down_to_the_tick_never_up():
    """Rounding up is the one direction that could move price toward the book."""
    client = FakeClient(specs=[spec(tick="0.07")], market=summary(bid="40.00"))
    plan = build_plan(client, "XRPZAR")
    assert plan.price % Decimal("0.07") == 0
    assert plan.price <= Decimal("20.00")


def test_quantity_clears_both_exchange_minimums():
    client = FakeClient(
        specs=[spec(min_base="0.3", min_quote="5", decimals=4)], market=summary(bid="40")
    )
    plan = build_plan(client, "XRPZAR")
    assert plan.quantity >= Decimal("0.3")
    assert plan.quantity * plan.price >= Decimal("5")
    assert plan.notional <= MAX_NOTIONAL_ZAR


# ── Every guard refuses rather than sends ──────────────────────────────────


def test_refuses_an_unlisted_pair():
    with pytest.raises(CanaryAborted, match="not listed"):
        build_plan(FakeClient(), "NOPEZAR")


def test_refuses_a_perpetual():
    client = FakeClient(specs=[spec(pair_type=PairType.FUTURE)])
    with pytest.raises(CanaryAborted, match="not SPOT"):
        build_plan(client, "XRPZAR")


def test_refuses_an_inactive_pair():
    with pytest.raises(CanaryAborted, match="not active"):
        build_plan(FakeClient(specs=[spec(active=False)]), "XRPZAR")


def test_refuses_a_non_zar_quote():
    client = FakeClient(specs=[spec(symbol="XRPUSDC", quote="USDC")])
    with pytest.raises(CanaryAborted, match="not ZAR"):
        build_plan(client, "XRPUSDC")


def test_refuses_a_crossed_book():
    client = FakeClient(market=summary(bid="40.10", ask="40.00"))
    with pytest.raises(CanaryAborted, match="crossed or locked"):
        build_plan(client, "XRPZAR")


def test_refuses_a_one_sided_market():
    client = FakeClient(market=summary(bid="0", ask="40"))
    with pytest.raises(CanaryAborted, match="no two-sided market"):
        build_plan(client, "XRPZAR")


def test_refuses_when_the_minimum_order_exceeds_the_notional_cap():
    """A pair whose minimum is large must be declined, not shrunk."""
    client = FakeClient(
        specs=[spec(min_quote=str(MAX_NOTIONAL_ZAR * 3))], market=summary(bid="40")
    )
    with pytest.raises(CanaryAborted, match="exceeds the .* cap"):
        build_plan(client, "XRPZAR")


def test_refuses_when_the_tick_rounds_the_price_to_zero():
    client = FakeClient(specs=[spec(tick="100")], market=summary(bid="40", ask="41"))
    with pytest.raises(CanaryAborted, match="rounds the canary price to zero"):
        build_plan(client, "XRPZAR")


# ── Dry run really is dry ──────────────────────────────────────────────────


def test_dry_run_sends_nothing(tmp_path):
    """FakeClient raises on any write, so reaching the end proves no order."""
    client = FakeClient(allow_writes=False)
    report = run_canary(client, "XRPZAR", armed=False, receipt_path=tmp_path / "r.json")
    assert report.ok
    assert client.placed == []
    assert [s.name for s in report.steps] == [
        "auth",
        "order_types",
        "plan",
        "clean_slate",
        "dry_run",
    ]


def test_dry_run_receipt_does_not_claim_the_path_is_proven(tmp_path):
    receipt_path = tmp_path / "r.json"
    run_canary(FakeClient(), "XRPZAR", armed=False, receipt_path=receipt_path)
    receipt = json.loads(receipt_path.read_text())
    assert receipt["armed"] is False
    assert receipt["proven"] == []
    assert receipt["still_unproven"]


# ── Preconditions that would have failed live ──────────────────────────────


def test_aborts_without_trade_permission(tmp_path):
    client = FakeClient(permissions=["View access"])
    with pytest.raises(CanaryAborted, match="trade permission"):
        run_canary(client, "XRPZAR", armed=False, receipt_path=tmp_path / "r.json")


def test_aborts_when_the_pair_lacks_stop_loss_support(tmp_path):
    """_execute_spot_long needs STOP_LOSS_LIMIT; better to learn it here."""
    client = FakeClient(types={"LIMIT"})
    with pytest.raises(CanaryAborted, match="STOP_LOSS_LIMIT"):
        run_canary(client, "XRPZAR", armed=False, receipt_path=tmp_path / "r.json")


def test_aborts_when_a_previous_canary_is_still_resting(tmp_path):
    client = FakeClient(open_rows=[{"orderId": "old", "customerOrderId": f"{ORDER_TAG}-1"}])
    with pytest.raises(CanaryAborted, match="previous run are still open"):
        run_canary(client, "XRPZAR", armed=False, receipt_path=tmp_path / "r.json")


def test_unrelated_open_orders_are_left_alone(tmp_path):
    """The sweep must recognise only its own litter."""
    client = FakeClient(open_rows=[{"orderId": "mine", "customerOrderId": "user-strategy-7"}])
    report = run_canary(client, "XRPZAR", armed=False, receipt_path=tmp_path / "r.json")
    assert report.ok


# ── Armed run ──────────────────────────────────────────────────────────────


def test_armed_run_places_cancels_and_leaves_nothing(tmp_path):
    client = FakeClient(allow_writes=True)
    report = run_canary(client, "XRPZAR", armed=True, receipt_path=tmp_path / "r.json")
    assert report.ok, [s.render() for s in report.steps]
    assert len(client.placed) == 2
    assert report.residual_order_ids == []
    assert client.open_rows == []


def test_the_fok_order_is_fill_or_kill_and_the_resting_order_is_post_only():
    """The two properties that make each order unable to hurt us."""
    client = FakeClient(allow_writes=True)
    run_canary(client, "XRPZAR", armed=True)
    fok, rest = client.placed
    assert fok["timeInForce"] == "FOK" and fok["postOnly"] is False
    assert rest["timeInForce"] == "GTC" and rest["postOnly"] is True
    assert fok["side"] == rest["side"] == "BUY"


def test_both_orders_are_tagged_so_the_sweep_can_find_them():
    client = FakeClient(allow_writes=True)
    run_canary(client, "XRPZAR", armed=True)
    assert all(ORDER_TAG in body["customerOrderId"] for body in client.placed)
    assert all(len(body["customerOrderId"]) <= 50 for body in client.placed)


def test_a_filled_fok_is_escalated_not_reported_as_a_pass():
    """Impossible by construction, so if it happens, say so loudly."""
    client = FakeClient(allow_writes=True, completed_status="Filled", completed_filled="5")
    with pytest.raises(CanaryResidual, match="FILLED"):
        run_canary(client, "XRPZAR", armed=True)


def test_the_resting_order_is_cancelled_even_if_confirmation_fails(monkeypatch):
    """The finally block is the difference between a failed test and a live bid."""
    monkeypatch.setattr(order_canary, "CONFIRM_TIMEOUT_SECONDS", 0.01)
    client = FakeClient(allow_writes=True, active_status="")
    report = run_canary(client, "XRPZAR", armed=True)
    assert not report.ok  # confirmation failed, honestly reported
    assert client.cancelled  # ...but nothing was left behind
    assert report.residual_order_ids == []


def test_a_failed_cancel_is_reported_as_residual_risk():
    client = FakeClient(allow_writes=True, cancel_error="boom")
    report = run_canary(client, "XRPZAR", armed=True)
    assert not report.ok
    assert report.residual_order_ids
    assert any("STILL OPEN" in s.detail for s in report.steps if s.name == "no_residual")


def test_armed_receipt_records_what_is_still_unproven(tmp_path):
    receipt_path = tmp_path / "r.json"
    run_canary(FakeClient(allow_writes=True), "XRPZAR", armed=True, receipt_path=receipt_path)
    receipt = json.loads(receipt_path.read_text())
    assert receipt["ok"] is True and receipt["armed"] is True
    joined = " ".join(receipt["still_unproven"])
    assert "place_spot_stop_limit" in joined
    assert "real fill" in joined


# ── The acknowledgement ────────────────────────────────────────────────────


def test_canary_ack_is_its_own_key_not_the_live_trading_one(monkeypatch):
    monkeypatch.delenv("BREAKWATER_CANARY_ACK", raising=False)
    assert not canary_ack_ok()
    monkeypatch.setenv("BREAKWATER_LIVE_ACK", "I_ACCEPT_BREAKWATER_LIVE_RISK")
    assert not canary_ack_ok()
    monkeypatch.setenv("BREAKWATER_CANARY_ACK", "I_ACCEPT_BREAKWATER_CANARY_ORDERS")
    assert canary_ack_ok()
