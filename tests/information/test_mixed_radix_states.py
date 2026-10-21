# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent native mixed-radix construction and subsystem contracts."""

import gc
from itertools import product
from math import prod

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Statevector


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims,index", [((2,4),5),((3,2),4),((2,3,2),7),((6,),3),((1,),0),((),0)])
@pytest.mark.parametrize("managed", [False,True])
def test_basis_constructor_preserves_declared_subsystems_and_actual_numbers(cls,dims,index,managed):
    ledger=Ledger()
    if managed:
        with ResourceScope(ledger):state=cls.from_int(index,dims)
    else:state=cls.from_int(index,dims)
    vector=np.zeros(prod(dims),complex)
    vector[index]=1
    expected=vector if cls is Statevector else np.outer(vector,vector.conj())
    np.testing.assert_array_equal(state.data,expected)
    assert state.dims()==dims
    assert state.num_qubits==(len(dims) if all(dim==2 for dim in dims) else None)
    assert state.dim==(prod(dims) if cls is Statevector else (prod(dims),)*2)
    if managed:assert ledger.receipt()["live_memory_bytes"]==state.data.nbytes


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_explicit_numeric_constructor_accepts_mixed_radix_without_changing_legacy_default(cls):
    vector=np.array([1,2j,3,-4j,5,6j],complex)
    vector/=np.linalg.norm(vector)
    data=vector if cls is Statevector else np.outer(vector,vector.conj())
    with pytest.raises(ValueError,match="power of two"):cls(data)
    ledger=Ledger()
    with ResourceScope(ledger):state=cls(data,dims=(3,2))
    np.testing.assert_array_equal(state.data,data)
    assert state.dims()==(3,2) and state.dims([1,0])==(2,3)
    assert state.num_qubits is None
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims", [True,False,0,-1,(2,0),(2,-1),(True,2),(2.,2),(2,3)])
def test_invalid_dimensions_reject_before_input_conversion(cls,dims,monkeypatch):
    data=[1,0,0,0] if cls is Statevector else np.eye(4,dtype=complex).tolist()
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Invalid dimension reached array factory"))
    with ResourceScope(Ledger()),pytest.raises(ValueError):cls(data,dims=dims)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("index", [-1,6,True,1.5])
def test_invalid_basis_index_rejects_before_array_factory(cls,index,monkeypatch):
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Invalid basis index allocated"))
    with ResourceScope(Ledger()),pytest.raises(ValueError):cls.from_int(index,(3,2))


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_mixed_radix_basis_quota_and_actual_last_root(cls,monkeypatch):
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with monkeypatch.context() as patch:
        patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Mixed-radix basis preceded admission"))
        with ResourceScope(ledger),pytest.raises(MemoryError):cls.from_int(4,(3,2))
    assert ledger.receipt()["live_memory_bytes"]==0
    ledger=Ledger()
    with ResourceScope(ledger):state=cls.from_int(4,(3,2))
    amount=state.data.nbytes
    view=state.data[:1]
    del state
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_native_legacy_positional_normalization_is_not_reinterpreted_as_dimensions():
    state=Statevector([0,2j],True)
    np.testing.assert_array_equal(state.data,[0,1j])
    assert state.dims()==(2,)


def test_integer_factory_dimensions_infer_binary_or_a_single_qudit():
    assert Statevector.from_int(2,4).dims()==(2,2)
    state=Statevector.from_int(5,6)
    assert state.dims()==(6,) and state.num_qubits is None
    np.testing.assert_array_equal(state.data,[0,0,0,0,0,1])


def complex_vector(dims):
    data=np.array([complex(index+1,(-1)**index*(index+.5)) for index in range(prod(dims))])
    return data/np.linalg.norm(data)


def make_state(cls,dims):
    vector=complex_vector(dims)
    return cls(vector if cls is Statevector else np.outer(vector,vector.conj()),dims=dims)


def reference_label(index,dims,selected):
    digits=np.unravel_index(index,dims) if dims else ()
    separator="|" if any(dims[position]>10 for position in selected) else ""
    return separator.join(str(digits[position]) for position in selected)


def reference_probabilities(vector,dims,selected):
    result={}
    for index,value in enumerate(vector):
        label=reference_label(index,dims,selected)
        result[label]=result.get(label,0)+abs(value)**2
    return result


def reference_reduction(matrix,dims,keep):
    keep=tuple(position for position in range(len(dims)) if position in keep)
    remaining=tuple(dims[position] for position in keep)
    output=np.zeros((prod(remaining),)*2,complex)
    for row,column in product(range(prod(dims)),repeat=2):
        r=np.unravel_index(row,dims) if dims else ()
        c=np.unravel_index(column,dims) if dims else ()
        if any(r[position]!=c[position] for position in range(len(dims)) if position not in keep):continue
        target_r=np.ravel_multi_index(tuple(r[position] for position in keep),remaining) if remaining else 0
        target_c=np.ravel_multi_index(tuple(c[position] for position in keep),remaining) if remaining else 0
        output[target_r,target_c]+=matrix[row,column]
    return output


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims", [(2,4),(3,2)])
@pytest.mark.parametrize("method", ["copy","conjugate","transpose","tensor","expand","evolve"])
def test_existing_numeric_operations_preserve_real_subsystem_structure(cls,dims,method):
    state=make_state(cls,dims)
    original=state.data.copy()
    other=cls.from_int(1,(3,))
    if method=="tensor":expected=np.kron(original,other.data);expected_dims=dims+(3,)
    elif method=="expand":expected=np.kron(other.data,original);expected_dims=(3,)+dims
    elif method=="conjugate":expected=original.conj();expected_dims=dims
    elif method=="transpose":expected=original if cls is Statevector else original.T;expected_dims=dims
    elif method=="evolve":
        matrix=np.diag(np.exp(1j*np.arange(prod(dims))*.27))
        expected=matrix@original if cls is Statevector else matrix@original@matrix.conj().T
        expected_dims=dims
    else:expected=original;expected_dims=dims
    ledger=Ledger()
    with ResourceScope(ledger):
        if method in {"tensor","expand"}:actual=getattr(state,method)(other)
        elif method=="evolve":actual=state.evolve(matrix)
        else:actual=getattr(state,method)()
    # Assert the independent numbers before dims: a metadata-only failure is real.
    np.testing.assert_allclose(actual.data,expected,atol=2e-15,rtol=0)
    assert actual.dims()==expected_dims
    np.testing.assert_array_equal(state.data,original)


@pytest.mark.parametrize("dims", [(2,4),(3,2),(2,3,2),(1,),()])
def test_state_density_conversion_and_eigenvector_retain_dimensions(dims):
    state=Statevector(complex_vector(dims),dims=dims)
    with ResourceScope(Ledger()):
        density=state.to_density_matrix()
        restored=density.to_statevector()
    np.testing.assert_allclose(density.data,np.outer(state.data,state.data.conj()),atol=1e-15)
    assert restored.equiv(state)
    assert density.dims()==restored.dims()==dims


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("selected", [(0,),(1,),(1,0),()])
def test_probabilities_and_samples_use_native_mixed_radix_digits(cls,selected):
    dims=(3,2)
    state=make_state(cls,dims)
    expected=reference_probabilities(complex_vector(dims),dims,selected)
    ledger=Ledger()
    with ResourceScope(ledger):
        probabilities=state.probabilities(selected)
        memory=state.sample_memory(19,qargs=selected,seed=11)
    assert type(probabilities) is dict
    assert probabilities==pytest.approx(expected,abs=2e-15)
    labels=sorted(expected)
    weights=np.array([expected[label] for label in labels]);weights/=weights.sum()
    draws=np.random.default_rng(11).choice(len(labels),19,p=weights)
    assert memory==[labels[index] for index in draws]
    assert ledger.receipt()["consumed_shots"]==19
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("selected", [(0,),(1,),(1,0),()])
def test_mixed_radix_projection_and_reset_follow_actual_native_quantum_rules(cls,selected):
    dims=(3,2)
    state=make_state(cls,dims)
    vector=complex_vector(dims)
    ledger=Ledger()
    with ResourceScope(ledger):
        outcome,collapsed=state.measure(selected,seed=7)
        reset=state.reset(selected,**({"seed":7} if cls is Statevector else {}))
    projected=vector.copy()
    for index in range(len(projected)):
        if reference_label(index,dims,selected)!=outcome:projected[index]=0
    projected/=np.linalg.norm(projected)
    expected=projected if cls is Statevector else np.outer(projected,projected.conj())
    np.testing.assert_allclose(collapsed.data,expected,atol=2e-15)
    assert collapsed.dims()==reset.dims()==dims
    if cls is Statevector:
        expected=np.zeros(prod(dims),complex)
        for index,value in enumerate(projected):
            digits=list(np.unravel_index(index,dims))
            for position in selected:digits[position]=0
            expected[np.ravel_multi_index(tuple(digits),dims)]+=value
    else:
        expected=np.zeros((prod(dims),)*2,complex)
        for row,column in product(range(prod(dims)),repeat=2):
            r=list(np.unravel_index(row,dims));c=list(np.unravel_index(column,dims))
            if any(r[position]!=c[position] for position in selected):continue
            for position in selected:r[position]=c[position]=0
            expected[np.ravel_multi_index(tuple(r),dims),np.ravel_multi_index(tuple(c),dims)]+=state.data[row,column]
    np.testing.assert_allclose(reset.data,expected,atol=2e-15)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims,keep", [((2,4),(0,)),((3,2),(1,)),((2,3,2),(2,0)),((3,2),()),((3,2),(1,0))])
def test_partial_trace_uses_real_subsystem_dimensions_and_preserves_native_keep_order(cls,dims,keep):
    state=make_state(cls,dims)
    matrix=np.outer(state.data,state.data.conj()) if cls is Statevector else state.data
    ledger=Ledger()
    with ResourceScope(ledger):reduced=state.partial_trace(keep)
    np.testing.assert_allclose(reduced.data,reference_reduction(matrix,dims,keep),atol=2e-15)
    assert reduced.dims()==tuple(dim for position,dim in enumerate(dims) if position in keep)
    assert reduced.trace()==pytest.approx(1.)
    assert np.linalg.eigvalsh(reduced.data).min()>-2e-15


@pytest.mark.parametrize("dims", [(2,4),(3,2)])
def test_native_end_to_end_composition_has_real_mixed_radix_reduction(dims):
    state=Statevector.from_int(1,dims).tensor(Statevector.from_label("+"))
    matrix=np.outer(state.data,state.data.conj())
    with ResourceScope(Ledger()):density=state.to_density_matrix().partial_trace([0,2])
    np.testing.assert_allclose(density.data,reference_reduction(matrix,dims+(2,),(0,2)),atol=1e-15)
    assert density.dims()==(dims[0],2)
    assert sum(density.probabilities().values())==pytest.approx(1.)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_large_qudit_digit_labels_are_unambiguous(cls):
    state=cls.from_int(21,(12,2))
    assert state.sample_memory(3,seed=2)==["10|1"]*3
    assert state.probabilities([1,0])["1|10"]==1


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("method", ["partial_trace","reset","reverse_qargs","evolve","measure"])
def test_mixed_radix_operations_deny_before_real_factory(cls,method,monkeypatch):
    state=make_state(cls,(3,2))
    matrix=np.eye(6,dtype=complex)
    def forbidden(*a,**k):pytest.fail("Mixed-radix buffer or quantum sampling preceded admission")
    for name in ("empty","array","trace","kron"):monkeypatch.setattr(np,name,forbidden)
    monkeypatch.setattr(np.random,"default_rng",forbidden)
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger),pytest.raises(MemoryError):
        if method=="partial_trace":state.partial_trace([0])
        elif method=="evolve":state.evolve(matrix)
        elif method=="reset":state.reset([0])
        else:getattr(state,method)()
    assert ledger.receipt()["live_memory_bytes"]==ledger.receipt()["consumed_shots"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_partial_trace_owned_output_survives_as_a_view_then_releases(cls):
    state=make_state(cls,(3,2))
    ledger=Ledger()
    with ResourceScope(ledger):reduced=state.partial_trace([0])
    amount=reduced.data.nbytes
    assert ledger.receipt()["live_memory_bytes"]==amount
    view=reduced.data[:,0]
    del reduced
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_mixed_radix_reverse_has_actual_permutation_and_reversed_dimensions(cls):
    dims=(3,2)
    state=make_state(cls,dims)
    order=[np.ravel_multi_index(np.unravel_index(index,dims)[::-1],dims[::-1]) for index in range(6)]
    expected=np.empty_like(state.data)
    if cls is Statevector:expected[order]=state.data
    else:expected[np.ix_(order,order)]=state.data
    with ResourceScope(Ledger()):reversed_state=state.reverse_qargs()
    assert reversed_state.dims()==(2,3)
    np.testing.assert_array_equal(reversed_state.data,expected)
    np.testing.assert_array_equal(reversed_state.reverse_qargs().data,state.data)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_unsupported_mixed_radix_circuit_does_not_dispatch_binary_kernels(cls,monkeypatch):
    from quantumbridge import Circuit
    from quantumbridge.core.classical import UnsupportedFeature
    state=make_state(cls,(2,4))
    def forbidden(*a,**k):pytest.fail("Unsupported mixed-radix operation reached binary machinery")
    monkeypatch.setattr(np,"empty",forbidden)
    with ResourceScope(Ledger()):
        with pytest.raises(UnsupportedFeature):state.evolve(Circuit(3).h(0))


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims", [(2,4),(3,2),(2,3,2)])
def test_optional_public_numeric_oracles_use_explicit_native_to_public_subsystem_mapping(cls,dims):
    info=pytest.importorskip("qiskit.quantum_info")
    native=make_state(cls,dims)
    public_cls=info.Statevector if cls is Statevector else info.DensityMatrix
    # Native q0 is the high radix; public qarg 0 is the low radix.
    public=public_cls(native.data,dims=dims[::-1])
    assert public.dims()==native.dims()[::-1]
    for selected in ((0,),(len(dims)-1,),tuple(reversed(range(len(dims))))):
        public_qargs=[len(dims)-1-position for position in reversed(selected)]
        probabilities=native.probabilities(selected)
        selected_dims=tuple(dims[position] for position in selected)
        labels=["".join(map(str,digits)) for digits in product(*(range(dim) for dim in selected_dims))]
        np.testing.assert_allclose([probabilities[label] for label in labels],public.probabilities(public_qargs),atol=2e-15)
    density=native.to_density_matrix() if cls is Statevector else native
    keep=(0,)
    expected=info.partial_trace(public,[len(dims)-1-position for position in range(len(dims)) if position not in keep])
    reduced=density.partial_trace(keep)
    np.testing.assert_allclose(reduced.data,expected.data,atol=2e-15)
    assert reduced.dims()==expected.dims()[::-1]


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("name", ["concurrence","mutual_information","negativity","schmidt_decomposition"])
def test_binary_analysis_does_not_silently_reinterpret_a_single_four_level_subsystem(cls,name):
    import quantumbridge.information as info
    from quantumbridge.core.classical import UnsupportedFeature
    state=cls.from_int(0,(4,))
    arguments=([0],) if name in {"negativity","schmidt_decomposition"} else ()
    with pytest.raises(UnsupportedFeature):getattr(info,name)(state,*arguments)


@pytest.mark.parametrize("dims", [(4,),(2,4)])
def test_direct_channel_entry_rejects_unimplemented_mixed_radix_metadata_mapping(dims):
    from quantumbridge.information import Kraus
    from quantumbridge.core.classical import UnsupportedFeature
    density=DensityMatrix.from_int(0,dims)
    channel=Kraus(np.eye(prod(dims),dtype=complex))
    with pytest.raises(UnsupportedFeature):channel.evolve(density)
