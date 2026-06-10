# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from numbers import Number

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import apply_unitary, expectation_hamiltonian, probabilities_from_state


def _validate_qargs(qargs, num_qubits: int) -> tuple[int, ...]:
    normalized = tuple(range(num_qubits) if qargs is None else (int(qarg) for qarg in qargs))
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge Statevector qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge Statevector qargs are outside this state.")
    return normalized


def _index_bits(index: int, qargs: tuple[int, ...], num_qubits: int) -> str:
    return "".join(str((index >> (num_qubits - 1 - qarg)) & 1) for qarg in qargs)


class Statevector:
    def __init__(self, data, normalize: bool = False):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 1:
            raise ValueError("QuantumBridge Statevector data must be one-dimensional.")
        if len(self.data) == 0 or len(self.data) & (len(self.data) - 1):
            raise ValueError("QuantumBridge Statevector dimension must be a power of two.")
        if normalize:
            norm = np.linalg.norm(self.data)
            if norm == 0:
                raise ValueError("QuantumBridge cannot normalize a zero Statevector.")
            self.data = self.data / norm
        self.num_qubits = int(np.log2(len(self.data)))

    @property
    def dim(self) -> int:
        return len(self.data)

    def dims(self, qargs=None) -> tuple[int, ...]:
        return (2,) * len(_validate_qargs(qargs, self.num_qubits))

    @classmethod
    def from_circuit(cls, circuit) -> "Statevector":
        return cls(StatevectorDevice().statevector(circuit))

    @classmethod
    def from_int(cls, index: int, dims) -> "Statevector":
        if isinstance(dims, int):
            dim = int(dims)
        else:
            dim = int(np.prod(tuple(dims)))
        if dim <= 0 or dim & (dim - 1):
            raise ValueError("QuantumBridge Statevector.from_int dims must describe a power-of-two dimension.")
        if index < 0 or index >= dim:
            raise ValueError("QuantumBridge Statevector.from_int index is outside dims.")
        data = np.zeros(dim, dtype=complex)
        data[int(index)] = 1.0
        return cls(data)

    @classmethod
    def from_label(cls, label: str) -> "Statevector":
        if any(bit not in "01" for bit in label):
            raise ValueError("QuantumBridge Statevector labels may contain only 0 and 1.")
        data = np.zeros(1 << len(label), dtype=complex)
        data[int(label, 2)] = 1.0
        return cls(data)

    def is_valid(self, atol: float = 1e-10) -> bool:
        return bool(np.isclose(np.vdot(self.data, self.data), 1.0, atol=atol))

    def probabilities(self, wires=None) -> dict[str, float]:
        return probabilities_from_state(self.data, self.num_qubits, wires)

    def probabilities_dict(self, qargs=None) -> dict[str, float]:
        return self.probabilities(qargs)

    def expectation_value(self, observable, qargs=None) -> complex:
        from quantumbridge.information.operator import Operator

        if hasattr(observable, "to_hamiltonian"):
            return expectation_hamiltonian(self.data, self.num_qubits, observable.to_hamiltonian())
        matrix = observable.data if hasattr(observable, "data") else np.asarray(observable, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            matrix = Operator(np.eye(len(self.data), dtype=complex)).compose(Operator(matrix), qargs=qargs_tuple).data
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge observable dimension must match Statevector dimension.")
        return np.vdot(self.data, matrix @ self.data)

    def evolve(self, operator, qargs=None) -> "Statevector":
        from quantumbridge.information.operator import Operator

        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        matrix = op.data if isinstance(op, Operator) else np.asarray(op, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            dim = 1 << len(qargs_tuple)
            if matrix.shape != (dim, dim):
                raise ValueError("QuantumBridge subsystem evolution operator dimension must match qargs.")
            return Statevector(apply_unitary(self.data, matrix, qargs_tuple, self.num_qubits))
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge evolution operator dimension must match Statevector dimension.")
        return Statevector(matrix @ self.data)

    def tensor(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(np.kron(self.data, other_state.data))

    def expand(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(np.kron(other_state.data, self.data))

    def reverse_qargs(self) -> "Statevector":
        data = np.zeros_like(self.data)
        for source, amplitude in enumerate(self.data):
            bits = format(source, f"0{self.num_qubits}b")
            data[int(bits[::-1], 2)] = amplitude
        return Statevector(data)

    def inner(self, other) -> complex:
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        if len(self.data) != len(other_state.data):
            raise ValueError("QuantumBridge Statevector inner product requires equal dimensions.")
        return np.vdot(self.data, other_state.data)

    def equiv(self, other, atol: float = 1e-10) -> bool:
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        if len(self.data) != len(other_state.data):
            return False
        if np.allclose(self.data, other_state.data, atol=atol):
            return True
        nonzero = np.argwhere(np.abs(other_state.data) > atol)
        if nonzero.size == 0:
            return bool(np.allclose(self.data, other_state.data, atol=atol))
        index = int(nonzero[0][0])
        phase = self.data[index] / other_state.data[index]
        if abs(abs(phase) - 1.0) > atol:
            return False
        return bool(np.allclose(self.data, phase * other_state.data, atol=atol))

    def sample_counts(self, shots: int, seed: int | None = None) -> dict[str, int]:
        if shots < 0:
            raise ValueError("QuantumBridge sample_counts shots cannot be negative.")
        rng = np.random.default_rng(seed)
        labels = [format(index, f"0{self.num_qubits}b") for index in range(len(self.data))]
        probs = np.array([abs(value) ** 2 for value in self.data], dtype=float)
        probs = probs / probs.sum()
        draws = rng.choice(len(labels), size=shots, p=probs)
        counts = {label: 0 for label in labels}
        for draw in draws:
            counts[labels[int(draw)]] += 1
        return {key: value for key, value in counts.items() if value}

    def sample_memory(self, shots: int, qargs=None, seed: int | None = None) -> list[str]:
        if shots < 0:
            raise ValueError("QuantumBridge sample_memory shots cannot be negative.")
        qargs_tuple = _validate_qargs(qargs, self.num_qubits)
        labels = sorted(self.probabilities(qargs_tuple))
        probs_dict = self.probabilities(qargs_tuple)
        probs = np.array([probs_dict[label] for label in labels], dtype=float)
        probs = probs / probs.sum()
        rng = np.random.default_rng(seed)
        draws = rng.choice(len(labels), size=shots, p=probs)
        return [labels[int(draw)] for draw in draws]

    def measure(self, qargs=None, seed: int | None = None) -> tuple[str, "Statevector"]:
        qargs_tuple = _validate_qargs(qargs, self.num_qubits)
        memory = self.sample_memory(1, qargs=qargs_tuple, seed=seed)
        outcome = memory[0] if memory else ""
        collapsed = np.array(self.data, copy=True)
        for index in range(len(collapsed)):
            if _index_bits(index, qargs_tuple, self.num_qubits) != outcome:
                collapsed[index] = 0.0
        norm = np.linalg.norm(collapsed)
        if norm == 0:
            raise ValueError("QuantumBridge measurement produced a zero-probability collapse.")
        return outcome, Statevector(collapsed / norm)

    def to_operator(self):
        from quantumbridge.information.operator import Operator

        return Operator(np.outer(self.data, np.conjugate(self.data)))

    def copy(self) -> "Statevector":
        return Statevector(np.array(self.data, copy=True))

    def to_dict(self, decimals: int | None = None) -> dict[str, complex]:
        out = {}
        for index, amplitude in enumerate(self.data):
            if abs(amplitude) <= 1e-15:
                continue
            if decimals is not None:
                amplitude = np.round(amplitude, decimals=decimals)
            out[format(index, f"0{self.num_qubits}b")] = complex(amplitude)
        return out

    def __len__(self) -> int:
        return len(self.data)

    def __mul__(self, scalar):
        if not isinstance(scalar, Number):
            return NotImplemented
        return Statevector(self.data * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if not isinstance(scalar, Number):
            return NotImplemented
        return Statevector(self.data / scalar)

    def __eq__(self, other) -> bool:
        try:
            return self.equiv(other)
        except Exception:
            return False
