"""Realized-P&L reconciliation: the feed that makes the loss limits real.

Before this existed, RiskStateStore.append_realized_pnl had no call sites
outside tests/test_ledger.py. realized_pnl_events stayed empty, so
RiskManager.check_account always saw daily_pnl_zar == seven_day_pnl_zar == 0
and neither loss limit could ever fire on a live account.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from breakwater.ledger import Ledger
from breakwater.reconcile import realized_pnl_zar, reconcile_realized_pnl
from breakwater.risk import RiskManager, RiskPolicy
from breakwater.risk_state import RiskStateStore

NOW = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


class Client:
    """Only completed_order is consumed, and only fields the executor uses."""

    def __init__(self, orders):
        self.orders = orders
        self.asked = []

    def completed_order(self, order_id):
        self.asked.append(order_id)
        return self.orders[order_id]


def zar(_currency):
    return Decimal(1)


def stores(tmp_path):
    return (
        Ledger(tmp_path / "ledger.db"),
        RiskStateStore(tmp_path / "risk_state.json"),
    )


def live_entry(
    ledger,
    *,
    protection="stop-1",
    entry="100",
    quantity="1",
    side="BUY",
    pair="BTCZAR",
    quote="ZAR",
):
    ledger.append(
        event_id=f"entry-{protection}",
        kind="live_entry",
        payload={
            "strategy_id": "big-wave-BTCZAR-buy",
            "pair": pair,
            "entry_order_id": f"e-{protection}",
            "protection_order_id": protection,
            "filled_quantity": quantity,
            "average_price": entry,
            "side": side,
            "quote_currency": quote,
        },
        occurred_at=NOW - timedelta(hours=2),
        pair=pair,
    )


def filled(price, quantity="1"):
    return {
        "orderStatusType": "Filled",
        "totalExecutedQuantity": quantity,
        "averagePrice": price,
    }


def test_no_live_entries_is_a_no_op(tmp_path):
    """On current committed state this must do nothing at all."""
    ledger, risk_state = stores(tmp_path)
    report = reconcile_realized_pnl(
        client=Client({}), ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )
    assert report.checked == 0
    assert report.booked == 0
    assert report.errors == []
    assert risk_state.daily_pnl(NOW) == Decimal(0)


def test_a_filled_protection_order_books_a_loss(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger, entry="100", quantity="1")
    client = Client({"stop-1": filled("90")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 1
    # gross -10, fees on both legs at 70bps ZAR round trip:
    # (100 + 90) * 35 / 10000 = 0.665
    assert report.booked_zar == Decimal("-10.665")
    assert risk_state.daily_pnl(NOW) == Decimal("-10.665")
    assert ledger.pnl_since(NOW - timedelta(days=1)) == Decimal("-10.665")


def test_a_winner_is_booked_net_of_both_legs(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger, entry="100", quantity="2")
    client = Client({"stop-1": filled("110", quantity="2")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    # gross +20, fees (200 + 220) * 35 / 10000 = 1.47
    assert report.booked_zar == Decimal("18.53")
    assert risk_state.daily_pnl(NOW) == Decimal("18.53")


def test_booking_is_idempotent_across_cycles(tmp_path):
    """The guardian runs hourly. A loss must not be counted twice."""
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger)
    client = Client({"stop-1": filled("90")})

    first = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )
    second = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert first.booked == 1
    assert second.booked == 0
    assert second.checked == 0
    assert risk_state.daily_pnl(NOW) == Decimal("-10.665")


def test_a_resting_protection_order_is_not_booked(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger)
    client = Client({"stop-1": {"orderStatusType": "Active"}})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.still_open == 1
    assert report.booked == 0
    assert risk_state.daily_pnl(NOW) == Decimal(0)


def test_a_cancelled_protection_order_is_flagged_not_booked(tmp_path):
    """A stop that vanished without filling is an unprotected position, not
    a flat trade. Booking it as zero P&L would hide live exposure."""
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger)
    client = Client({"stop-1": {"orderStatusType": "Cancelled"}})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 0
    assert len(report.unprotected) == 1
    assert "stop-1" in report.unprotected[0]


def test_a_partial_exit_stays_open(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger, quantity="2")
    client = Client({"stop-1": filled("90", quantity="1")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 0
    assert report.still_open == 1


def test_a_missing_side_refuses_to_guess(tmp_path):
    ledger, risk_state = stores(tmp_path)
    ledger.append(
        event_id="entry-legacy",
        kind="live_entry",
        payload={
            "pair": "BTCZAR",
            "protection_order_id": "stop-legacy",
            "filled_quantity": "1",
            "average_price": "100",
        },
        occurred_at=NOW,
    )
    client = Client({"stop-legacy": filled("90")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 0
    assert len(report.unsupported) == 1
    assert risk_state.daily_pnl(NOW) == Decimal(0)


def test_a_broken_row_does_not_stop_the_rest(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger, protection="stop-bad", entry="not-a-number")
    live_entry(ledger, protection="stop-good", entry="100")
    client = Client({"stop-bad": filled("90"), "stop-good": filled("90")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 1
    assert len(report.errors) == 1
    assert risk_state.daily_pnl(NOW) == Decimal("-10.665")


def test_reconciliation_never_raises_on_a_broken_client(tmp_path):
    """The guardian is what reports the failure; it must survive it."""
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger)

    class Exploding:
        def completed_order(self, order_id):
            raise RuntimeError("VALR is down")

    report = reconcile_realized_pnl(
        client=Exploding(), ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=zar,
    )

    assert report.booked == 0
    assert len(report.errors) == 1
    assert "VALR is down" in report.errors[0]


def test_non_zar_quote_is_converted(tmp_path):
    ledger, risk_state = stores(tmp_path)
    live_entry(ledger, pair="BTCUSDT", quote="USDT", entry="100", quantity="1")
    client = Client({"stop-1": filled("110")})

    report = reconcile_realized_pnl(
        client=client, ledger=ledger, risk_state=risk_state,
        server_time=NOW, quote_to_zar=lambda c: Decimal("18"),
    )

    # Crypto-quoted spot is 20bps, not 70: (100 + 110) * 10 / 10000 = 0.21
    assert report.booked_zar == Decimal("10") * Decimal("18") - Decimal("0.21") * Decimal("18")


def test_the_daily_loss_limit_now_actually_fires(tmp_path):
    """The whole point. Book enough realized loss and the risk gate closes.

    Run against the pre-fix behaviour (an unfed risk state) this asserts
    False, because daily_pnl_zar was structurally pinned at 0.
    """
    ledger, risk_state = stores(tmp_path)
    policy = RiskPolicy(
        initial_equity_zar=Decimal("510"),
        absolute_equity_floor_zar=Decimal("222.07"),
        max_total_loss_zar=Decimal("109.38"),
        max_drawdown_fraction=Decimal("0.33"),
        risk_per_trade_zar=Decimal("6.63"),
        daily_loss_limit_zar=Decimal("9.94"),
        seven_day_loss_limit_zar=Decimal("19.89"),
        max_aggregate_open_risk_zar=Decimal("6.63"),
        max_position_notional_zar=Decimal("200"),
        max_effective_leverage=Decimal("1"),
        perp_leverage_cap=Decimal("3"),
        max_positions=1,
    )
    manager = RiskManager(policy)

    def gate():
        return manager.check_account(
            equity_zar=Decimal("500"),
            high_water_zar=Decimal("510"),
            daily_pnl_zar=risk_state.daily_pnl(NOW),
            seven_day_pnl_zar=risk_state.seven_day_pnl(NOW),
            open_positions=0,
            aggregate_open_risk_zar=Decimal(0),
        )

    assert gate().allowed is True

    live_entry(ledger, protection="stop-1", entry="100", quantity="1")
    reconcile_realized_pnl(
        client=Client({"stop-1": filled("90")}), ledger=ledger,
        risk_state=risk_state, server_time=NOW, quote_to_zar=zar,
    )
    # -10.665 breaches the 9.94 daily limit.
    verdict = gate()
    assert verdict.allowed is False
    assert "daily loss limit reached" in verdict.reasons


def test_realized_pnl_matches_the_paper_fee_convention():
    """Live and paper must price a round trip the same way, or the shadow
    record stops being comparable to the live record."""
    from breakwater.costs import spot_round_trip_decimal

    entry, exit_price, quantity = Decimal("100"), Decimal("110"), Decimal("3")
    bps = spot_round_trip_decimal("BTCZAR")
    expected_fee = (entry * quantity + exit_price * quantity) * (bps / 2) / Decimal(10000)
    got = realized_pnl_zar(
        side="BUY", entry_price=entry, exit_price=exit_price,
        quantity=quantity, pair="BTCZAR", quote_to_zar=Decimal(1),
    )
    assert got == Decimal("30") - expected_fee
