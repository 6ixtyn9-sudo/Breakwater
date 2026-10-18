from __future__ import annotations

import csv
import gzip
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from breakwater import positioning as pos

UNIVERSE_CSV = (
    "symbol,kind,base,quote,active,liquidity_rank,quote_volume,mark_price,"
    "max_leverage,min_notional,min_margin,as_of,venue\n"
    "BTCUSDC,PERP,BTC,USDC,True,1,1000,100,50,10,1,2026-10-18T00:00:00+00:00,hyperliquid\n"
    "KPEPEUSDC,PERP,KPEPE,USDC,True,2,500,0.01,10,10,1,2026-10-18T00:00:00+00:00,hyperliquid\n"
    "DEADUSDC,PERP,DEAD,USDC,False,3,0,1,10,10,1,2026-10-18T00:00:00+00:00,hyperliquid\n"
    "BTCZAR,SPOT,BTC,ZAR,True,1,1000,100,1,10,1,2026-10-18T00:00:00+00:00,valr\n"
)

META = [
    {"universe": [{"name": "BTC"}, {"name": "kPEPE"}, {"name": "xyz:GOLD"}, {"name": "DEAD"}, {"name": "kBONK"}]},
    [
        {
            "markPx": "100.0", "oraclePx": "99.0", "midPx": "100.05", "premium": "0.0101",
            "funding": "0.0000125", "openInterest": "1500", "dayNtlVlm": "123456789",
        },
        {
            "markPx": "0.01", "oraclePx": "0.01", "midPx": "0.01", "premium": "0",
            "funding": "-0.00005", "openInterest": "2000000", "dayNtlVlm": "1000",
        },
        {"markPx": "4000", "oraclePx": "4000", "funding": "0", "openInterest": "1"},
        {"markPx": "1", "oraclePx": "1", "funding": "0", "openInterest": "0"},
        {"markPx": "0.00001", "oraclePx": "0.00001", "funding": "0", "openInterest": "5"},
    ],
]

BOOK = {
    "BTC": {
        "levels": [
            [{"px": "100", "sz": "2"}, {"px": "99", "sz": "1"}],
            [{"px": "101", "sz": "1"}],
        ]
    },
    "kPEPE": {"levels": [[{"px": "0.01", "sz": "100"}], [{"px": "0.011", "sz": "100"}]]},
    "kBONK": {"levels": [[{"px": "0.00001", "sz": "1"}], [{"px": "0.000011", "sz": "1"}]]},
}


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self._payload = payload
        self.status_code = status
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, *, meta=META, books=BOOK, funding=None, fail_books=(), rate_limit_once=False):
        self.calls = []
        self.meta = meta
        self.books = books
        self.funding = funding or {}
        self.fail_books = set(fail_books)
        self.rate_limit_once = rate_limit_once

    def post(self, url, json=None, timeout=None):
        self.calls.append(json)
        kind = json["type"]
        if kind == "metaAndAssetCtxs":
            return FakeResponse(self.meta)
        if kind == "l2Book":
            coin = json["coin"]
            if self.rate_limit_once:
                self.rate_limit_once = False
                return FakeResponse(None, status=429, headers={"Retry-After": "0"})
            if coin in self.fail_books:
                return FakeResponse(None, status=500)
            return FakeResponse(self.books[coin])
        if kind == "fundingHistory":
            rows = self.funding.get(json["coin"], [])
            page = [r for r in rows if json["startTime"] <= r["time"] <= json["endTime"]][:2]
            return FakeResponse(page)
        raise AssertionError(kind)


@pytest.fixture
def universe(tmp_path: Path) -> Path:
    path = tmp_path / "universe.csv"
    path.write_text(UNIVERSE_CSV)
    return path


def _read(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_context_row_parses_and_derives_oi_notional():
    row = pos.context_row("BTC", META[1][0])
    assert row["mark_px"] == "100"
    assert row["funding_hourly"] == "1.25e-05"
    assert float(row["oi_notional_usd"]) == pytest.approx(150000.0)
    assert float(row["premium"]) == pytest.approx(0.0101)


def test_context_row_derives_premium_when_missing():
    row = pos.context_row("X", {"markPx": "101", "oraclePx": "100"})
    assert float(row["premium"]) == pytest.approx(0.01)
    assert row["open_interest"] == ""
    assert row["oi_notional_usd"] == ""


def test_book_metrics_depth_and_imbalance():
    bids = [(100.0, 2.0), (99.0, 1.0)]
    asks = [(101.0, 1.0)]
    m = pos.book_metrics(bids, asks)
    assert m["bid_px"] == "100" and m["ask_px"] == "101"
    assert float(m["spread_bps"]) == pytest.approx(1.0 / 100.5 * 10000)
    assert float(m["bid_depth_1"]) == 200.0 and float(m["ask_depth_1"]) == 101.0
    assert float(m["bid_depth_5"]) == 299.0
    assert float(m["imbalance_1"]) == pytest.approx((200 - 101) / 301)
    assert float(m["imbalance_10"]) == pytest.approx((299 - 101) / 400)
    assert m["n_bid_levels"] == "2" and m["n_ask_levels"] == "1"


def test_book_metrics_empty_side_is_blank_not_error():
    m = pos.book_metrics([], [(1.0, 1.0)])
    assert m["bid_px"] == "" and m["spread_bps"] == ""
    assert float(m["imbalance_1"]) == -1.0
    assert pos.book_metrics([], [])["imbalance_5"] == ""


def test_fetch_asset_contexts_skips_hip3_names():
    out = pos.fetch_asset_contexts(FakeSession())
    assert set(out) == {"BTC", "kPEPE", "DEAD", "kBONK"}


def test_universe_coins_active_perps_only_with_alias_and_cap(universe):
    assert pos.universe_coins(universe) == ["BTC", "kPEPE"]
    assert pos.universe_coins(universe, max_coins=1) == ["BTC"]


def test_snapshot_writes_rows_and_is_idempotent_per_hour(tmp_path, universe):
    now = datetime(2026, 10, 18, 14, 37, tzinfo=timezone.utc)
    session = FakeSession()
    summary = pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=universe, session=session, now=now, sleep_seconds=0
    )
    assert summary["rows"] == 2 and summary["coins"] == 2 and summary["book_errors"] == 0
    path = Path(summary["path"])
    assert path.name == "2026-W42.csv"
    rows = _read(path)
    assert [r["coin"] for r in rows] == ["BTC", "kPEPE"]
    assert rows[0]["snapshot_hour"] == "2026-10-18T14:00Z"
    assert float(rows[0]["imbalance_1"]) == pytest.approx((200 - 101) / 301)
    assert rows[1]["funding_hourly"] == "-5e-05"
    # the alias was used on the wire, the universe name in the file
    assert any(c.get("coin") == "kPEPE" for c in session.calls if c["type"] == "l2Book")

    # Same hour, 20 minutes later: no new rows, no network.
    later = FakeSession()
    again = pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=universe, session=later, now=now + timedelta(minutes=20), sleep_seconds=0
    )
    assert again["skipped_existing_hour"] is True
    assert later.calls == []
    assert len(_read(path)) == 2

    # Next hour appends.
    pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=universe, session=FakeSession(), now=now + timedelta(hours=1), sleep_seconds=0
    )
    assert len(_read(path)) == 4


def test_snapshot_resolves_k_prefixed_coins_by_case_and_reports_missing(tmp_path):
    # KBONK is not in HL_COIN_ALIASES (only KPEPE is); the venue calls it kBONK.
    # GHOST is in the universe but not on the venue at all.
    path = tmp_path / "universe.csv"
    path.write_text(
        UNIVERSE_CSV
        + "KBONKUSDC,PERP,KBONK,USDC,True,4,400,0.00001,10,10,1,2026-10-18T00:00:00+00:00,hyperliquid\n"
        + "GHOSTUSDC,PERP,GHOST,USDC,True,5,300,1,10,10,1,2026-10-18T00:00:00+00:00,hyperliquid\n"
    )
    now = datetime(2026, 10, 18, 14, tzinfo=timezone.utc)
    session = FakeSession()
    summary = pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=path, session=session, now=now, sleep_seconds=0
    )
    assert summary["coins"] == 4 and summary["rows"] == 3 and summary["book_errors"] == 0
    assert summary["missing_coins"] == ["GHOST"]
    rows = _read(Path(summary["path"]))
    assert [r["coin"] for r in rows] == ["BTC", "kPEPE", "kBONK"]
    assert rows[2]["open_interest"] == "5"
    assert any(c.get("coin") == "kBONK" for c in session.calls if c["type"] == "l2Book")


def test_snapshot_book_failure_keeps_context_row(tmp_path, universe):
    now = datetime(2026, 10, 18, 14, tzinfo=timezone.utc)
    summary = pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=universe, session=FakeSession(fail_books={"BTC"}), now=now, sleep_seconds=0
    )
    assert summary["rows"] == 2 and summary["book_errors"] == 1
    rows = _read(Path(summary["path"]))
    btc = rows[0]
    assert btc["open_interest"] == "1500" and btc["bid_px"] == "" and btc["book_error"]
    assert rows[1]["book_error"] == ""


def test_snapshot_retries_on_429(tmp_path, universe):
    now = datetime(2026, 10, 18, 14, tzinfo=timezone.utc)
    session = FakeSession(rate_limit_once=True)
    summary = pos.run_positioning_snapshot(
        data_dir=tmp_path, universe_path=universe, session=session, now=now, sleep_seconds=0
    )
    assert summary["book_errors"] == 0
    assert sum(1 for c in session.calls if c["type"] == "l2Book") == 3


def test_weekly_rotation_gzips_previous_week(tmp_path, universe):
    sunday = datetime(2026, 10, 25, 23, tzinfo=timezone.utc)
    monday = sunday + timedelta(hours=1)
    for when in (sunday, monday):
        pos.run_positioning_snapshot(
            data_dir=tmp_path, universe_path=universe, session=FakeSession(), now=when, sleep_seconds=0
        )
    directory = pos.positioning_dir(tmp_path)
    names = sorted(p.name for p in directory.iterdir())
    assert names == ["2026-W43.csv.gz", "2026-W44.csv"]
    with gzip.open(directory / "2026-W43.csv.gz", "rt", newline="") as handle:
        packed = list(csv.DictReader(handle))
    assert len(packed) == 2 and packed[0]["snapshot_hour"] == "2026-10-25T23:00Z"
    everything = pos.read_snapshots(directory)
    assert len(everything) == 4


def test_funding_backfill_paginates_dedupes_and_resumes(tmp_path, universe):
    now = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)
    base = int((now - timedelta(hours=5)).timestamp() * 1000)
    hour = 3_600_000
    funding = {
        "BTC": [{"time": base + i * hour, "fundingRate": f"0.0000{i}", "premium": "0.001"} for i in range(5)],
        "kPEPE": [{"time": base, "fundingRate": "-0.00001", "premium": "0"}],
    }
    session = FakeSession(funding=funding)
    summary = pos.run_funding_backfill(
        data_dir=tmp_path, universe_path=universe, days=1, session=session, now=now
    )
    assert summary["added"] == 6 and summary["rows"] == 6 and summary["errors"] == []
    rows = _read(Path(summary["path"]))
    assert [r["coin"] for r in rows] == ["BTC"] * 5 + ["kPEPE"]
    assert rows[0]["funding_rate"] == "0.00000"
    assert rows[0]["time"].startswith("2026-10-18T07:00:00")
    # 5 BTC entries at 2 per page -> 3 pages + empty terminator; 1 + terminator for kPEPE
    assert sum(1 for c in session.calls if c["type"] == "fundingHistory") == 6

    # Second run: nothing new, resumes after the newest stored point.
    session2 = FakeSession(funding=funding)
    again = pos.run_funding_backfill(
        data_dir=tmp_path, universe_path=universe, days=1, session=session2, now=now
    )
    assert again["added"] == 0 and again["rows"] == 6
    btc_calls = [c for c in session2.calls if c["type"] == "fundingHistory" and c["coin"] == "BTC"]
    assert btc_calls[0]["startTime"] > base + 4 * hour
