# QuantumBridge SDK

QuantumBridge is an experimental quantum SDK. The current repository is in Stage 5.5 P1 release-candidate baseline: a small native core plus optional compatibility adapters for common Qiskit and PennyLane workflows.

QuantumBridge is an independent project. It is not an official Qiskit, PennyLane, IBM, or Xanadu project, and it does not claim full feature parity or full replacement coverage.

## Current Status

- Experimental SDK.
- P1 release-candidate subset implementation.
- Apache-2.0 compliance route with attribution records.
- Qiskit and PennyLane support is provided through optional adapter / compatibility layers.
- Qiskit and PennyLane remain separate projects owned by their respective rightsholders.

## Supported P0 Features

- Native circuit construction with X, Y, Z, H, RX, RY, RZ, CX, CZ.
- Statevector simulation.
- Shot sampling.
- Result serialization.
- PauliString, Hamiltonian, and SparsePauliOperator basics.
- Statevector and DensityMatrix information helpers.
- Sampler and Estimator primitives.
- Parameter-shift and finite-difference gradients.
- Simple VQE and QAOA.
- OpenQASM-style subset import/export.
- Qiskit basic circuit import/export and counts adapter when Qiskit is installed.
- PennyLane observable/tape/executable subset bridge when PennyLane is installed.
- NumPy/Torch/JAX array interface helpers, with Torch and JAX optional.
- Minimal QNode-like wrapper and QML templates.

## P1 Controlled Expansion

Stage 5 adds controlled P1 subset coverage:

- CI dependency matrix workflow.
- PennyLane installed-environment tests, skipped when the optional dependency is unavailable.
- OpenQASM 2.0 subset parser improvements: include handling, comments, multi-register flattening, barrier no-op, whole-register measurement.
- Additional gates: S, SDG, T, TDG, Phase, SWAP, experimental iSWAP, and basic CCX matrix path.
- Operator/Hamiltonian enhancements.
- Testable compiler PassManager basics.
- Basic noise channels and error model metadata.

## Not Supported Yet

- Full Qiskit feature parity.
- Full PennyLane feature parity.
- Full OpenQASM grammar.
- Hardware cloud providers.
- Qiskit Aer/noise integration.
- Full transpiler and pass ecosystem.
- Full PennyLane plugin ecosystem.
- Quantum chemistry.
- Production-grade visualization.
- Production release guarantees.

## Install

For local development:

```bash
python -m pip install -e .
```

Optional adapter extras:

```bash
python -m pip install -e '.[qiskit]'
python -m pip install -e '.[pennylane]'
python -m pip install -e '.[torch]'
python -m pip install -e '.[jax]'
python -m pip install -e '.[dev]'
```

Qiskit, PennyLane, Torch, and JAX are optional dependencies. Tests that require unavailable optional packages should skip with an explicit reason.

## Test

Run:

```bash
pytest -q
```

Run with skip reasons:

```bash
pytest -q -rs
```

In the current P1 hardening environment after installing the PennyLane extra, the acceptance run is:

```text
68 passed
```

Core-only style tests:

```bash
pytest -q -rs tests/information tests/operators tests/primitives tests/compiler tests/noise tests/qml/test_qml_gradient_extended.py
```

Qiskit extra tests:

```bash
pytest -q -rs tests/compat/test_qiskit_adapter_realistic.py tests/compat/test_qiskit_import_basic_circuit.py tests/compat/test_qiskit_export_basic_circuit.py tests/compat/test_qiskit_roundtrip_ir.py
```

PennyLane extra tests:

```bash
pytest -q -rs tests/compat/test_pennylane_installed_environment.py tests/compat/test_pennylane_adapter_realistic.py tests/qml/test_pennylane_observable_bridge.py tests/qml/test_pennylane_qnode_basic.py
```

Coverage:

```bash
pytest --cov=quantumbridge
```

Only run coverage if `pytest-cov` is installed. In the Stage 5.5 local gate, the dev extra installed `pytest-cov` successfully and coverage passed.

Local matrix simulation:

```bash
bash scripts/run_local_matrix.sh
```

Suggested P1 RC tag name for a future explicit release action:

```text
v0.1.0-p1-rc1
```

Do not create or push the release tag until remote CI has run and the release is explicitly approved.

## Legal and Attribution

- Apache-2.0 plan: [docs/legal/apache2_compliance_plan.md](/Users/avalok/work/QuantumBridge/docs/legal/apache2_compliance_plan.md)
- Third-party source policy: [docs/legal/third_party_source_policy.md](/Users/avalok/work/QuantumBridge/docs/legal/third_party_source_policy.md)
- Third-party notices: [THIRD_PARTY_NOTICES.md](/Users/avalok/work/QuantumBridge/THIRD_PARTY_NOTICES.md)
- Source migration ledger: [docs/migration/source_migration_ledger.md](/Users/avalok/work/QuantumBridge/docs/migration/source_migration_ledger.md)

Suggested public description:

> QuantumBridge is an independent quantum SDK that provides adapters and compatibility layers for common quantum computing workflows.
