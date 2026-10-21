# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native inverse-state/reverse-cotangent differentiation; no SDK gradients.

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.utils.math import apply_unitary, gate_matrix, pauli_matrix, Hamiltonian, PauliString, observable_matrix


def gate_derivative(operation, parameters):
    name = operation.name
    base = {"crx": "rx", "cry": "ry", "crz": "rz", "cphase": "phase", "cp": "phase"}.get(name, name)
    matrix = gate_matrix(base, parameters)
    if base in {"rx", "ry", "rz"}: derivative = -.5j * pauli_matrix(base[-1].upper()) @ matrix
    elif base in {"phase", "p", "u1"}: derivative = np.diag([0, 1j * np.exp(1j * parameters[0])])
    elif base in {"rxx", "ryy", "rzz"}:
        pauli = pauli_matrix(base[-1].upper())
        derivative = -.5j * np.kron(pauli, pauli) @ matrix
    else: raise UnsupportedFeature("gate_derivative", f"No native derivative recipe for {name}.")
    if name != base:
        controlled = np.zeros((4, 4), complex)
        controlled[2:, 2:] = derivative
        derivative = controlled
    return derivative


def apply_observable(state, observable, width):
    if hasattr(observable, "to_hamiltonian"): observable = observable.to_hamiltonian()
    if isinstance(observable, PauliString):
        result = state
        for wire, label in observable.terms: result = apply_unitary(result, pauli_matrix(label), (wire,), width)
        return result
    if isinstance(observable, Hamiltonian):
        return sum((coefficient * apply_observable(state, pauli, width) for coefficient, pauli in observable.terms), np.zeros_like(state))
    if width > 12: raise UnsupportedFeature("dense_observable", "Large adjoint observables require native Pauli/Hamiltonian form.")
    matrix = observable_matrix(observable, width)
    from quantumbridge.utils.math import validate_observable_matrix
    if not validate_observable_matrix(matrix, width, atol=1e-8, rtol=1e-5): raise ValueError("Adjoint requires a Hermitian observable matching circuit width.")
    return matrix @ state


def adjoint_rows(device, circuit, angle_parameters, values, requests):
    from quantumbridge.devices import StatevectorDevice
    if type(device) is not StatevectorDevice or circuit.has_dynamic_operations or getattr(device,"noise_model",None) is not None:
        raise UnsupportedFeature("adjoint_device", "Native adjoint requires analytic unitary StatevectorDevice execution.")
    mapping = dict(zip(angle_parameters, values))
    bound = circuit.bind(mapping)
    state = device.statevector(bound)
    # The reverse sweep retains a constant number of state vectors per output.
    if device.max_memory_mb is not None and state.nbytes * 8 > device.max_memory_mb * 1024 ** 2:
        raise MemoryError("Adjoint buffers exceed max_memory_mb.")
    rows = []
    for request in requests:
        if request.kind in {"expval", "var"}:
            operated = apply_observable(state, request.observable, circuit.num_qubits)
            if request.kind == "var":
                mean = np.vdot(state, operated).real
                cotangents = [(apply_observable(operated, request.observable, circuit.num_qubits), -2 * mean * operated)]
            else: cotangents = [(operated,)]
        elif request.kind == "probs":
            wires = tuple(range(circuit.num_qubits)) if request.wires is None else request.wires
            if len(wires) > 16: raise UnsupportedFeature("probability_jacobian_size", "Probability Jacobian output exceeds the native budget.")
            labels = np.zeros(state.size, dtype=np.int64)
            for wire in wires: labels = 2 * labels + ((np.arange(state.size) >> (circuit.num_qubits - 1 - wire)) & 1)
            if state.size * (1 << len(wires)) * max(1, len(bound.operations)) > 100000000:
                raise MemoryError("Adjoint probability derivative work exceeds the native contraction budget.")
            cotangents = ((state * (labels == label),) for label in range(1 << len(wires)))
        else: raise UnsupportedFeature("adjoint_measurement", f"No adjoint rule for {request.kind}.")
        for terms in cotangents:
            psi, adjoint, row = state.copy(), sum(terms), np.zeros(len(values))
            for raw, operation in zip(reversed(circuit.operations), reversed(bound.operations)):
                if operation.metadata.get("directive") and operation.name in {"barrier", "delay"}: continue
                matrix = gate_matrix(operation.name, operation.params, operation.metadata)
                before = apply_unitary(psi, matrix.conj().T, operation.wires, circuit.num_qubits)
                for parameter_index, parameter in enumerate(raw.params):
                    if parameter not in angle_parameters: continue
                    if parameter_index or len(raw.params) != 1: raise UnsupportedFeature("adjoint_gate_parameters")
                    derivative = gate_derivative(raw, operation.params)
                    row[angle_parameters.index(parameter)] += 2 * np.vdot(adjoint, apply_unitary(before, derivative, operation.wires, circuit.num_qubits)).real
                adjoint = apply_unitary(adjoint, matrix.conj().T, operation.wires, circuit.num_qubits)
                psi = before
            rows.append(row)
    return np.asarray(rows)
