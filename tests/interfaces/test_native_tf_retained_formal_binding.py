# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Retained-only identities survive real frozen QNode and TensorFlow AD paths."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")


def make(partial=False, mps=False, max_diff=2):
    vector = qb.ParameterVector("angles", 12)
    q,r = vector[2],vector[10]
    angle = (r.sin()+q*q).gradient(r)
    if partial:
        angle = angle.assign(r,.31)
    circuit = qb.Circuit(1).rx(angle,0)
    device = qb.MatrixProductStateDevice(max_bond_dim=2,cutoff=0) if mps else qb.StatevectorDevice()
    node = QNode.from_circuit(circuit,qb.PauliZ(0),interface="tensorflow",
        diff_method="mps-tangent" if mps else "adjoint",max_diff=max_diff,device=device,
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((1 if partial else 2,),tf.float64)],
        max_derivative_order=max_diff)
    return node,circuit,handle


@pytest.mark.parametrize("partial", [False, True])
def test_native_frozen_tensor_map_has_true_zero_ad_without_private_rules(partial):
    q,r = qb.Parameter("q"),qb.Parameter("r")
    expression = (r.sin()+q*q).gradient(r)
    if partial:
        expression = expression.assign(r,.31)
    binding = FrozenParameterBinding.create((q,) if partial else (q,r),(expression,))
    point = tf.constant([.2] if partial else [.2,.31],tf.float64)
    direction = tf.constant([.7] if partial else [.7,-.2],tf.float64)
    with tf.autodiff.ForwardAccumulator(point,direction) as forward:
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            value = tf.convert_to_tensor(binding.evaluate(tuple(tf.unstack(point)))[0],tf.float64)
        gradient = reverse.gradient(value,point,unconnected_gradients=tf.UnconnectedGradients.ZERO)
    product = forward.jvp(gradient)
    # A completely constant AST has no TensorFlow edge. The existing native
    # interface normalizes this documented unconnected case, not arbitrary None.
    if partial:
        assert product is None
        np.testing.assert_array_equal(gradient,[0.])
    else:
        assert product is not None
        np.testing.assert_allclose(gradient,[0.,-np.sin(.31)],atol=2e-15,rtol=0)
        np.testing.assert_allclose(product,[0.,.2*np.cos(.31)],atol=2e-15,rtol=0)


@pytest.mark.parametrize("mps", [False, True])
@pytest.mark.parametrize("partial", [False, True])
def test_managed_formal_parameters_keep_owned_zero_jvp_vjp_and_streamed_hvp(partial,mps,monkeypatch):
    captured = []
    original = FrozenParameterBinding.create.__func__
    def capture(cls,*args,**kwargs):
        result = original(cls,*args,**kwargs)
        captured.append(result)
        return result
    monkeypatch.setattr(FrozenParameterBinding,"create",classmethod(capture))
    node,circuit,handle = make(partial,mps)
    binding = handle._frozen_binding
    assert type(binding) is FrozenParameterBinding
    assert len(captured) == 2
    assert binding.parameters is captured[1].parameters is captured[0].parameters
    assert binding.node_count == captured[1].node_count == captured[0].node_count
    assert all(any(expression is original for original in captured[1].expressions)
        for expression in binding.expressions)
    if partial:
        assert not binding.expressions and captured[0].expressions
    assert binding.parameters == circuit.parameters
    assert [p.index for p in binding.parameters] == ([2] if partial else [2,10])
    if not partial:
        assert any(p.index == 2 for expression in binding.expressions for p in expression._retained_parameters)
    before = circuit.to_ir().to_json()
    point = tf.constant([.2] if partial else [.2,.31],tf.float64)
    direction = tf.constant([.7] if partial else [.7,-.2],tf.float64)
    gradient = np.zeros(len(point))
    hvp = gradient.copy()
    if not partial:
        gradient[1] = np.sin(np.cos(.31))*np.sin(.31)
        hvp[1] = -.2*(-np.cos(np.cos(.31))*np.sin(.31)**2+np.sin(np.cos(.31))*np.cos(.31))
    parent = UnifiedResourceLedger()
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(child):
        for kind in ("value","jvp","vjp","hvp","hvp"):
            request = DerivativeExecutionRequest(node,point,derivative_kind=kind,
                derivative_order=0 if kind == "value" else 2 if kind == "hvp" else 1,
                tangent=direction if kind in {"jvp","hvp"} else None,
                cotangent=tf.constant([.4],tf.float64) if kind == "vjp" else None)
            result = handle.execute(request)
            np.testing.assert_allclose(result.value,np.cos(np.cos(.31)),atol=3e-13,rtol=0)
            expected = {"jvp":gradient@np.asarray(direction),"vjp":.4*gradient,"hvp":hvp}.get(kind)
            if expected is not None:
                np.testing.assert_allclose(np.asarray(result.derivative).reshape(-1),
                    np.asarray(expected).reshape(-1),atol=4e-10,rtol=0)
    assert parent.receipt()["consumed_derivative_work"] == child.receipt()["consumed_derivative_work"] > 0
    assert parent.receipt()["live_memory_bytes"] == child.receipt()["live_memory_bytes"] == 0
    assert circuit.to_ir().to_json() == before
    assert handle.cache_info()["aborted_calls"] == 0


@pytest.mark.parametrize("partial", [False,True])
@pytest.mark.parametrize("mps", [False,True])
def test_nonlinear_loss_curvature_and_zero_tangent_use_real_managed_graphs(partial,mps):
    node,_,handle = make(partial,mps)
    point = tf.constant([.2] if partial else [.2,.31],tf.float64)
    direction = tf.constant([.7] if partial else [.7,-.2],tf.float64)
    def evaluate(x,d):
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x,d) as forward:
                value = handle(x)
                loss = tf.exp(value)+.2*value**3
            tangent = forward.jvp(loss)
        return value,reverse.gradient(tangent,x)
    value,product = evaluate(point,direction)
    expected = np.zeros(len(point))
    if not partial:
        y = np.cos(np.cos(.31))
        first = np.sin(np.cos(.31))*np.sin(.31)
        second = -np.cos(np.cos(.31))*np.sin(.31)**2+np.sin(np.cos(.31))*np.cos(.31)
        expected[1] = -.2*((np.exp(y)+1.2*y)*first**2+(np.exp(y)+.6*y*y)*second)
    assert product is not None
    np.testing.assert_allclose(product,expected,atol=4e-10,rtol=0)
    shifted = tf.constant([99.] if partial else [99.,.31],tf.float64)
    np.testing.assert_array_equal(handle(shifted),value)
    _,zero = evaluate(point,tf.zeros_like(point))
    assert zero is not None
    np.testing.assert_array_equal(zero,np.zeros(len(point)))


@pytest.mark.parametrize("partial", [False,True])
@pytest.mark.parametrize("field,key", [("max_total_memory_bytes","required_memory_bytes"),
    ("max_derivative_work","first_call_work"),("max_total_tapes","logical_evaluations")])
def test_zero_formal_derivative_does_not_bypass_managed_admission(partial,field,key,monkeypatch):
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    node,_,handle = make(partial)
    point = tf.constant([.2] if partial else [.2,.31],tf.float64)
    query = DerivativeExecutionRequest(node,point,derivative_kind="hvp",derivative_order=2,
        tangent=tf.zeros_like(point))
    work = handle.estimate(query)
    assert work[key] > 0
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(**{field:work[key]-1}))
    with monkeypatch.context() as patch:
        patch.setattr(handle,"_run_graph",lambda *a:pytest.fail("Refused formal query executed"))
        with ResourceScope(ledger),pytest.raises(MemoryError):
            handle.execute(query)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["consumed_tapes"] == 0
    with ResourceScope(UnifiedResourceLedger()):
        result = handle.execute(query)
    np.testing.assert_array_equal(result.derivative,np.zeros_like(result.derivative))


@pytest.mark.parametrize("mps", [False, True])
def test_managed_formal_map_first_order_cap_and_source_snapshot(mps):
    node,circuit,handle = make(mps=mps,max_diff=1)
    point = tf.constant([.2,.31],tf.float64)
    before = tf.stack(handle(point))
    circuit.x(0)
    np.testing.assert_array_equal(tf.stack(handle(point)),before)
    with pytest.raises((ValueError, qb.UnsupportedFeature),match="order|second|derivative"):
        handle.execute(DerivativeExecutionRequest(node,point,derivative_kind="hvp",derivative_order=2,
            tangent=tf.constant([.7,-.2],tf.float64)))
    owner = circuit.parameters[0].vector
    owner.resize(14)
    with pytest.raises(qb.UnsupportedFeature,match="identity|changed"):
        handle(point)
    owner.resize(12)
    np.testing.assert_array_equal(tf.stack(handle(point)),before)


@pytest.mark.parametrize("kind", ["surplus", "missing", "foreign", "oversize", "wrong_math",
    "wrong_uuid","extra_output","forged_ast","unproved_function"])
def test_captured_binding_requires_full_native_readmission_before_projection(kind,monkeypatch):
    p,q = qb.Parameter("p"),qb.Parameter("q")
    class Foreign:
        @property
        def parameters(self):
            pytest.fail("Foreign captured owner property was inspected")
    expressions = (qb.ParameterExpression("const",(2.,)),) if kind == "surplus" else (p+q,)
    if kind == "wrong_math":
        expressions = (p*2,)
    elif kind == "unproved_function":
        expressions = (p,)
    elif kind == "wrong_uuid":
        expressions = (qb.Parameter("p"),)
    elif kind == "extra_output":
        expressions = (p,p)
    elif kind == "forged_ast":
        invalid = object.__new__(qb.ParameterExpression)
        object.__setattr__(invalid,"op","unvalidated")
        object.__setattr__(invalid,"args",())
        expressions = (invalid,)
    if kind == "oversize":
        expression = p.expression()
        for _ in range(25):
            expression = expression.sin()
        expressions = (expression,)
    captured = Foreign() if kind == "foreign" else FrozenParameterBinding((p,),expressions,0)
    def program(tape,point):
        tape.ry(tf.tanh(point[0]) if kind == "unproved_function" else point[0],0)
        tape._native_parameter_binding = (captured,tuple(tape.parameter_transform.parameters))
        return tape.expval(qb.PauliZ(0))
    node = QNode(program,1,interface="tensorflow",diff_method="adjoint",max_diff=2,
        higher_order_limits=HigherOrderLimits(max_parameter_graph_nodes=20 if kind == "oversize" else 100000))
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    from quantumbridge.interfaces.native_host import NativeHostKernel
    def forbidden(*a,**k):
        pytest.fail("Unproved captured source reached quantum graph construction/execution")
    monkeypatch.setattr(TensorFlowStatevectorPlan,"__init__",forbidden)
    monkeypatch.setattr(NativeHostKernel,"run",forbidden)
    expected = MemoryError if kind == "oversize" else (ValueError,TypeError,qb.UnsupportedFeature)
    identity = str(p.uuid)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger),pytest.raises(expected):
        node.compile_tensorflow(input_signature=[tf.TensorSpec((1,),tf.float64)])
    assert str(p.uuid) == identity
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0


@pytest.mark.parametrize("kind", ["unsupported", "nonfinite"])
def test_partial_native_capture_needs_complete_proved_source_not_legacy_fallback(kind,monkeypatch):
    import quantumbridge.interfaces.tensorflow_managed as managed
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    p,q = qb.ParameterVector("input",2)
    builder = QNode.from_circuit(qb.Circuit(1).ry(p*p+q,0),qb.PauliZ(0)).fn
    def program(tape,point):
        result = builder(tape,point)
        angle = tf.tan(point[0]) if kind == "unsupported" else point[0]+tf.constant(float("nan"),tf.float64)
        tape.rx(angle,0)
        return result
    def forbidden(*a,**k):
        pytest.fail("Partial capture published an unproved old query or a quantum tensor plan")
    monkeypatch.setattr(managed,"_admit_legacy_scalar_query",forbidden)
    monkeypatch.setattr(TensorFlowStatevectorPlan,"__init__",forbidden)
    node = QNode(program,1,interface="tensorflow",diff_method="adjoint",max_diff=2)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger),pytest.raises(qb.UnsupportedFeature):
        node.compile_tensorflow(input_signature=[tf.TensorSpec((2,),tf.float64)])
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0


def test_complete_lowered_partial_capture_keeps_all_gate_occurrences_and_wire_targets():
    vector = qb.ParameterVector("source",12)
    p,q = vector[2],vector[10]
    source = qb.Circuit(3).ry(p*p+q,2).rz(p*p+q,0)
    before = source.to_ir().to_json()
    builder = QNode.from_circuit(source,qb.PauliZ(2)).fn
    def program(tape,point):
        result = builder(tape,point)
        tape.rx(.2*point[0],2)
        return result
    node = QNode(program,3,interface="tensorflow",diff_method="adjoint",max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,),tf.float64)])
    binding = handle._frozen_binding
    operations = handle._whole._circuit.operations
    slots = handle._whole._parameters
    assert len(binding.expressions) == len(slots) == len(operations) == 3
    assert [(op.name,op.wires) for op in operations] == [("ry",(2,)),("rz",(0,)),("rx",(2,))]
    for operation,slot in zip(operations,slots):
        assert operation.params[0].parameters == {slot}
    for x,z in ((.37,.82),(.41,.91)):
        np.testing.assert_allclose(binding.evaluate((x,z)),[x*x+z,x*x+z,.2*x],atol=2e-15,rtol=0)
        np.testing.assert_allclose(handle(tf.constant([x,z],tf.float64)),
            np.cos(x*x+z)*np.cos(.2*x),atol=3e-13,rtol=0)
    assert source.to_ir().to_json() == before
    assert [parameter.index for parameter in source.parameters] == [2,10]
