# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from cmath import phase as scalar_phase, rect
from math import isfinite
from numbers import Number

import numpy as np

from quantumbridge.core.operations import Instruction
from quantumbridge.utils.math import apply_unitary, gate_matrix
from .state_dimensions import state_dimensions, qubit_count, subsystem_positions, basis_digits, basis_index


def _validate_qargs(qargs, num_qubits: int, width: int) -> tuple[int, ...]:
    normalized = tuple(int(qarg) for qarg in qargs)
    if len(normalized) != width:
        raise ValueError("QuantumBridge Operator qargs width must match the composed operator.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge Operator qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge Operator qargs are outside this operator.")
    return normalized


def _index_to_bits(index: int, num_qubits: int) -> list[int]:
    return [(index >> (num_qubits - 1 - wire)) & 1 for wire in range(num_qubits)]


def _bits_to_index(bits: list[int] | tuple[int, ...]) -> int:
    out = 0
    for bit in bits:
        out = (out << 1) | int(bit)
    return out


def _expand_subsystem_operator(data: np.ndarray, qargs: tuple[int, ...], num_qubits: int) -> np.ndarray:
    size = 1 << num_qubits
    sub_dim = 1 << len(qargs)
    from quantumbridge.execution.resource_context import current_resources
    if current_resources() is None:out = np.zeros((size, size), dtype=complex)
    else:
        from quantumbridge.execution.array_reservations import numeric_array, numeric_shape
        from quantumbridge.execution import mps_arrays as arrays
        if numeric_shape(data)!=(sub_dim,sub_dim):raise ValueError("Subsystem operator shape does not match qargs.")
        data=numeric_array(data,category="subsystem_operator_input")
        out=arrays.filled("subsystem_operator_expansion",(size,size),complex,0)
    for col in range(size):
        basis_bits = _index_to_bits(col, num_qubits)
        sub_col = _bits_to_index([basis_bits[qarg] for qarg in qargs])
        for sub_row in range(sub_dim):
            row_bits = basis_bits.copy()
            replacement_bits = _index_to_bits(sub_row, len(qargs))
            for offset, qarg in enumerate(qargs):
                row_bits[qarg] = replacement_bits[offset]
            row = _bits_to_index(row_bits)
            out[row, col] += data[sub_row, sub_col]
    return out


def _reverse_qubit_order(data: np.ndarray, num_qubits: int) -> np.ndarray:
    from quantumbridge.execution.array_ownership import copied_array
    size = 1 << num_qubits
    output=copied_array(data,category="operator_reverse")
    order=tuple(_bits_to_index(list(reversed(_index_to_bits(index,num_qubits)))) for index in range(size))
    for row,destination in enumerate(order):
        for column,target in enumerate(order):output[destination,target]=data[row,column]
    return output


class Operator:
    """Dense linear operator with a Qiskit quantum_info-like core API."""

    __array_priority__ = 1000

    def __init__(self, data, input_dims=None, output_dims=None):
        from quantumbridge.execution.resource_context import current_resources
        scope=current_resources()
        if scope is None:
            self.data = np.asarray(data, dtype=complex)
            shape=self.data.shape
        else:
            from quantumbridge.execution.array_reservations import numeric_array, numeric_shape
            shape=numeric_shape(data)
        if len(shape)!=2 or not all(shape):
            raise ValueError("QuantumBridge Operator data must be a nonempty matrix.")
        self._input_dims=state_dimensions(shape[1] if input_dims is None else input_dims,size=shape[1])
        self._output_dims=state_dimensions(shape[0] if output_dims is None else output_dims,size=shape[0])
        self.num_qubits=qubit_count(self._input_dims) if self._input_dims==self._output_dims else None
        if scope is not None:self.data=numeric_array(data,category="operator_input_conversion")

    @property
    def dim(self) -> tuple[int, int]:
        return (self.data.shape[1], self.data.shape[0])

    def input_dims(self, qargs=None) -> tuple[int, ...]:
        return tuple(self._input_dims[position] for position in subsystem_positions(qargs,len(self._input_dims)))

    def output_dims(self, qargs=None) -> tuple[int, ...]:
        return tuple(self._output_dims[position] for position in subsystem_positions(qargs,len(self._output_dims)))

    @classmethod
    def from_label(cls, label: str) -> "Operator":
        if type(label) is not str or any(char not in "IXYZ" for char in label.upper()):
            raise ValueError("QuantumBridge Operator labels may contain only I, X, Y, Z.")
        from quantumbridge.execution import mps_arrays as arrays
        label=label.upper()
        out=arrays.filled("operator_pauli_label",(1<<len(label),)*2,complex,0)
        for column in range(len(out)):
            row,amplitude=column,1.+0j
            for wire,symbol in enumerate(label):
                mask=1<<(len(label)-1-wire)
                bit=bool(column&mask)
                if symbol in "XY":row^=mask
                if symbol=="Y":amplitude*=(-1j if bit else 1j)
                elif symbol=="Z" and bit:amplitude=-amplitude
            out[row,column]=amplitude
        return cls(out)

    @classmethod
    def from_circuit(cls, circuit) -> "Operator":
        if circuit.has_dynamic_operations:
            raise ValueError("QuantumBridge Operator cannot represent measurement, reset or classical control flow as a unitary.")
        size = 1 << circuit.num_qubits
        from quantumbridge.execution.resource_context import current_resources
        scope=current_resources()
        if scope is None:matrix = np.zeros((size, size), dtype=complex)
        else:
            from quantumbridge.execution import mps_arrays as arrays
            matrix=arrays.filled("circuit_operator_output",(size,size),complex,0)
        for col in range(size):
            state = np.zeros(size, dtype=complex) if scope is None else arrays.filled("circuit_operator_column",(size,),complex,0)
            state[col] = 1.0
            for op in circuit.operations:
                if op.metadata.get("directive") and op.name in {"barrier", "delay"}:
                    continue
                gate = gate_matrix(op.name, op.params, op.metadata)
                state = apply_unitary(state, gate, op.controls + op.targets, circuit.num_qubits)
            np.multiply(state,np.exp(1j*float(circuit.global_phase)),out=matrix[:,col])
        return cls(matrix)

    def is_unitary(self, atol: float = 1e-10) -> bool:
        if self.data.shape[0]!=self.data.shape[1]:return False
        from quantumbridge.execution.resource_context import current_resources
        if current_resources() is not None:
            from quantumbridge.utils.math import validate_unitary_matrix
            return validate_unitary_matrix(self.data,atol=atol,rtol=1e-5)
        eye = np.eye(self.data.shape[0], dtype=complex)
        return bool(np.allclose(self.data.conj().T @ self.data, eye, atol=atol))

    def adjoint(self) -> "Operator":
        return self._new(self.conjugate().data.T,input_dims=self._output_dims,output_dims=self._input_dims)

    def transpose(self) -> "Operator":
        return self._new(self.data.T,input_dims=self._output_dims,output_dims=self._input_dims)

    def conjugate(self) -> "Operator":
        copied=self.copy()
        np.conjugate(copied.data,out=copied.data)
        return copied

    def copy(self) -> "Operator":
        from quantumbridge.execution.array_ownership import copied_array
        return self._new(copied_array(self.data,category="operator_copy"))

    def _new(self, data, *, input_dims=None, output_dims=None):
        return Operator(data,input_dims=self._input_dims if input_dims is None else input_dims,
                        output_dims=self._output_dims if output_dims is None else output_dims)

    def compose(self, other: "Operator", qargs=None, front: bool = False) -> "Operator":
        if qargs is not None and self.num_qubits is None:
            from quantumbridge.core.classical import UnsupportedFeature
            raise UnsupportedFeature("mixed_radix_operator_compose","Mapped operator-on-operator composition is not mixed-radix state evolution.")
        if not isinstance(other,Operator):
            dims=self._output_dims if front else self._input_dims
            other=Operator(other) if qargs is not None else Operator(other,input_dims=dims,output_dims=dims)
        other_data = other.data
        if qargs is not None:
            if other.num_qubits is None:
                from quantumbridge.core.classical import UnsupportedFeature
                raise UnsupportedFeature("mixed_radix_operator_compose")
            qargs_tuple = _validate_qargs(qargs, self.num_qubits, other.num_qubits)
            other_data = _expand_subsystem_operator(other.data, qargs_tuple, self.num_qubits)
            incoming,outgoing=self._input_dims,self._output_dims
        else:
            if (other._input_dims!=self._output_dims if front else self._input_dims!=other._output_dims):
                raise ValueError("QuantumBridge Operator composition subsystem dimensions do not match.")
            incoming,outgoing=(self._input_dims,other._output_dims) if front else (other._input_dims,self._output_dims)
        from quantumbridge.execution.resource_context import current_resources
        if current_resources() is not None:
            from quantumbridge.execution import mps_arrays as arrays
            return self._new(arrays.contracted(other_data,self.data) if front else arrays.contracted(self.data,other_data),input_dims=incoming,output_dims=outgoing)
        return self._new(other_data @ self.data if front else self.data @ other_data,input_dims=incoming,output_dims=outgoing)

    def dot(self, other: "Operator", qargs=None) -> "Operator":
        return self.compose(other, qargs=qargs)

    def tensor(self, other: "Operator") -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        incoming,outgoing=self._input_dims+other._input_dims,self._output_dims+other._output_dims
        from quantumbridge.execution.resource_context import current_resources
        if current_resources() is not None:
            from quantumbridge.execution import mps_arrays as arrays
            from quantumbridge.execution.array_reservations import kron_into
            out=arrays.owned("operator_tensor",(self.data.shape[0]*other.data.shape[0],self.data.shape[1]*other.data.shape[1]),complex)
            kron_into(self.data,other.data,out,scope=current_resources())
            return self._new(out,input_dims=incoming,output_dims=outgoing)
        return self._new(np.kron(self.data, other.data),input_dims=incoming,output_dims=outgoing)

    def expand(self, other: "Operator") -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        return other.tensor(self)

    def power(self, n: int) -> "Operator":
        if not isinstance(n, int):
            raise ValueError("QuantumBridge Operator power requires an integer exponent.")
        if self._input_dims!=self._output_dims:
            raise ValueError("Operator powers require matching input and output subsystems.")
        from quantumbridge.execution import mps_arrays as arrays
        return self._new(arrays.matrix_power(self.data, n))

    def tensorpower(self, n: int) -> "Operator":
        if not isinstance(n, int) or n < 0:
            raise ValueError("QuantumBridge Operator tensorpower requires a non-negative integer exponent.")
        out = Operator.from_label("")
        for _ in range(n):
            out = out.tensor(self)
        return out

    def reverse_qargs(self) -> "Operator":
        if self.num_qubits is not None:return self._new(_reverse_qubit_order(self.data,self.num_qubits))
        from quantumbridge.execution.array_ownership import copied_array
        data=copied_array(self.data,category="operator_reverse")
        rows=tuple(basis_index(basis_digits(index,self._output_dims)[::-1],self._output_dims[::-1]) for index in range(self.data.shape[0]))
        columns=tuple(basis_index(basis_digits(index,self._input_dims)[::-1],self._input_dims[::-1]) for index in range(self.data.shape[1]))
        for row,target_row in enumerate(rows):
            for column,target_column in enumerate(columns):data[target_row,target_column]=self.data[row,column]
        return self._new(data,input_dims=self._input_dims[::-1],output_dims=self._output_dims[::-1])

    def is_identity(self, atol: float = 1e-10) -> bool:
        if self.data.shape[0]!=self.data.shape[1]:return False
        return bool(np.allclose(self.data, np.eye(self.data.shape[0], dtype=complex), atol=atol))

    def reshape(self, input_dims=None, output_dims=None, num_qubits: int | None = None) -> "Operator":
        incoming=self._input_dims if input_dims is None else state_dimensions(input_dims,size=self.data.shape[1])
        outgoing=self._output_dims if output_dims is None else state_dimensions(output_dims,size=self.data.shape[0])
        count=qubit_count(incoming) if incoming==outgoing else None
        if num_qubits is not None and int(num_qubits)!=count:
            raise ValueError("QuantumBridge Operator reshape cannot change dense matrix size.")
        from quantumbridge.execution.array_ownership import copied_array
        return self._new(copied_array(self.data,category="operator_copy"),input_dims=incoming,output_dims=outgoing)

    def equiv(self, other, atol: float = 1e-10) -> bool:
        from quantumbridge.execution.resource_context import current_resources
        first=self.data
        other_data = other.data if isinstance(other, Operator) else other
        if current_resources() is not None:
            from quantumbridge.execution.array_reservations import numeric_array
            first=numeric_array(first,category="operator_equiv_input")
            other_data=numeric_array(other_data,category="operator_equiv_input")
        else:other_data=np.asarray(other_data,dtype=complex)
        if first.shape != other_data.shape:
            return False
        if not isfinite(atol) or atol<0:raise ValueError("Operator equivalence tolerance must be finite and nonnegative.")
        pivot,largest=0,0.
        for index,(a,b) in enumerate(zip(first.flat,other_data.flat)):
            a,b=complex(a),complex(b)
            if not all(isfinite(value) for value in (a.real,a.imag,b.real,b.imag)):return False
            size=max(abs(b.real),abs(b.imag))
            if size>largest:pivot,largest=index,size
        def matches(phase):
            for a,b in zip(first.flat,other_data.flat):
                a,b=complex(a),complex(b)
                scale=max(1.,abs(a.real),abs(a.imag),abs(b.real),abs(b.imag))
                reference=(b/scale)*phase
                if abs(a/scale-reference)>atol/scale+1e-5*abs(reference):return False
            return True
        if matches(1.):return True
        if not largest:return False
        # A largest-component pivot avoids amplifying noise in a tiny entry.
        phase=rect(1.,scalar_phase(complex(first.flat[pivot]))-scalar_phase(complex(other_data.flat[pivot])))
        return matches(phase)

    def to_instruction(self, name: str = "unitary", label: str | None = None) -> Instruction:
        if self.num_qubits is None:
            from quantumbridge.core.classical import UnsupportedFeature
            raise UnsupportedFeature("mixed_radix_operator_instruction","Qubit instructions cannot reinterpret qudits or rectangular maps.")
        return Instruction(
            name=label or name,
            num_qubits=self.num_qubits,
            metadata={"matrix": self.to_matrix(), "source": "quantumbridge.information.Operator"},
        )

    def to_matrix(self) -> np.ndarray:
        from quantumbridge.execution.array_ownership import copied_array
        return copied_array(self.data,category="operator_matrix_export")

    def __matmul__(self, other: "Operator") -> "Operator":
        return self.compose(other)

    def __rmatmul__(self, other) -> "Operator":
        return Operator(other,input_dims=self._output_dims,output_dims=self._output_dims).compose(self)

    def _arithmetic(self, other, operation, *, scalar=False, reverse=False):
        from quantumbridge.execution.resource_context import current_resources
        scope=current_resources()
        first=self.data
        second=other.data if isinstance(other,Operator) else other
        if scope is not None:
            from quantumbridge.execution.array_reservations import numeric_array, numeric_shape
            first=numeric_array(first,category="operator_arithmetic_input")
            if scalar:
                if numeric_shape(second):raise ValueError("Operator scaling requires a numeric scalar.")
            else:second=numeric_array(second,category="operator_arithmetic_input")
        elif not scalar:second=np.asarray(second,dtype=complex)
        if not scalar and first.shape!=second.shape:
            raise ValueError("QuantumBridge Operator arithmetic requires equal dimensions.")
        if not scalar and isinstance(other,Operator) and (self._input_dims!=other._input_dims or self._output_dims!=other._output_dims):
            raise ValueError("Operator arithmetic requires matching subsystem dimensions.")
        left,right=(second,first) if reverse else (first,second)
        if scope is None:return self._new(operation(left,right))
        from quantumbridge.execution import mps_arrays as arrays
        output=arrays.owned("operator_arithmetic_output",first.shape,complex)
        scope.ledger.unavailable("operator_ufunc_iterator_workspace",
            "The independent matrix output is reserved; NumPy scalar/iterator workspace is not measured RSS.")
        operation(left,right,out=output)
        return self._new(output)

    def __mul__(self, scalar) -> "Operator":
        if not isinstance(scalar, Number):
            return NotImplemented
        return self._arithmetic(scalar,np.multiply,scalar=True)

    def __rmul__(self, scalar) -> "Operator":
        return self.__mul__(scalar)

    def __truediv__(self, scalar) -> "Operator":
        if not isinstance(scalar, Number):
            return NotImplemented
        return self._arithmetic(scalar,np.divide,scalar=True)

    def __add__(self, other) -> "Operator":
        return self._arithmetic(other,np.add)

    def __radd__(self, other) -> "Operator":
        return self._arithmetic(other,np.add,reverse=True)

    def __sub__(self, other) -> "Operator":
        return self._arithmetic(other,np.subtract)

    def __rsub__(self, other) -> "Operator":
        return self._arithmetic(other,np.subtract,reverse=True)

    def __xor__(self, n: int) -> "Operator":
        return self.tensorpower(n)

    def __copy__(self) -> "Operator":
        return self.copy()

    def __deepcopy__(self, memo) -> "Operator":
        from quantumbridge.execution.array_ownership import native_object_deepcopy
        return native_object_deepcopy(self,memo)

    def __eq__(self, other) -> bool:
        try:
            return self.equiv(other)
        except Exception:
            return False
