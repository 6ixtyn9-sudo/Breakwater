"""Configuration with immutable capital and loss boundaries."""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

INITIAL_EQUITY_ZAR = Decimal("331.45")
MAX_TOTAL_DRAWDOWN_FRACTION = Decimal("0.33")
ABSOLUTE_EQUITY_FLOOR_ZAR = Decimal("222.07")
MAX_TOTAL_LOSS_ZAR = Decimal("109.38")
RISK_PER_TRADE_ZAR = Decimal("3.31")
DAILY_LOSS_LIMIT_ZAR = Decimal("9.94")
SEVEN_DAY_LOSS_LIMIT_ZAR = Decimal("19.89")
MAX_AGGREGATE_OPEN_RISK_ZAR = Decimal("6.63")
MAX_POSITION_NOTIONAL_ZAR = Decimal("99.43")
MAX_EFFECTIVE_LEVERAGE = Decimal("1")
MAX_POSITIONS = 1
LIVE_ACKNOWLEDGEMENT = "I_ACCEPT_BREAKWATER_LIVE_RISK"


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    api_secret: str | None
    subaccount_id: str | None
    mode: str
    live_ack: str
    data_dir: Path
    price_candidates_url: str | None

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
    def candidates_path(self) -> Path:
        return self.data_dir / "price_candidates.csv"


def get_settings() -> Settings:
    mode = os.getenv("BREAKWATER_MODE", "readonly").strip().lower()
    if mode not in {"readonly", "shadow", "live"}:
        raise RuntimeError("BREAKWATER_MODE must be readonly, shadow, or live")
    data_dir = Path(os.getenv("BREAKWATER_DATA_DIR", "localdata"))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    settings = Settings(
        api_key=os.getenv("VALR_API_KEY") or None,
        api_secret=os.getenv("VALR_API_SECRET") or None,
        subaccount_id=os.getenv("VALR_SUBACCOUNT_ID") or None,
        mode=mode,
        live_ack=os.getenv("BREAKWATER_LIVE_ACK", "off"),
        data_dir=data_dir.resolve(),
        price_candidates_url=os.getenv("BREAKWATER_PRICE_CANDIDATES_URL") or None,
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    if bool(settings.api_key) != bool(settings.api_secret):
        raise RuntimeError("VALR_API_KEY and VALR_API_SECRET must be configured together")
    return settings
