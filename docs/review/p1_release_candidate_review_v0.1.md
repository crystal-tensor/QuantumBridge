# P1 Release Candidate Review v0.1

Status: Local P1 RC validation complete  
Date: 2026-06-04  
Suggested RC label: `v0.1.0-p1-rc1`

## 1. Current Version Status

- Package name: `quantumbridge-sdk`.
- Package version: `0.1.0rc1`.
- Release posture: experimental P1 release candidate.
- Compatibility posture: optional Qiskit and PennyLane adapter layers only.
- Public claim boundary: no full feature parity, no complete replacement claim,
  and no IBM, Qiskit, Xanadu, or PennyLane endorsement claim.

## 2. P1 Completed Capabilities

- Native circuit, operation, measurement, IR, result, device, gradient, and
  simple algorithm foundation.
- Statevector and sampler execution for the supported subset.
- Pauli/Hamiltonian and sparse operator basics.
- QASM subset import/export.
- Optional Qiskit basic circuit import/export and counts result adapter.
- Optional PennyLane observable/tape/executable bridge subset.
- QML-style QNode/Tape/template basics.
- Array interface helpers for NumPy, Torch, and JAX.
- Provider/backend/job lightweight abstractions.
- Compiler PassManager basics, depth/two-qubit analyses, simple cancellation,
  zero-rotation removal, and adjacent same-axis rotation merge.
- Basic noise channel objects and noise model metadata.
- Legal/attribution automation tests.

## 3. P1 Unfinished Capabilities

- Full Qiskit parity.
- Full PennyLane parity.
- Full OpenQASM grammar parser.
- Qiskit Aer execution adapter.
- Real noisy execution path.
- Production-grade transpiler/routing/layout/decomposition.
- Production visualization.
- Hardware/cloud provider integration.
- Stable public API guarantee.

## 4. Current Test Results

Standard test suite:

```text
pytest -q -rs
68 passed in 1.96s
```

Coverage:

```text
pytest --cov=quantumbridge
68 passed in 2.56s
TOTAL 1310 statements, 160 missed, 88% coverage
```

Local matrix:

```text
core-only: 68 passed in 2.22s
qiskit-extra: 5 passed in 0.28s
pennylane-extra: 9 passed in 1.08s
dev: 68 passed in 1.84s; coverage passed
```

## 5. GitHub Actions Status

`.github/workflows/test-matrix.yml` exists and uses a matrix with:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`

Remote Actions were not run because no remote is configured and `gh` is not
authenticated. A remote Actions run URL is therefore unavailable.

## 6. Optional Dependencies Status

- Qiskit: available in the local test environment; adapter subset passed.
- PennyLane: available in the local test environment; installed-environment
  adapter subset passed.
- Torch/JAX: optional interface tests passed under the available local setup.
- Core tests do not require optional packages as mandatory runtime dependencies.

## 7. PennyLane Installed-Environment Verification

PennyLane installed-environment tests passed locally:

```text
tests/compat/test_pennylane_installed_environment.py
tests/compat/test_pennylane_adapter_realistic.py
tests/qml/test_pennylane_observable_bridge.py
tests/qml/test_pennylane_qnode_basic.py
9 passed in 1.08s
```

## 8. Qiskit Installed-Environment Verification

Qiskit adapter tests passed locally:

```text
tests/compat/test_qiskit_adapter_realistic.py
tests/compat/test_qiskit_import_basic_circuit.py
tests/compat/test_qiskit_export_basic_circuit.py
tests/compat/test_qiskit_roundtrip_ir.py
5 passed in 0.28s
```

## 9. Coverage Status

Coverage is now available after installing the dev extra in the Python 3.9
environment used by bare `pytest`. Current total coverage is 88%.

Areas intentionally low or placeholder-like remain visible in coverage:

- compiler routing/layout/decomposition placeholder modules
- visualization placeholder modules
- simple transforms placeholders

These should not be promoted as production-ready.

## 10. Packaging Status

- Editable dev install passed.
- Wheel build passed.
- `pip check` passed.
- Root license metadata and package license metadata identify Apache-2.0.

## 11. Legal / Attribution Status

- Apache-2.0 license and notices are present.
- Qiskit and PennyLane license records are retained.
- Source migration ledger records no copied source and no Stage 5.5 upstream
  source migration.
- Public docs avoid endorsement and full-parity claims.

## 12. README Accuracy

README accurately states:

- experimental status
- P1 release-candidate subset
- optional compatibility layers
- unsupported full parity and replacement claims
- required legal and attribution records

## 13. Freeze Recommendation

Recommendation: freeze the local P1 RC baseline as `v0.1.0-p1-rc1` after local
commit creation.

Do not publish a release or create/push a remote tag until:

- GitHub remote is configured.
- `gh` or another CI access path is authenticated.
- GitHub Actions matrix has run successfully.
- Human review accepts this RC package.

## 14. P2 Recommendation

Do not enter P2 implementation yet.

P2 may begin only after the P1 RC baseline is frozen and remote CI evidence is
available.

## 15. P2 Preconditions

- Remote GitHub Actions matrix pass.
- Human acceptance of `stage5_5_repository_gate_v0.1.md`.
- Human acceptance of this P1 RC review.
- P2 issue selection and owner assignment.
- Legal/trademark review for any expanded adapter claims.
