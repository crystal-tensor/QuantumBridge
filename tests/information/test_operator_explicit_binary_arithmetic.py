# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Binary results must not inherit a proved basis from unqualified operands."""

from contextlib import nullcontext

import numpy as np
import pytest

from quantumbridge.information import Operator
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits, ResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope


def owner(mode, seed=12401):
    rng = np.random.default_rng(seed)
    data, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    value = Operator(data)
    return value.as_native_operator() if mode == "native" else value.as_qiskit_operator()


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
@pytest.mark.parametrize("managed", [False, True])
def test_mixed_binary_conventions_refuse_before_inheriting_output_basis(mode, method, managed):
    first = owner(mode)
    second = first.as_qiskit_operator() if mode == "native" else first.as_native_operator()
    before = first.data.copy(), second.data.copy()
    ledger = Ledger()
    with ResourceScope(ledger) if managed else nullcontext():
        with pytest.raises(UnsupportedFeature) as error:getattr(first, method)(second)
    assert error.value.feature == "operator_arithmetic_convention"
    np.testing.assert_array_equal(first.data, before[0])
    np.testing.assert_array_equal(second.data, before[1])
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
@pytest.mark.parametrize("managed", [False, True])
def test_foreign_binary_operand_property_is_never_dispatched(mode, method, managed):
    calls = []
    class Foreign(Operator):
        @property
        def data(self):
            calls.append("data")
            raise AssertionError("Foreign binary operand read before qualification")
    first = owner(mode)
    ledger = Ledger()
    with ResourceScope(ledger) if managed else nullcontext():
        with pytest.raises(UnsupportedFeature):getattr(first, method)(object.__new__(Foreign))
    assert not calls and ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
def test_binary_operand_origin_is_qualified_without_foreign_equality(mode, method):
    calls = []
    class Origin(str):
        def __eq__(self, other):
            calls.append("eq")
            raise AssertionError("Foreign origin compared")
    first, second = owner(mode), owner(mode, 12402)
    second._public_matrix_basis = Origin("native")
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature):getattr(first, method)(second)
    assert not calls and ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
def test_binary_raw_conversion_and_output_share_prior_memory_admission(mode, method, monkeypatch):
    first = owner(mode)
    raw = np.eye(4, dtype=float)
    ledger = Ledger(Limits(max_total_memory_bytes=511))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Known binary group denial allocated"))
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):getattr(first, method)(raw)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
def test_valid_binary_and_scalar_math_keep_the_selected_frame(mode, method):
    first, second = owner(mode), owner(mode, 12402)
    expected = first.data + second.data if method == "__add__" else first.data - second.data
    ledger = Ledger()
    with ResourceScope(ledger):result = getattr(first, method)(second)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    assert result.arithmetic_convention == mode
    assert ledger.receipt()["live_memory_bytes"] == 256
    np.testing.assert_allclose((.3j * result).data, .3j * expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose((result / 2).data, expected / 2, atol=3e-12, rtol=0)


@pytest.mark.parametrize("mode", ["native", "qiskit"])
@pytest.mark.parametrize("method", ["__add__", "__sub__"])
def test_exact_binary_group_budget_succeeds_and_keeps_only_output_live(mode, method):
    first = owner(mode)
    raw = np.eye(4, dtype=float)
    expected = first.data + raw if method == "__add__" else first.data - raw
    ledger = Ledger(Limits(max_total_memory_bytes=512))
    with ResourceScope(ledger):result = getattr(first, method)(raw)
    np.testing.assert_allclose(result.data, expected, atol=3e-12, rtol=0)
    assert ledger.receipt()["peak_memory_bytes"] == 512
    assert ledger.receipt()["live_memory_bytes"] == 256
