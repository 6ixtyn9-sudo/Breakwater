"""Versioned, read-only import of Price crypto research candidates."""

from __future__ import annotations

import io
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pandas as pd
import requests

from breakwater.decimal_utils import D
from breakwater.models import Side

REQUIRED_COLUMNS = {
    "symbol", "timeframe", "slice_combination", "side", "bin_mode",
    "valid_n", "valid_mean_ret_costadj", "valid_p_value_nw",
    "walk_forward_pass_pattern", "search_wide_bh_pass",
    "search_wide_bonferroni_pass",
}


@dataclass(frozen=True)
class PriceCandidate:
    candidate_id: str
    source_symbol: str
    timeframe: str
    slice_combination: str
    side: Side
    validation_count: int
    net_validation_return: Decimal
    validation_p_value: Decimal
    walk_forward_passes: int
    bh_pass: bool
    bonferroni_pass: bool


def _truth(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_candidates(frame: pd.DataFrame) -> list[PriceCandidate]:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise RuntimeError(f"Price candidate file is missing columns: {sorted(missing)}")
    out = []
    for _, row in frame.iterrows():
        symbol = str(row["symbol"]).strip().upper()
        side_text = str(row["side"]).strip().upper()
        if not symbol or side_text not in {"LONG", "SHORT", "BUY", "SELL"}:
            continue
        side = Side.BUY if side_text in {"LONG", "BUY"} else Side.SELL
        combination = str(row["slice_combination"]).strip()
        timeframe = str(row["timeframe"]).strip().lower()
        candidate_id = __import__("hashlib").sha256(
            f"{symbol}|{timeframe}|{combination}|{side.value}".encode()
        ).hexdigest()[:20]
        out.append(PriceCandidate(
            candidate_id=candidate_id,
            source_symbol=symbol,
            timeframe=timeframe,
            slice_combination=combination,
            side=side,
            validation_count=int(row["valid_n"]),
            net_validation_return=D(row["valid_mean_ret_costadj"]),
            validation_p_value=D(row["valid_p_value_nw"]),
            walk_forward_passes=int(row["walk_forward_pass_pattern"]),
            bh_pass=_truth(row["search_wide_bh_pass"]),
            bonferroni_pass=_truth(row["search_wide_bonferroni_pass"]),
        ))
    return out


def load_candidates(path: Path) -> list[PriceCandidate]:
    if not path.exists():
        return []
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise RuntimeError(f"Price candidate file is unreadable: {exc}") from exc
    return parse_candidates(frame)


def refresh_candidates(url: str, path: Path, *, timeout: float = 30) -> int:
    if not url.startswith("https://raw.githubusercontent.com/"):
        raise RuntimeError("Price candidate URL must use raw.githubusercontent.com over HTTPS")
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    frame = pd.read_csv(io.StringIO(response.text))
    candidates = parse_candidates(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(response.text)
    temporary.replace(path)
    return len(candidates)


def candidate_pairs(
    candidate: PriceCandidate,
    active_spot: set[str],
    active_futures: set[str],
) -> list[str]:
    base = candidate.source_symbol.split("/")[0]
    if candidate.side is Side.SELL:
        target = f"{base}USDTPERP"
        return [target] if target in active_futures else []
    preferred = [f"{base}ZAR", f"{base}USDT", f"{base}USDTPERP"]
    return [pair for pair in preferred if pair in active_spot or pair in active_futures]
