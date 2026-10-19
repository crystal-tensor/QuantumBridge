# qiskit_aer Fusion Coverage Matrix

## Stage 11I Executable Native MPS Method

Native MatrixProductStateDevice/Backend implement SVD tensor execution,
nonadjacent/multiwire gates, CPTP trajectories/ensembles, dynamic measurement,
reset and feedback. Pauli observables, selected probabilities and reduced
density outputs do not expand global states. Provider/Job/V2 and native/IR
Aer-adjacent dispatch are executable without Aer installed.

Evidence: tests/devices/test_matrix_product_state_device.py (including a
100-qubit dense-call-blocked GHZ test), optional Aer MPS differential tests in
tests/compat_qiskit_aer/test_matrix_product_state_native.py, and the Stage 11I
report. This does not claim full Aer save/set snapshots, Gamma/Lambda format,
gate-attached noise or GPU/distributed method parity. The older inventories
below remain historical records, not a complete parity measurement.

## Stage 11H Executable Mixed-State Path

The native density_matrix device/backend accepts bound non-Clifford gates,
ordered multi-qubit CPTP Kraus instructions, reset, feedback and mixed initial
states. Backend/Job/V2 integration and serialized density results are exercised
without upstream SDKs. Optional Aer tests compare random Kraus evolution,
unitary/channel import/export, dynamic density matrices and counts.

Evidence: tests/devices/test_density_matrix_device.py and
tests/compat_qiskit_aer/test_density_matrix_native.py. Dense memory is
exponential and guarded. This is not full AerSimulator, gate-attached noise,
save-instruction or MPS parity; see the Stage 11H report.

## Stage 11G Executable Native Stabilizer Path

The runtime inventory below is historical, not proof of callable parity.
The native path now executes the following independently of installed Aer:

| Capability | Executable behavior | Evidence |
| --- | --- | --- |
| Stabilizer backend | Backend/Job, circuit batches, parameter binding, seeds, memory and exact Pauli expectations | tests/devices/test_stabilizer_device.py |
| Dynamic Clifford execution | Ordered measurement, reset, nested/repeated if/else, branch-entry snapshot and classical-bit remapping | Same tests and tests/core/test_ordered_measurements.py |
| Native noise | End-of-circuit single-wire Clifford mixtures and asymmetric readout; exact ensembles or shot trajectories | Same device suite; optional Aer statistics in tests/compat_qiskit_aer/test_stabilizer_native.py |
| Large-shot execution | 64-qubit uniform superposition with dense states and probability enumeration blocked | Device suite and examples/native_stabilizer_backend_quantumbridge.py |
| Aer-adjacent callable | run_stabilizer_simulator_native and backend='stabilizer', native Circuit/IR, 32-qubit GHZ, serialized result | tests/compat_qiskit_aer/test_stabilizer_native.py |

This does not implement complete AerSimulator, gate-attached Aer noise, every
save instruction or other Aer simulation methods. See the Stage 11G report
for supported contracts and explicit rejection paths.

## Historical Inventory

Generated from runtime public-name introspection. No upstream source, tests, comments, or documentation text is copied.

- Upstream package: qiskit-aer
- Upstream version: 0.17.2
- Dependency available: True
- Advisory: False
- Offline only: False
- Records: 24
- Unsupported: 0

| Module | Name | Type | Level | Supported | Advisory | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qiskit_aer | AerError | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | AerJob | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | AerProvider | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | AerSimulator | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | QasmSimulator | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | StatevectorSimulator | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer | UnitarySimulator | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | LocalNoisePass | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | NoiseModel | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | PauliError | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | PauliLindbladError | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | QuantumError | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | ReadoutError | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | RelaxationNoisePass | class | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | amplitude_damping_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | coherent_unitary_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | depolarizing_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | kraus_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | mixed_unitary_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | pauli_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | phase_amplitude_damping_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | phase_damping_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | reset_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit_aer.noise | thermal_relaxation_error | function | 0 | True | False | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
