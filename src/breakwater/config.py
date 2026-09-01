"""Configuration assembled from the environment.

The capital mandate is never compiled into this repository. Every boundary is
read from environment variables so that nothing personal appears in source
control. Any partial mandate is a configuration error and fails closed.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dotenv import load_dotenv

from breakwater.risk import RiskPolicy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

LIVE_ACKNOWLEDGEMENT = "I_ACCEPT_BREAKWATER_LIVE_RISK"

MANDATE_KEYS = [
    "initial_equity_zar",
    "absolute_equity_floor_zar",
    "max_total_loss_zar",
    "max_drawdown_fraction",
    "risk_per_trade_zar",
    "daily_loss_limit_zar",
    "seven_day_loss_limit_zar",
    "max_aggregate_open_risk_zar",
    "max_position_notional_zar",
    "max_effective_leverage",
    "perp_leverage_cap",
    "max_positions",
]

MANDATE_ENV = {
    "initial_equity_zar": "BREAKWATER_INITIAL_EQUITY_ZAR",
    "absolute_equity_floor_zar": "BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR",
    "max_total_loss_zar": "BREAKWATER_MAX_TOTAL_LOSS_ZAR",
    "max_drawdown_fraction": "BREAKWATER_MAX_TOTAL_DRAWDOWN_FRACTION",
    "risk_per_trade_zar": "BREAKWATER_RISK_PER_TRADE_ZAR",
    "daily_loss_limit_zar": "BREAKWATER_DAILY_LOSS_LIMIT_ZAR",
    "seven_day_loss_limit_zar": "BREAKWATER_SEVEN_DAY_LOSS_LIMIT_ZAR",
    "max_aggregate_open_risk_zar": "BREAKWATER_MAX_AGGREGATE_OPEN_RISK_ZAR",
    "max_position_notional_zar": "BREAKWATER_MAX_POSITION_NOTIONAL_ZAR",
    "max_effective_leverage": "BREAKWATER_MAX_EFFECTIVE_LEVERAGE",
    "perp_leverage_cap": "BREAKWATER_PERP_LEVERAGE_CAP",
    "max_positions": "BREAKWATER_MAX_POSITIONS",
}


def _decimal(name: str, value: str) -> Decimal:
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise RuntimeError(f"{name} is not a decimal") from exc
    if not number.is_finite():
        raise RuntimeError(f"{name} must be finite")
    return number


def _clean_credential(name: str, value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise RuntimeError(f"{name} is empty after trimming whitespace")
    if any(character.isspace() for character in cleaned):
        raise RuntimeError(
            f"{name} contains internal whitespace or newlines; "
            "re-export it cleanly before uploading it"
        )
    return cleaned


def _policy_from_mandate_values(raw_values: dict, *, source: str) -> RiskPolicy:
    if set(raw_values) != set(MANDATE_KEYS):
        missing = sorted(set(MANDATE_KEYS) - set(raw_values))
        extra = sorted(set(raw_values) - set(MANDATE_KEYS))
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unknown: " + ", ".join(extra))
        raise RuntimeError(f"{source} mandate schema is invalid; " + "; ".join(details))
    if any(isinstance(value, bool) for value in raw_values.values()):
        raise RuntimeError(f"{source} mandate values must be numbers, not booleans")
    values = {
        key: _decimal(f"{source}.{key}", raw_values[key])
        for key in MANDATE_KEYS
    }
    max_positions_decimal = values["max_positions"]
    max_positions = int(max_positions_decimal.to_integral_value())
    if max_positions_decimal != Decimal(max_positions):
        raise RuntimeError(f"{source}.max_positions must be a whole number")
    if max_positions < 1:
        raise RuntimeError(f"{source}.max_positions must be at least 1")
    if values["initial_equity_zar"] <= 0:
        raise RuntimeError(f"{source}.initial_equity_zar must be positive")
    if values["absolute_equity_floor_zar"] >= values["initial_equity_zar"]:
        raise RuntimeError("equity floor must be below initial equity")
    if values["perp_leverage_cap"] <= 0:
        raise RuntimeError(f"{source}.perp_leverage_cap must be positive")
    return RiskPolicy(
        initial_equity_zar=values["initial_equity_zar"],
        absolute_equity_floor_zar=values["absolute_equity_floor_zar"],
        max_total_loss_zar=values["max_total_loss_zar"],
        max_drawdown_fraction=values["max_drawdown_fraction"],
        risk_per_trade_zar=values["risk_per_trade_zar"],
        daily_loss_limit_zar=values["daily_loss_limit_zar"],
        seven_day_loss_limit_zar=values["seven_day_loss_limit_zar"],
        max_aggregate_open_risk_zar=values["max_aggregate_open_risk_zar"],
        max_position_notional_zar=values["max_position_notional_zar"],
        max_effective_leverage=values["max_effective_leverage"],
        perp_leverage_cap=values["perp_leverage_cap"],
        max_positions=max_positions,
    )


def mandate_from_env() -> RiskPolicy | None:
    json_payload = str(os.getenv("BREAKWATER_MANDATE_JSON") or "").strip()
    present = {
        key: os.getenv(env_name)
        for key, env_name in MANDATE_ENV.items()
        if os.getenv(env_name) not in (None, "")
    }
    if json_payload and present:
        raise RuntimeError(
            "capital mandate is configured through both BREAKWATER_MANDATE_JSON "
            "and legacy variables; choose exactly one source"
        )
    if json_payload:
        try:
            decoded = json.loads(json_payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("BREAKWATER_MANDATE_JSON is not valid JSON") from exc
        if not isinstance(decoded, dict):
            raise RuntimeError("BREAKWATER_MANDATE_JSON must be a JSON object")
        return _policy_from_mandate_values(decoded, source="BREAKWATER_MANDATE_JSON")
    if not present:
        return None
    if set(present) != set(MANDATE_ENV):
        missing = sorted(MANDATE_ENV[key] for key in MANDATE_ENV if key not in present)
        raise RuntimeError(
            "capital mandate is partially configured; missing: " + ", ".join(missing)
        )
    legacy_values = {key: present[key] for key in MANDATE_KEYS}
    return _policy_from_mandate_values(legacy_values, source="legacy mandate")


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    api_secret: str | None
    mode: str
    live_ack: str
    data_dir: Path
    mandate: RiskPolicy | None

    @property
    def has_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)

    @property
    def writes_allowed(self) -> bool:
        return self.mode == "live" and self.live_ack == LIVE_ACKNOWLEDGEMENT

    @property
    def ledger_path(self) -> Path:
        return self.data_dir / "breakwater.db"

    @property
    def status_path(self) -> Path:
        return self.data_dir / "status.csv"

    @property
    def registry_path(self) -> Path:
        return self.data_dir / "promotion_registry.json"

    @property
    def risk_state_path(self) -> Path:
        return self.data_dir / "risk_state.json"

    @property
    def universe_path(self) -> Path:
        return self.data_dir / "universe.csv"

    @property
    def discovered_path(self) -> Path:
        return self.data_dir / "research" / "discovered_slices.csv"

    @property
    def validated_path(self) -> Path:
        return self.data_dir / "research" / "validated_slices.csv"

    @property
    def asset_edges_path(self) -> Path:
        return self.data_dir / "research" / "asset_edges.csv"

    @property
    def book_path(self) -> Path:
        return self.data_dir / "research" / "monitored_slices.csv"

    @property
    def paper_log_path(self) -> Path:
        return self.data_dir / "research" / "paper_trade_log.csv"

    @property
    def cooldown_path(self) -> Path:
        return self.data_dir / "research" / "cooldown_journal.json"

    @property
    def hip3_data_dir(self) -> Path:
        return self.data_dir / "hip3"

    @property
    def hip3_universe_path(self) -> Path:
        return self.hip3_data_dir / "universe.csv"

    @property
    def hip3_status_path(self) -> Path:
        return self.hip3_data_dir / "status.csv"

    @property
    def hip3_dexs_path(self) -> Path:
        return self.hip3_data_dir / "dexs.json"

    @property
    def hip3_research_dir(self) -> Path:
        return self.hip3_data_dir / "research"

    @property
    def hip3_coverage_path(self) -> Path:
        return self.hip3_research_dir / "candle_coverage.csv"

    @property
    def hip3_book_path(self) -> Path:
        return self.hip3_research_dir / "monitored_slices.csv"

    @property
    def hip3_gate_path(self) -> Path:
        return self.hip3_data_dir / "gate.json"

    @property
    def hip3_discovered_path(self) -> Path:
        return self.hip3_research_dir / "discovered_slices.csv"

    @property
    def hip3_validated_path(self) -> Path:
        return self.hip3_research_dir / "validated_slices.csv"

    @property
    def hip3_asset_edges_path(self) -> Path:
        return self.hip3_research_dir / "asset_edges.csv"


def get_settings() -> Settings:
    mode = os.getenv("BREAKWATER_MODE", "readonly").strip().lower()
    if mode not in {"readonly", "shadow", "live"}:
        raise RuntimeError("BREAKWATER_MODE must be readonly, shadow, or live")
    data_dir = Path(os.getenv("BREAKWATER_DATA_DIR", "localdata"))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    api_key = os.getenv("VALR_API_KEY") or None
    api_secret = os.getenv("VALR_API_SECRET") or None
    if bool(api_key) != bool(api_secret):
        raise RuntimeError("VALR_API_KEY and VALR_API_SECRET must be configured together")
    if api_key is not None:
        api_key = _clean_credential("VALR_API_KEY", api_key)
        api_secret = _clean_credential("VALR_API_SECRET", api_secret or "")
        if api_key == api_secret:
            raise RuntimeError(
                "VALR_API_KEY and VALR_API_SECRET are identical; check the .env values"
            )
    settings = Settings(
        api_key=api_key,
        api_secret=api_secret,
        mode=mode,
        live_ack=os.getenv("BREAKWATER_LIVE_ACK", "off"),
        data_dir=data_dir.resolve(),
        mandate=mandate_from_env(),
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "research").mkdir(parents=True, exist_ok=True)
    settings.hip3_data_dir.mkdir(parents=True, exist_ok=True)
    settings.hip3_research_dir.mkdir(parents=True, exist_ok=True)
    return settings
