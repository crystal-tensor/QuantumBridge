# Stage 7.7 Main CI Failure Diagnosis v0.1

Date: 2026-06-08
Status: Local fix applied; push to `main` prepared

## 1. Main HEAD

- Starting `main` HEAD before fix: `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
- Starting title: `Stage 6.1/6.2 P2 Dual-Track Expansion: Core SDK + Chemistry/Algorithms Adapters (#1)`

## 2. Latest Actions run

- Workflow: `QuantumBridge Test Matrix`
- Latest observed run id before fix push: `27113410261`
- Branch: `main`
- Head sha: `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
- Status: `completed`
- Conclusion: `failure`
- URL: `https://github.com/crystal-tensor/QuantumBridge/actions/runs/27113410261`

## 3. Failed job

Observed non-advisory failing jobs on the original failed `main` run:

- `qiskit-optimization-extra`
- `chemistry-extra`
- `qiskit-nature-p2-extra`
- `chemistry-core`

These are non-advisory jobs and therefore had to be fixed rather than hidden.

## 4. Failure reason

Primary root causes found on `main`:

1. `pyproject.toml` was an empty tracked file.
2. `scripts/run_local_matrix.sh` was an empty tracked file.
3. Global `pytest` collection failed because two test files shared the same module basename:
   - `tests/chemistry/test_chemistry_result_schema.py`
   - `tests/compat_qiskit_nature/test_chemistry_result_schema.py`

Additional reproduction detail:

- In a clean virtual environment, `python -m pip install -e . pytest` failed before tests ran.
- Failure mode was editable-build package discovery falling back incorrectly because the tracked `pyproject.toml` no longer contained the explicit setuptools package selection.
- Once packaging metadata was restored, editable installation succeeded again.
- After the first restoration push, one remaining non-advisory failure persisted:
  - `qiskit-nature-extra`
- Exact local reproduction of that lane showed `tests/compat_qiskit_nature/test_nature_workflows.py` requires `PySCFDriver`, but `.[qiskit-nature]` did not install `pyscf`.
- Final fix for that lane:
  - add `pyscf` to the `qiskit-nature` extra

## 5. Whether PR #1 merge caused the issue

Yes.

Compared with PR #2 mainline commit `6ce01d3c6d923a83139cb03a1966ac46ff015770`,
the later PR #1 mainline commit `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
overwrote the following CI-critical files:

- `pyproject.toml` -> emptied
- `scripts/run_local_matrix.sh` -> emptied

PR #1 also introduced a broader P2 chemistry / algorithms test surface on `main`,
which made the existing duplicate test basename more visible during full
collection.

## 6. Whether PR #2 merge caused the issue

No for the failure itself.

PR #2 contributed the Stage 7 ecosystem workflow, extras, inventory scripts,
matrix docs, and advisory lane structure. Those pieces remained largely present.
The CI break happened because later `main` content no longer preserved two key
operational files from PR #2.

## 7. Whether merge order caused regression

Yes.

PR #2 merged first and established a valid Stage 7 ecosystem matrix baseline.
PR #1 merged later and partially preserved Stage 7 content while regressing the
shared operational entrypoints. The merge order therefore directly caused the
mainline regression.

## 8. Files inspected

- `pyproject.toml`
- `.github/workflows/test-matrix.yml`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/migration/source_migration_ledger.md`
- `scripts/run_local_matrix.sh`
- `scripts/inventory_*.py`
- `requirements/constraints-*`
- `tests/chemistry/*`
- `tests/compat_qiskit_*/*`
- `tests/compat_pennylane_full/*`
- `tests/ecosystem/*`
- `docs/compat/matrix/*`
- `docs/compat/inventory/*`

## 9. Fix applied

Applied minimal CI restoration only:

1. Restored `pyproject.toml` with explicit setuptools package discovery and merged optional extras from both PR lines.
2. Preserved Stage 7 extras used by workflow lanes:
   - `qiskit-aer`
   - `qiskit-finance`
   - `qiskit-optimization`
   - `qiskit-machine-learning`
   - `qiskit-dynamics`
   - `qiskit-experiments`
   - `qiskit-runtime`
   - `qiskit-addons`
   - `pennylane-full`
3. Restored Stage 6/P2 extras needed on `main`:
   - `chemistry`
   - `chemistry-compatible`
   - `chemistry-numpy2`
   - `qiskit-nature`
   - `algorithms`
   - `openfermion`
   - `quafu`
   - `quafu-compatible`
4. Restored `scripts/run_local_matrix.sh` with Stage 7 lanes plus Stage 6/P2 lanes:
   - `chemistry-core`
   - `chemistry-extra`
   - `qiskit-nature-p2-extra`
   - `algorithms-extra`
   - `openfermion-extra`
5. Renamed the duplicate-basename test file to avoid global pytest import collision:
   - from `tests/compat_qiskit_nature/test_chemistry_result_schema.py`
   - to `tests/compat_qiskit_nature/test_qiskit_nature_chemistry_result_schema.py`
6. Corrected the `qiskit-nature` extra so the non-advisory workflow lane installs `pyscf` in addition to `qiskit-nature` and `qiskit-algorithms`.

No feature behavior was added. No advisory lane was converted into production
support. No tag or release action was performed.

## 10. Tests run

Commands run after fix:

```bash
pytest -q -rs
pytest --cov=quantumbridge
bash scripts/run_local_matrix.sh
python3 -m venv /tmp/qb-ci-diag2
/tmp/qb-ci-diag2/bin/python -m pip install --upgrade pip setuptools wheel
/tmp/qb-ci-diag2/bin/python -m pip install -e . pytest
python3 -m venv /tmp/qb-qn2
/tmp/qb-qn2/bin/python -m pip install --upgrade pip
/tmp/qb-qn2/bin/python -m pip install -c requirements/constraints-qiskit-nature.txt -e '.[qiskit-nature]' pytest
/tmp/qb-qn2/bin/python scripts/inventory_qiskit_nature_api.py
/tmp/qb-qn2/bin/pytest -q -rs tests/compat_qiskit_nature
```

## 11. Local matrix result

Result after fix:

- `core-only`: pass
- `dev`: pass
- `chemistry-core`: pass
- `chemistry-extra`: pass with expected skips for unavailable optional dependencies
- `qiskit-nature-p2-extra`: pass with expected skips for unavailable optional dependencies
- `algorithms-extra`: pass with expected skips for unavailable optional dependencies
- `openfermion-extra`: skip only when optional dependency unavailable
- exact `qiskit-nature-extra` reproduction: `6 passed, 1 skipped`
- Stage 7 ecosystem lanes no longer fail due to empty runner file

## 12. GitHub Actions result

Before fix push:

- latest `main` run was `failure`

After local fix:

- local reproduction is green
- editable install is restored
- workflow-impacting files are restored
- a new remote result depends on pushing the fix commit to `main`

## 13. Remaining risks

- Some optional lanes still depend on upstream package availability and may skip.
- Advisory lanes remain advisory and should not be interpreted as production support.
- `gh` was not logged in locally, so diagnosis relied on public GitHub API plus local reproduction rather than `gh run view`.
- Node 20 deprecation warnings remain in GitHub Actions annotations, but they were warnings, not the cause of this CI failure.

## 14. Whether v0.3.0 release candidate review can proceed

Conditionally yes, but only after the fix commit is pushed to `main` and the
new GitHub Actions run turns green.

Local evidence after the fix is sufficient to justify pushing the CI repair.
