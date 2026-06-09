# Qiskit Algorithms Compatibility Strategy

Qiskit Algorithms support combines optional upstream passthrough, schema
wrapping, and Stage 9C educational native executable workflows.

## Stage 9C Executable Slice

Stage 9C adds:

- native minimal VQE for small Pauli Hamiltonians;
- native minimal QAOA-compatible MaxCut workflow with exact verification;
- native minimal Grover marked-bitstring statevector workflow;
- optional local upstream passthrough smoke paths for VQE, QAOA, and Grover
  when `qiskit-algorithms` and compatible Qiskit primitives are installed;
- algorithm result schemas with warnings, provenance, unsupported reasons, and
  `production_ready = False`.

This is an IBM Quantum Ecosystem clean-room parity algorithms slice. It is not
a full Qiskit Algorithms replacement, not production algorithm software, not
an IBM or Qiskit endorsement, and does not access IBM Cloud, tokens, or real
hardware.
