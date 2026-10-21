# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from math import isfinite, prod
from numbers import Integral, Number

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import apply_unitary, expectation_hamiltonian
from quantumbridge.execution.resource_context import (
    current_resources, meter_native_samples, record_completed_native_shots,
)
from .state_dimensions import (
    state_dimensions, qubit_count, basis_digits, basis_index, basis_label,
    require_qubits, subsystem_positions,
)


def _validate_qargs(qargs, num_qubits: int) -> tuple[int, ...]:
    return subsystem_positions(qargs,num_qubits)


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
    _sampling_preflight(prod(state.dims(selected)),shots)
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


def _mapped_evolution_data(operator, qargs, dimensions, *, density=False):
    from quantumbridge.information.operator import Operator
    from quantumbridge.information.channels import _operator_data
    from quantumbridge.utils.math import _local_operator_shapes
    from quantumbridge.execution.array_reservations import numeric_shape, array_layout
    from quantumbridge.core.classical import UnsupportedFeature
    scope=current_resources()
    selected=subsystem_positions(qargs,len(dimensions))
    incoming=tuple(dimensions[position] for position in selected)
    native=type(operator) is Operator if scope is not None else isinstance(operator,Operator)
    raw=operator.data if native else operator
    if scope is not None:
        if not native and not (issubclass(type(raw),np.ndarray) or type(raw) in (tuple,list)):
            raise UnsupportedFeature("managed_channel_operator","Mapped evolution requires a native operator or explicit numeric buffer.")
        shape=numeric_shape(raw)
    else:
        if not native and hasattr(operator,"to_matrix"):raw=operator.to_matrix()
        raw=np.asarray(raw,dtype=complex)
        shape=raw.shape
    if len(shape)!=2 or shape[1]!=prod(incoming):
        raise ValueError("Local operator input dimension does not match the selected subsystems.")
    if native:
        if qargs is not None and operator.input_dims()!=incoming:
            raise ValueError("Local operator input subsystem dimensions do not match qargs order.")
        outgoing=operator.output_dims()
    else:
        if shape[0]!=shape[1]:
            raise ValueError("Rectangular evolution requires explicit native Operator output_dims.")
        outgoing=incoming
    if qargs is not None and len(outgoing)!=len(selected):
        raise UnsupportedFeature("mixed_radix_output_subsystem_count","Mapped evolution cannot insert or remove subsystem positions.")
    if qargs is not None and shape[0]!=shape[1] and not density:
        raise UnsupportedFeature("mixed_radix_rectangular_statevector","Public mapped Statevector rectangular evolution fails in both verified versions; use a full typed map or DensityMatrix.")
    result_dims,shapes=_local_operator_shapes(dimensions,selected,outgoing,density=density)
    if scope is not None:
        conversion=array_layout(shape,complex)[2] if native or not issubclass(type(raw),np.ndarray) or np.ndarray.view(raw,np.ndarray).dtype!=np.dtype(complex) else 0
        scope.ledger.preflight(memory_bytes=conversion+sum(array_layout(shape,complex)[2] for shape in shapes))
        matrix=_operator_data(operator)
    else:matrix=raw
    return matrix,selected,outgoing,result_dims


class Statevector:
    def __init__(self, data, normalize: bool = False, *, dims=None):
        from quantumbridge.execution.resource_context import current_resources
        scope = current_resources()
        if scope is None:
            self.data = np.asarray(data, dtype=complex)
            shape=self.data.shape
        else:
            from quantumbridge.execution.array_reservations import numeric_array, numeric_shape
            shape=numeric_shape(data)
        if len(shape)!=1:
            raise ValueError("QuantumBridge Statevector data must be one-dimensional.")
        self._dims=state_dimensions(dims,size=shape[0])
        if scope is not None:
            self.data = numeric_array(data, category="statevector_input_conversion")
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
        self.num_qubits = qubit_count(self._dims)

    @property
    def dim(self) -> int:
        return len(self.data)

    def dims(self, qargs=None) -> tuple[int, ...]:
        return tuple(self._dims[position] for position in _validate_qargs(qargs,len(self._dims)))

    @classmethod
    def from_circuit(cls, circuit) -> "Statevector":
        return cls(StatevectorDevice().statevector(circuit))

    @classmethod
    def from_int(cls, index: int, dims) -> "Statevector":
        if isinstance(index,bool) or not isinstance(index,Integral):
            raise ValueError("Statevector.from_int index must be an integer.")
        dimensions=state_dimensions(dims)
        dim=prod(dimensions)
        if index < 0 or index >= dim:
            raise ValueError("QuantumBridge Statevector.from_int index is outside dims.")
        from quantumbridge.execution import mps_arrays as arrays
        data=arrays.filled("statevector_basis",(dim,),complex,0)
        data[int(index)] = 1.0
        return cls(data,dims=dimensions)

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
        selected=_validate_qargs(wires,len(self._dims))
        probabilities={}
        for index,amplitude in enumerate(self.data):
            label=basis_label(index,self._dims,selected)
            probabilities[label]=probabilities.get(label,0.)+float(abs(amplitude)**2)
        return probabilities

    def probabilities_dict(self, qargs=None) -> dict[str, float]:
        return self.probabilities(qargs)

    def expectation_value(self, observable, qargs=None) -> complex:
        from quantumbridge.information.operator import Operator

        if qargs is not None:require_qubits(self._dims,"mixed_radix_subsystem_expectation")
        if hasattr(observable, "to_hamiltonian"):
            require_qubits(self._dims,"mixed_radix_hamiltonian")
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

        if hasattr(operator,"operations"):require_qubits(self._dims,"mixed_radix_circuit_evolution")
        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        native=type(op) is Operator if scope is not None else isinstance(op,Operator)
        if qargs is not None or native and op.input_dims()!=op.output_dims():
            matrix,selected,outgoing,result_dims=_mapped_evolution_data(op,qargs,self._dims)
            return Statevector(apply_unitary(self.data,matrix,selected,self.num_qubits,dims=self._dims,output_dims=outgoing),dims=result_dims)
        if scope is not None:
            from quantumbridge.information.channels import _operator_data
            matrix=_operator_data(op)
        else:matrix = np.asarray(op.to_matrix(), dtype=complex) if hasattr(op, "to_matrix") else np.asarray(op, dtype=complex)
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge evolution operator dimension must match Statevector dimension.")
        if scope is not None:
            from quantumbridge.execution import mps_arrays as arrays
            return Statevector(arrays.contracted(matrix,self.data),dims=self._dims)
        return Statevector(matrix @ self.data,dims=self._dims)

    def tensor(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(_tensor_arrays(self.data, other_state.data),dims=self._dims+other_state._dims)

    def expand(self, other) -> "Statevector":
        other_state = other if isinstance(other, Statevector) else Statevector(other)
        return Statevector(_tensor_arrays(other_state.data, self.data),dims=other_state._dims+self._dims)

    def reverse_qargs(self) -> "Statevector":
        from quantumbridge.execution.array_ownership import copied_array
        data=copied_array(self.data,category="statevector_reverse")
        for source, amplitude in enumerate(self.data):
            target=basis_index(basis_digits(source,self._dims)[::-1],self._dims[::-1])
            data[target] = amplitude
        return Statevector(data,dims=self._dims[::-1])

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
        selected=_validate_qargs(qargs,len(self._dims))
        return _counts_from_indices(*_sample_measurements(self,selected,shots,seed))

    @meter_native_samples
    def sample_memory(self, shots: int, qargs=None, seed: int | None = None) -> list[str]:
        qargs_tuple = _validate_qargs(qargs,len(self._dims))
        return _memory_from_indices(*_sample_measurements(self,qargs_tuple,shots,seed))

    def measure(self, qargs=None, seed: int | None = None) -> tuple[str, "Statevector"]:
        qargs_tuple = _validate_qargs(qargs,len(self._dims))
        if current_resources() is not None:
            current_resources().ledger.preflight(memory_bytes=self.data.nbytes)
        memory = self.sample_memory(1, qargs=qargs_tuple, seed=seed)
        outcome = memory[0] if memory else ""
        from quantumbridge.execution.array_ownership import copied_array
        collapsed=copied_array(self.data,category="statevector_projection")
        for index in range(len(collapsed)):
            if basis_label(index,self._dims,qargs_tuple) != outcome:
                collapsed[index] = 0.0
        if current_resources() is None:norm=np.linalg.norm(collapsed)
        else:
            from quantumbridge.execution import mps_arrays as arrays
            norm=np.sqrt(arrays.norm_squared(collapsed))
        if norm == 0:
            raise ValueError("QuantumBridge measurement produced a zero-probability collapse.")
        np.divide(collapsed,norm,out=collapsed)
        return outcome, Statevector(collapsed,dims=self._dims)

    def reset(self, qargs=None, seed: int | None = None) -> "Statevector":
        selected=_validate_qargs(qargs,len(self._dims))
        if qargs is None:
            return Statevector.from_int(0,self._dims)
        if not selected:return self.copy()
        _,collapsed=self.measure(selected,seed=seed)
        # Zeroing measured digits maps uniquely to earlier basis indices.
        for index in range(len(collapsed.data)):
            digits=list(basis_digits(index,self._dims))
            for position in selected:digits[position]=0
            target=basis_index(digits,self._dims)
            if target!=index and collapsed.data[index]!=0:
                collapsed.data[target]=collapsed.data[index]
                collapsed.data[index]=0
        return collapsed

    def to_operator(self):
        from quantumbridge.information.operator import Operator

        require_qubits(self._dims,"mixed_radix_operator_conversion")
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
        return Statevector(copied_array(self.data,category="statevector_copy"),dims=self._dims)

    def to_dict(self, decimals: int | None = None) -> dict[str, complex]:
        out = {}
        for index, amplitude in enumerate(self.data):
            if abs(amplitude) <= 1e-15:
                continue
            if decimals is not None:
                amplitude = np.round(amplitude, decimals=decimals)
            label=basis_label(index,self._dims,tuple(range(len(self._dims)))) if self._dims else "0"
            out[label] = complex(amplitude)
        return out

    def __len__(self) -> int:
        return len(self.data)

    def __mul__(self, scalar):
        if not isinstance(scalar, Number):
            return NotImplemented
        return Statevector(self.data * scalar,dims=self._dims)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if not isinstance(scalar, Number):
            return NotImplemented
        return Statevector(self.data / scalar,dims=self._dims)

    def __eq__(self, other) -> bool:
        try:
            return self.equiv(other)
        except Exception:
            return False
