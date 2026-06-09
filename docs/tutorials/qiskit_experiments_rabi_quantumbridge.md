# Qiskit Experiments Rabi Workflow With QuantumBridge

This clean-room tutorial runs a deterministic educational offline Rabi workflow
implemented by QuantumBridge.

```bash
python3 examples/qiskit_experiments_rabi_quantumbridge.py
```

The example prints a `RabiExperimentResult` JSON payload, fitted frequency,
contrast, offset, pi-amplitude, SSE, RMSE, R-squared, warnings, provenance, and
explicit no-cloud/no-token/no-hardware flags.

This is not hardware calibration, production experiment analysis, or a full
Qiskit Experiments replacement.
