# QuantumBridge Qiskit Algorithms QAOA Tutorial

This tutorial shows the Stage 9C QAOA-compatible MaxCut executable adapter. It
is a QuantumBridge-owned educational workflow, not copied from Qiskit
documentation or examples.

Run:

```bash
python3 examples/qiskit_algorithms_qaoa_quantumbridge.py
```

The example:

- builds a small MaxCut problem;
- runs a QuantumBridge-native exact verification path with QAOA-compatible
  metadata;
- optionally runs a local upstream `qiskit-algorithms` QAOA smoke path if the
  dependency is installed;
- prints JSON result schemas, warnings, and provenance.

The native path is not production QAOA and does not access IBM Cloud, tokens,
or hardware.
