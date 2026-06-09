# Qiskit Machine Learning QNN Classifier With QuantumBridge

This clean-room example runs the QuantumBridge-native educational QNN
classifier slice.

```bash
python3 examples/qiskit_ml_qnn_classifier_quantumbridge.py
```

The native path creates a deterministic toy dataset, builds a small
feature-encoding plus RX/RY ansatz, evaluates an expectation value, trains with
a tiny deterministic grid search, and returns weights, predictions, and
accuracy through `QNNClassifierResult`.

The optional upstream path only introspects local `qiskit-machine-learning`
objects when installed. Missing dependencies return unsupported metadata.

This workflow is not production ML, does not guarantee training performance or
generalization, is not a high-risk decision system, and does not access cloud,
tokens, or hardware.
