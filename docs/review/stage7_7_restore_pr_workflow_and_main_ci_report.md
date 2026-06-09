# Stage 7.7-R Restore PR Workflow and Main CI Report

Date: 2026-06-09
Status: Ready for PR

## 1. Current Branch

- Working branch: `fix/main-ci-stabilization`
- Workflow correction: QuantumBridge should use branch + pull request for new
  changes. Direct push to `main` is no longer the default workflow.

## 2. Main HEAD

- `main` / `origin/main` HEAD at branch creation:
  `eaabf7a687a341730a40423e6528ef741e052c02`
- Commit title: `docs: record Stage 7.7 main CI stabilization`

## 3. Main CI Status

- Latest checked GitHub Actions run: QuantumBridge Test Matrix #47
- Run URL: `https://github.com/crystal-tensor/QuantumBridge/actions/runs/27192245401`
- Branch: `main`
- Head commit: `eaabf7a687a341730a40423e6528ef741e052c02`
- Status: success
- Matrix: 22 jobs completed

`gh` is installed locally but not authenticated:

```text
You are not logged into any GitHub hosts. To log in, run: gh auth login
```

Because `gh run list` was unavailable, CI status was checked from the GitHub
Actions page and local reproduction.

## 4. Local Pytest Result

Command:

```bash
pytest -q -rs
```

Result:

- 178 passed
- 33 skipped
- 6 warnings

Skips were expected optional-dependency skips, including qiskit-nature,
qiskit-algorithms, openfermion, pyscf, and advisory ecosystem dependencies not
installed in the local environment.

## 5. Coverage

Command:

```bash
pytest --cov=quantumbridge
```

Result:

- 178 passed
- 33 skipped
- 6 warnings
- Total coverage: 86%

## 6. Local Matrix

Command:

```bash
bash scripts/run_local_matrix.sh
```

Result: completed successfully.

Observed lane behavior:

- `core-only`: pass
- `qiskit-extra`: pass
- `pennylane-extra`: pass
- `qiskit-aer-extra`: pass
- `qiskit-nature-extra`: pass with expected optional-driver skips
- `qiskit-algorithms-extra`: pass with expected optional dependency skips
- `pennylane-full-extra`: pass
- `ecosystem-inventory`: pass
- `chemistry-core`: pass
- `chemistry-extra`: pass with expected optional dependency skips
- `qiskit-nature-p2-extra`: pass with expected optional dependency skips
- `algorithms-extra`: pass with expected optional dependency skips
- `openfermion-extra`: skip when optional dependency unavailable
- Unavailable advisory or optional ecosystems were reported as not executed
  rather than treated as production support.

## 7. Main Regression Check

No current main regression was found.

The previous Stage 7.7 regression caused by PR #1 / PR #2 merge order has
already been repaired on `main`:

- `pyproject.toml` is restored and includes explicit package discovery plus
  Stage 6 / Stage 7 optional extras.
- `scripts/run_local_matrix.sh` is restored.
- duplicate pytest basename collision has been removed.
- `qiskit-nature` extra includes `pyscf` for the non-advisory installed-driver
  lane.

No additional CI code fix was required in this Stage 7.7-R pass.

## 8. PR #1 / PR #2 Merge Order

The earlier mainline failure was caused by merge-order regression:

- PR #2 first established Stage 7 workflow and ecosystem matrix content.
- PR #1 then landed Stage 6 content but overwrote CI-critical operational files
  in the merged history.
- That issue was repaired before this report.

Current `main` has both Stage 6 and Stage 7 content and passes local validation
plus the latest observed Actions run.

## 9. Files Checked

Checked file groups:

- `.github/workflows/test-matrix.yml`
- `pyproject.toml`
- `requirements/constraints-*`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/migration/source_migration_ledger.md`
- `scripts/inventory_*`
- `quantumbridge/compat/`
- `quantumbridge/schema/`
- `tests/compat_qiskit_*`
- `tests/compat_pennylane_full`
- `tests/chemistry`
- `tests/algorithms_compat`
- `tests/ecosystem`

Relevant findings:

- Advisory workflow profiles have `advisory: true`.
- Workflow has `continue-on-error: ${{ matrix.advisory == true }}`.
- README marks Qiskit Metal advisory/unsupported and Qiskit Experiments
  advisory/offline-only.
- THIRD_PARTY_NOTICES states upstream packages are not vendored.
- quafu / pyquafu remains isolated in a NumPy `<2` optional environment.
- chemistry / qiskit-nature remains in a NumPy 2.x optional environment.

## 10. Fix Content

This branch restores the PR-based workflow by documenting the corrected
process and the current main CI status.

No source code, dependency, workflow, release, tag, or vendored third-party
content was changed in this pass.

## 11. Whether A PR Is Needed

Yes.

Even though no CI code fix was needed, this report should be merged by PR so
the repository history records the workflow correction and current mainline
stability gate without direct-pushing to `main`.

## 12. Suggested PR Title

```text
docs: restore PR workflow and record Stage 7.7-R main CI status
```

## 13. Suggested PR Body

```markdown
## Summary

This PR restores the branch + pull request workflow for QuantumBridge and
records the Stage 7.7-R main CI stabilization check.

## Validation

- `pytest -q -rs`: 178 passed, 33 skipped, 6 warnings
- `pytest --cov=quantumbridge`: 178 passed, 33 skipped, 6 warnings
- Coverage: 86%
- `bash scripts/run_local_matrix.sh`: completed successfully
- Latest observed main Actions run #47: success, 22 jobs completed

## Risk

Low. This is a documentation/report-only PR.

## Non-goals

- No direct push to main
- No release
- No tag
- No Stage 8 implementation
- No third-party source vendoring
- No site-packages, wheel, dist-info, egg-info, or venv upload
- No production-support claim for advisory ecosystems
```

## 14. Stage 8 Gate

Yes, QuantumBridge can proceed to Stage 8 after this PR workflow restoration
report is reviewed and merged.

Stage 8 should proceed by branch + PR only and remain bounded to planned
Qiskit/PennyLane fusion work without claiming full replacement or production
parity.
