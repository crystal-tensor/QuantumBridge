# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Construction-stage exception atomicity through the real existing compiler."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from test_native_tf_scalar_graph_lowering import capture, tf
from test_native_tf_scalar_lowering_atomicity import compile_node, node_for


@pytest.mark.parametrize("failure", [RuntimeError, MemoryError, KeyboardInterrupt])
@pytest.mark.parametrize("phase", ["snapshot", "audit", "layout", "cost", "admission", "partial_ast", "binding"])
def test_lowering_exception_is_atomic_at_every_construction_phase(phase, failure, monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    graph, root, output = capture("reverse" if phase == "layout" else "nonlinear")
    parameters = tuple(qb.ParameterVector("registered", 2))
    source = qb.Circuit(1).ry(parameters[0]+parameters[1], 0)
    source_before = source.to_ir().to_json()
    identities = tuple(p.uuid for p in parameters)
    parent, published, created, injected = UnifiedResourceLedger(), [], [], []
    child = UnifiedResourceLedger(parent=parent)
    def reject(*args, **kwargs):
        injected.append(phase)
        raise failure("injected scalar "+phase)
    constructor = module.ParameterExpression
    def count_nodes(*args, **kwargs):
        if phase == "partial_ast" and len(created) == 3:
            reject()
        result = constructor(*args, **kwargs)
        created.append(result)
        return result
    with monkeypatch.context() as patch:
        patch.setattr(module, "ParameterExpression", count_nodes)
        if phase == "snapshot":
            patch.setattr(tf.compat.v1.GraphDef, "CopyFrom", reject)
        elif phase == "audit":
            patch.setattr(tf.DeviceSpec, "from_string", reject)
        elif phase == "layout":
            patch.setattr(module.np, "flip", reject)
        elif phase == "cost":
            maximum = len(graph.node)+sum(np.prod([d.size for d in s.dim], dtype=np.int64)
                for n in graph.node for s in n.attr["_output_shapes"].list.shape)
            check = HigherOrderLimits.check
            def fail_cost(self, name, count):
                if name == "max_adjoint_operations" and count > maximum:
                    reject()
                return check(self, name, count)
            patch.setattr(HigherOrderLimits, "check", fail_cost)
        elif phase == "admission":
            reserve = child.reserve
            def fail_reservation(category, **amounts):
                if category == "tensorflow_scalar_native_binding":
                    reject()
                return reserve(category, **amounts)
            patch.setattr(child, "reserve", fail_reservation)
        elif phase == "binding":
            patch.setattr(FrozenParameterBinding, "create", classmethod(reject))
        with ResourceScope(parent), pytest.raises(failure, match="injected scalar"):
            published.append(module.lower_scalar_graph(graph, input_name=root, output_name=output,
                parameters=parameters, ledger=child))
    assert injected == [phase] and not published
    assert len(created) == 3 if phase == "partial_ast" else bool(created) if phase == "binding" else not created
    assert tuple(p.uuid for p in parameters) == identities
    assert source.to_ir().to_json() == source_before
    receipts = parent.receipt(), child.receipt()
    assert receipts[0]["consumed_derivative_work"] == receipts[1]["consumed_derivative_work"]
    assert (receipts[0]["consumed_derivative_work"] == 0) == (phase in {"snapshot", "audit"})
    for receipt in receipts:
        assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == receipt["active_tapes"] == 0
    binding, _ = module.lower_scalar_graph(graph, input_name=root, output_name=output, parameters=parameters)
    expected = [.8, .3] if phase == "layout" else [np.sin(.3*.8+.4), np.exp(1.1)]
    np.testing.assert_allclose(binding.evaluate((.3, .8)), expected, atol=2e-15, rtol=0)


@pytest.mark.parametrize("failure", [RuntimeError, MemoryError, KeyboardInterrupt])
@pytest.mark.parametrize("phase", ["partial_ast", "binding", "whole_plan"])
def test_failed_public_compile_preserves_existing_handle_and_source_owner(phase, failure, monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    import quantumbridge.interfaces.tensorflow_managed as managed
    node, calls = node_for()
    original = compile_node(node)
    function, snapshot = node.fn, original._binding_fingerprint()
    parent, created = UnifiedResourceLedger(), []
    constructor = module.ParameterExpression
    def reject(*args, **kwargs):
        raise failure("injected public "+phase)
    def fail_partial(*args, **kwargs):
        if len(created) == 4:
            reject()
        result = constructor(*args, **kwargs)
        created.append(result)
        return result
    with monkeypatch.context() as patch:
        if phase == "partial_ast":
            patch.setattr(module, "ParameterExpression", fail_partial)
        elif phase == "binding":
            patch.setattr(FrozenParameterBinding, "create", classmethod(reject))
        else:
            patch.setattr(managed.TensorFlowStatevectorPlan, "__init__", reject)
        with ResourceScope(parent), pytest.raises(failure, match="injected public"):
            compile_node(node)
    assert node.fn is function and original._binding_fingerprint() == snapshot
    assert parent.receipt()["consumed_derivative_work"] > 0
    assert parent.receipt()["live_memory_bytes"] == parent.receipt()["reserved_derivative_work"] == 0
    x = tf.constant([.37, .82], tf.float64)
    np.testing.assert_allclose(original(x), np.cos(np.sin(.37)**2+.82), atol=2e-12, rtol=0)
    again = compile_node(node)
    np.testing.assert_allclose(again(x), original(x), atol=2e-12, rtol=0)
    assert calls == ["construct"]*3


@pytest.mark.parametrize("failure", [RuntimeError, MemoryError, KeyboardInterrupt])
def test_runtime_whole_plan_failure_releases_work_and_the_same_handle_recovers(failure, monkeypatch):
    node, calls = node_for()
    handle = compile_node(node)
    snapshot, parent = handle._binding_fingerprint(), UnifiedResourceLedger()
    x = tf.constant([.37, .82], tf.float64)
    before = handle.cache_info()
    with monkeypatch.context() as patch:
        def reject(*a, **k):
            raise failure("injected quantum execution")
        patch.setattr(handle._whole, "values", reject)
        with ResourceScope(parent), pytest.raises(failure, match="injected quantum"):
            handle(x)
    receipt = parent.receipt()
    assert receipt["consumed_derivative_work"] > 0
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == receipt["active_tapes"] == 0
    after = handle.cache_info()
    assert after["aborted_calls"] == before["aborted_calls"]+1
    assert after["successful_calls"] == before["successful_calls"]
    with ResourceScope(parent):
        np.testing.assert_allclose(handle(x), np.cos(np.sin(.37)**2+.82), atol=2e-12, rtol=0)
    assert handle._binding_fingerprint() == snapshot and calls == ["construct"]
