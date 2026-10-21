# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native tableau mathematics, admitted storage and non-dense large execution."""

import gc
from copy import deepcopy
from itertools import product

import numpy as np
import numpy.random
import pytest

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Clifford, StabilizerState, Operator, Statevector
from quantumbridge.operators import Pauli


@pytest.mark.parametrize("method", ["constructor","identity","copy","compose","adjoint","conjugate","tensor","array","labels","synthesis","generators","measure","samples","pauli_x","pauli_z"])
def test_tableau_factory_denied_before_allocation(method,monkeypatch):
    clifford=Clifford(Circuit(2).h(0).s(0).cx(0,1))
    state=StabilizerState(clifford)
    raw=clifford.tableau.copy()
    pauli=Pauli("XY")
    def forbidden(*a,**k):pytest.fail("Tableau buffer factory ran before admission")
    for name in ("empty","array","asarray","zeros","eye","arange","concatenate","column_stack"):
        monkeypatch.setattr(np,name,forbidden)
    def execute():
        if method=="constructor":return Clifford(raw)
        if method=="identity":return Clifford.identity(2)
        if method=="copy":return clifford.copy()
        if method=="compose":return clifford.compose(clifford)
        if method=="adjoint":return clifford.adjoint()
        if method=="conjugate":return clifford.conjugate()
        if method=="tensor":return clifford.tensor(clifford)
        if method=="array":return clifford.__array__()
        if method=="labels":return clifford.to_labels(array=True)
        if method=="synthesis":return clifford.to_circuit()
        if method=="generators":return StabilizerState.from_stabilizer_list(["XX","ZZ"])
        if method=="measure":return state.measure([0])
        if method=="samples":return state.sample_memory(3)
        return pauli.x if method=="pauli_x" else pauli.z
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger),pytest.raises(MemoryError):execute()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("qargs", [[True],[False],[.5],[-1],[2],[0,0]])
def test_invalid_tableau_qargs_reject(qargs):
    width=len(qargs)
    with pytest.raises(ValueError):Clifford.identity(2).compose(Clifford.identity(width),qargs=qargs)


@pytest.mark.parametrize("width", [True,False])
def test_boolean_is_not_a_clifford_width(width):
    with pytest.raises(ValueError):Clifford.identity(width)


@pytest.mark.parametrize("n", [1,2,3,4,5])
def test_composition_adjoint_conjugation_and_synthesis_have_full_complex_oracles(n):
    first=Circuit(n).h(0).s(0)
    second=Circuit(n).x(n-1).sdg(n-1)
    for wire in range(1,n):
        first.cx(wire-1,wire)
        second.h(wire).cz(0,wire)
    a,b=Operator.from_circuit(first).data,Operator.from_circuit(second).data
    ledger=Ledger()
    with ResourceScope(ledger):
        left,right=Clifford(first),Clifford(second)
        composed=left.compose(right)
        front=left.compose(right,front=True)
        inverse=left.adjoint()
        identity=left.compose(inverse)
        assert identity==inverse.compose(left)==Clifford.identity(n)
        assert composed.is_unitary() and inverse.is_unitary()
        np.testing.assert_array_equal(Clifford(composed.to_circuit()).tableau,composed.tableau)
        assert Operator(composed.to_matrix()).equiv(Operator(b@a))
        assert Operator(front.to_matrix()).equiv(Operator(a@b))
        assert Operator(inverse.to_matrix()).equiv(Operator(a.conj().T))
        assert Operator(left.conjugate().to_matrix()).equiv(Operator(a.conj()))
        for label in ("Y"*n,"-"+"X"*n,"i"+"Z"*n):
            pauli=Pauli(label)
            expected=a@pauli.to_matrix()@a.conj().T
            np.testing.assert_allclose(left.conjugate_pauli(pauli).to_matrix(),expected,atol=2e-13)
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes([value.tableau for value in (left,right,composed,front,inverse,identity)])


@pytest.mark.parametrize("front", [False,True])
def test_subsystem_composition_uses_correct_little_endian_qargs_and_phase(front):
    base=Clifford(Circuit(3).h(0).s(1).cx(0,2))
    small=Clifford(Circuit(2).h(0).s(0).cx(0,1))
    # Small qarg 0 is the low local bit; qargs [2,0] means native wires [2,0].
    embedded=Operator.from_circuit(Circuit(3).h(2).s(2).cx(2,0)).data
    matrix=base.to_matrix()
    ledger=Ledger()
    with ResourceScope(ledger):result=base.compose(small,qargs=[2,0],front=front)
    expected=matrix@embedded if front else embedded@matrix
    assert Operator(result.to_matrix()).equiv(Operator(expected))
    assert ledger.receipt()["live_memory_bytes"]==result.tableau.nbytes


def test_owned_tableau_copy_and_borrowed_views_follow_actual_last_root():
    ledger=Ledger()
    with ResourceScope(ledger):original=Clifford.from_label("HS")
    copied=original.copy()
    amount=original.tableau.nbytes
    assert ledger.receipt()["live_memory_bytes"]==2*amount
    shared=Clifford(copied,copy=False)
    view=shared.phase
    assert np.shares_memory(shared.tableau,copied.tableau)
    del original,copied,shared
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_tableau_copy_valid_overbudget_valid_on_same_ledger():
    amount=4*5
    ledger=Ledger(Limits(max_total_memory_bytes=2*amount))
    with ResourceScope(ledger):
        original=Clifford.identity(2)
        copied=original.copy()
        with pytest.raises(MemoryError):original.copy()
        del copied
        gc.collect()
        recovered=original.copy()
        assert recovered==original
    del original,recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_generator_completion_preserves_signed_stabilizers_and_pairing():
    ledger=Ledger()
    with ResourceScope(ledger):
        state=StabilizerState.from_stabilizer_list(["-ZZ","XX","YY"],allow_redundant=True)
        partial=StabilizerState.from_stabilizer_list(["-ZZ"],allow_underconstrained=True)
        assert state.is_valid() and partial.is_valid()
        assert state.expectation_value(Pauli("-ZZ"))==state.expectation_value(Pauli("XX"))==1
        generators=[state.clifford._row_pauli(row) for row in range(4)]
        for i,j in product(range(4),repeat=2):
            expected=not (i%2==j%2 and i//2!=j//2)
            assert generators[i].commutes(generators[j])==expected
    assert ledger.receipt()["live_memory_bytes"]==state.clifford.tableau.nbytes+partial.clifford.tableau.nbytes


def test_failed_nonsymplectic_constructor_does_not_retain_storage_and_recovers():
    ledger=Ledger()
    with ResourceScope(ledger),pytest.raises(ValueError):Clifford([[1,0,0],[1,0,0]])
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(ledger):valid=Clifford.from_label("H")
    assert valid.is_unitary()


@pytest.mark.parametrize("shape", [(0,0),(0,1)])
@pytest.mark.parametrize("dtype", [np.complex64,np.complex128])
@pytest.mark.parametrize("subclass", [False,True])
def test_empty_complex_matrix_is_not_a_zero_qubit_boolean_tableau(shape,dtype,subclass):
    class ExplicitBuffer(np.ndarray):
        def __array__(self,*args,**kwargs):
            pytest.fail("Managed validation dispatched a foreign array protocol")
    value=np.empty(shape,dtype=dtype)
    if subclass:value=value.view(ExplicitBuffer)
    with pytest.raises(ValueError):Clifford(value)
    ledger=Ledger()
    with ResourceScope(ledger),pytest.raises(ValueError):Clifford(value)
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("shape", [(0,0),(0,1)])
def test_empty_boolean_tableau_remains_valid(shape):
    ledger=Ledger()
    with ResourceScope(ledger):result=Clifford(np.empty(shape,dtype=bool))
    assert result.num_qubits==0 and result.is_unitary()
    assert result.tableau.shape==(0,1)
    assert ledger.receipt()["live_memory_bytes"]==0


def test_large_clifford_matrix_rejects_before_synthesis(monkeypatch):
    clifford=Clifford.identity(100)
    monkeypatch.setattr(Clifford,"to_circuit",lambda *a:pytest.fail("Dense output admission came after synthesis"))
    with ResourceScope(Ledger()),pytest.raises(MemoryError):clifford.to_matrix()


def test_existing_large_stabilizer_statevector_preflight_is_preserved(monkeypatch):
    state=StabilizerState(Clifford.identity(100))
    monkeypatch.setattr(Statevector,"from_circuit",lambda *a:pytest.fail("Exponential state factory entered"))
    with ResourceScope(Ledger()),pytest.raises(MemoryError):state.to_statevector()


def test_one_hundred_qubit_tableau_executes_without_dense_fallback(monkeypatch):
    for cls,name in ((Clifford,"to_matrix"),(Operator,"from_circuit"),(Statevector,"from_circuit")):
        monkeypatch.setattr(cls,name,lambda *a,**k:pytest.fail("Dense fallback in 100-qubit tableau"))
    circuit=Circuit(100).h(0)
    for wire in range(1,100):circuit.cx(wire-1,wire)
    ledger=Ledger(Limits(max_total_memory_bytes=16*1024*1024))
    with ResourceScope(ledger):
        clifford=Clifford(circuit)
        inverse=clifford.adjoint()
        assert clifford.compose(inverse)==Clifford.identity(100)
        assert inverse.compose(clifford)==Clifford.identity(100)
        state=StabilizerState(clifford)
        assert state.expectation_value(Pauli("X"*100))==1
        state.seed(11)
        outcome,collapsed=state.measure([0,99])
        assert outcome in {"00","11"}
        assert collapsed.expectation_value(Pauli("Z"+"I"*99)) in {-1,1}
        samples=state.sample_memory(3,qargs=[0,99])
        assert set(samples)<= {"00","11"}
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes((clifford.tableau,inverse.tableau,state.clifford.tableau,collapsed.clifford.tableau,samples))


@pytest.mark.parametrize("factory", [lambda c:c,StabilizerState])
def test_tableau_default_deepcopy_is_admitted_and_shared_memo_is_preserved(factory):
    source=factory(Clifford.from_label("HS"))
    tableau=source.tableau if type(source) is Clifford else source.clifford.tableau
    ledger=Ledger()
    with ResourceScope(ledger):first,second,raw=deepcopy([source,source,tableau])
    assert first is second
    copied=first.tableau if type(first) is Clifford else first.clifford.tableau
    assert raw is copied and not np.shares_memory(copied,tableau)
    assert ledger.receipt()["live_memory_bytes"]==tableau.nbytes


def test_stabilizer_sampler_charges_completed_trajectories_and_recovers(monkeypatch):
    state=StabilizerState(Circuit(2).h(0).cx(0,1))
    state.seed(7)
    ledger=Ledger(Limits(max_total_shots=4))
    with ResourceScope(ledger):
        memory=state.sample_memory(3)
        with monkeypatch.context() as patch:
            patch.setattr(StabilizerState,"copy",lambda *a:pytest.fail("Sampling dispatched beyond shot budget"))
            with pytest.raises(MemoryError):state.sample_memory(2)
        assert state.sample_memory(1).size==1
    assert ledger.receipt()["consumed_shots"]==4
    assert ledger.receipt()["reserved_shots"]==0
    del memory
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_stabilizer_label_factory_failure_preserves_completed_shots(monkeypatch):
    from quantumbridge.information import stabilizer_state as module
    state=StabilizerState(Clifford.from_label("H"))
    ledger=Ledger()
    def failed(*a,**k):raise MemoryError("injected label output failure")
    with monkeypatch.context() as patch:
        patch.setattr(module,"_label_array",failed)
        with ResourceScope(ledger),pytest.raises(MemoryError):state.sample_memory(3)
    gc.collect()
    assert ledger.receipt()["consumed_shots"]==3
    assert ledger.receipt()["reserved_shots"]==ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("label", ["H","S","HS","SHY"])
def test_optional_public_qiskit_tableau_compose_inverse_and_phase_oracles(label):
    quantum_info=pytest.importorskip("qiskit.quantum_info")
    expected=quantum_info.Clifford.from_label(label)
    ledger=Ledger()
    with ResourceScope(ledger):
        actual=Clifford.from_label(label)
        np.testing.assert_array_equal(actual.tableau,expected.tableau)
        np.testing.assert_array_equal(actual.adjoint().tableau,expected.adjoint().tableau)
        np.testing.assert_array_equal(actual.compose(actual).tableau,expected.compose(expected).tableau)
        for word in ("-"+"Y"*len(label),"i"+"X"*len(label)):
            expected_pauli=quantum_info.Pauli(word).evolve(expected,frame="s")
            assert actual.conjugate_pauli(Pauli(word)).to_label()==expected_pauli.to_label()


@pytest.mark.parametrize("dynamic", [False,True])
def test_audited_direct_dense_device_output_has_actual_storage_owner(dynamic):
    circuit=Circuit(2,1).h(0).cx(0,1)
    if dynamic:circuit.measure(0,0).z(1)
    expected=np.diag([.5,0,0,.5]).astype(complex)
    if not dynamic:expected[0,3]=expected[3,0]=.5
    ledger=Ledger()
    with ResourceScope(ledger):result=StatevectorDevice().density_matrix(circuit)
    np.testing.assert_allclose(result,expected,atol=1e-15)
    assert np.trace(result)==pytest.approx(1)
    assert np.linalg.eigvalsh(result).min()>-1e-15
    assert ledger.receipt()["live_memory_bytes"]==result.nbytes
    escaped=result[:1]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==expected.nbytes
    del escaped
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_direct_dense_output_rejects_before_outer_product_or_state_build(monkeypatch):
    monkeypatch.setattr(np,"outer",lambda *a,**k:pytest.fail("Unadmitted dense device outer product"))
    ledger=Ledger(Limits(max_total_memory_bytes=255))
    with ResourceScope(ledger),pytest.raises(MemoryError):StatevectorDevice().density_matrix(Circuit(2))
    assert ledger.receipt()["live_memory_bytes"]==0


def test_direct_density_second_access_exceeds_budget_then_recovers():
    ledger=Ledger(Limits(max_total_memory_bytes=128))
    device=StatevectorDevice()
    with ResourceScope(ledger):
        first=device.density_matrix(Circuit(1))
        with pytest.raises(MemoryError):device.density_matrix(Circuit(1))
        del first
        gc.collect()
        recovered=device.density_matrix(Circuit(1))
    np.testing.assert_array_equal(recovered,[[1,0],[0,0]])
    assert ledger.receipt()["live_memory_bytes"]==recovered.nbytes


@pytest.mark.parametrize("kind", ["symplectic_only","integer","list","complex_matrix","operator","dict"])
def test_scoped_tableau_input_forms_preserve_generators_and_independent_storage(kind):
    original=Clifford.from_label("HS")
    if kind=="symplectic_only":raw=original.symplectic_matrix
    elif kind=="integer":raw=original.tableau.astype(np.int8)
    elif kind=="list":raw=original.tableau.tolist()
    elif kind=="complex_matrix":raw=original.to_matrix()
    elif kind=="operator":raw=original.to_operator()
    else:raw=original.to_dict()
    ledger=Ledger()
    with ResourceScope(ledger):actual=Clifford(raw)
    assert actual==original
    assert not np.shares_memory(actual.tableau,original.tableau)
    assert ledger.receipt()["live_memory_bytes"]==actual.tableau.nbytes


def test_gf2_solve_and_nullspace_use_correct_binary_arithmetic():
    from quantumbridge.information.clifford import _gf2_solve,_gf2_basis
    from quantumbridge.information.stabilizer_state import _nullspace
    matrix=np.array([[1,1,0,1],[0,1,1,0]],bool)
    target=np.array([1,0],bool)
    ledger=Ledger()
    with ResourceScope(ledger):
        solution=_gf2_solve(matrix,target)
        kernel=_nullspace(matrix)
        basis=_gf2_basis(matrix)
    np.testing.assert_array_equal(matrix.astype(int)@solution.astype(int)%2,target)
    np.testing.assert_array_equal(matrix.astype(int)@kernel.astype(int).T%2,np.zeros((2,2),int))
    assert len(basis)==2 and len(kernel)==2
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes((solution,kernel,basis))
    del solution,kernel,basis
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(ledger),pytest.raises(ValueError):_gf2_solve([[0,0]],[1])
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_matrix_input_and_array_dtype_exports_are_controlled_without_aliasing():
    source=Clifford.from_label("S")
    ledger=Ledger()
    with ResourceScope(ledger):
        converted=Clifford.from_operator(Operator(source.to_matrix()))
        pauli=Clifford.from_operator(Pauli("Y"))
        integer=converted.__array__(dtype=np.int32)
    assert converted==source and pauli==Clifford.from_label("Y")
    np.testing.assert_array_equal(integer,source.tableau)
    assert integer.dtype==np.dtype(np.int32)
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes((converted.tableau,pauli.tableau,integer))


def test_empty_tableau_exports_keep_zero_qubit_mathematics():
    ledger=Ledger()
    with ResourceScope(ledger):
        empty=Clifford.identity(0)
        labels=empty.to_labels(array=True)
        matrix=empty.to_matrix()
        vector=StabilizerState(empty).to_statevector().data
    assert labels.shape==(0,) and labels.dtype==np.dtype(float)
    np.testing.assert_array_equal(matrix,[[1]])
    np.testing.assert_array_equal(vector,[1])
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes((empty.tableau,labels,matrix,vector))


def test_unmanaged_array_protocol_is_preserved_but_managed_foreign_factory_rejects():
    from quantumbridge.core.classical import UnsupportedFeature
    class ArrayLike:
        calls=0
        def __array__(self,dtype=None,copy=None):
            self.calls+=1
            return np.asarray([[0,-1j],[1j,0]],dtype=dtype)
    supplied=ArrayLike()
    assert Clifford.from_matrix(supplied)==Clifford.from_label("Y")
    assert supplied.calls==1
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):Clifford.from_matrix(supplied)
    assert supplied.calls==1
