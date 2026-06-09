# Qiskit Ecosystem Fusion Master Matrix v0.1

**Version**: v0.1  
**Date**: 2026-06-09  
**Status**: Stage 8D adapter contract matrix

## Capability Levels

| Level | Meaning |
| --- | --- |
| 0 | Inventory only. |
| 1 | Upstream passthrough. |
| 2 | QuantumBridge schema adapter. |
| 3 | QuantumBridge native subset. |
| 4 | Production equivalent; not promised. |

## Matrix

| Ecosystem | API group | Inventory status | Level 0 | Level 1 | Level 2 | Level 3 | Required adapter functions | Tests | Risk | Next stage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qiskit core | circuit / transpiler / primitives / quantum_info | Existing matrices present | Yes | Partial | Partial | Native core subset exists | dependency, version, inventory, object lookup, passthrough, wrap, schema, provenance, warnings | core + qiskit-extra | Medium | 8D |
| Qiskit Aer | simulator / noise | Existing matrices present | Yes | Partial | Partial | Stage 9F native statevector/qasm/noise educational subset | same contract plus executable Aer result schema | qiskit-aer-extra | Medium | 9F |
| Qiskit Nature | drivers / problems / mappers | Existing matrices present | Yes | Partial | Partial | Stage 9D native H2/LiH chemistry subset | same contract plus executable chemistry result schema | qiskit-nature-extra, chemistry | High | 9D |
| Qiskit Algorithms | VQE / QAOA / Grover / eigensolvers / optimizers | Existing matrices present | Yes | Partial | Partial | Stage 9C native VQE/QAOA/Grover subset | same contract plus executable algorithms result schema | qiskit-algorithms-extra, algorithms | Medium | 9C |
| Qiskit Finance | applications / data providers / uncertainty | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-finance-extra | High | 8D |
| Qiskit Optimization | quadratic program / converters / optimizers | Existing matrices present | Yes | Partial | Partial | No | same contract | qiskit-optimization-extra | High | 8D |
| Qiskit Machine Learning | QNN / kernels / classifiers / regressors | Existing matrices present | Yes | Partial | Partial | Stage 9E native quantum kernel / kernel classifier / QNN classifier subset | same contract plus executable ML result schema | qiskit-machine-learning-extra | High | 9E |
| Qiskit Dynamics | models / signals / solver / backend | Existing matrices present | Yes | Partial executable slice | Educational offline one-qubit dynamics plus optional upstream boundary | No | Z precession, Rabi drive, dephasing metadata; no production dynamics claim | qiskit-dynamics-extra | High | 9I |
| Qiskit Experiments | experiments / calibration / tomography / RB | Existing matrices present | Yes | Partial executable slice | Educational offline Rabi/T1/Ramsey plus optional upstream boundary | No | deterministic synthetic workflows; no hardware calibration claim | qiskit-experiments-extra | High | 9I |
| Qiskit Metal | design / components / renderers / simulation | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus chip-design disclaimer | qiskit-metal-extra | High | 8D |
| Qiskit Runtime | backend / job / result / runtime | Existing matrices present | Yes | Offline-only | Offline-only | No | same contract plus no-token policy | qiskit-runtime-extra | High | 8D |
| Qiskit Addons | sqd / mpf / aqc / obp | Existing matrices present | Yes | Advisory | Advisory | No | same contract plus addon warnings | qiskit-addons-extra | Medium | 8D |
| Mitiq | error mitigation | Manual Stage 9G catalog row | Yes | Optional passthrough metadata | ErrorMitigationResult wrapper | Stage 9G native ZNE/readout educational subset | dependency, upstream metadata, native ZNE/readout workflows, schema, provenance, warnings | compat_mitiq | Medium | 9G |
| PennyLane-Qiskit bridge | framework bridge | Manual Stage 9H catalog row | Yes | Optional upstream plugin metadata | PennyLaneQiskitBridgeResult wrapper | Stage 9H native bidirectional bridge educational subset | dependency, bridge conversion, executable proof, schema, provenance, warnings | compat_pennylane_qiskit | Medium | 9H |

## Stage 8D Inventory Snapshot

Generated inventory files live under `docs/compat/inventory/`. They are runtime
public-name snapshots and copy no upstream source.

| Ecosystem | Records | Level 0 | Level 1 | Level 2 | Level 3 | Unsupported | Advisory | Offline-only | Local dependency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Qiskit core | 311 | 311 | 0 | 0 | 0 | 0 | No | No | qiskit 2.4.1 |
| Qiskit Aer | 24 | 24 | 0 | 0 | 0 | 0 | No | No | qiskit-aer 0.17.2 |
| Qiskit Nature | 221 | 221 | 0 | 0 | 0 | 0 | No | No | qiskit-nature 0.8.0 |
| Qiskit Algorithms | 145 | 145 | 0 | 0 | 0 | 0 | No | No | qiskit-algorithms 0.4.0 |
| Qiskit Finance | 4 | 4 | 0 | 0 | 0 | 4 | No | No | not installed |
| Qiskit Optimization | 5 | 5 | 0 | 0 | 0 | 5 | No | No | not installed |
| Qiskit Machine Learning | 6 | 6 | 0 | 0 | 0 | 6 | No | No | not installed |
| Qiskit Dynamics | 6 | 6 | 0 | 0 | 0 | 6 | Yes | No | not installed |
| Qiskit Experiments | 4 | 4 | 0 | 0 | 0 | 4 | Yes | Yes | not installed |
| Qiskit Metal | 5 | 5 | 0 | 0 | 0 | 5 | Yes | No | not installed |
| Qiskit Runtime | 3 | 3 | 0 | 0 | 0 | 3 | Yes | Yes | not installed |
| Qiskit Addons | 4 | 4 | 0 | 0 | 0 | 4 | Yes | No | not installed |

## Required Function Checklist

Each row exposes or documents:

- `capability_level`;
- `production_ready`;
- `native_implementation`;
- `upstream_required`;
- `dependency_available`;
- `get_upstream_version`;
- `get_dependency_report`;
- `list_public_api_inventory`;
- `get_public_object`;
- `passthrough_class`;
- `passthrough_call`;
- `wrap_result`;
- `to_quantumbridge_schema`;
- `get_provenance`;
- `unsupported(reason)`;
- warnings;
- tests.

## Non-Goals

- No native replacement for Qiskit.
- No production-equivalence claim.
- No IBM Cloud access.
- No token reads or credential storage.
- No production finance, ML, optimization, chemistry, experiments, dynamics,
  or chip design claim.

## Stage 9B Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Qiskit Optimization | Minimal binary `QuadraticProgram` exact enumeration | Level 3 | Optional `qiskit-optimization` + `qiskit-algorithms` exact passthrough | No | Supports small educational binary problems, QUBO metadata, and Ising metadata. Not full parity. |

All other Qiskit Optimization APIs remain inventory, passthrough, or schema
coverage unless individually promoted by a later reviewed stage.

## Stage 9C Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Qiskit Algorithms | Minimal VQE, QAOA-compatible MaxCut, and Grover workflows | Level 3 | Optional local `qiskit-algorithms` passthrough smoke paths | No | Supports small educational workflows with result schemas, warnings, and provenance. Not full parity. |

This row is also the Algorithms slice for QuantumBridge's IBM Quantum Ecosystem
clean-room parity plan. It does not copy IBM website content, Qiskit source, or
third-party project source.

## Stage 9D Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Qiskit Nature | Minimal H2 and LiH molecular problems, qubit Hamiltonians, and exact diagonalization | Level 3 | Optional local `qiskit-nature` / PySCF smoke paths | No | Supports small educational workflows with chemistry result schemas, warnings, and provenance. Not full parity or production chemistry. |

This row is the Qiskit Nature slice for QuantumBridge's IBM Quantum Ecosystem
clean-room parity plan. It does not copy IBM website content, Qiskit Nature
source, PySCF source, OpenFermion source, or third-party project source.

## Stage 9E Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Qiskit Machine Learning | Native toy quantum kernel, kernel classifier, QNN forward, and QNN classifier | Level 3 | Optional local `qiskit-machine-learning` runtime introspection | No | Supports small educational QML workflows with ML result schemas, warnings, and provenance. Not full parity, production ML, or high-risk decision software. |

This row is the Qiskit Machine Learning slice for QuantumBridge's IBM Quantum
Ecosystem clean-room parity plan. It does not copy IBM website content, Qiskit
Machine Learning source, tutorial code, UI, branding, or third-party project
source.

## Stage 9F Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Qiskit Aer | Native statevector, qasm-style counts, and simple measurement bit-flip noise | Level 3 | Optional local `qiskit-aer` passthrough | No | Supports small educational simulator workflows with Aer result schemas, warnings, and provenance. Not full parity or production simulation. |

## Stage 9G Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| Mitiq | Native educational ZNE and readout mitigation | Level 3 | Optional local `mitiq` dependency metadata / passthrough boundary | No | Supports small simulated error-mitigation workflows with ErrorMitigationResult schemas, warnings, and provenance. Not full Mitiq parity, production error mitigation, or hardware calibration parity. |

This row is the Mitiq / error-mitigation slice for QuantumBridge's IBM Quantum
Ecosystem clean-room parity plan. It does not copy IBM website content, Mitiq
source, Qiskit source, tutorial code, UI, branding, or third-party project
source.

## Stage 9H Update

| Ecosystem | New executable subset | Native level | Upstream path | Production-ready | Notes |
| --- | --- | --- | --- | --- | --- |
| PennyLane-Qiskit bridge | Qiskit circuit to PennyLane spec, PennyLane operations/tape metadata to Qiskit circuit, and Bell equivalence proof | Level 3 | Optional local `pennylane-qiskit` metadata passthrough | No | Supports a basic educational gate subset with bridge result schemas, warnings, provenance, and no cloud/token/hardware access. Not full plugin parity. |

This row is the PennyLane-Qiskit bridge slice for QuantumBridge's IBM Quantum
Ecosystem clean-room parity plan. It does not copy IBM website content,
Qiskit source, PennyLane source, PennyLane-Qiskit source, tutorial code, UI,
branding, or third-party project source.
