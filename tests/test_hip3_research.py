from dataclasses import replace
from decimal import Decimal

from breakwater.hip3 import Hip3UniverseRow
from breakwater.hip3_research import _candidate_rows, classify_market


def row(coin="xyz:NVDA", **changes):
    base = Hip3UniverseRow(
        dex=coin.split(":", 1)[0],
        dex_full_name="DEX",
        deployer="0x1",
        oracle_updater="0x2",
        coin=coin,
        collateral_token=0,
        active=True,
        liquidity_rank=1,
        day_notional_volume=Decimal("100000"),
        mark_price=Decimal("100"),
        oracle_price=Decimal("100"),
        previous_day_price=Decimal("99"),
        oracle_mark_deviation_fraction=Decimal("0"),
        funding_rate=Decimal("0"),
        open_interest=Decimal("10"),
        max_leverage=Decimal("10"),
        size_decimals=3,
        margin_mode="strictIsolated",
        growth_mode="enabled",
        as_of="2026-08-23T00:00:00+00:00",
    )
    return replace(base, **changes)


def test_market_classes_keep_builder_crypto_out_of_equity_pool():
    native = {"BTC", "ETH", "SOL"}
    assert classify_market("hyna:BTC", native) == "builder_crypto"
    assert classify_market("xyz:EUR", native) == "fx"
    assert classify_market("xyz:BRENTOIL", native) == "commodity"
    assert classify_market("xyz:SP500", native) == "index"
    assert classify_market("xyz:NVDA", native) == "provisional_equity"


def test_research_candidates_fail_closed_on_oracle_and_activity():
    rows = (
        row("xyz:NVDA", day_notional_volume=Decimal("200000")),
        row("hyna:BTC", day_notional_volume=Decimal("300000")),
        row("xyz:TSLA", oracle_mark_deviation_fraction=Decimal("0.03")),
        row("xyz:AMZN", active=False),
        row("xyz:META", day_notional_volume=Decimal("0")),
    )
    selected = _candidate_rows(
        rows,
        native_crypto={"BTC"},
        max_pairs=60,
        max_oracle_deviation=Decimal("0.02"),
    )
    assert [(item.coin, market_class) for item, market_class in selected] == [
        ("xyz:NVDA", "provisional_equity")
    ]
