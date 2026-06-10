# QuantumBridge SDK

Clean-room ecosystem parity for experimental quantum workflows.

QuantumBridge is an experimental quantum SDK. The current repository keeps the P1 release-candidate baseline intact while Stage 9 promotes selected ecosystem lanes from inventory/schema coverage to bounded executable slices.

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
- Qiskit Aer: Level 0/1 inventory and passthrough, Level 2 result wrapper, and a Stage 9F Level 3 educational native simulator subset for small statevector, qasm-style counts, and simple sampling-noise examples. Missing optional packages report unsupported metadata.
- Qiskit Nature: Level 0 inventory, Level 1 passthrough contract, Level 2 result schema wrappers, and a Stage 9D Level 3 educational native executable H2 / LiH chemistry subset. Missing optional packages report unsupported metadata.
- Qiskit Algorithms: Level 0/1 inventory and passthrough, Level 2 result wrappers, and a Stage 9C Level 3 educational native executable subset for VQE, QAOA-compatible MaxCut, and Grover examples. Missing optional packages report unsupported metadata.
- Qiskit Finance: Level 0/1 inventory and passthrough, Level 2 result wrapper, and a Stage 9A Level 3 educational portfolio-optimization native subset for deterministic four-asset mean-variance examples. Missing optional packages report unsupported metadata.
- Qiskit Optimization: Level 0/1 inventory and passthrough, Level 2 result wrappers, and a Stage 9B Level 3 educational native `QuadraticProgram` subset for small binary optimization examples. Missing optional packages report unsupported metadata.
- Qiskit Machine Learning: Level 0 inventory and contract metadata; missing optional packages report unsupported metadata.
- Qiskit Dynamics, Experiments, Metal, Runtime, and Addons: advisory or offline-only contracts with explicit warnings.
- Qiskit Runtime remains offline-only: no IBM Cloud access, no token reads, no credential storage, and no job submission.
- Qiskit Metal remains advisory: no chip fabrication, external EM simulation, or layout signoff support is claimed.
- Mitiq / error mitigation: Stage 9G Level 3 educational native zero-noise extrapolation and readout mitigation, plus optional upstream Mitiq dependency metadata when installed. This is not production error mitigation and not a complete Mitiq replacement.
- PennyLane-Qiskit bridge: Stage 9H Level 3 educational native bidirectional bridge for a basic-gate subset, including Qiskit circuit to PennyLane executable spec, PennyLane operation/tape metadata to Qiskit circuit, and Bell-state equivalence proof. This is not a full PennyLane-Qiskit plugin replacement and not full Qiskit or PennyLane parity.
- MQT Core / DDSIM / QMAP compatibility: Stage 9J Level 3 educational native circuit/IR compatibility, DDSIM-like small-circuit simulation, decision-diagram-inspired metadata, and QMAP-like topology routing with SWAP insertion. This is not a full MQT replacement, not decision-diagram parity, and not production compiler/simulator/mapper parity.
- TorchQuantum / PyTorch-style QML compatibility: Stage 9K Level 3 educational native quantum layer, tensor/batch forward, deterministic toy classifier training, optional torch tensor path, and optional upstream TorchQuantum boundary. This is not a full TorchQuantum or PyTorch replacement, not production QML, and not for high-risk automated decisions.
- QOS-UQCI / Quafu backend compatibility: Stage 10A Level 3 offline job specs, clean-room payloads, mock backend execution, result schemas, and optional upstream package boundaries. This is not production runtime or real hardware execution and does not access cloud services or tokens.
- Benchpress / Benchmarking compatibility: Stage 10B Level 3 clean-room local benchmark registry, runner, default suites, JSON / Markdown reports, and optional upstream Benchpress boundary. This is not official Benchpress output, not a full Benchpress replacement, and not production performance ranking.
- QuantumBridge Studio backend API: Stage 10C local service layer for catalog, workflow registry, input schema, execution, result store, export, benchmark, warnings/provenance, and REST-like local router. This is not a frontend UI, not a production API server, and does not access cloud services, tokens, or hardware.
- QuantumBridge Studio frontend prototype: Stage 10D static local prototype for catalog, workflow registry, workflow detail, mock local execution, results, warnings, provenance, benchmarks, and exports over Stage 10C seed data. This is not a production UI, not a production API server, and does not access cloud services, tokens, or hardware.

Current PennyLane ecosystem status:

- Operations, measurements, QNode, devices, qchem, transforms, gradients, templates, resources, and plugin-adjacent APIs: Level 0 inventory and Level 1 scaffold when PennyLane is installed.
- Existing P1 PennyLane tape/observable support remains a small reviewed Level 2 subset.
- PennyLane-Qiskit bridge: Stage 9H Level 3 educational bidirectional executable slice for H/X/Y/Z/RX/RY/RZ/Phase/CNOT/CZ/SWAP-style workflows, result schemas, warnings, provenance, and optional upstream plugin metadata.
- Full plugin ecosystem, Catalyst bridge, TensorFlow interface parity, and production qchem workflows are not implemented.

## Stage 7.2 Full Function Coverage

Stage 7.2 expands installed-environment verification and adapter schemas. It remains an ecosystem coverage project, not a full replacement for any upstream SDK.

| Ecosystem | Current coverage | Install extra | Status |
| --- | --- | --- | --- |
| Qiskit Nature | Level 0/1 plus ChemistryResult Level 2 wrapper and Stage 9D educational native H2 / LiH exact-diagonalization subset | `.[qiskit-nature]` | Verified: 0.8.0; native subset does not require upstream |
| Qiskit Finance | Level 0/1 plus FinanceResult Level 2 wrapper and Stage 9A educational portfolio native subset | `.[qiskit-finance]` | Verified: 0.4.1; not production finance |
| Qiskit Algorithms | Level 0/1 plus AlgorithmsResult Level 2 wrapper and Stage 9C educational native VQE/QAOA/Grover subset | `.[qiskit-algorithms]` | Verified: 0.4.0; native subset does not require upstream |
| Qiskit Machine Learning | Level 0/1 plus MLResult Level 2 wrapper and Stage 9E educational native quantum kernel / kernel classifier / QNN classifier subset | `.[qiskit-machine-learning]` | Verified: 0.9.0; native subset does not require upstream; not production ML |
| Qiskit Optimization | Level 0/1 plus OptimizationResult Level 2 wrapper and Stage 9B educational native QuadraticProgram subset | `.[qiskit-optimization]` | Verified: 0.7.0; native subset does not require upstream |
| Qiskit Dynamics | Level 3 educational offline one-qubit dynamics plus optional upstream boundary | `.[qiskit-dynamics]` | Z precession, Rabi drive, dephasing metadata; not production dynamics |
| Qiskit Experiments | Level 3 educational offline experiments plus optional upstream boundary | `.[qiskit-experiments]` | Rabi, T1, Ramsey synthetic workflows; not hardware calibration |
| Qiskit Metal | Level 0 inventory plus MetalDesignResult schema | `.[qiskit-metal]` | Install failed on Python 3.12; advisory/unsupported |
| Qiskit Aer | Level 0/1 plus AerResult Level 2 wrapper and Stage 9F educational native statevector / qasm counts / simple noise subset | `.[qiskit-aer]` | Verified: 0.17.2; native subset does not require upstream; no Aer parity claim |
| Mitiq / error mitigation | Stage 9G educational native ZNE and readout mitigation plus optional upstream Mitiq passthrough metadata | install upstream `mitiq` separately if needed | Native subset does not require upstream; not production error mitigation; no hardware calibration parity |
| PennyLane-Qiskit bridge | Stage 9H educational native bidirectional bridge and Bell equivalence proof plus optional upstream plugin metadata | install upstream `pennylane-qiskit` separately if needed | Native subset does not require upstream; not full plugin parity; no cloud/token/hardware |
| MQT Core / DDSIM / QMAP | Stage 9J educational native MQT Core-like circuit dict/QASM subset, DDSIM-like statevector/counts, and QMAP-like routing | install upstream MQT packages separately if needed | Native subset does not require upstream; not full MQT replacement; no decision-diagram or optimal-mapper parity |
| TorchQuantum / PyTorch-style QML | Stage 9K educational native TorchQuantum-like layer, tensor/batch forward, and classifier training | torch is optional for tensor interop; TorchQuantum is optional for upstream boundary metadata | Native subset does not require TorchQuantum; not full TorchQuantum/PyTorch replacement; not production QML or high-risk ML |
| QOS-UQCI / Quafu backends | Stage 10A offline QOS-UQCI job spec, DeviceSpec / CalSet / Manifest, Quafu-compatible payload, and mock execution | QOS-UQCI and pyquafu are optional upstream boundaries | No production runtime, no cloud/token/hardware access, no official endorsement |
| Benchpress / Benchmarking | Stage 10B local benchmark registry, runner, default suites, and JSON / Markdown reports | Benchpress is optional for upstream boundary metadata | Not official Benchpress output, not production performance ranking, no cloud/token/hardware access |
| QuantumBridge Studio Backend API | Stage 10C local catalog, workflow, execution, result, export, benchmark, and local router services | No heavy dependency; optional FastAPI boundary only | Backend-only, no frontend UI, no production server, no cloud/token/hardware access |
| QuantumBridge Studio Frontend Prototype | Stage 10D static local UI over generated Stage 10C seed data | No Node dependency required | Prototype-only, no production UI, no server, no cloud/token/hardware access |
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

Stage 9D adds Qiskit Nature executable chemistry adapters:

- `quantumbridge.compat.qiskit_nature.run_h2_native()`
- `quantumbridge.compat.qiskit_nature.run_lih_native()`
- `quantumbridge.compat.qiskit_nature.build_h2_problem()`
- `quantumbridge.compat.qiskit_nature.build_lih_problem()`
- optional local upstream smoke paths through `run_h2_upstream_passthrough()` and `run_lih_upstream_passthrough()` when Qiskit Nature and its local chemistry stack are installed;
- `quantumbridge.schema.chemistry_results` result envelopes for molecular problems, qubit Hamiltonians, exact diagonalization, H2, LiH, upstream passthrough, and comparison results.

This is an educational exact-diagonalization chemistry slice, not production quantum chemistry, not a complete Qiskit Nature replacement, not a materials band-gap workflow, and not an IBM or Qiskit endorsement.

Stage 9E adds Qiskit Machine Learning executable educational adapters:

- `quantumbridge.compat.qiskit_machine_learning.run_quantum_kernel_native()`
- `quantumbridge.compat.qiskit_machine_learning.run_kernel_classifier_native()`
- `quantumbridge.compat.qiskit_machine_learning.run_qnn_classifier_native()`
- `quantumbridge.compat.qiskit_machine_learning.qnn_forward_native()`
- deterministic toy datasets, angle feature maps, state-fidelity kernel matrices, nearest-kernel classifier, and deterministic QNN grid-search classifier;
- optional local upstream introspection paths when `qiskit-machine-learning` is installed;
- `quantumbridge.schema.ml_results` result envelopes for native kernel, classifier, QNN, upstream passthrough, and comparison results.

This is an educational QML slice, not production machine learning, not a complete Qiskit Machine Learning replacement, not suitable for medical, financial, employment, identity, safety, or other high-risk automated decisions, and not an IBM or Qiskit endorsement.

Stage 9F adds Qiskit Aer-style executable educational simulator adapters:

- `quantumbridge.compat.qiskit_aer.run_statevector_simulator_native()`
- `quantumbridge.compat.qiskit_aer.run_qasm_simulator_native()`
- `quantumbridge.compat.qiskit_aer.run_noisy_qasm_simulator_native()`
- `quantumbridge.compat.qiskit_aer.execute_basic_circuit_native()`
- deterministic small-circuit statevectors, seeded qasm-style counts, and simple educational measurement bit-flip noise;
- optional local upstream passthrough paths when `qiskit-aer` is installed;
- `quantumbridge.schema.aer_results` result envelopes for native, noisy, upstream, and comparison results.

This is an educational simulator slice, not production simulator software, not a complete Qiskit Aer replacement, not Qiskit Aer noise-model parity, and not an IBM or Qiskit endorsement.

Stage 9G adds Mitiq-style executable educational error mitigation adapters:

- `quantumbridge.compat.mitiq.run_zne_native()`
- `quantumbridge.compat.mitiq.run_noisy_expectation_native()`
- `quantumbridge.compat.mitiq.linear_zero_noise_extrapolate()`
- `quantumbridge.compat.mitiq.run_readout_mitigation_native()`
- `quantumbridge.compat.mitiq.mitigate_readout_counts()`
- optional local upstream Mitiq dependency metadata when `mitiq` is installed;
- `quantumbridge.schema.error_mitigation_results` result envelopes for native ZNE, native readout mitigation, upstream passthrough, and comparison results.

This is an educational error mitigation slice, not production error mitigation, not a complete Mitiq replacement, not hardware calibration parity, and not an IBM, Qiskit, or Mitiq endorsement.

Stage 9H adds PennyLane-Qiskit bridge executable educational adapters:

- `quantumbridge.compat.pennylane_qiskit.run_qiskit_to_pennylane_bridge()`
- `quantumbridge.compat.pennylane_qiskit.run_pennylane_to_qiskit_bridge()`
- `quantumbridge.compat.pennylane_qiskit.run_bidirectional_bridge_equivalence()`
- Qiskit `QuantumCircuit` to QuantumBridge IR to PennyLane executable spec for a basic gate subset;
- PennyLane operation/tape/QNode metadata to QuantumBridge IR to Qiskit `QuantumCircuit`;
- Bell-state bidirectional equivalence proof over the native simulator;
- optional local upstream PennyLane-Qiskit plugin metadata when `pennylane-qiskit` is installed;
- `quantumbridge.schema.pennylane_qiskit_bridge_results` result envelopes for native bridge, upstream passthrough, IR summary, execution, and equivalence results.

This is an educational bridge slice, not a complete PennyLane-Qiskit plugin replacement, not full Qiskit or PennyLane parity, not production parity, and not an IBM, Qiskit, PennyLane, Xanadu, or PennyLane-Qiskit endorsement.

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

### Qiskit Experiments / Dynamics Offline Slices

Stage 9I adds executable educational offline workflows for:

- Rabi, T1, and Ramsey synthetic experiments with deterministic fitting metadata.
- Single-qubit Z precession, Rabi drive dynamics, and dephasing metadata simulation.
- Optional upstream `qiskit-experiments` and `qiskit-dynamics` passthrough wrappers when those packages are installed.

These paths do not access IBM Runtime, cloud services, tokens, or real hardware.
They are not hardware calibration, production experiment analysis, production
dynamics software, or full replacements for upstream projects.

### MQT Core / DDSIM / QMAP Compatibility Slice

Stage 9J adds clean-room educational workflows for:

- MQT Core-like circuit dictionaries, QuantumBridge IR roundtrip, and a small QASM subset artifact.
- DDSIM-like statevector and counts simulation for small circuits using QuantumBridge native simulation.
- Decision-diagram-inspired metadata such as support bitstrings, unique amplitude counts, and compression hints.
- QMAP-like line/ring/full/custom topology validation, greedy CNOT routing, SWAP insertion, mapping cost, and original-vs-mapped execution comparison.
- Optional upstream MQT dependency boundary helpers when local MQT packages are installed separately.

These paths do not access cloud services, tokens, or real hardware. They are
not full MQT Core, DDSIM, or QMAP replacements, not decision-diagram parity,
not optimal mapping software, and not production compiler/simulator/mapper
parity.

### TorchQuantum / PyTorch-style QML Compatibility Slice

Stage 9K adds clean-room educational TorchQuantum-like QML workflows:

- tensor-like adapters for Python lists, NumPy arrays, and optional torch tensors;
- native small-circuit quantum layer forward passes over QuantumBridge simulation;
- batch forward execution with probabilities, outputs, predictions, warnings, and provenance;
- deterministic toy classifier training with grid search and explicit high-risk ML warnings;
- optional upstream TorchQuantum passthrough boundary when installed separately.

This slice is not a full TorchQuantum replacement, not a full PyTorch
replacement, not production QML training, and not suitable for medical,
financial, employment, identity, safety, or other high-risk automated
decisions. It does not access cloud services, tokens, or real hardware.

### QOS-UQCI / Quafu Backend Compatibility Slice

Stage 10A adds clean-room offline backend execution workflows:

- QuantumBridge IR to QOS-UQCI clean-room IR and job spec;
- QOS-UQCI DeviceSpec, CalSet, Manifest, and OpenQASM compatibility artifact;
- QOS-UQCI offline mock runtime returning QuantumBridge result schemas;
- QuantumBridge IR to Quafu-compatible payload and job spec;
- Quafu offline mock backend returning QuantumBridge result schemas;
- optional QOS-UQCI and pyquafu upstream boundary metadata.

This slice is not production QOS runtime support, not production Quafu backend
support, not real hardware execution, and not official endorsement. It does not
read tokens or access cloud services by default.

### Benchpress / Benchmarking Compatibility Slice

Stage 10B adds clean-room local benchmark execution workflows:

- benchmark case registry and default local suites;
- basic circuit, simulator, algorithms, finance / optimization, chemistry,
  QML, mitigation, backend, and bridge benchmark cases;
- deterministic local runner with pass/fail metrics;
- JSON and Markdown report generation;
- optional upstream Benchpress boundary metadata.

This slice is not a full Benchpress replacement, not official benchmark output,
not a production performance ranking system, and does not access cloud services,
tokens, or real hardware.

### QuantumBridge Studio Backend API Slice

Stage 10C adds a local backend API executable slice for future QuantumBridge
Studio frontends:

- catalog API over QuantumBridge-owned ecosystem metadata;
- workflow registry and input schema API for executable slices;
- local execution service and in-memory result store;
- JSON, Markdown, Python snippet, and notebook-stub exports;
- benchmark service wrapping the Stage 10B local benchmark runner;
- REST-like local router without starting an HTTP server;
- optional FastAPI adapter boundary when FastAPI is installed separately.

This slice is backend-only. It is not a frontend UI, not a production API
server, not an official IBM / Qiskit / PennyLane / Benchpress service, and does
not access cloud services, tokens, credentials, or real hardware.

### QuantumBridge Studio Frontend Prototype

Stage 10D adds a static local frontend prototype under `studio/`:

- ecosystem catalog view;
- workflow registry view;
- workflow detail view with input/output schema;
- mock local execution panel;
- result JSON, warning, and provenance viewers;
- benchmark report panel;
- JSON, Markdown, Python snippet, and notebook-stub export display.

Generate local seed data and run the frontend smoke check:

```bash
python3 examples/studio_generate_frontend_seed_data_quantumbridge.py
node studio/scripts/smoke-check.mjs
```

The prototype uses generated Stage 10C seed data and does not start a server,
open ports, access cloud services, read credentials, access real hardware, copy
third-party UI/branding/prose, or claim production UI readiness.

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
- Full MQT Core / DDSIM / QMAP parity.
- Full TorchQuantum or PyTorch parity, production QML, or high-risk ML decision support.
- Production QOS runtime, production Quafu backend, real quantum cloud access,
  token handling, or real hardware execution.
- Full Benchpress replacement, official benchmark claims, or production
  performance ranking.
- QuantumBridge Studio production UI, production API server claims, cloud
  service execution, token handling, or real hardware execution.
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
python -m pip install -e '.[qiskit-nature]'
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
- `qiskit-aer`: optional Aer simulator/noise passthrough plus Stage 9F educational native statevector, qasm-counts, and simple sampling-noise slice.
- `mitiq`: no default extra; if installed separately, QuantumBridge records optional upstream Mitiq passthrough metadata while native Stage 9G ZNE/readout examples run without it.
- `pennylane-qiskit`: no default extra; if installed separately, QuantumBridge records optional upstream plugin metadata while native Stage 9H bridge examples run without it.
- `mqt`: no default extra; if installed separately, QuantumBridge records optional upstream MQT Core/DDSIM/QMAP passthrough metadata while native Stage 9J examples run without it.
- `torchquantum`: no default extra; if installed separately, QuantumBridge records optional upstream TorchQuantum passthrough metadata while native Stage 9K examples run without it. `torch` is optional for tensor interop only.
- `qos_uqci` / `quafu`: no default extra; if installed separately,
  QuantumBridge records optional upstream boundary metadata while Stage 10A
  native examples run offline without cloud, token, or hardware access.
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
