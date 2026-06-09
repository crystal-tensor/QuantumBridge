# PennyLane to Qiskit Bridge

This clean-room QuantumBridge example converts PennyLane-style operation
metadata into QuantumBridge IR and a Qiskit `QuantumCircuit`, then runs the
QuantumBridge native simulator for proof.

Run:

```bash
python3 examples/pennylane_qiskit_pennylane_to_qiskit_quantumbridge.py
```

The example prints probabilities, qasm-style counts, target Qiskit operations,
warnings, provenance, and explicit no-cloud/no-token/no-hardware metadata.

This is an educational basic-gate subset, not full PennyLane-Qiskit plugin
parity or production framework parity.
