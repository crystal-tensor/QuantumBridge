# Stage 9D Qiskit Nature Executable Chemistry Slice Report

Status: implementation in progress
Date: 2026-06-09

## Scope

Stage 9D adds a clean-room, QuantumBridge-native educational chemistry slice
for Qiskit Nature compatibility targets:

- H2 minimal molecular problem metadata;
- LiH minimal molecular problem metadata;
- deterministic small qubit Hamiltonians;
- exact diagonalization;
- optional local upstream Qiskit Nature passthrough;
- chemistry result schemas;
- examples, tests, warnings, provenance, and Studio-readiness metadata.

## Executable Proof

The native examples are:

- `examples/qiskit_nature_h2_quantumbridge.py`
- `examples/qiskit_nature_lih_quantumbridge.py`

The native APIs are:

- `quantumbridge.compat.qiskit_nature.run_h2_native()`
- `quantumbridge.compat.qiskit_nature.run_lih_native()`
- `quantumbridge.compat.qiskit_nature.build_h2_problem()`
- `quantumbridge.compat.qiskit_nature.build_lih_problem()`

Each result records molecule, basis, bond length, mapper, qubit count, particle
count, Hamiltonian term count, electronic energy, nuclear repulsion, total
energy, warnings, and provenance.

## Upstream Path

Optional upstream passthrough is exposed through:

- `run_h2_upstream_passthrough()`
- `run_lih_upstream_passthrough()`

This path runs only when the local optional chemistry stack is installed. It is
reported as upstream passthrough and is not claimed as QuantumBridge-native
chemistry behavior.

## Non-Goals

Stage 9D does not:

- implement full Qiskit Nature parity;
- provide production quantum chemistry;
- provide molecular design software;
- implement materials band-gap calculation;
- access IBM Runtime, cloud accounts, tokens, credentials, or real hardware;
- vendor Qiskit Nature, PySCF, OpenFermion, or any other third-party source;
- create a tag or release.

## Validation

Validation commands are run before direct-pushing main:

- `python3 -m py_compile quantumbridge/compat/qiskit_nature/*.py quantumbridge/schema/*.py examples/qiskit_nature_h2_quantumbridge.py examples/qiskit_nature_lih_quantumbridge.py`
- `python3 examples/qiskit_nature_h2_quantumbridge.py`
- `python3 examples/qiskit_nature_lih_quantumbridge.py`
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
