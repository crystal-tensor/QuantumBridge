# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Full complex algebraic oracles, independent of native recipe execution."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.circuit_library import standard_gate_definition, standard_gate_object
from quantumbridge.information import Operator

NAMES = ["id", "h", "x", "y", "z", "s", "sdg", "t", "tdg", "sx", "sxdg",
    "rx", "ry", "rz", "phase", "p", "u1", "u", "u2", "u3", "cx", "cz", "swap",
    "crx", "cry", "crz", "cp", "cphase", "rxx", "ryy", "rzz"]


def angles(name, value):
    if name in {"u", "u3"}: return (value, value/3, -2*value)
    if name == "u2": return (value/3, -2*value)
    if name in {"rx", "ry", "rz", "phase", "p", "u1", "crx", "cry", "crz", "cp", "cphase", "rxx", "ryy", "rzz"}: return (value,)
    return ()


def oracle(name, values):
    identity = np.eye(2, dtype=complex)
    x = np.array([[0, 1], [1, 0]], complex)
    y = np.array([[0, -1j], [1j, 0]], complex)
    z = np.diag([1, -1])
    if name in {"cx", "cz", "crx", "cry", "crz", "cp", "cphase"}:
        base = oracle({"cx": "x", "cz": "z", "cp": "phase", "cphase": "phase"}.get(name, name[1:]), values)
        result = np.eye(4, dtype=complex)
        result[2:, 2:] = base
        return result
    if name == "swap": return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    if name in {"rxx", "ryy", "rzz"}:
        generator = {"rxx": x, "ryy": y, "rzz": z}[name]
        return np.cos(values[0]/2)*np.eye(4)-1j*np.sin(values[0]/2)*np.kron(generator, generator)
    if name in {"rx", "ry", "rz"}: return np.cos(values[0]/2)*identity-1j*np.sin(values[0]/2)*{"rx": x, "ry": y, "rz": z}[name]
    if name in {"phase", "p", "u1"}: return np.diag([1, np.exp(1j*values[0])])
    if name in {"u", "u2", "u3"}:
        theta, phi, lam = (np.pi/2, *values) if name == "u2" else values
        c, s = np.cos(theta/2), np.sin(theta/2)
        return np.array([[c, -np.exp(1j*lam)*s], [np.exp(1j*phi)*s, np.exp(1j*(phi+lam))*c]])
    return {"id": identity, "x": x, "y": y, "z": z, "h": (x+z)/np.sqrt(2),
        "s": np.diag([1, 1j]), "sdg": np.diag([1, -1j]), "t": np.diag([1, np.exp(1j*np.pi/4)]),
        "tdg": np.diag([1, np.exp(-1j*np.pi/4)]), "sx": ((1+1j)*identity+(1-1j)*x)/2,
        "sxdg": ((1-1j)*identity+(1+1j)*x)/2}[name]


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("symbolic", [False, True])
def test_real_definition_inverse_nested_and_controlled_full_phase(name, symbolic):
    p = qb.Parameter("theta")
    values = angles(name, p if symbolic else .37)
    gate = standard_gate_object(name, *values, label="standard")
    expected = oracle(name, angles(name, .37))
    bound = gate.assign_parameters({p: .37}, strict=False)
    assert gate.definition is not None
    np.testing.assert_allclose(bound.to_matrix(), expected, atol=6e-13)
    np.testing.assert_allclose(bound.inverse().to_matrix(), expected.conj().T, atol=6e-13)
    controlled = np.eye(2*len(expected), dtype=complex)
    controlled[:len(expected), :len(expected)] = expected
    np.testing.assert_allclose(bound.control(ctrl_state=0).to_matrix(), controlled, atol=7e-13)
    source = qb.Circuit(gate.num_qubits).append(gate, range(gate.num_qubits))
    for repetitions in (1, 2):
        actual = source.decompose(reps=repetitions).assign_parameters({p: .37}, strict=False)
        np.testing.assert_allclose(Operator(actual).data, expected, atol=8e-13)


def test_primitive_decompose_is_one_layer_and_name_collision_still_owned():
    source = qb.Circuit(1).sx(0)
    once = source.decompose()
    assert [op.name for op in once.operations] == ["rx"]
    assert once.global_phase == pytest.approx(np.pi/4)
    np.testing.assert_allclose(Operator(once).data, oracle("sx", ()), atol=2e-13)
    custom = qb.Circuit(1, name="h").x(0).to_gate()
    assert [op.name for op in qb.Circuit(1).append(custom, [0]).decompose().operations] == ["x"]


@pytest.mark.parametrize("name,values", [("h", (.1,)), ("rx", ()), ("ry", (.1, .2)), ("u", (.1,)), ("cx", (.1,))])
def test_standard_definition_rejects_wrong_parameter_arity(name, values):
    with pytest.raises(ValueError): standard_gate_definition(name, *values)
