# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from copy import deepcopy
from numbers import Integral

import numpy as np

from quantumbridge.information.clifford import Clifford, _gf2_basis, _gf2_solve, _symplectic_product
from quantumbridge.operators import Pauli, SparsePauliOperator
from quantumbridge.operators.pauli import _PHASE_FACTORS, _validate_qargs


def _pauli_vector(pauli: Pauli):
    return np.r_[pauli.x, pauli.z]


def _nullspace(matrix):
    reduced = _gf2_basis(matrix)
    width = reduced.shape[1]
    pivots = [int(np.flatnonzero(row)[0]) for row in reduced]
    vectors = []
    for column in range(width):
        if column in pivots:
            continue
        vector = np.zeros(width, dtype=bool)
        vector[column] = True
        for row, pivot in enumerate(pivots):
            vector[pivot] = reduced[row, column]
        vectors.append(vector)
    return np.array(vectors, dtype=bool).reshape(-1, width)


class StabilizerState:
    """Pure stabilizer state with polynomial-memory Clifford-tableau execution."""

    def __init__(self, data, validate: bool = True):
        if isinstance(data, StabilizerState):
            self._clifford = data.clifford.copy()
            self._rng = deepcopy(data._rng)
        else:
            self._clifford = Clifford(data, validate=validate)
            self._rng = np.random.default_rng()

    @classmethod
    def from_stabilizer_list(
        cls,
        stabilizers,
        allow_redundant: bool = False,
        allow_underconstrained: bool = False,
    ) -> "StabilizerState":
        supplied = [Pauli(label) for label in stabilizers]
        if not supplied:
            raise ValueError("QuantumBridge needs a non-empty stabilizer list to infer state width.")
        width = supplied[0].num_qubits
        if width == 0 or any(pauli.num_qubits != width or pauli.phase % 2 for pauli in supplied):
            raise ValueError("QuantumBridge stabilizers must be matching-width Hermitian Paulis.")
        if any(not left.commutes(right) for index, left in enumerate(supplied) for right in supplied[index + 1:]):
            raise ValueError("QuantumBridge stabilizer generators must commute.")

        basis = {}
        independent = []
        for pauli in supplied:
            reduced = pauli.copy()
            for pivot in sorted(basis):
                if _pauli_vector(reduced)[pivot]:
                    reduced = reduced.dot(basis[pivot])
            positions = np.flatnonzero(_pauli_vector(reduced))
            if not positions.size:
                if reduced.phase:
                    raise ValueError("QuantumBridge stabilizer constraints contain negative identity.")
                if not allow_redundant:
                    raise ValueError("QuantumBridge stabilizer generators are redundant.")
                continue
            basis[int(positions[0])] = reduced
            independent.append(pauli)

        if len(independent) < width and not allow_underconstrained:
            raise ValueError("QuantumBridge stabilizer list is underconstrained.")
        while len(independent) < width:
            vectors = np.array([_pauli_vector(pauli) for pauli in independent], dtype=bool).reshape(-1, 2 * width)
            constraints = np.c_[vectors[:, width:], vectors[:, :width]]
            for candidate in _nullspace(constraints):
                if len(_gf2_basis(np.vstack([vectors, candidate]))) > len(independent):
                    independent.append(Pauli((candidate[width:], candidate[:width])))
                    break
            else:
                raise ValueError("QuantumBridge cannot complete the stabilizer constraints.")

        stabilizer_vectors = np.array([_pauli_vector(pauli) for pauli in independent])
        constraints = np.c_[stabilizer_vectors[:, width:], stabilizer_vectors[:, :width]]
        destabilizers = []
        for index in range(width):
            additional = np.array([_pauli_vector(pauli) for pauli in destabilizers], dtype=bool).reshape(-1, 2 * width)
            equations = np.vstack([constraints, np.c_[additional[:, width:], additional[:, :width]]])
            target = np.zeros(width + index, dtype=bool)
            target[index] = True
            vector = _gf2_solve(equations, target)
            destabilizers.append(Pauli((vector[width:], vector[:width])))
        clifford = Clifford.identity(width)
        for row, pauli in enumerate(destabilizers + independent):
            clifford._set_row(row, pauli)
        return cls(clifford)

    @property
    def clifford(self):
        return self._clifford

    @property
    def num_qubits(self):
        return self.clifford.num_qubits

    @property
    def dim(self):
        return 1 << self.num_qubits

    def _qubits(self, qargs):
        selected = tuple(range(self.num_qubits) if qargs is None else qargs)
        return _validate_qargs(selected, len(selected), self.num_qubits)

    def dims(self, qargs=None):
        return (2,) * len(self._qubits(qargs))

    def is_valid(self, atol=None, rtol=None) -> bool:
        return self.clifford.is_unitary()

    def copy(self):
        return StabilizerState(self)

    def seed(self, value=None) -> None:
        self._rng = np.random.default_rng(value)

    def trace(self):
        return 1.0

    def purity(self):
        return 1.0

    def expectation_value(self, oper, qargs=None):
        if isinstance(oper, SparsePauliOperator):
            return sum(coefficient * self.expectation_value(Pauli(label), qargs=qargs) for label, coefficient in oper.terms)
        pauli = oper if isinstance(oper, Pauli) else Pauli(oper)
        if qargs is not None:
            pauli = pauli._embedded(qargs, self.num_qubits)
        if pauli.num_qubits != self.num_qubits:
            raise ValueError("QuantumBridge stabilizer observable width must match the state.")
        vector = _pauli_vector(pauli)
        if any(_symplectic_product(vector, row[:-1]) for row in self.clifford.stab):
            return 0j
        represented = Pauli("I" * self.num_qubits)
        for index, row in enumerate(self.clifford.destab):
            if _symplectic_product(vector, row[:-1]):
                represented = represented.dot(self.clifford._row_pauli(self.num_qubits + index))
        return complex(_PHASE_FACTORS[(pauli.phase - represented.phase) % 4])

    def evolve(self, other, qargs=None):
        result = self.copy()
        result._clifford = self.clifford.compose(other, qargs=qargs)
        return result

    def conjugate(self):
        result = self.copy()
        result._clifford = self.clifford.conjugate()
        return result

    def tensor(self, other):
        operand = other if isinstance(other, StabilizerState) else StabilizerState(other)
        return StabilizerState(self.clifford.tensor(operand.clifford))

    def expand(self, other):
        operand = other if isinstance(other, StabilizerState) else StabilizerState(other)
        return operand.tensor(self)

    def equiv(self, other) -> bool:
        operand = other if isinstance(other, StabilizerState) else StabilizerState(other)
        if self.num_qubits != operand.num_qubits:
            return False
        return all(self.expectation_value(operand.clifford._row_pauli(self.num_qubits + row)) == 1 for row in range(self.num_qubits))

    def _measure_z(self, qubit: int, forced=None, rng=None):
        pivot_rows = np.flatnonzero(self.clifford.stab_x[:, qubit])
        if not pivot_rows.size:
            z = np.zeros(self.num_qubits, dtype=bool)
            z[qubit] = True
            observable = Pauli((z, np.zeros(self.num_qubits, dtype=bool)))
            outcome = 0 if self.expectation_value(observable).real > 0 else 1
            return outcome, float(forced is None or forced == outcome)

        outcome = int((self._rng if rng is None else rng).integers(2)) if forced is None else int(forced)
        destabilizer_row = int(pivot_rows[0])
        pivot = self.num_qubits + destabilizer_row
        generator = self.clifford._row_pauli(pivot)
        for row in np.flatnonzero(self.clifford.x[:, qubit]):
            if row not in (pivot, destabilizer_row):
                self.clifford._set_row(int(row), self.clifford._row_pauli(int(row)).dot(generator))
        self.clifford._set_row(destabilizer_row, generator)
        z = np.zeros(self.num_qubits, dtype=bool)
        z[qubit] = True
        self.clifford._set_row(pivot, Pauli((z, np.zeros(self.num_qubits, dtype=bool), 2 * outcome)))
        return outcome, 0.5

    def measure(self, qargs=None):
        selected = self._qubits(qargs)
        result = self.copy()
        outcomes = [result._measure_z(qubit, rng=self._rng)[0] for qubit in selected]
        result._rng = deepcopy(self._rng)
        return "".join(str(value) for value in reversed(outcomes)), result

    def reset(self, qargs=None):
        selected = self._qubits(qargs)
        result = self.copy()
        for qubit in selected:
            outcome, _ = result._measure_z(qubit, rng=self._rng)
            if outcome:
                result.clifford._append_gate("x", (qubit,))
        result._rng = deepcopy(self._rng)
        return result

    def sample_memory(self, shots: int, qargs=None):
        if not isinstance(shots, Integral) or shots < 0:
            raise ValueError("QuantumBridge stabilizer shots must be a non-negative integer.")
        selected = self._qubits(qargs)
        memory = []
        for _ in range(shots):
            collapsed = self.copy()
            outcomes = [collapsed._measure_z(qubit, rng=self._rng)[0] for qubit in selected]
            memory.append("".join(str(value) for value in reversed(outcomes)))
        return np.asarray(memory, dtype=str)

    def sample_counts(self, shots: int, qargs=None):
        counts = {}
        for bitstring in self.sample_memory(shots, qargs=qargs):
            bitstring = str(bitstring)
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return counts

    def probabilities_dict(self, qargs=None, decimals=None):
        selected = self._qubits(qargs)
        branches = [(self.copy(), (), 1.0)]
        for qubit in selected:
            next_branches = []
            for state, bits, probability in branches:
                for outcome in (0, 1):
                    collapsed = state.copy()
                    _, weight = collapsed._measure_z(qubit, forced=outcome)
                    if weight:
                        next_branches.append((collapsed, bits + (outcome,), probability * weight))
            branches = next_branches
        probabilities = {
            "".join(str(value) for value in reversed(bits)): probability
            for _, bits, probability in branches
        }
        if decimals is not None:
            probabilities = {key: round(value, decimals) for key, value in probabilities.items()}
        return dict(sorted((key, value) for key, value in probabilities.items() if value))

    def probabilities(self, qargs=None, decimals=None):
        selected = self._qubits(qargs)
        probabilities = np.zeros(1 << len(selected))
        for key, value in self.probabilities_dict(selected, decimals=decimals).items():
            probabilities[int(key or "0", 2)] = value
        return probabilities

    def to_statevector(self):
        from quantumbridge.information.statevector import Statevector

        if self.num_qubits == 0:
            return Statevector([1])
        return Statevector.from_circuit(self.clifford.to_circuit())

    def to_operator(self):
        """Return the state's Clifford preparation unitary, not its projector."""
        return self.clifford.to_operator()

    def to_density_matrix(self):
        from quantumbridge.information.density_matrix import DensityMatrix

        vector = self.to_statevector().data
        return DensityMatrix(np.outer(vector, vector.conj()))

    def __repr__(self):
        return f"StabilizerState({self.clifford.to_labels(mode='S')!r})"
