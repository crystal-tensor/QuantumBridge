# Qiskit to PennyLane Bridge

This clean-room QuantumBridge example converts a basic Qiskit circuit into
QuantumBridge IR and a PennyLane executable spec, then runs the QuantumBridge
native simulator for proof.

Run:

```bash
python3 examples/pennylane_qiskit_qiskit_to_pennylane_quantumbridge.py
```

The example prints probabilities, qasm-style counts, warnings, provenance, and
explicit `cloud_access: False`, `token_read: False`, `hardware_access: False`,
and `full_plugin_parity_claim: False` metadata.

This is not a complete PennyLane-Qiskit plugin replacement and not full Qiskit
or PennyLane parity.
