# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native global-phase comparisons and shared-memo operator/channel copying."""

from copy import deepcopy
import copy
import gc

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator, Kraus, SuperOp, Choi, PTM, Chi, Stinespring


@pytest.mark.parametrize("phase", [.3,1.7,-2.3])
def test_phase_equivalence_uses_stable_pivot_not_first_tiny_entry(phase):
    reference=np.diag([2e-10,1.]).astype(complex)
    candidate=np.exp(1j*phase)*reference
    candidate[0,0]*=.8
    np.testing.assert_allclose(candidate,np.exp(1j*phase)*reference,atol=1e-10,rtol=0)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))):
        assert Operator(candidate).equiv(Operator(reference),atol=1e-10)


@pytest.mark.parametrize("invalid", [float("inf"),float("nan")])
def test_nonfinite_operator_is_not_phase_equivalent(invalid):
    matrix=np.diag([invalid,1.]).astype(complex)
    assert not Operator(matrix).equiv(Operator(matrix))


@pytest.mark.parametrize("factory", [Operator,Kraus,SuperOp,Choi,PTM,Chi,Stinespring])
def test_deepcopy_rejects_before_numpy_deepcopy_dispatch(factory,monkeypatch):
    source=Operator(np.array([[0,1j],[-1j,0]],complex))
    value=source if factory is Operator else factory(source)
    def forbidden(*a,**k):pytest.fail("ndarray deepcopy dispatched before admission")
    monkeypatch.setitem(copy._deepcopy_dispatch,np.ndarray,forbidden)
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger),pytest.raises(MemoryError):deepcopy(value)
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("factory", [Operator,Kraus,SuperOp,Choi,PTM,Chi,Stinespring])
def test_channel_copy_keeps_shared_memo_and_independent_roots(factory):
    source=Operator(np.array([[0,1j],[-1j,0]],complex))
    original=source if factory is Operator else factory(source)
    expected=source.data.copy() if factory is Operator else original.to_superop().data.copy()
    ledger=Ledger()
    with ResourceScope(ledger):
        copies=deepcopy([original,original])
    assert copies[0] is copies[1]
    actual=copies[0].data if factory is Operator else copies[0].to_superop().data
    np.testing.assert_allclose(actual,expected,atol=1e-14)
    amount=native_storage_bytes(vars(copies[0]))
    assert ledger.receipt()["live_memory_bytes"]==amount>0
    if factory is Kraus:assert copies[0]._left is copies[0]._right is copies[0].data
    if factory is Stinespring:assert copies[0]._left_data is copies[0]._right_data is copies[0].data
    arrays=copies[0].data if type(copies[0].data) is tuple else (copies[0].data,)
    view=arrays[0][:1]
    retained=native_storage_bytes(view)
    del copies,arrays,actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==retained
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_operator_copy_outside_scope_follows_source_ledger_and_recovers():
    ledger=Ledger(Limits(max_total_memory_bytes=128))
    with ResourceScope(ledger):source=Operator([[0,1j],[-1j,0]])
    copied=deepcopy(source)
    assert ledger.receipt()["live_memory_bytes"]==128
    with pytest.raises(MemoryError):deepcopy(source)
    del copied
    gc.collect()
    recovered=deepcopy(source)
    np.testing.assert_array_equal(recovered.data,source.data)
    del source,recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("factory", [Operator,Kraus,SuperOp,Choi,PTM,Chi,Stinespring])
def test_foreign_nested_copy_protocol_rejects_before_dispatch(factory):
    class Foreign:
        def __deepcopy__(self,memo):pytest.fail("Foreign native-object copy hook dispatched")
    source=Operator(np.eye(2,dtype=complex))
    value=source if factory is Operator else factory(source)
    value.data=Foreign()
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):deepcopy(value)


def test_generalized_kraus_deepcopy_keeps_both_map_sides_and_cptp_semantics():
    left=(np.array([[1,0],[0,.8]],complex),np.array([[0,.6],[0,0]],complex))
    right=(left[0]*1j,left[1]*-.5j)
    channel=Kraus((left,right))
    expected=channel.to_superop().data.copy()
    ledger=Ledger()
    with ResourceScope(ledger):copied=deepcopy(channel)
    assert copied._left is not copied._right
    assert copied.data[0] is copied._left and copied.data[1] is copied._right
    np.testing.assert_allclose(copied.to_superop().data,expected,atol=1e-15)
    assert not copied.is_cptp()
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes(vars(copied))


@pytest.mark.parametrize("kind", ["label","reverse","add","subtract","multiply","divide","radd","rsub","rmatmul"])
def test_operator_outputs_denied_before_named_factory(kind,monkeypatch):
    matrix=np.array([[0,1j],[-1j,0]],complex)
    operator=Operator(matrix)
    def forbidden(*a,**k):pytest.fail("Operator output factory preceded admission")
    for name in ("empty","zeros","array","kron","add","subtract","multiply","divide"):
        monkeypatch.setattr(np,name,forbidden)
    def execute():
        if kind=="label":return Operator.from_label("XY")
        if kind=="reverse":return operator.reverse_qargs()
        if kind=="add":return operator+operator
        if kind=="subtract":return operator-operator
        if kind=="multiply":return operator*2
        if kind=="divide":return operator/2
        if kind=="radd":return matrix+operator
        if kind=="rsub":return matrix-operator
        return matrix@operator
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger),pytest.raises(MemoryError):execute()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("label", ["","I","Y","XYIZ","zy"])
def test_native_operator_labels_have_exact_pauli_tensor_order_and_retained_storage(label):
    factors={"I":np.eye(2),"X":np.array([[0,1],[1,0]]),
        "Y":np.array([[0,-1j],[1j,0]]),"Z":np.diag([1,-1])}
    expected=np.array([[1]],complex)
    for symbol in label.upper():expected=np.kron(expected,factors[symbol])
    ledger=Ledger()
    with ResourceScope(ledger):actual=Operator.from_label(label)
    np.testing.assert_array_equal(actual.data,expected)
    assert ledger.receipt()["live_memory_bytes"]==actual.data.nbytes
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("kind", ["add","subtract","multiply","divide","radd","rsub","rmatmul","reverse"])
def test_operator_arithmetic_complex_strided_values_and_output_ownership(kind):
    matrix=np.arange(16,dtype=float).reshape(4,4).astype(complex)
    matrix=(matrix+1j*matrix.T)[::-1,::-1]
    other=matrix.T[::-1]
    operator=Operator(matrix)
    before=matrix.copy()
    if kind in {"add","radd"}:expected=matrix+other
    elif kind=="subtract":expected=matrix-other
    elif kind=="rsub":expected=other-matrix
    elif kind=="multiply":expected=matrix*(.3+1.2j)
    elif kind=="divide":expected=matrix/(.3+1.2j)
    elif kind=="rmatmul":expected=other@matrix
    else:expected=matrix[np.ix_([0,2,1,3],[0,2,1,3])]
    ledger=Ledger()
    with ResourceScope(ledger):
        if kind=="add":actual=operator+other
        elif kind=="subtract":actual=operator-other
        elif kind=="radd":actual=other+operator
        elif kind=="rsub":actual=other-operator
        elif kind=="multiply":actual=operator*(.3+1.2j)
        elif kind=="divide":actual=operator/(.3+1.2j)
        elif kind=="rmatmul":actual=other@operator
        else:actual=operator.reverse_qargs()
    np.testing.assert_allclose(actual.data,expected,atol=1e-13)
    np.testing.assert_array_equal(matrix,before)
    assert not np.shares_memory(actual.data,matrix)
    assert ledger.receipt()["live_memory_bytes"]==actual.data.nbytes


@pytest.mark.parametrize("phase", [.2,1.3,-2.1])
def test_optional_public_qiskit_operator_global_phase_oracle(phase):
    quantum_info=pytest.importorskip("qiskit.quantum_info")
    reference=np.array([[1,2j],[-3j,4]],complex)[:,::-1]
    candidate=np.exp(1j*phase)*reference
    expected=quantum_info.Operator(reference).equiv(quantum_info.Operator(candidate))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))):
        assert Operator(reference).equiv(Operator(candidate))==expected
        assert not Operator(reference).equiv(Operator(candidate+np.eye(2)*.1))


@pytest.mark.parametrize("kind", ["tensor","expand","power"])
def test_previously_controlled_operator_products_remain_correct(kind):
    first=np.array([[0,1j],[-1j,0]],complex)
    second=np.diag([1,-1j])
    expected=np.kron(first,second) if kind=="tensor" else np.kron(second,first) if kind=="expand" else np.linalg.matrix_power(first,3)
    ledger=Ledger()
    with ResourceScope(ledger):
        operator=Operator(first)
        actual=operator.power(3) if kind=="power" else getattr(operator,kind)(Operator(second))
    np.testing.assert_allclose(actual.data,expected,atol=1e-15)
    assert ledger.receipt()["live_memory_bytes"]==actual.data.nbytes


def test_caller_memo_alias_to_operator_array_is_reused_without_another_copy():
    original=Operator(np.array([[1,2j],[-3j,4]],complex))
    ledger=Ledger()
    with ResourceScope(ledger):copied,raw,repeated=deepcopy([original,original.data,original])
    assert copied is repeated and raw is copied.data
    assert ledger.receipt()["live_memory_bytes"]==raw.nbytes
    assert not np.shares_memory(raw,original.data)


def test_whole_kraus_deepcopy_group_rejects_before_first_factory(monkeypatch):
    channel=Kraus((np.diag([1,.8]).astype(complex),np.array([[0,.6],[0,0]],complex)))
    amount=native_storage_bytes(vars(channel))
    assert amount==128
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Partial channel deepcopy before group admission"))
    ledger=Ledger(Limits(max_total_memory_bytes=amount-1))
    with ResourceScope(ledger),pytest.raises(MemoryError):deepcopy(channel)
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("label", ["A","-iX",3,None])
def test_invalid_operator_label_does_not_allocate(label,monkeypatch):
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("Invalid label allocated"))
    with ResourceScope(Ledger()),pytest.raises(ValueError):Operator.from_label(label)


@pytest.mark.parametrize("factory", [Operator,Kraus,SuperOp,Choi,PTM,Chi,Stinespring])
def test_complex_strided_deepcopy_never_aliases_input(factory):
    data=np.array([[1,2j],[-3j,4]],complex)[:,::-1]
    original=Operator(data) if factory is Operator else factory(Operator(data))
    ledger=Ledger()
    with ResourceScope(ledger):copied=deepcopy(original)
    expected=original.data if factory is Operator else original.to_superop().data
    actual=copied.data if factory is Operator else copied.to_superop().data
    np.testing.assert_allclose(actual,expected,atol=1e-13)
    if factory is Operator:
        copied.data[0,0]+=1j
        assert copied.data[0,0]!=original.data[0,0]
    assert ledger.receipt()["live_memory_bytes"]==native_storage_bytes(vars(copied))


@pytest.mark.parametrize("scale", [1e-300,1e300])
def test_phase_equivalence_does_not_overflow_or_create_large_temporaries(scale):
    reference=np.array([[1,1j],[-1j,.5]],complex)*scale
    candidate=reference*np.exp(.7j)
    ledger=Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger):assert Operator(reference).equiv(Operator(candidate))
    assert ledger.receipt()["live_memory_bytes"]==0
