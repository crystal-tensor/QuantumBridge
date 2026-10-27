# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent amplitude oracles for the nonunitary MPS tangent path."""

import numpy as np
import pytest

from quantumbridge.information import MatrixProductState


@pytest.mark.parametrize("theta", [0.0, 0.37, -1.2, 3.0])
@pytest.mark.parametrize("phase", [1.0, 1j, -0.3 + 0.4j])
def test_ry_derivative_keeps_its_amplitude_and_complex_scale(theta, phase):
    from quantumbridge.information.mps_tangent import MPSTangent

    c, s = np.cos(theta / 2), np.sin(theta / 2)
    derivative = 0.5 * np.array([[-s, -c], [c, -s]], complex)
    source = MatrixProductState.zero(1)
    tangent = MPSTangent(source, phase).applied(derivative, (0,))
    expected = phase * np.array([-0.5 * s, 0.5 * c])
    assert tangent.inner(tangent).real == pytest.approx(abs(phase) ** 2 / 4)
    for bit in range(2):
        basis = MatrixProductState.zero(1)
        if bit:
            basis.apply(np.array([[0, 1], [1, 0]], complex), (0,))
        assert MPSTangent(basis).inner(tangent) == pytest.approx(expected[bit])
    np.testing.assert_array_equal(source.statevector(), [1, 0])


def test_ordinary_branch_entry_still_normalizes_nonunitary_updates():
    theta = 0.37
    derivative = 0.5 * np.array(
        [[-np.sin(theta / 2), -np.cos(theta / 2)],
         [np.cos(theta / 2), -np.sin(theta / 2)]], complex
    )
    branch = MatrixProductState.zero(1).apply(derivative, (0,))
    assert np.linalg.norm(branch.statevector()) == pytest.approx(1.0)
    np.testing.assert_allclose(
        branch.statevector(), [-np.sin(theta / 2), np.cos(theta / 2)], atol=1e-15
    )


@pytest.mark.parametrize("small", [1e-100, 1e-200, 1e-300])
@pytest.mark.parametrize("phase", [1.0, 1j, -0.6 + 0.8j])
def test_tiny_nonzero_tangent_survives_before_norm_squared_underflows(small, phase):
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(1)
    tangent = MPSTangent(source).applied(small * phase * np.eye(2), (0,))
    assert tangent.num_components == 1
    actual = MPSTangent(source).inner(tangent)
    assert actual / (small * phase) == pytest.approx(1, abs=2e-14)


@pytest.mark.parametrize("scalar,operator", [(1e-300, 1e300), (1e300, 1e-300)])
def test_balanced_scale_factors_do_not_overflow_or_underflow(scalar, operator):
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(2)
    tangent = MPSTangent(source, scalar * 1j).applied(operator * np.eye(4), (1, 0))
    assert MPSTangent(source).inner(tangent) == pytest.approx(1j)


@pytest.mark.parametrize("kind", ["zero_scale", "zero_operator", "annihilated"])
def test_zero_tangent_is_not_normalized_into_a_state(kind):
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(3)
    tangent = MPSTangent(source, 0 if kind == "zero_scale" else 1)
    matrix = np.zeros((2, 2)) if kind == "zero_operator" else np.diag([0.0, 1.0])
    tangent = tangent.applied(matrix, (2,))
    assert tangent.num_components == 0
    assert tangent.inner(MPSTangent(source)) == 0
    assert tangent.inner(tangent) == 0
    assert tangent.copy().num_qubits == 3


@pytest.mark.parametrize("wires", [(0, 1), (0, 3), (3, 0), (3, 1, 0)])
def test_complex_nonunitary_routing_and_bilinear_paulis_match_dense_math(wires):
    from quantumbridge.information.mps_tangent import MPSTangent
    from quantumbridge.utils.math import apply_unitary, pauli_matrix

    rng = np.random.default_rng(23)
    vector = rng.normal(size=16) + 1j * rng.normal(size=16)
    vector /= np.linalg.norm(vector)
    state = MatrixProductState.from_statevector(vector, cutoff=0)
    dimension = 1 << len(wires)
    matrix = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    scale = -0.3 + 0.8j
    expected = apply_unitary(scale * vector, matrix, wires, 4)
    tangent = MPSTangent(state, scale).applied(matrix, wires)
    initial = MPSTangent(state)
    for label in ["IIII", "XYZI", "YYZX"]:
        operator = np.array([[1]], complex)
        for char in label:
            operator = np.kron(operator, pauli_matrix(char))
        assert initial.inner(tangent, label) == pytest.approx(np.vdot(vector, operator @ expected), abs=3e-12)
        assert tangent.inner(tangent, label) == pytest.approx(np.vdot(expected, operator @ expected), abs=3e-11)
        assert tangent.inner(initial, label) == pytest.approx(initial.inner(tangent, label).conjugate(), abs=3e-12)
    np.testing.assert_allclose(state.statevector(), vector, atol=2e-15)


def test_coherent_sum_has_cross_terms_and_destructive_interference():
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(1)
    a = MPSTangent(source, 1j)
    b = MPSTangent(source, -0.3 + 0.4j)
    total = MPSTangent.linear_combination([(2j, a), (0.7 - 0.2j, b), (-0.3, a)])
    expected = 2j * 1j + (0.7 - 0.2j) * (-0.3 + 0.4j) - 0.3j
    assert MPSTangent(source).inner(total) == pytest.approx(expected)
    assert total.inner(total) == pytest.approx(abs(expected) ** 2)
    zero = MPSTangent.linear_combination([(1, a), (-1, a)])
    assert zero.inner(zero) == 0
    # It is a coherent zero, not an incoherent probability mixture.
    assert zero.num_components == 2


def test_tangent_does_not_inherit_simulation_cutoff_and_refuses_bond_truncation():
    from quantumbridge.information.mps_tangent import MPSTangent

    small = 1e-8
    matrix = np.eye(4, dtype=complex)
    matrix[:, 0] = [1, 0, 0, small]
    source = MatrixProductState.zero(2, cutoff=0.4)
    exact = MPSTangent(source).applied(matrix, (0, 1))
    assert exact.component_states[0].bond_dimensions == (2,)
    other = MatrixProductState.zero(2).apply(np.array([[0, 1], [1, 0]]), (0,)).apply(np.array([[0, 1], [1, 0]]), (1,))
    assert MPSTangent(other).inner(exact) == pytest.approx(small, rel=1e-13, abs=0)
    limited = MatrixProductState.zero(2, max_bond_dim=1)
    with pytest.raises(MemoryError, match="refusing derivative truncation"):
        MPSTangent(limited).applied(matrix, (0, 1))
    np.testing.assert_array_equal(limited.statevector(), [1, 0, 0, 0])


def test_truncated_source_is_refused_instead_of_claiming_exact_derivatives():
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.from_statevector(np.array([1, 0, 0, 1]) / np.sqrt(2), max_bond_dim=1)
    with pytest.raises(ValueError, match="previously truncated"):
        MPSTangent(source)


def test_owned_copy_and_exported_components_cannot_mutate_the_source():
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(3)
    tangent = MPSTangent(source, 1j)
    copied = tangent.copy()
    source.apply(np.array([[0, 1], [1, 0]]), (0,))
    exported = tangent.component_states
    exported[0].apply(np.array([[0, 1], [1, 0]]), (1,))
    assert copied.inner(tangent) == pytest.approx(1)
    assert tangent.inner(tangent, "ZII") == pytest.approx(1)
    assert tangent.inner(tangent, "IZI") == pytest.approx(1)


def test_large_real_and_imaginary_scale_components_remain_finite():
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(1)
    result = MPSTangent(source, complex(1e308, 1e308)).applied(np.eye(2), (0,))
    actual = MPSTangent(source).inner(result)
    assert actual.real / 1e308 == pytest.approx(1)
    assert actual.imag / 1e308 == pytest.approx(1)


@pytest.mark.parametrize("scale,factor", [(1e300, 1e300), (1e-300, 1e-300)])
def test_unrepresentable_nonzero_scale_is_explicitly_refused(scale, factor):
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(1)
    tangent = MPSTangent(source, scale)
    with pytest.raises(FloatingPointError, match="flows complex128"):
        tangent.applied(factor * np.eye(2), (0,))
    assert tangent.component_scales == (complex(scale),)


def test_sum_bound_precedes_component_copy_and_rejects_unbounded_iterators(monkeypatch):
    from quantumbridge.information.mps_tangent import MPSTangent

    tangent = MPSTangent(MatrixProductState.zero(1), max_components=1)
    def forbidden(*a, **k):
        pytest.fail("Component limit must be checked before copying a chain")
    monkeypatch.setattr(MatrixProductState, "copy", forbidden)
    with pytest.raises(MemoryError, match="max_components"):
        MPSTangent.linear_combination([(1, tangent), (1, tangent)])
    def unbounded():
        pytest.fail("Unbounded term iterator must not be consumed")
        yield None
    with pytest.raises(ValueError, match="bounded"):
        MPSTangent.linear_combination(unbounded())


@pytest.mark.parametrize("matrix,wires,error", [
    (np.eye(2), (0, 0), ValueError), (np.eye(2), (True,), ValueError),
    (np.eye(2), (2,), ValueError), (np.eye(3), (0,), ValueError),
    (np.array([[1, 0], [0, np.nan]]), (0,), ValueError),
    (np.array([[1, 0], [0, np.inf]]), (0,), ValueError),
    (np.array([[1, 0], [0, 1]], object), (0,), ValueError),
    ([[1, 0], [0, 1]], (0,), TypeError),
])
def test_bad_operator_inputs_are_refused_without_owner_mutation(matrix, wires, error):
    from quantumbridge.information.mps_tangent import MPSTangent

    source = MatrixProductState.zero(2)
    tangent = MPSTangent(source)
    with pytest.raises(error):
        tangent.applied(matrix, wires)
    assert tangent.inner(tangent) == 1


def test_foreign_numpy_protocols_and_wire_iterators_are_not_executed():
    from quantumbridge.information.mps_tangent import MPSTangent

    class Foreign(np.ndarray):
        def __array_ufunc__(self, *a, **k):
            pytest.fail("Foreign ndarray dispatch executed")
        def __array_function__(self, *a, **k):
            pytest.fail("Foreign ndarray dispatch executed")
    tangent = MPSTangent(MatrixProductState.zero(1))
    actual = tangent.applied(np.eye(2).view(Foreign), (0,))
    assert actual.inner(tangent) == 1
    def wires():
        pytest.fail("Foreign wire iterator executed")
        yield 0
    with pytest.raises(TypeError, match="bounded"):
        tangent.applied(np.eye(2), wires())


def test_projection_of_tiny_source_branch_does_not_square_it_to_zero():
    from quantumbridge.information.mps_tangent import MPSTangent

    state = MatrixProductState.from_statevector(np.array([1, 1e-300], complex))
    projected = MPSTangent(state).applied(np.diag([0.0, 1.0]), (0,))
    basis = MatrixProductState.zero(1).apply(np.array([[0, 1], [1, 0]]), (0,))
    assert MPSTangent(basis).inner(projected) / 1e-300 == pytest.approx(1)
    with pytest.raises(FloatingPointError, match="underflows"):
        projected.inner(projected)


@pytest.mark.parametrize("bad", [float("inf"), float("nan"), complex(0, float("inf"))])
def test_nonfinite_scale_is_rejected(bad):
    from quantumbridge.information.mps_tangent import MPSTangent

    with pytest.raises(ValueError, match="finite"):
        MPSTangent(MatrixProductState.zero(1), bad)


@pytest.mark.parametrize("label", ["", "ZZ", "Q", ["Z"]])
def test_bad_pauli_contractions_are_rejected(label):
    from quantumbridge.information.mps_tangent import MPSTangent

    tangent = MPSTangent(MatrixProductState.zero(1))
    with pytest.raises(ValueError, match="Pauli"):
        tangent.inner(tangent, label)


def test_tangent_sum_preserves_narrower_limits_and_width_contract():
    from quantumbridge.information.mps_tangent import MPSTangent

    a = MPSTangent(MatrixProductState.zero(1), max_components=1)
    b = MPSTangent.zero(2)
    with pytest.raises(ValueError, match="widths"):
        MPSTangent.linear_combination([(1, a), (1, b)])
    with pytest.raises(ValueError, match="widths"):
        a.inner(b)
    with pytest.raises(MemoryError, match="max_components"):
        MPSTangent.linear_combination([(1, a), (1, a)], max_components=100)


def test_matrix_dimension_limit_precedes_validation_buffer_allocation(monkeypatch):
    from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
    from quantumbridge.information.mps_tangent import MPSTangent

    tangent = MPSTangent(MatrixProductState.zero(3))
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)):
        monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Dimension limit must precede allocation"))
        with pytest.raises(MemoryError, match="max_matrix_dimension"):
            tangent.applied(np.eye(4), (0, 2))


def test_balanced_overlap_on_100_wires_survives_intermediate_underflow(monkeypatch):
    from decimal import Decimal, localcontext
    from quantumbridge.information.mps_tangent import MPSTangent

    small = 1e-4
    chain = MatrixProductState([
        np.array([small, np.sqrt(1 - small * small)], complex).reshape(1, 2, 1)
        for _ in range(100)
    ])
    other = MatrixProductState.zero(100)
    # QR is backward stable, not relatively accurate in each tiny component.
    # Compare the represented product chain, using independent decimal math.
    with localcontext() as context:
        context.prec = 80
        expected = Decimal.from_float(1e300)
        for tensor in chain._tensors:
            expected *= Decimal.from_float(float(tensor[0, 0, 0].real))
        expected = complex(0, float(expected))
    monkeypatch.setattr(MatrixProductState, "statevector", lambda *a, **k: pytest.fail("Dense overlap"))
    actual = MPSTangent(other).inner(MPSTangent(chain, 1e300j))
    assert actual / expected == pytest.approx(1, abs=8e-13)


def test_matrix_dynamic_range_does_not_silently_annihilate_a_nonzero_branch():
    from quantumbridge.information.mps_tangent import MPSTangent

    basis = MatrixProductState.zero(1).apply(np.array([[0, 1], [1, 0]]), (0,))
    with pytest.raises(FloatingPointError, match="rescaling underflows"):
        MPSTangent(basis).applied(np.diag([1e300, 1e-300]), (0,))
