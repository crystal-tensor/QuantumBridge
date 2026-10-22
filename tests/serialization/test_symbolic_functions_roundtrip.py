# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real source/binary roundtrips for symbolic functions, not private QPY JSON."""

import io

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, ParameterVector, ParameterVectorElement
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir import IRProgram
from quantumbridge.serialization import qasm3_dumps, qasm3_loads, qpy_dumps, qpy_loads
from quantumbridge.serialization.errors import UnsupportedFeature, SerializationError
from quantumbridge.core import SymbolicExpressionLimits, symbolic_expression_scope
from quantumbridge.serialization.errors import ResourceLimitError
from quantumbridge.serialization.limits import SerializationLimits


FUNCTIONS = ["sin", "cos", "tan", "exp", "log", "arcsin", "arccos", "arctan", "abs", "sign", "conjugate"]


@pytest.mark.parametrize("name", FUNCTIONS)
@pytest.mark.parametrize("format", ["ir-json", "qpy", "qasm3"])
def test_native_symbolic_functions_roundtrip_with_executable_partial_binding(name, format):
    p, q = Parameter("theta"), Parameter("phi")
    expression = getattr(p, name)()+q.sin()
    circuit = Circuit(1).ry(expression, 0)
    circuit.global_phase = q.exp()/7
    if format == "ir-json": restored = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif format == "qpy": restored = qpy_loads(qpy_dumps(circuit))[0]
    elif name in {"sign", "conjugate"}:
        with pytest.raises(UnsupportedFeature): qasm3_dumps(circuit)
        return
    else: restored = qasm3_loads(qasm3_dumps(circuit))
    if format != "qasm3": assert set(restored.parameters) == {p, q}
    for theta, phi in ((.2, -.3), (.4, .5), (.8, 1.1)):
        actual = restored.assign_parameters({"theta": theta}).assign_parameters({"phi": phi})
        expected = circuit.assign_parameters({p: theta, q: phi})
        np.testing.assert_allclose(Operator(actual).data, Operator(expected).data, atol=5e-15, rtol=0)


@pytest.mark.parametrize("name", FUNCTIONS)
def test_optional_public_binary_bilateral_elementary_function_interoperability(name):
    public = pytest.importorskip("qiskit")
    public_qpy = pytest.importorskip("qiskit.qpy")
    from qiskit.circuit import Parameter as PublicParameter
    from qiskit.quantum_info import Operator as PublicOperator
    p = Parameter("theta")
    native = Circuit(1).ry(getattr(p, name)(), 0)
    native.global_phase = p.sin()/7
    imported = public_qpy.load(io.BytesIO(qpy_dumps(native)))[0]
    assert str(next(iter(imported.parameters)).uuid) == p.uuid
    pp = PublicParameter("theta")
    exported = public.QuantumCircuit(1)
    exported.ry(getattr(pp, name)(), 0)
    exported.global_phase = pp.sin()/7
    stream = io.BytesIO(); public_qpy.dump(exported, stream, version=13)
    restored = qpy_loads(stream.getvalue())[0]
    for value in (.2, .4, .8):
        expected = PublicOperator(exported.assign_parameters({pp: value})).data
        np.testing.assert_allclose(Operator(native.bind({p: value})).data, expected, atol=5e-15, rtol=0)
        np.testing.assert_allclose(Operator(restored.bind({"theta": value})).data, expected, atol=5e-15, rtol=0)
        np.testing.assert_allclose(PublicOperator(imported.assign_parameters({"theta": value})).data, expected, atol=5e-15, rtol=0)


@pytest.mark.parametrize("format", ["ir-json", "qpy", "qasm3"])
def test_symbolic_serialization_byte_budget_applies_before_transport_joins(format):
    p = Parameter("theta")
    circuit = Circuit(1).ry(p.sin(), 0)
    dump, load = ((lambda c: c.to_ir().to_json(), IRProgram.from_json) if format == "ir-json"
                  else (qpy_dumps, qpy_loads) if format == "qpy" else (qasm3_dumps, qasm3_loads))
    payload = dump(circuit)
    with symbolic_expression_scope(SymbolicExpressionLimits(max_serialized_bytes=16)):
        with pytest.raises(ResourceLimitError): dump(circuit)
        with pytest.raises(ResourceLimitError): load(payload)


def test_ir_symbolic_depth_and_aggregate_nodes_reject_before_recursive_construction():
    p = Parameter("theta")
    circuit = Circuit(1).rx(p.sin().cos().exp(), 0)
    payload = circuit.to_ir().to_dict()
    with pytest.raises(ResourceLimitError, match="depth"):
        IRProgram.from_dict(payload, serialization_limits=SerializationLimits(max_symbolic_expression_depth=1))
    for _ in range(4): circuit.ry(p.sin(), 0)
    with pytest.raises(ResourceLimitError, match="max_parameter_nodes"):
        IRProgram.from_dict(circuit.to_ir().to_dict(), serialization_limits=SerializationLimits(max_parameter_nodes=8))


@pytest.mark.parametrize("format", ["qpy", "ir-json"])
def test_complex_intermediate_cancellation_survives_binary_or_ir_without_a_real_cast(format):
    p = Parameter("theta")
    circuit = Circuit(1).ry((p+1j).conjugate()+1j, 0)
    restored = (qpy_loads(qpy_dumps(circuit))[0] if format == "qpy" else
                circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json())))
    assert set(restored.parameters) == {p}
    np.testing.assert_allclose(Operator(restored.bind({p: .4})).data, Operator(Circuit(1).ry(.4, 0)).data, atol=2e-15, rtol=0)


def test_optional_public_qpy_nested_calculus_and_simultaneous_replacements_are_executable():
    public = pytest.importorskip("qiskit")
    public_qpy = pytest.importorskip("qiskit.qpy")
    from qiskit.circuit import Parameter as PublicParameter
    from qiskit.quantum_info import Operator as PublicOperator
    p, q = PublicParameter("theta"), PublicParameter("phi")
    expression = (p*q+p**2).sin()+(2*p-q).exp()
    source = public.QuantumCircuit(1)
    source.ry(expression, 0)
    source.rz(expression.gradient(p).subs({p: q, q: p}), 0)
    source.global_phase = (p+1).log()/7
    stream = io.BytesIO(); public_qpy.dump(source, stream, version=13)
    restored = qpy_loads(stream.getvalue())[0]
    for theta, phi in ((.2, -.3), (.4, .5), (.8, 1.1)):
        mapping = {"theta": theta, "phi": phi}
        np.testing.assert_allclose(Operator(restored.bind(mapping)).data,
                                   PublicOperator(source.assign_parameters(mapping)).data, atol=8e-15, rtol=0)


def test_qasm_symbolic_functions_keep_loop_locals_distinct_from_free_inputs():
    from quantumbridge import DensityMatrixDevice
    source = ('OPENQASM 3.0; include "stdgates.inc"; input float[64] theta; '
              'qubit q; for int i in {0,1} { ry(sin(theta+i)) q; }')
    circuit = qasm3_loads(source)
    assert [p.name for p in circuit.parameters] == ["theta"]
    restored = qasm3_loads(qasm3_dumps(circuit))
    for value in (.2, -.7, .8):
        expected = DensityMatrixDevice().density_matrix(Circuit(1).ry(np.sin(value)+np.sin(value+1), 0))
        np.testing.assert_allclose(DensityMatrixDevice().density_matrix(restored.bind({"theta": value})), expected, atol=4e-15, rtol=0)


@pytest.mark.parametrize("kind", ["scalar_first", "vector_first", "shared_expression"])
def test_qpy_never_merges_scalar_and_vector_kinds_with_colliding_display_names(kind):
    from quantumbridge.core import Operation
    vector = ParameterVector("v", 2)
    parameter = vector[1]
    alias = Parameter(parameter.name, parameter.uuid)
    assert alias != parameter
    if kind == "shared_expression":
        with pytest.raises(ValueError, match="Conflicting"):
            parameter.sin()+alias.cos()
        return
    first, second = (alias, parameter) if kind == "scalar_first" else (parameter, alias)
    with pytest.raises(ValueError, match="Conflicting"):
        Circuit(1).rx(first, 0).ry(second.sin(), 0)
    malformed = Circuit(1)
    malformed.operations.extend((Operation("rx", (0,), params=(first,)), Operation("ry", (0,), params=(second.sin(),))))
    with pytest.raises(UnsupportedFeature, match="uniquely"):
        qpy_dumps(malformed)


@pytest.mark.parametrize("kind", ["scalar_first", "vector_first", "shared_expression"])
def test_optional_public_qpy_distinct_scalar_vector_kinds_are_an_explicit_native_boundary(kind):
    public = pytest.importorskip("qiskit")
    public_qpy = pytest.importorskip("qiskit.qpy")
    from qiskit.circuit import Parameter as PublicParameter, ParameterVector as PublicVector
    vector = PublicVector("v", 2)
    parameter = vector[1]
    alias = PublicParameter(parameter.name, uuid=parameter.uuid)
    circuit = public.QuantumCircuit(1)
    if kind == "shared_expression":
        # Matching displayed names/UUIDs do not erase the public symbol kind.
        from qiskit.circuit.exceptions import CircuitError
        assert alias != parameter
        with pytest.raises(CircuitError, match="Name conflict"):
            parameter.sin()+alias.cos()
        return
    else:
        first, second = (alias, parameter) if kind == "scalar_first" else (parameter, alias)
        circuit.rx(first, 0); circuit.ry(second.sin(), 0)
    stream = io.BytesIO(); public_qpy.dump(circuit, stream, version=13)
    with pytest.raises(SerializationError, match="Conflicting|Distinct"):
        qpy_loads(stream.getvalue())
