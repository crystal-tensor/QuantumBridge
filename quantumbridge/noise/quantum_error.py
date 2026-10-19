# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native CPTP algebra. Error matrices use public little-endian qarg ordering.
from itertools import product
from numbers import Integral, Real
import numpy as np
from quantumbridge.utils.math import validate_kraus_operators, pauli_matrix


class QuantumError:
    def __init__(self, operators, name="kraus", *, max_kraus_ops=256, max_dimension=64):
        operators = tuple(operators)
        if not operators or len(operators) > max_kraus_ops:
            raise ValueError("Quantum error exceeds the Kraus construction budget.")
        first = np.asarray(operators[0])
        dimension = first.shape[0] if first.ndim == 2 else 0
        if dimension < 2 or dimension & (dimension-1) or dimension > max_dimension:
            raise ValueError("Quantum error needs a bounded power-of-two dimension.")
        self._operators = tuple(op.copy() for op in validate_kraus_operators(operators, dimension))
        self.num_qubits = dimension.bit_length()-1
        self.name = str(name)
        self.provenance = {"implementation":"quantumbridge_native", "mathematics":"CPTP Kraus", "matrix_order":"little-endian qargs"}

    def kraus(self): return tuple(op.copy() for op in self._operators)

    def compose(self, other, *, front=False):
        if not isinstance(other, QuantumError) or self.num_qubits != other.num_qubits:
            raise ValueError("QuantumError composition requires equal widths.")
        if len(self._operators)*len(other._operators) > 256:
            raise MemoryError("Composed error exceeds the Kraus construction budget.")
        left, right = (self,other) if front else (other,self)
        return QuantumError([a@b for a in left._operators for b in right._operators], "compose")

    def tensor(self, other):
        if not isinstance(other, QuantumError): raise TypeError("Expected native QuantumError.")
        if len(self._operators)*len(other._operators)>256 or self.num_qubits+other.num_qubits>6:
            raise MemoryError("Tensor error exceeds the construction budget.")
        return QuantumError([np.kron(a,b) for a in self._operators for b in other._operators], "tensor")

    def expand(self, other): return other.tensor(self)

    def to_quantumchannel(self):
        from quantumbridge.information import Kraus
        return Kraus(self.kraus())

    def to_dict(self):
        return {"format":"qb-quantum-error-v1", "name":self.name,
                "kraus":[{"real":op.real.tolist(),"imag":op.imag.tolist()} for op in self._operators]}

    @classmethod
    def from_dict(cls, value):
        from quantumbridge.ir.qb_ir import matrix_from_ir
        if value.get("format")!="qb-quantum-error-v1": raise ValueError("Unknown quantum-error schema.")
        return cls([matrix_from_ir(op) for op in value["kraus"]],value["name"])


def probability(value):
    if isinstance(value,bool) or not isinstance(value,Real) or not np.isfinite(value) or not 0<=value<=1:
        raise ValueError("Expected a finite noise probability in [0,1].")
    return float(value)


def kraus_error(operators, canonical_kraus=False):
    error = QuantumError(operators)
    if not isinstance(canonical_kraus,bool): raise TypeError("canonical_kraus must be boolean.")
    if not canonical_kraus: return error
    if error.num_qubits>4:raise MemoryError("Canonical Kraus Choi diagonalization exceeds dimension budget.")
    choi = sum(np.outer(op.reshape(-1,order="F"),op.reshape(-1,order="F").conj()) for op in error.kraus())
    values,vectors = np.linalg.eigh(choi)
    dimension = 1<<error.num_qubits
    return QuantumError([np.sqrt(value)*vector.reshape(dimension,dimension,order="F") for value,vector in zip(values,vectors.T) if value>1e-14])


def mixed_unitary_error(entries):
    entries = tuple(entries)
    if not entries or len(entries)>256: raise ValueError("Invalid mixed-unitary size.")
    probabilities = [probability(p) for _,p in entries]
    if not np.isclose(sum(probabilities),1,atol=1e-12,rtol=0): raise ValueError("Mixture weights must sum to one.")
    operators=[]
    for (matrix,_),p in zip(entries,probabilities):
        matrix=np.asarray(matrix,complex)
        if matrix.ndim!=2 or matrix.shape[0]!=matrix.shape[1] or matrix.shape[0]>64 or not np.all(np.isfinite(matrix)) or not np.allclose(matrix.conj().T@matrix,np.eye(len(matrix)),atol=1e-10,rtol=0):
            raise ValueError("Mixture entries must be finite unitaries.")
        operators.append(np.sqrt(p)*matrix)
    return QuantumError(operators,"mixed_unitary")


def coherent_unitary_error(matrix): return mixed_unitary_error([(matrix,1.)])


def pauli_error(entries):
    from quantumbridge.operators import Pauli
    entries=tuple(entries)
    if not entries or len(entries)>256: raise ValueError("Invalid Pauli mixture size.")
    width=len(entries[0][0])
    if not 1<=width<=6 or any(not isinstance(label,str) or len(label)!=width or set(label)-set("IXYZ") for label,_ in entries):
        raise ValueError("Pauli errors require equal bounded nonempty Pauli labels.")
    error=mixed_unitary_error([(Pauli(label).to_matrix(),p) for label,p in entries])
    error.name="pauli"
    return error


def depolarizing_error(param, num_qubits):
    if isinstance(num_qubits,bool) or not isinstance(num_qubits,Integral) or not 1<=num_qubits<=4:
        raise ValueError("Depolarizing width exceeds the explicit construction budget [1,4].")
    count=4**num_qubits
    if isinstance(param,bool) or not isinstance(param,Real) or not np.isfinite(param) or not 0<=param<=count/(count-1):
        raise ValueError("Invalid depolarizing parameter for this width.")
    entries=[("".join(label),float(param)/count) for label in product("IXYZ",repeat=num_qubits)]
    entries[0]=(entries[0][0],1-param+param/count)
    return pauli_error(entries)


def reset_error(prob0, prob1=0):
    p0,p1=probability(prob0),probability(prob1)
    if p0+p1>1: raise ValueError("Reset probabilities exceed one.")
    zero=np.array([[1,0],[0,0]],complex); lower=np.array([[0,1],[0,0]],complex)
    return QuantumError([np.sqrt(1-p0-p1)*np.eye(2),np.sqrt(p0)*zero,np.sqrt(p0)*lower,
                         np.sqrt(p1)*lower.T,np.sqrt(p1)*(np.eye(2)-zero)],"reset")


def phase_amplitude_damping_error(param_amp, param_phase, excited_state_population=0, canonical_kraus=True):
    a,b,p=probability(param_amp),probability(param_phase),probability(excited_state_population)
    if a+b>1: raise ValueError("Amplitude and phase damping probabilities exceed one.")
    down=np.array([[0,np.sqrt(a)],[0,0]],complex)
    ops=[np.sqrt(1-p)*np.diag([1,np.sqrt(1-a-b)]),np.sqrt(1-p)*down,np.sqrt(1-p)*np.diag([0,np.sqrt(b)]),
         np.sqrt(p)*np.diag([np.sqrt(1-a-b),1]),np.sqrt(p)*down.T,np.sqrt(p)*np.diag([np.sqrt(b),0])]
    result=kraus_error(ops,canonical_kraus); result.name="phase_amplitude_damping"
    return result


def amplitude_damping_error(param_amp, excited_state_population=0, canonical_kraus=True):
    return phase_amplitude_damping_error(param_amp,0,excited_state_population,canonical_kraus)


def phase_damping_error(param_phase, canonical_kraus=True):
    return phase_amplitude_damping_error(0,param_phase,0,canonical_kraus)


def thermal_relaxation_error(t1,t2,time,excited_state_population=0):
    if any(isinstance(v,bool) or not isinstance(v,Real) or np.isnan(v) or v<=0 for v in (t1,t2)) or t2>2*t1:
        raise ValueError("Thermal times require T1,T2>0 and T2<=2*T1.")
    if isinstance(time,bool) or not isinstance(time,Real) or not np.isfinite(time) or time<0:
        raise ValueError("Thermal duration must be finite and nonnegative.")
    p=probability(excited_state_population)
    gamma=-np.expm1(-time/t1)
    rate=max(0.,1/t2-1/(2*t1))
    dephase=-np.expm1(-2*time*rate)
    error=amplitude_damping_error(gamma,p).compose(phase_damping_error(dephase))
    error.name="thermal_relaxation"
    return error
