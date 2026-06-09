# QuantumBridge SDK

QuantumBridge is an experimental quantum SDK. The current repository keeps the P1 release-candidate baseline intact while Stage 8 hardens optional ecosystem inventory, adapter contracts, and schema wrappers.

QuantumBridge is an independent project. It is not an official Qiskit, PennyLane, IBM, or Xanadu project, and it does not claim full feature parity or full replacement coverage.

## Current Status

- Experimental SDK.
- P1 release-candidate subset implementation.
- Apache-2.0 compliance route with attribution records.
- Qiskit and PennyLane support is provided through optional adapter / compatibility layers.
- Qiskit and PennyLane remain separate projects owned by their respective rightsholders.
- Wider ecosystem packages are optional dependencies only; QuantumBridge does not vendor third-party package source.

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

## Ecosystem Compatibility Status

Stage 7 planning defines function coverage by level:

- Level 0 Inventory: public API names are identified and written to a matrix; this does not mean runnable support.
- Level 1 Passthrough: when the upstream optional dependency is installed, QuantumBridge can retrieve or call selected upstream objects and wrap results with provenance.
- Level 2 Adapter: selected upstream objects convert into QuantumBridge schemas, such as Circuit, IR, Result, Hamiltonian, Problem, Job, or Backend.
- Level 3 Native subset: QuantumBridge implements an independent subset for core capabilities.
- Level 4 Production equivalent: not promised in this project stage.

Current Qiskit ecosystem status:

- Qiskit core: Level 0 inventory, Level 1 passthrough contract, and a reviewed Level 2 subset for basic circuits/results.
- Qiskit Aer: Level 0 inventory, Level 1 passthrough contract, and Level 2 result schema wrapper when installed.
- Qiskit Nature: Level 0 inventory, Level 1 passthrough contract, and Level 2 result schema wrappers when installed.
- Qiskit Algorithms: Level 0/1 inventory and passthrough, Level 2 result wrappers, and a Stage 9C Level 3 educational native executable subset for VQE, QAOA-compatible MaxCut, and Grover examples. Missing optional packages report unsupported metadata.
- Qiskit Finance: Level 0/1 inventory and passthrough, Level 2 result wrapper, and a Stage 9A Level 3 educational portfolio-optimization native subset for deterministic four-asset mean-variance examples. Missing optional packages report unsupported metadata.
- Qiskit Optimization: Level 0/1 inventory and passthrough, Level 2 result wrappers, and a Stage 9B Level 3 educational native `QuadraticProgram` subset for small binary optimization examples. Missing optional packages report unsupported metadata.
- Qiskit Machine Learning: Level 0 inventory and contract metadata; missing optional packages report unsupported metadata.
- Qiskit Dynamics, Experiments, Metal, Runtime, and Addons: advisory or offline-only contracts with explicit warnings.
- Qiskit Runtime remains offline-only: no IBM Cloud access, no token reads, no credential storage, and no job submission.
- Qiskit Metal remains advisory: no chip fabrication, external EM simulation, or layout signoff support is claimed.

Current PennyLane ecosystem status:

- Operations, measurements, QNode, devices, qchem, transforms, gradients, templates, resources, and plugin-adjacent APIs: Level 0 inventory and Level 1 scaffold when PennyLane is installed.
- Existing P1 PennyLane tape/observable support remains a small reviewed Level 2 subset.
- Full plugin ecosystem, Catalyst bridge, TensorFlow interface parity, and production qchem workflows are not implemented.

## Stage 7.2 Full Function Coverage

Stage 7.2 expands installed-environment verification and adapter schemas. It remains an ecosystem coverage project, not a full replacement for any upstream SDK.

| Ecosystem | Current coverage | Install extra | Status |
| --- | --- | --- | --- |
| Qiskit Nature | Level 0/1 plus ChemistryResult Level 2 wrapper | `.[qiskit-nature]` | Verified: 0.8.0 |
| Qiskit Finance | Level 0/1 plus FinanceResult Level 2 wrapper and Stage 9A educational portfolio native subset | `.[qiskit-finance]` | Verified: 0.4.1; not production finance |
| Qiskit Algorithms | Level 0/1 plus AlgorithmsResult Level 2 wrapper and Stage 9C educational native VQE/QAOA/Grover subset | `.[qiskit-algorithms]` | Verified: 0.4.0; native subset does not require upstream |
| Qiskit Machine Learning | Level 0/1 plus MLResult Level 2 wrapper | `.[qiskit-machine-learning]` | Verified: 0.9.0; not production ML |
| Qiskit Optimization | Level 0/1 plus OptimizationResult Level 2 wrapper and Stage 9B educational native QuadraticProgram subset | `.[qiskit-optimization]` | Verified: 0.7.0; native subset does not require upstream |
| Qiskit Dynamics | Level 0/1 plus DynamicsResult Level 2 wrapper | `.[qiskit-dynamics]` | Verified: 0.6.0; advisory |
| Qiskit Experiments | Level 0/1 plus ExperimentsResult Level 2 wrapper | `.[qiskit-experiments]` | Verified: 0.14.1; advisory and offline-only |
| Qiskit Metal | Level 0 inventory plus MetalDesignResult schema | `.[qiskit-metal]` | Install failed on Python 3.12; advisory/unsupported |
| Qiskit Aer | Level 0/1 plus AerResult Level 2 wrapper | `.[qiskit-aer]` | Verified: 0.17.2; no Aer parity claim |
| PennyLane full | Level 0/1 plus PennyLaneResult Level 2 wrapper | `.[pennylane-full]` | Verified: 0.42.3; no complete replacement claim |

Level 2 here means a QuantumBridge result-schema wrapper. It does not mean complete input conversion, behavioral parity, performance parity, or production equivalence.

Stage 9A adds `quantumbridge.compat.qiskit_finance.run_portfolio_optimization_native()` for a deterministic, educational four-asset mean-variance portfolio example and optional upstream calls through installed Qiskit Finance / Qiskit Optimization / Qiskit Algorithms packages. This is not investment advice, production portfolio optimization, real market-data support, or a complete Qiskit Finance replacement.

Stage 9B adds a Qiskit Optimization `QuadraticProgram` executable adapter:

- `quantumbridge.compat.qiskit_optimization.create_quadratic_program_native()`
- binary variables, linear/quadratic objectives, and linear constraints;
- deterministic brute-force exact solving for small educational problems;
- QUBO and Ising metadata generation;
- optional upstream exact passthrough when `qiskit-optimization` and `qiskit-algorithms` are installed.

This is not production optimization software, not a complete Qiskit Optimization replacement, and not an IBM or Qiskit endorsement.

Stage 9C adds Qiskit Algorithms executable adapters:

- `quantumbridge.compat.qiskit_algorithms.run_vqe_native()`
- `quantumbridge.compat.qiskit_algorithms.run_qaoa_native_maxcut()`
- `quantumbridge.compat.qiskit_algorithms.run_grover_native()`
- optional local upstream smoke paths through `run_vqe_upstream()`, `run_qaoa_upstream()`, and `run_grover_upstream()` when `qiskit-algorithms` is installed;
- `quantumbridge.schema.algorithms_results` result envelopes for native, upstream, and comparison results.

This is not production algorithm software, not a complete Qiskit Algorithms replacement, and not an IBM or Qiskit endorsement.

## IBM Quantum Ecosystem Clean-Room Parity

QuantumBridge's long-term ecosystem goal is clean-room functional parity for
the capability areas represented across IBM Quantum Ecosystem project listings:
project discovery, capability cataloging, optional adapters, executable
examples, result schemas, provenance, warnings, tests, and future Studio
visualization readiness.

This does not mean copying IBM's website, brand presentation, text, images,
icons, page layout, source code, or third-party project implementations.
Project names are used only to identify compatibility targets. The planning
baseline lives in `docs/roadmap/ibm_quantum_ecosystem_clean_room_parity_master_plan.md`.

## Stage 8D Qiskit Adapter Contract Hardening

Stage 8D adds a uniform contract across the Qiskit ecosystem lanes:

- capability metadata: `capability_level`, `production_ready`, `native_implementation`, and `upstream_required`;
- dependency and version reporting;
- generated public API inventory;
- public-object lookup, passthrough call/class helpers, result wrapping, schema conversion, warnings, provenance, unsupported metadata, and environment validation;
- Qiskit result schema envelopes for core, Aer, Nature, Algorithms, Finance, Optimization, Machine Learning, Dynamics, Experiments, Metal, Runtime, Addons, and conversions.

Generated Qiskit inventory snapshots live in `docs/compat/inventory/`, with summary matrices in `docs/compat/matrix/`. These snapshots are public-name inventories and do not copy upstream source or documentation prose.

Install one lane per environment:

```bash
python -m pip install -c requirements/constraints-qiskit-nature.txt -e '.[qiskit-nature]'
python -m pip install -c requirements/constraints-qiskit-algorithms.txt -e '.[qiskit-algorithms]'
python -m pip install -c requirements/constraints-qiskit-dynamics.txt -e '.[qiskit-dynamics]'
python -m pip install -c requirements/constraints-qiskit-metal.txt -e '.[qiskit-metal]'
```

Use `python scripts/verify_ecosystem_installed_envs.py` to create isolated temporary verification environments. Do not install every optional extra together. Qiskit Runtime verification is offline-only: QuantumBridge does not request tokens or contact IBM Cloud. Finance, chemistry, ML, Experiments, Dynamics, and Metal coverage is experimental and not production-grade. Metal coverage does not imply chip fabrication readiness or external electromagnetic solver validation.

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
- Full Qiskit Nature / Algorithms / Finance / Optimization / Machine Learning / Aer / Runtime / Experiments parity.
- Full OpenQASM grammar.
- Hardware cloud providers.
- Production Qiskit Aer/noise integration.
- Full transpiler and pass ecosystem.
- Full PennyLane plugin ecosystem.
- Production quantum chemistry, finance, optimization, or machine learning workflows.
- Materials band gap workflows.
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
python -m pip install -e '.[qiskit-core]'
python -m pip install -e '.[qiskit-aer]'
python -m pip install -e '.[qiskit-finance]'
python -m pip install -e '.[qiskit-optimization]'
python -m pip install -e '.[qiskit-machine-learning]'
python -m pip install -e '.[pennylane]'
python -m pip install -e '.[pennylane-full]'
python -m pip install -e '.[torch]'
python -m pip install -e '.[jax]'
python -m pip install -e '.[dev]'
```

Qiskit, Qiskit ecosystem packages, PennyLane, Torch, and JAX are optional dependencies. Tests that require unavailable optional packages should skip with an explicit reason or run only dependency-smoke checks.

Do not commit third-party package source trees, local `site-packages`, downloaded wheels, or vendored Qiskit / PennyLane / PySCF / OpenFermion / Quafu code into this repository.

### Ecosystem dependency lanes

Stage 7 uses separate optional dependency lanes. Do not assume all optional dependencies can coexist in one environment.

- `qiskit-core`: Qiskit core public API inventory and selected P1 adapters.
- `qiskit-aer`: optional Aer simulator/noise passthrough scaffold.
- `qiskit-finance`: optional finance application/data-provider/circuit inventory.
- `qiskit-optimization`: optional optimization inventory and passthrough scaffold.
- `qiskit-machine-learning`: optional QNN/kernel/classifier/Torch connector inventory.
- `pennylane-full`: optional PennyLane operations, measurements, QNode, devices, qchem, transforms, gradients, templates, resources, and plugin-adjacent inventory.
- `ecosystem-chemistry`: optional Qiskit Nature / Algorithms / PySCF / OpenFermion lane; not production chemistry.

If environment conflicts appear, use separate virtual environments such as `quantumbridge-ecosystem-qiskit`, `quantumbridge-chemistry`, and `quantumbridge-pennylane`. Materials band gap workflows are not implemented.

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

Ecosystem inventory scripts:

```bash
python scripts/inventory_qiskit_core_api.py
python scripts/inventory_qiskit_aer_api.py
python scripts/inventory_qiskit_finance_api.py
python scripts/inventory_qiskit_optimization_api.py
python scripts/inventory_qiskit_machine_learning_api.py
python scripts/inventory_pennylane_full_api.py
```

Suggested P1 RC tag name for a future explicit release action:

```text
v0.1.0-p1-rc1
```

Do not create or push the release tag until remote CI has run and the release is explicitly approved.

## Legal and Attribution

- Apache-2.0 plan: [docs/legal/apache2_compliance_plan.md](docs/legal/apache2_compliance_plan.md)
- Third-party source policy: [docs/legal/third_party_source_policy.md](docs/legal/third_party_source_policy.md)
- Qiskit ecosystem attribution: [docs/legal/qiskit_ecosystem_attribution_v0.1.md](docs/legal/qiskit_ecosystem_attribution_v0.1.md)
- PennyLane ecosystem attribution: [docs/legal/pennylane_ecosystem_attribution_v0.1.md](docs/legal/pennylane_ecosystem_attribution_v0.1.md)
- Third-party notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- Source migration ledger: [docs/migration/source_migration_ledger.md](docs/migration/source_migration_ledger.md)

Suggested public description:

> QuantumBridge is an independent quantum SDK that provides adapters and compatibility layers for common quantum computing workflows.
