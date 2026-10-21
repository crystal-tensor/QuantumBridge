# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent vector/matrix and analytic spectral state arithmetic checks."""

from contextlib import nullcontext
import gc
from math import prod

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


DIMS = [(3,), (4,), (2, 4), (3, 2), (2, 3, 2), (), (1,)]


def vector(dims, shift=0):
    x = np.arange(prod(dims)) + shift + .3
    return (np.cos(x * .7) + 1j * np.sin(x * .4 + .2)) / np.sqrt(prod(dims))


def state(cls, dims, shift=0):
    values = vector(dims, shift)
    data = values if cls is Statevector else .7 * np.outer(values, values.conj()) + .3 * np.diag(abs(values)**2)
    return cls(data, dims=dims)


@pytest.mark.parametrize("dims", DIMS)
@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("operation", ["add", "sub", "scale", "rscale", "divide", "neg"])
def test_complex_arithmetic_is_actual_linear_algebra_with_left_dimensions(dims, cls, managed, operation):
    a, b = state(cls, dims), state(cls, dims, .8)
    before, other = a.data.copy(), b.data.copy()
    scalar = .2 + .7j
    expected = {"add": before + other, "sub": before - other,
                "scale": before * scalar, "rscale": scalar * before,
                "divide": before / scalar, "neg": -before}[operation]
    ledger = Ledger()
    with ResourceScope(ledger) if managed else nullcontext():
        if operation == "add": result = a + b
        elif operation == "sub": result = a - b
        elif operation == "scale": result = a * scalar
        elif operation == "rscale": result = scalar * a
        elif operation == "divide": result = a / scalar
        else: result = -a
    np.testing.assert_allclose(result.data, expected, atol=3e-14, rtol=0)
    np.testing.assert_array_equal(a.data, before)
    np.testing.assert_array_equal(b.data, other)
    assert result.dims() == dims and type(result) is cls
    assert not np.shares_memory(result.data, a.data)
    assert not np.shares_memory(result.data, b.data)
    if managed:
        assert ledger.receipt()["live_memory_bytes"] == result.data.nbytes
        del result
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("right_dims", [(2, 2, 2), (8,), (4, 2)])
def test_flat_addition_preserves_left_partition_without_claiming_same_subsystems(cls, right_dims):
    a, b = state(cls, (2, 4)), state(cls, right_dims, .3)
    with ResourceScope(Ledger()):
        added, subtracted = a + b, a - b
    assert added.dims() == subtracted.dims() == (2, 4)
    np.testing.assert_allclose(added.data, a.data + b.data, atol=3e-14, rtol=0)
    np.testing.assert_allclose(subtracted.data, a.data - b.data, atol=3e-14, rtol=0)
    if cls is Statevector:
        with ResourceScope(Ledger()), pytest.raises(ValueError):
            a.inner(b)


@pytest.mark.parametrize("dims", DIMS)
@pytest.mark.parametrize("managed", [False, True])
def test_vector_trace_purity_and_inner_have_independent_unnormalized_math(dims, managed):
    a, b = state(Statevector, dims), state(Statevector, dims, .8)
    norm2 = sum(abs(complex(x))**2 for x in a.data)
    expected_inner = np.vdot(a.data, b.data)
    with ResourceScope(Ledger()) if managed else nullcontext():
        trace, purity, inner = a.trace(), a.purity(), a.inner(b)
    np.testing.assert_allclose(trace, norm2, atol=3e-14, rtol=0)
    np.testing.assert_allclose(purity, norm2**2, atol=3e-14, rtol=0)
    np.testing.assert_allclose(inner, expected_inner, atol=3e-14, rtol=0)
    assert isinstance(trace, np.floating) and isinstance(purity, np.floating)
    assert not hasattr(Statevector, "norm") and not hasattr(DensityMatrix, "inner")


@pytest.mark.parametrize("dims", DIMS[:5])
@pytest.mark.parametrize("scale", [1, 2.3])
def test_density_purity_matches_direct_trace_and_independent_known_spectrum(dims, scale):
    size = prod(dims)
    weights = np.arange(1, size + 1, dtype=float)
    weights /= weights.sum()
    indices = np.arange(size)
    unitary = np.exp(2j * np.pi * np.outer(indices, indices) / size) / np.sqrt(size)
    matrix = scale * (unitary @ np.diag(weights) @ unitary.conj().T)
    density = DensityMatrix(matrix, dims=dims)
    expected = np.trace(matrix @ matrix)
    spectral = scale**2 * sum(weight**2 for weight in weights)
    with ResourceScope(Ledger()):
        actual = density.purity()
        trace = density.trace()
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(actual, spectral, atol=3e-14, rtol=0)
    np.testing.assert_allclose(trace, scale, atol=3e-14, rtol=0)


@pytest.mark.parametrize("managed", [False, True])
def test_nonhermitian_density_purity_is_trace_square_not_a_frobenius_norm(managed):
    matrix = np.array([[1 + .2j, .3j], [.1, .4 - .7j]])
    value = DensityMatrix(matrix)
    expected = np.trace(matrix @ matrix)
    assert abs(expected.imag) > .09
    with ResourceScope(Ledger()) if managed else nullcontext():
        actual = value.purity()
    np.testing.assert_allclose(actual, expected, atol=2e-15, rtol=0)
    assert isinstance(actual, np.complexfloating)
    assert abs(actual - np.sum(abs(matrix)**2)) > .1


@pytest.mark.parametrize("size,expected", [(2, .5), (3, 1/3), (4, .25)])
def test_maximally_mixed_purity_is_reciprocal_dimension(size, expected):
    rho = DensityMatrix(np.eye(size) / size, dims=(size,))
    assert rho.purity() == pytest.approx(expected, abs=1e-15)
    assert rho.trace() == 1
    assert rho.is_valid()


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("operation", ["add", "sub", "scale", "neg"])
def test_arithmetic_denies_before_first_output_factory_or_ufunc(cls, operation, monkeypatch):
    a, b = state(cls, (2, 3)), state(cls, (2, 3), .3)
    def forbidden(*a, **k):
        pytest.fail("Arithmetic output/core work preceded resource admission")
    for name in ("empty", "add", "subtract", "multiply"):
        monkeypatch.setattr(np, name, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=a.data.size * 16 - 1))), pytest.raises(MemoryError):
        if operation == "add": a + b
        elif operation == "sub": a - b
        elif operation == "scale": a * (.2 + .7j)
        else: -a


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_both_numeric_conversions_and_output_are_one_known_group(cls, monkeypatch):
    a, b = state(cls, (2, 3)), state(cls, (2, 3), .3)
    a.data = a.data.real.copy()
    raw = b.data.tolist()
    expected = a.data + b.data
    group = 3 * a.data.size * 16
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Partial input conversion before whole admission"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=group - 1))), pytest.raises(MemoryError):
            a + raw
    ledger = Ledger(Limits(max_total_memory_bytes=group))
    with ResourceScope(ledger):
        result = a + raw
    np.testing.assert_allclose(result.data, expected, atol=3e-14, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == result.data.nbytes


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_escaped_arithmetic_output_view_keeps_lease_and_allows_real_recovery(cls):
    a = state(cls, (2, 3))
    size = a.data.size * 16
    ledger = Ledger(Limits(max_total_memory_bytes=2*size-1))
    with ResourceScope(ledger):
        result = a * 2
    view = result.data[::2]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == size
    with ResourceScope(ledger), pytest.raises(MemoryError):
        a * .5
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):
        recovered = a * .5
    np.testing.assert_allclose(recovered.data, .5 * a.data, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_outside_scope_new_arithmetic_follows_actual_source_storage_account(cls):
    ledger = Ledger()
    with ResourceScope(ledger):
        a = cls.from_int(0, (2, 3))
    size = a.data.nbytes
    result = a * 2
    assert ledger.receipt()["live_memory_bytes"] == 2*size
    view = result.data[::2]
    del result, a
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == size
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_zero_division_and_bad_shapes_are_rejected_before_a_numeric_factory(cls, monkeypatch):
    a, b = state(cls, (3,)), state(cls, (4,))
    before = a.data.copy()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid arithmetic allocated output"))
    with ResourceScope(Ledger()):
        with pytest.raises(ZeroDivisionError): a / 0
        with pytest.raises(ValueError): a + b
        with pytest.raises(ValueError): a - b
    np.testing.assert_array_equal(a.data, before)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_managed_strided_readonly_queries_do_not_flatten_or_build_a_matrix_product(cls, monkeypatch):
    a = state(cls, (2, 3))
    raw = a.data.copy()
    backing = np.zeros((12, 18), complex) if cls is DensityMatrix else np.zeros(18, complex)
    view = backing[::2, ::3].T if cls is DensityMatrix else backing[::3]
    view[:] = raw
    a.data = view
    expected_trace = np.vdot(raw, raw).real if cls is Statevector else np.trace(raw)
    expected_purity = expected_trace**2 if cls is Statevector else np.trace(raw @ raw)
    def forbidden(*a, **k):
        pytest.fail("Read-only scalar query allocated/packed a numeric array")
    for name in ("empty", "vdot", "matmul", "trace", "reshape"):
        monkeypatch.setattr(np, name, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))):
        trace, purity, exported = a.trace(), a.purity(), a.to_dict()
        if cls is Statevector:
            inner = a.inner(Statevector(raw, dims=(2, 3)))
            np.testing.assert_allclose(inner, expected_trace, atol=3e-14, rtol=0)
    np.testing.assert_allclose(trace, expected_trace, atol=3e-14, rtol=0)
    np.testing.assert_allclose(purity, expected_purity, atol=3e-14, rtol=0)
    assert exported


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_export_keeps_tiny_values_omits_rounded_zeros_and_has_ordered_keys(cls):
    values = np.array([1e-16 + 1e-17j, .1234 + .0003j, 0])
    a = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=(3,))
    data = a.to_dict()
    assert ("0" if cls is Statevector else "0|0") in data
    assert a.to_dict(decimals=0) == {}
    rounded = a.to_dict(decimals=2)
    assert set(rounded) == ({"1"} if cls is Statevector else {"1|1"})
    matrix = np.zeros((22, 22), complex)
    matrix[0, 21], matrix[21, 0] = .2 + .7j, -.4j
    if cls is DensityMatrix:
        a = cls(matrix, dims=(2, 11))
        assert a.to_dict() == {"1,10|0,0": .2 + .7j, "0,0|1,10": -.4j}
    else:
        a = cls(matrix[0], dims=(2, 11))
        assert a.to_dict() == {"1,10": .2 + .7j}


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
def test_validity_defaults_and_explicit_tolerances_do_not_normalize(cls, managed):
    values = np.array([np.sqrt(1 + 5e-6), 0])
    a = cls(values if cls is Statevector else np.outer(values, values), dims=(2,))
    before = a.data.copy()
    with ResourceScope(Ledger()) if managed else nullcontext():
        assert a.is_valid(atol=None, rtol=None)
        assert not a.is_valid(atol=0, rtol=0)
        assert not a.is_valid(atol=1e-8, rtol=0)
    np.testing.assert_array_equal(a.data, before)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("entry", [np.nan, np.inf])
def test_nonfinite_values_remain_nonfinite_and_validity_returns_false(cls, entry):
    values = np.array([entry, 0, 0])
    a = cls(values if cls is Statevector else np.diag(values), dims=(3,))
    with ResourceScope(Ledger()), np.errstate(invalid="ignore", over="ignore"):
        assert not a.is_valid()
        assert not np.isfinite(a.trace())
        assert not np.isfinite(a.purity())
        assert a.to_dict()


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_explicit_numeric_subclasses_do_not_dispatch_foreign_protocols(cls):
    class Trap(np.ndarray):
        def __array_function__(self, *a, **k): pytest.fail("Foreign array function dispatched")
        def __array_ufunc__(self, *a, **k): pytest.fail("Foreign ufunc dispatched")
        def __getitem__(self, *a, **k): pytest.fail("Foreign item access dispatched")
    a, b = state(cls, (2, 3)), state(cls, (2, 3), .3)
    before = a.data.copy()
    other = b.data.copy()
    a.data, b.data = a.data.view(Trap), b.data.view(Trap)
    with ResourceScope(Ledger()):
        result = (a + b) * (.2 + .7j)
        a.to_dict()
        a.trace()
        a.purity()
        a.is_valid()
        if cls is Statevector: a.inner(b)
    np.testing.assert_allclose(result.data, (before + other) * (.2 + .7j), atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_opaque_operands_and_object_arrays_are_rejected_without_running_conversion(cls):
    class Foreign:
        def __array__(self, *a, **k): pytest.fail("Foreign array conversion dispatched")
    a = state(cls, (3,))
    for operand in (Foreign(), np.array([object()] * 3, dtype=object)):
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            a + operand


def test_three_native_arithmetic_workflows_distinguish_interference_and_mixing():
    zero, one = Statevector.from_int(0, (3,)), Statevector.from_int(1, (3,))
    op = Operator(np.diag([1., -1., .5]), (3,), (3,))
    with ResourceScope(Ledger()):
        coherent = (zero + 1j * one) / np.sqrt(2)
        assert coherent.inner(coherent) == pytest.approx(1)
        assert coherent.expectation_value(op) == pytest.approx(0, abs=1e-15)
        mixture = .3 * DensityMatrix.from_statevector(zero) + .7 * DensityMatrix.from_statevector(one)
        assert mixture.is_valid()
        assert mixture.purity() == pytest.approx(.3**2 + .7**2)
        assert mixture.partial_trace((0,)).expectation_value(op) == pytest.approx(-.4)
        assert DensityMatrix.from_statevector(coherent).purity() == pytest.approx(1)
        mixed = Statevector.from_int(1, (2,)).tensor(coherent) + .2j * Statevector.from_int(4, (2, 3))
        density = DensityMatrix.from_statevector(mixed)
        transform = Operator(np.diag([1, 2j, .5]), (3,), (3,))
        evolved = density.evolve(transform, (1,))
        actual = evolved.expectation_value(op, (1,))
    full = np.kron(np.eye(2), transform.data)
    expected_density = full @ np.outer(mixed.data, mixed.data.conj()) @ full.conj().T
    expected = np.trace(expected_density @ np.kron(np.eye(2), op.data))
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_managed_operand_inspection_does_not_consult_a_foreign_class_property(cls):
    class Foreign:
        @property
        def __class__(self): pytest.fail("Opaque operand class property dispatched")
        def __array__(self, *a, **k): pytest.fail("Opaque operand conversion dispatched")
    value = state(cls, (3,))
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
        value + Foreign()


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
def test_validity_checks_vector_norm_but_density_trace_not_the_same_square(cls, managed):
    values = np.array([1 + 9e-6, 0])
    value = cls(values if cls is Statevector else np.outer(values, values), dims=(2,))
    with ResourceScope(Ledger()) if managed else nullcontext():
        assert value.is_valid() is (cls is Statevector)
        assert not value.is_valid(atol=0, rtol=0)


@pytest.mark.parametrize("kind", ["native", "list", "array", "column"])
@pytest.mark.parametrize("subtract", [False, True])
def test_density_vector_coercion_is_an_outer_product_not_coherent_amplitude_addition(kind, subtract, monkeypatch):
    dims = (3,)
    value = state(DensityMatrix, dims)
    pure = state(Statevector, dims, .7)
    expected = value.data + (-1 if subtract else 1) * np.outer(pure.data, pure.data.conj())
    argument = pure if kind == "native" else pure.data.tolist() if kind == "list" else pure.data[:, None] if kind == "column" else pure.data
    known = value.data.nbytes + (pure.data.nbytes if kind == "list" else 0)
    monkeypatch.setattr(np, "outer", lambda *a, **k: pytest.fail("Full temporary outer product allocated"))
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        result = value - argument if subtract else value + argument
    np.testing.assert_allclose(result.data, expected, atol=3e-14, rtol=0)
    assert result.dims() == dims
    assert ledger.receipt()["live_memory_bytes"] == result.data.nbytes


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("scalar", [np.float32(.2), np.complex64(.2j), np.int32(3)])
def test_numpy_scalar_division_uses_the_actual_scalar_reciprocal_precision(cls, scalar):
    value = state(cls, (3,))
    expected = value.data * (1 / scalar)
    with ResourceScope(Ledger()):
        actual = value / scalar
        reflected = scalar * value
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(reflected.data, scalar * value.data, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_zero_dimensional_numeric_array_is_division_input_not_multiplication_scalar(cls):
    value = state(cls, (3,))
    with ResourceScope(Ledger()):
        actual = value / np.array(2)
        with pytest.raises(TypeError): value * np.array(2)
    np.testing.assert_allclose(actual.data, value.data / 2, atol=3e-14, rtol=0)


def test_raw_inner_uses_actual_inferred_partition_and_column_vectors_are_supported():
    qutrit = state(Statevector, (3,))
    value = state(Statevector, (2, 3))
    with ResourceScope(Ledger()):
        np.testing.assert_allclose(qutrit.inner(qutrit.data.tolist()), np.vdot(qutrit.data, qutrit.data), atol=3e-14, rtol=0)
        np.testing.assert_allclose(qutrit.inner(qutrit.data[:, None]), qutrit.trace(), atol=3e-14, rtol=0)
        with pytest.raises(ValueError): value.inner(value.data)
        added = value + value.data[:, None]
    np.testing.assert_allclose(added.data, 2 * value.data, atol=3e-14, rtol=0)
    assert added.dims() == (2, 3)


def test_density_validity_admits_strided_input_pack_and_eigenvalues_before_first_factory(monkeypatch):
    matrix = np.diag([.2, .3, .5]).astype(complex)
    value = DensityMatrix(matrix, dims=(3,))
    backing = np.zeros((6, 9), complex)
    view = backing[::2, ::3].T
    view[:] = matrix
    value.data = view
    known = matrix.nbytes + 3 * 8
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Validity packing preceded admission"))
        patch.setattr(np.linalg, "eigvalsh", lambda *a, **k: pytest.fail("Eigenvalue work preceded admission"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            value.is_valid()
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    original = np.linalg.eigvalsh
    def observe(data):
        assert type(data) is np.ndarray
        assert data.flags.c_contiguous or data.flags.f_contiguous
        assert data.dtype == np.dtype(complex)
        return original(data)
    with monkeypatch.context() as patch:
        patch.setattr(np.linalg, "eigvalsh", observe)
        with ResourceScope(ledger):
            assert value.is_valid()
    assert ledger.receipt()["peak_memory_bytes"] == known
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_foreign_receiver_scalar_and_tolerance_are_rejected_before_callbacks(cls):
    class ForeignState(cls):
        @property
        def data(self): pytest.fail("Foreign state property dispatched")
    class ForeignFloat(float):
        def __float__(self): pytest.fail("Foreign scalar conversion dispatched")
        def __complex__(self): pytest.fail("Foreign complex conversion dispatched")
    value = state(cls, (3,))
    foreign = object.__new__(ForeignState)
    for method in ("trace", "purity", "to_dict", "is_valid"):
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            getattr(foreign, method)()
    with ResourceScope(Ledger()):
        with pytest.raises(UnsupportedFeature): value * ForeignFloat(2)
        with pytest.raises(UnsupportedFeature): value.is_valid(atol=ForeignFloat(1e-8))
        for atol in (-1, np.nan, np.inf):
            with pytest.raises(ValueError): value.is_valid(atol=atol)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_zero_register_dictionary_is_a_native_extension_not_public_acceptance(cls):
    value = cls.from_int(0, ())
    assert value.to_dict() == ({"0": 1} if cls is Statevector else {"0|0": 1})
    assert value.trace() == value.purity() == 1


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("dims", [(3,), (2, 4), (3, 2), (2, 3, 2), (11,), (2, 11), (11, 2)])
def test_optional_public_arithmetic_and_queries_use_explicit_dimension_conversion(cls, dims):
    public = pytest.importorskip("qiskit.quantum_info")
    a, b = state(cls, dims), state(cls, dims, .7)
    public_cls = public.Statevector if cls is Statevector else public.DensityMatrix
    left, right = public_cls(a.data, dims=dims[::-1]), public_cls(b.data, dims=dims[::-1])
    scalar = .2 + .7j
    with ResourceScope(Ledger()):
        native_results = [a + b, a - b, a * scalar, scalar * a, a / scalar, -a]
        trace, purity, valid = a.trace(), a.purity(), a.is_valid()
        exported = a.to_dict(decimals=3)
    expected_results = [left + right, left - right, left * scalar, scalar * left, left / scalar, -left]
    for actual, expected in zip(native_results, expected_results):
        np.testing.assert_allclose(actual.data, expected.data, atol=3e-14, rtol=0)
        assert actual.dims() == expected.dims()[::-1]
    np.testing.assert_allclose(trace, left.trace(), atol=3e-14, rtol=0)
    np.testing.assert_allclose(purity, left.purity(), atol=3e-14, rtol=0)
    assert valid is left.is_valid()
    assert exported == left.to_dict(decimals=3)


@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("route", ["initial", "replacement"])
def test_public_style_query_tolerance_does_not_relax_physical_simulator_admission(managed, route):
    from quantumbridge import Circuit
    from quantumbridge.devices import DensityMatrixDevice
    raw = np.diag([1.000001, 0]).astype(complex)
    value = DensityMatrix(raw)
    assert value.is_valid()
    assert not value.is_valid(atol=1e-10, rtol=0)
    with ResourceScope(Ledger()) if managed else nullcontext():
        with pytest.raises(ValueError):
            if route == "initial":
                DensityMatrixDevice(initial_state=raw).density_matrix(Circuit(1))
            else:
                Circuit(1).set_density_matrix(raw)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("operation", ["multiply", "reflected", "divide"])
def test_existing_unmanaged_fraction_numbers_do_not_become_object_dtype_ufunc_errors(cls, operation):
    from fractions import Fraction
    value = state(cls, (3,))
    scalar = Fraction(1, 2)
    expected = value.data * (.5 if operation != "divide" else 2)
    if operation == "multiply": actual = value * scalar
    elif operation == "reflected": actual = scalar * value
    else: actual = value / scalar
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    assert actual.dims() == (3,) and actual.data.dtype == np.dtype(complex)
