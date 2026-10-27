# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""One frozen plan, complete request sequence and actual evidence export."""

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import tf


def build(**options):
    parameters = qb.ParameterVector("angle", 2)
    p, q = parameters
    node = QNode.from_circuit(qb.Circuit(1).ry(p*p+q, 0), qb.PauliZ(0),
        interface="tensorflow", diff_method="adjoint", max_diff=2, **options)
    return node, parameters, node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])


def reference():
    point = np.array([0.37, 0.82])
    angle, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    return point, np.cos(angle), -np.sin(angle)*slope, -np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*np.diag([2., 0.])


def test_complete_request_chain_owns_each_delta_once_and_exports_execution_evidence():
    node, parameters, handle = build()
    point, value, gradient, hessian = reference()
    directions = np.array([[0.4, -0.3], [-0.1, 0.8]])
    parent = UnifiedResourceLedger()
    child = UnifiedResourceLedger(parent=parent)
    records = []
    for kind, many in [("value", False), ("gradient", False), ("jvp", False), ("vjp", False),
            ("hvp", False), ("hvp", True), ("hessian", False), ("gradient", False), ("value", False)]:
        request = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind=kind,
            derivative_order=0 if kind == "value" else 2 if kind in {"hvp", "hessian"} else 1,
            tangent=tf.constant(directions if many else directions[0], tf.float64) if kind in {"jvp", "hvp"} else None,
            cotangent=tf.constant([0.7], tf.float64) if kind == "vjp" else None)
        bound = handle.estimate(request)
        before = child.receipt()
        with ResourceScope(child):
            result = handle.execute(request)
        after = child.receipt()
        spent = after["consumed_derivative_work"]-before["consumed_derivative_work"]
        assert spent == bound["first_call_work"] == result.receipt["consumed_derivative_work"]
        assert after["consumed_tapes"]-before["consumed_tapes"] == bound["logical_evaluations"]
        assert parent.receipt()["consumed_derivative_work"] == after["consumed_derivative_work"]
        assert after["live_memory_bytes"] == result.receipt["reserved_derivative_work"] == 0
        np.testing.assert_allclose(result.value, value, atol=1e-12, rtol=0)
        expected = None if kind == "value" else gradient if kind == "gradient" else gradient @ directions[0] if kind == "jvp" else 0.7*gradient if kind == "vjp" else tuple(hessian @ d for d in directions) if many else hessian @ directions[0] if kind == "hvp" else hessian
        if expected is not None:
            np.testing.assert_allclose(result.derivative, expected, atol=2e-11, rtol=0)
        metadata = result.metadata
        assert metadata["physical_shots"] == metadata["host_quantum_calls"] == metadata["device_updates"] == 0
        records.append(dict(operation=kind, multiple_directions=many, bound=bound,
            request=metadata["request"], value=np.asarray(result.value).tolist(),
            derivative=None if result.derivative is None else np.asarray(result.derivative).tolist(),
            observed_logical_work_delta=spent, receipt=result.receipt,
            actual_host_quantum_calls=metadata["host_quantum_calls"], actual_device_updates=metadata["device_updates"]))
    inline = node.compile_tensorflow_inline(parameters=tuple(parameters), input_signature=[tf.TensorSpec((2,), tf.float64)])
    np.testing.assert_allclose(inline(tf.constant(point, tf.float64)), value, atol=1e-12, rtol=0)
    # Export only after every mathematical and accounting assertion succeeded.
    destination = os.environ.get("QB_TF_M2_QUERY_EVIDENCE")
    if destination:
        root = Path(__file__).parents[2]
        source_paths = ["quantumbridge/qml/qnode.py", "quantumbridge/interfaces/tensorflow_managed.py", "quantumbridge/interfaces/tensorflow_inline.py",
            "quantumbridge/interfaces/tensorflow_scalar_lowering.py",
            "quantumbridge/interfaces/tensorflow_whole_execution.py", "quantumbridge/interfaces/tensorflow_autodiff.py",
            "quantumbridge/execution/derivative_planning.py", "quantumbridge/execution/derivative_request.py", str(Path(__file__).relative_to(root))]
        payload = dict(test_id="tests/interfaces/test_native_tf_m2_query_lifecycle.py::test_complete_request_chain_owns_each_delta_once_and_exports_execution_evidence",
            assertions_completed=True, tensorflow=tf.__version__, tensorflow_origin=tf.__file__,
            source_sha256={path: hashlib.sha256((root/path).read_bytes()).hexdigest() for path in source_paths},
            query_capability=dict(handle.execution_capabilities["MANAGED_EXPLICIT_QUERY"]),
            experimental_capability=dict(handle.execution_capabilities["EXPERIMENTAL_CACHED_CALLABLE"]),
            inline_capability=dict(inline.execution_capabilities["TRACE_INLINE_DIFFERENTIABLE"]),
            sequence=records, final_parent_receipt=parent.receipt(), cache_info=handle.cache_info())
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")


def test_direction_only_contract_never_uses_a_complete_hessian(monkeypatch):
    node, _, handle = build(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    point, _, _, hessian = reference()
    def forbidden(*a, **k):
        pytest.fail("A directional query requested a complete Hessian")
    monkeypatch.setattr(QNode, "compute_hessian", forbidden)
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    request = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind="hvp", derivative_order=2,
        tangent=tf.constant([[0.4, -0.3], [-0.1, 0.8]], tf.float64))
    np.testing.assert_allclose(handle.execute(request).derivative, [hessian @ d for d in np.array(request.tangent)], atol=2e-11, rtol=0)
    with pytest.raises(MemoryError, match="max_hessian_elements"):
        handle.execute(replace(request, derivative_kind="hessian", tangent=None))
