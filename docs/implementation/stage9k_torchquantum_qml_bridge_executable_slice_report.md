# Stage 9K TorchQuantum / PyTorch-style QML Bridge Executable Slice Report

## Summary

Stage 9K adds a clean-room, educational TorchQuantum-like / PyTorch-style QML
bridge slice for QuantumBridge. It implements a native small-circuit quantum
layer, tensor and batch helpers, deterministic toy classifier training,
optional torch tensor interop, optional upstream TorchQuantum boundary metadata,
serializable result schemas, examples, and tests.

This stage does not copy TorchQuantum, PyTorch, IBM, Qiskit, or third-party
source, tutorials, UI, branding, model weights, wheels, dist-info, egg-info,
site-packages trees, or virtual environments.

## Implemented Scope

- `quantumbridge.compat.torchquantum` package.
- TensorLike adapters for Python lists, NumPy arrays, and optional torch tensors.
- Native TorchQuantum-like angle-encoder plus variational layer for 1-3 qubits.
- Batch forward execution using QuantumBridge native simulation.
- Deterministic toy binary classifier training through grid search.
- Optional torch tensor execution path when torch is installed.
- Optional upstream TorchQuantum passthrough boundary when installed.
- `quantumbridge.schema.torchquantum_results` result envelopes.
- Examples and tests proving actual execution.

## Example Proofs

- Layer forward returns probabilities, one output score, prediction, circuit
  metadata, warnings, and provenance.
- Batch forward returns outputs and predictions for multiple samples.
- Classifier training returns best weights, predictions, accuracy, loss, and a
  deterministic training trace.
- Optional upstream TorchQuantum reports unsupported metadata when not installed.

## Boundaries

- Not a full TorchQuantum replacement.
- Not a full PyTorch replacement.
- Not production QML training.
- Not suitable for high-risk automated decisions.
- No cloud access.
- No token reads.
- No real hardware access.
- No official endorsement claim.

## Validation Plan

- `python3 -m py_compile quantumbridge/compat/torchquantum/*.py quantumbridge/schema/*.py examples/torchquantum_like_layer_quantumbridge.py examples/torchquantum_like_batch_forward_quantumbridge.py examples/torchquantum_like_classifier_quantumbridge.py`
- `python3 examples/torchquantum_like_layer_quantumbridge.py`
- `python3 examples/torchquantum_like_batch_forward_quantumbridge.py`
- `python3 examples/torchquantum_like_classifier_quantumbridge.py`
- `pytest -q -rs tests/compat_torchquantum`
- related compatibility suites
- full `pytest -q -rs`
- `pytest --cov=quantumbridge`
- `bash scripts/run_local_matrix.sh`
- `git diff --check`

## Studio Readiness

The result schemas are suitable for future QuantumBridge Studio visualization of
tensor summaries, layer forward outputs, probabilities, predictions, training
trace, loss, accuracy, warnings, and provenance. No UI implementation is added
in Stage 9K.
