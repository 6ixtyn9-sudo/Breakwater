from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_workflows_parse_and_execution_is_externally_dispatched():
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        payload = yaml.safe_load(path.read_text())
        assert payload
    guardian = (ROOT / ".github" / "workflows" / "guardian.yml").read_text()
    research = (ROOT / ".github" / "workflows" / "research.yml").read_text()
    assert "workflow_dispatch" in guardian
    assert "workflow_dispatch" in research
    assert "schedule:" not in guardian
    assert "schedule:" not in research


def test_guardian_defaults_to_readonly():
    text = (ROOT / ".github" / "workflows" / "guardian.yml").read_text()
    assert "BREAKWATER_MODE" in text
    assert "readonly" in text
    assert "BREAKWATER_LIVE_ACK" in text


def test_workflow_does_not_expose_forbidden_permissions():
    text = "\n".join(
        path.read_text() for path in (ROOT / ".github" / "workflows").glob("*.yml")
    )
    assert "VALR_API_SECRET:" in text
    assert "withdraw" not in text.lower()
    assert "transfer" not in text.lower()
