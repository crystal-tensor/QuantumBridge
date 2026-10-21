# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent partial-transpose algebra, composition and ownership contracts."""

from contextlib import nullcontext
import gc
from itertools import product
from math import prod

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


CASES = [
    ((2,), ()), ((2,), (0,)), ((3,), (0,)), ((4,), (0,)),
    ((2,2), (0,)), ((3,2), (1,)), ((3,2), (0,1)),
    ((2,4), (1,)), ((2,3,2), (1,)), ((2,3,2), (0,2)),
    ((2,3,2), (2,0)), ((3,2,4), (0,)), ((3,2,4), (2,0)),
    ((3,2,4), (2,1,0)), ((1,), (0,)), ((), ()),
]


def fixture(dims, kind):
    size = prod(dims)
    values = np.arange(1, size + 1)
    vector = np.cos(values) + 1j * np.sin(2 * values)
    vector /= np.linalg.norm(vector)
    other = np.sin(3 * values) + 1j * np.cos(2 * values)
    other /= np.linalg.norm(other)
    pure = np.outer(vector, vector.conj())
    if kind == "pure": return pure
    if kind == "mixed": return .3 * pure + .7 * np.outer(other, other.conj())
    raw = (np.arange(size*size).reshape(size,size) + 1j*np.arange(size*size,0,-1).reshape(size,size)) / max(size,1)
    return raw if kind == "nonhermitian" else 3.7 * pure


def enumeration_reference(matrix, dims, selected):
    result = np.zeros_like(matrix)
    for row, column in product(range(len(matrix)), repeat=2):
        r, c = list(np.unravel_index(row,dims)), list(np.unravel_index(column,dims))
        for axis in selected: r[axis], c[axis] = c[axis], r[axis]
        result[row,column] = matrix[np.ravel_multi_index(tuple(r),dims),np.ravel_multi_index(tuple(c),dims)]
    return result


def tensor_reference(matrix, dims, selected):
    count = len(dims)
    axes = list(range(2*count))
    for axis in selected: axes[axis],axes[axis+count] = axes[axis+count],axes[axis]
    return matrix.reshape(dims+dims).transpose(axes).reshape(matrix.shape)


@pytest.mark.parametrize("dims,selected", CASES)
@pytest.mark.parametrize("kind", ["pure","mixed","nonhermitian","unnormalized"])
@pytest.mark.parametrize("strided", [False,True])
def test_full_complex_matrix_matches_two_independent_oracles(dims, selected, kind, strided):
    matrix = fixture(dims,kind)
    value = DensityMatrix(matrix.copy(),dims=dims)
    if strided:
        backing = np.zeros((len(matrix)*2,len(matrix)*3),complex)
        view = backing[::2,::3].T
        view[:] = matrix
        value.data = view
    before = value.data.copy()
    with ResourceScope(Ledger()):
        result = value.partial_transpose(selected)
        restored = result.partial_transpose(selected)
    np.testing.assert_array_equal(result.data,enumeration_reference(matrix,dims,selected))
    np.testing.assert_array_equal(result.data,tensor_reference(matrix,dims,selected))
    np.testing.assert_array_equal(restored.data,matrix)
    np.testing.assert_array_equal(value.data,before)
    assert result.dims() == dims and result.dim == matrix.shape
    assert result.num_qubits == (len(dims) if all(d==2 for d in dims) else None)
    assert result.data.dtype == np.dtype(complex)
    assert not np.shares_memory(result.data,value.data)
    assert result.trace() == pytest.approx(value.trace(),abs=1e-12)
    assert result.purity() == pytest.approx(value.purity(),rel=2e-14,abs=1e-12)
    if kind!="nonhermitian":
        np.testing.assert_allclose(result.data,result.data.conj().T,atol=3e-15,rtol=0)
    if len(selected)==len(dims): np.testing.assert_array_equal(result.data,matrix.T)


@pytest.mark.parametrize("managed", [False,True])
def test_order_is_irrelevant_and_disjoint_transposes_compose(managed):
    dims = (3,2,4)
    value = DensityMatrix(fixture(dims,"nonhermitian"),dims=dims)
    with ResourceScope(Ledger()) if managed else nullcontext():
        together = value.partial_transpose([0,2])
        reverse = value.partial_transpose([2,0])
        separate = value.partial_transpose([0]).partial_transpose([2])
    np.testing.assert_array_equal(together.data,reverse.data)
    np.testing.assert_array_equal(together.data,separate.data)


@pytest.mark.parametrize("selected", [None,[0,0],[-1],[3],[True],[1.0],["0"],[[0]],1])
def test_invalid_targets_reject_before_output_factory(selected, monkeypatch):
    value = DensityMatrix(fixture((2,3,2),"mixed"),dims=(2,3,2))
    before = value.data.copy()
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Invalid targets reached output allocation"))
    with ResourceScope(Ledger()), pytest.raises((ValueError,TypeError,UnsupportedFeature)):
        value.partial_transpose(selected)
    np.testing.assert_array_equal(value.data,before)


def test_output_admission_reuse_and_real_escaped_view_lifetime(monkeypatch):
    value = DensityMatrix(fixture((3,2),"mixed"),dims=(3,2))
    before = value.data.copy()
    amount = value.data.nbytes
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):
        first = value.partial_transpose((0,))
        with monkeypatch.context() as patch:
            patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Output factory preceded admission"))
            with pytest.raises(MemoryError): value.partial_transpose((1,))
        view = first.data[:,0]
        del first
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == amount
        del view
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 0
        recovered = value.partial_transpose((1,))
    assert ledger.receipt()["live_memory_bytes"] == amount
    np.testing.assert_array_equal(value.data,before)
    del recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("dtype", [float,np.complex64])
def test_known_numeric_conversion_and_output_are_admitted_as_one_group(dtype,monkeypatch):
    raw = np.arange(36).reshape(6,6).astype(dtype)
    value = DensityMatrix(raw,dims=(3,2))
    value.data = raw
    required = 2*36*16
    with monkeypatch.context() as patch:
        patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Input or output factory preceded group admission"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=required-1))),pytest.raises(MemoryError):
            value.partial_transpose((0,))
    ledger = Ledger(Limits(max_total_memory_bytes=required))
    with ResourceScope(ledger): result = value.partial_transpose((0,))
    np.testing.assert_array_equal(result.data,enumeration_reference(raw,(3,2),(0,)))
    assert ledger.receipt()["peak_memory_bytes"] == required
    assert ledger.receipt()["live_memory_bytes"] == 36*16


def test_outputs_follow_actual_source_owner_without_scope_and_active_owner_with_scope():
    a,b = Ledger(),Ledger()
    with ResourceScope(a): value = DensityMatrix.from_int(3,(3,2))
    amount = value.data.nbytes
    assert a.receipt()["live_memory_bytes"] == amount
    first = value.partial_transpose((0,))
    assert a.receipt()["live_memory_bytes"] == 2*amount
    with ResourceScope(b): second = value.partial_transpose((1,))
    assert b.receipt()["live_memory_bytes"] == amount
    del first,second,value
    gc.collect()
    assert a.receipt()["live_memory_bytes"] == b.receipt()["live_memory_bytes"] == 0


def test_explicit_numeric_subclass_does_not_dispatch_foreign_array_protocols():
    class Trap(np.ndarray):
        def __array_function__(self,*a,**k): pytest.fail("Foreign array function dispatched")
        def __array_ufunc__(self,*a,**k): pytest.fail("Foreign ufunc dispatched")
        def __getitem__(self,*a,**k): pytest.fail("Foreign indexing dispatched")
    matrix = fixture((3,2),"nonhermitian")
    value = DensityMatrix(matrix.copy(),dims=(3,2))
    value.data = value.data.view(Trap)
    with ResourceScope(Ledger()): result = value.partial_transpose([np.int64(1)])
    np.testing.assert_array_equal(result.data,enumeration_reference(matrix,(3,2),(1,)))


def test_managed_foreign_receiver_targets_and_object_buffer_reject_without_callbacks():
    class Foreign(DensityMatrix):
        @property
        def data(self): pytest.fail("Foreign receiver property dispatched")
    class Targets:
        def __iter__(self): pytest.fail("Foreign target iterator dispatched")
    value = DensityMatrix.from_int(0,(3,2))
    with ResourceScope(Ledger()):
        with pytest.raises(UnsupportedFeature): object.__new__(Foreign).partial_transpose([0])
        with pytest.raises(UnsupportedFeature): value.partial_transpose(Targets())
        value.data = np.array([[object()]*6]*6,dtype=object)
        with pytest.raises(UnsupportedFeature): value.partial_transpose([0])


@pytest.mark.parametrize("probability,phase,scale", [(.5,1,1),(.7,1j,1),(.2,-1j,2)])
def test_actual_entangled_vector_density_partial_transpose_chain(probability,phase,scale):
    vector = np.zeros(6,complex)
    vector[0],vector[3] = np.sqrt(probability),phase*np.sqrt(1-probability)
    vector *= scale
    with ResourceScope(Ledger()):
        density = Statevector(vector,dims=(3,2)).to_density_matrix()
        actual = density.partial_transpose([1])
    matrix = np.outer(vector,vector.conj())
    reference = enumeration_reference(matrix,(3,2),(1,))
    np.testing.assert_array_equal(actual.data,reference)
    eigenvalues = np.linalg.eigvalsh(actual.data)
    np.testing.assert_allclose(eigenvalues,np.linalg.eigvalsh(reference),atol=3e-15,rtol=0)
    analytical = scale**2*np.sort([probability,1-probability,np.sqrt(probability*(1-probability)),
                                 -np.sqrt(probability*(1-probability)),0,0])
    np.testing.assert_allclose(eigenvalues,analytical,atol=4e-15,rtol=0)
    assert eigenvalues[0]<0 and actual.trace()==pytest.approx(scale**2)


def test_actual_mapped_evolution_reduction_partial_transpose_expectation_chain():
    dims = (3,2,4)
    x = np.arange(1,25)
    vector = np.sin(x)+1j*np.cos(2*x)
    vector /= np.linalg.norm(vector)
    matrix = np.array([[1,.2j,0],[.3,.7,.1j],[.2j,0,1.2]],complex)
    observable = np.array([[1,1j,.2],[0,-.5,.3j],[.1,.2,2j]],complex)
    with ResourceScope(Ledger()):
        evolved = Statevector(vector,dims=dims).evolve(Operator(matrix,(3,),(3,)),qargs=[0])
        reduced = evolved.to_density_matrix().partial_trace((2,0))
        transposed = reduced.partial_transpose([1])
        expectation = transposed.expectation_value(Operator(observable,(3,),(3,)),qargs=[0])
    reference_vector = np.kron(matrix,np.eye(8))@vector
    reference_density = np.outer(reference_vector,reference_vector.conj())
    reference_reduced = np.trace(reference_density.reshape(dims+dims),axis1=1,axis2=4).reshape(12,12)
    reference = enumeration_reference(reference_reduced,(3,4),(1,))
    np.testing.assert_allclose(transposed.data,reference,atol=3e-15,rtol=0)
    assert transposed.dims() == (3,4)
    np.testing.assert_allclose(expectation,np.trace(reference@np.kron(observable,np.eye(4))),atol=3e-15,rtol=0)


@pytest.mark.parametrize("dims,selected", CASES)
@pytest.mark.parametrize("kind", ["pure","mixed","nonhermitian"])
def test_optional_public_complete_numeric_result_uses_explicit_wire_translation(dims,selected,kind):
    public = pytest.importorskip("qiskit.quantum_info")
    matrix = fixture(dims,kind)
    native = DensityMatrix(matrix,dims=dims).partial_transpose(selected)
    expected = public.DensityMatrix(matrix,dims=dims[::-1]).partial_transpose([len(dims)-1-i for i in selected])
    np.testing.assert_array_equal(native.data,expected.data)
    assert native.dims() == expected.dims()[::-1]
    assert native.num_qubits == expected.num_qubits
    assert native.dim == expected.data.shape and native.data.dtype == expected.data.dtype
