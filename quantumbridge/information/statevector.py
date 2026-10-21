# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from math import isfinite, prod
from numbers import Integral, Number

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import apply_unitary, expectation_hamiltonian, probabilities_from_state
from quantumbridge.execution.resource_context import (
    current_resources, meter_native_samples, record_completed_native_shots,
)


def _validate_qargs(qargs, num_qubits: int) -> tuple[int, ...]:
    normalized = tuple(range(num_qubits) if qargs is None else qargs)
    if any(isinstance(qarg,bool) or not isinstance(qarg,Integral) for qarg in normalized):
        raise ValueError("QuantumBridge Statevector qargs must be integer subsystem positions.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge Statevector qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge Statevector qargs are outside this state.")
    return normalized


def _index_bits(index: int, qargs: tuple[int, ...], num_qubits: int) -> str:
    return "".join(str((index >> (num_qubits - 1 - qarg)) & 1) for qarg in qargs)


def _sampling_preflight(outcomes, shots):
    if isinstance(shots,bool) or not isinstance(shots,Integral) or shots<0:
        raise ValueError("Native state sampling requires nonnegative integer shots.")
    scope=current_resources()
    if scope is not None:
        from quantumbridge.execution.array_reservations import array_layout
        scope.ledger.preflight(memory_bytes=(2*array_layout((outcomes,),float)[2]
            +array_layout((shots,),float)[2]+array_layout((shots,),np.intp)[2]) if shots else 0)
        scope.ledger.unavailable("state_sampling_python_rng_workspace",
            "Probability/CDF/uniform/outcome ndarray buffers are explicit; labels, Python containers and bit-generator internals are not measured RSS.")


def _sample_measurements(state, selected, shots, seed):
    _sampling_preflight(1<<len(selected),shots)
    distribution=state.probabilities(selected)
    labels=sorted(distribution)
    values=tuple(distribution[label] for label in labels)
    if not values or any(not isfinite(value) or value<0 for value in values) or not 0<sum(values)<float("inf"):
        raise ValueError("State sampling probabilities must be finite, nonnegative and nonzero.")
    if not shots:return labels,()
    scope=current_resources()
    if scope is None:
        weights=np.array(values,dtype=float)
        weights/=weights.sum()
        draws=np.random.default_rng(seed).choice(len(labels),size=shots,p=weights)
    else:
        from quantumbridge.execution.array_reservations import ArrayReservation, owned_arrays
        from quantumbridge.execution.array_ownership import retain_reservation, native_storage_bytes
        reservation=ArrayReservation(scope.ledger,"state_sampling_outcomes",(shots,),np.intp)
        try:
            weights,cdf,uniforms=owned_arrays([((len(labels),),float),((len(labels),),float),((shots,),float)],category="state_sampling_workspace")
            for index,value in enumerate(values):weights[index]=value
            np.divide(weights,weights.sum(),out=weights)
            np.cumsum(weights,out=cdf)
            np.divide(cdf,cdf[-1],out=cdf)
            np.random.default_rng(seed).random(shots,out=uniforms)
            draws=reservation.create(lambda:np.searchsorted(cdf,uniforms,side="right"))
            if native_storage_bytes(draws)!=draws.nbytes or np.may_share_memory(draws,uniforms):
                raise RuntimeError("State sampling produced unexpected outcome storage.")
            retain_reservation(reservation,draws)
        except BaseException:
            reservation.release()
            raise
    record_completed_native_shots(shots)
    return labels,draws


def _memory_from_indices(labels,indices):
    return [labels[int(index)] for index in indices]


def _counts_from_indices(labels,indices):
    counts={label:0 for label in labels}
    for index in indices:counts[labels[int(index)]]+=1
    return {label:count for label,count in counts.items() if count}


def _tensor_arrays(first,second):
    if current_resources() is None:return np.kron(first,second)
    from quantumbridge.execution import mps_arrays as arrays
    from quantumbridge.execution.array_reservations import kron_into
    if first.ndim==1:
        result=arrays.owned("state_tensor",(first.size*second.size,),complex)
        kron_into(first[:,None],second[:,None],result.reshape(-1,1),scope=current_resources())
    else:
        result=arrays.owned("density_tensor",(first.shape[0]*second.shape[0],first.shape[1]*second.shape[1]),complex)
        kron_into(first,second,result,scope=current_resources())
    return result


class Statevector:
    def __init__(self, data, normalize: bool = False):
        from quantumbridge.execution.resource_context import current_resources
        scope = current_resources()
        if scope is None:self.data = np.asarray(data, dtype=complex)
        else:
            from quantumbridge.execution.array_reservations import numeric_array
            self.data = numeric_array(data, category="statevector_input_conversion")
        if self.data.ndim != 1:
            raise ValueError("QuantumBridge Statevector data must be one-dimensional.")
        if len(self.data) == 0 or len(self.data) & (len(self.data) - 1):
            raise ValueError("QuantumBridge Statevector dimension must be a power of two.")
        if normalize:
            if scope is None:norm = np.linalg.norm(self.data)
            else:
                from quantumbridge.execution import mps_arrays as arrays
                norm = np.sqrt(arrays.norm_squared(self.data))
            if norm == 0:
                raise ValueError("QuantumBridge cannot normalize a zero Statevector.")
            if scope is None:self.data = self.data / norm
            else:
                output = arrays.owned("statevector_normalized", self.data.shape, complex)
                np.divide(self.data, norm, out=output)
                self.data = output
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
        if isinstance(index,bool) or not isinstance(index,Integral):
            raise ValueError("Statevector.from_int index must be an integer.")
        if isinstance(dims, Integral) and not isinstance(dims,bool):
            dim = int(dims)
        else:
            if current_resources() is not None and type(dims) not in (tuple,list):
                raise ValueError("Managed state dimensions require a builtin integer sequence.")
            dimensions=tuple(dims)
            if any(isinstance(value,bool) or not isinstance(value,Integral) or value<=0 for value in dimensions):
                raise ValueError("State dimensions must be positive integers.")
            dim = prod(int(value) for value in dimensions)
        if dim <= 0 or dim & (dim - 1):
            raise ValueError("QuantumBridge Statevector.from_int dims must describe a power-of-two dimension.")
        if index < 0 or index >= dim:
            raise ValueError("QuantumBridge Statevector.from_int index is outside dims.")
        from quantumbridge.execution import mps_arrays as arrays
        data=arrays.filled("statevector_basis",(dim,),complex,0)
        data[int(index)] = 1.0
        return cls(data)

    @classmethod
    def from_label(cls, label: str) -> "Statevector":
        if type(label) is not str or any(bit not in "01+-rl" for bit in label):
            raise ValueError("Statevector labels must contain Pauli eigenstates 0, 1, +, -, r or l.")
        from quantumbridge.execution import mps_arrays as arrays
        coefficients={"0":(1,0),"1":(0,1),"+":(1,1),"-":(1,-1),"r":(1,1j),"l":(1,-1j)}
        data=arrays.owned("statevector_label",(1<<len(label),),complex)
        normalization=2**(-.5*sum(symbol not in "01" for symbol in label))
        for index in range(len(data)):
            value=complex(normalization)
            for wire,symbol in enumerate(label):value*=coefficients[symbol][(index>>(len(label)-1-wire))&1]
            data[index]=value
        return cls(data)

    def is_valid(self, atol: float = 1e-10) -> bool:
        if current_resources() is not None:
            from quantumbridge.execution import mps_arrays as arrays
            return bool(np.isclose(arrays.norm_squared(self.data),1.,atol=atol))
        return bool(np.isclose(np.vdot(self.data, self.data), 1.0, atol=atol))

    def probabilities(self, wires=None) -> dict[str, float]:
        return probabilities_from_state(self.data, self.num_qubits, wires)

    def probabilities_dict(self, qargs=None) -> dict[str, float]:
        return self.probabilities(qargs)

    def expectation_value(self, observable, qargs=None) -> complex:
        from quantumbridge.information.operator import Operator

        if hasattr(observable, "to_hamiltonian"):
            return expectation_hamiltonian(self.data, self.num_qubits, observable.to_hamiltonian())
        if hasattr(observable, "to_matrix"):
            matrix = np.asarray(observable.to_matrix(), dtype=complex)
        else:
            matrix = observable.data if hasattr(observable, "data") else np.asarray(observable, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            matrix = Operator(np.eye(len(self.data), dtype=complex)).compose(Operator(matrix), qargs=qargs_tuple).data
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge observable dimension must match Statevector dimension.")
        return np.vdot(self.data, matrix @ self.data)

    def evolve(self, operator, qargs=None) -> "Statevector":
        from quantumbridge.information.operator import Operator
        from quantumbridge.execution.resource_context import current_resources
        scope=current_resources()

        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        if scope is not None:
            from quantumbridge.information.channels import _operator_data
            matrix=_operator_data(op)
        else:matrix = np.asarray(op.to_matrix(), dtype=complex) if hasattr(op, "to_matrix") else np.asarray(op, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            dim = 1 << len(qargs_tuple)
            if matrix.shape != (dim, dim):
                raise ValueError("QuantumBridge subsystem evolution operator dimension must match qargs.")
            return Statevector(apply_unitary(self.data, matrix, qargs_tuple, self.num_qubits))
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge evolution operator dimension must match Statevector dimension.")
        if scope is not None:
            from quantumbridge.execution import mps_arrays as arrays
            return Statevector(arrays.contracted(matrix,self.data))
        return Statevector(matrix @ self.data)

    def tensor(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(_tensor_arrays(self.data, other_state.data))

    def expand(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(_tensor_arrays(other_state.data, self.data))

    def reverse_qargs(self) -> "Statevector":
        from quantumbridge.execution.array_ownership import copied_array
        data=copied_array(self.data,category="statevector_reverse")
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

    @meter_native_samples(result_count=lambda counts:sum(counts.values()))
    def sample_counts(self, shots: int, qargs=None, seed: int | None = None) -> dict[str, int]:
        # Keep the old positional integer seed while accepting subsystem lists.
        if isinstance(qargs,Integral) and seed is None:seed,qargs=int(qargs),None
        selected=_validate_qargs(qargs,self.num_qubits)
        return _counts_from_indices(*_sample_measurements(self,selected,shots,seed))

    @meter_native_samples
    def sample_memory(self, shots: int, qargs=None, seed: int | None = None) -> list[str]:
        qargs_tuple = _validate_qargs(qargs, self.num_qubits)
        return _memory_from_indices(*_sample_measurements(self,qargs_tuple,shots,seed))

    def measure(self, qargs=None, seed: int | None = None) -> tuple[str, "Statevector"]:
        qargs_tuple = _validate_qargs(qargs, self.num_qubits)
        if current_resources() is not None:
            current_resources().ledger.preflight(memory_bytes=self.data.nbytes)
        memory = self.sample_memory(1, qargs=qargs_tuple, seed=seed)
        outcome = memory[0] if memory else ""
        from quantumbridge.execution.array_ownership import copied_array
        collapsed=copied_array(self.data,category="statevector_projection")
        for index in range(len(collapsed)):
            if _index_bits(index, qargs_tuple, self.num_qubits) != outcome:
                collapsed[index] = 0.0
        if current_resources() is None:norm=np.linalg.norm(collapsed)
        else:
            from quantumbridge.execution import mps_arrays as arrays
            norm=np.sqrt(arrays.norm_squared(collapsed))
        if norm == 0:
            raise ValueError("QuantumBridge measurement produced a zero-probability collapse.")
        np.divide(collapsed,norm,out=collapsed)
        return outcome, Statevector(collapsed)

    def reset(self, qargs=None, seed: int | None = None) -> "Statevector":
        selected=_validate_qargs(qargs,self.num_qubits)
        if qargs is None:
            return Statevector.from_int(0,self.dim)
        if not selected:return self.copy()
        outcome,collapsed=self.measure(selected,seed=seed)
        mask=sum(1<<(self.num_qubits-1-wire) for wire,bit in zip(selected,outcome) if bit=="1")
        if mask:
            for index in range(len(collapsed.data)):
                if index&mask==mask:
                    collapsed.data[index&~mask]=collapsed.data[index]
                    collapsed.data[index]=0
        return collapsed

    def to_operator(self):
        from quantumbridge.information.operator import Operator

        return Operator(np.outer(self.data, np.conjugate(self.data)))

    def to_density_matrix(self):
        from quantumbridge.information.density_matrix import DensityMatrix

        return DensityMatrix.from_statevector(self)

    def partial_trace(self, keep: tuple[int, ...] | list[int]):
        from quantumbridge.information.density_matrix import DensityMatrix

        return DensityMatrix.from_statevector(self).partial_trace(keep)

    def conjugate(self) -> "Statevector":
        copied=self.copy()
        np.conjugate(copied.data,out=copied.data)
        return copied

    def transpose(self) -> "Statevector":
        return self.copy()

    def adjoint(self) -> np.ndarray:
        return self.conjugate().data.reshape(1,-1)

    def copy(self) -> "Statevector":
        from quantumbridge.execution.array_ownership import copied_array
        return Statevector(copied_array(self.data,category="statevector_copy"))

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
