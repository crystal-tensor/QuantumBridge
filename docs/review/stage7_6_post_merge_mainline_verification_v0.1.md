# Stage 7.6 Post-Merge Mainline Verification v0.1

Date: 2026-06-08
Status: Verification complete; mainline regression detected

## 1. Main HEAD commit

- Main HEAD: `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
- Main commit title: `Stage 6.1/6.2 P2 Dual-Track Expansion: Core SDK + Chemistry/Algorithms Adapters (#1)`

## 2. PR #1 merge commit

- PR #1 mainline commit: `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
- Merge mode observed on `main`: single mainline commit, not a traditional two-parent merge commit

## 3. PR #2 merge commit

- PR #2 mainline commit: `6ce01d3c6d923a83139cb03a1966ac46ff015770`
- Merge mode observed on `main`: single mainline commit, not a traditional two-parent merge commit

## 4. Merge-order risk summary

PR #2 reached `main` first and added the Stage 7 ecosystem workflow, documentation,
constraints, inventory coverage, and local matrix runner. PR #1 then reached `main`
later as commit `6dfe9b7` and preserved much of the Stage 7 file tree, but it also
deleted critical Stage 7 operational files that had been added by PR #2.

Observed regression introduced on current `main` relative to PR #2 commit `6ce01d3`:

- `pyproject.toml` is now an empty tracked file on `main`
- `scripts/run_local_matrix.sh` is now an empty tracked file on `main`
- `.github/workflows/test-matrix.yml` still contains Stage 7 ecosystem jobs and Stage 6 P2 jobs
- `README.md` Stage 7 wording remains present
- `THIRD_PARTY_NOTICES.md` and `docs/migration/source_migration_ledger.md` still contain Stage 7 and Stage 6/P2 records

Conclusion: PR #1 did not wipe out all Stage 7 content, but it did overwrite two
critical operational assets from PR #2, creating a real post-merge mainline
regression.

## 5. Stage 6 content presence

Stage 6 / P2 content is present on `main`, including:

- `quantumbridge/chemistry/*`
- `quantumbridge/algorithms/*`
- `quantumbridge/schema/*`
- `requirements/constraints-chemistry.txt`
- `requirements/constraints-core.txt`
- `requirements/constraints-dev.txt`
- `requirements/constraints-quafu.txt`
- Stage 6 implementation and review documents under `docs/implementation/` and `docs/review/`

Result: Stage 6 content exists on current `main`.

## 6. Stage 7 content presence

Stage 7 ecosystem coverage content is still present on `main`, including:

- Qiskit Nature adapters and inventory artifacts
- Qiskit Finance adapters and inventory artifacts
- Qiskit Algorithms adapters and inventory artifacts
- Qiskit Machine Learning adapters and inventory artifacts
- Qiskit Optimization adapters and inventory artifacts
- Qiskit Dynamics adapters and inventory artifacts
- Qiskit Experiments adapters and inventory artifacts
- Qiskit Aer adapters and inventory artifacts
- PennyLane full adapters and inventory artifacts
- Qiskit Metal advisory documentation and inventory artifacts
- Qiskit Runtime offline-only wording and runtime inventory artifacts
- Qiskit Addons advisory inventory artifacts
- Level 0 / Level 1 / Level 2 matrix wording in README and review docs
- "not full replacement" / "not production" / advisory wording in README and review docs

Result: Stage 7 ecosystem coverage is largely present on current `main`.

## 7. Dependency extras status

Current `main` fails this check.

- `pyproject.toml` was present with full extras at PR #2 commit `6ce01d3`
- Current `main` tracked `pyproject.toml` is empty
- Therefore current `main` no longer carries the declared optional extras in the tracked file

Result: dependency extras are not intact on current `main`.

## 8. Constraints status

Constraints files are still present under `requirements/`, including:

- `constraints-qiskit-aer.txt`
- `constraints-qiskit-finance.txt`
- `constraints-qiskit-optimization.txt`
- `constraints-qiskit-machine-learning.txt`
- `constraints-qiskit-nature.txt`
- `constraints-qiskit-algorithms.txt`
- `constraints-qiskit-dynamics.txt`
- `constraints-qiskit-experiments.txt`
- `constraints-qiskit-runtime.txt`
- `constraints-qiskit-metal.txt`
- `constraints-qiskit-addons.txt`
- `constraints-pennylane-full.txt`

Result: constraints remain present.

## 9. CI matrix completeness

The tracked GitHub Actions workflow still contains the major Stage 7 ecosystem
profiles and the later Stage 6/P2 profiles.

Observed profiles include:

- `qiskit-aer-extra`
- `qiskit-finance-extra`
- `qiskit-optimization-extra`
- `qiskit-machine-learning-extra`
- `pennylane-full-extra`
- `qiskit-nature-extra`
- `qiskit-algorithms-extra`
- `qiskit-dynamics-extra`
- `qiskit-metal-extra`
- `ecosystem-inventory`
- `qiskit-runtime-extra`
- `qiskit-experiments-extra`
- `qiskit-addons-extra`
- `chemistry-core`
- `chemistry-extra`
- `qiskit-nature-p2-extra`
- `algorithms-extra`
- `openfermion-extra`

Result: the workflow matrix file is still structurally complete.

## 10. Scaffold warnings status

Scaffold warnings are present in multiple Stage 7 result adapters, including:

- `quantumbridge/compat/qiskit_finance/result_adapter.py`
- `quantumbridge/compat/qiskit_optimization/result_adapter.py`
- `quantumbridge/compat/qiskit_machine_learning/result_adapter.py`
- `quantumbridge/compat/qiskit_dynamics/result_adapter.py`
- `quantumbridge/compat/qiskit_experiments/result_adapter.py`
- `quantumbridge/compat/qiskit_metal/result_adapter.py`
- `quantumbridge/compat/qiskit_runtime/result_adapter.py`
- `quantumbridge/compat/qiskit_addons/result_adapter.py`

Result: scaffold warnings exist in the tracked codebase.

## 11. Metal advisory clarity

Metal advisory wording remains clear in the tracked repository.

Observed wording includes:

- Metal is advisory only
- Python 3.12 install failed / unresolved locally
- No chip fabrication claim
- No electromagnetic simulation validation claim

Result: Metal advisory wording remains clear.

## 12. Runtime offline-only clarity

Runtime wording remains clear in the tracked repository.

Observed wording includes:

- Runtime verification is offline-only
- No token storage
- No IBM Cloud or hardware contact
- No service emulation claim

Result: Runtime offline-only wording remains clear.

## 13. Unsupported claims review

README and review/legal docs still reject unsupported claims, including:

- no full replacement claim
- no full parity claim
- no production finance claim
- no production ML claim
- no production control-system claim
- no hardware calibration claim
- no chip fabrication claim

Result: unsupported positive claims are still rejected in the tracked docs.

## 14. Local test result

Command run:

```bash
pytest -q -rs
```

Result:

- failed during collection
- blocking error:
  - `tests/compat_qiskit_nature/test_chemistry_result_schema.py`
  - import file mismatch with `tests/chemistry/test_chemistry_result_schema.py`
- summary: `Interrupted: 1 error during collection`

Interpretation: current `main` does not pass the full local test run.

## 15. Coverage result

Command run:

```bash
pytest --cov=quantumbridge
```

Result:

- failed during collection with the same import-file-mismatch error
- no valid coverage percentage was produced because collection did not complete

Interpretation: coverage verification is blocked on the current `main`.

## 16. Local matrix result

Command run:

```bash
bash scripts/run_local_matrix.sh
```

Result:

- current tracked `scripts/run_local_matrix.sh` is empty
- command exits immediately and performs no matrix verification
- comparison against PR #2 commit `6ce01d3` shows the script previously contained the full local verification matrix

Interpretation: local matrix verification is currently broken on `main`.

## 17. GitHub Actions result

Remote GitHub Actions check for current `main` HEAD:

- workflow run id: `27113410261`
- workflow: `QuantumBridge Test Matrix`
- head sha: `6dfe9b7aa2685f450079e02e1cfffb17b0a23424`
- status: `completed`
- conclusion: `failure`

Observed failing jobs from check runs include:

- `qiskit-optimization-extra`
- `chemistry-extra`
- `qiskit-nature-p2-extra`
- `chemistry-core`

Result: latest `main` GitHub Actions run is not successful.

## 18. Mainline regression verdict

Mainline regression was found.

High-confidence regressions:

- `pyproject.toml` emptied on `main`
- `scripts/run_local_matrix.sh` emptied on `main`
- full local pytest broken by test collection conflict
- latest remote GitHub Actions run failed on `main`

Result: current `main` is not in a clean post-merge state.

## 19. Release-candidate review readiness

Current recommendation:

- do not enter `v0.3.0-ecosystem-alpha1` release candidate review yet

Reason:

- post-merge mainline verification failed
- mainline regression exists
- full pytest is red
- coverage run is blocked
- local matrix runner is empty
- latest remote GitHub Actions run failed

## 20. Conclusion

Stage 7 ecosystem coverage artifacts remain broadly present on `main`, and the
documentation still preserves the intended advisory / non-parity / offline-only
boundaries. However, the post-merge result is not healthy: PR #1, merged after
PR #2, appears to have reintroduced a stale tree state that emptied
`pyproject.toml` and `scripts/run_local_matrix.sh`. Those regressions, combined
with the full-test collection failure and a failing latest GitHub Actions run,
mean the main branch fails Stage 7.6 post-merge verification.

Final verdict: regression found; do not proceed to release-candidate review
until `main` is repaired and verification is rerun.
