# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual SDK readers of independent legacy u records, not writer-history claims."""

import io

import numpy as np
import pytest

from quantumbridge.serialization import qpy_dumps, qpy_loads
from quantumbridge.information import Operator
from tests.serialization.test_qpy_v13_substitution import CASES, case_records, expression, phase_circuit
from tests.serialization.test_qpy_v13_parameter_replay import circuit_bytes


@pytest.mark.parametrize("case", CASES)
def test_actual_sdk_reads_legacy_substitution_and_bilateral_rewrites_execute(case):
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    records, symbols, names, numeric = case_records(case)
    payload = circuit_bytes(expression(records, symbols))
    public = qpy.load(io.BytesIO(payload))[0]
    assert tuple(p.name for p in public.parameters) == names
    native = qpy_loads(payload)[0]
    assert [(p.name, p.uuid) for p in native.parameters] == [(p.name, str(p.uuid)) for p in public.parameters]
    stream = io.BytesIO()
    qpy.dump(public, stream, version=13)
    returned = qpy_loads(stream.getvalue())[0]
    exported = qpy.load(io.BytesIO(qpy_dumps(native)))[0]
    for values in ((.17, -.38, .51)[:len(names)], (-.21, .43, -.62)[:len(names)]):
        mapping = dict(zip(names, values))
        angle = numeric(*values)
        expected = [[np.cos(angle/2), -1j*np.sin(angle/2)], [-1j*np.sin(angle/2), np.cos(angle/2)]]
        for circuit in (public, exported):
            np.testing.assert_allclose(PublicOperator(circuit.assign_parameters(mapping)).data,
                                       expected, atol=4e-15, rtol=0)
        for circuit in (native, returned):
            np.testing.assert_allclose(Operator(circuit.bind(mapping)).data, expected, atol=4e-15, rtol=0)


def test_actual_sdk_substitution_global_phase_has_full_complex_matrix():
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    records, symbols, _, numeric = case_records("nested")
    public = qpy.load(io.BytesIO(phase_circuit(expression(records, symbols))))[0]
    native = qpy_loads(phase_circuit(expression(records, symbols)))[0]
    angle = numeric(.17, -.38)
    expected = np.exp(1j*angle)*np.array([[np.cos(angle/2), -1j*np.sin(angle/2)],
                                       [-1j*np.sin(angle/2), np.cos(angle/2)]])
    np.testing.assert_allclose(PublicOperator(public.assign_parameters({"q": .17, "r": -.38})).data,
                               expected, atol=4e-15, rtol=0)
    np.testing.assert_allclose(Operator(native.bind({"q": .17, "r": -.38})).data,
                               expected, atol=4e-15, rtol=0)


def test_native_retained_formals_actual_api_binding_and_rewrite_stability():
    import quantumbridge as qb
    from qiskit import qpy,QuantumCircuit
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator as PublicOperator
    p,q,r=(qb.Parameter(name) for name in ("p","q","r"))
    pp,qq,rr=(Parameter(x.name,uuid=__import__("uuid").UUID(x.uuid)) for x in (p,q,r))
    native=(p+q*q).subs({p:r.sin()}).gradient(r)
    public=(pp+qq*qq).subs({pp:rr.sin()}).gradient(rr)
    assert sorted((p.name,p.uuid) for p in native.parameters) == sorted((p.name,str(p.uuid)) for p in public.parameters)
    assert native._dependencies == {r} and native.op == "cos"
    for expression,formal,real in ((native,q,r),(public,qq,rr)):
        bound=expression.bind({real:.31})
        assert {p.name for p in bound.parameters} == {"q"}
        with pytest.raises(TypeError):bound.numeric()
        assert bound.numeric(strict=False) == pytest.approx(np.cos(.31),abs=2e-15)
        assert float(bound) == pytest.approx(np.cos(.31),abs=2e-15)
        assert expression.bind({formal:.2}).parameters == {real}
    circuit=qb.Circuit(1).rx(native,0)
    sizes=[]
    for _ in range(3):
        encoded=qpy_dumps(circuit);sizes.append(len(encoded))
        loaded=qpy.load(io.BytesIO(encoded))[0]
        assert [(p.name,str(p.uuid)) for p in loaded.parameters] == [(p.name,p.uuid) for p in circuit.parameters]
        partial=loaded.assign_parameters({"r":.31})
        assert [p.name for p in partial.parameters] == ["q"]
        expected=PublicOperator(partial).data
        np.testing.assert_allclose(Operator(circuit.assign_parameters({r:.31})).data,expected,atol=3e-15,rtol=0)
        stream=io.BytesIO();qpy.dump(loaded,stream,version=13)
        circuit=qpy_loads(stream.getvalue())[0]
        assert circuit.operations[0].params[0].op == "cos"
        assert circuit.operations[0].params[0]._dependencies == {r}
    assert len(set(sizes)) == 1
