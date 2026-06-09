# Qiskit Experiments T1 And Ramsey Workflows With QuantumBridge

This clean-room tutorial runs deterministic educational offline T1 and Ramsey
workflows implemented by QuantumBridge.

```bash
python3 examples/qiskit_experiments_t1_ramsey_quantumbridge.py
```

The example prints `T1ExperimentResult` and `RamseyExperimentResult` JSON
payloads, positive T1-like metadata, finite detuning and T2-star-like Ramsey
metadata, warnings, provenance, and explicit no-cloud/no-token/no-hardware
flags.

These workflows use synthetic data and educational fitting only. They are not
hardware experiment results.
