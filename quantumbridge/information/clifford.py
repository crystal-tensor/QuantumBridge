# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from functools import lru_cache
from numbers import Integral

import numpy as np

from quantumbridge.core import Circuit
from quantumbridge.core.operations import Instruction
from quantumbridge.information.operator import Operator
from quantumbridge.operators import Pauli
from quantumbridge.operators.pauli import _PHASE_FACTORS, _validate_qargs
from quantumbridge.utils.math import gate_matrix


def _symplectic_product(left, right) -> int:
    width = len(left) // 2
    return int(
        np.count_nonzero(left[:width] & right[width:])
        + np.count_nonzero(left[width:] & right[:width])
    ) % 2


def _gf2_basis(rows) -> np.ndarray:
    matrix = np.array(rows, dtype=bool, copy=True)
    rank = 0
    for column in range(matrix.shape[1]):
        candidates = np.flatnonzero(matrix[rank:, column])
        if not candidates.size:
            continue
        pivot = rank + int(candidates[0])
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        other = np.flatnonzero(matrix[:, column])
        other = other[other != rank]
        matrix[other] ^= matrix[rank]
        rank += 1
        if rank == matrix.shape[0]:
            break
    return matrix[:rank]


def _gf2_solve(matrix, rhs) -> np.ndarray:
    coefficients = np.asarray(matrix, dtype=bool)
    target = np.asarray(rhs, dtype=bool)
    augmented = np.column_stack([coefficients, target])
    rank = 0
    pivots = []
    for column in range(coefficients.shape[1]):
        candidates = np.flatnonzero(augmented[rank:, column])
        if not candidates.size:
            continue
        pivot = rank + int(candidates[0])
        augmented[[rank, pivot]] = augmented[[pivot, rank]]
        others = np.flatnonzero(augmented[:, column])
        others = others[others != rank]
        augmented[others] ^= augmented[rank]
        pivots.append(column)
        rank += 1
        if rank == len(augmented):
            break
    if np.any(~np.any(augmented[:, :-1], axis=1) & augmented[:, -1]):
        raise ValueError("QuantumBridge binary constraints are inconsistent.")
    solution = np.zeros(coefficients.shape[1], dtype=bool)
    for row, column in enumerate(pivots):
        solution[column] = augmented[row, -1]
    return solution


def _matrix_pauli(matrix, atol: float = 1e-8) -> Pauli:
    data = np.asarray(matrix, dtype=complex)
    if data.ndim != 2:
        raise ValueError("QuantumBridge Pauli matrix must be two-dimensional.")
    dimension = data.shape[0]
    if data.shape != (dimension, dimension) or dimension == 0 or dimension & (dimension - 1):
        raise ValueError("QuantumBridge Pauli matrix must have power-of-two square dimensions.")
    width = dimension.bit_length() - 1
    first_column = np.flatnonzero(np.abs(data[:, 0]) > atol)
    if len(first_column) != 1:
        raise ValueError("QuantumBridge unitary does not normalize the Pauli group.")
    shift = int(first_column[0])
    amplitude = data[shift, 0]
    z = np.zeros(width, dtype=bool)
    x = np.array([bool(shift & (1 << qubit)) for qubit in range(width)])
    for qubit in range(width):
        column = 1 << qubit
        ratio = data[shift ^ column, column] / amplitude
        if np.isclose(ratio, -1, atol=atol, rtol=0):
            z[qubit] = True
        elif not np.isclose(ratio, 1, atol=atol, rtol=0):
            raise ValueError("QuantumBridge unitary does not normalize the Pauli group.")
    factor = amplitude / (1j ** np.count_nonzero(z & x))
    matches = [phase for phase, value in enumerate(_PHASE_FACTORS) if np.isclose(factor, value, atol=atol, rtol=0)]
    if not matches:
        raise ValueError("QuantumBridge Pauli image has an invalid phase.")
    result = Pauli((z, x, matches[0]))
    if not np.allclose(data, result.to_matrix(), atol=atol, rtol=0):
        raise ValueError("QuantumBridge unitary does not normalize the Pauli group.")
    return result


@lru_cache(maxsize=128)
def _small_gate_table(matrix_bytes: bytes, width: int):
    dimension = 1 << width
    matrix = np.frombuffer(matrix_bytes, dtype=np.complex128).reshape(dimension, dimension)
    if not np.allclose(matrix.conj().T @ matrix, np.eye(dimension), atol=1e-8, rtol=0):
        raise ValueError("QuantumBridge Clifford gate must be unitary.")
    result = np.zeros((4 ** width, 2 * width + 1), dtype=bool)
    for code in range(4 ** width):
        digits = [(code >> (2 * qubit)) & 3 for qubit in range(width)]
        x = np.array([bool(digit & 1) for digit in digits])
        z = np.array([bool(digit & 2) for digit in digits])
        pauli = _matrix_pauli(matrix @ Pauli((z, x)).to_matrix() @ matrix.conj().T)
        if pauli.phase % 2:
            raise ValueError("QuantumBridge Clifford images must be Hermitian.")
        result[code] = np.r_[pauli.x, pauli.z, bool(pauli.phase // 2)]
    return result


class Clifford:
    """Native Clifford group element stored as a signed binary symplectic tableau."""

    CLIFFORD_GATES = {"id", "i", "h", "s", "sdg", "sx", "sxdg", "x", "y", "z", "cx", "cy", "cz", "swap", "dcx", "ecr", "iswap"}

    def __init__(self, data, validate: bool = True, copy: bool = True):
        if isinstance(data, Clifford):
            tableau = np.array(data.tableau, copy=copy)
        elif isinstance(data, (Circuit, Instruction)):
            tableau = self.from_circuit(data).tableau
        elif isinstance(data, Pauli):
            tableau = self.from_label(data._body).tableau
        elif isinstance(data, Operator):
            tableau = self.from_matrix(data.data).tableau
        elif isinstance(data, dict):
            tableau = self.from_dict(data).tableau
        else:
            raw = np.asarray(data)
            if np.iscomplexobj(raw):
                tableau = self.from_matrix(raw).tableau
            else:
                if raw.ndim != 2 or raw.shape[0] % 2 or raw.shape[1] not in (raw.shape[0], raw.shape[0] + 1):
                    raise ValueError("QuantumBridge Clifford tableau must have shape (2n, 2n) or (2n, 2n+1).")
                if not np.all((raw == 0) | (raw == 1)):
                    raise ValueError("QuantumBridge Clifford tableau entries must be binary.")
                tableau = np.array(raw, dtype=bool, copy=True) if copy else np.asarray(raw, dtype=bool)
                if tableau.shape[1] == tableau.shape[0]:
                    tableau = np.column_stack([tableau, np.zeros(len(tableau), dtype=bool)])
        self.tableau = tableau
        self.num_qubits = len(tableau) // 2
        if validate and not self.is_unitary():
            raise ValueError("QuantumBridge Clifford tableau is not symplectic.")

    @classmethod
    def identity(cls, num_qubits: int) -> "Clifford":
        if not isinstance(num_qubits, Integral) or num_qubits < 0:
            raise ValueError("QuantumBridge Clifford width must be a non-negative integer.")
        return cls(np.eye(2 * int(num_qubits), dtype=bool), validate=False)

    @classmethod
    def from_label(cls, label: str) -> "Clifford":
        if any(char not in "IXYZHS" for char in label):
            raise ValueError("QuantumBridge Clifford labels support I, X, Y, Z, H and S.")
        result = cls.identity(len(label))
        for wire, char in enumerate(label):
            if char != "I":
                result._append_gate(char.lower(), (len(label) - 1 - wire,))
        return result

    @classmethod
    def from_circuit(cls, circuit) -> "Clifford":
        if isinstance(circuit, Instruction):
            if circuit.metadata.get("condition") is not None or circuit.metadata.get("control_flow") is not None:
                raise ValueError("QuantumBridge Clifford cannot represent classical control flow.")
            if circuit.definition is not None:
                circuit = circuit.definition
            else:
                circuit = Circuit(circuit.num_qubits).append(circuit, range(circuit.num_qubits))
        if not isinstance(circuit, Circuit):
            raise TypeError("QuantumBridge Clifford.from_circuit requires a native Circuit or Instruction.")
        if circuit.measurements:
            raise ValueError("QuantumBridge Clifford cannot represent measurement or reset.")
        result = cls.identity(circuit.num_qubits)
        for operation in circuit.operations:
            if operation.metadata.get("condition") is not None or operation.metadata.get("control_flow") is not None:
                raise ValueError("QuantumBridge Clifford cannot represent classical control flow.")
            if operation.name in {"barrier", "delay"} and operation.metadata.get("directive"):
                continue
            if operation.name in {"measure", "reset"}:
                raise ValueError("QuantumBridge Clifford cannot represent measurement or reset.")
            try:
                matrix = gate_matrix(operation.name, operation.params, operation.metadata)
                qubits = tuple(circuit.num_qubits - 1 - wire for wire in reversed(operation.wires))
                result._append_matrix(matrix, qubits)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"QuantumBridge operation {operation.name!r} is not a supported Clifford gate.") from exc
        return result

    @classmethod
    def from_matrix(cls, matrix) -> "Clifford":
        data = np.asarray(matrix, dtype=complex)
        if data.ndim != 2 or data.shape[0] != data.shape[1]:
            raise ValueError("QuantumBridge Clifford matrix must be square.")
        dimension = data.shape[0]
        if dimension == 0 or dimension & (dimension - 1):
            raise ValueError("QuantumBridge Clifford matrix dimensions must be powers of two.")
        if not np.allclose(data.conj().T @ data, np.eye(dimension), atol=1e-8, rtol=0):
            raise ValueError("QuantumBridge Clifford matrix must be unitary.")
        result = cls.identity(dimension.bit_length() - 1)
        for row in range(2 * result.num_qubits):
            image = _matrix_pauli(data @ result._row_pauli(row).to_matrix() @ data.conj().T)
            result._set_row(row, image)
        return result

    @classmethod
    def from_operator(cls, operator) -> "Clifford":
        matrix = operator.to_matrix() if hasattr(operator, "to_matrix") else operator
        return cls.from_matrix(matrix)

    @classmethod
    def from_dict(cls, obj) -> "Clifford":
        stabilizers = [Pauli(label) for label in obj["stabilizer"]]
        destabilizers = [Pauli(label) for label in obj["destabilizer"]]
        if len(stabilizers) != len(destabilizers):
            raise ValueError("QuantumBridge Clifford stabilizer and destabilizer counts must match.")
        width = len(stabilizers)
        if any(pauli.num_qubits != width for pauli in destabilizers + stabilizers):
            raise ValueError("QuantumBridge Clifford generator widths must match their count.")
        result = cls.identity(width)
        for row, pauli in enumerate(destabilizers + stabilizers):
            result._set_row(row, pauli)
        if not result.is_unitary():
            raise ValueError("QuantumBridge Clifford generators do not form a symplectic basis.")
        return result

    @property
    def dim(self):
        return 1 << self.num_qubits, 1 << self.num_qubits

    @property
    def symplectic_matrix(self):
        return self.tableau[:, :-1]

    @property
    def x(self):
        return self.tableau[:, :self.num_qubits]

    @property
    def z(self):
        return self.tableau[:, self.num_qubits:2 * self.num_qubits]

    @property
    def phase(self):
        return self.tableau[:, -1]

    @property
    def destab(self):
        return self.tableau[:self.num_qubits]

    @property
    def stab(self):
        return self.tableau[self.num_qubits:]

    @property
    def destab_x(self):
        return self.x[:self.num_qubits]

    @property
    def destab_z(self):
        return self.z[:self.num_qubits]

    @property
    def destab_phase(self):
        return self.phase[:self.num_qubits]

    @property
    def stab_x(self):
        return self.x[self.num_qubits:]

    @property
    def stab_z(self):
        return self.z[self.num_qubits:]

    @property
    def stab_phase(self):
        return self.phase[self.num_qubits:]

    def input_dims(self, qargs=None):
        selected = tuple(range(self.num_qubits) if qargs is None else qargs)
        _validate_qargs(selected, len(selected), self.num_qubits)
        return (2,) * len(selected)

    output_dims = input_dims

    def _row_pauli(self, row: int) -> Pauli:
        return Pauli((self.z[row], self.x[row], 2 * int(self.phase[row])))

    def _set_row(self, row: int, pauli: Pauli) -> None:
        if pauli.num_qubits != self.num_qubits or pauli.phase % 2:
            raise ValueError("QuantumBridge Clifford generators must be Hermitian Paulis of matching width.")
        self.x[row] = pauli.x
        self.z[row] = pauli.z
        self.phase[row] = bool(pauli.phase // 2)

    def _append_matrix(self, matrix, qubits) -> None:
        selected = _validate_qargs(qubits, len(qubits), self.num_qubits)
        width = len(selected)
        data = np.asarray(matrix, dtype=np.complex128)
        if data.shape != (1 << width, 1 << width):
            raise ValueError("QuantumBridge Clifford gate matrix does not match its qubits.")
        if width > 2:
            composed = self.compose(Clifford.from_matrix(data), qargs=selected)
            self.tableau[:] = composed.tableau
            return
        actions = _small_gate_table(data.tobytes(), width)
        codes = np.zeros(2 * self.num_qubits, dtype=int)
        for offset, qubit in enumerate(selected):
            codes += (self.x[:, qubit].astype(int) + 2 * self.z[:, qubit].astype(int)) << (2 * offset)
        images = actions[codes]
        self.x[:, selected] = images[:, :width]
        self.z[:, selected] = images[:, width:2 * width]
        self.phase[:] ^= images[:, -1]

    def _append_gate(self, name: str, qubits) -> None:
        # Native two-qubit gate matrices list control first (the high local bit).
        selected = tuple(qubits)
        local = selected[::-1] if name in {"cx", "cy"} else selected
        self._append_matrix(gate_matrix(name), local)

    def is_unitary(self) -> bool:
        width = self.num_qubits
        identity = np.eye(width, dtype=np.uint8)
        zeros = np.zeros((width, width), dtype=np.uint8)
        form = np.block([[zeros, identity], [identity, zeros]])
        matrix = self.symplectic_matrix.astype(np.uint8)
        return bool(np.array_equal((matrix @ form @ matrix.T) % 2, form))

    def copy(self) -> "Clifford":
        return Clifford(self, validate=False)

    def to_labels(self, array: bool = False, mode: str = "B"):
        if mode not in {"B", "D", "S"}:
            raise ValueError("QuantumBridge Clifford label mode must be B, D or S.")
        rows = range(2 * self.num_qubits)
        if mode == "D":
            rows = range(self.num_qubits)
        elif mode == "S":
            rows = range(self.num_qubits, 2 * self.num_qubits)
        labels = [("-" if self.phase[row] else "+") + self._row_pauli(row)._body for row in rows]
        return np.asarray(labels) if array else labels

    def to_dict(self):
        return {"stabilizer": self.to_labels(mode="S"), "destabilizer": self.to_labels(mode="D")}

    def conjugate_pauli(self, pauli) -> Pauli:
        operator = pauli if isinstance(pauli, Pauli) else Pauli(pauli)
        if operator.num_qubits != self.num_qubits:
            raise ValueError("QuantumBridge Pauli and Clifford widths must match.")
        result = Pauli("I" * self.num_qubits)
        result.phase = operator.phase + 3 * np.count_nonzero(operator.x & operator.z)
        for qubit in range(self.num_qubits):
            if operator.x[qubit]:
                result = result.dot(self._row_pauli(qubit))
            if operator.z[qubit]:
                result = result.dot(self._row_pauli(self.num_qubits + qubit))
        return result

    def _embedded(self, qargs, width: int) -> "Clifford":
        selected = _validate_qargs(qargs, self.num_qubits, width)
        result = Clifford.identity(width)
        for index, qubit in enumerate(selected):
            result._set_row(qubit, self._row_pauli(index)._embedded(selected, width))
            result._set_row(width + qubit, self._row_pauli(self.num_qubits + index)._embedded(selected, width))
        return result

    def compose(self, other, qargs=None, front: bool = False) -> "Clifford":
        operand = other if isinstance(other, Clifford) else Clifford(other)
        if qargs is not None:
            operand = operand._embedded(qargs, self.num_qubits)
        if self.num_qubits != operand.num_qubits:
            raise ValueError("QuantumBridge Clifford composition requires matching widths.")
        first, second = (operand, self) if front else (self, operand)
        result = Clifford.identity(self.num_qubits)
        for row in range(2 * self.num_qubits):
            result._set_row(row, second.conjugate_pauli(first._row_pauli(row)))
        return result

    def dot(self, other, qargs=None) -> "Clifford":
        return self.compose(other, qargs=qargs, front=True)

    def adjoint(self) -> "Clifford":
        width = self.num_qubits
        order = np.r_[np.arange(width, 2 * width), np.arange(width)]
        inverse_matrix = self.symplectic_matrix.T[np.ix_(order, order)]
        result = Clifford(inverse_matrix, validate=False)
        for row in range(2 * width):
            image = self.conjugate_pauli(result._row_pauli(row))
            result.phase[row] = bool(image.phase // 2)
        return result

    def conjugate(self) -> "Clifford":
        result = self.copy()
        result.phase[:] ^= np.count_nonzero(result.x & result.z, axis=1) % 2 == 1
        return result

    def transpose(self) -> "Clifford":
        return self.adjoint().conjugate()

    def tensor(self, other) -> "Clifford":
        operand = other if isinstance(other, Clifford) else Clifford(other)
        width = self.num_qubits + operand.num_qubits
        result = Clifford.identity(width)
        for source, positions in ((operand, tuple(range(operand.num_qubits))), (self, tuple(range(operand.num_qubits, width)))):
            for offset, qubit in enumerate(positions):
                result._set_row(qubit, source._row_pauli(offset)._embedded(positions, width))
                result._set_row(width + qubit, source._row_pauli(source.num_qubits + offset)._embedded(positions, width))
        return result

    def expand(self, other) -> "Clifford":
        return Clifford(other).tensor(self)

    def power(self, n: int) -> "Clifford":
        if not isinstance(n, Integral) or n < 1:
            raise ValueError("QuantumBridge Clifford powers must be positive integers; use adjoint() for the inverse.")
        factor = self.copy()
        remaining = int(n)
        result = Clifford.identity(self.num_qubits)
        while remaining:
            if remaining & 1:
                result = result.compose(factor)
            remaining >>= 1
            if remaining:
                factor = factor.compose(factor)
        return result

    def to_circuit(self) -> Circuit:
        reduced = self.copy()
        width = self.num_qubits
        reductions = []

        def apply(name, *qubits):
            reduced._append_gate(name, qubits)
            reductions.append((name, qubits))

        # Reduce each conjugate X/Z generator pair, preserving earlier pairs.
        for index in range(width):
            active = np.flatnonzero(reduced.x[index, index:] | reduced.z[index, index:])
            if not active.size:
                raise ValueError("QuantumBridge Clifford tableau is not symplectic.")
            pivot = index + int(active[0])
            if reduced.z[index, pivot]:
                apply("sdg" if reduced.x[index, pivot] else "h", pivot)
            if pivot != index:
                apply("swap", index, pivot)
            for qubit in range(index + 1, width):
                if not (reduced.x[index, qubit] or reduced.z[index, qubit]):
                    continue
                if reduced.z[index, qubit]:
                    apply("sdg" if reduced.x[index, qubit] else "h", qubit)
                apply("cx", index, qubit)

            stabilizer_row = width + index
            if reduced.x[stabilizer_row, index]:
                apply("h", index)
                apply("s", index)
                apply("h", index)
            for qubit in range(index + 1, width):
                if not (reduced.x[stabilizer_row, qubit] or reduced.z[stabilizer_row, qubit]):
                    continue
                if reduced.x[stabilizer_row, qubit]:
                    if reduced.z[stabilizer_row, qubit]:
                        apply("sdg", qubit)
                    apply("h", qubit)
                apply("cx", qubit, index)
            if reduced.phase[index]:
                apply("z", index)
            if reduced.phase[stabilizer_row]:
                apply("x", index)

        if not np.array_equal(reduced.tableau, Clifford.identity(width).tableau):
            raise ValueError("QuantumBridge Clifford synthesis did not reduce to identity.")
        circuit = Circuit(width)
        inverse_names = {"s": "sdg", "sdg": "s"}
        for name, qubits in reversed(reductions):
            wires = [width - 1 - qubit for qubit in qubits]
            getattr(circuit, inverse_names.get(name, name))(*wires)
        return circuit

    def to_matrix(self) -> np.ndarray:
        if self.num_qubits == 0:
            return np.ones((1, 1), dtype=complex)
        return Operator.from_circuit(self.to_circuit()).data

    def to_operator(self) -> Operator:
        return Operator(self.to_matrix())

    def to_instruction(self) -> Instruction:
        return self.to_circuit().to_instruction(name="clifford")

    def equiv(self, other, atol: float = 1e-10) -> bool:
        if isinstance(other, Clifford):
            return self == other
        if isinstance(other, (Circuit, Instruction)):
            return self == Clifford(other)
        return self.to_operator().equiv(other, atol=atol)

    def __array__(self, dtype=None, copy=None):
        return np.array(self.tableau, dtype=dtype, copy=True)

    def __matmul__(self, other):
        return self.dot(other)

    def __xor__(self, other):
        return self.tensor(other)

    def __eq__(self, other) -> bool:
        return isinstance(other, Clifford) and np.array_equal(self.tableau, other.tableau)

    def __repr__(self):
        return f"Clifford({self.to_dict()!r})"
