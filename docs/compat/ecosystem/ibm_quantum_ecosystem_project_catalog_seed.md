# QuantumBridge Ecosystem Project Catalog Seed

Status: Stage 9F manual seed
Source mode: manually curated clean-room compatibility target list.

This seed uses project names only for compatibility identification. It does not
copy IBM Quantum Ecosystem card text, ordering rules, UI, descriptions, icons,
or branding.

| Project ID | Upstream name | Category | Proposed QuantumBridge adapter | Current status | Next action | Priority | Legal boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `torchquantum` | TorchQuantum | QML | `quantumbridge.compat.torchquantum` | planned | Inventory and QML bridge review. | P2 | Name only; no source copy. |
| `qiskit-machine-learning` | Qiskit Machine Learning | QML | `quantumbridge.compat.qiskit_machine_learning` | executable subset | Expand beyond Stage 9E educational quantum kernel / kernel classifier / QNN classifier workflows. | P1 | Optional dependency; no production ML or full replacement claim. |
| `qiskit-aer` | Qiskit Aer | simulator | `quantumbridge.compat.qiskit_aer` | executable subset | Expand beyond Stage 9F educational statevector / qasm counts / simple noise workflows. | P1 | Optional dependency; no Aer replacement claim. |
| `mitiq` | Mitiq | error mitigation | `quantumbridge.compat.mitiq` | planned | Stage 9H error mitigation adapter. | P1 | Name only; no source copy. |
| `qiskit-nature` | Qiskit Nature | chemistry | `quantumbridge.compat.qiskit_nature` | executable subset | Expand beyond educational H2 / LiH exact-diagonalization workflows. | P1 | Optional dependency; no production chemistry or materials claim. |
| `qiskit-finance` | Qiskit Finance | finance | `quantumbridge.compat.qiskit_finance` | executable subset | Expand beyond portfolio example. | P1 | Not investment advice; no finance parity claim. |
| `qiskit-optimization` | Qiskit Optimization | optimization | `quantumbridge.compat.qiskit_optimization` | executable subset | Connect QAOA-style solver helpers. | P1 | No production optimizer claim. |
| `pennylane-qiskit` | PennyLane-Qiskit | bridge | `quantumbridge.compat.pennylane_full.qiskit_bridge` | partial bridge | Stage 9I bidirectional bridge hardening. | P1 | Compatibility only; no endorsement. |
| `qiskit-ibm-runtime` | IBM Quantum Runtime client | runtime | `quantumbridge.compat.qiskit_runtime` | offline-only | Keep token/cloud-disabled advisory path. | P2 | No IBM Cloud access or token reads. |
| `mqt-qecc` | MQT QECC | error correction | `quantumbridge.compat.mqt_qecc` | planned | Stage 9K inventory and adapter review. | P2 | Name only; no source copy. |
| `qiskit-experiments` | Qiskit Experiments | experiments | `quantumbridge.compat.qiskit_experiments` | advisory/schema | Stage 9G offline executable smoke paths. | P2 | No lab workflow guarantee. |
| `qiskit-algorithms` | Qiskit Algorithms | algorithms | `quantumbridge.compat.qiskit_algorithms` | executable subset | Stage 9C VQE/QAOA/Grover slice. | P1 | Not full replacement or production parity. |
| `mqt-ddsim` | MQT DDSIM | simulator | `quantumbridge.compat.mqt_ddsim` | planned | Stage 9K simulator compatibility review. | P2 | Name only; no source copy. |
| `rasqberry` | RasQberry | education | `quantumbridge.compat.rasqberry` | planned | Stage 9N advisory educational hardware slice. | P3 | No hardware support claim. |
| `azure-quantum` | Azure Quantum | provider | `quantumbridge.compat.azure_quantum` | planned | Stage 9L advisory no-token provider slice. | P2 | No cloud access by default. |
| `benchpress` | Benchpress | benchmarking | `quantumbridge.compat.benchpress` | planned | Stage 9M benchmark metadata slice. | P2 | Name only; no source copy. |
| `mqt-qmap` | MQT QMAP | compilation | `quantumbridge.compat.mqt_qmap` | planned | Stage 9K compilation compatibility review. | P2 | Name only; no source copy. |
| `mqt-core` | MQT Core | compilation | `quantumbridge.compat.mqt_core` | planned | Stage 9K core compatibility review. | P2 | Name only; no source copy. |

## Stage 9D Executable Proof

The `qiskit-nature` catalog row now has a QuantumBridge-native Level 3
educational chemistry slice:

- H2 minimal molecular problem construction;
- LiH minimal molecular problem construction;
- deterministic qubit Hamiltonian construction;
- exact diagonalization with NumPy;
- serializable chemistry result envelopes with warnings and provenance;
- optional local upstream passthrough when Qiskit Nature and a local chemistry
  stack are installed.

The slice is not production chemistry, not molecular design software, not a
materials band-gap workflow, and not a full Qiskit Nature replacement.

## Stage 9E Executable Proof

The `qiskit-machine-learning` catalog row now has a QuantumBridge-native Level 3
educational QML slice:

- deterministic toy binary datasets;
- native angle feature maps backed by QuantumBridge circuits;
- state-fidelity quantum kernel matrices;
- nearest-kernel classifier execution;
- minimal QNN forward pass;
- deterministic QNN grid-search classifier execution;
- serializable ML result envelopes with warnings and provenance;
- optional local upstream `qiskit-machine-learning` runtime introspection when
  installed.

The slice is not production ML, not a high-risk decision system, and not a full
Qiskit Machine Learning replacement.

## Stage 9F Executable Proof

The `qiskit-aer` catalog row now has a QuantumBridge-native Level 3
educational simulator slice:

- deterministic small-circuit statevector execution;
- seeded qasm-style shot sampling;
- simple educational measurement bit-flip noise;
- QuantumBridge Circuit, QuantumBridge IR, IR dictionary, and basic Qiskit
  QuantumCircuit input normalization;
- serializable Aer result envelopes with warnings and provenance;
- optional local upstream `qiskit-aer` passthrough when installed.

The slice is not production simulator software, not Qiskit Aer noise-model
parity, and not a full Qiskit Aer replacement.
