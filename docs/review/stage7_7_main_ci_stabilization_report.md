# Stage 7.7 Main CI Stabilization Report

Date: 2026-06-09
Status: Complete

## Main HEAD

- Validated main HEAD: `2680ece1359c0923fe556f57b4f05864efd680bd`
- Commit title: `ci: fix qiskit-nature workflow lane`

Recent main history:

- `2680ece` ci: fix qiskit-nature workflow lane
- `89ab513` ci: restore main ecosystem matrix after PR merges
- `6dfe9b7` Stage 6.1/6.2 P2 Dual-Track Expansion: Core SDK + Chemistry/Algorithms Adapters (#1)
- `6ce01d3` Stage 7 Ecosystem Function Coverage Planning and Adapter Scaffolds (#2)

## Actions Status

- Latest verified main workflow: QuantumBridge Test Matrix run #45
- Run URL: `https://github.com/crystal-tensor/QuantumBridge/actions/runs/27114230357`
- Head commit: `2680ece1359c0923fe556f57b4f05864efd680bd`
- Result: success
- Jobs: 22 of 22 successful

`gh` was available locally but not authenticated, so `gh run list` could not be
used. The run was checked through the GitHub integration and local
reproduction.

Historical PR #1 runs on the merged pull request still show failed checks for
the old head `ffb827dd7f42285db143b5e55d28782e680760d5`. Those historical
checks cannot be made green by a later commit because the pull request was
already merged and closed. The PR #1 source branch was repaired separately, and
the latest source-branch workflow run succeeded, but mainline health is judged
from current `main`.

## Local Validation

Commands run on `main`:

```bash
pytest -q -rs
pytest --cov=quantumbridge
bash scripts/run_local_matrix.sh
```

Results:

- `pytest -q -rs`: 178 passed, 33 skipped, 6 warnings
- `pytest --cov=quantumbridge`: 178 passed, 33 skipped, 6 warnings
- Coverage: 86%
- Local matrix: completed successfully

The local matrix completed with expected optional-dependency skips where
optional ecosystems were not installed. Advisory lanes stayed advisory and did
not claim production support.

## Failure Reason

The mainline CI regression came from the PR #1 merge path:

1. `pyproject.toml` became an empty tracked file at the merged PR #1 head.
2. `scripts/run_local_matrix.sh` became an empty tracked file at the merged PR
   #1 head.
3. Full pytest collection also exposed a duplicate test-module basename between
   chemistry and qiskit-nature compatibility tests.
4. After the first restoration, the `qiskit-nature-extra` lane still failed
   because `PySCFDriver` required `pyscf`, but the `qiskit-nature` optional
   extra did not install it.

The detailed diagnosis is recorded in
`docs/review/stage7_7_main_ci_failure_diagnosis_v0.1.md`.

## Fix Content

The applied fixes were limited to mainline CI stabilization:

- Restored `pyproject.toml` packaging metadata, package discovery, and optional
  dependency extras.
- Restored `scripts/run_local_matrix.sh` with the Stage 7 ecosystem matrix and
  Stage 6 chemistry / algorithms lanes.
- Renamed the duplicate qiskit-nature chemistry result-schema test file to
  avoid pytest import collision.
- Added `pyscf` to the `qiskit-nature` extra so the non-advisory
  qiskit-nature workflow lane can run its installed-driver checks.

No new feature implementation was added in Stage 7.7. No tag or release was
created. No third-party source was vendored.

## Advisory Lanes

- Qiskit Metal remains advisory only and does not imply executable Metal, EM
  simulation, or chip fabrication support.
- Qiskit Runtime remains offline-only and does not access IBM Cloud, read
  tokens, or store credentials.
- Qiskit Addons remain inventory / advisory unless installed and verified.
- Scaffold adapters continue to emit warnings or capability metadata so they do
  not imply production-ready support.

Node.js 20 deprecation warnings from GitHub Actions dependencies were observed
in older runs. They are warnings, not the cause of the Stage 7.7 CI failure.

## Stage 8 Gate

QuantumBridge can enter Stage 8 after this Stage 7.7 gate.

Stage 8 should remain bounded to the documented coverage model:

- Level 0: public API inventory
- Level 1: upstream passthrough smoke
- Level 2: QuantumBridge Result schema wrappers
- No full Qiskit replacement claim
- No full PennyLane replacement claim
- No production parity claim
- No release or tag until explicitly authorized
