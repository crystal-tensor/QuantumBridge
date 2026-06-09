# PennyLane-Qiskit Bridge Equivalence

This clean-room QuantumBridge example compares a Bell-state workflow through
both bridge directions:

- Qiskit circuit -> QuantumBridge IR -> PennyLane executable spec;
- PennyLane operation metadata -> QuantumBridge IR -> Qiskit circuit.

Run:

```bash
python3 examples/pennylane_qiskit_bridge_equivalence_quantumbridge.py
```

The result reports `equivalence_status`, statevector probabilities, sampled
counts, maximum probability delta, warnings, provenance, and explicit
no-cloud/no-token/no-hardware metadata.

Counts are sampled and therefore compared as statistical support. Exact
statevector probabilities use a documented tolerance.
