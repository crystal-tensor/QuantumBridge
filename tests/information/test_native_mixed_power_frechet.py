# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent noncommuting, mixed-direction matrix-function identities."""

import cmath
import gc

import numpy as np
import pytest

from quantumbridge.information import matrix_functions
from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope


Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1.0, -1.0])


def rotation(pauli, angle, a, b, ab=0):
    value = np.cos(angle / 2) * np.eye(2) - 1j * np.sin(angle / 2) * pauli
    first = -0.5j * pauli @ value
    return value, a * first, b * first, ab * first - 0.25 * a * b * value


def product(left, right):
    a, ap, aq, apq = left
    b, bp, bq, bpq = right
    return (
        a @ b,
        ap @ b + a @ bp,
        aq @ b + a @ bq,
        apq @ b + ap @ bq + aq @ bp + a @ bpq,
    )


def family(p, q, power=1.0, dimension=2):
    # Deliberately nonlinear q+p*q: the source mixed derivative is nonzero.
    angle = q + p * q
    effective = -2 * power * cmath.phase(cmath.exp(-0.5j * angle))
    result = product(
        product(
            rotation(Y, p, 1, 0),
            rotation(Z, effective, power * q, power * (1 + p), power),
        ),
        rotation(Y, -p, -1, 0),
    )
    if dimension == 2:
        return result
    blocks = [np.eye(dimension, dtype=complex)] + [
        np.zeros((dimension, dimension), complex) for _ in range(3)
    ]
    for block, local in zip(blocks, result):
        block[-2:, -2:] = local
    indices = np.arange(dimension)
    basis = np.exp(
        2j * np.pi * indices[:, None] * indices[None, :] / dimension
    ) / np.sqrt(dimension)
    return tuple(basis @ block @ basis.conj().T for block in blocks)


@pytest.mark.parametrize("dimension", [2, 4])
@pytest.mark.parametrize("p,q", [(0.37, 0.82), (1.3, 3.17), (2.1, -2.6)])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_two_directions_and_source_mixed_term_have_the_correct_full_complex_jet(
    dimension, p, q, power
):
    source = family(p, q, dimension=dimension)
    expected = family(p, q, power, dimension)
    actual = matrix_functions.unitary_power_mixed_jet(*source, power)
    for value, reference in zip(actual, expected):
        np.testing.assert_allclose(value, reference, atol=5e-11, rtol=3e-12)
    assert np.linalg.norm(source[0] @ source[1] - source[1] @ source[0]) > 0.05
    assert np.linalg.norm(source[3]) > 0.05


def test_mixed_frechet_is_symmetric_under_exchange_of_directions():
    u, p, q, mixed = family(0.37, 0.82)
    left = matrix_functions.unitary_power_mixed_jet(u, p, q, mixed, 0.5)
    right = matrix_functions.unitary_power_mixed_jet(u, q, p, mixed, 0.5)
    for a, b in zip(left, (right[0], right[2], right[1], right[3])):
        np.testing.assert_allclose(a, b, atol=4e-12, rtol=0)


def test_equal_directions_match_the_existing_three_block_rule():
    u, p, _, mixed = family(0.37, 0.82)
    source = matrix_functions.unitary_power_jet(u, p, mixed, 0.5)
    actual = matrix_functions.unitary_power_mixed_jet(u, p, p, mixed, 0.5)
    for received, expected in zip((actual[0], actual[1], actual[3]), source):
        np.testing.assert_allclose(received, expected, atol=4e-12, rtol=0)


def test_mixed_workspace_denial_precedes_any_factorization(monkeypatch):
    source = family(0.37, 0.82)
    saved = [value.copy() for value in source]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))
    monkeypatch.setattr(np.linalg, "eig", lambda *a, **k: pytest.fail("unadmitted eig"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        matrix_functions.unitary_power_mixed_jet(*source, 0.5)
    for received, expected in zip(source, saved):
        np.testing.assert_array_equal(received, expected)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_all_four_mixed_outputs_keep_only_their_actual_storage_leases():
    source = family(0.37, 0.82)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        result = matrix_functions.unitary_power_mixed_jet(*source, 0.5)
    gc.collect()
    assert (
        ledger.receipt()["live_memory_bytes"]
        == sum(value.nbytes for value in result)
        == 256
    )
    view = result[3][0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 64
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
