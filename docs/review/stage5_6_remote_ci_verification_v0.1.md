# Stage 5.6 Remote CI Verification v0.1

Status: Remote CI verification preparation complete  
Date: 2026-06-04  
Remote repository: https://github.com/crystal-tensor/QuantumBridge

QuantumBridge remains an experimental P1 release-candidate subset. Stage 5.6
does not approve P2 work, full Qiskit feature parity, full PennyLane feature
parity, or a complete replacement claim for either project.

## 1. Current Remote Repository

- GitHub repository: `https://github.com/crystal-tensor/QuantumBridge`
- Local `origin`: `https://github.com/crystal-tensor/QuantumBridge`
- Release tag status: no tag should be created before remote CI passes.
- Release status: no GitHub release should be created at this stage.

## 2. Current P1 RC Status

- Local baseline commit: `41a8dd1 chore: freeze QuantumBridge P1 release candidate baseline`
- Suggested future tag after remote CI success: `v0.1.0-p1-rc1`
- Package version: `0.1.0rc1`
- Scope: P1 release-candidate baseline with native SDK subset and optional
  Qiskit/PennyLane compatibility adapters.

## 3. Local Test Result Summary

Latest Stage 5.6 local validation:

```text
pytest -q -rs
68 passed in 1.97s
```

Coverage result:

```text
pytest --cov=quantumbridge
68 passed in 2.53s
TOTAL 1310 statements, 160 missed, 88% coverage
```

`pytest-cov` is available in the local test environment.

## 4. GitHub Actions Workflow Check

Workflow file: `.github/workflows/test-matrix.yml`

Checked requirements:

| Requirement | Status | Evidence |
| --- | --- | --- |
| `on: push` | Pass | Workflow includes `push`. |
| `on: pull_request` | Pass | Workflow includes `pull_request`. |
| `core-only` matrix | Pass | Matrix includes `profile: core-only`. |
| `qiskit-extra` matrix | Pass | Matrix includes `profile: qiskit-extra`. |
| `pennylane-extra` matrix | Pass | Matrix includes `profile: pennylane-extra`. |
| `dev` matrix | Pass | Matrix includes `profile: dev`. |
| dev coverage | Pass | dev command runs `pytest --cov=quantumbridge`. |
| Qiskit extra install | Pass | qiskit profile runs `python -m pip install -e '.[qiskit]' pytest`. |
| PennyLane extra install | Pass | pennylane profile runs `python -m pip install -e '.[pennylane]' pytest`. |
| No P2 feature work | Pass | Workflow-only check; no new feature implementation. |

## 5. Required GitHub Page Confirmation

After pushing the current branch to `origin`, the user should open GitHub
Actions for the repository and confirm that the `QuantumBridge Test Matrix`
workflow completed successfully.

Required confirmation items:

- Workflow name is `QuantumBridge Test Matrix`.
- The run is attached to the intended commit.
- All four matrix profiles completed.
- No profile is green only because the intended adapter tests were skipped.
- The dev profile executed coverage.

## 6. Matrix Acceptance Standards

| Matrix profile | Acceptance standard |
| --- | --- |
| core-only | Installs the package without optional Qiskit/PennyLane extras and runs `pytest -q -rs`. |
| qiskit-extra | Installs `.[qiskit]` and passes the Qiskit adapter test subset. |
| pennylane-extra | Installs `.[pennylane]` and passes the PennyLane adapter and installed-environment tests. |
| dev | Installs `.[dev]`, passes the full test suite, and runs coverage. |

## 7. Failure Triage Guide

Dependency install failure:

- Check Python version, pip resolver output, and whether the failing dependency
  belongs to base, dev, qiskit, or pennylane extras.
- Do not move optional dependencies into the base package to hide an install
  failure.

Qiskit extra failure:

- Confirm `.[qiskit]` installed successfully.
- Confirm failures are in the adapter subset and not caused by unsupported
  full-parity expectations.
- Keep Qiskit support as an optional compatibility layer.

PennyLane extra failure:

- Confirm `.[pennylane]` installed successfully.
- Confirm `tests/compat/test_pennylane_installed_environment.py` ran rather
  than skipped.
- Check optional dependency resolver issues before changing adapter behavior.

Coverage failure:

- Confirm `pytest-cov` installed through the dev extra.
- Inspect whether failure is a tooling problem or a real test failure.
- Do not disable coverage in the dev matrix to force a green run.

Python version issue:

- The workflow currently uses Python 3.11.
- If an upstream optional dependency has a Python-version-specific issue,
  document the resolver output and adjust the supported matrix only through
  review.

## 8. Tag Permission

Do not create a tag yet.

Only after all four remote Actions matrix profiles pass, the recommended tag
commands are:

```bash
git tag -a v0.1.0-p1-rc1 -m "QuantumBridge P1 release candidate 1"
git push origin v0.1.0-p1-rc1
```

## 9. P2 Permission

Do not enter P2 yet.

P2 remains blocked until:

- remote Actions matrix passes
- the P1 RC review is accepted
- the P1 RC tag/release decision is made
- P2 issues are selected explicitly

## 10. Conclusion

Stage 5.6 is ready for remote CI verification. The next action is to push the
current branch to `origin` and inspect the GitHub Actions matrix result. If all
four matrix profiles pass, the project can proceed to P1 RC freeze/tag approval.
