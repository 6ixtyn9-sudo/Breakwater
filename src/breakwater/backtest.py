"""Multi-year offline backtest harness.

Why this exists. Everything Breakwater ever promoted was discovered and
validated on ``BREAKWATER_PERP_CANDLE_COUNT = 1000`` hourly bars - 42 days.
September 2026 (+468) was the regime persisting; October (-163) was the
system re-learning September while the market moved on. Before anything
else re-enters the paper loop it has to pass here, on years, out of sample.

Two hypotheses, both parameter grids with NO fitting: every variant is
reported, the verdict is read from the MEDIAN variant, and the holdout
window is fixed in advance (``HOLDOUT_START``). Costs are the repo's own:
9 bps taker fee per side, 15 bps adverse slip on stop fills, 5 bps on
entries.

H1 trend + trail (daily bars). Direction from close vs SMA(N); enter at
the next open; ATR(14) x k trailing stop checked against the bar extreme;
exit on stop or on the trend flipping (next open). Long and short.

H2 funding carry (daily bars + hourly Hyperliquid funding). When the
trailing 24h funding, annualised, exceeds a threshold, take the side that
RECEIVES funding for the next day and hold while the condition persists.
Reported two ways: directional (price P&L + funding) and hedged (funding
only, less two legs of fees per episode; the spot/second leg is assumed
to cost the same 9 bps - VALR spot at 70 bps would not qualify).

Data: Hyperliquid ``candleSnapshot`` serves at most the latest 5000
candles per interval (1d = full history since 2023 listing; 1h = ~7
months), so daily bars come from Hyperliquid, deeper daily history for
BTC/ETH from Binance when reachable, and hourly funding from Hyperliquid
``fundingHistory``. Raw data lives under ``localdata/backtest/data`` and
is NOT committed (gitignored; the workflow caches it); only the small
result tables and ``summary.md`` are.
"""

from __future__ import annotations

import csv
import math
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from breakwater.positioning import HYPERLIQUID_INFO_URL, _post_info, fetch_funding_history

# ----------------------------------------------------------------------------
# pre-registered parameters - change these only with a HANDOVER entry
# ----------------------------------------------------------------------------

UNIVERSE = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "AVAX", "LINK", "LTC", "ADA"]
HOLDOUT_START = datetime(2025, 7, 1, tzinfo=timezone.utc)
FEE_BPS = 9.0
ENTRY_SLIP_BPS = 5.0
STOP_SLIP_BPS = 15.0
H1_SMA = (50, 100, 200)
H1_ATR_K = (2.0, 3.0, 4.0)
H1_ATR_N = 14
H2_THRESHOLDS_ANNUAL = (0.10, 0.20, 0.30)  # trailing-24h funding, annualised
MIN_COIN_YEAR_SHARE = 0.60  # pass needs >= 60% of coin-years positive (median variant)

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


# ----------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------


def data_dir(root: Path) -> Path:
    path = root / "backtest" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def fetch_hl_candles(
    coin: str,
    *,
    interval: str,
    start: datetime,
    end: datetime,
    session=None,
    info_url: str = HYPERLIQUID_INFO_URL,
    page_sleep: float = 0.2,
) -> pd.DataFrame:
    """Paginate ``candleSnapshot`` forward from ``start``; the venue returns at
    most 5000 rows per call and never more than its retained window."""
    rows: list[dict] = []
    seen: set[int] = set()
    cursor = _ms(start)
    end_ms = _ms(end)
    for _ in range(50):
        payload = _post_info(
            session,
            {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": cursor, "endTime": end_ms}},
            info_url=info_url,
        )
        if not isinstance(payload, list) or not payload:
            break
        last = None
        for row in payload:
            try:
                t = int(row["t"])
            except (KeyError, TypeError, ValueError):
                continue
            last = t if last is None else max(last, t)
            if t in seen:
                continue
            seen.add(t)
            rows.append({
                "time": datetime.fromtimestamp(t / 1000, tz=timezone.utc),
                "open": float(row["o"]), "high": float(row["h"]), "low": float(row["l"]),
                "close": float(row["c"]), "volume": float(row.get("v") or 0.0),
            })
        if last is None or last >= end_ms or len(payload) < 2:
            break
        if last + 1 <= cursor:
            break
        cursor = last + 1
        if page_sleep > 0:
            time.sleep(page_sleep)
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    return frame


def fetch_binance_daily(symbol: str, *, start: datetime, end: datetime, session=None, page_sleep: float = 0.2) -> pd.DataFrame:
    """Daily klines, 1000 per page. Returns an empty frame on any failure so
    an unreachable Binance (post-hack) degrades to Hyperliquid-only history."""
    requester = session or requests
    rows: list[dict] = []
    cursor = _ms(start)
    end_ms = _ms(end)
    try:
        for _ in range(20):
            response = requester.get(
                BINANCE_KLINES_URL,
                params={"symbol": symbol, "interval": "1d", "startTime": cursor, "endTime": end_ms, "limit": 1000},
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list) or not payload:
                break
            for k in payload:
                rows.append({
                    "time": datetime.fromtimestamp(int(k[0]) / 1000, tz=timezone.utc),
                    "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4]),
                    "volume": float(k[5]),
                })
            last = int(payload[-1][0])
            if len(payload) < 1000 or last >= end_ms:
                break
            cursor = last + 1
            if page_sleep > 0:
                time.sleep(page_sleep)
    except Exception:  # noqa: BLE001 - optional source
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    return frame


def load_or_fetch(path: Path, fetch, *, max_age_hours: float = 20.0) -> pd.DataFrame:
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_hours * 3600:
        frame = pd.read_csv(path)
        if not frame.empty:
            frame["time"] = pd.to_datetime(frame["time"], utc=True)
        return frame
    frame = fetch()
    if frame is not None and not frame.empty:
        frame.to_csv(path, index=False)
    return frame if frame is not None else pd.DataFrame()


def fetch_all(root: Path, *, coins: list[str] = UNIVERSE, session=None, log=print) -> dict:
    """Populate the data directory. Returns a manifest of what was fetched."""
    now = datetime.now(timezone.utc)
    origin = datetime(2017, 1, 1, tzinfo=timezone.utc)
    hl_origin = datetime(2023, 1, 1, tzinfo=timezone.utc)
    out = data_dir(root)
    manifest: dict[str, dict] = {}
    for coin in coins:
        entry: dict = {}
        daily = load_or_fetch(out / f"hl_{coin}_1d.csv", lambda: fetch_hl_candles(coin, interval="1d", start=hl_origin, end=now, session=session))
        entry["hl_1d_rows"] = int(len(daily))
        if coin in {"BTC", "ETH"}:
            bn = load_or_fetch(out / f"binance_{coin}USDT_1d.csv", lambda: fetch_binance_daily(f"{coin}USDT", start=origin, end=now, session=session))
            entry["binance_1d_rows"] = int(len(bn))
        funding = load_or_fetch(
            out / f"hl_{coin}_funding.csv",
            lambda: pd.DataFrame(fetch_funding_history(coin, start=hl_origin, end=now, session=session)),
        )
        entry["funding_rows"] = int(len(funding))
        manifest[coin] = entry
        log(f"{coin}: {entry}")
    return manifest


def load_daily(root: Path, coin: str) -> pd.DataFrame:
    """Daily bars: Binance history (if present) spliced before Hyperliquid's."""
    out = data_dir(root)
    frames = []
    bn = out / f"binance_{coin}USDT_1d.csv"
    hl = out / f"hl_{coin}_1d.csv"
    hl_frame = pd.read_csv(hl) if hl.exists() else pd.DataFrame()
    if not hl_frame.empty:
        hl_frame["time"] = pd.to_datetime(hl_frame["time"], utc=True)
        hl_frame["source"] = "hyperliquid"
    if bn.exists():
        bn_frame = pd.read_csv(bn)
        if not bn_frame.empty:
            bn_frame["time"] = pd.to_datetime(bn_frame["time"], utc=True)
            bn_frame["source"] = "binance"
            if not hl_frame.empty:
                bn_frame = bn_frame[bn_frame["time"] < hl_frame["time"].min()]
            frames.append(bn_frame)
    if not hl_frame.empty:
        frames.append(hl_frame)
    if not frames:
        return pd.DataFrame()
    frame = pd.concat(frames, ignore_index=True).sort_values("time").drop_duplicates("time").reset_index(drop=True)
    return frame


def load_funding_daily(root: Path, coin: str) -> pd.DataFrame:
    """Hourly Hyperliquid funding summed per UTC day -> columns time, funding_day."""
    path = data_dir(root) / f"hl_{coin}_funding.csv"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if frame.empty:
        return frame
    frame["time"] = pd.to_datetime(frame["time"], utc=True)
    frame["funding_rate"] = pd.to_numeric(frame["funding_rate"], errors="coerce").fillna(0.0)
    daily = frame.groupby(frame["time"].dt.floor("D"))["funding_rate"].sum().rename("funding_day").reset_index()
    return daily


# ----------------------------------------------------------------------------
# H1: trend + trail
# ----------------------------------------------------------------------------


@dataclass
class Trade:
    coin: str
    side: str
    entry_time: datetime
    exit_time: datetime
    entry: float
    exit: float
    reason: str
    ret: float  # net fractional return on notional


def _atr(frame: pd.DataFrame, n: int) -> pd.Series:
    prev_close = frame["close"].shift(1)
    tr = pd.concat([
        frame["high"] - frame["low"],
        (frame["high"] - prev_close).abs(),
        (frame["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def simulate_trend_trail(frame: pd.DataFrame, *, coin: str, sma_n: int, atr_k: float, atr_n: int = H1_ATR_N) -> list[Trade]:
    """Daily-bar simulation. Signals at close t, fills at open t+1, trail
    checked against the bar extreme with STOP_SLIP_BPS, bounded by it."""
    if len(frame) < sma_n + atr_n + 2:
        return []
    f = frame.reset_index(drop=True).copy()
    f["sma"] = f["close"].rolling(sma_n).mean()
    f["atr"] = _atr(f, atr_n)
    fee = FEE_BPS / 1e4
    eslip = ENTRY_SLIP_BPS / 1e4
    sslip = STOP_SLIP_BPS / 1e4
    trades: list[Trade] = []
    pos = None  # dict(side, entry, entry_time, stop, extreme)
    pending = None  # side to open at next bar's open
    for i in range(1, len(f)):
        row = f.iloc[i]
        prev = f.iloc[i - 1]
        # 1. pending entry fills at this bar's open
        if pending is not None and pos is None and not math.isnan(prev["atr"]):
            side = pending
            price = row["open"] * (1 + eslip if side == "LONG" else 1 - eslip)
            stop = price - atr_k * prev["atr"] if side == "LONG" else price + atr_k * prev["atr"]
            pos = {"side": side, "entry": price, "entry_time": row["time"], "stop": stop, "extreme": price}
            pending = None
        if pos is not None:
            # 2. stop check against this bar's extreme
            hit = False
            if pos["side"] == "LONG" and row["low"] <= pos["stop"]:
                fill = max(row["low"], pos["stop"] * (1 - sslip))
                hit = True
            elif pos["side"] == "SHORT" and row["high"] >= pos["stop"]:
                fill = min(row["high"], pos["stop"] * (1 + sslip))
                hit = True
            if hit:
                ret = (fill / pos["entry"] - 1) * (1 if pos["side"] == "LONG" else -1) - 2 * fee
                trades.append(Trade(coin, pos["side"], pos["entry_time"], row["time"], pos["entry"], fill, "trail", ret))
                pos = None
            else:
                # 3. ratchet the trail on the close
                if pos["side"] == "LONG":
                    pos["extreme"] = max(pos["extreme"], row["high"])
                    pos["stop"] = max(pos["stop"], pos["extreme"] - atr_k * row["atr"])
                else:
                    pos["extreme"] = min(pos["extreme"], row["low"])
                    pos["stop"] = min(pos["stop"], pos["extreme"] + atr_k * row["atr"])
        # 4. trend state at this close decides tomorrow
        if math.isnan(row["sma"]) or math.isnan(row["atr"]):
            continue
        trend = "LONG" if row["close"] > row["sma"] else "SHORT"
        if pos is not None and pos["side"] != trend:
            # flip: exit at next open (modelled as next bar's open with entry slip)
            if i + 1 < len(f):
                nxt = f.iloc[i + 1]
                price = nxt["open"] * (1 - eslip if pos["side"] == "LONG" else 1 + eslip)
                ret = (price / pos["entry"] - 1) * (1 if pos["side"] == "LONG" else -1) - 2 * fee
                trades.append(Trade(coin, pos["side"], pos["entry_time"], nxt["time"], pos["entry"], price, "flip", ret))
                pos = None
                pending = trend
        elif pos is None and pending is None:
            pending = trend
    if pos is not None:
        # mark the open position at the last close: dropping it would bias
        # the result against exactly the long trends this hypothesis is about
        last = f.iloc[-1]
        ret = (last["close"] / pos["entry"] - 1) * (1 if pos["side"] == "LONG" else -1) - 2 * fee
        trades.append(Trade(coin, pos["side"], pos["entry_time"], last["time"], pos["entry"], float(last["close"]), "end", ret))
    return trades


# ----------------------------------------------------------------------------
# H2: funding carry
# ----------------------------------------------------------------------------


@dataclass
class CarryEpisode:
    coin: str
    side: str
    start: datetime
    end: datetime
    days: int
    funding: float  # fractional, received (+) by the position
    price: float  # directional price return, fractional
    hedged: float  # funding - 2 legs x 2 sides fees
    directional: float  # price + funding - 2 sides fees


def simulate_funding_carry(daily: pd.DataFrame, funding: pd.DataFrame, *, coin: str, threshold_annual: float) -> list[CarryEpisode]:
    """At close t: trailing-24h funding (day t's sum) annualised beyond the
    threshold -> take the receiving side for day t+1 (open to open), stay
    while the condition holds, collect day t+1's funding."""
    if daily.empty or funding.empty:
        return []
    f = daily.copy()
    f["day"] = f["time"].dt.floor("D")
    f = f.merge(funding.rename(columns={"time": "day"}), on="day", how="left")
    f["funding_day"] = f["funding_day"].fillna(0.0)
    f = f.reset_index(drop=True)
    fee = FEE_BPS / 1e4
    episodes: list[CarryEpisode] = []
    state = None  # side, start, funding, price_entry, days
    for i in range(len(f) - 1):
        ann = f.loc[i, "funding_day"] * 365.0
        want = "SHORT" if ann > threshold_annual else ("LONG" if ann < -threshold_annual else None)
        nxt = f.iloc[i + 1]
        if state is not None and (want != state["side"]):
            # close at next open
            price_ret = (nxt["open"] / state["entry"] - 1) * (1 if state["side"] == "LONG" else -1)
            episodes.append(CarryEpisode(
                coin, state["side"], state["start"], nxt["time"], state["days"], state["funding"], price_ret,
                state["funding"] - 4 * fee, price_ret + state["funding"] - 2 * fee,
            ))
            state = None
        if want is not None and state is None:
            state = {"side": want, "start": nxt["time"], "entry": nxt["open"], "funding": 0.0, "days": 0}
        if state is not None:
            # funding over day t+1 accrues to the position; shorts receive positive funding
            sign = -1 if state["side"] == "LONG" else 1
            state["funding"] += sign * nxt["funding_day"]
            state["days"] += 1
    if state is not None:
        last = f.iloc[-1]
        price_ret = (last["close"] / state["entry"] - 1) * (1 if state["side"] == "LONG" else -1)
        episodes.append(CarryEpisode(
            coin, state["side"], state["start"], last["time"], state["days"], state["funding"], price_ret,
            state["funding"] - 4 * fee, price_ret + state["funding"] - 2 * fee,
        ))
    return episodes


# ----------------------------------------------------------------------------
# scoring
# ----------------------------------------------------------------------------


def _year(ts) -> int:
    return int(pd.Timestamp(ts).year)


def score_h1(trades_by_variant: dict[tuple[int, float], list[Trade]]) -> tuple[pd.DataFrame, dict]:
    rows = []
    for (sma_n, atr_k), trades in trades_by_variant.items():
        for t in trades:
            rows.append({
                "sma": sma_n, "atr_k": atr_k, "coin": t.coin, "side": t.side, "year": _year(t.exit_time),
                "holdout": t.exit_time >= HOLDOUT_START, "ret": t.ret, "reason": t.reason,
            })
    if not rows:
        return pd.DataFrame(), {"verdict": "NO DATA"}
    df = pd.DataFrame(rows)
    table = (
        df.groupby(["sma", "atr_k", "coin", "year", "holdout"])["ret"]
        .agg(trades="size", net="sum", win_rate=lambda s: float((s > 0).mean()))
        .reset_index()
    )
    verdict = _verdict(table, key_cols=["sma", "atr_k"])
    return table, verdict


def score_h2(episodes_by_thr: dict[float, list[CarryEpisode]]) -> tuple[pd.DataFrame, dict]:
    rows = []
    for thr, eps in episodes_by_thr.items():
        for e in eps:
            rows.append({
                "threshold": thr, "coin": e.coin, "side": e.side, "year": _year(e.end), "holdout": e.end >= HOLDOUT_START,
                "days": e.days, "funding": e.funding, "price": e.price, "hedged": e.hedged, "directional": e.directional,
            })
    if not rows:
        return pd.DataFrame(), {"verdict": "NO DATA"}
    df = pd.DataFrame(rows)
    table = (
        df.groupby(["threshold", "coin", "year", "holdout"])
        .agg(episodes=("days", "size"), days=("days", "sum"), funding=("funding", "sum"), price=("price", "sum"),
             hedged=("hedged", "sum"), directional=("directional", "sum"))
        .reset_index()
    )
    hedged = _verdict(table.rename(columns={"hedged": "net"}), key_cols=["threshold"])
    directional = _verdict(table.rename(columns={"directional": "net"}), key_cols=["threshold"])
    return table, {"hedged": hedged, "directional": directional, "verdict": hedged["verdict"]}


def _verdict(table: pd.DataFrame, *, key_cols: list[str]) -> dict:
    """Median variant's holdout net must be > 0 AND >= MIN_COIN_YEAR_SHARE of
    its coin-years (all data) positive. Best-of-grid is reported but never
    used for the verdict."""
    per_variant = []
    for key, grp in table.groupby(key_cols):
        hold = grp[grp["holdout"]]
        per_variant.append({
            "variant": key if isinstance(key, tuple) else (key,),
            "holdout_net": float(hold["net"].sum()),
            "all_net": float(grp["net"].sum()),
            "coin_year_share": float((grp.groupby(["coin", "year"])["net"].sum() > 0).mean()) if len(grp) else 0.0,
        })
    if not per_variant:
        return {"verdict": "NO DATA"}
    per_variant.sort(key=lambda d: d["holdout_net"])
    median = per_variant[len(per_variant) // 2]
    best = per_variant[-1]
    passed = median["holdout_net"] > 0 and median["coin_year_share"] >= MIN_COIN_YEAR_SHARE
    return {
        "verdict": "PASS" if passed else "FAIL",
        "median_variant": median,
        "best_variant": best,
        "median_of_holdout_net": statistics.median(d["holdout_net"] for d in per_variant),
        "variants_positive_holdout": sum(1 for d in per_variant if d["holdout_net"] > 0),
        "variants": len(per_variant),
    }


# ----------------------------------------------------------------------------
# runner
# ----------------------------------------------------------------------------


def run(root: Path, *, coins: list[str] = UNIVERSE, log=print) -> dict:
    out = root / "backtest"
    out.mkdir(parents=True, exist_ok=True)
    h1: dict[tuple[int, float], list[Trade]] = {}
    h2: dict[float, list[CarryEpisode]] = {}
    coverage = []
    for coin in coins:
        daily = load_daily(root, coin)
        fund = load_funding_daily(root, coin)
        coverage.append({
            "coin": coin, "daily_rows": int(len(daily)),
            "daily_from": str(daily["time"].min().date()) if len(daily) else "",
            "funding_days": int(len(fund)), "funding_from": str(fund["time"].min().date()) if len(fund) else "",
        })
        if daily.empty:
            continue
        for sma_n in H1_SMA:
            for k in H1_ATR_K:
                h1.setdefault((sma_n, k), []).extend(simulate_trend_trail(daily, coin=coin, sma_n=sma_n, atr_k=k))
        for thr in H2_THRESHOLDS_ANNUAL:
            h2.setdefault(thr, []).extend(simulate_funding_carry(daily, fund, coin=coin, threshold_annual=thr))
        log(f"{coin}: daily {len(daily)} funding-days {len(fund)}")
    t1, v1 = score_h1(h1)
    t2, v2 = score_h2(h2)
    if not t1.empty:
        t1.to_csv(out / "h1_trend_trail.csv", index=False)
    if not t2.empty:
        t2.to_csv(out / "h2_funding_carry.csv", index=False)
    with (out / "coverage.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage[0].keys()))
        writer.writeheader()
        writer.writerows(coverage)
    summary = render_summary(coverage, v1, v2)
    (out / "summary.md").write_text(summary)
    return {"h1": v1, "h2": v2, "coverage": coverage}


def _fmt_variant(d: dict | None) -> str:
    if not d:
        return "n/a"
    return (f"{d['variant']}: holdout {d['holdout_net'] * 100:+.1f}% | all {d['all_net'] * 100:+.1f}% | "
            f"coin-years positive {d['coin_year_share'] * 100:.0f}%")


def render_summary(coverage: list[dict], v1: dict, v2: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    lines = [
        f"# Backtest summary - {now}",
        "",
        f"Holdout from {HOLDOUT_START.date()}. Costs: fee {FEE_BPS:.0f} bps/side, entry slip {ENTRY_SLIP_BPS:.0f} bps, "
        f"stop slip {STOP_SLIP_BPS:.0f} bps. Verdict = MEDIAN variant: holdout net > 0 and >= {MIN_COIN_YEAR_SHARE:.0%} "
        "coin-years positive. Best-of-grid shown for scale only; it is not the verdict.",
        "",
        "## Coverage",
        "",
        "| coin | daily rows | from | funding days | from |",
        "|---|---|---|---|---|",
    ]
    for c in coverage:
        lines.append(f"| {c['coin']} | {c['daily_rows']} | {c['daily_from']} | {c['funding_days']} | {c['funding_from']} |")
    lines += [
        "",
        f"## H1 trend + trail - **{v1.get('verdict')}**",
        "",
        f"- median variant (sma, atr_k) - {_fmt_variant(v1.get('median_variant'))}",
        f"- best variant - {_fmt_variant(v1.get('best_variant'))}",
        f"- variants with positive holdout: {v1.get('variants_positive_holdout', 0)} / {v1.get('variants', 0)}",
        "",
        f"## H2 funding carry - hedged **{v2.get('verdict')}**",
        "",
    ]
    for label in ("hedged", "directional"):
        v = v2.get(label) or {}
        lines += [
            f"### {label} - {v.get('verdict')}",
            f"- median threshold - {_fmt_variant(v.get('median_variant'))}",
            f"- best threshold - {_fmt_variant(v.get('best_variant'))}",
            f"- thresholds with positive holdout: {v.get('variants_positive_holdout', 0)} / {v.get('variants', 0)}",
            "",
        ]
    lines += [
        "Returns are fractional on a fixed 1x notional per coin, summed across trades/episodes; "
        "no compounding, no sizing. Hedged carry assumes a second leg at the same 9 bps; "
        "VALR spot (70 bps) does not qualify.",
    ]
    return "\n".join(lines) + "\n"
