# Qiskit Dynamics Single-Qubit Workflow With QuantumBridge

This clean-room tutorial runs deterministic educational offline single-qubit
dynamics workflows implemented by QuantumBridge.

```bash
python3 examples/qiskit_dynamics_single_qubit_quantumbridge.py
```

The example prints Z precession, Rabi drive, and dephasing metadata results,
including time series, expectation values, final states, warnings, provenance,
and explicit no-cloud/no-token/no-hardware flags.

These workflows are not production dynamics simulation software and do not
provide a full Lindblad solver or full Qiskit Dynamics replacement.
