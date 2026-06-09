# Stage 9E Qiskit Machine Learning Executable Slice Report

Status: completed locally; GitHub Actions pending after push
Date: 2026-06-09

## Scope

Stage 9E adds a clean-room, QuantumBridge-native educational QML slice for
Qiskit Machine Learning compatibility targets:

- deterministic toy binary datasets;
- native angle feature maps using QuantumBridge circuits;
- state-fidelity quantum kernel matrices;
- nearest-kernel classifier execution;
- minimal QNN forward pass;
- deterministic grid-search QNN classifier execution;
- optional local upstream `qiskit-machine-learning` runtime introspection;
- ML result schemas, examples, tests, warnings, provenance, and
  Studio-readiness metadata.

## Executable Proof

The native examples are:

- `examples/qiskit_ml_quantum_kernel_quantumbridge.py`
- `examples/qiskit_ml_kernel_classifier_quantumbridge.py`
- `examples/qiskit_ml_qnn_classifier_quantumbridge.py`

The native APIs are:

- `quantumbridge.compat.qiskit_machine_learning.run_quantum_kernel_native()`
- `quantumbridge.compat.qiskit_machine_learning.run_kernel_classifier_native()`
- `quantumbridge.compat.qiskit_machine_learning.run_qnn_classifier_native()`
- `quantumbridge.compat.qiskit_machine_learning.qnn_forward_native()`

Each result records dataset metadata, feature-map metadata where applicable,
kernel matrix or model summary, weights, predictions, accuracy, warnings, and
provenance.

## Upstream Path

Optional upstream introspection is exposed through:

- `run_upstream_quantum_kernel_if_available()`
- `run_upstream_classifier_if_available()`
- `run_upstream_qnn_if_available()`

This path runs only when the local optional Qiskit Machine Learning stack is
installed. Missing dependencies return clear unsupported metadata.

## Non-Goals

Stage 9E does not:

- implement full Qiskit Machine Learning parity;
- provide production machine learning;
- guarantee training performance or generalization;
- support medical, financial, employment, identity, safety, or other high-risk
  automated decisions;
- access IBM Runtime, cloud accounts, tokens, credentials, or real hardware;
- vendor Qiskit Machine Learning or any other third-party source;
- create a tag or release;
- implement QuantumBridge Studio UI.

## Validation

Validation commands are run before direct-pushing main:

- `python3 -m py_compile quantumbridge/compat/qiskit_machine_learning/*.py quantumbridge/schema/*.py examples/qiskit_ml_quantum_kernel_quantumbridge.py examples/qiskit_ml_kernel_classifier_quantumbridge.py examples/qiskit_ml_qnn_classifier_quantumbridge.py`
- `python3 examples/qiskit_ml_quantum_kernel_quantumbridge.py`
- `python3 examples/qiskit_ml_kernel_classifier_quantumbridge.py`
- `python3 examples/qiskit_ml_qnn_classifier_quantumbridge.py`
- `pytest -q -rs tests/compat_qiskit_machine_learning`
- `pytest -q -rs tests/compat_qiskit_nature`
- `pytest -q -rs tests/compat_qiskit_algorithms`
- `pytest -q -rs tests/compat_qiskit_optimization`
- `pytest -q -rs tests/compat_qiskit_finance`
- `pytest -q -rs tests/ecosystem`
- `pytest -q -rs`
- `pytest --cov=quantumbridge`
- `bash scripts/run_local_matrix.sh`
- `git diff --check`

Final results are recorded in the commit summary after the validation run.
