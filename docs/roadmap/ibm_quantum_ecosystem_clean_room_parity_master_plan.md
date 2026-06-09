# IBM Quantum Ecosystem Clean-Room Parity Master Plan

Status: Stage 9H planning baseline
Scope: QuantumBridge ecosystem parity, not IBM website replication.

## Goal

QuantumBridge aims to provide clean-room functional parity for the public
capability areas represented across IBM Quantum Ecosystem project listings.
That means project discovery, capability cataloging, optional adapters,
executable examples, result schemas, provenance, warnings, tests, and future
Studio visualization readiness.

QuantumBridge does not copy IBM's website, brand presentation, text, images,
icons, page layout, source code, or third-party project implementations.

## Legal And Brand Boundaries

- QuantumBridge is independent.
- Project names are used only to identify compatibility targets.
- Upstream packages remain owned by their maintainers.
- No IBM, Qiskit, PennyLane, Azure, MQT, Mitiq, TorchQuantum, or other upstream
  endorsement is implied.
- No upstream source, tests, documentation prose, website copy, wheels,
  dist-info, egg-info, site-packages trees, or virtual environments may be
  committed.
- Production parity must not be claimed unless separately tested, reviewed, and
  approved.

## Clean-Room Principles

1. Use public package names and APIs only for compatibility identification.
2. Implement QuantumBridge-owned schemas, adapters, and educational workflows.
3. Prefer optional upstream passthrough where installed and legally clean.
4. Provide unsupported reasons when a capability is not executable.
5. Record warnings and provenance for every workflow.
6. Keep cloud, token, and hardware access disabled by default.

## Catalog Schema

The catalog tracks:

- `project_id`;
- `display_name`;
- `upstream_name`;
- `upstream_homepage`;
- `upstream_repository`;
- `upstream_license`;
- `upstream_owner`;
- `category`;
- `tags`;
- `install_extra`;
- `package_name`;
- `dependency_available`;
- `adapter_module`;
- `capability_level`;
- `executable_workflows`;
- `examples`;
- `tests`;
- `docs`;
- `warnings`;
- `provenance`;
- `official_endorsement = False`;
- `clean_room_status`;
- `ui_ready`;
- `priority`;
- `notes`.

The schema lives in `quantumbridge/ecosystem/catalog.py` and the planning
contract lives in `docs/compat/ecosystem/ibm_quantum_ecosystem_project_catalog_schema.md`.

## Capability Slices

| Stage | Slice | Required proof |
| --- | --- | --- |
| Stage 9C | Qiskit Algorithms | Native VQE, QAOA, Grover plus upstream passthrough. |
| Stage 9D | Qiskit Nature | Native educational H2 / LiH exact-diagonalization workflows plus optional local upstream passthrough. |
| Stage 9E | Qiskit Machine Learning | Native educational quantum kernel, kernel classifier, QNN forward, QNN classifier, plus optional upstream introspection. |
| Stage 9F | Qiskit Aer | Statevector, qasm-style, and noise workflows. |
| Stage 9G | Mitiq | Native educational ZNE and readout-mitigation workflows plus optional upstream passthrough metadata. |
| Stage 9H | PennyLane-Qiskit | Native educational bidirectional bridge and Bell equivalence proof. |
| Stage 9I | Qiskit Experiments / Dynamics | Offline advisory executable workflows. |
| Stage 9J | TorchQuantum / QML | Exploratory QML bridge. |
| Stage 9K | MQT Core / DDSIM / QMAP / QECC | Compatibility slices. |
| Stage 9L | Azure Quantum | Advisory no-token/cloud compatibility slice. |
| Stage 9M | Benchpress | Benchmarking slice. |
| Stage 9N | RasQberry | Educational hardware advisory slice. |
| Stage 10A | Quafu / pyquafu | Executable backend adapter. |
| Stage 10B | QOS-UQCI | Offline job spec and mock runtime adapter. |
| Stage 11A | Studio backend | Catalog and executable workflow API. |
| Stage 11B | Studio frontend | Future UI prototype, separately authorized. |

Each slice must include executable proof, examples, tests, result schema,
warnings, provenance, unsupported reasons, no-vendor checks, no-endorsement
checks, and visualization readiness notes.

## Experience Strategy

QuantumBridge Studio should eventually provide an independent ecosystem
experience:

- project catalog;
- category filters;
- search;
- capability-level badges;
- install-extra badges;
- executable workflow badges;
- backend compatibility badges;
- warning and provenance panel;
- run example;
- export Python, notebook, JSON, or QASM where applicable;
- compare upstream and native paths;
- connect to Quafu and QOS-UQCI in future stages.

No IBM branding, IBM page structure, or copied UI should be used.

## Stage 9D Qiskit Nature Slice

Stage 9D promotes Qiskit Nature from inventory/schema coverage to a bounded
executable chemistry slice. The native path constructs QuantumBridge-owned H2
and LiH molecular problem metadata, maps each problem to a small educational
qubit Hamiltonian, diagonalizes that Hamiltonian locally, and emits chemistry
result envelopes with provenance, warnings, and unsupported metadata.

Optional upstream passthrough is allowed only when the relevant local Qiskit
Nature chemistry stack is installed. That path records the upstream package and
version and remains a passthrough comparison, not QuantumBridge-native
ownership of upstream behavior.

This slice deliberately excludes production quantum chemistry, molecular
design, materials band-gap calculations, IBM Runtime, cloud execution, token
handling, hardware access, and full Qiskit Nature parity.

## Stage 9E Qiskit Machine Learning Slice

Stage 9E promotes Qiskit Machine Learning from inventory/schema coverage to a
bounded executable educational QML slice. The native path creates
QuantumBridge-owned deterministic toy datasets, builds angle feature-map
circuits, computes state-fidelity quantum kernels, runs a nearest-kernel
classifier, runs a minimal QNN forward pass, and trains a deterministic
grid-search QNN classifier.

Optional upstream passthrough is allowed only when the local
`qiskit-machine-learning` stack is installed. That path uses runtime
introspection and clear unsupported reasons, not QuantumBridge ownership of
upstream behavior.

This slice deliberately excludes production ML, high-risk automated decisions,
training-performance guarantees, IBM Runtime, cloud execution, token handling,
hardware access, and full Qiskit Machine Learning parity.

## Stage 9F Qiskit Aer Slice

Stage 9F promotes Qiskit Aer-style simulator coverage to a bounded educational
native executable slice. The native path runs small statevector simulations,
seeded qasm-style counts, and simple measurement bit-flip sampling noise using
QuantumBridge-owned code and result schemas.

Optional upstream passthrough is allowed only when `qiskit-aer` is installed.
This slice deliberately excludes production simulator validation, Qiskit Aer
noise-model parity, IBM Runtime, cloud execution, token handling, hardware
access, and full Qiskit Aer parity.

## Stage 9G Mitiq Error-Mitigation Slice

Stage 9G promotes Mitiq / error mitigation from catalog planning to a bounded
educational executable slice. The native path connects Stage 9F simulator
counts to noisy expectation values, linear zero-noise extrapolation, and a
calibration-matrix readout-mitigation workflow.

Optional upstream Mitiq passthrough records dependency availability and
unsupported reasons unless the caller supplies the upstream execution context.
This slice deliberately excludes production error mitigation, statistical
parity with Mitiq, hardware calibration parity, IBM Runtime, cloud execution,
token handling, hardware access, and full Mitiq parity.

## Stage 9H PennyLane-Qiskit Bridge Slice

Stage 9H promotes PennyLane-Qiskit bridge coverage to a bounded educational
executable slice. The native path converts Qiskit circuits through
QuantumBridge IR into a PennyLane executable spec, converts PennyLane
operation/tape/QNode metadata through QuantumBridge IR into a Qiskit circuit,
and proves Bell-state equivalence through the QuantumBridge native simulator.

Optional upstream PennyLane-Qiskit passthrough records dependency availability
and provenance only. This stage excludes full plugin replacement, full Qiskit
or PennyLane parity, advanced device/transform/gradient parity, cloud
execution, token handling, hardware access, UI implementation, tags, releases,
and vendored third-party source.

## Release Gating

Do not tag or release based on catalog planning alone. A release candidate
requires passing local tests, local matrix, CI, legal ledger checks, and a
review that no upstream source or branded assets were copied.
