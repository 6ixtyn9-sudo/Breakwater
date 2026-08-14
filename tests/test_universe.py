from datetime import datetime, timezone
from decimal import Decimal

from breakwater.models import MarketSummary, PairSpec, PairType, PerpSymbol
from breakwater.universe import (
    ingest_universe,
    read_universe,
    write_universe,
)


def spot_spec(symbol, base=None):
    return PairSpec(
        symbol=symbol,
        base_currency=base or symbol[:3],
        quote_currency="ZAR",
        active=True,
        min_base=Decimal("0.001"),
        max_base=Decimal("100"),
        min_quote=Decimal("10"),
        max_quote=Decimal("100000"),
        tick_size=Decimal("0.01"),
        base_decimal_places=3,
        pair_type=PairType.SPOT,
    )


def summary(pair, volume):
    return MarketSummary(
        pair=pair,
        bid=Decimal("100"),
        ask=Decimal("100.1"),
        last=Decimal("100"),
        mark=Decimal("100"),
        quote_volume=Decimal(volume),
        timestamp=datetime.now(timezone.utc),
    )


class FakeClient:
    def pairs(self, pair_type=None):
        return [
            spot_spec("BTCZAR"), spot_spec("ETHZAR"), spot_spec("XRPZAR"),
            spot_spec("USDTZAR", "USDT"), spot_spec("USDCZAR", "USDC"),
        ]

    def market_summaries(self):
        return [
            summary("BTCZAR", "900000"),
            summary("ETHZAR", "500000"),
            summary("XRPZAR", "100000"),
        ]

    def perps_symbol_info(self):
        return [
            PerpSymbol(
                pair="BTCUSDC",
                base_asset="BTC",
                max_leverage=Decimal("10"),
                min_notional=Decimal("11"),
                min_margin=Decimal("2"),
                mark_price=Decimal("1500"),
                price_decimal_places=6,
                volume=Decimal("900000"),
                open_interest=Decimal("1200"),
                funding_rate=Decimal("0.00001"),
            ),
            PerpSymbol(
                pair="ETHUSDC",
                base_asset="ETH",
                max_leverage=Decimal("10"),
                min_notional=Decimal("11"),
                min_margin=Decimal("2"),
                mark_price=Decimal("90"),
                price_decimal_places=6,
                volume=Decimal("400000"),
                open_interest=Decimal("800"),
                funding_rate=Decimal("0.00002"),
            ),
        ]


def test_universe_ingests_all_spot_and_perp_symbols():
    snapshot = ingest_universe(FakeClient())
    assert len(snapshot.symbols("SPOT")) == 3
    assert "USDTZAR" not in snapshot.symbols("SPOT")
    assert len(snapshot.symbols("PERP")) == 2
    assert snapshot.ranked("SPOT", 1) == ["BTCZAR"]
    assert snapshot.ranked("PERP", 1) == ["BTCUSDC"]


def test_universe_roundtrip(tmp_path):
    snapshot = ingest_universe(FakeClient())
    path = tmp_path / "universe.csv"
    write_universe(path, snapshot)
    loaded = read_universe(path)
    assert loaded is not None
    assert len(loaded.rows) == len(snapshot.rows)
    assert loaded.symbols("SPOT") == snapshot.symbols("SPOT")


def test_missing_universe_file_reads_none(tmp_path):
    assert read_universe(tmp_path / "missing.csv") is None
