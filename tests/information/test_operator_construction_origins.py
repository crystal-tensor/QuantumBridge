# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""State-derived coordinates are distinct from raw matrix literal semantics."""

from math import prod
from fractions import Fraction

import numpy as np
import pytest

from quantumbridge.information import Operator, Statevector, DensityMatrix


def public_coordinates(data, dims):
    result = np.empty_like(data)
    order = [np.ravel_multi_index(np.unravel_index(i, dims), dims, order="F")
        for i in range(prod(dims))]
    for row, public_row in enumerate(order):
        for column, public_column in enumerate(order):
            result[public_row, public_column] = data[row, column]
    return result


def assert_projector_rounding(actual, vector):
    # Each complex component is a two-term dot product. Compare with exact
    # input-float arithmetic, bounded by gamma_2, not another rounding path.
    unit_roundoff = Fraction(1, 1 << 53)
    gamma_2 = 2*unit_roundoff/(1-2*unit_roundoff)
    parts = [(Fraction.from_float(float(x.real)),
              Fraction.from_float(float(x.imag))) for x in vector]
    assert actual.shape == (len(vector), len(vector))
    assert actual.dtype == np.complex128 and np.isfinite(actual).all()
    for row, (a, b) in enumerate(parts):
        for column, (c, d) in enumerate(parts):
            for component, terms in ((actual[row, column].real, (a*c, b*d)),
                                     (actual[row, column].imag, (b*c, -a*d))):
                exact = sum(terms)
                error = abs(Fraction.from_float(float(component))-exact)
                bound = gamma_2*sum(abs(term) for term in terms)
                assert error <= bound, (row, column, float(error), float(bound))


@pytest.mark.parametrize("dims", [(2,), (2, 2), (2, 2, 2), (2, 2, 2, 2), (2, 3), (3, 2)])
@pytest.mark.parametrize("factory", ["state", "density"])
def test_state_factory_retains_native_coordinates_without_extra_matrix_copy(dims, factory):
    rng = np.random.default_rng(12401)
    vector = rng.normal(size=prod(dims)) + 1j * rng.normal(size=prod(dims))
    vector /= np.linalg.norm(vector)
    state = Statevector(vector, dims=dims)
    raw = np.outer(vector, vector.conj())
    owner = state if factory == "state" else DensityMatrix(raw, dims=dims)
    operator = owner.to_operator()
    if factory == "state":
        assert_projector_rounding(operator.data, vector)
    else:
        np.testing.assert_array_equal(operator.data, raw)
    assert operator.input_dims() == operator.output_dims() == dims
    assert operator.arithmetic_convention == "native"
    assert np.shares_memory(operator.data, owner.data) == (factory == "density")
    native_snapshot = operator.data.copy()
    expected = public_coordinates(native_snapshot, dims)
    public = operator.as_qiskit_operator()
    np.testing.assert_array_equal(public.data, expected)
    assert public.input_dims() == public.output_dims() == dims
    np.testing.assert_array_equal(public.as_native_operator().data, native_snapshot)
    np.testing.assert_array_equal(operator.data, native_snapshot)
    assert not np.shares_memory(public.data, operator.data)


@pytest.mark.parametrize("factory", ["state", "density"])
@pytest.mark.parametrize("method", ["copy", "adjoint", "power"])
def test_state_operator_derivations_preserve_origin_not_a_second_conversion(factory, method):
    vector = np.array([1, 2j, -3 + 1j, 4 - 2j], complex) / np.sqrt(35)
    state = Statevector(vector)
    owner = state if factory == "state" else DensityMatrix.from_statevector(state)
    operator = owner.to_operator()
    derived = operator.power(2) if method == "power" else getattr(operator, method)()
    raw = operator.data @ operator.data if method == "power" else operator.data.conj().T if method == "adjoint" else operator.data
    np.testing.assert_allclose(derived.data, raw, atol=2e-15, rtol=0)
    np.testing.assert_allclose(derived.as_qiskit_operator().data,
        public_coordinates(raw, (2, 2)), atol=2e-15, rtol=0)


@pytest.mark.parametrize("dims", [(2, 2), (2, 3), (3, 2)])
def test_raw_operator_remains_literal_even_for_same_numeric_state_projector(dims):
    vector = np.arange(1, prod(dims) + 1) + 1j * np.arange(prod(dims))
    raw = np.outer(vector, vector.conj())
    operator = Operator(raw, dims, dims)
    np.testing.assert_array_equal(operator.data, raw)
    np.testing.assert_array_equal(operator.as_qiskit_operator().data, raw)
    assert operator.__dict__.get("_public_matrix_basis") is None


@pytest.mark.parametrize("factory", [Statevector, DensityMatrix])
def test_state_factory_does_not_admit_foreign_property_as_native_origin(factory):
    class Foreign(factory):
        @property
        def data(self):pytest.fail("Foreign state property was read")
    with pytest.raises((TypeError, ValueError)):
        factory.to_operator(object.__new__(Foreign))
