import csv
import json
from decimal import Decimal

import pytest

from breakwater.hip3 import (
    HyperliquidHip3Discovery,
    read_hip3_universe,
    write_hip3_dexs,
    write_hip3_universe,
)
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


def annotation_payload():
    return [
        ["xyz:NVDA", {"category": "equities", "keywords": ["stocks", "ai"]}],
        ["xyz:TSLA", {"category": "equities"}],
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
    session = Session(dex_payload(), annotation_payload(), meta_payload())
    snapshot = HyperliquidHip3Discovery(session=session).discover()
    assert len(snapshot.dexs) == 1
    assert [row.coin for row in snapshot.rows] == ["xyz:TSLA", "xyz:NVDA"]
    assert [row.liquidity_rank for row in snapshot.rows] == [1, 2]
    nvda = snapshot.rows[1]
    assert nvda.oracle_mark_deviation_fraction == abs(Decimal("180") - 181) / 181
    assert nvda.margin_mode == "strictIsolated"
    assert nvda.annotation_category == "equities"
    assert nvda.annotation_keywords == "stocks,ai"
    assert session.calls[0][1] == {"type": "perpDexs"}
    assert session.calls[1][1] == {"type": "perpConciseAnnotations"}
    assert session.calls[2][1] == {"type": "metaAndAssetCtxs", "dex": "xyz"}


def test_discover_persists_full_dex_operator_metadata(tmp_path):
    dexs = dex_payload()
    dexs[1].update(
        {
            "feeRecipient": "0x" + "9" * 40,
            "assetToFundingMultiplier": [["xyz:NVDA", "2"], ["xyz:TSLA", "0.5"]],
            "assetToStreamingOiCap": [["xyz:NVDA", "1000000"]],
            "maxZlpLeverage": 10,
        }
    )
    session = Session(dexs, annotation_payload(), meta_payload())
    snapshot = HyperliquidHip3Discovery(session=session).discover()
    assert snapshot.dex_metadata[0]["feeRecipient"] == "0x" + "9" * 40
    assert snapshot.dex_metadata[0]["assetToFundingMultiplier"] == [
        ["xyz:NVDA", "2"],
        ["xyz:TSLA", "0.5"],
    ]
    # perpDexs is fetched exactly once per discovery run.
    assert [call[1]["type"] for call in session.calls] == [
        "perpDexs",
        "perpConciseAnnotations",
        "metaAndAssetCtxs",
    ]
    path = tmp_path / "hip3" / "dexs.json"
    write_hip3_dexs(path, snapshot)
    persisted = json.loads(path.read_text())
    assert persisted["as_of"] == snapshot.as_of
    assert persisted["dexs"][0]["name"] == "xyz"
    assert persisted["dexs"][0]["feeRecipient"] == "0x" + "9" * 40
    assert persisted["dexs"][0]["assetToFundingMultiplier"][0] == ["xyz:NVDA", "2"]


def test_rejects_instrument_that_loses_dex_identity():
    payload = meta_payload()
    payload[0]["universe"][0]["name"] = "NVDA"
    with pytest.raises(PerpVenueError, match="does not preserve DEX prefix"):
        HyperliquidHip3Discovery(session=Session(dex_payload(), annotation_payload(), payload)).discover()


def test_writes_dedicated_hip3_universe(tmp_path):
    snapshot = HyperliquidHip3Discovery(session=Session(dex_payload(), annotation_payload(), meta_payload())).discover()
    path = tmp_path / "hip3" / "universe.csv"
    write_hip3_universe(path, snapshot)
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["dex"] == "xyz"
    assert rows[0]["coin"] == "xyz:TSLA"
    loaded = read_hip3_universe(path)
    assert loaded is not None
    assert loaded.rows[1].annotation_category == "equities"
    assert loaded.rows[1].annotation_keywords == "stocks,ai"
    # The universe CSV carries no operator metadata; snapshots rebuilt from
    # it fall back to the empty default.
    assert loaded.dex_metadata == ()


def test_market_session_is_derived_from_class_not_a_variable():
    """Sessions come from the market class, never an operator hour variable.
    Equity-like classes are gated to NYSE regular hours (DST-aware);
    24/7 classes are ungated; unknown classes fail closed."""
    from datetime import datetime, timezone

    from breakwater.hip3 import (
        hip3_in_market_session,
        hip3_session_restricted,
        hip3_slice_market_class,
    )

    # Class parsing (class may itself contain underscores).
    assert (
        hip3_slice_market_class("hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h12")
        == "equity"
    )
    assert (
        hip3_slice_market_class("hip3_io_provisional_equity_c0:feat:0:LONG:h5")
        == "provisional_equity"
    )
    assert hip3_slice_market_class("hip3_mkts_index_c0:feat:0:LONG:h3") == "index"
    assert hip3_slice_market_class("feat:0:LONG") is None

    utc = timezone.utc
    # DST-aware NYSE session (09:30-16:00 America/New_York).
    assert hip3_in_market_session("equity", datetime(2026, 8, 25, 14, 0, tzinfo=utc))  # 10:00 ET
    assert not hip3_in_market_session("equity", datetime(2026, 8, 25, 13, 0, tzinfo=utc))  # 09:00 ET pre-open
    assert hip3_in_market_session("equity", datetime(2026, 1, 15, 15, 0, tzinfo=utc))  # winter 10:00 ET
    assert not hip3_in_market_session("equity", datetime(2026, 1, 15, 14, 0, tzinfo=utc))  # winter pre-open
    assert not hip3_in_market_session("equity", datetime(2026, 8, 22, 15, 0, tzinfo=utc))  # Saturday

    # 24/7 classes ungated; unknown/missing fail closed.
    assert hip3_in_market_session("builder_crypto", datetime(2026, 8, 25, 3, 0, tzinfo=utc))
    assert hip3_in_market_session("fx", datetime(2026, 8, 25, 3, 0, tzinfo=utc))
    assert not hip3_in_market_session("wat", datetime(2026, 8, 25, 15, 0, tzinfo=utc))
    assert not hip3_in_market_session(None, datetime(2026, 8, 25, 15, 0, tzinfo=utc))

    assert hip3_session_restricted("equity") is True
    assert hip3_session_restricted("provisional_equity") is True
    assert hip3_session_restricted("index") is True
    assert hip3_session_restricted("builder_crypto") is False
