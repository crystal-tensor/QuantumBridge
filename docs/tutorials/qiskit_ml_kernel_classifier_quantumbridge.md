# Qiskit Machine Learning Kernel Classifier With QuantumBridge

This clean-room example runs the QuantumBridge-native educational kernel
classifier slice.

```bash
python3 examples/qiskit_ml_kernel_classifier_quantumbridge.py
```

The native path creates a deterministic toy dataset, computes a native quantum
kernel, trains a nearest-kernel classifier, and returns predictions and accuracy
through `KernelClassifierResult`.

The optional upstream path only introspects local `qiskit-machine-learning`
objects when installed. Missing dependencies return unsupported metadata.

This workflow is not production ML, not a high-risk decision system, and does
not access cloud, tokens, or hardware.
