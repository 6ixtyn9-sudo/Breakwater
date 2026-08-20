from datetime import datetime, timezone
from decimal import Decimal

from breakwater.models import MarketSummary, PairSpec, PairType, PerpSymbol
from breakwater.universe import (
    UniverseRow,
    UniverseSnapshot,
    ingest_universe,
    is_legacy_universe,
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


def test_ranked_perp_drops_xyz_inside_rank_window_without_tail_fill():
    as_of = datetime.now(timezone.utc).isoformat()
    rows = [
        UniverseRow(
            symbol="XYZ:NVDAUSDC", kind="PERP", base="XYZ:NVDA", quote="USDC",
            active=True, liquidity_rank=1, quote_volume=Decimal("9e8"),
            mark_price=Decimal("200"), max_leverage=Decimal("10"),
            min_notional=Decimal("11"), min_margin=Decimal("2"), as_of=as_of,
        ),
        UniverseRow(
            symbol="BTCUSDC", kind="PERP", base="BTC", quote="USDC",
            active=True, liquidity_rank=2, quote_volume=Decimal("8e8"),
            mark_price=Decimal("60000"), max_leverage=Decimal("40"),
            min_notional=Decimal("11"), min_margin=Decimal("2"), as_of=as_of,
        ),
        UniverseRow(
            symbol="XYZ:GOLDUSDC", kind="PERP", base="XYZ:GOLD", quote="USDC",
            active=True, liquidity_rank=3, quote_volume=Decimal("7e8"),
            mark_price=Decimal("4000"), max_leverage=Decimal("25"),
            min_notional=Decimal("11"), min_margin=Decimal("2"), as_of=as_of,
        ),
        UniverseRow(
            symbol="ETHUSDC", kind="PERP", base="ETH", quote="USDC",
            active=True, liquidity_rank=4, quote_volume=Decimal("6e8"),
            mark_price=Decimal("2000"), max_leverage=Decimal("25"),
            min_notional=Decimal("11"), min_margin=Decimal("2"), as_of=as_of,
        ),
        UniverseRow(
            symbol="SOLUSDC", kind="PERP", base="SOL", quote="USDC",
            active=True, liquidity_rank=5, quote_volume=Decimal("5e8"),
            mark_price=Decimal("80"), max_leverage=Decimal("20"),
            min_notional=Decimal("11"), min_margin=Decimal("2"), as_of=as_of,
        ),
    ]
    snapshot = UniverseSnapshot(rows=tuple(rows), as_of=as_of)
    # Top-2 window is NVDA + BTC; drop xyz → BTC only. Do not pull ETH.
    assert snapshot.ranked("PERP", 2) == ["BTCUSDC"]
    assert snapshot.ranked("PERP", 2, mappable_only=False) == [
        "XYZ:NVDAUSDC",
        "BTCUSDC",
    ]
    assert snapshot.ranked("PERP", 4) == ["BTCUSDC", "ETHUSDC"]
    assert snapshot.ranked("PERP", 10) == ["BTCUSDC", "ETHUSDC", "SOLUSDC"]


def test_legacy_universe_with_zero_perp_volumes_is_detected():
    from breakwater.universe import ingest_universe

    fresh = ingest_universe(FakeClient())
    rows = []
    for row in fresh.rows:
        rows.append(UniverseRow(
            symbol=row.symbol, kind=row.kind, base=row.base, quote=row.quote,
            active=row.active, liquidity_rank=row.liquidity_rank,
            quote_volume=Decimal(0) if row.kind == "PERP" else row.quote_volume,
            mark_price=row.mark_price, max_leverage=row.max_leverage,
            min_notional=row.min_notional, min_margin=row.min_margin,
            as_of=row.as_of,
        ))
    legacy = UniverseSnapshot(rows=tuple(rows), as_of=fresh.as_of)
    assert is_legacy_universe(legacy) is True
    assert is_legacy_universe(fresh) is False
