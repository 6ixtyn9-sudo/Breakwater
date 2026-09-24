"""The capped canary mandate: small, published, and enforced by the same code.

A canary is not a smaller version of going live, it is a different claim: "we
believe the mechanism works end to end on a real venue, and we are willing to
pay a few ZAR to find out". So the numbers here are deliberately small and the
loss caps are deliberately close:

===============  =======  ====================================================
field            value    why
===============  =======  ====================================================
initial_equity    500.00  live VALR equity is ~497 ZAR; the mandate must not
                          claim more capital than exists
equity_floor      450.00  a 10% hole stops the canary before it becomes a
                          position
max_total_loss     50.00  the whole canary may lose 10% of the account
daily_loss_limit   15.00  one bad session stops trading for the day
seven_day_limit    30.00  three bad sessions stop it for the week
agg_open_risk      10.00  two positions at max risk cannot both be open
notional_cap      100.00  the requested 50-100 ZAR ceiling per position
risk_per_trade      5.00  1% of the mandate per trade
max_positions          1  one position at a time, like the paper book
max_leverage           1  cash spot only; no margin, no leverage
perp_leverage_cap      1  perps are code-locked regardless; belt and braces
===============  =======  ====================================================

This module exists so the preset is *executable and tested* rather than prose
in a document that rots. It arms nothing: it builds a RiskPolicy. Arming still
requires ``BREAKWATER_MODE=live``, ``BREAKWATER_LIVE_ACK``, credentials, and a
LIVE_CAPPED row in the promotion registry - each of which the operator must set
deliberately, and the last of which the promotion gate refuses to write until
the evidence supports it.
"""

from __future__ import annotations

import json
from decimal import Decimal

from breakwater.config import _policy_from_mandate_values
from breakwater.risk import RiskPolicy

CANARY_MANDATE: dict[str, str] = {
    "initial_equity_zar": "500.00",
    "absolute_equity_floor_zar": "450.00",
    "max_total_loss_zar": "50.00",
    "max_drawdown_fraction": "0.10",
    "risk_per_trade_zar": "5.00",
    "daily_loss_limit_zar": "15.00",
    "seven_day_loss_limit_zar": "30.00",
    "max_aggregate_open_risk_zar": "10.00",
    "max_position_notional_zar": "100.00",
    "max_effective_leverage": "1",
    "perp_leverage_cap": "1",
    "max_positions": "1",
}


def canary_mandate_json() -> str:
    """Serialise the preset exactly as ``BREAKWATER_MANDATE_JSON`` expects."""
    return json.dumps(CANARY_MANDATE, sort_keys=True, separators=(",", ":"))


def canary_policy() -> RiskPolicy:
    """Build the canary mandate through the same validator production uses.

    Any drift in the mandate schema fails here, in a test, instead of at 2am
    on the first live run.
    """
    return _policy_from_mandate_values(dict(CANARY_MANDATE), source="canary preset")


def canary_notional_ceiling_zar() -> Decimal:
    return canary_policy().max_position_notional_zar
