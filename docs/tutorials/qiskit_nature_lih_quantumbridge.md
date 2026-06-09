# Qiskit Nature LiH With QuantumBridge

Status: Stage 9D educational executable slice

This tutorial shows the QuantumBridge-native LiH chemistry path. It is a small
educational exact-diagonalization workflow, not production quantum chemistry,
not molecular design software, and not a complete Qiskit Nature replacement.

Run:

```bash
python3 examples/qiskit_nature_lih_quantumbridge.py
```

The example:

- builds a minimal LiH molecular problem;
- constructs a small qubit Hamiltonian;
- diagonalizes it locally;
- prints a JSON chemistry result envelope;
- optionally runs a local upstream Qiskit Nature smoke path when installed;
- records warnings and provenance.

No IBM Runtime, cloud account, token, credential, or hardware access is used.
