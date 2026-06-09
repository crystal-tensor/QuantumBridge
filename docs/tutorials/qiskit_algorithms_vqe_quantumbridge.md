# QuantumBridge Qiskit Algorithms VQE Tutorial

This tutorial shows the Stage 9C native VQE executable adapter. It is a
QuantumBridge-owned educational workflow, not copied from Qiskit documentation
or examples.

Run:

```bash
python3 examples/qiskit_algorithms_vqe_quantumbridge.py
```

The example:

- builds a small Pauli Hamiltonian;
- runs a deterministic QuantumBridge-native grid-search VQE;
- optionally runs a local upstream `qiskit-algorithms` VQE smoke path if the
  dependency is installed;
- prints JSON result schemas, warnings, and provenance.

The native path is not a production optimizer and does not access IBM Cloud,
tokens, or hardware.
