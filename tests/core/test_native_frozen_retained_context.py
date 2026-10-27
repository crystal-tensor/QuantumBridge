# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Frozen scalar syntax preserves formal ownership, not artificial operands."""

import math

import pytest

import quantumbridge as qb
from quantumbridge.core import SymbolicExpressionLimits, symbolic_expression_scope
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger


def source(vector=False):
    if vector:
        owner = qb.ParameterVector("angles", 12)
        q, r = owner[2], owner[10]
    else:
        q, r = qb.Parameter("q"), qb.Parameter("r")
    return q, r, (r.sin()+q*q).gradient(r)


@pytest.mark.parametrize("vector", [False, True])
@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.parametrize("occurrences", [1, 3])
def test_frozen_formal_context_uses_owned_identities_and_unchanged_math(vector, partial, occurrences):
    q, r, expression = source(vector)
    if partial:
        expression = expression.assign(r, .31)
    parameters = (q,) if partial else (q, r)
    values = (.2,) if partial else (.2, .31)
    binding = FrozenParameterBinding.create(parameters, (expression,)*occurrences)
    for frozen in binding.expressions:
        assert frozen is not expression
        assert frozen.op == expression.op
        assert frozen._nodes == expression._nodes
        assert frozen._dependencies == (frozenset() if partial else {r})
        assert frozen.parameters == set(parameters)
        assert frozen._retained_parameters == {q}
        assert frozen._derivative_order == expression._derivative_order
        for parameter in frozen.parameters:
            original = next(p for p in parameters if p == parameter)
            assert parameter is original
            if vector:
                assert parameter.vector is q.vector
                assert parameter.index in (2, 10)
                assert len(parameter.vector) == 12
    assert binding.parameter_uuids == tuple(str(p.uuid) for p in parameters)
    assert binding.evaluate(values) == pytest.approx((math.cos(.31),)*occurrences, abs=2e-15)
    assert expression.parameters == set(parameters)
    assert binding.to_record()["expressions"]


def test_plain_and_fully_bound_expressions_need_no_surplus_formals():
    q, r, expression = source()
    plain = FrozenParameterBinding.create((r,), (r.cos(),))
    assert plain.expressions[0].parameters == {r}
    value = expression.bind({q:.2, r:.31})
    assert type(value) is float
    assert FrozenParameterBinding.create((), (value,)).evaluate(()) == (value,)
    with pytest.raises(ValueError, match="missing or surplus"):
        FrozenParameterBinding.create((q, r), (r.cos(),))


@pytest.mark.parametrize("kind", ["missing", "surplus", "duplicate", "same_name", "same_uuid"])
def test_formal_input_identity_errors_are_not_coalesced(kind):
    q, r, expression = source()
    options = {
        "missing": (r,), "surplus": (q,r,qb.Parameter("s")),
        "duplicate": (q,r,q), "same_name": (qb.Parameter("q"),r),
        "same_uuid": (qb.Parameter("renamed",q.uuid),r),
    }
    with pytest.raises(ValueError):
        FrozenParameterBinding.create(options[kind], (expression,))
    assert expression.parameters == {q,r} and expression._dependencies == {r}


def test_retained_identity_storage_is_bounded_without_double_counting_ast_symbols():
    q,r,expression = source()
    plain = FrozenParameterBinding.create((r,), (r.cos(),))
    binding = FrozenParameterBinding.create((q,r), (expression,))
    assert binding.node_count == plain.node_count+1
    with pytest.raises(MemoryError, match="max_parameter_graph_nodes"):
        FrozenParameterBinding.create((q,r), (expression,),
            limits=HigherOrderLimits(max_parameter_graph_nodes=plain.node_count))
    with pytest.raises(MemoryError, match="max_input_parameters"):
        FrozenParameterBinding.create((q,r), (expression,), limits=HigherOrderLimits(max_input_parameters=1))
    with symbolic_expression_scope(SymbolicExpressionLimits(max_parameters=1)):
        with pytest.raises(ValueError, match="max_parameters"):
            FrozenParameterBinding.create((q,r), (expression,))
    duplicate = qb.ParameterExpression(expression.op, expression.args,
        _retained_parameters=frozenset({q,r}))
    assert FrozenParameterBinding.create((q,r),(duplicate,)).node_count == binding.node_count


def test_managed_foreign_formal_is_refused_before_property_access_and_recovers():
    q,r,expression = source()
    class Foreign(qb.Parameter):
        @property
        def name(self):
            pytest.fail("Untrusted parameter owner property was inspected")
    foreign = object.__new__(Foreign)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        with pytest.raises((TypeError, ValueError, qb.UnsupportedFeature)):
            FrozenParameterBinding.create((foreign,r),(expression,))
        binding = FrozenParameterBinding.create((q,r),(expression,))
    assert binding.evaluate((.2,.31)) == pytest.approx((math.cos(.31),))
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["consumed_derivative_work"] == 0


def test_failed_freezing_is_atomic_and_owned_snapshot_keeps_context():
    q,r,expression = source()
    before = qb.Circuit(1).rx(expression,0).to_ir().to_json()
    binding = FrozenParameterBinding.create((q,r),(expression,))
    with pytest.raises(MemoryError):
        FrozenParameterBinding.create((q,r),(expression,)*10,
            limits=HigherOrderLimits(max_parameter_graph_nodes=2))
    assert qb.Circuit(1).rx(expression,0).to_ir().to_json() == before
    assert binding.evaluate((99.,.31)) == binding.evaluate((.2,.31))
    with pytest.raises(ValueError, match="count"):
        binding.evaluate((.31,))


def test_frozen_capture_keeps_the_symbolic_derivative_order_guard():
    q,r,expression = source()
    object.__setattr__(expression,"_derivative_order",100)
    with pytest.raises(ValueError,match="max_derivative_order"):
        FrozenParameterBinding.create((q,r),(expression,))
