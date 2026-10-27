# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual installed SDK oracles; no absent-SDK fallback or hidden xfail."""

import io
from uuid import UUID

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps, qpy_loads
from tests.serialization.test_qpy_v13_parameter_replay import (
    IDS, circuit_bytes, expression, recursive_records, record,
)


@pytest.mark.parametrize("writer", ["native", "public"])
@pytest.mark.parametrize("reader", ["native", "public"])
def test_original_annotation_index_four_direction_diagnosis(writer, reader):
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import AnnotatedOperation, InverseModifier, Parameter
    from qiskit.circuit.library import RXGate
    if writer == "native":
        parameter = qb.Parameter("p", IDS["p"])
        op = qb.AnnotatedOperation(qb.Gate("rx", 1, [parameter]), qb.InverseModifier())
        payload = qpy_dumps(qb.Circuit(1).append(op, [0]))
    else:
        parameter = Parameter("p", uuid=IDS["p"])
        circuit = QuantumCircuit(1)
        circuit.append(AnnotatedOperation(RXGate(parameter), InverseModifier()), [0])
        stream = io.BytesIO()
        qpy.dump(circuit, stream, version=13)
        payload = stream.getvalue()
    assert payload[6] == 13
    if reader == "native":
        restored = qpy_loads(payload)[0]
        assert [(p.name, p.uuid) for p in restored.parameters] == [("p", str(IDS["p"]))]
        bound = restored.bind({restored.parameters[0]: .3})
        np.testing.assert_allclose(Operator(bound).data,
                                   [[np.cos(.15), 1j*np.sin(.15)],
                                    [1j*np.sin(.15), np.cos(.15)]], atol=3e-15, rtol=0)
    else:
        restored = qpy.load(io.BytesIO(payload))[0]
        # Diagnosis, NOT a parity pass: both installed public versions lose
        # their own circuit index while the annotation retains the UUID.
        assert len(restored.parameters) == 0
        assert [(p.name, p.uuid) for p in restored.data[0].operation.params] == [("p", IDS["p"])]


@pytest.mark.parametrize("side", ["left", "right"])
def test_independent_recursive_fixture_actual_public_reader(side):
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    payload = circuit_bytes(expression(recursive_records(side=side)))
    restored = qpy.load(io.BytesIO(payload))[0]
    assert [(p.name, p.uuid) for p in restored.parameters] == [(name, IDS[name]) for name in ("p", "q", "r")]
    point = {"p": .17, "q": -.38, "r": .51}
    angle = point["r"]**2 + (point["p"]+point["q"])/2
    expected = [[np.cos(angle/2), -1j*np.sin(angle/2)], [-1j*np.sin(angle/2), np.cos(angle/2)]]
    np.testing.assert_allclose(PublicOperator(restored.assign_parameters(point)).data,
                               expected, atol=3e-15, rtol=0)


def test_independent_gradient_fixture_actual_public_reader():
    from qiskit import qpy
    payload = circuit_bytes(expression([
        record(5, b"p", IDS["p"].bytes), record(2, right=b"p", rhs=IDS["q"].bytes),
        record(13, right=b"p", rhs=IDS["p"].bytes)], ("q", "p")))
    restored = qpy.load(io.BytesIO(payload))[0]
    assert [(p.name, p.uuid) for p in restored.parameters] == [(name, IDS[name]) for name in ("p", "q")]
    value = float(restored.data[0].operation.params[0].bind({p: {"p": .31, "q": -.42}[p.name]
                                                          for p in restored.parameters}))
    assert value == pytest.approx(-.42*np.cos(.31), abs=2e-15)


@pytest.mark.parametrize("writer", ["native", "public"])
@pytest.mark.parametrize("reader", ["native", "public"])
@pytest.mark.parametrize("case", ["single", "sparse_vector", "regrown_vector", "two_vectors", "nested", "partial", "repeated_uuid"])
def test_parameter_identity_and_full_math_four_directions(writer, reader, case):
    import qiskit
    from qiskit import QuantumCircuit, qpy
    from qiskit.circuit import Parameter, ParameterVector
    from qiskit.quantum_info import Operator as PublicOperator
    Circuit, Scalar, Vector = ((qb.Circuit, qb.Parameter, qb.ParameterVector) if writer == "native"
                                else (QuantumCircuit, Parameter, ParameterVector))
    p = Scalar("p", uuid=UUID(int=111))
    q = Scalar("q", uuid=UUID(int=222))
    circuit = Circuit(1)
    if case == "single":
        angle, values = p, {"p": .21}
    elif case in {"sparse_vector", "regrown_vector"}:
        vector = Vector("angles", 12)
        before = [str(value.uuid) for value in vector]
        if case == "regrown_vector":
            vector.resize(2)
            vector.resize(12)
            assert [str(value.uuid) for value in vector] == before
        angle, values = vector[10]**2 + vector[2]/2, {"angles[2]": -.27, "angles[10]": .41}
    elif case == "two_vectors":
        a, b = Vector("a", 3), Vector("b", 3)
        angle, values = a[2]-b[2], {"a[2]": .21, "b[2]": -.34}
    elif case == "nested":
        angle, values = (p.sin()+q**2)/(q+2), {"p": .21, "q": -.34}
    elif case == "partial":
        angle, values = (p.sin()+q**2).assign(p, .21), {"q": -.34}
    else:
        alias = Scalar("p", uuid=UUID(int=111))
        angle, values = p*alias + q, {"p": .21, "q": -.34}
    circuit.rx(angle, 0)
    circuit.global_phase = angle/7
    identities = [(x.name, str(x.uuid), getattr(x, "index", None),
                   len(x.vector) if getattr(x, "index", None) is not None else None) for x in circuit.parameters]
    if writer == "native":
        payload = qpy_dumps(circuit)
        expected = Operator(circuit.bind(values)).data
    else:
        stream = io.BytesIO()
        qpy.dump(circuit, stream, version=13)
        payload = stream.getvalue()
        expected = PublicOperator(circuit.assign_parameters(values)).data
    if case == "partial" and writer == "public" and qiskit.__version__ == "2.4.1":
        # An upstream-produced malformed replay is a diagnosis, not a native
        # identity/mathematics pass. The original red receipt retains both errors.
        from quantumbridge.serialization import FormatValidationError
        from qiskit.qpy import QpyError
        load = (lambda: qpy_loads(payload)) if reader == "native" else (lambda: qpy.load(io.BytesIO(payload)))
        error = FormatValidationError if reader == "native" else QpyError
        with pytest.raises(error, match="exactly one expression|malformed expression stack"):
            load()
        return
    restored = qpy_loads(payload)[0] if reader == "native" else qpy.load(io.BytesIO(payload))[0]
    actual_identities = [(x.name, str(x.uuid), getattr(x, "index", None),
                         len(x.vector) if getattr(x, "index", None) is not None else None) for x in restored.parameters]
    assert actual_identities == identities
    actual = Operator(restored.bind(values)).data if reader == "native" else PublicOperator(restored.assign_parameters(values)).data
    np.testing.assert_allclose(actual, expected, atol=5e-15, rtol=0)
