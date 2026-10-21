# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Bounded second source-map contractions, not another quantum derivative engine."""

import numpy as np
import pytest

from quantumbridge.execution import ResourceLimitError, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_reservations import mapped_second
from quantumbridge.execution.resource_context import ResourceScope


@pytest.mark.parametrize("directional", [False, True])
@pytest.mark.parametrize("complex_values", [False, True])
def test_second_mapping_matches_independent_tensor_equations(directional, complex_values):
    rng = np.random.default_rng(12)
    rows, packed, inputs = 3, 4, 2
    columns = 1 if directional else inputs
    def data(shape):
        result = rng.normal(size=shape)
        return result+1j*rng.normal(size=shape) if complex_values else result
    internal = data((rows, packed, 1 if directional else packed))
    classical, own = data((packed, inputs)), data((rows, packed))
    second = data((packed, inputs, columns))
    expected = (np.einsum("rpk,pn->rnk", internal, classical) if directional
        else np.einsum("rpq,pn,qm->rnm", internal, classical, classical))
    expected += np.einsum("rp,pnk->rnk", own, second)
    ledger = Ledger()
    with ResourceScope(ledger) as scope:
        result = mapped_second(scope, internal, classical, own, second, directional=directional)
        np.testing.assert_allclose(result, expected, atol=1e-12)
        assert ledger.receipt()["live_memory_bytes"] == result.nbytes
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_small_final_hessian_still_preflights_larger_workspace(monkeypatch):
    internal, classical = np.ones((2, 64, 64)), np.ones((64, 1))
    own, second = np.ones((2, 64)), np.zeros((64, 1, 1))
    ledger = Ledger(Limits(max_total_memory_bytes=527))
    original, calls = np.matmul, []
    def matmul(*a, **k):
        calls.append(True)
        return original(*a, **k)
    monkeypatch.setattr(np, "matmul", matmul)
    with pytest.raises(ResourceLimitError), ResourceScope(ledger) as scope:
        mapped_second(scope, internal, classical, own, second, directional=False)
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0
    exact = Ledger(Limits(max_total_memory_bytes=528))
    with ResourceScope(exact) as scope:
        result = mapped_second(scope, internal, classical, own, second, directional=False)
        np.testing.assert_allclose(result, np.full((2, 1, 1), 64**2))
        assert exact.receipt()["peak_memory_bytes"] == 528
        assert exact.receipt()["live_memory_bytes"] == 16


def test_directional_mapping_never_allocates_the_full_input_hessian(monkeypatch):
    rows, packed, inputs = 2, 3, 64
    internal, classical = np.ones((rows, packed, 1)), np.ones((packed, inputs))
    own, second = np.ones((rows, packed)), np.zeros((packed, inputs, 1))
    original = np.empty
    shapes = []
    def empty(shape, *a, **k):
        shapes.append(tuple(shape))
        assert tuple(shape) != (rows, inputs, inputs)
        return original(shape, *a, **k)
    monkeypatch.setattr(np, "empty", empty)
    with ResourceScope(Ledger()) as scope:
        result = mapped_second(scope, internal, classical, own, second, directional=True)
        np.testing.assert_allclose(result, np.full((rows, inputs, 1), 3.))
    assert (rows, inputs, 1) in shapes


def test_contraction_exception_releases_workspace_and_request_recovers(monkeypatch):
    arrays = (np.ones((2, 3, 3)), np.ones((3, 2)), np.ones((2, 3)), np.ones((3, 2, 2)))
    ledger = Ledger()
    with monkeypatch.context() as patch:
        def fail(*a, **k): raise RuntimeError("injected contraction failure")
        patch.setattr(np, "matmul", fail)
        with pytest.raises(RuntimeError), ResourceScope(ledger) as scope:
            mapped_second(scope, *arrays, directional=False)
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger) as scope:
        actual = mapped_second(scope, *arrays, directional=False)
        np.testing.assert_allclose(actual, np.full((2, 2, 2), 12.))
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_empty_and_invalid_second_map_shapes():
    actual = mapped_second(None, np.empty((0, 3, 3)), np.empty((3, 2)),
        np.empty((0, 3)), np.empty((3, 2, 2)), directional=False)
    assert actual.shape == (0, 2, 2)
    with pytest.raises(ValueError):
        mapped_second(None, np.zeros((1, 3, 2)), np.zeros((3, 2)), np.zeros((1, 3)),
            np.zeros((3, 2, 1)), directional=True)
    with pytest.raises(ValueError):
        mapped_second(None, np.zeros((1, 3, 3)), np.zeros((4, 2)), np.zeros((1, 3)),
            np.zeros((3, 2, 2)), directional=False)
