#!/usr/bin/env python3
"""Breakwater daily print.

Reads the committed observation state (localdata/*) and writes a one-page
"where is the money / where are we losing it" report. It performs no writes to
venues and promotes nothing. It is idempotent per UTC date, so it can be
invoked from every state-committing workflow without creating per-run churn.

Output:
  localdata/daily/YYYY-MM-DD.md   (committed, durable)
  localdata/daily/latest.md       (same content, easy to inspect)
  stdout                          (the same markdown)
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "localdata"
# Ensure the breakwater package under src/ is imported, not scripts/breakwater.py.
sys.path.insert(0, str(ROOT / "src"))

# Section 2b must count closes using the gate's real-close definition, never a
# local copy that can drift from it. Both lane_gate._is_real_close and
# lane_gate.ACTUAL_EXITS are reused below via the module, not re-derived.
from breakwater import lane_gate  # noqa: E402

# Section 2b sample gate and verdict thresholds are hard-coded on purpose: no
# new configuration surface (env var, flag or YAML) for an advisory readout.
MIN_VERDICT_CLOSES = 30
VERDICT_T_THRESHOLD = 2.0

ACTUAL_EXITS = {
    "target",
    "stop",
    "trail_stop",
    "horizon",
    "rotated",
    "stale_data",
    "time_stop",
    "regime_shift",
    "lane_gate",
}
SKIP_REASONS = {
    "regime",
    "not_book",
    "no_price",
    "adverse",
    "risk_cap",
    "edge_cap",
    "below_perp_min_notional",
    "aggregate_risk_cap",
    "aggregate_risk_unknown",
    "session",
    "session_blocked",
}


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _load_detail(text):
    """Parse a status.csv ``detail`` blob without ever raising.

    status.py caps every detail at 4000 characters, so a long shadow-scan
    payload (the green-gate blocked-slice map is thousands of characters on its
    own) is stored truncated and is not valid JSON. A bare ``json.loads`` here
    is what killed the daily digest: the runner kept reporting "operational"
    while the one artifact that would have shown a frozen, liquidating book
    crashed on every run. Parse what survives, never raise.
    """
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, ValueError):
        pass
    # Salvage: re-close whatever containers were left open by the truncation.
    for tail in ("", '"', "]", "}", '"]', '"}', "]}", '"]}', '"}]', '"}]}'):
        try:
            parsed = json.loads(text + tail)
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError):
            continue
    # Last resort: cut back to the last complete top-level pair and close it.
    cut = text.rfind(",")
    while cut > 0:
        for tail in ("}", "]}", '"]}'):
            try:
                parsed = json.loads(text[:cut] + tail)
                if isinstance(parsed, dict):
                    return parsed
            except (TypeError, ValueError):
                pass
        cut = text.rfind(",", 0, cut)
    return {}


def _lane(slice_id: str) -> str:
    return "hip3" if str(slice_id).startswith("hip3_") else "native"


def _day(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).date().isoformat()


def _iso(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _paper_performance(trade_rows):
    per_lane = defaultdict(
        lambda: {
            "closed": 0,
            "wins": 0,
            "pnl": 0.0,
            "by_exit": defaultdict(float),
            "by_regime": defaultdict(lambda: [0, 0.0]),
            "by_slice": defaultdict(lambda: [0, 0.0, 0]),
            "by_pair": defaultdict(lambda: [0, 0.0, 0]),
        }
    )
    today = _now()
    last7 = today - timedelta(days=7)
    last30 = today - timedelta(days=30)
    recent = {
        "today": defaultdict(lambda: [0, 0.0, 0]),
        "7d": defaultdict(lambda: [0, 0.0, 0]),
        "30d": defaultdict(lambda: [0, 0.0, 0]),
    }
    for r in trade_rows:
        if str(r.get("outcome") or "") not in {"win", "loss"}:
            continue
        if str(r.get("exit_reason") or "") not in ACTUAL_EXITS:
            continue
        lane = _lane(r.get("slice_id", ""))
        pnl = _num(r.get("pnl_zar"))
        outcome = str(r.get("pnl_outcome") or (str(r.get("outcome")) == "win" and "win" or "loss"))
        win = 1 if outcome == "win" else 0
        p = per_lane[lane]
        p["closed"] += 1
        p["wins"] += win
        p["pnl"] += pnl
        p["by_exit"][str(r.get("exit_reason") or "unknown")] += pnl
        # entry regime from the row's stored regime; that is the entry bar's regime
        reg = str(r.get("regime") or "unknown")
        p["by_regime"][reg][0] += 1
        p["by_regime"][reg][1] += pnl
        sid = str(r.get("slice_id") or "?")
        p["by_slice"][sid][0] += 1
        p["by_slice"][sid][1] += pnl
        p["by_slice"][sid][2] += win
        pair = str(r.get("pair") or "?")
        p["by_pair"][pair][0] += 1
        p["by_pair"][pair][1] += pnl
        p["by_pair"][pair][2] += win

        closed_at = _iso(r.get("closed_at", "")) or _iso(r.get("exit_bar_start", ""))
        if closed_at is None:
            continue
        # today uses date, else relative windows
        for window, start in (
            ("today", today.replace(hour=0, minute=0, second=0, microsecond=0)),
            ("7d", last7),
            ("30d", last30),
        ):
            if closed_at >= start:
                recent[window][lane][0] += 1
                recent[window][lane][1] += pnl
                recent[window][lane][2] += win
    return per_lane, recent


def _open_risk_summary(positions):
    per_lane = defaultdict(list)
    for p in positions:
        lane = _lane(p.get("slice_id", ""))
        entry = _num(p.get("entry_price"))
        stop = _num(p.get("stop_price"))
        notional = _num(p.get("notional_zar"))
        side = str(p.get("side", "")).upper()
        if entry <= 0 or notional < 0:
            continue
        if side == "BUY":
            risk_frac = max((entry - stop) / entry, 0.0)
        else:
            risk_frac = max((stop - entry) / entry, 0.0)
        risk_zar = notional * risk_frac
        per_lane[lane].append({**p, "risk_zar": risk_zar})
    return per_lane


def _book_rows(path: Path):
    rows = _read_csv(path)
    return [r for r in rows if str(r.get("status") or "").lower() == "monitored"]


def _gate_top(book_rows):
    out = []
    for r in book_rows:
        out.append(
            {
                "slice_id": r.get("slice_id"),
                "mean_ret_costadj": _num(r.get("mean_ret_costadj")),
                "n": _int(r.get("n")),
                "p_value": _num(r.get("p_value")),
                "source": r.get("source"),
                "hostile_unproven": r.get("hostile_unproven"),
                "paper_trades": _int(r.get("paper_trades")),
                "paper_pnl_zar": _num(r.get("paper_pnl_zar")),
            }
        )
    out.sort(key=lambda x: x["paper_pnl_zar"], reverse=True)
    return out


def _validated_edge_pool(validated_rows):
    """Map slice_id -> mean_ret_costadj for rows that passed validation.

    validated_slices.csv also holds failed candidates (validated=False); the
    monitored books are promoted from passing rows, so the pool is the
    validated=True subset only.
    """
    pool = {}
    for r in validated_rows:
        if str(r.get("validated") or "").strip() == "True":
            pool[str(r.get("slice_id") or "")] = _num(r.get("mean_ret_costadj"))
    return pool


def _book_edges(book_rows, pool):
    """Validated edges for monitored-book slices plus ids absent from the pool.

    A book slice missing from validated_slices.csv is reported, never silently
    dropped: a median over "whatever matched" would overstate coverage.
    """
    edges = []
    missing = []
    for r in book_rows:
        sid = str(r.get("slice_id") or "")
        if sid in pool:
            edges.append(pool[sid])
        else:
            missing.append(sid)
    return edges, missing


def _real_close_rows(trade_rows, lane=None):
    """Real closes under the gate's definition; never re-derived here.

    Skipped/guard rows (~800 appended per cycle) are decision-ledger entries,
    not closes. lane_gate owns the predicate and the ACTUAL_EXITS set.
    """
    out = []
    for r in trade_rows:
        if not lane_gate._is_real_close(r):
            continue
        if lane is not None and _lane(r.get("slice_id", "")) != lane:
            continue
        out.append(r)
    return out


def _close_stats(close_rows):
    """n, mean/sample-sd/SE of pnl_zar (net of fees) and mean notional."""
    pnl = [_num(r.get("pnl_zar")) for r in close_rows]
    notional = [_num(r.get("notional_zar")) for r in close_rows]
    n = len(pnl)
    mean = sum(pnl) / n if n else 0.0
    sd = 0.0
    if n > 1:
        sd = (sum((v - mean) ** 2 for v in pnl) / (n - 1)) ** 0.5
    se = sd / n ** 0.5 if n else 0.0
    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "se": se,
        "mean_notional": sum(notional) / n if n else 0.0,
    }


def _gap_t(mean, se, claimed_zar):
    """One-sample t of a realised mean against a fixed claimed per-trade edge."""
    if se <= 0.0:
        if mean > claimed_zar:
            return float("inf")
        if mean < claimed_zar:
            return float("-inf")
        return 0.0
    return (mean - claimed_zar) / se


def _verdict(t, realised, claimed_zar):
    """Coarse word list; a comparison, never a claim of proof or causality.

    Mapping (VERDICT_T_THRESHOLD = 2):
      |t| < 2                          -> NOT ESTABLISHED
      t >= 2 and realised > claimed    -> EXCEEDS
      t <= -2                          -> FALLS SHORT
    Words such as "works"/"broken" are forbidden: the statistic only compares
    a realised mean against the claimed constant.
    """
    if t >= VERDICT_T_THRESHOLD and realised > claimed_zar:
        return "EXCEEDS"
    if t <= -VERDICT_T_THRESHOLD:
        return "FALLS SHORT"
    return "NOT ESTABLISHED"


def _claimed_vs_realised_section(
    trade_rows, native_book, hip3_book, native_validated, hip3_validated
):
    """Section 2b: claimed research edge versus realised paper edge.

    READ-ONLY AND ADVISORY. This section feeds no gate, admission decision or
    promotion path and writes no state; it exists so the gap between the
    median claimed edge over the monitored books and the forward paper book
    cannot again be computed by hand during an audit.

    Claimed: median mean_ret_costadj over monitored-book slices joined to the
    validated pools (not over the whole validated file). Realised: mean
    pnl_zar over lane_gate real closes; pnl_zar is net of fees (paper_trade.py
    writes ``pnl_zar = gross - fees``). Below MIN_VERDICT_CLOSES closes the
    section prints a mean and INSUFFICIENT SAMPLE, never a t-statistic.
    """
    lines = ["## 2b. Claimed vs realised", ""]
    books = {"native": native_book, "hip3": hip3_book}
    pools = {
        "native": _validated_edge_pool(native_validated),
        "hip3": _validated_edge_pool(hip3_validated),
    }
    info = {}
    pooled_edges = []
    missing_all = []
    for lane in ("native", "hip3"):
        edges, missing = _book_edges(books[lane], pools[lane])
        info[lane] = {
            "book_n": len(books[lane]),
            "pool_n": len(pools[lane]),
            "edges": edges,
            "missing": missing,
        }
        pooled_edges.extend(edges)
        missing_all.extend((lane, sid) for sid in missing)
    native_n = info["native"]["book_n"]
    hip3_n = info["hip3"]["book_n"]
    lines.append(
        f"- Book: {native_n + hip3_n} slices (native {native_n} | hip3 {hip3_n}); "
        f"validated pools: native {info['native']['pool_n']} | "
        f"hip3 {info['hip3']['pool_n']}; book slices absent from pools: {len(missing_all)}"
    )
    for lane, sid in missing_all[:10]:
        lines.append(f"  - absent: `{sid}` ({lane})")
    if len(missing_all) > 10:
        lines.append(f"  - ... and {len(missing_all) - 10} more")

    pooled_stats = _close_stats(_real_close_rows(trade_rows))
    lane_stats = {
        lane: _close_stats(_real_close_rows(trade_rows, lane))
        for lane in ("native", "hip3")
    }

    if pooled_edges:
        claimed_edge = statistics.median(pooled_edges)
        claimed_zar = claimed_edge * pooled_stats["mean_notional"]
        lines.append(
            f"- Claimed edge (median mean_ret_costadj over {len(pooled_edges)} book "
            f"slices present in the validated pools): {100 * claimed_edge:+.3f}% | at "
            f"{pooled_stats['mean_notional']:.2f} ZAR mean notional/trade: "
            f"{claimed_zar:+.2f} ZAR/trade"
        )
    else:
        claimed_edge = None
        claimed_zar = None
        lines.append(
            f"- Claimed edge: unknown (0/{native_n + hip3_n} book slices present in "
            f"the validated pools)"
        )

    n = pooled_stats["n"]
    if n == 0:
        lines.append(
            "- Realised (0 real closes per lane_gate._is_real_close, net of fees): "
            f"no real closes | INSUFFICIENT SAMPLE (n<{MIN_VERDICT_CLOSES})"
        )
    elif n < MIN_VERDICT_CLOSES:
        lines.append(
            f"- Realised ({n} real closes per lane_gate._is_real_close, net of fees): "
            f"{pooled_stats['mean']:+.2f} ZAR/trade | INSUFFICIENT SAMPLE "
            f"(n<{MIN_VERDICT_CLOSES})"
        )
    else:
        lines.append(
            f"- Realised ({n} real closes per lane_gate._is_real_close, net of fees): "
            f"{pooled_stats['mean']:+.2f} ZAR/trade | sd {pooled_stats['sd']:.2f} | "
            f"SE {pooled_stats['se']:.2f}"
        )
    if claimed_zar is not None and n >= MIN_VERDICT_CLOSES:
        gap = pooled_stats["mean"] - claimed_zar
        t = _gap_t(pooled_stats["mean"], pooled_stats["se"], claimed_zar)
        lines.append(
            f"- Gap: {gap:+.2f} ZAR/trade | t = {t:+.2f} (one-sample t of realised "
            f"mean vs the claimed constant) | verdict: "
            f"{_verdict(t, pooled_stats['mean'], claimed_zar)}"
        )
    else:
        why = (
            "claimed edge unknown"
            if claimed_zar is None
            else f"INSUFFICIENT SAMPLE (n<{MIN_VERDICT_CLOSES})"
        )
        lines.append(f"- Gap: not computed | verdict: {why}")

    for lane in ("native", "hip3"):
        inf = info[lane]
        st = lane_stats[lane]
        if inf["edges"]:
            med = statistics.median(inf["edges"])
            notional_ref = st["mean_notional"] if st["n"] else pooled_stats["mean_notional"]
            lane_claimed_zar = med * notional_ref
            claim_txt = (
                f"claimed median {100 * med:+.3f}% over {len(inf['edges'])}/"
                f"{inf['book_n']} slices (pool {inf['pool_n']}) ~ "
                f"{lane_claimed_zar:+.2f} ZAR"
            )
        else:
            med = None
            lane_claimed_zar = None
            claim_txt = (
                f"claimed unknown (0/{inf['book_n']} slices in pool {inf['pool_n']})"
            )
        if st["n"] == 0:
            real_txt = f"0 real closes | INSUFFICIENT SAMPLE (n<{MIN_VERDICT_CLOSES})"
        elif st["n"] < MIN_VERDICT_CLOSES:
            real_txt = (
                f"realised {st['n']} closes {st['mean']:+.2f} ZAR sd {st['sd']:.2f} | "
                f"INSUFFICIENT SAMPLE (n<{MIN_VERDICT_CLOSES})"
            )
        elif lane_claimed_zar is not None:
            lt = _gap_t(st["mean"], st["se"], lane_claimed_zar)
            real_txt = (
                f"realised {st['n']} closes {st['mean']:+.2f} ZAR sd {st['sd']:.2f} "
                f"SE {st['se']:.2f} | gap {st['mean'] - lane_claimed_zar:+.2f} "
                f"t {lt:+.2f} | {_verdict(lt, st['mean'], lane_claimed_zar)}"
            )
        else:
            real_txt = f"realised {st['n']} closes {st['mean']:+.2f} ZAR | claimed unknown"
        lines.append(f"- {lane}: {claim_txt} | {real_txt}")

    lines.append(
        f"- Ledger: {len(trade_rows)} decision rows; {n} real closes (outcome win/loss "
        f"and exit_reason in lane_gate.ACTUAL_EXITS, {len(lane_gate.ACTUAL_EXITS)} exit "
        f"reasons); the other {max(len(trade_rows) - n, 0)} rows are skipped/guard "
        f"decisions and never count"
    )
    lines.append("")
    lines.append(
        "_Read-only and advisory: this section feeds no gate, admission decision or "
        "promotion path._"
    )
    lines.append("")
    return "\n".join(lines)


def _short_audit_from_files() -> dict:
    """Compute a short audit directly from committed validated rows.

    This is the fallback when the committed research_done payload predates the
    short_audit field (so the daily print is honest even before the next run).
    """
    try:
        from breakwater.engine import _short_research_audit
        from breakwater.validation import read_validated

        validated = read_validated(DATA / "research" / "validated_slices.csv")
        discovered = []
        for r in _read_csv(DATA / "research" / "discovered_slices.csv"):

            class _R:
                pass

            row = _R()
            row.slice_id = r.get("slice_id")
            row.side = r.get("side")
            row.mean_ret_costadj = _num(r.get("mean_ret_costadj"))
            row.validated = False
            row.fail_reasons = ""
            discovered.append(row)
        return _short_research_audit(validated, discovered)
    except Exception:
        return {}


def _hip3_short_audit() -> dict:
    """Short evidence from the HIP-3 lane (best-effort, audit-only)."""
    try:
        from breakwater.engine import _short_research_audit
        from breakwater.validation import read_validated

        validated = read_validated(DATA / "hip3" / "research" / "validated_slices.csv")
        discovered = []
        for r in _read_csv(DATA / "hip3" / "research" / "discovered_slices.csv"):

            class _R:
                pass

            row = _R()
            row.slice_id = r.get("slice_id")
            row.side = r.get("side")
            row.mean_ret_costadj = _num(r.get("mean_ret_costadj"))
            row.validated = False
            row.fail_reasons = ""
            discovered.append(row)
        return _short_research_audit(validated, discovered)
    except Exception:
        return {}


def _report_text() -> str:
    now = _now()
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    add = lines.append

    add(f"# Breakwater daily print — {stamp}\n")
    add(
        "> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.\n"
    )

    # ---- gate / coma state, computed once and reused below ----
    gate = None
    tradability = None
    try:
        from breakwater.lane_gate import LANE_WINDOW, compute_green_gate, lane_tradability

        gate = compute_green_gate(DATA / "research" / "paper_trade_log.csv")
        tradability = lane_tradability(
            gate,
            (r.get("slice_id") for r in _book_rows(DATA / "research" / "monitored_slices.csv")),
            (
                r.get("slice_id")
                for r in _book_rows(DATA / "hip3" / "research" / "monitored_slices.csv")
            ),
        )
    except Exception:  # pragma: no cover - defensive
        gate = None
        tradability = None
    if tradability and tradability.get("coma"):
        add(f"> ## COMA ALARM — {', '.join(tradability['coma_lanes']).upper()}\n")
        add(
            "> No **proven** slice in this lane. Auditions can still open entries, so\n"
            "> this is not a dead lane: it trades, but nothing in it trades on a record\n"
            "> it earned, so it cannot unfreeze itself. The runner will keep reporting\n"
            "> operational, which is why this block exists. Attention, not intervention.\n"
        )
    elif tradability and (tradability["native_proven"] + tradability["hip3_proven"]) <= 3:
        add(
            f"> ## WARNING — only "
            f"{tradability['native_proven'] + tradability['hip3_proven']} proven slice(s) "
            f"trading (native {tradability['native_proven']}, "
            f"hip3 {tradability['hip3_proven']}); "
            f"{tradability['native_tradable'] + tradability['hip3_tradable']} slices are "
            f"auditioning in frozen lanes. One bad proven trade from coma.\n"
        )

    # ---- account / mode ----
    add("## 1. Posture\n")
    mode_rows = [r for r in _read_csv(DATA / "status.csv") if r.get("stage") == "guardian_ok"]
    if mode_rows:
        last = _load_detail(mode_rows[-1]["detail"])
        add(
            f"- Mode: **{last.get('mode')}** | VALR equity: **{last.get('equity_zar')} ZAR** | "
            f"high-water: **{last.get('high_water_zar')} ZAR**"
        )
        add(
            f"- Key perms: {', '.join(last.get('key_permissions') or [])} | perps API: "
            f"{last.get('perps_api')} {('(' + str(last.get('perp_state_error')) + ')') if last.get('perp_state_error') else ''}"
        )
        add(f"- risk_allowed: **{last.get('risk_allowed')}** reasons={last.get('risk_reasons')}\n")
    else:
        add("- No guardian_ok row found.\n")

    paper_positions = _read_json(DATA / "research" / "paper_positions.json", [])
    trade_rows = _read_csv(DATA / "research" / "paper_trade_log.csv")
    per_lane, recent = _paper_performance(trade_rows)

    equity_seed = 2000.0
    lifetime = sum(p["pnl"] for p in per_lane.values())
    paper_equity = equity_seed + lifetime

    add("## 2. Paper account\n")
    add(
        f"- Equity: **{paper_equity:.2f} ZAR** (seed {equity_seed:.0f}) | lifetime: "
        f"**{lifetime:+.2f} ZAR** | closed: {sum(p['closed'] for p in per_lane.values())}"
    )
    add(
        f"- Today: {recent['today']['native'][0] + recent['today']['hip3'][0]} closed, "
        f"**{recent['today']['native'][1] + recent['today']['hip3'][1]:+.2f} ZAR**"
    )
    add(
        f"- 7d: **{recent['7d']['native'][1] + recent['7d']['hip3'][1]:+.2f} ZAR** | "
        f"30d: **{recent['30d']['native'][1] + recent['30d']['hip3'][1]:+.2f} ZAR**\n"
    )

    # ---- claimed vs realised: read-only advisory verdict (section 2b) ----
    native_book = _book_rows(DATA / "research" / "monitored_slices.csv")
    hip3_book = _book_rows(DATA / "hip3" / "research" / "monitored_slices.csv")
    native_validated = _read_csv(DATA / "research" / "validated_slices.csv")
    hip3_validated = _read_csv(DATA / "hip3" / "research" / "validated_slices.csv")
    add(
        _claimed_vs_realised_section(
            trade_rows, native_book, hip3_book, native_validated, hip3_validated
        )
    )

    # ---- per lane ----
    add("## 3. Lanes\n")
    for lane in ("native", "hip3"):
        p = per_lane[lane]
        wr = (100 * p["wins"] / p["closed"]) if p["closed"] else 0.0
        add(f"### {lane.upper()}\n")
        add(
            f"- Closed: {p['closed']} | wins: {p['wins']} | win%: {wr:.1f} | P&L: "
            f"**{p['pnl']:+.2f} ZAR** | today: {recent['today'][lane][1]:+.2f} | "
            f"7d: {recent['7d'][lane][1]:+.2f} | 30d: {recent['30d'][lane][1]:+.2f}"
        )
        if p["by_exit"]:
            by_exit = ", ".join(
                f"{k} {v:+.1f}"
                for k, v in sorted(p["by_exit"].items(), key=lambda kv: kv[1], reverse=True)
            )
            add(f"- By exit: {by_exit}")
        if p["by_regime"]:
            by_reg = ", ".join(
                f"{k} {v[0]:.0f}/{v[1]:+.1f}"
                for k, v in sorted(p["by_regime"].items(), key=lambda kv: kv[1][1], reverse=True)
            )
            add(f"- By entry regime (n/pnl): {by_reg}")
        if p["by_slice"]:
            top = sorted(p["by_slice"].items(), key=lambda kv: kv[1][1], reverse=True)[:5]
            bot = sorted(p["by_slice"].items(), key=lambda kv: kv[1][1])[:5]
            add(
                "- Top slices: "
                + "; ".join(f"{k[:56]} {v[0]}n/{v[2]}w {v[1]:+.2f}" for k, v in top)
            )
            add(
                "- Worst slices: "
                + "; ".join(f"{k[:56]} {v[0]}n/{v[2]}w {v[1]:+.2f}" for k, v in bot)
            )
        if p["by_pair"]:
            top = sorted(p["by_pair"].items(), key=lambda kv: kv[1][1], reverse=True)[:5]
            bot = sorted(p["by_pair"].items(), key=lambda kv: kv[1][1])[:5]
            add("- Top pairs: " + "; ".join(f"{k} {v[0]}n {v[1]:+.2f}" for k, v in top))
            add("- Worst pairs: " + "; ".join(f"{k} {v[0]}n {v[1]:+.2f}" for k, v in bot))
        add("")

    # ---- open risk ----
    add("## 4. Open positions & risk\n")
    open_by_lane = _open_risk_summary(paper_positions)
    total_open_risk = 0.0
    for lane in ("native", "hip3"):
        rows = open_by_lane.get(lane, [])
        risk = sum(x["risk_zar"] for x in rows)
        total_open_risk += risk
        add(f"- **{lane.upper()}**: {len(rows)} open, stop-risk **{risk:.2f} ZAR**")
        for x in sorted(rows, key=lambda v: v["risk_zar"], reverse=True):
            add(
                f"  - {x.get('pair')} {x.get('side')} ntl={_num(x.get('notional_zar')):.0f} "
                f"risk={x['risk_zar']:.2f} bars={x.get('bars_held')} "
                f"stop={x.get('stop_price')} peak={x.get('peak_price')}"
            )
        add("")

    # ---- aggregate risk ----
    add("## 5. Aggregate risk leash\n")
    shadow_rows = [
        r
        for r in _read_csv(DATA / "status.csv")
        if r.get("stage") == "shadow_scan_done" and r.get("mode") == "shadow"
    ]
    last_scan_ts = ""
    if shadow_rows:
        last = _load_detail(shadow_rows[-1]["detail"])
        last_scan_ts = shadow_rows[-1].get("timestamp_utc", "")[:19]
        paper = last.get("paper") or {}
        cap = _num(paper.get("aggregate_risk_cap_zar"))
        oc = _num(paper.get("aggregate_open_risk_zar"))
        util = _num(paper.get("aggregate_risk_utilization"))
        status = paper.get("aggregate_risk_status")
        add(
            "- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any "
            "live position (there is no live executor); the computed open stop-risk "
            "is informational only."
        )
        add(
            f"- Computed open stop-risk (section 4): **{total_open_risk:.2f} ZAR** "
            f"(informational only, no cap applied)"
        )
        add(
            f"- Paper shadow ledger (gates paper entries only, nothing live): "
            f"**{oc:.2f} / {cap:.2f} ZAR | {100 * util:.1f}% | {status}**"
        )
        add(
            f"- Remaining: {paper.get('aggregate_risk_remaining_zar')} | "
            f"cap skips: {paper.get('aggregate_risk_cap_skips')} | unknown skips: {paper.get('aggregate_risk_unknown_skips')}"
        )
        add(f"- booked stats: {json.dumps(paper.get('book_stats'))}")
        hs = paper.get("highest_risk_position")
        if hs:
            add(f"- Highest-risk: **{hs.get('pair')}** {hs.get('risk_zar')} ZAR")
        add(
            f"- positions without bars: {paper.get('positions_without_new_bars')} | "
            f"replayed: {paper.get('replayed_bars')} | invalid: {paper.get('invalid_positions_quarantined')}"
        )
        add("")

    # ---- books (loaded once above for section 2b) ----
    add("## 6. Monitored books\n")
    add(f"- Native: {len(native_book)} | HIP-3: {len(hip3_book)}")
    add("- Native top (by paper P&L):")
    for r in _gate_top(native_book)[:8]:
        add(
            f"  - `{r['slice_id']}` edge={r['mean_ret_costadj']:.4f} n={r['n']} p={r['p_value']:.4f} "
            f"src={r['source']} unproven={r['hostile_unproven']} paper={r['paper_trades']}n/{r['paper_pnl_zar']:+.2f}"
        )
    add("- HIP-3 top (by paper P&L):")
    for r in _gate_top(hip3_book)[:8]:
        add(
            f"  - `{r['slice_id']}` edge={r['mean_ret_costadj']:.4f} n={r['n']} p={r['p_value']:.4f} "
            f"src={r['source']} unproven={r['hostile_unproven']} paper={r['paper_trades']}n/{r['paper_pnl_zar']:+.2f}"
        )
    add("")

    # ---- HIP-3 gate ----
    add("## 7. HIP-3 live gate\n")
    hip3_actual = [
        r
        for r in trade_rows
        if _lane(r.get("slice_id")) == "hip3"
        and str(r.get("outcome") or "") in {"win", "loss"}
        and str(r.get("exit_reason") or "") in ACTUAL_EXITS
    ]
    hip3_pnl = sum(_num(r.get("pnl_zar")) for r in hip3_actual)
    cf_rows = [
        r
        for r in _read_csv(DATA / "research" / "paper_counterfactual_log.csv")
        if _lane(r.get("slice_id")) == "hip3"
    ]
    add(
        f"- Closed paper trades: **{len(hip3_actual)}/50** | ghost rows: **{len(cf_rows)}/50** | "
        f"PnL: **{hip3_pnl:+.2f} ZAR**"
    )
    add(
        f"- Gate verdict: {'**READY**' if len(hip3_actual) >= 50 and len(cf_rows) >= 50 and hip3_pnl > 0 else '**NOT READY**'}"
    )
    hip3_gate = _read_json(DATA / "hip3" / "hip3_gate.json", {})
    if hip3_gate:
        add(
            f"- hip3_gate.json: paper_ready={hip3_gate.get('paper_ready')} live_ready={hip3_gate.get('live_ready')} "
            f"book_frozen={hip3_gate.get('book_frozen')} book_rows={hip3_gate.get('book_rows')}"
        )
        add(f"- live unresolved: {', '.join(hip3_gate.get('live_unresolved') or [])}")
    add("")

    # ---- research health ----
    add("## 8. Research / honesty checks\n")
    research_rows = [r for r in _read_csv(DATA / "status.csv") if r.get("stage") == "research_done"]
    if research_rows:
        last = _load_detail(research_rows[-1]["detail"])
        add(
            f"- Latest research: {last.get('server_time')} | discovered {last.get('discovered_slices')} | "
            f"validated {last.get('validated_slices')} | reg-confounded {last.get('regime_confounded_slices')} | "
            f"hostile-unproven {last.get('hostile_unproven_slices')}"
        )
        add(
            f"- floors: {json.dumps(last.get('book', {}).get('net_edge_floor_enter_bps'))} | "
            f"book: {json.dumps(last.get('book'))}"
        )
        short_audit = last.get("short_audit") or _short_audit_from_files()
        if short_audit:
            add(
                f"- Short audit: discovered={short_audit.get('shorts_discovered')} "
                f"validated={short_audit.get('shorts_validated')} passing={short_audit.get('shorts_passing')} "
                f"eligible={short_audit.get('shorts_eligible')} best={short_audit.get('best_short_edge_bps')}b "
                f"best_fail={short_audit.get('best_failing_short_fail_reasons')}"
            )
        add(f"- pair_errors: {json.dumps(last.get('pair_errors'))}")
    deep = _read_json(DATA / "deep_audit" / "summary.json", {})
    if deep:
        audit_rows = _read_csv(DATA / "deep_audit" / "candidates.csv")
        audit_pass = sum(1 for r in audit_rows if str(r.get("audit_pass") or "").strip() == "True")
        prelim_pass = sum(
            1 for r in audit_rows if str(r.get("preliminary_pass") or "").strip() == "True"
        )
        add(
            f"- Deep audit: candidates={deep.get('candidates')} preliminary_passes={prelim_pass} "
            f"audit_passes={audit_pass} plateaus={deep.get('families_with_plateaus')} "
            f"fetch_errors={deep.get('fetch_error_count')}"
        )
    add("")

    # ---- promotion / live readiness ----
    add("## 9. Live readiness checks\n")
    registry = _read_json(DATA / "promotion_registry.json", {})
    strategies = (registry or {}).get("strategies") or {}
    add(
        f"- Promotion registry strategies: **{len(strategies)}** | "
        f"live_capped: {sum(1 for v in strategies.values() if v.get('lifecycle') == 'live_capped')}"
    )
    live = {
        "1 live HL executor": "NOT PRESENT - hyperliquid.py is read-only; no mainnet signer",
        "2 mechanism canary": "NOT RUN - no testnet agent key / no signed action",
        "3 live aggregate risk in guardian": "NOT WIRED - guardian passes aggregate_open_risk_zar=0, loss-limit events never appended",
        "4 promotion registry valr_native": "NOT APPLICABLE TO HL - gate requires valr_native=True",
        "5 big-wave-only live path": "NOT YOUR BOOK - engine executes slice_id=='big-wave' only",
        "6 deep audit passes": f"{_int(deep.get('preliminary_passes'))} preliminary / {_int(deep.get('audit_pass'))} audit",
        "7 book regime durability": "NOT PROVEN - hostile_unproven can be True and still promoted",
    }
    for k, v in live.items():
        add(f"- {k}: {v}")
    add("")

    # ---- signals / skips today ----
    add("## 10. Regime shift\n")
    regime_state = _read_json(DATA / "research" / "regime_state.json", {})
    if regime_state:
        breadth = regime_state.get("breadth") or {}
        add(
            f"- Label: **{regime_state.get('label')}** | breadth bear={breadth.get('bear')} "
            f"bull={breadth.get('bull')} neutral={breadth.get('neutral')} | "
            f"symbols={regime_state.get('bear', 0) + regime_state.get('bull', 0) + regime_state.get('neutral', 0)}"
        )
        add(
            f"- confirmed_bear: **{regime_state.get('confirmed_bear')}** | "
            f"confirmed_bull: **{regime_state.get('confirmed_bull')}** | "
            f"flip: **{regime_state.get('flip')}** | flipped_from: {regime_state.get('flipped_from')} | "
            f"consecutive_bear: {regime_state.get('consecutive_bear')} / bull {regime_state.get('consecutive_bull')}"
        )
        add(f"- as_of: {regime_state.get('as_of')}")
        add(
            f"- Defensive gate: {'ON (wrong-direction entries blocked & opposite exits armed)' if regime_state.get('confirmed_bear') or regime_state.get('confirmed_bull') else 'off (no confirmed flip)'}"
        )
    else:
        add("- No regime_state.json yet (first paper cycle since the tracker was added).")
    add("")

    add("## 11. Short inventory\n")
    short_inv = _read_json(DATA / "research" / "short_inventory.json", {})
    if short_inv:
        add(
            f"- confirmed_bear: **{short_inv.get('confirmed_bear')}** | "
            f"promote_env: {'ON' if short_inv.get('promote_enabled') else 'OFF'}"
        )
        add(
            f"- candidates: {short_inv.get('candidates')} | eligible: {short_inv.get('eligible')} | "
            f"observations: {short_inv.get('observations')} | armable: **{short_inv.get('armable')}**"
        )
        if short_inv.get("armable_slices"):
            add(f"- Armable slices: {', '.join(short_inv.get('armable_slices') or [])}")
            add(f"- Armable pairs: {', '.join(short_inv.get('armable_pairs') or [])}")
        else:
            add("- No armable short today (no validated SHORT slice clears the floor).")
        for cand in (short_inv.get("candidates_sample") or [])[:6]:
            armable, reason = cand.get("armable") or [False, ""]
            add(
                f"  - `{cand.get('slice_id')}` edge={cand.get('edge_bps')}b n={cand.get('n')} "
                f"breadth={cand.get('breadth')} validated={cand.get('validated')} "
                f"prov={cand.get('provisional')} armable={armable} ({reason})"
            )
    hip3_short_audit = _hip3_short_audit()
    if hip3_short_audit:
        add(
            f"- HIP-3 short evidence: discovered={hip3_short_audit.get('shorts_discovered')} "
            f"validated={hip3_short_audit.get('shorts_validated')} passing={hip3_short_audit.get('shorts_passing')} "
            f"eligible={hip3_short_audit.get('shorts_eligible')} best={hip3_short_audit.get('best_short_edge_bps')}b "
            f"best_fail={hip3_short_audit.get('best_failing_short_fail_reasons')}"
        )
    else:
        add("- No HIP-3 short evidence file.")
    if not short_inv:
        add("- No short_inventory.json yet (first cycle with the short-observation hook).")
    add("")

    add("## 12. Green gate\n")
    try:
        if gate is None:
            raise RuntimeError("gate unavailable")
        if gate.enabled:
            native = gate.native
            hip3 = gate.hip3
            add(
                f"- Native lane: **{'GREEN' if gate.native_green else 'RED'}** | "
                f"closed={native.closed} pnl={native.pnl:+.2f} | "
                f"frozen={'YES' if 'native' in gate.frozen_lanes else 'NO'}"
            )
            add(
                f"- HIP-3 lane: **{'GREEN' if gate.hip3_green else 'RED'}** | "
                f"closed={hip3.closed} pnl={hip3.pnl:+.2f} | "
                f"frozen={'YES' if 'hip3' in gate.frozen_lanes else 'NO'}"
            )
            add(f"- Frozen lanes: {', '.join(sorted(gate.frozen_lanes)) or 'none'}")
            add(f"- Lane verdict judged on the last {LANE_WINDOW} closes per lane; section 3 is the "
                f"lifetime ledger. They differ by design, not by staleness.")
            add(f"- Green islands kept alive inside red lanes: {len(gate.green_islands)}")
            for sid, pnl in gate.green_islands.items():
                add(f"  - `{sid}` pnl={pnl:+.2f}")
            if tradability:
                native_book_n = len(_book_rows(DATA / "research" / "monitored_slices.csv"))
                hip3_book_n = len(_book_rows(DATA / "hip3" / "research" / "monitored_slices.csv"))
                add(
                    f"- Tradable slices: native **{tradability['native_tradable']}/{native_book_n}** | "
                    f"hip3 **{tradability['hip3_tradable']}/{hip3_book_n}**"
                )
                if tradability["coma"]:
                    add(
                        f"- **COMA LANES: {', '.join(tradability['coma_lanes'])}** — frozen with no "
                        f"tradable slice on an earned green record; auditions may still open."
                    )
            add(
                "- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new "
                "entries only; open positions run to their own stop/target/horizon."
            )
            add(f"- Slice blocks: {len(gate.blocked_slices)}")
            top = sorted(gate.blocked_slices.items(), key=lambda kv: kv[0])
            for sid, reason in top:
                add(f"  - `{sid}` {reason}")
        else:
            add("- Disabled (BREAKWATER_GREEN_GATE=0).")
    except Exception as exc:  # pragma: no cover - defensive
        add(f"- Could not compute green gate: {exc}")
    add("")

    add("## 13. Signal activity\n")
    last_scan = shadow_rows[-1] if shadow_rows else None
    if last_scan:
        d = _load_detail(last_scan["detail"])
        add(
            f"- Latest scan {last_scan_ts or '?'}: errors={d.get('errors')} signals={d.get('signals')} "
            f"regime_blocked={d.get('regime_blocked')}"
        )
        paper = d.get("paper") or {}
        add(
            f"- this cycle: closed={paper.get('closed')} new_signals={paper.get('new_signals')} "
            f"skipped={paper.get('skipped')} slot_full={paper.get('slot_full')} "
            f"slice_full={paper.get('slice_full')} pair_held={paper.get('pair_held')}"
        )
        add_funnel = [
            ("regime_blocked", d.get("regime_blocked")),
            ("lane_gate_blocked", d.get("lane_gate_blocked") or paper.get("lane_gate_blocked")),
            ("aggregate_risk_cap_skips", paper.get("aggregate_risk_cap_skips")),
            ("aggregate_risk_unknown_skips", paper.get("aggregate_risk_unknown_skips")),
            ("slice_full", paper.get("slice_full")),
            ("pair_held", paper.get("pair_held")),
            ("slot_full", paper.get("slot_full")),
            ("skipped", paper.get("skipped")),
        ]
        active = [(k, v) for k, v in add_funnel if v is not None]
        if active:
            add("- Action funnel: " + " | ".join(f"{k}={v}" for k, v in active))
        if d.get("no_action_reason"):
            add(
                f"- **NO ACTION:** dominant blocker = `{d.get('no_action_reason')}` "
                f"(funnel={json.dumps(d.get('no_action_funnel'))})"
            )
        if d.get("green_gate"):
            gg = d["green_gate"]
            add(
                f"- green_gate: native_green={gg.get('native_green')} hip3_green={gg.get('hip3_green')} "
                f"frozen={','.join(gg.get('frozen_lanes') or []) or 'none'} "
                f"islands={len(gg.get('green_islands') or {})} blocks={len(gg.get('blocked_slices') or {})}"
            )
        agg = paper.get("aggregate_risk_status")
        if agg:
            add(
                f"- aggregate_risk: {agg} open={paper.get('aggregate_risk_start_zar')} "
                f"cap={paper.get('aggregate_risk_cap_zar')} used={paper.get('aggregate_risk_utilization')} "
                f"remaining={paper.get('aggregate_risk_remaining_zar')} "
                f"replayed={paper.get('replayed_bars')} no_new_bars={paper.get('positions_without_new_bars')}"
            )
        add(f"- pair_errors: {json.dumps(d.get('pair_errors'))}")
    add("")

    add(
        "---\n_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._\n"
    )
    return "\n".join(lines)


def main() -> int:
    text = _report_text()
    today = _now().astimezone(timezone.utc).date().isoformat()
    out_dir = DATA / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{today}.md").write_text(text)
    (out_dir / "latest.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
