# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Trusted inverse qualification is not an inverse_of metadata heuristic."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.core.unitary_inverse import primitive_matrix_inverse
from quantumbridge.core import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.execution.derivative_status import ResourceLimitError as RuntimeResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.serialization import qpy_dumps,qpy_loads,SerializationLimits,ResourceLimitError,UnsupportedFeature
from quantumbridge.information import Operator


def source():
    value=np.array([[1,1j],[1j,1]],complex)/np.sqrt(2)
    return qb.Circuit(1).unitary(value,[0])


def test_same_matrix_and_inverse_metadata_do_not_qualify_an_unconstructed_operation():
    real=source().inverse()
    operation=real.operations[0]
    fake=qb.Operation(operation.name,operation.targets,operation.controls,operation.params,dict(operation.metadata))
    assert fake.metadata["matrix"] is operation.metadata["matrix"]
    assert fake.metadata["inverse_of"]==operation.metadata["inverse_of"]
    untrusted=qb.Circuit(1)
    untrusted.operations.append(fake)
    qpy_dumps(real)
    with pytest.raises(UnsupportedFeature): qpy_dumps(untrusted)


@pytest.mark.parametrize("corruption",["inverse_of","name","matrix","owner","owner_width","binding","foreign_comparison","changed_array","digest","writable"])
def test_inverse_qualification_rejects_changed_or_foreign_fields_without_callbacks(corruption):
    circuit=source().inverse()
    operation=circuit.operations[0]
    calls=[]
    class Trap:
        def __eq__(self,other): calls.append("eq");raise AssertionError("Foreign comparison executed")
        def __array__(self,*a,**k): calls.append("array");raise AssertionError("Foreign array executed")
    if corruption=="inverse_of": operation.metadata["inverse_of"]="rx"
    elif corruption=="name": object.__setattr__(operation,"name","opaque_dg")
    elif corruption=="matrix": operation.metadata["matrix"]=Trap()
    elif corruption=="owner":
        class Foreign(UnitaryGate):
            @property
            def definition(self): calls.append("definition");raise AssertionError("Foreign definition executed")
        object.__setattr__(operation,"_native_inverse_owner",object.__new__(Foreign))
    elif corruption=="owner_width": object.__setattr__(operation._native_inverse_owner,"num_qubits",100000000)
    elif corruption=="binding":
        duplicate=qb.Operation(operation.name,operation.targets,metadata=dict(operation.metadata))
        object.__setattr__(duplicate,"_native_inverse_owner",operation._native_inverse_owner)
        object.__setattr__(duplicate,"_native_inverse_qualification",operation._native_inverse_qualification)
        circuit.operations[0]=duplicate
    elif corruption=="foreign_comparison":
        fields=list(operation._native_inverse_qualification)
        fields[5]=Trap()
        object.__setattr__(operation,"_native_inverse_qualification",tuple(fields))
    elif corruption=="digest":
        fields=list(operation._native_inverse_qualification)
        fields[8]=b"forged"
        object.__setattr__(operation,"_native_inverse_qualification",tuple(fields))
    elif corruption=="writable": operation.metadata["matrix"].flags.writeable=True
    else:
        array=operation.metadata["matrix"]
        array.flags.writeable=True
        array[0,0]+=.1
        array.flags.writeable=False
    with pytest.raises((qb.UnsupportedFeature,MemoryError)): qpy_dumps(circuit)
    assert calls==[]
    qpy_dumps(source().inverse())


@pytest.mark.parametrize("limit",[SerializationLimits(max_numeric_elements=3),SerializationLimits(max_input_bytes=63)])
def test_qpy_inverse_numeric_limits_precede_owned_canonical_copy(limit,monkeypatch):
    circuit=source().inverse()
    monkeypatch.setattr(UnitaryGate,"copy",lambda *a,**k:pytest.fail("Canonical copy preceded QPY admission"))
    with pytest.raises(ResourceLimitError): qpy_dumps(circuit,limits=limit)


def test_primitive_inverse_matrix_cap_precedes_any_destination(monkeypatch):
    operation=source().operations[0]
    import quantumbridge.execution.array_ownership as arrays
    monkeypatch.setattr(arrays,"retained_array",lambda *a,**k:pytest.fail("Inverse allocated before matrix cap"))
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=1)),pytest.raises(MemoryError):
        primitive_matrix_inverse(operation)


def test_qualified_copy_ir_remap_and_phase_binding_do_not_export_private_fields():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    original=source().inverse()
    original.global_phase=qb.Parameter("phase")
    copy=original.copy()
    assert copy.operations[0].metadata["matrix"] is not original.operations[0].metadata["matrix"]
    qpy_dumps(copy)
    ir=copy.to_ir().to_json()
    assert "_native_inverse" not in ir and "inverse_of" not in ir
    restored=circuit_from_ir(IRProgram.from_json(ir))
    bound=restored.bind({"phase":.23})
    target=qb.Circuit(3).compose(bound,qubits=[2],inplace=False,copy=False)
    roundtrip=qpy_loads(qpy_dumps(target))[0]
    np.testing.assert_allclose(Operator(roundtrip).data,Operator(target).data,atol=2e-14,rtol=0)
    assert original.operations[0].name=="unitary_dg" and original.operations[0].metadata["inverse_of"]=="unitary"


def test_concurrent_dumps_are_readonly_and_deterministic():
    circuit=source().inverse()
    operation=circuit.operations[0]
    fields=dict(operation.__dict__)
    matrix=operation.metadata["matrix"].copy()
    with ThreadPoolExecutor(max_workers=4) as executor: outputs=list(executor.map(lambda _:qpy_dumps(circuit),range(12)))
    assert all(value==outputs[0] for value in outputs)
    assert operation.__dict__.keys()==fields.keys()
    assert operation._native_inverse_owner is fields["_native_inverse_owner"]
    np.testing.assert_array_equal(operation.metadata["matrix"],matrix)


@pytest.mark.parametrize("limiter",["parent","child"])
def test_owned_inverse_equal_one_below_and_escaped_storage_lifetimes(limiter):
    operation=source().operations[0]
    baseline=UnifiedResourceLedger()
    with ResourceScope(baseline): result=primitive_matrix_inverse(operation)
    receipt=baseline.receipt()
    peak=receipt["peak_memory_bytes"]
    assert receipt["live_memory_bytes"]==64
    assert receipt["observed_array_bytes"]["native_inverse_matrix_adjoint"]==64
    del result
    gc.collect()
    assert baseline.receipt()["live_memory_bytes"]==0
    for maximum,success in [(peak,True),(peak-1,False)]:
        small=UnifiedExecutionLimits(max_total_memory_bytes=maximum)
        parent=UnifiedResourceLedger(small if limiter=="parent" else None)
        child=UnifiedResourceLedger(small if limiter=="child" else None,parent=parent)
        try:
            with ResourceScope(child): value=primitive_matrix_inverse(operation)
        except RuntimeResourceLimitError:
            assert not success
        else:
            assert success and not value.metadata["matrix"].flags.writeable
            assert parent.receipt()["live_memory_bytes"]==child.receipt()["live_memory_bytes"]==64
            del value
        gc.collect()
        assert child.receipt()["live_memory_bytes"]==parent.receipt()["live_memory_bytes"]==0


def test_witness_constructor_failure_releases_arrays_and_preserves_source(monkeypatch):
    operation=source().operations[0]
    before=operation.metadata["matrix"].copy()
    ledger=UnifiedResourceLedger()
    original=UnitaryGate.validate_parameter
    calls=[]
    def fail_second(owner,value):
        calls.append(True)
        if len(calls)==2: raise ValueError("injected witness validation failure")
        return original(owner,value)
    monkeypatch.setattr(UnitaryGate,"validate_parameter",fail_second)
    try:
        with ResourceScope(ledger): primitive_matrix_inverse(operation)
    except ValueError as error:
        assert "injected witness" in str(error)
    else: pytest.fail("Injected constructor error did not propagate")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    np.testing.assert_array_equal(operation.metadata["matrix"],before)
    assert not hasattr(operation,"_native_inverse_owner")
    monkeypatch.undo()
    qpy_dumps(source().inverse())


def test_failed_standard_dump_never_publishes_partial_qpy(monkeypatch):
    import io
    from quantumbridge.serialization import qpy_dump
    circuit=source().inverse()
    stream=io.BytesIO(b"untouched")
    stream.seek(0,2)
    monkeypatch.setattr(UnitaryGate,"copy",lambda *a,**k:(_ for _ in ()).throw(ValueError("injected copy failure")))
    with pytest.raises(ValueError,match="injected copy"): qpy_dump(circuit,stream)
    assert stream.getvalue()==b"untouched"


@pytest.mark.parametrize("name",["opaque_dg","h_dg","unitary_dg","unitary_dg_dg"])
def test_unknown_derived_name_never_gets_a_matrix_fallback(name):
    circuit=qb.Circuit(1)
    circuit.operations.append(qb.Operation(name,(0,),metadata={"matrix":np.eye(2),"inverse_of":name.removesuffix("_dg")}))
    with pytest.raises(UnsupportedFeature): qpy_dumps(circuit)


def test_owned_witness_is_isolated_from_external_source_array_changes():
    original=source()
    inverse=original.inverse()
    expected=Operator(inverse).data.copy()
    original.operations[0].metadata["matrix"][0,0]+=.3
    np.testing.assert_array_equal(Operator(qpy_loads(qpy_dumps(inverse))[0]).data,expected)


def test_trusted_copy_still_refuses_numerical_mutation_of_its_private_snapshot():
    copy=source().inverse().copy()
    matrix=copy.operations[0].metadata["matrix"]
    matrix.flags.writeable=True
    matrix[0,0]+=.1
    with pytest.raises(qb.UnsupportedFeature): qpy_dumps(copy)


def test_concurrent_readonly_serialization_releases_shared_parent_child_account():
    from contextvars import copy_context
    circuit=source().inverse()
    parent=UnifiedResourceLedger()
    child=UnifiedResourceLedger(parent=parent)
    with ResourceScope(child),ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(copy_context().run,qpy_dumps,circuit) for _ in range(12)]
        outputs=[future.result() for future in futures]
    gc.collect()
    assert all(value==outputs[0] for value in outputs)
    assert parent.receipt()["peak_memory_bytes"]>0
    assert parent.receipt()["live_memory_bytes"]==child.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("managed",[False,True])
@pytest.mark.parametrize("path",["operation","circuit","gate","instruction"])
def test_trusted_inverse_witness_copies_preserve_readonly_owned_snapshot(path,managed):
    from contextlib import nullcontext
    from quantumbridge.core.unitary_inverse import inverse_matrix_owner
    original=source().inverse()
    operation=original.operations[0]
    before=operation.metadata["matrix"].copy()
    digest=operation._native_inverse_qualification[8]
    ledger=UnifiedResourceLedger()
    with ResourceScope(ledger) if managed else nullcontext():
        if path=="operation": copied=deepcopy(operation)
        elif path=="circuit": copied=original.copy().operations[0]
        else:
            owner=getattr(original,"to_"+path)().copy()
            copied=object.__getattribute__(owner,"_definition").operations[0]
        assert inverse_matrix_owner(copied) is copied._native_inverse_owner
        assert copied._native_inverse_owner is not operation._native_inverse_owner
        array=copied.metadata["matrix"]
        assert array is not operation.metadata["matrix"]
        assert not np.shares_memory(array,operation.metadata["matrix"])
        assert array.flags.writeable is False
        with pytest.raises(ValueError,match="read-only"):
            array[0,0]+=.1
        assert copied._native_inverse_qualification[8]==digest
    np.testing.assert_array_equal(operation.metadata["matrix"],before)
    assert operation._native_inverse_qualification[8]==digest
    assert operation.metadata["matrix"].flags.writeable is False


@pytest.mark.parametrize("path",["compose","remap","bind","qpy","ir"])
def test_canonicalization_drops_witness_without_changing_complex_matrix_or_phase(path):
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.core.circuit import _remap_operation
    from quantumbridge.core.operations import execution_operation
    original=source().inverse()
    original.global_phase=.23
    expected=Operator(original).data.copy()
    if path=="compose": target=qb.Circuit(1).compose(original)
    elif path=="remap":
        target=qb.Circuit(1)
        target.global_phase=.23
        target.operations=[_remap_operation(original.operations[0],{0:0},copy_operation=False)]
    elif path=="bind": target=original.assign_parameters({})
    elif path=="qpy": target=qpy_loads(qpy_dumps(original))[0]
    else: target=circuit_from_ir(original.to_ir())
    for operation in target.operations:
        assert "_native_inverse_owner" not in operation.__dict__
        assert "_native_inverse_qualification" not in operation.__dict__
        normalized=execution_operation(operation,standardize_inverse=True)
        assert "_native_inverse_owner" not in normalized.__dict__
        assert "_native_inverse_qualification" not in normalized.__dict__
    np.testing.assert_allclose(Operator(qpy_loads(qpy_dumps(target))[0]).data,expected,atol=2e-14,rtol=0)
    assert original.operations[0].metadata["matrix"].flags.writeable is False


@pytest.mark.parametrize("limiter",["parent","child"])
def test_readonly_witness_copy_exact_and_one_below_preflight(limiter,monkeypatch):
    original=source().inverse()
    for maximum,success in [(64,True),(63,False)]:
        small=UnifiedExecutionLimits(max_total_memory_bytes=maximum)
        parent=UnifiedResourceLedger(small if limiter=="parent" else None)
        child=UnifiedResourceLedger(small if limiter=="child" else None,parent=parent)
        with monkeypatch.context() as patch:
            if not success:
                import quantumbridge.execution.array_ownership as arrays
                patch.setattr(arrays,"retained_array",lambda *a,**k:pytest.fail("Denied copy allocated a destination"))
            try:
                with ResourceScope(child): copied=deepcopy(original.operations[0])
            except RuntimeResourceLimitError:
                assert not success
            else:
                assert success
                assert copied.metadata["matrix"].flags.writeable is False
                assert parent.receipt()["live_memory_bytes"]==child.receipt()["live_memory_bytes"]==64
                del copied
        gc.collect()
        assert parent.receipt()["live_memory_bytes"]==child.receipt()["live_memory_bytes"]==0


def test_invalid_witness_copy_refuses_before_allocation_and_recovers(monkeypatch):
    import quantumbridge.execution.array_ownership as arrays
    original=source().inverse()
    operation=original.operations[0]
    before=operation.metadata["matrix"].copy()
    operation.metadata["inverse_of"]="forged"
    with monkeypatch.context() as patch:
        patch.setattr(arrays,"retained_array",lambda *a,**k:pytest.fail("Invalid witness copied before admission"))
        with pytest.raises(qb.UnsupportedFeature): deepcopy(operation)
    np.testing.assert_array_equal(operation.metadata["matrix"],before)
    qpy_dumps(source().inverse().copy())
