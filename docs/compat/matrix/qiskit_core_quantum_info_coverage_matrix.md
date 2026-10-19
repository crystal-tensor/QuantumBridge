# qiskit Coverage Matrix

## Stage 11F Executable Update

These native capabilities are independently executable without Qiskit. The
optional behavioral oracle is Qiskit 2.6.0, not the historical inventory below.

| Native API | Executed behavior | Evidence |
| --- | --- | --- |
| Clifford | Signed symplectic construction/validation, matrices, native circuits/instructions, composition/subsystems, adjoint/conjugate/transpose, tensor/expand, positive integer powers, circuit synthesis | tests/information/test_clifford_stabilizer_native.py and tests/compat_qiskit_core/test_clifford_stabilizer_parity.py |
| Pauli/PauliList.evolve | Heisenberg and Schrodinger Clifford evolution with subsystem indices and retained phase | Same test suites |
| StabilizerState | Stabilizer-list preparation, Clifford evolution, Pauli/sparse-Pauli expectations, probabilities, measurement/reset, seeded sampling, tensor products and explicit dense conversion | Same test suites |
| random_clifford | Uniform symplectic-basis and independent sign sampling, deterministic native seeds, all 24 one-qubit group elements reached | Same test suites; seeded sequences are not promised identical to Qiskit |
| Large tableau execution | 64-qubit GHZ construction, synthesis roundtrip, probabilities, expectation, reset and sampling, with dense conversions blocked | Native test suite and examples/native_clifford_stabilizer_quantumbridge.py |

Remaining boundaries and intentional API differences are recorded in the
Stage 11F report. These rows do not imply full quantum_info or Aer parity.

## Stage 11E Executable Update

The inventory below is a historical package-name snapshot. The following
native Pauli behavior is now verified against installed Qiskit 2.6.0:

| Native API | Executed behavior | Evidence |
| --- | --- | --- |
| Pauli | Multi-qubit phase, symplectic arrays, matrix, compose/dot, tensor/expand, adjoint/conjugate/transpose, powers, integer insertion/deletion, subsystem indices | tests/operators/test_pauli_phase_algebra.py and tests/compat_qiskit_core/test_pauli_phase_parity.py |
| PauliList | Phase-preserving row broadcasting, Cartesian tensor, commutation, sorting, uniqueness, row operations, greedy commuting groups | Same test suites; group correctness is checked without promising an identical coloring |
| random_pauli | Seeded labels, phase and Generator inputs | Same test suites |
| random_pauli_list | Seeded rows, phase and empty-list metadata | Same test suites |
| Native QNode and state observables | Expectation, state evolution, matrix instructions and PennyLane expectation comparison | tests/operators/test_pauli_phase_algebra.py and tests/qml/test_native_pauli_pennylane_parity.py |

This update is an executable subset. Clifford evolution was added in Stage
11F; layout contracts remain outside this slice. It does not turn historical
inventory rows into complete behavioral parity claims.

## Historical Inventory

Generated from runtime public-name introspection. No upstream source, tests, comments, or documentation text is copied.

- Installed: True
- Upstream version: 2.4.1
- Inventory generated: true
- Public API count: 54
- QuantumBridge coverage level: 0

| Upstream Package | Module | Public API | Type | QuantumBridge Level | Mode | Dependency Extra | Test | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qiskit | qiskit.quantum_info | CNOTDihedral | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Chi | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Choi | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Clifford | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | DensityMatrix | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Kraus | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Operator | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | PTM | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Pauli | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | PauliLindbladMap | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | PauliList | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | PhasedQubitSparsePauli | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | PhasedQubitSparsePauliList | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Quaternion | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | QubitSparsePauli | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | QubitSparsePauliList | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | ScalarOp | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | SparseObservable | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | SparsePauliOp | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | StabilizerState | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Statevector | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Stinespring | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | SuperOp | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | Z2Symmetries | class | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | anti_commutator | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | average_gate_fidelity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | commutator | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | concurrence | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | diamond_norm | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | double_commutator | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | entanglement_of_formation | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | entropy | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | gate_error | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | get_clifford_gate_names | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | hellinger_distance | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | hellinger_fidelity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | mutual_information | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | negativity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | partial_trace | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | pauli_basis | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | process_fidelity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | purity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_clifford | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_cnotdihedral | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_density_matrix | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_hermitian | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_pauli | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_pauli_list | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_quantum_channel | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_statevector | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | random_unitary | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | schmidt_decomposition | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | shannon_entropy | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
| qiskit | qiskit.quantum_info | state_fidelity | function | 0 | Inventory/Passthrough scaffold | qiskit-core | inventory/introspection smoke | MEDIUM | Runtime public-name inventory; no upstream source or docs copied. |
