# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit native conversion and arithmetic share existing storage admission."""

import gc
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from quantumbridge.information import Operator
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits, ResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope


def source(public=False):
    raw = Operator(np.array([[1, 1, 1, 1], [1, 1j, -1, -1j],
        [1, -1, 1, -1], [1, -1j, -1, 1j]], complex) / 2)
    return raw.as_qiskit_operator() if public else raw.as_native_operator()


@pytest.mark.parametrize("public", [False, True])
def test_native_factory_owned_conversion_denial_precedes_numeric_factory(public, monkeypatch):
    owner = source(public)
    before = owner.data.copy()
    ledger = Ledger(Limits(max_total_memory_bytes=255))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied native conversion allocated"))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):owner.as_native_operator()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)


@pytest.mark.parametrize("public", [False, True])
def test_native_conversion_logical_work_denial_precedes_copy(public, monkeypatch):
    owner = source(public)
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overwork native conversion allocated"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=15)), pytest.raises(MemoryError):
        owner.as_native_operator()


@pytest.mark.parametrize("method", ["compose", "tensor", "expand"])
def test_native_arithmetic_memory_is_prior_admitted_and_escaped_result_keeps_lease(method):
    first, second = source(), source()
    expected = first.data @ second.data if method == "compose" else np.kron(first.data, second.data)
    ledger = Ledger(Limits(max_total_memory_bytes=expected.nbytes - 1))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):getattr(first, method)(second)
    assert ledger.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=expected.nbytes))
    with ResourceScope(ledger):result = getattr(first, method)(second)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    view = result.data[:, :1]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == expected.nbytes
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("method", ["tensor", "expand"])
def test_native_raw_operand_group_denial_before_dtype_conversion(method, monkeypatch):
    owner = source()
    raw = np.eye(4, dtype=float)
    ledger = Ledger(Limits(max_total_memory_bytes=4096 + 256 - 1))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Combined native denial allocated"))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):getattr(owner, method)(raw)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("field", ["data", "dims", "width", "basis", "mode"])
@pytest.mark.parametrize("method", ["as_native_operator", "as_qiskit_operator", "copy", "transpose", "power"])
def test_native_forged_owners_refuse_without_foreign_callbacks(field, method):
    calls = []
    class Foreign:
        def __getattr__(self, name):
            calls.append(name)
            raise AssertionError("Foreign owner field accessed")
        def __iter__(self):
            calls.append("iter")
            raise AssertionError("Foreign owner iterated")
    class Origin(str):
        def __eq__(self, value):
            calls.append("eq")
            raise AssertionError("Foreign origin equality")
    owner = source()
    if field == "data":owner.data = Foreign()
    elif field == "dims":owner._input_dims = Foreign()
    elif field == "width":owner.num_qubits = Foreign()
    elif field == "basis":owner._public_matrix_basis = Origin("native")
    else:object.__setattr__(owner, "_arithmetic_convention", Origin("native"))
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises((TypeError, ValueError)):
        getattr(owner, method)(.37) if method == "power" else getattr(owner, method)()
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_foreign_native_factory_receiver_is_rejected_before_subclass_property():
    class Foreign(Operator):
        @property
        def data(self):pytest.fail("Foreign native factory property")
    with pytest.raises(UnsupportedFeature):Operator.as_native_operator(object.__new__(Foreign))


def test_unresolved_legacy_origin_cannot_be_laundered_through_native_factory():
    import quantumbridge as qb
    body = qb.Circuit(2).ry(.4, 0).cx(0, 1)
    legacy = Operator(body).compose(Operator(np.eye(4)))
    before = legacy.data.copy()
    with pytest.raises(UnsupportedFeature):legacy.as_native_operator()
    np.testing.assert_array_equal(legacy.data, before)
    assert legacy.__dict__.get("_arithmetic_convention") is None


def test_native_concurrent_children_and_conversion_snapshots_release_exact_owned_outputs():
    first, second = source(), source()
    first.data.flags.writeable = second.data.flags.writeable = False
    before = first.data.copy(), second.data.copy()
    parent = Ledger(Limits(max_total_memory_bytes=6 * 256))
    children = [Ledger(parent=parent) for _ in range(6)]
    def execute(ledger):
        with ResourceScope(ledger):return first.compose(second)
    with ThreadPoolExecutor(max_workers=3) as pool:results = list(pool.map(execute, children))
    assert parent.receipt()["live_memory_bytes"] == 6 * 256
    for item in results:
        np.testing.assert_allclose(item.data, before[0] @ before[1], atol=3e-12, rtol=0)
        assert item.__dict__["_arithmetic_convention"] == "native"
    del item, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0
    assert all(child.receipt()["live_memory_bytes"] == 0 for child in children)
    np.testing.assert_array_equal(first.data, before[0])


def test_numeric_failure_releases_native_output_and_allows_recovery(monkeypatch):
    first, second = source(), source()
    expected = first.data @ second.data
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(np, "matmul", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("injected product failure")))
        try:
            with ResourceScope(ledger):first.compose(second)
        except RuntimeError as error:
            assert str(error) == "injected product failure"
        else:pytest.fail("Numeric fault was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):result = first.compose(second)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)


def test_public_native_public_roundtrip_has_two_exact_owned_buffers_not_four():
    public = source(public=True)
    original = public.data.copy()
    ledger = Ledger(Limits(max_total_memory_bytes=512))
    with ResourceScope(ledger):
        native = public.as_native_operator()
        assert ledger.receipt()["live_memory_bytes"] == 256
        again = native.as_qiskit_operator()
        assert ledger.receipt()["live_memory_bytes"] == 512
    np.testing.assert_array_equal(again.data, original)
    assert not np.shares_memory(again.data, public.data)
    assert not np.shares_memory(again.data, native.data)
    escaped = native.data[:, :1], again.data[:, :1]
    del native, again
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 512
    del escaped
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
