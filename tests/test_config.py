from decimal import Decimal

import pytest

from breakwater.config import MANDATE_ENV, get_settings


def _set_mandate(monkeypatch):
    for key, env_name in MANDATE_ENV.items():
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.setenv("BREAKWATER_INITIAL_EQUITY_ZAR", "331.45")
    monkeypatch.setenv("BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR", "222.07")
    monkeypatch.setenv("BREAKWATER_MAX_TOTAL_LOSS_ZAR", "109.38")
    monkeypatch.setenv("BREAKWATER_MAX_TOTAL_DRAWDOWN_FRACTION", "0.33")
    monkeypatch.setenv("BREAKWATER_RISK_PER_TRADE_ZAR", "6.63")
    monkeypatch.setenv("BREAKWATER_DAILY_LOSS_LIMIT_ZAR", "9.94")
    monkeypatch.setenv("BREAKWATER_SEVEN_DAY_LOSS_LIMIT_ZAR", "19.89")
    monkeypatch.setenv("BREAKWATER_MAX_AGGREGATE_OPEN_RISK_ZAR", "6.63")
    monkeypatch.setenv("BREAKWATER_MAX_POSITION_NOTIONAL_ZAR", "200.00")
    monkeypatch.setenv("BREAKWATER_MAX_EFFECTIVE_LEVERAGE", "1")
    monkeypatch.setenv("BREAKWATER_PERP_LEVERAGE_CAP", "3")
    monkeypatch.setenv("BREAKWATER_MAX_POSITIONS", "1")


def _clear_mandate(monkeypatch):
    for key, env_name in MANDATE_ENV.items():
        monkeypatch.delenv(env_name, raising=False)


def test_mandate_loads_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    _set_mandate(monkeypatch)
    settings = get_settings()
    assert settings.mandate is not None
    assert settings.mandate.initial_equity_zar == Decimal("331.45")
    assert settings.mandate.absolute_equity_floor_zar == Decimal("222.07")
    assert settings.mandate.max_position_notional_zar == Decimal("200.00")
    assert settings.mandate.perp_leverage_cap == Decimal("3")
    assert settings.mandate.max_positions == 1


def test_missing_mandate_is_none(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    _clear_mandate(monkeypatch)
    assert get_settings().mandate is None


def test_partial_mandate_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    _set_mandate(monkeypatch)
    monkeypatch.delenv("BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR")
    with pytest.raises(RuntimeError, match="partially configured"):
        get_settings()


def test_floor_must_be_below_initial_equity(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    _set_mandate(monkeypatch)
    monkeypatch.setenv("BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR", "400")
    with pytest.raises(RuntimeError, match="floor must be below"):
        get_settings()


def test_default_mode_is_readonly(monkeypatch, tmp_path):
    monkeypatch.delenv("BREAKWATER_MODE", raising=False)
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    settings = get_settings()
    assert settings.mode == "readonly"
    assert settings.writes_allowed is False


def test_live_requires_exact_ack(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("BREAKWATER_MODE", "live")
    monkeypatch.setenv("BREAKWATER_LIVE_ACK", "yes")
    settings = get_settings()
    assert settings.writes_allowed is False

    monkeypatch.setenv("BREAKWATER_LIVE_ACK", "I_ACCEPT_BREAKWATER_LIVE_RISK")
    assert get_settings().writes_allowed is True


def test_partial_credentials_fail(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("VALR_API_KEY", "key")
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="configured together"):
        get_settings()


def test_unknown_mode_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("BREAKWATER_MODE", "aggressive")
    with pytest.raises(RuntimeError, match="readonly, shadow, or live"):
        get_settings()
