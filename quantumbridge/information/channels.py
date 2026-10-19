# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from copy import deepcopy
from math import isqrt

import numpy as np

from quantumbridge.information.density_matrix import DensityMatrix
from quantumbridge.information.operator import Operator


def _is_power_of_two(value: int) -> bool:
    return value > 0 and not value & (value - 1)


def _num_qubits(input_dim: int, output_dim: int) -> int | None:
    if input_dim != output_dim or not _is_power_of_two(input_dim):
        return None
    return int(np.log2(input_dim))


def _dims_for_dimension(dimension: int) -> tuple[int, ...]:
    if _is_power_of_two(dimension):
        return (2,) * int(np.log2(dimension))
    return (dimension,)


def _operator_data(data) -> np.ndarray:
    if isinstance(data, Operator):
        return np.array(data.data, copy=True)
    if hasattr(data, "operations"):
        return Operator.from_circuit(data).data
    if hasattr(data, "to_matrix"):
        return np.asarray(data.to_matrix(), dtype=complex)
    if hasattr(data, "data") and not isinstance(data, np.ndarray):
        candidate = np.asarray(data.data, dtype=complex)
        if candidate.ndim == 2:
            return candidate
    return np.asarray(data, dtype=complex)


def _infer_superop_dimensions(shape: tuple[int, int]) -> tuple[int, int]:
    output_dim = isqrt(shape[0])
    input_dim = isqrt(shape[1])
    if output_dim * output_dim != shape[0] or input_dim * input_dim != shape[1]:
        raise ValueError("QuantumBridge SuperOp dimensions must be perfect squares.")
    return input_dim, output_dim


def _superop_to_choi(data: np.ndarray, input_dim: int, output_dim: int) -> np.ndarray:
    return (
        data.reshape(output_dim, output_dim, input_dim, input_dim)
        .transpose(3, 1, 2, 0)
        .reshape(input_dim * output_dim, input_dim * output_dim)
    )


def _choi_to_superop(data: np.ndarray, input_dim: int, output_dim: int) -> np.ndarray:
    return (
        data.reshape(input_dim, output_dim, input_dim, output_dim)
        .transpose(3, 1, 2, 0)
        .reshape(output_dim * output_dim, input_dim * input_dim)
    )


def _kraus_from_choi(
    data: np.ndarray,
    input_dim: int,
    output_dim: int,
    atol: float = 1e-12,
) -> tuple[np.ndarray, ...]:
    hermitian = (data + data.conj().T) / 2
    values, vectors = np.linalg.eigh(hermitian)
    if np.min(values) < -atol:
        raise ValueError("QuantumBridge cannot convert a non-CP channel to standard Kraus form.")
    operators = []
    for index in np.flatnonzero(values > atol):
        vector = np.sqrt(values[index]) * vectors[:, index]
        operators.append(vector.reshape((output_dim, input_dim), order="F"))
    if not operators:
        operators.append(np.zeros((output_dim, input_dim), dtype=complex))
    return tuple(operators)


def _pauli_basis(num_qubits: int) -> tuple[np.ndarray, ...]:
    one_qubit = (
        np.eye(2, dtype=complex),
        np.array([[0, 1], [1, 0]], dtype=complex),
        np.array([[0, -1j], [1j, 0]], dtype=complex),
        np.array([[1, 0], [0, -1]], dtype=complex),
    )
    basis = (np.array([[1]], dtype=complex),)
    for _ in range(num_qubits):
        basis = tuple(np.kron(prefix, pauli) for prefix in basis for pauli in one_qubit)
    return basis


def _pauli_change_matrix(num_qubits: int) -> np.ndarray:
    return np.column_stack([matrix.reshape(-1, order="F") for matrix in _pauli_basis(num_qubits)])


def _validate_qargs(qargs, num_qubits: int, width: int) -> tuple[int, ...]:
    normalized = tuple(int(qarg) for qarg in qargs)
    if len(normalized) != width:
        raise ValueError("QuantumBridge channel qargs width must match the channel width.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge channel qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge channel qargs are outside the target state.")
    return normalized


def _embed_operator(matrix: np.ndarray, qargs: tuple[int, ...], num_qubits: int) -> np.ndarray:
    identity = Operator(np.eye(1 << num_qubits, dtype=complex))
    return identity.compose(Operator(matrix), qargs=qargs).data


class _QuantumChannel:
    """Shared native channel operations across matrix representations."""

    _input_dim: int
    _output_dim: int

    @property
    def dim(self) -> tuple[int, int]:
        return (self._input_dim, self._output_dim)

    @property
    def num_qubits(self) -> int | None:
        return _num_qubits(self._input_dim, self._output_dim)

    def input_dims(self, qargs=None) -> tuple[int, ...]:
        dims = _dims_for_dimension(self._input_dim)
        if qargs is None:
            return dims
        if self.num_qubits is None:
            raise ValueError("QuantumBridge subsystem dimensions require a qubit channel.")
        selected = tuple(int(qarg) for qarg in qargs)
        _validate_qargs(selected, self.num_qubits, len(selected))
        return tuple(dims[qarg] for qarg in selected)

    def output_dims(self, qargs=None) -> tuple[int, ...]:
        dims = _dims_for_dimension(self._output_dim)
        if qargs is None:
            return dims
        if self.num_qubits is None:
            raise ValueError("QuantumBridge subsystem dimensions require a qubit channel.")
        selected = tuple(int(qarg) for qarg in qargs)
        _validate_qargs(selected, self.num_qubits, len(selected))
        return tuple(dims[qarg] for qarg in selected)

    def copy(self):
        return type(self)(self)

    def to_superop(self) -> "SuperOp":
        return SuperOp(self)

    def to_choi(self) -> "Choi":
        return Choi(self)

    def to_kraus(self) -> "Kraus":
        return Kraus(self)

    def to_ptm(self) -> "PTM":
        return PTM(self)

    def to_chi(self) -> "Chi":
        return Chi(self)

    def to_stinespring(self) -> "Stinespring":
        return Stinespring(self)

    def compose(self, other, qargs=None, front: bool = False):
        other_channel = SuperOp(other)
        if qargs is not None:
            if self.num_qubits is None or other_channel.num_qubits is None:
                raise ValueError("QuantumBridge subsystem channel composition requires qubit channels.")
            normalized = _validate_qargs(qargs, self.num_qubits, other_channel.num_qubits)
            other_channel = Kraus(
                tuple(
                    _embed_operator(op, normalized, self.num_qubits)
                    for op in other_channel.to_kraus().data
                )
            ).to_superop()

        this = self.to_superop()
        if front:
            if other_channel._output_dim != this._input_dim:
                raise ValueError("QuantumBridge front composition has incompatible channel dimensions.")
            result = this.data @ other_channel.data
            input_dim = other_channel._input_dim
            output_dim = this._output_dim
        else:
            if this._output_dim != other_channel._input_dim:
                raise ValueError("QuantumBridge channel composition has incompatible dimensions.")
            result = other_channel.data @ this.data
            input_dim = this._input_dim
            output_dim = other_channel._output_dim
        return type(self)(SuperOp._from_matrix(result, input_dim, output_dim))

    def dot(self, other, qargs=None):
        return self.compose(other, qargs=qargs, front=True)

    def tensor(self, other):
        other_kraus = Kraus(other)
        this_kraus = self.to_kraus()
        operators = tuple(
            np.kron(left, right)
            for left in this_kraus.data
            for right in other_kraus.data
        )
        return type(self)(Kraus(operators))

    def expand(self, other):
        return type(self)(other).tensor(self)

    def power(self, n: int):
        if not isinstance(n, int):
            raise ValueError("QuantumBridge channel power requires an integer exponent.")
        if self._input_dim != self._output_dim:
            raise ValueError("QuantumBridge channel power requires equal input and output dimensions.")
        powered = np.linalg.matrix_power(self.to_superop().data, n)
        return type(self)(SuperOp._from_matrix(powered, self._input_dim, self._output_dim))

    def tensorpower(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("QuantumBridge channel tensorpower requires a non-negative integer exponent.")
        if n == 0:
            return type(self)(Operator(np.ones((1, 1), dtype=complex)))
        result = self.copy()
        for _ in range(1, n):
            result = result.tensor(self)
        return result

    def adjoint(self):
        matrix = self.to_superop().data.conj().T
        return type(self)(SuperOp._from_matrix(matrix, self._output_dim, self._input_dim))

    def conjugate(self):
        matrix = np.conjugate(self.to_superop().data)
        return type(self)(SuperOp._from_matrix(matrix, self._input_dim, self._output_dim))

    def transpose(self):
        return self.conjugate().adjoint()

    def is_cp(self, atol: float = 1e-8, rtol: float = 1e-5) -> bool:
        choi = self.to_choi().data
        if not np.allclose(choi, choi.conj().T, atol=atol, rtol=rtol):
            return False
        hermitian = (choi + choi.conj().T) / 2
        return bool(np.min(np.linalg.eigvalsh(hermitian)) >= -atol)

    def is_tp(self, atol: float = 1e-8, rtol: float = 1e-5) -> bool:
        choi = self.to_choi().data.reshape(
            self._input_dim,
            self._output_dim,
            self._input_dim,
            self._output_dim,
        )
        partial = np.trace(choi, axis1=1, axis2=3)
        return bool(np.allclose(partial, np.eye(self._input_dim), atol=atol, rtol=rtol))

    def is_cptp(self, atol: float = 1e-8, rtol: float = 1e-5) -> bool:
        return self.is_cp(atol=atol, rtol=rtol) and self.is_tp(atol=atol, rtol=rtol)

    def evolve(self, state, qargs=None) -> DensityMatrix:
        rho = state.data if isinstance(state, DensityMatrix) else np.asarray(state, dtype=complex)
        if rho.ndim == 1:
            rho = np.outer(rho, rho.conj())
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
            raise ValueError("QuantumBridge channel evolution requires a statevector or density matrix.")

        operators = self.to_kraus().data
        if qargs is not None:
            state_dim = rho.shape[0]
            if not _is_power_of_two(state_dim) or self.num_qubits is None:
                raise ValueError("QuantumBridge subsystem channel evolution requires qubit dimensions.")
            state_qubits = int(np.log2(state_dim))
            normalized = _validate_qargs(qargs, state_qubits, self.num_qubits)
            operators = tuple(_embed_operator(op, normalized, state_qubits) for op in operators)
        elif rho.shape[0] != self._input_dim:
            raise ValueError("QuantumBridge state and channel input dimensions do not match.")

        output = sum(op @ rho @ op.conj().T for op in operators)
        return DensityMatrix(output)

    def to_operator(self) -> Operator:
        operators = self.to_kraus().data
        if len(operators) != 1:
            raise ValueError("QuantumBridge channel is not representable by one operator.")
        operator = Operator(operators[0])
        if not operator.is_unitary():
            raise ValueError("QuantumBridge channel operator is not unitary.")
        return operator

    def __xor__(self, n: int):
        return self.tensorpower(n)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        copied = type(self)(deepcopy(self.data, memo))
        memo[id(self)] = copied
        return copied


class Kraus(_QuantumChannel):
    """Standard Kraus representation of a completely positive quantum map."""

    def __init__(self, data):
        if isinstance(data, Kraus):
            operators = tuple(np.array(op, copy=True) for op in data.data)
        elif isinstance(data, _QuantumChannel):
            choi = data.to_superop().to_choi()
            operators = _kraus_from_choi(choi.data, choi._input_dim, choi._output_dim)
        elif isinstance(data, Operator) or hasattr(data, "operations") or hasattr(data, "to_matrix"):
            operators = (_operator_data(data),)
        elif isinstance(data, np.ndarray) and data.ndim == 2:
            operators = (np.asarray(data, dtype=complex),)
        else:
            operators = tuple(np.asarray(operator, dtype=complex) for operator in data)

        if not operators:
            raise ValueError("QuantumBridge Kraus channel requires at least one operator.")
        shape = operators[0].shape
        if len(shape) != 2:
            raise ValueError("QuantumBridge Kraus operators must be matrices.")
        if any(operator.shape != shape for operator in operators):
            raise ValueError("QuantumBridge Kraus operators must have equal shape.")
        self.data = operators
        self._output_dim, self._input_dim = shape

    @classmethod
    def from_channel(cls, channel) -> "Kraus":
        return cls(channel)

    def to_kraus(self) -> "Kraus":
        return self.copy()

    def to_superop(self) -> "SuperOp":
        matrix = sum(np.kron(operator.conj(), operator) for operator in self.data)
        return SuperOp._from_matrix(matrix, self._input_dim, self._output_dim)

    def to_choi(self) -> "Choi":
        matrix = sum(
            np.outer(
                operator.reshape(-1, order="F"),
                operator.reshape(-1, order="F").conj(),
            )
            for operator in self.data
        )
        return Choi._from_matrix(matrix, self._input_dim, self._output_dim)


class SuperOp(_QuantumChannel):
    """Column-vectorized matrix representation of a quantum channel."""

    def __init__(self, data):
        if isinstance(data, SuperOp):
            self.data = np.array(data.data, copy=True)
            self._input_dim = data._input_dim
            self._output_dim = data._output_dim
            return
        if isinstance(data, _QuantumChannel):
            converted = data.to_superop()
            self.data = np.array(converted.data, copy=True)
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        if isinstance(data, Operator) or hasattr(data, "operations") or hasattr(data, "to_matrix"):
            converted = self.from_operator(data)
            self.data = converted.data
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        matrix = np.asarray(data, dtype=complex)
        if matrix.ndim != 2:
            raise ValueError("QuantumBridge SuperOp data must be a matrix.")
        self._input_dim, self._output_dim = _infer_superop_dimensions(matrix.shape)
        self.data = matrix

    @classmethod
    def _from_matrix(cls, matrix: np.ndarray, input_dim: int, output_dim: int) -> "SuperOp":
        instance = cls.__new__(cls)
        instance.data = np.asarray(matrix, dtype=complex)
        instance._input_dim = int(input_dim)
        instance._output_dim = int(output_dim)
        return instance

    @classmethod
    def from_operator(cls, operator) -> "SuperOp":
        matrix = _operator_data(operator)
        if matrix.ndim != 2:
            raise ValueError("QuantumBridge SuperOp operator input must be a matrix.")
        output_dim, input_dim = matrix.shape
        return cls._from_matrix(np.kron(matrix.conj(), matrix), input_dim, output_dim)

    def to_superop(self) -> "SuperOp":
        return self.copy()

    def to_choi(self) -> "Choi":
        matrix = _superop_to_choi(self.data, self._input_dim, self._output_dim)
        return Choi._from_matrix(matrix, self._input_dim, self._output_dim)


class Choi(_QuantumChannel):
    """Choi-matrix representation of a quantum channel."""

    def __init__(self, data):
        if isinstance(data, Choi):
            self.data = np.array(data.data, copy=True)
            self._input_dim = data._input_dim
            self._output_dim = data._output_dim
            return
        if isinstance(data, _QuantumChannel):
            converted = data.to_superop().to_choi()
            self.data = np.array(converted.data, copy=True)
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        if isinstance(data, Operator) or hasattr(data, "operations") or hasattr(data, "to_matrix"):
            converted = Kraus(data).to_choi()
            self.data = converted.data
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        matrix = np.asarray(data, dtype=complex)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("QuantumBridge Choi data must be a square matrix.")
        channel_dim = matrix.shape[0]
        inferred = isqrt(channel_dim)
        if inferred * inferred == channel_dim:
            self._input_dim = inferred
            self._output_dim = inferred
        else:
            self._input_dim = channel_dim
            self._output_dim = 1
        self.data = matrix

    @classmethod
    def _from_matrix(cls, matrix: np.ndarray, input_dim: int, output_dim: int) -> "Choi":
        instance = cls.__new__(cls)
        instance.data = np.asarray(matrix, dtype=complex)
        instance._input_dim = int(input_dim)
        instance._output_dim = int(output_dim)
        return instance

    @classmethod
    def from_channel(cls, channel) -> "Choi":
        return cls(channel)

    def to_choi(self) -> "Choi":
        return self.copy()

    def to_superop(self) -> SuperOp:
        matrix = _choi_to_superop(self.data, self._input_dim, self._output_dim)
        return SuperOp._from_matrix(matrix, self._input_dim, self._output_dim)


class PTM(_QuantumChannel):
    """Pauli-transfer-matrix representation for equal-dimension qubit channels."""

    def __init__(self, data):
        if isinstance(data, PTM):
            self.data = np.array(data.data, copy=True)
            self._input_dim = data._input_dim
            self._output_dim = data._output_dim
            return
        if (
            isinstance(data, _QuantumChannel)
            or isinstance(data, Operator)
            or hasattr(data, "operations")
            or hasattr(data, "to_matrix")
        ):
            channel = data if isinstance(data, _QuantumChannel) else Kraus(data)
            converted = self.from_superop(channel.to_superop())
            self.data = converted.data
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        matrix = np.asarray(data, dtype=complex)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("QuantumBridge PTM data must be square.")
        dimension = isqrt(matrix.shape[0])
        if dimension * dimension != matrix.shape[0] or not _is_power_of_two(dimension):
            raise ValueError("QuantumBridge PTM data must represent an n-qubit channel.")
        self.data = np.real_if_close(matrix)
        self._input_dim = dimension
        self._output_dim = dimension

    @classmethod
    def from_superop(cls, channel: SuperOp) -> "PTM":
        if channel._input_dim != channel._output_dim or not _is_power_of_two(channel._input_dim):
            raise ValueError("QuantumBridge PTM requires an equal-dimension qubit channel.")
        num_qubits = int(np.log2(channel._input_dim))
        change = _pauli_change_matrix(num_qubits)
        matrix = change.conj().T @ channel.data @ change / channel._input_dim
        return cls(np.real_if_close(matrix))

    def to_superop(self) -> SuperOp:
        change = _pauli_change_matrix(self.num_qubits or 0)
        matrix = change @ self.data @ change.conj().T / self._input_dim
        return SuperOp._from_matrix(matrix, self._input_dim, self._output_dim)


class Chi(_QuantumChannel):
    """Pauli-basis process-matrix representation for n-qubit channels."""

    def __init__(self, data):
        if isinstance(data, Chi):
            self.data = np.array(data.data, copy=True)
            self._input_dim = data._input_dim
            self._output_dim = data._output_dim
            return
        if (
            isinstance(data, _QuantumChannel)
            or isinstance(data, Operator)
            or hasattr(data, "operations")
            or hasattr(data, "to_matrix")
        ):
            channel = data if isinstance(data, _QuantumChannel) else Kraus(data)
            converted = self.from_choi(channel.to_choi())
            self.data = converted.data
            self._input_dim = converted._input_dim
            self._output_dim = converted._output_dim
            return
        matrix = np.asarray(data, dtype=complex)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("QuantumBridge Chi data must be square.")
        dimension = isqrt(matrix.shape[0])
        if dimension * dimension != matrix.shape[0] or not _is_power_of_two(dimension):
            raise ValueError("QuantumBridge Chi data must represent an n-qubit channel.")
        self.data = matrix
        self._input_dim = dimension
        self._output_dim = dimension

    @classmethod
    def from_choi(cls, channel: Choi) -> "Chi":
        if channel._input_dim != channel._output_dim or not _is_power_of_two(channel._input_dim):
            raise ValueError("QuantumBridge Chi requires an equal-dimension qubit channel.")
        num_qubits = int(np.log2(channel._input_dim))
        change = _pauli_change_matrix(num_qubits)
        matrix = change.conj().T @ channel.data @ change / channel._input_dim
        return cls(matrix)

    def to_choi(self) -> Choi:
        change = _pauli_change_matrix(self.num_qubits or 0)
        matrix = change @ self.data @ change.conj().T / self._input_dim
        return Choi._from_matrix(matrix, self._input_dim, self._output_dim)

    def to_superop(self) -> SuperOp:
        return self.to_choi().to_superop()


class Stinespring(_QuantumChannel):
    """Stinespring isometry representation of a completely positive map."""

    def __init__(self, data):
        if isinstance(data, Stinespring):
            self.data = np.array(data.data, copy=True)
            self._input_dim = data._input_dim
            self._output_dim = data._output_dim
            self._environment_dim = data._environment_dim
            return
        if isinstance(data, _QuantumChannel):
            kraus = data.to_kraus()
            environment_dim = len(kraus.data)
            stacked = np.stack(kraus.data, axis=1).reshape(
                kraus._output_dim * environment_dim,
                kraus._input_dim,
            )
            self.data = stacked
            self._input_dim = kraus._input_dim
            self._output_dim = kraus._output_dim
            self._environment_dim = environment_dim
            return
        matrix = _operator_data(data)
        if matrix.ndim != 2:
            raise ValueError("QuantumBridge Stinespring data must be a matrix.")
        self.data = matrix
        self._input_dim = matrix.shape[1]
        self._output_dim = matrix.shape[1]
        if matrix.shape[0] % self._output_dim:
            raise ValueError("QuantumBridge cannot infer Stinespring output dimensions.")
        self._environment_dim = matrix.shape[0] // self._output_dim

    def to_kraus(self) -> Kraus:
        tensor = self.data.reshape(
            self._output_dim,
            self._environment_dim,
            self._input_dim,
        )
        return Kraus(tuple(tensor[:, index, :] for index in range(self._environment_dim)))

    def to_superop(self) -> SuperOp:
        return self.to_kraus().to_superop()

    def to_choi(self) -> Choi:
        return self.to_kraus().to_choi()


__all__ = ["Chi", "Choi", "Kraus", "PTM", "Stinespring", "SuperOp"]
