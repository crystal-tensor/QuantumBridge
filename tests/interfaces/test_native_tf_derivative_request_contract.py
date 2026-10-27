# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Framework-free work contracts shared with managed TF execution."""

from dataclasses import FrozenInstanceError, replace

import pytest
import numpy as np

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.derivative_planning import tensorflow_statevector_work
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.qml import QNode


def make_plan(outputs=1, **options):
    p, q = qb.ParameterVector("angles", 2)
    source = qb.QuantumCircuit(2)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (1,))
    node = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2, **options)
    plan = node._construct(([0.37, 0.82],), {})
    if outputs == 2:
        plan.requests = [*plan.requests, *plan.requests]
    return plan


@pytest.mark.parametrize("kind,order", [("value", 0), ("gradient", 1), ("jacobian", 1), ("jvp", 1), ("vjp", 1), ("hvp", 2), ("hessian", 2)])
def test_immutable_requests_have_explicit_operation_and_resource_descriptions(kind, order):
    plan = make_plan()
    request = DerivativeExecutionRequest(plan.node, derivative_kind=kind, derivative_order=order)
    work = tensorflow_statevector_work(plan, plan.circuit.lowered(), 2, request=request)
    assert work["planning_mode"] == "explicit_derivative_request"
    assert work["request"]["operation"] == kind
    assert work["request"]["order"] == order
    assert work["request"]["input_count"] == 2
    assert work["request"]["parameter_identity"] == tuple(str(p.uuid) for p in plan.recorder.parameters)
    with pytest.raises(FrozenInstanceError):
        request.derivative_order = 0
    description = request.describe(inputs=2, outputs=1, directions=1, cotangents=1,
        parameters=(p.uuid for p in plan.recorder.parameters), plan_identity=work["compiled_plan_identity"])
    with pytest.raises(TypeError):
        description["order"] = 3


def test_value_first_and_second_direction_requests_have_distinct_monotone_work():
    plan = make_plan()
    work = []
    for kind, order in (("value", 0), ("vjp", 1), ("hvp", 2), ("hessian", 2)):
        work.append(tensorflow_statevector_work(plan, plan.circuit.lowered(), 2,
            request=DerivativeExecutionRequest(plan.node, derivative_kind=kind, derivative_order=order)))
    assert all(a["planned_work"] < b["planned_work"] for a, b in zip(work, work[1:]))
    assert all(a["workspace_bytes"] <= b["workspace_bytes"] for a, b in zip(work, work[1:]))


@pytest.mark.parametrize("kind,order", [("jvp", 1), ("vjp", 1), ("hvp", 2)])
def test_multiple_directions_or_cotangents_increase_work_without_full_hessian(kind, order):
    plan = make_plan(outputs=2)
    request = DerivativeExecutionRequest(plan.node, derivative_kind=kind, derivative_order=order)
    one = tensorflow_statevector_work(plan, plan.circuit.lowered(), 2, request=request)
    many = tensorflow_statevector_work(plan, plan.circuit.lowered(), 2, request=request,
        directions=2 if kind != "vjp" else 1, cotangents=2 if kind == "vjp" else 1)
    assert many["planned_work"] == 2*one["planned_work"]
    assert many["logical_evaluations"] == 2*one["logical_evaluations"]


def test_full_hessian_and_hvp_limits_are_separate_in_the_shared_planner():
    plan = make_plan(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    request = DerivativeExecutionRequest(plan.node, derivative_kind="hvp", derivative_order=2)
    tensorflow_statevector_work(plan, plan.circuit.lowered(), 2, request=request)
    with pytest.raises(MemoryError, match="max_hessian_elements"):
        tensorflow_statevector_work(plan, plan.circuit.lowered(), 2,
            request=replace(request, derivative_kind="hessian"))


@pytest.mark.parametrize("order", [False, 0, 1, 3])
def test_wrong_operation_order_is_rejected_before_tensor_execution(order):
    plan = make_plan()
    with pytest.raises(ValueError, match="Derivative order"):
        tensorflow_statevector_work(plan, plan.circuit.lowered(), 2,
            request=DerivativeExecutionRequest(plan.node, derivative_kind="hvp", derivative_order=order))


def test_unbounded_direction_iterators_are_not_consumed_for_admission():
    class Unbounded:
        def __iter__(self):
            pytest.fail("An unbounded direction iterator was consumed")
    plan = make_plan()
    with pytest.raises(ValueError, match="counts"):
        tensorflow_statevector_work(plan, plan.circuit.lowered(), 2,
            request=DerivativeExecutionRequest(plan.node, derivative_kind="hvp", derivative_order=2), directions=Unbounded())


def test_shared_native_device_gradient_request_has_a_scalar_output_contract():
    plan = make_plan()
    request = DerivativeExecutionRequest(plan.node, [0.37, 0.82], derivative_kind="gradient", derivative_order=1)
    result = qb.StatevectorDevice().execute_derivatives(request)
    assert result.derivative.shape == (2,)
    np.testing.assert_allclose(result.derivative, plan.node.gradient([0.37, 0.82]), atol=1e-10, rtol=0)
    multiple = make_plan(outputs=2)
    with pytest.raises(ValueError, match="scalar output"):
        tensorflow_statevector_work(multiple, multiple.circuit.lowered(), 2,
            request=DerivativeExecutionRequest(multiple.node, derivative_kind="gradient", derivative_order=1))
