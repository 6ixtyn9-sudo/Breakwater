import re
from pathlib import Path

from scripts.migrate_actions_config import (
    ALLOWED_SECRET_REFERENCES,
    MANDATE_ENV_NAMES,
    migrate_workflow_text,
)

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_migration_keeps_only_real_secrets_and_is_idempotent():
    for name in ("guardian.yml", "paper.yml", "research.yml"):
        original = (ROOT / ".github" / "workflows" / name).read_text()
        migrated = migrate_workflow_text(original)
        secrets = set(re.findall(r"secrets\.([A-Z0-9_]+)", migrated))
        assert secrets <= ALLOWED_SECRET_REFERENCES
        assert migrate_workflow_text(migrated) == migrated
        for mandate_name in MANDATE_ENV_NAMES:
            assert f"{mandate_name}:" not in migrated
        if name in {"guardian.yml", "paper.yml"}:
            assert migrated.count("BREAKWATER_MANDATE_JSON:") == 1
        else:
            assert "BREAKWATER_MANDATE_JSON:" not in migrated


def test_live_ack_and_strategy_knobs_become_variables():
    guardian = migrate_workflow_text(
        (ROOT / ".github" / "workflows" / "guardian.yml").read_text()
    )
    research = migrate_workflow_text(
        (ROOT / ".github" / "workflows" / "research.yml").read_text()
    )
    assert "vars.BREAKWATER_LIVE_ACK" in guardian
    assert "secrets.BREAKWATER_LIVE_ACK" not in guardian
    assert "vars.BREAKWATER_RESEARCH_HORIZONS" in research
    assert "secrets.BREAKWATER_RESEARCH_HORIZONS" not in research
