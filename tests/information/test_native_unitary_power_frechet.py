# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Moving-projector matrix-power derivatives from an independent conjugation family."""

import cmath
import gc

import numpy as np
import pytest

from quantumbridge.information import matrix_functions
from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope


Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1., -1.])


def rotation_jet(pauli, angle, first, second):
    value = np.cos(angle/2)*np.eye(2)-1j*np.sin(angle/2)*pauli
    derivative = -.5j*pauli@value
    return value, first*derivative, second*derivative-.25*first**2*value


def product(left, right):
    a, da, dda = left
    b, db, ddb = right
    return a@b, da@b+a@db, dda@b+2*da@db+a@ddb


def conjugation_family(point, power=1., dimension=2):
    angle = point*point+.4
    # The eigenvectors vary with point, so U and U' do not generally commute.
    left = rotation_jet(Y, point, 1., 0.)
    right = rotation_jet(Y, -point, -1., 0.)
    phase = cmath.phase(cmath.exp(-.5j*angle))
    middle = rotation_jet(Z, -2*power*phase, 2*power*point, 2*power)
    jets = product(product(left, middle), right)
    if dimension == 2: return jets
    # Add repeated inactive eigenvalues, then mix every subspace by a known
    # constant Fourier matrix. This is not an SDK or production-code oracle.
    blocks = [np.eye(dimension, dtype=complex), np.zeros((dimension, dimension), complex), np.zeros((dimension, dimension), complex)]
    for result, local in zip(blocks, jets): result[-2:, -2:] = local
    index = np.arange(dimension)
    fourier = np.exp(2j*np.pi*index[:, None]*index[None, :]/dimension)/np.sqrt(dimension)
    return tuple(fourier@block@fourier.conj().T for block in blocks)


@pytest.mark.parametrize("dimension", [2, 4, 8])
@pytest.mark.parametrize("point", [.37, 1.3, 2.8])
@pytest.mark.parametrize("power", [.5, -.5, 1.5])
def test_first_and_second_frechet_chain_matches_moving_projector_oracle(dimension, point, power):
    source = conjugation_family(point, dimension=dimension)
    expected = conjugation_family(point, power, dimension)
    actual = matrix_functions.unitary_power_jet(*source, power)
    for received, reference in zip(actual, expected):
        np.testing.assert_allclose(received, reference, atol=3e-11, rtol=2e-12)
    if dimension == 2:
        assert np.linalg.norm(source[0]@source[1]-source[1]@source[0]) > .05


def test_frechet_rule_is_not_the_invalid_commuting_shortcut():
    source = conjugation_family(1.3)
    value, first, _ = matrix_functions.unitary_power_jet(*source, .5)
    false = .5*np.linalg.inv(value)@source[1]
    assert np.linalg.norm(first-false) > .1


def test_repeated_unitary_spectrum_has_the_correct_confluent_derivatives():
    generator = np.array([[.3, .7j], [-.7j, -.2]])
    source = np.eye(2, dtype=complex), 1j*generator, -generator@generator
    actual = matrix_functions.unitary_power_jet(*source, .5)
    for received, reference in zip(actual, [source[0], .5j*generator, -.25*generator@generator]):
        np.testing.assert_allclose(received, reference, atol=3e-13, rtol=0)


def test_branch_cut_and_nonunitary_inputs_are_not_given_fake_finite_derivatives():
    unitary = np.diag([-1.+0j, 1.])
    with pytest.raises((ValueError, np.linalg.LinAlgError), match="branch"):
        matrix_functions.unitary_power_jet(unitary, np.eye(2), np.zeros((2, 2)), .5)
    with pytest.raises(ValueError, match="unitary"):
        matrix_functions.unitary_power_jet(2*np.eye(2), np.eye(2), np.zeros((2, 2)), .5)


def test_resource_denial_precedes_factorization_and_preserves_inputs(monkeypatch):
    source = conjugation_family(.37)
    before = [matrix.copy() for matrix in source]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))
    monkeypatch.setattr(np.linalg, 'eig', lambda *a, **k:pytest.fail('unadmitted Frechet factorization'))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        matrix_functions.unitary_power_jet(*source, .5)
    for actual, expected in zip(source, before): np.testing.assert_array_equal(actual, expected)
    assert ledger.receipt()['live_memory_bytes'] == 0


def test_jet_outputs_have_native_storage_leases_retained_by_views():
    source = conjugation_family(.37)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger): outputs = matrix_functions.unitary_power_jet(*source, .5)
    gc.collect()
    expected_bytes = sum(value.nbytes for value in outputs)
    assert ledger.receipt()['live_memory_bytes'] == expected_bytes
    view = outputs[1][0]
    del outputs
    gc.collect()
    assert ledger.receipt()['live_memory_bytes'] == 64
    del view
    gc.collect()
    assert ledger.receipt()['live_memory_bytes'] == 0
