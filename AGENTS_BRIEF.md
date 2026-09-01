# Agent brief: root-cause fixes + Sept fresh slate

Hand this brief to the other agents working the branch. It gives each agent a
self-contained task and the exact bash commands to run. The repo is on:

- Branch: `arena/01a052f8-breakwater`
- Local commit: `13a3426` (`feat: per-asset macro fix, evidence-gated shorts, September fresh slate`)
- Current state: `284 passed`, `ruff check .` clean, working tree clean.

## Reconciliation note (read before claiming commit hashes)

- An agent reported completing the 5 review fixes on `265e33f`, then a later
  report claimed `3fa852d`. Those commits, plus `1ecef11`, `ab3a826`, and
  `f8670f9`, are **not present** in this workspace: `git cat-file -t 265e33f`
  and `git cat-file -t 3fa852d` both fail, reflog does not contain them, and
  the local `origin/main` ref points at the clone-time commit `50f90de`.
- This workspace is the source of truth for this session: the same five fixes
  are **already present and committed** here in `13a3426` (verified by grep /
  `git status` clean).
- Do not cite the other agent's hashes unless you are in that agent's clone.
  Re-verify against this branch before pushing or opening a PR.
- **Do NOT set `SHORT_PROMOTE_ENABLED = False`.** That is a regression against
  the user's root-cause complaint ("why can't the system short?"): it makes
  `_armable()` return `promote_env_off` even for a validated short meeting every
  evidence floor. The intended state is `SHORT_PROMOTE_ENABLED = True` with
  `SHORT_USE_PROVISIONAL = False`, so promotion is strictly evidence-gated
  (validated + edge + breadth + confirmed bear). A later agent report claiming
  `SHORT_PROMOTE_ENABLED = False` should be rejected on this branch.

## Five review fixes (already present in `13a3426`)

- A.1/A.6 `read_asset_edges` fail-closed: missing file / bad schema raises
  `RuntimeError` (no silent allow-all).
- A.4 intentional allow-bias comment in `validation.py` around the untested
  verdict.
- C.13 calibration doc: `lane_gate.py` docstring + README now describe HIP-3
  freeze behavior and calibration values.
- C.15 per-asset visibility: `_asset_edge_status_counts` in `engine.py` and
  stale engine comment corrected to FAIL-CLOSED.
- Engine stale comment fixed (`grep FAIL-CLOSED` hits `engine.py`).

## Hard constraints (do not violate)

- **No env-var cold-start knobs.** The user explicitly rejected
  `BREAKWATER_PAPER_REGIME_WARMUP`. Do not re-add it, and do not introduce a
  similar env var for macro/regime/cold-start behavior. Fix root causes in code.
- **Do not merge to main.** Pushing the branch and opening a PR are allowed only
  in a NEW session; this session is closed to GitHub and must not attempt remote
  GitHub operations.
- **Shorting must stay honest.** Do not fabricate SHORT slices. Arming is
  evidence-gated: validated + edge floor + n + breadth + confirmed bear.
- **Keep green-gate cold-start/warm-up behavior** (`lane_gate.py`). It is valid
  and already lets warm-up lanes accumulate closes.

## Root causes already fixed

1. **Macro gate over-application.** `monitor.monitor_book()` was applying the
   global confirmed macro shift per symbol before the per-asset asset-edge gate.
   Fixed: per-asset edge gate runs first (`blocked` denied, `green`/`untested`
   allowed); the confirmed macro shift is portfolio context, not a per-asset hard
   block. It still drives `defensive_exit` and SHORT-inventory arming. The
   per-symbol `hostile_unproven` rule remains.
2. **Short promotion blockade.** `short_inventory._armable()` required a default-off
   operator env flag. Fixed: `SHORT_PROMOTE_ENABLED` is now true and promotion is
   evidence-gated. Data remains the blocker: zero validated SHORT slices exist.
3. **No SHORT edge (data, not a bug).** Live `main` `discovered_slices.csv` has
   SHORT candidates but all have negative cost-adjusted net edge (~-0.0067 to
   -0.007); `validated_slices.csv` has zero `validated=True` SHORT rows.
4. **Secondary side-flip rejection.** `validation.validate_slices()` re-chooses
   direction on the training-only window. Live rows show some LONG candidates
   failing `direction_ok` with `side_train=SHORT`.

## Agent tasks

### Agent A — Code review
File set:
- `src/breakwater/monitor.py`
- `src/breakwater/regime_tracker.py`
- `src/breakwater/paper_trade.py`
- `src/breakwater/short_inventory.py`
- `src/breakwater/lane_gate.py`

Check:
- Per-asset `asset_edge_lookup` runs before `regime_gate` in `monitor_book`.
- `regime_gate` denies `asset_status == "blocked"` and does NOT hard-block
  green/untested assets on a confirmed macro shift.
- Per-symbol `hostile_unproven` rule still blocks an asset whose own bar is
  hostile.
- No `BREAKWATER_PAPER_REGIME_WARMUP` / `BREAKWATER_SHORT_OBSERVATION_PROMOTE`
  exists anywhere.
- `SHORT_PROMOTE_ENABLED is True` and `SHORT_USE_PROVISIONAL is False` (the
  evidence-gated combination). Reject any change that sets
  `SHORT_PROMOTE_ENABLED = False`.
- A validated SHORT can arm under the evidence floor; invalid/below-floor/
  thin-breadth shorts still cannot.

### Agent B — Data evidence
Verify the no-short claim from the live `main` artifacts:
- `localdata/research/discovered_slices.csv`
- `localdata/research/validated_slices.csv`
- `localdata/research/monitored_slices.csv`

Check:
- Count SHORT candidates in discovered and SHORT rows with `validated=True` in
  validated (expect 0).
- Confirm all real SHORT candidates have negative `mean_ret_costadj`.
- Confirm monitored book has zero SHORT rows.
- Record any `direction_ok` side-flip rejections as secondary evidence only.

### Agent C — Verification
Run:
- Full pytest + ruff.
- Focused tests for the root-cause fix.
- `grep` for stale env-var artifacts.

### Agent D — Ops: use a Codespace, action on `main` without merging #3
- Use a GitHub Codespace (or another session authenticated as the repo owner),
  not the GitHub App. The App may lack `workflows` scope; a Codespace runs git
  ops under the repository owner's credentials, so it can push `.github/workflows/*`.
- Check out `main` (in the Codespace).
- Apply the full current delta: per-asset macro fix, evidence-gated shorts
  (`SHORT_PROMOTE_ENABLED=True`, `SHORT_USE_PROVISIONAL=False`,
  `SHORT_INVENTORY_ENABLED=True` as constants), green-gate cold-start, the 5
  review fixes, and the fresh-slate state files.
- Verify with pytest/ruff and the stale-env grep.
- Do **not** merge PR #3 and do not create/merge any merge to `main`.
- Leave the applied delta as an unmerged working change on `main` (or on the
  branch if that is the agreed transport). If the user later authorizes a push,
  push the branch — never a merge commit.

## Prompt to send the other agent (verbatim)

> "Action this delta on `main` without merging 3. Use a GitHub Codespace (or a
> session authenticated as the repo owner) — not the GitHub App, which lacks the
> `workflows` repository permission for committing/pushing `.github/workflows/*`.
> Check out `main` in the Codespace, apply the full work: per-asset macro gate before the
> macro aggregate, evidence-gated shorts (`SHORT_PROMOTE_ENABLED=True`,
> `SHORT_USE_PROVISIONAL=False`, `SHORT_INVENTORY_ENABLED=True` as constants,
> no `BREAKWATER_SHORT_OBSERVATION_PROMOTE` and no
> `BREAKWATER_PAPER_REGIME_WARMUP`), green-gate cold-start, the 5 review fixes
> (read_asset_edges fail-closed, allow-bias comment, calibration docs,
> per-asset visibility counts, FAIL-CLOSED engine comment), and the fresh-slate
> state reset. Run pytest/ruff and the stale-env grep, confirm the 5 fixes, and
> leave it applied but unmerged. Do NOT merge PR #3 and do not push any merge to
> main. Re-verify hashes against `git log --oneline -4` in your own clone before
> reporting back."

## Bash prompts to run

```bash
# --- state -------------
cd /home/user/Breakwater
git branch --show-current
git log --oneline -3
git status --short

# --- full verification ---
PYTHONPATH=src:/home/user/Breakwater/scripts python -m pytest -q
python -m ruff check .

# --- focused verification ---
PYTHONPATH=src:/home/user/Breakwater/scripts python -m pytest \
  tests/test_regime_tracker.py \
  tests/test_paper.py \
  tests/test_short_inventory.py \
  tests/test_monitor.py \
  -q

# --- reject env-var artifacts ---
grep -rn "BREAKWATER_PAPER_REGIME_WARMUP\|BREAKWATER_SHORT_OBSERVATION_PROMOTE" \
  src tests scripts .github || echo "NO-STALE-ENV"

# --- data evidence (Agent B) ---
python - <<'PY'
import csv
from collections import Counter
for path in [
    "localdata/research/discovered_slices.csv",
    "localdata/research/validated_slices.csv",
    "localdata/research/monitored_slices.csv",
]:
    try:
        with open(path) as fh:
            rows = list(csv.DictReader(fh))
        sides = Counter(r.get("side", "").upper() for r in rows)
        if "validated" in rows[0] if rows else False:
            val = Counter(str(r.get("validated", "")).strip() for r in rows)
        else:
            val = {}
        print(path, "rows", len(rows), "sides", dict(sides), "validated", dict(val))
    except FileNotFoundError:
        print(path, "MISSING")
PY

# --- ops: push + open PR (RUN IN A NEW SESSION ONLY) ---
git fetch origin
git push -u origin arena/01a052f8-breakwater
gh pr create \
  --base main \
  --head arena/01a052f8-breakwater \
  --title "feat: root-cause fixes: per-asset macro gate + evidence-gated shorts (Sept fresh slate)" \
  --body "Fresh slate reset + green-gate cold-start + per-asset research + root-cause fixes. No env-var cold-start knobs. Do not merge; review first."

# --- action this on main without merging 3 (Agent D) ---
# Use a fresh/github-connected clone. Apply the delta, do NOT merge PR #3.
git fetch origin arena/01a052f8-breakwater
git checkout main
git log --oneline -4
# HEAD_HASH = the branch tip from `git rev-parse origin/arena/01a052f8-breakwater`.
# Apply only the branch's own commits as unstaged work:
git cherry-pick --no-commit "$HEAD_HASH"
git status --short
git diff --cached --stat
# Do not commit/push a merge. Do not merge PR #3.
