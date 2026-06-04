# Stage 5.5 Repository Gate v0.1

Status: P1 release-candidate baseline review complete locally  
Date: 2026-06-04  
Recommended baseline label: `v0.1.0-p1-rc1`

QuantumBridge remains an experimental SDK. This gate does not approve full
Qiskit or PennyLane feature parity and does not approve a full replacement
claim for either project.

## 1. Repository Status

| Item | Status | Notes |
| --- | --- | --- |
| Git repository | Present | Initialized locally during Stage 5.5. |
| `.gitignore` | Present | Covers Python caches, coverage, build outputs, virtualenvs, and macOS metadata. |
| Root `LICENSE` | Present | Apache License 2.0 text copied from `LICENSES/Apache-2.0.txt`. |
| `NOTICE` | Present | Declares independence and optional compatibility layer boundaries. |
| `README.md` | Present | Updated to Stage 5.5 P1 RC baseline language. |
| `pyproject.toml` | Present | Package metadata checked and updated. |
| `THIRD_PARTY_NOTICES.md` | Present | Retained. |
| `LICENSES/` | Present | Apache, Qiskit, and PennyLane license records retained. |
| `.github/workflows/test-matrix.yml` | Present | Converted to a matrix job covering core, Qiskit extra, PennyLane extra, and dev. |
| `docs/review/` | Present | Stage review records retained and this gate added. |
| `docs/implementation/` | Present | Implementation reports retained. |
| `docs/roadmap/` | Present | P2 planning records retained and expanded. |
| `docs/legal/` | Present | Legal and trademark policy records retained. |
| `docs/migration/source_migration_ledger.md` | Present | Updated to Stage 5.5 status with no new upstream source migration. |

## 2. Git Status

- Initial state: not a git repository.
- Action taken: `git init`.
- Remote: none configured.
- Push/tag: not attempted.
- Commit: allowed after local gate completion if git identity permits.

## 3. CI Status

Local CI simulation was executed through `scripts/run_local_matrix.sh`.

Results:

| Profile | Result |
| --- | --- |
| core-only | `68 passed in 2.22s` |
| qiskit-extra | `5 passed in 0.28s` |
| pennylane-extra | `9 passed in 1.08s` |
| dev | `68 passed in 1.84s`, coverage also passed |

Remote GitHub Actions were not executed. Blockers:

- No GitHub remote configured.
- `gh` is installed but not authenticated.
- No Actions run URL is available.

## 4. Packaging Status

- `python3 -m pip install -e '.[dev]'`: passed.
- `/Library/Developer/CommandLineTools/usr/bin/python3 -m pip install -e '.[dev]'`: passed for the Python 3.9 environment used by bare `pytest`.
- `python3 -m pip wheel . --no-deps -w /tmp/quantumbridge_wheel_check`: passed.
- `python3 -m pip check`: passed.
- Package metadata version: `0.1.0rc1`.
- Suggested external RC label: `v0.1.0-p1-rc1`.

## 5. License Status

- Root `LICENSE`: present, Apache License 2.0.
- `NOTICE`: present.
- `THIRD_PARTY_NOTICES.md`: present.
- `LICENSES/Apache-2.0.txt`: present.
- `LICENSES/QISKIT_LICENSE.txt`: present.
- `LICENSES/PENNYLANE_LICENSE.txt`: present.
- No license or notice records were removed.

## 6. Attribution Status

The source migration ledger states that Stage 5.5 introduced no new upstream
source migration. Optional Qiskit and PennyLane interaction remains adapter/API
integration, not copied source.

## 7. README / Docs Consistency

README language is aligned with the current state:

- Experimental SDK.
- P1 release-candidate subset.
- Optional compatibility layers only.
- No full feature-parity claim.
- No official endorsement claim.

## 8. Current Blockers

Remote CI remains blocked until a GitHub remote is configured and `gh` is
authenticated. This is an infrastructure blocker, not a local test blocker.

## 9. Freeze Decision

Recommendation: P1 may be frozen locally as a release-candidate baseline after
the local commit is created. Public release or P2 entry should wait for remote
GitHub Actions matrix execution and human review of the RC docs.
