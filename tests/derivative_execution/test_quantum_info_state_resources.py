# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual native state APIs, numerical semantics and preallocation contracts."""

import gc

import numpy as np
import numpy.random
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Statevector


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("method", ["copy", "conjugate", "tensor", "expand", "measure", "sample_memory", "sample_counts", "reverse_qargs"])
def test_state_api_rejects_budget_before_real_factory(cls, method, monkeypatch):
    vector=np.array([1,1j],complex)/np.sqrt(2)
    state=cls(vector) if cls is Statevector else cls(np.outer(vector,vector.conj()))
    arguments=(state,) if method in {"tensor","expand"} else (5,) if method.startswith("sample") else ()
    def forbidden(*a, **k):pytest.fail("State allocated before admission")
    for name in ("array","empty","zeros","zeros_like","kron","conjugate"):
        monkeypatch.setattr(np,name,forbidden)
    monkeypatch.setattr(np.random,"default_rng",forbidden)
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger),pytest.raises(MemoryError):getattr(state,method)(*arguments)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_density_outer_product_rejects_before_conversion_or_conjugate(monkeypatch):
    vector=np.array([1,1j],np.complex64)
    def forbidden(*a, **k):pytest.fail("Density outer product preceded admission")
    for name in ("asarray","outer","conjugate","empty"):monkeypatch.setattr(np,name,forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))),pytest.raises(MemoryError):
        DensityMatrix.from_statevector(vector)


@pytest.mark.parametrize("factory,args", [(Statevector.from_int,(0,4)),(Statevector.from_label,("01",))])
def test_state_factory_rejects_before_zero_array(factory,args,monkeypatch):
    for name in ("zeros","empty"):
        monkeypatch.setattr(np,name,lambda *a, **k: pytest.fail("State factory preceded admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))),pytest.raises(MemoryError):factory(*args)


@pytest.mark.parametrize("label", ["+","-","r","l","+1","rl",""])
def test_pauli_eigenstate_labels_have_actual_native_amplitudes(label):
    coefficients={"0":[1,0],"1":[0,1],"+":[1,1],"-":[1,-1],"r":[1,1j],"l":[1,-1j]}
    expected=np.array([1],complex)
    for symbol in label:
        factor=np.array(coefficients[symbol],complex)
        if symbol not in "01":factor/=np.sqrt(2)
        expected=np.kron(expected,factor)
    ledger=Ledger()
    with ResourceScope(ledger):actual=Statevector.from_label(label)
    np.testing.assert_allclose(actual.data,expected,atol=3e-16)
    assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("qargs", [None,[],[0],[1],[1,0]])
def test_native_reset_is_a_new_state_with_zeroed_selected_qubits(qargs):
    vector=np.array([1,0,0,1j],complex)/np.sqrt(2)
    state=Statevector(vector)
    ledger=Ledger()
    with ResourceScope(ledger):actual=state.reset(qargs=qargs,seed=7)
    selected=tuple(range(2) if qargs is None else qargs)
    if not selected:np.testing.assert_allclose(actual.data,vector,atol=2e-16)
    elif qargs is None:np.testing.assert_array_equal(actual.data,[1,0,0,0])
    elif len(selected)==2:np.testing.assert_array_equal(actual.data,[1j,0,0,0])
    else:
        probabilities=actual.probabilities(selected)
        assert probabilities["0"] == pytest.approx(1.)
        assert actual.is_valid()
    np.testing.assert_array_equal(state.data,vector)
    assert not np.shares_memory(actual.data,vector)
    assert ledger.receipt()["consumed_shots"] == (1 if qargs is not None and selected else 0)
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_owned_state_copy_outside_scope_keeps_source_account_and_escaped_view(cls):
    ledger=Ledger()
    with ResourceScope(ledger):original=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    amount=original.data.nbytes
    copied=original.copy()
    assert ledger.receipt()["live_memory_bytes"] == 2*amount
    view=copied.data[:1]
    del original,copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_complete_sampling_buffer_group_denied_before_first_factory(cls,monkeypatch):
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    # Two float probability/CDF buffers, uniforms and intp outcome buffers.
    amount=2*2*8+5*(8+np.dtype(np.intp).itemsize)
    monkeypatch.setattr(np,"empty",lambda *a, **k: pytest.fail("Partial sampling workspace allocation"))
    monkeypatch.setattr(np,"array",lambda *a, **k: pytest.fail("Partial sampling workspace conversion"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=amount-1))),pytest.raises(MemoryError):state.sample_memory(5,seed=3)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("qargs", [[0],[2,0],[]])
def test_samples_match_numpy_categorical_draws_and_do_not_modify_state(cls,qargs):
    vector=np.array([1,.2j,.3,-.4j,.5j,.6,.7j,-.8],complex);vector/=np.linalg.norm(vector)
    state=cls(vector) if cls is Statevector else cls(np.outer(vector,vector.conj()))
    before=state.data.copy()
    probabilities=state.probabilities(qargs)
    labels=sorted(probabilities)
    weights=np.array([probabilities[label] for label in labels]);weights/=weights.sum()
    expected=[labels[index] for index in np.random.default_rng(12).choice(len(labels),size=23,p=weights)]
    ledger=Ledger()
    with ResourceScope(ledger):
        actual=state.sample_memory(23,qargs=qargs,seed=12)
        counts=state.sample_counts(23,qargs=qargs,seed=12)
    assert actual == expected
    assert counts == {label:expected.count(label) for label in labels if label in expected}
    np.testing.assert_array_equal(state.data,before)
    assert ledger.receipt()["consumed_shots"] == 46
    assert ledger.receipt()["reserved_shots"] == ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_cumulative_sampling_shots_reject_before_rng_then_recover(cls,monkeypatch):
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    ledger=Ledger(Limits(max_total_shots=5))
    with ResourceScope(ledger):
        state.sample_memory(3,seed=5)
        with monkeypatch.context() as patch:
            patch.setattr(np.random,"default_rng",lambda *a, **k: pytest.fail("Shot cap ignored"))
            with pytest.raises(MemoryError):state.sample_memory(3,seed=5)
        assert state.sample_memory(2,seed=5) == ["0","0"]
    assert ledger.receipt()["consumed_shots"] == 5


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_postprocessing_failure_does_not_refund_completed_samples(cls,monkeypatch):
    from quantumbridge.information import statevector as module
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    ledger=Ledger()
    def failure(*a, **k):raise MemoryError("injected sample formatting failure")
    with monkeypatch.context() as patch:
        patch.setattr(module,"_memory_from_indices",failure,raising=False)
        with ResourceScope(ledger),pytest.raises(MemoryError):state.sample_memory(5,seed=2)
    assert ledger.receipt()["consumed_shots"] == 5
    assert ledger.receipt()["reserved_shots"] == 0
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("method", ["tensor","expand","copy","conjugate","reverse_qargs","adjoint"])
def test_complex_strided_state_operations_match_independent_numpy(cls,method):
    vector=np.array([1,2j,-3j,4],complex)[::-1];vector/=np.linalg.norm(vector)
    data=vector if cls is Statevector else np.outer(vector,vector.conj())[::-1,::-1]
    first,second=cls(data),cls(data[::-1] if cls is Statevector else data[::-1,::-1])
    before=first.data.copy()
    if method=="tensor":expected=np.kron(first.data,second.data)
    elif method=="expand":expected=np.kron(second.data,first.data)
    elif method=="copy":expected=first.data.copy()
    elif method=="conjugate":expected=first.data.conj()
    elif method=="adjoint":expected=first.data.conj().reshape(1,-1) if cls is Statevector else first.data.conj().T
    else:
        indices=[int(format(index,"02b")[::-1],2) for index in range(4)]
        expected=first.data[indices] if cls is Statevector else first.data[np.ix_(indices,indices)]
    ledger=Ledger()
    with ResourceScope(ledger):
        actual=getattr(first,method)(second) if method in {"tensor","expand"} else getattr(first,method)()
    array=actual if type(actual) is np.ndarray else actual.data
    np.testing.assert_allclose(array,expected,atol=1e-15)
    np.testing.assert_array_equal(first.data,before)
    assert not np.shares_memory(array,first.data)
    assert ledger.receipt()["live_memory_bytes"] == array.nbytes
    del array,actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("qargs", [[0],[1],[],[1,0]])
def test_measurement_matches_projection_with_correct_phase_trace_and_psd(cls,qargs):
    vector=np.array([1,2j,-3,4j],complex);vector/=np.linalg.norm(vector)
    state=cls(vector) if cls is Statevector else cls(np.outer(vector,vector.conj()))
    original=state.data.copy()
    ledger=Ledger()
    with ResourceScope(ledger):outcome,collapsed=state.measure(qargs=qargs,seed=11)
    mask=np.array(["".join(format(index,"02b")[wire] for wire in qargs)==outcome for index in range(4)])
    projected=vector*mask;projected/=np.linalg.norm(projected)
    expected=projected if cls is Statevector else np.outer(projected,projected.conj())
    np.testing.assert_allclose(collapsed.data,expected,atol=2e-15)
    np.testing.assert_array_equal(state.data,original)
    if cls is DensityMatrix:
        np.testing.assert_allclose(collapsed.trace(),1,atol=1e-15)
        assert np.linalg.eigvalsh(collapsed.data).min()>-1e-15
    else:assert np.linalg.norm(collapsed.data)==pytest.approx(1.)
    assert ledger.receipt()["consumed_shots"] == 1
    assert ledger.receipt()["live_memory_bytes"] == collapsed.data.nbytes


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_state_copy_memory_overbudget_then_valid_recovery(cls):
    data=np.array([1,1j],complex)/np.sqrt(2)
    if cls is DensityMatrix:data=np.outer(data,data.conj())
    ledger=Ledger(Limits(max_total_memory_bytes=2*data.nbytes))
    with ResourceScope(ledger):
        source=cls(data.tolist())
        first=source.copy()
        assert ledger.receipt()["live_memory_bytes"] == 2*data.nbytes
        with pytest.raises(MemoryError):source.copy()
        del first
        gc.collect()
        second=source.copy()
        np.testing.assert_array_equal(second.data,data)
    del source,second
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("shots", [-1,True,1.5])
def test_invalid_shots_reject_before_rng_in_and_outside_scope(cls,shots,monkeypatch):
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    monkeypatch.setattr(np.random,"default_rng",lambda *a,**k:pytest.fail("Invalid sampling dispatched"))
    with pytest.raises(ValueError):state.sample_memory(shots)
    ledger=Ledger()
    with ResourceScope(ledger),pytest.raises(ValueError):state.sample_memory(shots)
    assert ledger.receipt()["consumed_shots"] == ledger.receipt()["reserved_shots"] == 0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_zero_shots_needs_no_sampling_arrays_or_rng(cls,monkeypatch):
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    monkeypatch.setattr(np.random,"default_rng",lambda *a,**k:pytest.fail("Zero-shot RNG dispatched"))
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Zero-shot numeric allocation"))
    ledger=Ledger(Limits(max_total_memory_bytes=0,max_total_shots=0))
    with ResourceScope(ledger):
        assert state.sample_memory(0) == []
        assert state.sample_counts(0) == {}
    assert ledger.receipt()["consumed_shots"] == ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("dtype", [np.complex64,np.complex128])
def test_density_construction_from_strided_vector_preserves_trace_psd_and_leases(dtype):
    vector=np.array([1,2j,-3,4j],dtype=dtype)[::-1]
    vector/=np.linalg.norm(vector)
    expected=np.outer(vector.astype(complex),vector.astype(complex).conj())
    ledger=Ledger()
    with ResourceScope(ledger):actual=DensityMatrix.from_statevector(vector)
    np.testing.assert_allclose(actual.data,expected,atol=1e-15)
    assert actual.data.dtype==np.dtype(complex)
    assert np.linalg.eigvalsh(actual.data).min()>-1e-15
    assert actual.trace()==pytest.approx(1.,abs=2e-7)
    assert ledger.receipt()["live_memory_bytes"]==actual.data.nbytes
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("qargs", [[0,0],[2],[0.5],[True]])
def test_invalid_sample_qargs_reject_before_rng_and_do_not_spend_shots(cls,qargs,monkeypatch):
    state=cls([1,0]) if cls is Statevector else cls([[1,0],[0,0]])
    monkeypatch.setattr(np.random,"default_rng",lambda *a,**k:pytest.fail("Invalid qargs dispatched"))
    ledger=Ledger()
    with ResourceScope(ledger),pytest.raises(ValueError):state.sample_memory(5,qargs=qargs)
    assert ledger.receipt()["consumed_shots"]==ledger.receipt()["reserved_shots"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("invalid", [0,float("nan"),float("inf")])
def test_invalid_distribution_rejects_before_rng(cls,invalid,monkeypatch):
    state=cls([invalid,0]) if cls is Statevector else cls([[invalid,0],[0,0]])
    monkeypatch.setattr(np.random,"default_rng",lambda *a,**k:pytest.fail("Invalid distribution dispatched"))
    ledger=Ledger()
    with ResourceScope(ledger),pytest.raises(ValueError):state.sample_memory(3,seed=8)
    assert ledger.receipt()["consumed_shots"]==ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("label", ["+","-","r","l","+1","rl"])
def test_optional_public_qiskit_eigenstate_oracle(label):
    quantum_info=pytest.importorskip("qiskit.quantum_info")
    expected=quantum_info.Statevector.from_label(label).data
    ledger=Ledger()
    with ResourceScope(ledger):actual=Statevector.from_label(label)
    np.testing.assert_allclose(actual.data,expected,atol=3e-16)


@pytest.mark.parametrize("qargs", [None,[],[0],[1],[1,0]])
def test_optional_public_qiskit_reset_oracle_with_explicit_wire_conversion(qargs):
    quantum_info=pytest.importorskip("qiskit.quantum_info")
    vector=np.array([1,2j,-3,4j],complex);vector/=np.linalg.norm(vector)
    oracle=quantum_info.Statevector(vector)
    oracle.seed(7)
    # Native wire zero is the leftmost bit; Qiskit subsystem zero is rightmost.
    mapped=None if qargs is None else [1-wire for wire in reversed(qargs)]
    expected=oracle.reset(mapped).data
    ledger=Ledger()
    with ResourceScope(ledger):actual=Statevector(vector).reset(qargs=qargs,seed=7)
    np.testing.assert_allclose(actual.data,expected,atol=2e-15)
