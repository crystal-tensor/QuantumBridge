# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Actual binary inputs, exact Jordan blocks, and independent branch references."""

import cmath
import json
import math
from pathlib import Path

import numpy as np
import pytest

from quantumbridge.information import Operator
from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope


FIXTURE = json.loads((Path(__file__).parent / "data/operator_branch_actual_input.json").read_text())


def frozen_input():
    return np.array([[complex(float.fromhex(real), float.fromhex(imag)) for real, imag in row]
                     for row in FIXTURE["matrix_hex"]])


def branch_value(value, p, cut):
    return cmath.exp(p * (math.log(abs(value)) + 1j * (cmath.phase(value * cmath.exp(-1j * cut)) + cut)))


@pytest.mark.parametrize("row", FIXTURE["cases"], ids=lambda row: str(row["p"]))
def test_original_captured_input_does_not_return_a_wrong_finite_primary_power(row):
    matrix = frozen_input()
    expected = np.array([[complex(real, imag) for real, imag in line] for line in row["reference"]])
    before = matrix.copy()
    try:
        actual = Operator(matrix).power(row["p"], branch_cut_rotation=FIXTURE["branch_cut_rotation"]).data
    except np.linalg.LinAlgError as error:
        # Corrected R2L contract: input-specific, quantified numerical refusal.
        assert "branch-sensitive" in str(error) and "gap" in str(error) and "resolution" in str(error)
    else:
        np.testing.assert_allclose(actual, expected, atol=3e-12, rtol=3e-13)
    np.testing.assert_array_equal(matrix, before)


@pytest.mark.parametrize("value", [-.25, -1., -2.])
@pytest.mark.parametrize("coupling", [.125, .25, .5])
@pytest.mark.parametrize("p", [.5, .3, -.3])
@pytest.mark.parametrize("cut", [math.pi * 1e-12, -math.pi * 1e-12, .001, -.001])
def test_exact_binary_dense_jordan_must_compute_the_derivative_not_refuse(value, coupling, p, cut):
    # All entries and N^2=0 are exact binary numbers, unlike rounded F J F*.
    nilpotent = np.array([[coupling, coupling], [-coupling, -coupling]], dtype=complex)
    np.testing.assert_array_equal(nilpotent @ nilpotent, np.zeros((2, 2)))
    matrix = value * np.eye(2) + nilpotent
    expected = branch_value(value, p, cut) * (np.eye(2) + (p / value) * nilpotent)
    before = matrix.copy()
    actual = Operator(matrix).power(p, branch_cut_rotation=cut).data
    np.testing.assert_allclose(actual, expected, atol=3e-12, rtol=3e-13)
    np.testing.assert_array_equal(matrix, before)
    if p == .5:
        np.testing.assert_allclose(actual @ actual, matrix, atol=3e-12, rtol=3e-13)


@pytest.mark.parametrize("p", [.5, .3, -.3, 1.3])
@pytest.mark.parametrize("cut", [math.pi * 1e-12, -math.pi * 1e-12, .001, -.001])
@pytest.mark.parametrize("dense", [False, True])
def test_separated_cross_cut_nonnormal_pair_is_computed_not_blanket_refused(p, cut, dense):
    a, b, coupling = -1+.1j, -1-.1j, .3-.2j
    matrix = np.array([[a, coupling], [0, b]])
    fa, fb = branch_value(a, p, cut), branch_value(b, p, cut)
    expected = np.array([[fa, coupling*(fa-fb)/(a-b)], [0, fb]])
    if dense:
        change = np.array([[1, 1j], [1j, 1]]) / math.sqrt(2)
        matrix = change @ matrix @ change.conj().T
        expected = change @ expected @ change.conj().T
    actual = Operator(matrix).power(p, branch_cut_rotation=cut).data
    np.testing.assert_allclose(actual, expected, atol=3e-12, rtol=3e-13)


@pytest.mark.parametrize("p", [.5, .3, -.3])
def test_four_by_four_disconnected_exact_jordan_blocks_are_computed(p):
    nilpotent = .125*np.array([[1, 1], [-1, -1]], dtype=complex)
    matrix, expected = np.zeros((4, 4), complex), np.zeros((4, 4), complex)
    for start, value in ((0, -1.), (2, -2.)):
        matrix[start:start+2, start:start+2] = value*np.eye(2)+nilpotent
        expected[start:start+2, start:start+2] = branch_value(value, p, FIXTURE["branch_cut_rotation"])*(np.eye(2)+p/value*nilpotent)
    np.testing.assert_allclose(Operator(matrix).power(p).data, expected, atol=3e-12, rtol=3e-13)


def test_interleaved_disconnected_components_preserve_output_positions():
    block = np.array([[-.875, .125], [-.125, -1.125]], dtype=complex)
    source = np.zeros((4, 4), complex)
    source[:2, :2], source[2:, 2:] = block, 2*block
    expected = np.zeros((4, 4), complex)
    expected[:2, :2] = 1j*(np.eye(2)-.5*(block+np.eye(2)))
    expected[2:, 2:] = math.sqrt(2)*expected[:2, :2]
    order = [0, 2, 1, 3]
    source, expected = source[np.ix_(order, order)], expected[np.ix_(order, order)]
    np.testing.assert_allclose(Operator(source).power(.5).data, expected, atol=3e-12, rtol=3e-13)


def test_repeated_certificate_preserves_owner_and_releases_managed_storage():
    import gc

    source = np.array([[-.875, .125], [-.125, -1.125]], dtype=complex)
    owner, ledger = Operator(source), UnifiedResourceLedger()
    with ResourceScope(ledger):
        result = owner.power(.5)
    assert ledger.receipt()["live_memory_bytes"] == result.data.nbytes
    np.testing.assert_array_equal(owner.data, source)
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_exact_certificate_is_not_evaluated_before_memory_admission(monkeypatch):
    import quantumbridge.information.matrix_functions as functions

    owner = Operator(np.array([[-.875, .125], [-.125, -1.125]], dtype=complex))
    monkeypatch.setattr(functions, "Fraction", object())
    with ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        owner.power(.5)


def test_proven_repeated_pair_does_not_call_an_unstable_eigensolver(monkeypatch):
    monkeypatch.setattr(np.linalg, "eig", lambda *args, **kwargs: pytest.fail("strict repeated pair reached eig"))
    matrix = np.array([[-.875, .125], [-.125, -1.125]], dtype=complex)
    expected = 1j*(np.eye(2)-.5*(matrix+np.eye(2)))
    np.testing.assert_allclose(Operator(matrix).power(.5).data, expected, atol=3e-12, rtol=3e-13)


def test_exact_nonnormal_pair_still_rejects_false_unitarity():
    with pytest.raises(ValueError, match="normal"):
        Operator(np.array([[-.875, .125], [-.125, -1.125]], dtype=complex)).power(.5, assume_unitary=True)
