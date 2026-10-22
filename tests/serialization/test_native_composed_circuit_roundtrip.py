# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Typed scope belongs to native IR, never a fake QPY metadata sidecar."""
import numpy as np
import json
import pytest
import quantumbridge as qb
from quantumbridge.core import classical as ce
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads,qasm2_dumps,qasm3_dumps,UnsupportedFeature


def test_typed_capture_composition_ir_retains_identity_and_actual_state_trace():
    target=qb.Circuit(1,1);a=target.add_var("a",True)
    body=target.copy_empty_like(vars_mode="captures").store(a,False)
    source=target.compose(body,inline_captures=True).if_else(ce.logical_not(a),qb.Circuit(1,1).x(0)).measure(0,0)
    restored=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert type(restored.get_var("a")) is ce.Var and restored.get_var("a")==a
    result=qb.DensityMatrixDevice().run_shots(restored,shots=2,memory=True)
    assert result.counts()=={"1":2}
    assert all(item["variables"][a.value[0]]["value"] is False for item in result.metadata()["classical_memory"])


@pytest.mark.parametrize("kind",["local","input","capture","stretch"])
def test_qpy_rejects_scope_only_identifiers_instead_of_faking_a_zero_variable_header(kind):
    source=qb.Circuit(1)
    if kind=="local":source.add_uninitialized_var(ce.Var.new("a",ce.Bool()))
    elif kind=="input":source.add_input("a",ce.Bool())
    elif kind=="capture":source.add_capture(ce.Var.new("a",ce.Bool()))
    else:source.add_stretch("s")
    source.metadata=json.loads(json.dumps(source.metadata))
    with pytest.raises(UnsupportedFeature,match="classical|identifier"):qpy_dumps(source)


@pytest.mark.parametrize("version",[2,3])
def test_qasm_metadata_loss_permission_cannot_silently_drop_classical_scope(version):
    source=qb.Circuit(1);source.add_uninitialized_var(ce.Var.new("a",ce.Bool()))
    with pytest.raises(UnsupportedFeature):(qasm2_dumps if version==2 else qasm3_dumps)(source,allow_metadata_loss=True)


def test_wrapped_parameterized_gate_qpy_still_binds_and_executes_native_matrix():
    p=qb.Parameter("p");source=qb.Circuit(1,name="inner").ry(p,0);source.global_phase=p/3
    wrapped=qb.Circuit(2).compose(source,qubits=[1],wrap=True)
    restored=qpy_loads(qpy_dumps(wrapped))[0].bind({p:.3})
    c,s=np.cos(.15),np.sin(.15)
    expected=np.exp(.1j)*np.kron(np.eye(2),np.array([[c,-s],[s,c]]))
    np.testing.assert_allclose(Operator(restored).data,expected,atol=5e-13,rtol=0)


def test_stretch_ir_scope_roundtrip_does_not_turn_it_into_integer_storage():
    source=qb.Circuit(1);s=source.add_stretch("s")
    restored=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert type(restored.get_stretch("s")) is ce.Stretch and restored.get_stretch("s")==s
    assert restored.num_vars==0 and restored.num_stretches==1


def test_public_typed_local_initializer_keyword_is_an_actual_store():
    circuit=qb.Circuit(1);a=circuit.add_var("a",initial=True)
    assert circuit.get_var("a")==a and len(circuit.operations)==1
