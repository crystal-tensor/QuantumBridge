# Stage 6.3 Dependency Compatibility Report

## 1. New / Modified Files

New:

- `docs/review/stage6_3_dependency_compatibility_review.md`
- `docs/implementation/stage6_3_dependency_compatibility_report.md`
- `requirements/constraints-core.txt`
- `requirements/constraints-chemistry.txt`
- `requirements/constraints-quafu.txt`
- `requirements/constraints-dev.txt`
- `tests/compat/test_quafu_dependency_compatibility.py`

Modified:

- `pyproject.toml`
- `.github/workflows/test-matrix.yml`
- `scripts/run_local_matrix.sh`
- `README.md`

## 2. PR Creation

PR creation was attempted.

Result:

- `gh auth status`: not logged in.
- GitHub connector PR creation: `403 Resource not accessible by integration`.

PR was not created by automation.

## 3. PR URL

Manual PR URL:

`https://github.com/crystal-tensor/QuantumBridge/pull/new/p2/dual-track-expansion`

## 4. Dependency Conflict Conclusion

The conflict is real:

- `pyquafu==0.4.5` requires `numpy<2.0.0,>=1.20.3`.
- `qiskit-nature==0.8.0` requires `numpy>=2`.

These cannot be satisfied together in the same environment with the verified Stage 6.2 package versions.

## 5. Was PyQuafu + NumPy Conflict Solved?

Not in a single environment.

It was solved operationally by adding separate extras, constraints, and CI profiles:

- `quafu` / `quafu-compatible`: NumPy 1.x.
- `chemistry` / `chemistry-compatible`: NumPy 2.x.

## 6. Should Chemistry / Quafu Environments Be Split?

Yes.

This is the recommended installation and CI strategy until upstream dependency ranges become compatible.

## 7. Constraints Files

Added:

- `constraints-core.txt`: core NumPy range.
- `constraints-chemistry.txt`: verified chemistry stack with NumPy 2.
- `constraints-quafu.txt`: `pyquafu==0.4.5` with `numpy<2`.
- `constraints-dev.txt`: pytest and coverage helpers.

## 8. CI Matrix Updates

Added / confirmed:

- `chemistry-compatible`
- `quafu-compatible`

The matrix does not require `all-optional` to pass.

## 9. Local Test Results

Core/default Python 3.9 path:

- `pytest -q -rs`: `108 passed, 18 skipped`

Installed Python 3.12 path from Stage 6.2 remains:

- `python3 -m pytest -q -rs`: `125 passed`

Targeted quafu-compatible venv:

- `/tmp/qb-quafu-venv/bin/python -m pytest -q -rs tests/compat/test_quafu_dependency_compatibility.py`: `1 passed`

Local matrix:

- `bash scripts/run_local_matrix.sh`: passed.
- Combined chemistry/numpy2 environment `quafu-compatible` subsection: `1 skipped`, because that environment is intentionally not quafu-compatible.

## 10. Pip Check Result

Current combined Python 3.12 environment:

```text
pyquafu 0.4.5 has requirement numpy<2.0.0,>=1.20.3, but you have numpy 2.4.6.
```

This failure is expected in the combined local environment and is the reason Stage 6.3 splits environments.

## 11. Skipped Tests

Default Python 3.9 path skips optional dependency tests when optional dependencies are unavailable:

- Qiskit Algorithms installed tests skipped.
- Qiskit Nature / PySCF / OpenFermion installed tests skipped.

The installed Python 3.12 chemistry environment ran these tests in Stage 6.2 without skips.

## 12. Coverage

Coverage should be reported from the relevant environment:

- Stage 6.2 installed chemistry environment: `86%`.
- Stage 6.3 default Python 3.9 environment: `pytest --cov=quantumbridge` produced `108 passed, 18 skipped`, coverage `84%`.
- Stage 6.3 combined Python 3.12 chemistry environment inside local matrix: coverage `86%`, with the quafu compatibility test skipped because NumPy 2 is installed.

## 13. Recommend P2 Review?

Yes, after the PR is manually created and expanded GitHub Actions matrix runs.

## 14. Recommend Merge?

Not yet.

Merge should wait for:

- Manual PR creation.
- Remote CI completion.
- Reviewer acceptance of split chemistry/quafu environment strategy.

## 15. Recommend v0.2.0-alpha1?

Not yet.

Alpha should wait for:

- P2 review.
- Remote expanded CI.
- Dependency compatibility decision recorded in release notes.
- Legal / attribution review for optional upstream dependency wording.
