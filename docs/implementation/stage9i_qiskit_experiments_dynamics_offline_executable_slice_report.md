# Stage 9I Qiskit Experiments / Dynamics Offline Executable Slice Report

Status: implemented locally; validation pending full matrix
Date: 2026-06-09

## Scope

Stage 9I adds clean-room educational offline executable slices for Qiskit
Experiments and Qiskit Dynamics compatibility targets. The implementation is
owned by QuantumBridge and does not copy IBM, Qiskit, Qiskit Experiments,
Qiskit Dynamics, tutorial prose, UI, branding, or third-party project source.

## Implemented Workflows

- Native educational Rabi synthetic experiment with deterministic fitting.
- Native educational T1 synthetic experiment with deterministic fitting.
- Native educational Ramsey synthetic experiment with deterministic fitting.
- Native educational single-qubit Z precession dynamics.
- Native educational Rabi drive dynamics.
- Native educational dephasing metadata simulation.
- Optional upstream `qiskit-experiments` and `qiskit-dynamics` passthrough
  boundaries when installed.

## Result Schemas

Added:

- `quantumbridge/schema/experiments_results.py`
- `quantumbridge/schema/dynamics_results.py`

The schemas include native, upstream passthrough, and comparison result
families. They reject production readiness and hardware calibration claims.

## Boundaries

This stage is not a full Qiskit Experiments replacement, not a full Qiskit
Dynamics replacement, not hardware calibration, not production experiment
analysis, not production dynamics software, not IBM Runtime access, and not
real hardware access. No UI implementation, tag, release, or vendored
third-party source is included.

## Initial Validation

- `python3 -m py_compile quantumbridge/compat/qiskit_experiments/*.py quantumbridge/compat/qiskit_dynamics/*.py quantumbridge/schema/*.py examples/qiskit_experiments_rabi_quantumbridge.py examples/qiskit_experiments_t1_ramsey_quantumbridge.py examples/qiskit_dynamics_single_qubit_quantumbridge.py`: passed
- `python3 examples/qiskit_experiments_rabi_quantumbridge.py`: passed
- `python3 examples/qiskit_experiments_t1_ramsey_quantumbridge.py`: passed
- `python3 examples/qiskit_dynamics_single_qubit_quantumbridge.py`: passed
- `pytest -q -rs tests/compat_qiskit_experiments tests/compat_qiskit_dynamics`: `35 passed, 2 skipped`

Full pytest, coverage, local matrix, and remote Actions are recorded in the
final execution output after the stage is committed.

## Executable Proof Snapshot

- Rabi workflow returns finite frequency, contrast, offset, pi-amplitude, SSE,
  RMSE, and R-squared metadata.
- T1 workflow returns a positive T1-like parameter and goodness metadata.
- Ramsey workflow returns finite detuning and T2-star-like metadata.
- Dynamics workflows return time points, expectation values, and final states.

## Stage Gate Judgment

Stage 9I is a real executable educational offline slice, not scaffold-only. It
is ready for future QuantumBridge Studio visualization integration at the
API/schema level, but no UI implementation was performed in this stage.
