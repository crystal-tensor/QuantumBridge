# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Observable formal identities are not extra mathematical operands."""

import gc
from copy import deepcopy

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization import qpy_dumps, qpy_loads, SerializationError, SerializationLimits, ResourceLimitError


def source():
    p, q, r = (qb.Parameter(name) for name in ("p", "q", "r"))
    return q, r, (p+q*q).subs({p:r.sin()}).gradient(r)


def leaves(expression):
    if expression.op == "parameter":return {expression.args[0]}
    if expression.op == "const":return set()
    return set().union(*(leaves(child) for child in expression.args))


def test_retained_context_binds_and_differentiates_without_fabricated_ast_terms():
    q, r, h = source()
    assert h.parameters == {q, r} and h._dependencies == {r}
    assert h.op == "cos" and leaves(h) == {r}
    assert h._retained_parameters == {q}
    assert deepcopy(h).parameters == h.parameters
    numeric = h.bind({r:.31})
    assert numeric.parameters == {q} and numeric.op == "const"
    with pytest.raises(TypeError):numeric.numeric()
    assert numeric.numeric(strict=False) == pytest.approx(np.cos(.31), abs=2e-15)
    assert float(numeric) == pytest.approx(np.cos(.31), abs=2e-15)
    assert numeric.is_real() is True
    assert not h.bind({q:.2})._retained_parameters
    assert h.bind({q:.2,r:.31}) == pytest.approx(np.cos(.31), abs=2e-15)
    zero = h.gradient(q)
    assert type(zero) is float and zero == 0
    assert h.gradient(r).parameters == {q,r}
    assert h.gradient(r).bind({q:.2,r:.31}) == pytest.approx(-np.sin(.31), abs=2e-15)
    s = qb.Parameter("s")
    renamed = h.subs({q:s})
    assert renamed.parameters == {r,s} and leaves(renamed) == {r}
    assert renamed.bind({r:.31,s:.2}) == pytest.approx(np.cos(.31), abs=2e-15)


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("partial", [False, True])
def test_formal_context_roundtrip_is_stable_and_owned(format, partial):
    q, r, h = source()
    if partial:h = h.assign(r,.31)
    circuit = qb.Circuit(1).rx(h,0)
    sizes = []
    for _ in range(4):
        if format == "qpy":
            data = qpy_dumps(circuit);sizes.append(len(data));circuit=qpy_loads(data)[0]
        else:circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
        expected = {q} if partial else {q,r}
        assert set(circuit.parameters) == expected
        angle = circuit.operations[0].params[0]
        assert leaves(angle) == (set() if partial else {r})
        assert angle._retained_parameters == {q}
        assert angle._nodes == (1 if partial else 2)
    if sizes:assert len(set(sizes)) == 1
    if not partial:circuit=circuit.assign_parameters({r:.31})
    assert circuit.parameters == (q,)
    # Public numerical execution permits an irrelevant unbound formal; its
    # Circuit parameter table remains bindable until that identity is bound.
    from quantumbridge.information import Operator
    angle=np.cos(.31)
    np.testing.assert_allclose(Operator(circuit).data,
        [[np.cos(angle/2),-1j*np.sin(angle/2)],[-1j*np.sin(angle/2),np.cos(angle/2)]],atol=3e-15,rtol=0)
    assert not circuit.assign_parameters({q:.2}).parameters


@pytest.mark.parametrize("device", ["statevector", "mps"])
@pytest.mark.parametrize("partial", [False, True])
def test_formal_zero_direction_compiler_and_real_ad(device, partial):
    from quantumbridge.compiler import native_transpile
    from quantumbridge.qml import QNode
    q, r, h = source()
    circuit=qb.Circuit(1).rx(h,0)
    if partial:circuit=circuit.assign_parameters({r:.31})
    compiled=native_transpile(qb.Circuit(1).compose(circuit.copy()),basis_gates=["rz","sx","cx"],optimization_level=0)
    assert set(compiled.parameters) == ({q} if partial else {q,r})
    executor=qb.StatevectorDevice() if device == "statevector" else qb.MatrixProductStateDevice(max_bond_dim=2,cutoff=0)
    node=QNode.from_circuit(compiled,qb.PauliZ(0),max_diff=2,device=executor)
    point=np.array([.2] if partial else [.2,.31])
    direction=np.array([.7] if partial else [.7,-.2])
    gradient=np.zeros(len(point));hessian=np.zeros((len(point),len(point)))
    if not partial:
        gradient[1]=np.sin(np.cos(.31))*np.sin(.31)
        hessian[1,1]=-np.cos(np.cos(.31))*np.sin(.31)**2+np.sin(np.cos(.31))*np.cos(.31)
    np.testing.assert_allclose(node(point),np.cos(np.cos(.31)),atol=3e-13,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(point),gradient,atol=2e-10,rtol=0)
    np.testing.assert_allclose(node.compute_jvp(direction,point),gradient@direction,atol=2e-10,rtol=0)
    np.testing.assert_allclose(node.compute_vjp(.4,point),.4*gradient,atol=2e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(direction,point),hessian@direction,atol=4e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point),hessian,atol=4e-10,rtol=0)


def test_context_limits_and_unsupported_owner_precede_publication():
    from quantumbridge.core import SymbolicExpressionLimits, symbolic_expression_scope
    from quantumbridge.core.symbolic_limits import SymbolicResourceLimitError
    q,r,h=source()
    class Foreign:
        @property
        def name(self):pytest.fail("Foreign retained owner inspected")
    with pytest.raises(TypeError):qb.ParameterExpression("cos",(r.expression(),),_retained_parameters=frozenset({Foreign()}))
    with pytest.raises(ValueError):qb.ParameterExpression("cos",(r.expression(),),_retained_parameters=frozenset({qb.Parameter("r")}))
    with pytest.raises(ValueError):qb.ParameterExpression("cos",(r.expression(),),_retained_parameters=frozenset({qb.Parameter("q",r.uuid)}))
    with symbolic_expression_scope(SymbolicExpressionLimits(max_parameters=1)):
        with pytest.raises(SymbolicResourceLimitError):h.simplify()
    circuit=qb.Circuit(1).rx(h,0)
    before=circuit.to_ir().to_json()
    with pytest.raises(ResourceLimitError):qpy_dumps(circuit,limits=SerializationLimits(max_parameter_nodes=2))
    assert circuit.to_ir().to_json() == before


def test_failed_projection_releases_logical_numerical_storage_and_recovers(monkeypatch):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    q,r,h=source();circuit=qb.Circuit(1).rx(h,0)
    before=circuit.to_ir().to_json();ledger=UnifiedResourceLedger()
    import quantumbridge.serialization.qpy as qpy_codec
    actual=qpy_codec._parameter_value
    def fail(value,*args,**kwargs):
        if type(value) is type(q) and value == q:raise RuntimeError("injected formal projection failure")
        return actual(value,*args,**kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(qpy_codec,"_parameter_value",fail)
        with ResourceScope(ledger),pytest.raises(RuntimeError,match="injected"):
            qpy_dumps(circuit)
    gc.collect();assert ledger.receipt()["live_memory_bytes"] == 0
    assert circuit.to_ir().to_json() == before
    assert set(qpy_loads(qpy_dumps(circuit))[0].parameters) == {q,r}


def test_retained_vector_context_survives_regrowth_and_refuses_orphan_export():
    vector=qb.ParameterVector("angles",12)
    q,r=vector[2],vector[10]
    h=(r.sin()+q*q).gradient(r)
    assert h.parameters == {q,r} and h._dependencies == {r}
    original=[p.uuid for p in vector]
    vector.resize(2)
    with pytest.raises(SerializationError):qpy_dumps(qb.Circuit(1).rx(h,0))
    vector.resize(12)
    assert [p.uuid for p in vector] == original
    restored=qpy_loads(qpy_dumps(qb.Circuit(1).rx(h,0)))[0]
    a,b=restored.parameters
    assert (a.index,b.index) == (2,10) and a.vector is b.vector
    assert restored.operations[0].params[0]._dependencies == {r}
    assert restored.operations[0].params[0]._retained_parameters == {q}
