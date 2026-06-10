# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/simulator_design_v0.1.md, docs/mvp/algorithm_design_v0.1.md,
# and docs/mvp/gradient_design_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, sqrt
from numbers import Real
from typing import Iterable, Optional, Union

import numpy as np


I2 = np.eye(2, dtype=complex)
PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def gate_matrix(name: str, params: tuple[Real, ...] = (), metadata: Optional[dict] = None) -> np.ndarray:
    if name in {"id", "i"}:
        return I2
    if name == "x":
        return PAULI_X
    if name == "y":
        return PAULI_Y
    if name == "z":
        return PAULI_Z
    if name == "h":
        return np.array([[1, 1], [1, -1]], dtype=complex) / sqrt(2)
    if name == "sx":
        return 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex)
    if name == "sxdg":
        return 0.5 * np.array([[1 - 1j, 1 + 1j], [1 + 1j, 1 - 1j]], dtype=complex)
    if name == "s":
        return np.array([[1, 0], [0, 1j]], dtype=complex)
    if name == "sdg":
        return np.array([[1, 0], [0, -1j]], dtype=complex)
    if name == "t":
        return np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)
    if name == "tdg":
        return np.array([[1, 0], [0, np.exp(-1j * np.pi / 4)]], dtype=complex)
    if name == "rx":
        theta = float(params[0])
        return np.array([[cos(theta / 2), -1j * sin(theta / 2)], [-1j * sin(theta / 2), cos(theta / 2)]], dtype=complex)
    if name == "ry":
        theta = float(params[0])
        return np.array([[cos(theta / 2), -sin(theta / 2)], [sin(theta / 2), cos(theta / 2)]], dtype=complex)
    if name == "rz":
        theta = float(params[0])
        return np.array([[np.exp(-0.5j * theta), 0], [0, np.exp(0.5j * theta)]], dtype=complex)
    if name in {"phase", "p", "u1"}:
        theta = float(params[0])
        return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)
    if name == "u2":
        return _u_matrix(np.pi / 2, float(params[0]), float(params[1]))
    if name in {"u", "u3"}:
        return _u_matrix(float(params[0]), float(params[1]), float(params[2]))
    if name == "cx":
        return np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
            dtype=complex,
        )
    if name == "cy":
        return _controlled_one_qubit_matrix(PAULI_Y)
    if name == "cz":
        return np.diag([1, 1, 1, -1]).astype(complex)
    if name == "ch":
        return _controlled_one_qubit_matrix(gate_matrix("h"))
    if name == "csx":
        return _controlled_one_qubit_matrix(gate_matrix("sx"))
    if name == "csxdg":
        return _controlled_one_qubit_matrix(gate_matrix("sxdg"))
    if name in {"crx", "cry", "crz", "cphase", "cp"}:
        target_name = {"crx": "rx", "cry": "ry", "crz": "rz", "cphase": "phase", "cp": "phase"}[name]
        target = gate_matrix(target_name, params)
        return _controlled_one_qubit_matrix(target)
    if name in {"rxx", "ryy", "rzz"}:
        theta = float(params[0])
        pauli = {
            "rxx": np.kron(PAULI_X, PAULI_X),
            "ryy": np.kron(PAULI_Y, PAULI_Y),
            "rzz": np.kron(PAULI_Z, PAULI_Z),
        }[name]
        return cos(theta / 2) * np.eye(4, dtype=complex) - 1j * sin(theta / 2) * pauli
    if name == "swap":
        return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
    if name == "dcx":
        return _reverse_control_cx_matrix() @ gate_matrix("cx")
    if name == "ecr":
        return (
            np.array(
                [[0, 0, 1, 1j], [0, 0, 1j, 1], [1, -1j, 0, 0], [-1j, 1, 0, 0]],
                dtype=complex,
            )
            / sqrt(2)
        )
    if name == "iswap":
        return np.array([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, 1]], dtype=complex)
    if name == "ccx":
        matrix = np.eye(8, dtype=complex)
        matrix[6, 6] = 0
        matrix[7, 7] = 0
        matrix[6, 7] = 1
        matrix[7, 6] = 1
        return matrix
    if name == "cswap":
        matrix = np.eye(8, dtype=complex)
        matrix[5, 5] = 0
        matrix[6, 6] = 0
        matrix[5, 6] = 1
        matrix[6, 5] = 1
        return matrix
    if metadata and "matrix" in metadata:
        return np.asarray(metadata["matrix"], dtype=complex)
    raise ValueError(f"QuantumBridge operation {name!r} is not supported by the MVP simulator.")


def _u_matrix(theta: float, phi: float, lam: float) -> np.ndarray:
    return np.array(
        [
            [cos(theta / 2), -np.exp(1j * lam) * sin(theta / 2)],
            [np.exp(1j * phi) * sin(theta / 2), np.exp(1j * (phi + lam)) * cos(theta / 2)],
        ],
        dtype=complex,
    )


def _controlled_one_qubit_matrix(target: np.ndarray) -> np.ndarray:
    out = np.eye(4, dtype=complex)
    out[2:4, 2:4] = np.asarray(target, dtype=complex)
    return out


def _reverse_control_cx_matrix() -> np.ndarray:
    return np.array(
        [[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]],
        dtype=complex,
    )


def bit_at(index: int, wire: int, num_qubits: int) -> int:
    return (index >> (num_qubits - 1 - wire)) & 1


def set_bit(index: int, wire: int, value: int, num_qubits: int) -> int:
    mask = 1 << (num_qubits - 1 - wire)
    return (index | mask) if value else (index & ~mask)


def apply_unitary(state: np.ndarray, matrix: np.ndarray, targets: tuple[int, ...], num_qubits: int) -> np.ndarray:
    targets = tuple(targets)
    size = 1 << num_qubits
    dim = 1 << len(targets)
    if matrix.shape != (dim, dim):
        raise ValueError("QuantumBridge unitary shape does not match target wires.")
    out = np.zeros_like(state, dtype=complex)
    for basis in range(size):
        col = 0
        base = basis
        for wire in targets:
            col = (col << 1) | bit_at(basis, wire, num_qubits)
            base = set_bit(base, wire, 0, num_qubits)
        for row in range(dim):
            dest = base
            for offset, wire in enumerate(reversed(targets)):
                dest = set_bit(dest, wire, (row >> offset) & 1, num_qubits)
            out[dest] += matrix[row, col] * state[basis]
    return out


def probabilities_from_state(state: np.ndarray, num_qubits: int, wires: Optional[Iterable[int]] = None) -> dict[str, float]:
    selected = tuple(range(num_qubits) if wires is None else wires)
    probs: dict[str, float] = {}
    for index, amp in enumerate(state):
        key = "".join(str(bit_at(index, wire, num_qubits)) for wire in selected)
        probs[key] = probs.get(key, 0.0) + float(abs(amp) ** 2)
    return probs


@dataclass(frozen=True)
class PauliString:
    """Tensor product of Pauli operators over selected wires."""

    terms: tuple[tuple[int, str], ...]

    def __init__(self, terms: Iterable[tuple[int, str]]):
        normalized = tuple((int(wire), label.upper()) for wire, label in terms)
        for _, label in normalized:
            if label not in {"I", "X", "Y", "Z"}:
                raise ValueError("QuantumBridge PauliString labels must be I, X, Y, or Z.")
        object.__setattr__(self, "terms", normalized)

    @staticmethod
    def x(wire: int) -> "PauliString":
        return PauliString([(wire, "X")])

    @staticmethod
    def y(wire: int) -> "PauliString":
        return PauliString([(wire, "Y")])

    @staticmethod
    def z(wire: int) -> "PauliString":
        return PauliString([(wire, "Z")])

    def tensor(self, other: "PauliString") -> "PauliString":
        occupied = {wire for wire, _ in self.terms}
        for wire, _ in other.terms:
            if wire in occupied:
                raise ValueError("QuantumBridge PauliString tensor inputs cannot overlap wires.")
        return PauliString(self.terms + other.terms)

    def matrix(self, num_qubits: Optional[int] = None) -> np.ndarray:
        if num_qubits is None:
            num_qubits = 1 + max((wire for wire, _ in self.terms), default=0)
        term_map = dict(self.terms)
        out = np.array([[1]], dtype=complex)
        for wire in range(num_qubits):
            out = np.kron(out, pauli_matrix(term_map.get(wire, "I")))
        return out


@dataclass(frozen=True)
class Hamiltonian:
    """Weighted sum of PauliString observables."""

    terms: tuple[tuple[float, PauliString], ...]

    def __init__(self, terms: Iterable[tuple[Real, PauliString]]):
        normalized = []
        for coeff, pauli in terms:
            if not isinstance(pauli, PauliString):
                raise ValueError("QuantumBridge Hamiltonian terms require PauliString observables.")
            normalized.append((float(coeff), pauli))
        object.__setattr__(self, "terms", tuple(normalized))

    def __add__(self, other: "Hamiltonian") -> "Hamiltonian":
        return Hamiltonian(self.terms + other.terms)

    def __mul__(self, scalar: Real) -> "Hamiltonian":
        return Hamiltonian([(float(scalar) * coeff, pauli) for coeff, pauli in self.terms])

    __rmul__ = __mul__


def PauliX(wire: int) -> PauliString:
    return PauliString.x(wire)


def PauliY(wire: int) -> PauliString:
    return PauliString.y(wire)


def PauliZ(wire: int) -> PauliString:
    return PauliString.z(wire)


def pauli_matrix(label: str) -> np.ndarray:
    return {"I": I2, "X": PAULI_X, "Y": PAULI_Y, "Z": PAULI_Z}[label]


def expectation_pauli_string(state: np.ndarray, num_qubits: int, pauli: PauliString) -> float:
    op_state = state
    term_map = dict(pauli.terms)
    for wire in range(num_qubits):
        matrix = pauli_matrix(term_map.get(wire, "I"))
        op_state = apply_unitary(op_state, matrix, (wire,), num_qubits)
    value = np.vdot(state, op_state)
    return float(np.real_if_close(value))


def expectation_hamiltonian(state: np.ndarray, num_qubits: int, hamiltonian: Union[Hamiltonian, PauliString]) -> float:
    if isinstance(hamiltonian, PauliString):
        return expectation_pauli_string(state, num_qubits, hamiltonian)
    return float(sum(coeff * expectation_pauli_string(state, num_qubits, pauli) for coeff, pauli in hamiltonian.terms))


def observable_matrix(observable, num_qubits: int) -> np.ndarray:
    if isinstance(observable, PauliString):
        return observable.matrix(num_qubits)
    if isinstance(observable, Hamiltonian):
        out = np.zeros((1 << num_qubits, 1 << num_qubits), dtype=complex)
        for coeff, pauli in observable.terms:
            out += coeff * pauli.matrix(num_qubits)
        return out
    if hasattr(observable, "to_hamiltonian"):
        return observable_matrix(observable.to_hamiltonian(), num_qubits)
    if hasattr(observable, "to_matrix"):
        try:
            matrix = observable.to_matrix(num_qubits)
        except TypeError:
            matrix = observable.to_matrix()
        return np.asarray(matrix, dtype=complex)
    if hasattr(observable, "matrix"):
        try:
            matrix = observable.matrix(num_qubits=num_qubits)
        except TypeError:
            matrix = observable.matrix()
        return np.asarray(matrix, dtype=complex)
    return np.asarray(observable, dtype=complex)


def expectation_observable(state: np.ndarray, num_qubits: int, observable) -> complex:
    if isinstance(observable, (Hamiltonian, PauliString)) or hasattr(observable, "to_hamiltonian"):
        hamiltonian = observable.to_hamiltonian() if hasattr(observable, "to_hamiltonian") else observable
        return complex(expectation_hamiltonian(state, num_qubits, hamiltonian))
    matrix = observable_matrix(observable, num_qubits)
    if matrix.shape != (1 << num_qubits, 1 << num_qubits):
        raise ValueError("QuantumBridge observable matrix shape does not match state dimension.")
    return np.vdot(state, matrix @ state)


def variance_observable(state: np.ndarray, num_qubits: int, observable) -> float:
    matrix = observable_matrix(observable, num_qubits)
    if matrix.shape != (1 << num_qubits, 1 << num_qubits):
        raise ValueError("QuantumBridge observable matrix shape does not match state dimension.")
    mean = np.vdot(state, matrix @ state)
    second_moment = np.vdot(state, matrix @ (matrix @ state))
    return float(np.real_if_close(second_moment - mean * mean))
