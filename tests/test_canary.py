from decimal import Decimal

from breakwater.canary import (
    CANARY_MANDATE,
    canary_mandate_json,
    canary_notional_ceiling_zar,
    canary_policy,
)
from breakwater.config import MANDATE_KEYS


def test_canary_preset_uses_exactly_the_production_mandate_schema():
    assert set(CANARY_MANDATE) == set(MANDATE_KEYS)


def test_canary_mandate_json_round_trips_through_the_validator():
    policy = canary_policy()
    assert policy.initial_equity_zar == Decimal("500.00")
    assert policy.absolute_equity_floor_zar == Decimal("450.00")
    assert policy.max_positions == 1
    assert policy.max_effective_leverage == Decimal("1")


def test_canary_caps_are_tight_enough_to_be_a_canary():
    policy = canary_policy()
    # The notional ceiling is the 50-100 ZAR band the operator asked for.
    assert Decimal("50") <= policy.max_position_notional_zar <= Decimal("100")
    # One position at max risk fits inside the aggregate leash with headroom.
    assert policy.risk_per_trade_zar < policy.max_aggregate_open_risk_zar
    # And the aggregate leash is a small fraction of the mandate.
    assert policy.max_aggregate_open_risk_zar <= policy.initial_equity_zar * Decimal("0.05")
    # Daily and weekly caps are ordered and below the lifetime cap.
    assert policy.daily_loss_limit_zar < policy.seven_day_loss_limit_zar
    assert policy.seven_day_loss_limit_zar < policy.max_total_loss_zar
    # The floor is a real floor: losses stop before the account is gone.
    assert policy.initial_equity_zar - policy.absolute_equity_floor_zar == Decimal("50.00")


def test_canary_json_is_a_plain_object_with_string_numbers():
    import json

    decoded = json.loads(canary_mandate_json())
    assert isinstance(decoded, dict)
    assert all(isinstance(value, str) for value in decoded.values())


def test_canary_does_not_arm_anything():
    """Building the preset must not touch mode, ack or credentials."""
    import os

    for name in ("BREAKWATER_MODE", "BREAKWATER_LIVE_ACK"):
        assert os.getenv(name) in (None, "off", "readonly", "shadow", ""), (
            f"{name} must stay unarmed while the preset is merely built"
        )
    assert canary_notional_ceiling_zar() == Decimal("100.00")
