# Stage 4 P0 Implementation Plan

Status: Stage 4 draft  
Date: 2026-06-04  

This plan implements P0 features without copying upstream source code. Current Stage 4 implementation modes are Native Implementation, Adapter Integration, and Upstream Dependency. No Source Port with Attribution is planned for this P0 pass.

## P0 tasks

| Task | Module | Mode | Acceptance |
| --- | --- | --- | --- |
| Qiskit basic import | `quantumbridge.compat.qiskit_adapter` | Adapter Integration | H/CX/measure circuit imports to QuantumBridge Circuit |
| Qiskit basic export | `quantumbridge.compat.qiskit_adapter` | Adapter Integration | QuantumBridge Circuit exports to Qiskit QuantumCircuit |
| Qiskit IR roundtrip | `quantumbridge.compat.qiskit_adapter` | Adapter Integration | Qiskit -> QB -> IR -> Qiskit preserves basic ops |
| OpenQASM import | `quantumbridge.compat.qasm_adapter` | Native Implementation | Supported subset parses into Circuit |
| Pauli and Sparse operator | `quantumbridge.operators` | Native Implementation | PauliString and sparse operator expectation work |
| Statevector / DensityMatrix | `quantumbridge.information` | Native Implementation | State/probability/density matrix basics pass |
| Sampler / Estimator | `quantumbridge.primitives` | Native Implementation | counts and expectation results pass |
| Backend / Job / Provider | `quantumbridge.providers` | Native Implementation | backend run returns job/result |
| PennyLane QNode wrapper | `quantumbridge.qml.qnode` | Native + Adapter Integration | callable QNode returns expectation |
| Tape-like record | `quantumbridge.qml.tape` | Native Implementation | records operations and measurements |
| PennyLane observable bridge | `quantumbridge.compat.pennylane_adapter` | Adapter Integration | PauliZ observable bridge works |
| Finite difference | `quantumbridge.transforms.gradient_transforms` | Native Implementation | derivative matches analytic small case |
| NumPy/Torch/JAX interfaces | `quantumbridge.interfaces` | Adapter Integration | NumPy/Torch conversion works; JAX optional |
| Basic templates | `quantumbridge.qml.templates` | Native Implementation | angle embedding builds RY/RX/RZ circuits |
| Attribution ledger test | `docs/migration`, `THIRD_PARTY_NOTICES.md` | Governance | required rows and notices present |

## P0 not included

- Full Qiskit circuit support.
- Full PennyLane operation capture.
- Full OpenQASM grammar.
- Full transpiler/pass manager implementation.
- Source porting upstream code.
- Aer/noise integration.
- Quantum chemistry.

## Review gates

- All new files include Apache Stage 4 native or adapter headers.
- Optional upstream dependencies remain optional.
- Ledger and notices updated.
- Tests pass.

