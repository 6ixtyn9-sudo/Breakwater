from decimal import Decimal

import pytest

from breakwater.hyperliquid import (
    TESTNET_API_URL,
    HyperliquidReadOnlyVenue,
    validate_account_address,
)
from breakwater.models import Side
from breakwater.perp_venue import (
    PerpVenueError,
    PerpWriteBlocked,
    assess_native_stop_protection,
)


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class Session:
    def __init__(self, *payloads):
        self.payloads = list(payloads)
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json, timeout))
        return Response(self.payloads.pop(0))


def metadata():
    return [
        {
            "universe": [
                {"name": "BTC", "szDecimals": 5, "maxLeverage": 40},
                {"name": "xyz:NVDA", "szDecimals": 3, "maxLeverage": 10},
            ]
        },
        [
            {
                "markPx": "65000.5",
                "oraclePx": "65001",
                "funding": "0.00001",
                "openInterest": "123.4",
                "dayNtlVlm": "5000000",
            },
            {
                "markPx": "180",
                "oraclePx": "181",
                "funding": "0",
                "openInterest": "5",
                "dayNtlVlm": "1000",
            },
        ],
    ]


def test_instruments_normalize_precision_and_exclude_hip3():
    session = Session(metadata())
    venue = HyperliquidReadOnlyVenue(session=session)
    instruments = venue.instruments()
    assert len(instruments) == 1
    btc = instruments[0]
    assert btc.symbol == "BTCUSDC"
    assert btc.asset_id == 0
    assert btc.size_step == Decimal("0.00001")
    assert btc.max_price_decimals == 1
    assert btc.max_significant_figures == 5
    assert btc.mark_price == Decimal("65000.5")
    assert session.calls[0][1] == {"type": "metaAndAssetCtxs"}


def test_coverage_is_explicit_about_builder_and_missing_symbols():
    venue = HyperliquidReadOnlyVenue(session=Session(metadata()))
    coverage = venue.coverage(["BTCUSDC", "xyz:NVDAUSDC", "MISSINGUSDC"])
    assert coverage.tradable == ("BTCUSDC",)
    assert coverage.intentionally_excluded == ("XYZ:NVDAUSDC",)
    assert coverage.unavailable == ("MISSINGUSDC",)


def test_account_snapshot_normalizes_positions_and_orders():
    state = {
        "marginSummary": {
            "accountValue": "100.5",
            "totalMarginUsed": "10",
            "totalNtlPos": "50",
        },
        "withdrawable": "90.5",
        "assetPositions": [
            {
                "position": {
                    "coin": "BTC",
                    "szi": "-0.001",
                    "entryPx": "66000",
                    "positionValue": "65",
                    "unrealizedPnl": "1.25",
                    "liquidationPx": "80000",
                    "leverage": {"type": "isolated", "value": 2},
                }
            }
        ],
    }
    orders = [
        {
            "coin": "BTC",
            "oid": 123,
            "cloid": "0xabc",
            "side": "B",
            "limitPx": "64000",
            "sz": "0.001",
            "origSz": "0.002",
            "reduceOnly": True,
            "isTrigger": True,
            "isPositionTpsl": True,
            "orderType": "Stop Market",
            "triggerPx": "64000",
            "triggerCondition": "mark price above 64000",
            "timestamp": 123456,
        }
    ]
    venue = HyperliquidReadOnlyVenue(session=Session(metadata(), state, orders))
    snapshot = venue.account_snapshot("0x1111111111111111111111111111111111111111")
    assert snapshot.account_value == Decimal("100.5")
    assert snapshot.positions[0].side is Side.SELL
    assert snapshot.positions[0].quantity == Decimal("0.001")
    assert snapshot.open_orders[0].reduce_only is True
    assert snapshot.open_orders[0].side is Side.BUY
    assert venue.session.calls[2][1]["type"] == "frontendOpenOrders"
    protection = assess_native_stop_protection(snapshot)
    assert protection.all_protected is True
    assert protection.protected_symbols == ("BTCUSDC",)


def test_account_snapshot_fails_closed_on_unknown_position_coin():
    state = {
        "marginSummary": {
            "accountValue": "100",
            "totalMarginUsed": "0",
            "totalNtlPos": "0",
        },
        "withdrawable": "100",
        "assetPositions": [
            {
                "position": {
                    "coin": "UNKNOWN",
                    "szi": "1",
                    "entryPx": "1",
                    "positionValue": "1",
                    "leverage": {"value": 1},
                }
            }
        ],
    }
    venue = HyperliquidReadOnlyVenue(session=Session(metadata(), state, []))
    with pytest.raises(PerpVenueError, match="absent from metadata"):
        venue.account_snapshot("0x1111111111111111111111111111111111111111")


def test_testnet_candles_use_testnet_endpoint():
    rows = [
        {
            "t": 1786579200000,
            "o": "100",
            "c": "101",
            "h": "102",
            "l": "99",
            "v": "10",
        },
        {
            "t": 1786582800000,
            "o": "101",
            "c": "102",
            "h": "103",
            "l": "100",
            "v": "11",
        },
    ]
    session = Session(rows)
    venue = HyperliquidReadOnlyVenue(testnet=True, session=session)
    candles = venue.candles("BTCUSDC", count=2)
    assert len(candles) == 2
    assert session.calls[0][0] == f"{TESTNET_API_URL}/info"


def test_read_only_adapter_has_no_write_escape_hatch():
    venue = HyperliquidReadOnlyVenue(session=Session())
    for method in (
        venue.place_entry,
        venue.place_protective_orders,
        venue.cancel_order,
        venue.cancel_all,
    ):
        with pytest.raises(PerpWriteBlocked, match="no signer"):
            method({})


def test_account_address_validation():
    assert validate_account_address("0x" + "a" * 40) == "0x" + "a" * 40
    with pytest.raises(ValueError, match="40 hex"):
        validate_account_address("not-an-address")
