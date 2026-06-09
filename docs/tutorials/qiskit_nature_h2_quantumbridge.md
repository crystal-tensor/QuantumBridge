# Qiskit Nature H2 With QuantumBridge

Status: Stage 9D educational executable slice

This tutorial shows the QuantumBridge-native H2 chemistry path. It is a small
educational exact-diagonalization workflow, not production quantum chemistry
and not a complete Qiskit Nature replacement.

Run:

```bash
python3 examples/qiskit_nature_h2_quantumbridge.py
```

The example:

- builds a minimal H2 molecular problem;
- constructs a small qubit Hamiltonian;
- diagonalizes it locally;
- prints a JSON chemistry result envelope;
- optionally runs a local upstream Qiskit Nature smoke path when installed;
- records warnings and provenance.

No IBM Runtime, cloud account, token, credential, or hardware access is used.
