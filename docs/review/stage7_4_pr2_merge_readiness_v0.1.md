# Stage 7.4 PR #2 Merge Readiness v0.1

Status: not ready to merge
Date: 2026-06-06

## 1. PR URL

https://github.com/crystal-tensor/QuantumBridge/pull/2

## 2. Current Head Commit

Reviewed remote head: `5f4510075439940dd27e4b7ae14e5a2b83d6d0de`

Branch: `p2/ecosystem-full-coverage-planning`

Base: `main` at `b294f7a15d33ad9ff2ad774c5d1a75948b7e9ee4`

The PR is open and GitHub reports it as mergeable. It is based on the current
`main`, but does not contain PR #1. It must be rebased after PR #1 merges.

## 3. CI Status

Latest reviewed GitHub Actions run: `27054066563`, success.

All 17 ecosystem matrix jobs completed successfully. Advisory jobs remain
advisory and a green status does not convert an unavailable upstream runtime
into supported execution.

The final branch will include Stage 7.4 review documents and whitespace-only
cleanup, so one fresh remote matrix is required after the branch is rebased and
the final scope is pushed.

## 4. Stage 7.2 Verification Summary

- Local Python 3.12 test suite: 150 passed, 3 skipped.
- Local Python 3.12 coverage: 91%.
- Stage 7.4 rerun reproduced 150 passed, 3 skipped and 91% coverage.
- Local matrix completed; its default Python 3.9 lane reported 138 passed and
  15 optional-dependency skips.
- Isolated installed verification covers Qiskit Nature, Finance, Algorithms,
  Machine Learning, Optimization, Dynamics, Experiments, Aer, and PennyLane.

Coverage levels remain: Level 0 inventory, Level 1 installed passthrough smoke,
Level 2 selected QuantumBridge Result wrappers, no new Level 3 ecosystem-native
implementation, and no Level 4 production-equivalence claim.

## 5. Metal Status

Qiskit Metal is advisory only:

- local macOS/Python 3.12 installation failed on legacy build dependencies;
- CI installed `qiskit-metal==0.1.2` on Ubuntu/Python 3.11;
- the CI import then failed because the legacy PySide2/shiboken2 stack was
  incompatible with NumPy 2.4.6;
- inventory code attempted real imports and recorded `import-failed`;
- Metal tests validate the unavailable path and schema serialization.

Therefore the green job means compatibility-risk reporting worked. It does not
mean executable Metal, EM simulation, chip fabrication, or production design
support.

## 6. Unsupported Claims Review

README and Stage 7 documents explicitly reject full replacement, full parity,
official endorsement, production-grade ecosystem claims, IBM Runtime cloud
access, token storage, materials band-gap implementation, and chip fabrication
support. No prohibited affirmative claim was found.

## 7. Legal and Attribution Review

Required Stage 7 notices and ledgers are present:

- `THIRD_PARTY_NOTICES.md`
- `docs/migration/source_migration_ledger.md`
- `docs/legal/qiskit_ecosystem_attribution_v0.1.md`
- `docs/legal/pennylane_ecosystem_attribution_v0.1.md`
- `docs/legal/stage7_2_full_ecosystem_attribution_review.md`

No tracked third-party package tree, wheel, site-packages directory, virtual
environment, compiled package artifact, token, or credential was found.

## 8. PR #1 Ordering

PR #1 must merge first and the resulting `main` CI must be green. PR #1 and
PR #2 overlap in ten files:

- `.github/workflows/test-matrix.yml`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/legal/third_party_source_policy.md`
- `docs/migration/source_migration_ledger.md`
- `pyproject.toml`
- `quantumbridge/schema/__init__.py`
- `scripts/inventory_qiskit_algorithms_api.py`
- `scripts/inventory_qiskit_nature_api.py`
- `scripts/run_local_matrix.sh`

## 9. Rebase Requirement

After PR #1 merges, rebase PR #2 onto the new `main`. Resolve the ten
overlapping files deliberately, preserving dependency isolation, attribution,
schema exports, inventory behavior, and all matrix lanes. Then rerun local and
remote verification.

## 10. Merge Blockers

1. Merge PR #1 first and wait for green `main` CI.
2. Rebase PR #2 and review the overlapping files.
3. Update the PR #2 title/body from the stale Stage 7.0 description.
4. Split the 11 UI/OpenClaw planning documents into
   `p3/ui-product-planning`, or obtain explicit approval to retain them.
5. Commit and push the Stage 7.4 whitespace cleanup and review documents.
6. Obtain a fresh green CI result for the final rebased head.

The GitHub connector returned HTTP 403 and `gh` is not authenticated, so the
PR metadata update is an authenticated maintainer action.

## 11. Release Blockers

Do not publish `v0.3.0` or `v0.3.0-ecosystem-alpha1`. Release review still
requires a merged-commit CI result, final dependency/license review,
release-supported Python/OS policy, explicit Metal exclusion, and release
notes preserving every unsupported/experimental boundary.

## 12. Merge Recommendation

Do not merge PR #2 now.

After all blockers are resolved, prefer **squash merge** because the current
seven commits include implementation, review, and concurrent planning changes.
The final squash should contain only the approved Stage 7 ecosystem scope.

## 13. Conclusion

Stage 7 functionality and verification are healthy, but delivery ordering and
scope are not yet clean. PR #1 must land first. PR #2 then needs rebase,
metadata correction, UI/OpenClaw document separation, and a final full matrix.

## Required PR Metadata

Title:

`Stage 7 Full Ecosystem Function Coverage and Adapter Scaffolds`

Body:

```markdown
## Summary

This PR adds Stage 7 full ecosystem coverage planning, inventory generation, optional dependency adapters, and installed-environment smoke verification.

## Coverage model

- Level 0: public API inventory
- Level 1: upstream passthrough smoke
- Level 2: QuantumBridge Result schema wrappers
- Level 3: no new ecosystem-native implementation in this PR
- Level 4: production equivalence is not claimed

## Verified installed ecosystems

Installed verification completed for:
- Qiskit Nature
- Qiskit Finance
- Qiskit Algorithms
- Qiskit Machine Learning
- Qiskit Optimization
- Qiskit Dynamics
- Qiskit Experiments
- Qiskit Aer
- PennyLane

## Metal status

Qiskit Metal / Quantum Metal is advisory only.
Local Python 3.12 installation failed due to legacy build dependency issues.
CI records compatibility-path behavior and does not claim executable Metal, EM simulation, or chip fabrication support.

## Non-goals

This PR does not:
- vendor third-party source code
- claim full Qiskit replacement
- claim full PennyLane replacement
- claim production-grade chemistry, finance, ML, experiments, dynamics, or chip design
- access IBM Runtime cloud
- read or store tokens
- implement materials band-gap calculation
- provide real chip fabrication support

## Validation

- Stage 7.2 local tests: 150 passed, 3 skipped
- Coverage: 91%
- Latest GitHub Actions: success
- Local matrix: completed

## Merge order

This PR should be reviewed after PR #1 is merged and main CI is green.
```
