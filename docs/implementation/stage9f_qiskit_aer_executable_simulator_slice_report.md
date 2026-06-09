# Stage 9F Qiskit Aer Executable Simulator Slice Report

Status: completed locally; GitHub Actions pending after push
Date: 2026-06-09

## Scope

Stage 9F adds a clean-room, QuantumBridge-native educational simulator slice
for Qiskit Aer compatibility targets:

- deterministic small-circuit statevector execution;
- seeded qasm-style shot sampling;
- simple educational measurement bit-flip noise;
- QuantumBridge Circuit, QuantumBridge IR, IR dictionary, and basic Qiskit
  QuantumCircuit input normalization;
- optional local upstream `qiskit-aer` passthrough;
- Aer result schemas, examples, tests, warnings, provenance, and
  Studio-readiness metadata.

## Executable Proof

The native examples are:

- `examples/qiskit_aer_statevector_quantumbridge.py`
- `examples/qiskit_aer_qasm_counts_quantumbridge.py`
- `examples/qiskit_aer_noisy_counts_quantumbridge.py`

The native APIs are:

- `quantumbridge.compat.qiskit_aer.run_statevector_simulator_native()`
- `quantumbridge.compat.qiskit_aer.run_qasm_simulator_native()`
- `quantumbridge.compat.qiskit_aer.run_noisy_qasm_simulator_native()`
- `quantumbridge.compat.qiskit_aer.execute_basic_circuit_native()`
- `quantumbridge.compat.qiskit_aer.normalize_circuit_to_quantumbridge_ir()`

Each result records backend, mode, qubit count, shots, seed, statevector or
counts/probabilities, warnings, provenance, no-cloud/no-token/no-hardware
metadata, and production-ready false.

## Upstream Path

Optional upstream passthrough is exposed through:

- `run_statevector_upstream_aer()`
- `run_qasm_upstream_aer()`
- `run_noisy_upstream_aer()`
- `validate_aer_dependencies()`
- `wrap_upstream_aer_result()`

This path runs only when the local optional Qiskit Aer stack is installed.
Missing dependencies return clear unsupported metadata. It does not access IBM
Runtime, cloud accounts, tokens, credentials, or real hardware.

## Non-Goals

Stage 9F does not:

- implement full Qiskit Aer parity;
- provide production simulator software;
- provide Qiskit Aer performance parity;
- provide Qiskit Aer noise-model parity;
- emulate real cloud backends, hardware, IBM Runtime, tokens, or credentials;
- vendor Qiskit Aer or any other third-party source;
- create a tag or release;
- implement QuantumBridge Studio UI.

## Validation

Validation commands are run before direct-pushing main:

- `python3 -m py_compile quantumbridge/compat/qiskit_aer/*.py quantumbridge/schema/aer_results.py examples/qiskit_aer_statevector_quantumbridge.py examples/qiskit_aer_qasm_counts_quantumbridge.py examples/qiskit_aer_noisy_counts_quantumbridge.py`
- `python3 examples/qiskit_aer_statevector_quantumbridge.py`
- `python3 examples/qiskit_aer_qasm_counts_quantumbridge.py`
- `python3 examples/qiskit_aer_noisy_counts_quantumbridge.py`
- `pytest -q -rs tests/compat_qiskit_aer`
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
