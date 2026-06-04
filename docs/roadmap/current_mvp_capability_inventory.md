# Current MVP Capability Inventory

Status: Stage 4 baseline  
Date: 2026-06-04  

## Existing QuantumBridge MVP capabilities

| Area | Current capability |
| --- | --- |
| Circuit | Create fixed-qubit circuits, add gates, measurements, bind parameters |
| Gates | X, Y, Z, H, RX, RY, RZ, CX, CZ |
| IR | Circuit to QuantumBridge IR |
| QASM | OpenQASM-style export subset |
| Device | StatevectorDevice |
| Sampler | ShotSampler |
| Results | statevector, probabilities, counts, expectation, metadata, dict serialization |
| Operators | PauliString and Hamiltonian in `quantumbridge.utils.math` |
| Gradient | parameter-shift helper |
| Algorithms | simple VQE and QAOA |
| Tests | 12 MVP behavior tests pass |

## Stage 4 gaps before P0 expansion

- No Qiskit adapter.
- No PennyLane adapter.
- No QASM import.
- No operators package.
- No SparsePauli-like operator.
- No DensityMatrix object.
- No primitives Sampler/Estimator layer.
- No provider/backend/job abstraction.
- No QNode-like wrapper or Tape.
- No finite-difference gradient.
- No NumPy/Torch/JAX interface modules.
- No basic templates.
- No migration ledger.

