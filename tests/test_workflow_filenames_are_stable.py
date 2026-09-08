"""GitHub Actions cron/webhook URLs embed the workflow FILENAME.

The external dispatcher (cron-job.org; HANDOVER section 9) POSTs the
``workflow_dispatch`` URL for each cron-targeted workflow, so renaming or
moving one of these files makes that POST 404 and silently stops the trading
cycle. Nothing inside the repo can observe the missed dispatch, so the
filename contract is asserted here instead of relying on prose.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

# Files the external cron POSTs. Times are SAST: paper :00/:30, guardian
# :05/:35, research daily 02:25. See HANDOVER.md section 9.
CRON_TARGETS = {
    "paper.yml",
    "guardian.yml",
    "research.yml",
    "hip3-research.yml",
    "hip3-discovery.yml",
}

# Workflows that are expected to exist but must NOT be dispatched by cron.
CI_ONLY = {"ci.yml"}


def _present() -> set[str]:
    return {p.name for p in WORKFLOWS.glob("*.yml")}


def test_cron_targeted_workflows_exist() -> None:
    missing = sorted(CRON_TARGETS - _present())
    assert not missing, (
        f"cron POSTs a dispatch URL for {missing}, but those files are absent; "
        "a renamed workflow silently stops its cycle -- restore the filename or "
        "update the dispatcher URL and this list together"
    )


def test_no_unexpected_workflows() -> None:
    extra = sorted(_present() - CRON_TARGETS - CI_ONLY)
    assert not extra, (
        f"unexpected workflow(s) {extra}: either give it a cron dispatch URL and "
        "add it to CRON_TARGETS, or leave it out of CRON_TARGETS deliberately"
    )


def test_cron_targets_declare_workflow_dispatch() -> None:
    """A cron POST needs the `workflow_dispatch:` trigger or it is rejected."""
    undispatched = [
        name
        for name in sorted(CRON_TARGETS & _present())
        if "workflow_dispatch:" not in (WORKFLOWS / name).read_text(encoding="utf-8")
    ]
    assert not undispatched, f"{undispatched} cannot be dispatched by cron"
