import csv
from decimal import Decimal

import pytest

from breakwater.hip3 import HyperliquidHip3Discovery, write_hip3_universe
from breakwater.perp_venue import PerpVenueError


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


def dex_payload():
    return [
        None,
        {
            "name": "xyz",
            "fullName": "Trade XYZ",
            "deployer": "0x" + "1" * 40,
            "oracleUpdater": "0x" + "2" * 40,
        },
    ]


def meta_payload():
    return [
        {
            "collateralToken": 0,
            "universe": [
                {
                    "name": "xyz:NVDA",
                    "szDecimals": 3,
                    "maxLeverage": 10,
                    "marginMode": "strictIsolated",
                    "growthMode": "enabled",
                },
                {
                    "name": "xyz:TSLA",
                    "szDecimals": 3,
                    "maxLeverage": 10,
                    "marginMode": "strictIsolated",
                    "growthMode": "enabled",
                },
            ],
        },
        [
            {
                "dayNtlVlm": "100000",
                "markPx": "180",
                "oraclePx": "181",
                "prevDayPx": "175",
                "funding": "0.0001",
                "openInterest": "100",
            },
            {
                "dayNtlVlm": "200000",
                "markPx": "300",
                "oraclePx": "300",
                "prevDayPx": "290",
                "funding": "0.0002",
                "openInterest": "200",
            },
        ],
    ]


def test_discovers_and_ranks_hip3_inside_each_dex():
    session = Session(dex_payload(), meta_payload())
    snapshot = HyperliquidHip3Discovery(session=session).discover()
    assert len(snapshot.dexs) == 1
    assert [row.coin for row in snapshot.rows] == ["xyz:TSLA", "xyz:NVDA"]
    assert [row.liquidity_rank for row in snapshot.rows] == [1, 2]
    nvda = snapshot.rows[1]
    assert nvda.oracle_mark_deviation_fraction == abs(Decimal("180") - 181) / 181
    assert nvda.margin_mode == "strictIsolated"
    assert session.calls[0][1] == {"type": "perpDexs"}
    assert session.calls[1][1] == {"type": "metaAndAssetCtxs", "dex": "xyz"}


def test_rejects_instrument_that_loses_dex_identity():
    payload = meta_payload()
    payload[0]["universe"][0]["name"] = "NVDA"
    with pytest.raises(PerpVenueError, match="does not preserve DEX prefix"):
        HyperliquidHip3Discovery(session=Session(dex_payload(), payload)).discover()


def test_writes_dedicated_hip3_universe(tmp_path):
    snapshot = HyperliquidHip3Discovery(session=Session(dex_payload(), meta_payload())).discover()
    path = tmp_path / "hip3" / "universe.csv"
    write_hip3_universe(path, snapshot)
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["dex"] == "xyz"
    assert rows[0]["coin"] == "xyz:TSLA"
