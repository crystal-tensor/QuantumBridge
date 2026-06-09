# Qiskit Machine Learning Quantum Kernel With QuantumBridge

This clean-room example runs the QuantumBridge-native educational quantum-kernel
slice. It does not copy Qiskit Machine Learning tutorial code and does not
claim full Qiskit Machine Learning parity.

```bash
python3 examples/qiskit_ml_quantum_kernel_quantumbridge.py
```

The native path creates a deterministic toy dataset, builds QuantumBridge angle
feature-map circuits, evaluates statevectors locally, and returns a
state-fidelity kernel matrix through `QuantumKernelResult`.

The optional upstream path only introspects local `qiskit-machine-learning`
objects when installed. Missing dependencies return unsupported metadata.

This workflow is not production ML, not a high-risk decision system, and does
not access cloud, tokens, or hardware.
