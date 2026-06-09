# QuantumBridge Qiskit Algorithms Grover Tutorial

This tutorial shows the Stage 9C native Grover executable adapter. It is a
QuantumBridge-owned educational workflow, not copied from Qiskit documentation
or examples.

Run:

```bash
python3 examples/qiskit_algorithms_grover_quantumbridge.py
```

The example:

- defines a small marked-bitstring search problem;
- runs QuantumBridge-native statevector Grover simulation;
- optionally runs a local upstream `qiskit-algorithms` Grover smoke path if the
  dependency is installed;
- prints JSON result schemas, warnings, and provenance.

The native path is not full Grover parity and does not access IBM Cloud,
tokens, or hardware.
