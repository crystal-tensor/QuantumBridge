# Qiskit Ecosystem Fusion Architecture v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8D adapter contract hardening

## 1. Position

QuantumBridge is not a Qiskit replacement. It provides optional dependency
adapters, inventory, passthrough, schema wrappers, warnings, and provenance for
selected Qiskit ecosystem packages.

No official IBM, Qiskit, or package maintainer endorsement is claimed.

## 2. Covered Ecosystems

| Package | Stage 8 role | Boundary |
| --- | --- | --- |
| Qiskit core | Circuit, transpiler, primitives, quantum_info, result bridge. | Optional dependency, no complete parity claim. |
| Qiskit Aer | Simulator and noise model adapter path. | Not production-equivalent simulation validation. |
| Qiskit Nature | Chemistry problem, driver, mapping, result bridge. | Optional chemistry lane, not production chemistry. |
| Qiskit Algorithms | VQE, QAOA, eigensolver, optimizer bridge. | Optional algorithms lane, not full algorithm parity. |
| Qiskit Finance | Portfolio/data-provider result wrappers. | Not production finance or trading. |
| Qiskit Optimization | Quadratic program and optimizer bridge. | Not production optimization. |
| Qiskit Machine Learning | Stage 9E native educational quantum kernel, kernel classifier, QNN forward, QNN classifier, plus optional passthrough introspection. | Not production ML or high-risk decision software. |
| Qiskit Dynamics | Advisory dynamics model/solver bridge. | Not lab-grade dynamics validation. |
| Qiskit Experiments | Advisory experiment/calibration inventory. | Not calibration or lab operations support. |
| Qiskit Metal | Advisory design inventory. | Not chip fabrication, EM simulation, or layout signoff. |
| Qiskit IBM Runtime | Offline-only runtime metadata planning. | No IBM Cloud access, token reads, or credential storage. |
| Qiskit Addons | Inventory/advisory unless installed and verified. | No production addon support claim. |
| Mitiq / error mitigation | Stage 9G native educational ZNE and readout-mitigation workflows plus optional upstream Mitiq metadata. | Not production error mitigation, not hardware calibration parity, not full Mitiq replacement. |

## 3. Adapter Contract per Ecosystem

Every Qiskit ecosystem adapter now converges on this surface:

1. `capability_level`;
2. `production_ready`;
3. `native_implementation`;
4. `upstream_required`;
5. `dependency_available`;
6. `get_upstream_version`;
7. `get_dependency_report`;
8. `list_public_api_inventory`;
9. `get_public_object`;
10. `passthrough_call`;
11. `passthrough_class`;
12. `wrap_result`;
13. `to_quantumbridge_schema`;
14. `get_warnings`;
15. `get_provenance`;
16. `unsupported(reason)`;
17. `validate_environment`.

## 4. Data Flow

```text
User code
  -> QuantumBridge adapter
  -> optional Qiskit ecosystem dependency
  -> upstream object/result
  -> QuantumBridge result/schema wrapper
  -> provenance + warnings
```

## 5. Runtime and Credential Policy

Qiskit Runtime support is offline-only in this stage.

- Do not access IBM Cloud.
- Do not read tokens.
- Do not write credentials.
- Do not infer account status.
- Do not claim runtime execution support.

Future runtime work must introduce an explicit security review and token
handling policy before any cloud path is enabled.

## 6. Domain Boundaries

Finance, optimization, chemistry, machine learning, experiments, dynamics, and
chip design remain adapter/scaffold/advisory domains unless a later reviewed
stage proves a narrower production-quality subset. Documentation and warnings
must make this clear.

## 7. Tests

Required tests:

- dependency available/unavailable paths;
- import smoke;
- public API inventory smoke;
- passthrough object lookup;
- result wrapper schema validation;
- warnings and provenance;
- offline-only runtime behavior;
- advisory package `continue-on-error` behavior in workflow matrix where
  appropriate.

## 8. Stage 8D Implementation Snapshot

Stage 8D hardens the Qiskit ecosystem contract across core, Aer, Nature,
Algorithms, Finance, Optimization, Machine Learning, Dynamics, Experiments,
Metal, Runtime, and Addons.

The implementation uses a shared QuantumBridge facade for dependency checks,
public-object lookup, passthrough, schema wrapping, warnings, provenance, and
environment validation. The result envelope lives in
`quantumbridge.schema.qiskit_results` and records upstream package, upstream
version, capability level, mode, raw type, warnings, provenance, advisory
status, and offline-only status.

Runtime remains offline-only: no IBM Cloud access, no token reads, no token
storage, and no job submission. Metal remains advisory: no executable chip
design, EM simulation, layout signoff, or fabrication support is claimed.
Dynamics, Experiments, Runtime, Metal, and Addons expose advisory warnings where
appropriate. Missing optional packages report unsupported metadata instead of
pretending support exists.

Stage 8D does not introduce new Qiskit-native implementation. It strengthens the
adapter contract and generated inventory records so later conversion work can
start from explicit capability boundaries.

## 8.1 Stage 9G Error-Mitigation Architecture Note

Stage 9G adds an IBM Quantum Ecosystem-adjacent error-mitigation lane for
Mitiq-style workflows. The native path consumes QuantumBridge circuits,
delegates simulation to the Stage 9F educational Aer-style simulator, computes
noisy expectation values, applies simple zero-noise extrapolation, and emits
QuantumBridge error-mitigation result schemas.

The readout-mitigation path builds an educational calibration matrix, applies
simulated measurement bit-flip errors, inverts the calibration matrix with
numerical safeguards, and returns mitigated probabilities. It is not hardware
calibration, production mitigation, or Mitiq parity.

## 9. Stage 9B Optimization Executable Subset

Stage 9B adds the first bounded executable Qiskit Optimization workflow:

- QuantumBridge-native minimal binary `QuadraticProgram`;
- binary variables;
- linear and quadratic objectives;
- linear equality and inequality constraints;
- deterministic brute-force exact solving for small problems;
- QUBO and Ising metadata;
- optional upstream `qiskit-optimization` / `qiskit-algorithms` passthrough.

This stage moves Qiskit Optimization from inventory/schema-only status to a
reviewed Level 3 educational native subset for small binary optimization
examples. It does not claim full Qiskit Optimization parity, production
optimization, cloud execution, token handling, hardware access, or IBM/Qiskit
endorsement.

## 10. Stage 9D Nature Executable Chemistry Subset

Stage 9D adds a bounded Qiskit Nature executable lane:

- QuantumBridge-native H2 and LiH molecular problem metadata;
- deterministic small qubit Hamiltonians for educational exact diagonalization;
- local NumPy diagonalization with energy, eigenvalue, particle-count, mapper,
  basis, provenance, and warning metadata;
- optional local upstream Qiskit Nature smoke execution when installed;
- serializable chemistry schemas in `quantumbridge.schema.chemistry_results`;
- example scripts for H2 and LiH.

This stage moves Qiskit Nature beyond scaffold-only coverage for two small
educational molecules, but it does not claim complete Qiskit Nature parity,
production quantum chemistry, molecular design support, materials band-gap
support, cloud execution, token handling, hardware access, or IBM/Qiskit
endorsement.

## 11. Stage 9E Machine Learning Executable QML Subset

Stage 9E adds a bounded Qiskit Machine Learning lane:

- deterministic toy datasets without network access or real user data;
- QuantumBridge-native angle feature-map circuits;
- native state-fidelity quantum kernel matrices;
- native nearest-kernel classifier;
- native QNN forward pass;
- native deterministic QNN grid-search classifier;
- optional upstream `qiskit-machine-learning` runtime introspection.

This stage moves Qiskit Machine Learning beyond scaffold-only coverage for
small educational QML workflows, but it does not claim complete Qiskit Machine
Learning parity, production ML, high-risk decision suitability, training
performance, cloud execution, token handling, hardware access, UI
implementation, or IBM/Qiskit endorsement.

## 12. Stage 9H PennyLane-Qiskit Bridge

The Stage 9H bridge connects Qiskit and PennyLane through QuantumBridge-owned
IR and schemas. The Qiskit direction accepts a basic `QuantumCircuit` subset,
normalizes it to QuantumBridge IR, emits a PennyLane executable spec, and runs
the native simulator for proof. The PennyLane direction accepts operation,
tape, or QNode metadata, normalizes it to QuantumBridge IR, emits a Qiskit
`QuantumCircuit`, and compares Bell-state probabilities through the same native
execution path.

This bridge is intentionally bounded: it does not copy Qiskit, PennyLane, or
PennyLane-Qiskit source; it does not claim full framework or plugin parity; and
it does not access cloud services, tokens, or hardware.

## 13. Stage 9I Experiments / Dynamics Offline Slice

Stage 9I adds QuantumBridge-owned educational offline Rabi, T1, Ramsey, Z
precession, Rabi drive, and dephasing metadata workflows. The slice feeds
Result schemas for future Studio visualization, but it does not implement UI,
hardware calibration, IBM Runtime access, production experiment analysis, or
production dynamics simulation.
