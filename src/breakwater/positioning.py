"""Positioning snapshots from Hyperliquid (read-only data collection).

Why
---
Every research feature today is derived from hourly OHLCV. The operator
decision of 2026-10-18 is to add *positioning* inputs after the observation
window: funding, open interest, basis/premium and order-book imbalance. Of
those only funding has a history endpoint; the rest exist only as current
state on the venue. If nobody records them during the window, day eight has
one input instead of four. This module records them.

What it does
------------
``run_positioning_snapshot`` takes one hourly snapshot per perp coin in the
universe:

* from one ``metaAndAssetCtxs`` call: mark, oracle, mid, premium, hourly
  funding, open interest, 24h notional volume;
* from one ``l2Book`` call per coin: best bid/ask, spread, cumulative USD
  depth and imbalance at 1, 5 and 10 levels.

Rows are appended to ``localdata/positioning/YYYY-Www.csv`` (ISO week, same
rotation as the paper skip log: open week plain, older weeks gzipped). A
snapshot is keyed by ``snapshot_hour``; a second run inside the same hour is a
no-op, so riding on the 20-40 minute paper cadence yields one row per coin
per hour.

``run_funding_backfill`` pulls ``fundingHistory`` for each coin into
``localdata/positioning/funding_history.csv`` (deduped on coin+time) so the
one input with history is available retroactively.

Nothing here reads a decision or writes one. It is a tape recorder.
"""

from __future__ import annotations

import csv
import gzip
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from breakwater.perpdata import HYPERLIQUID_INFO_URL, pair_to_coin

POSITIONING_DIRNAME = "positioning"
FUNDING_HISTORY_FILENAME = "funding_history.csv"

SNAPSHOT_HEADERS = [
    "snapshot_at",
    "snapshot_hour",
    "coin",
    "mark_px",
    "oracle_px",
    "mid_px",
    "premium",
    "funding_hourly",
    "open_interest",
    "oi_notional_usd",
    "day_ntl_vlm",
    "bid_px",
    "ask_px",
    "spread_bps",
    "bid_depth_1",
    "ask_depth_1",
    "bid_depth_5",
    "ask_depth_5",
    "bid_depth_10",
    "ask_depth_10",
    "imbalance_1",
    "imbalance_5",
    "imbalance_10",
    "n_bid_levels",
    "n_ask_levels",
    "book_error",
]

FUNDING_HEADERS = ["coin", "time", "funding_rate", "premium"]

DEPTH_LEVELS = (1, 5, 10)
RETRY_STATUSES = (429, 500, 502, 503, 504)


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


def _post_info(session, payload: dict, *, info_url: str = HYPERLIQUID_INFO_URL, attempts: int = 3, timeout: int = 20):
    """POST to /info with the same 429/5xx backoff ``perpdata`` uses."""
    requester = session or requests
    response = None
    for attempt in range(attempts):
        response = requester.post(info_url, json=payload, timeout=timeout)
        status = getattr(response, "status_code", 200)
        if status in RETRY_STATUSES and attempt + 1 < attempts:
            headers = getattr(response, "headers", None) or {}
            try:
                delay = float(headers.get("Retry-After"))
            except (TypeError, ValueError):
                delay = 1.0 * (attempt + 1)
            time.sleep(max(delay, 0.1))
            continue
        break
    response.raise_for_status()
    return response.json()


def fetch_asset_contexts(session=None, *, info_url: str = HYPERLIQUID_INFO_URL) -> dict[str, dict]:
    """``{coin: context}`` for native perps (HIP-3 ``dex:asset`` names skipped)."""
    payload = _post_info(session, {"type": "metaAndAssetCtxs"}, info_url=info_url)
    if not isinstance(payload, list) or len(payload) != 2:
        raise RuntimeError("hyperliquid metaAndAssetCtxs response is malformed")
    meta, contexts = payload
    universe = meta.get("universe") if isinstance(meta, dict) else None
    if not isinstance(universe, list) or not isinstance(contexts, list) or len(universe) != len(contexts):
        raise RuntimeError("hyperliquid metaAndAssetCtxs schema is unrecognized")
    out: dict[str, dict] = {}
    for row, context in zip(universe, contexts, strict=True):
        coin = str((row or {}).get("name") or "").strip()
        if not coin or ":" in coin or not isinstance(context, dict):
            continue
        out[coin] = context
    return out


def fetch_l2_book(coin: str, session=None, *, info_url: str = HYPERLIQUID_INFO_URL) -> tuple[list, list]:
    """``(bids, asks)`` as lists of ``(px, sz)`` floats, best first.

    ``coin`` must be the venue's exact (case-sensitive) name as returned by
    ``metaAndAssetCtxs`` — e.g. ``kBONK``, not ``KBONK``.
    """
    payload = _post_info(session, {"type": "l2Book", "coin": coin}, info_url=info_url)
    levels = payload.get("levels") if isinstance(payload, dict) else None
    if not isinstance(levels, list) or len(levels) != 2:
        raise RuntimeError(f"hyperliquid l2Book response for {coin} is malformed")

    def _side(rows):
        out = []
        for level in rows or []:
            try:
                out.append((float(level["px"]), float(level["sz"])))
            except (KeyError, TypeError, ValueError):
                continue
        return out

    return _side(levels[0]), _side(levels[1])


# --------------------------------------------------------------------------
# Pure transforms (unit tested)
# --------------------------------------------------------------------------


def _f(value) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None  # NaN guard


def _fmt(value, digits: int = 10) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}g}"


def context_row(coin: str, context: dict) -> dict:
    mark = _f(context.get("markPx"))
    oracle = _f(context.get("oraclePx"))
    mid = _f(context.get("midPx"))
    oi = _f(context.get("openInterest"))
    premium = _f(context.get("premium"))
    if premium is None and mark is not None and oracle not in (None, 0.0):
        premium = mark / oracle - 1.0
    return {
        "coin": coin,
        "mark_px": _fmt(mark),
        "oracle_px": _fmt(oracle),
        "mid_px": _fmt(mid),
        "premium": _fmt(premium),
        "funding_hourly": _fmt(_f(context.get("funding"))),
        "open_interest": _fmt(oi),
        "oi_notional_usd": _fmt(oi * mark, 12) if oi is not None and mark is not None else "",
        "day_ntl_vlm": _fmt(_f(context.get("dayNtlVlm")), 12),
    }


def book_metrics(bids: list, asks: list) -> dict:
    """Spread, cumulative USD depth and imbalance at DEPTH_LEVELS."""
    out = {
        "bid_px": "",
        "ask_px": "",
        "spread_bps": "",
        "n_bid_levels": str(len(bids)),
        "n_ask_levels": str(len(asks)),
    }
    if bids and asks:
        bid, ask = bids[0][0], asks[0][0]
        out["bid_px"], out["ask_px"] = _fmt(bid), _fmt(ask)
        mid = 0.5 * (bid + ask)
        if mid > 0:
            out["spread_bps"] = _fmt((ask - bid) / mid * 10000.0, 8)
    for k in DEPTH_LEVELS:
        bid_depth = sum(px * sz for px, sz in bids[:k])
        ask_depth = sum(px * sz for px, sz in asks[:k])
        out[f"bid_depth_{k}"] = _fmt(bid_depth, 12)
        out[f"ask_depth_{k}"] = _fmt(ask_depth, 12)
        total = bid_depth + ask_depth
        out[f"imbalance_{k}"] = _fmt((bid_depth - ask_depth) / total, 8) if total > 0 else ""
    return out


def hour_key(now: datetime) -> str:
    return now.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:00Z")


def week_key(now: datetime) -> str:
    year, week, _ = now.astimezone(timezone.utc).isocalendar()
    return f"{year}-W{week:02d}"


# --------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------


def positioning_dir(data_dir: Path) -> Path:
    return Path(data_dir) / POSITIONING_DIRNAME


def snapshot_path(directory: Path, now: datetime) -> Path:
    return directory / f"{week_key(now)}.csv"


def _compress_stale(directory: Path, keep: Path) -> None:
    """Gzip every plain weekly file except the open one (skip-log pattern)."""
    import shutil

    for plain in sorted(directory.glob("*-W*.csv")):
        if plain == keep:
            continue
        packed = plain.with_suffix(".csv.gz")
        tmp = packed.with_name(packed.name + ".tmp")
        try:
            if packed.exists():
                packed.unlink()
            with plain.open("rb") as src, gzip.open(tmp, "wb", compresslevel=6) as dst:
                shutil.copyfileobj(src, dst)
            os.replace(tmp, packed)
            plain.unlink()
        except OSError:
            try:
                tmp.unlink()
            except OSError:
                pass
            return


def recorded_hours(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return {str(r.get("snapshot_hour") or "") for r in reader}


def append_snapshot_rows(directory: Path, rows: list[dict], now: datetime) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = snapshot_path(directory, now)
    new_week = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SNAPSHOT_HEADERS, extrasaction="ignore")
        if new_week:
            writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in SNAPSHOT_HEADERS})
        handle.flush()
    if new_week:
        _compress_stale(directory, keep=path)
    return path


def read_snapshots(directory: Path) -> list[dict]:
    """All snapshot rows, plain and gzipped, oldest week first."""
    out: list[dict] = []
    for file in sorted(directory.glob("*-W*.csv*")):
        opener = gzip.open if file.suffix == ".gz" else open
        with opener(file, "rt", newline="") as handle:
            out.extend(csv.DictReader(handle))
    return out


# --------------------------------------------------------------------------
# Universe
# --------------------------------------------------------------------------


def universe_coins(universe_path: Path, *, max_coins: int | None = None) -> list[str]:
    from breakwater.universe import read_universe

    snapshot = read_universe(universe_path)
    if snapshot is None:
        return []
    coins: list[str] = []
    for row in sorted(snapshot.rows, key=lambda r: r.liquidity_rank):
        if row.kind != "PERP" or not row.active:
            continue
        coin = pair_to_coin(row.symbol)
        if coin and coin not in coins:
            coins.append(coin)
    if max_coins is not None:
        coins = coins[: max(0, int(max_coins))]
    return coins


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------


def resolve_venue_names(coins: list[str], contexts: dict[str, dict]) -> tuple[list[str], list[str]]:
    """Map universe coin names onto the venue's exact names.

    The universe upper-cases symbols (``KBONK``) while the venue names the
    1000x-lot coins ``kBONK``; ``HL_COIN_ALIASES`` only covers kPEPE.  Resolve
    by case here rather than widening the shared alias table mid-freeze.
    Returns ``(resolved, missing)`` preserving order.
    """
    by_upper = {name.upper(): name for name in contexts}
    resolved: list[str] = []
    missing: list[str] = []
    for requested in coins:
        name = requested if requested in contexts else by_upper.get(requested.upper())
        if name is None:
            missing.append(requested)
        elif name not in resolved:
            resolved.append(name)
    return resolved, missing


def run_positioning_snapshot(
    *,
    data_dir: Path,
    universe_path: Path,
    session=None,
    now: datetime | None = None,
    max_coins: int | None = None,
    sleep_seconds: float | None = None,
    info_url: str = HYPERLIQUID_INFO_URL,
) -> dict:
    now = now or datetime.now(timezone.utc)
    directory = positioning_dir(data_dir)
    path = snapshot_path(directory, now)
    hour = hour_key(now)
    summary = {
        "snapshot_hour": hour,
        "path": str(path),
        "coins": 0,
        "rows": 0,
        "book_errors": 0,
        "skipped_existing_hour": False,
        "missing_coins": [],
        "error": "",
    }
    if hour in recorded_hours(path):
        summary["skipped_existing_hour"] = True
        return summary

    coins = universe_coins(universe_path, max_coins=max_coins)
    summary["coins"] = len(coins)
    if not coins:
        summary["error"] = "no active PERP coins in universe"
        return summary

    if sleep_seconds is None:
        try:
            sleep_seconds = float(os.getenv("BREAKWATER_POSITIONING_SLEEP_SECONDS", "0.1"))
        except ValueError:
            sleep_seconds = 0.1

    session = session or requests.Session()
    contexts = fetch_asset_contexts(session, info_url=info_url)
    resolved, missing = resolve_venue_names(coins, contexts)
    stamp = now.astimezone(timezone.utc).isoformat()
    rows: list[dict] = []
    for coin in resolved:
        context = contexts[coin]
        row = {"snapshot_at": stamp, "snapshot_hour": hour, **context_row(coin, context), "book_error": ""}
        try:
            bids, asks = fetch_l2_book(coin, session, info_url=info_url)
            row.update(book_metrics(bids, asks))
        except Exception as exc:  # one bad book must not lose the hour
            row["book_error"] = f"{type(exc).__name__}: {exc}"[:120]
            summary["book_errors"] += 1
        rows.append(row)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    if rows:
        append_snapshot_rows(directory, rows, now)
    summary["rows"] = len(rows)
    summary["missing_coins"] = missing
    return summary


def fetch_funding_history(
    coin: str,
    *,
    start: datetime,
    end: datetime,
    session=None,
    info_url: str = HYPERLIQUID_INFO_URL,
    page_sleep: float = 0.1,
) -> list[dict]:
    """Paginate ``fundingHistory`` (the venue caps a page at ~500 entries)."""
    out: list[dict] = []
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    seen: set[int] = set()
    for _ in range(200):  # hard stop; 200 pages × 500 h ≈ 11 years
        payload = _post_info(
            session,
            {"type": "fundingHistory", "coin": coin, "startTime": start_ms, "endTime": end_ms},
            info_url=info_url,
        )
        if not isinstance(payload, list) or not payload:
            break
        last_time = None
        for entry in payload:
            try:
                t = int(entry["time"])
            except (KeyError, TypeError, ValueError):
                continue
            last_time = t if last_time is None else max(last_time, t)
            if t in seen:
                continue
            seen.add(t)
            out.append({
                "coin": coin,
                "time": datetime.fromtimestamp(t / 1000, tz=timezone.utc).isoformat(),
                "funding_rate": str(entry.get("fundingRate", "")),
                "premium": str(entry.get("premium", "")),
            })
        if last_time is None or last_time >= end_ms or last_time + 1 <= start_ms:
            break
        start_ms = last_time + 1
        if page_sleep > 0:
            time.sleep(page_sleep)
    return out


def run_funding_backfill(
    *,
    data_dir: Path,
    universe_path: Path,
    days: int = 60,
    session=None,
    now: datetime | None = None,
    max_coins: int | None = None,
    info_url: str = HYPERLIQUID_INFO_URL,
) -> dict:
    now = now or datetime.now(timezone.utc)
    directory = positioning_dir(data_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / FUNDING_HISTORY_FILENAME
    existing: dict[tuple[str, str], dict] = {}
    if path.exists():
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                existing[(row.get("coin", ""), row.get("time", ""))] = row
    session = session or requests.Session()
    coins, missing = resolve_venue_names(
        universe_coins(universe_path, max_coins=max_coins),
        fetch_asset_contexts(session, info_url=info_url),
    )
    start = now - timedelta(days=max(1, int(days)))
    added = 0
    errors: list[str] = []
    for coin in coins:
        # Resume from the newest stored point for this coin.
        newest = max((r["time"] for (c, _), r in existing.items() if c == coin), default="")
        coin_start = start
        if newest:
            try:
                coin_start = max(start, datetime.fromisoformat(newest) + timedelta(milliseconds=1))
            except ValueError:
                pass
        try:
            for row in fetch_funding_history(coin, start=coin_start, end=now, session=session, info_url=info_url):
                key = (row["coin"], row["time"])
                if key not in existing:
                    existing[key] = row
                    added += 1
        except Exception as exc:
            errors.append(f"{coin}: {type(exc).__name__}: {exc}"[:160])
    rows = sorted(existing.values(), key=lambda r: (r.get("coin", ""), r.get("time", "")))
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FUNDING_HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)
    return {
        "path": str(path),
        "coins": len(coins),
        "missing_coins": missing,
        "added": added,
        "rows": len(rows),
        "errors": errors,
    }
