# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""User dictionaries are not an execution configuration or a format sidecar."""
import io
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.compiler import native_transpile
from quantumbridge.qml import QNode
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps, qpy_loads


class Token:
    pass


def source():
    p = qb.Parameter("angle")
    data = {"global_phase": "user phase", "registers": ["user register"],
        "classical_scope": {"user": True}, "nested": [1]}
    circuit = qb.QuantumCircuit(1, metadata=data, global_phase=p/5)
    circuit.ry(p, 0)
    return circuit, p, data


@pytest.mark.parametrize("action", ["copy", "empty", "inverse", "decompose", "compose", "bind", "compile"])
def test_metadata_reserved_names_do_not_change_execution_or_factory_phase(action):
    circuit, p, data = source()
    if action == "empty": result = circuit.copy_empty_like()
    elif action == "compose": result = circuit.compose(qb.QuantumCircuit(1))
    elif action == "bind": result = circuit.assign_parameters({p: .3})
    elif action == "compile": result = native_transpile(circuit, basis_gates=["rz", "sx", "x", "cx"])
    else: result = getattr(circuit, action)()
    if result.parameters: result = result.assign_parameters({result.parameters[0]: .3})
    rotation = np.array([[np.cos(.15), -np.sin(.15)], [np.sin(.15), np.cos(.15)]])
    expected = np.exp(.06j)*(np.eye(2) if action == "empty" else rotation)
    if action == "inverse": expected = expected.conj().T
    np.testing.assert_allclose(Operator(result).data, expected, atol=1e-12, rtol=0)
    assert circuit.metadata is data and circuit.parameters == (p,)
    assert data["global_phase"] == "user phase"


def test_arbitrary_python_userdata_mutation_leaves_operator_jacobian_hvp_and_frames_unchanged():
    circuit, p, data = source()
    data["token"] = Token()
    node = QNode.from_circuit(circuit, qb.PauliZ(0), diff_method="parameter-shift", max_diff=2)
    assert node(.3) == pytest.approx(np.cos(.3), abs=1e-12)
    data.clear()
    data.update(global_phase=object(), classical_scope=object(), registers=object())
    assert node.compute_jacobian(.3) == pytest.approx(-np.sin(.3), abs=1e-10)
    assert node.compute_hvp(.7, .3) == pytest.approx(-.7*np.cos(.3), abs=1e-10)
    assert circuit.data[0].params == [p]
    np.testing.assert_allclose(Operator(circuit.assign_parameters({p: .3})).data,
        np.exp(.06j)*np.array([[np.cos(.15), -np.sin(.15)], [np.sin(.15), np.cos(.15)]]), atol=1e-12, rtol=0)


def test_json_userdata_and_symbolic_execution_have_distinct_real_ir_records():
    circuit, p, data = source()
    payload = circuit.to_ir().to_dict()
    assert payload["metadata"] == data
    assert payload["execution"]["version"] == 1
    restored = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert restored.metadata == data and restored.parameters[0].name == p.name
    np.testing.assert_allclose(Operator(restored.assign_parameters({restored.parameters[0]: .3})).data,
        Operator(circuit.assign_parameters({p: .3})).data, atol=1e-12, rtol=0)


def test_json_reserved_userdata_has_standard_qpy_bilateral_transport():
    qiskit = pytest.importorskip("qiskit")
    from qiskit import qpy
    circuit, p, data = source()
    wire = qpy_dumps(circuit.assign_parameters({p: .3}))
    public = qpy.load(io.BytesIO(wire))[0]
    assert public.metadata == data and public.global_phase == pytest.approx(.06)
    upstream = qiskit.QuantumCircuit(1, metadata=data, global_phase=.06)
    upstream.ry(.3, 0)
    output = io.BytesIO()
    qpy.dump(upstream, output, version=13)
    restored = qpy_loads(output.getvalue())[0]
    assert restored.metadata == data and restored.global_phase == pytest.approx(.06)
    np.testing.assert_allclose(Operator(restored).data, Operator(circuit.assign_parameters({p: .3})).data,
        atol=1e-12, rtol=0)


def test_legacy_fluent_metadata_phase_contract_is_not_reinterpreted():
    circuit = qb.Circuit(1, metadata={"global_phase": .2}).x(0)
    assert circuit.global_phase == .2
    circuit.metadata["global_phase"] = .4
    assert circuit.global_phase == .4


class CopyBomb:
    def __deepcopy__(self, memo):
        pytest.fail("execution or rejected transport invoked a user copy callback")


@pytest.mark.parametrize("action", ["operator", "device", "decompose", "inverse", "compile", "qnode"])
def test_nonsemantic_user_callbacks_are_not_executed_by_calculation(action):
    circuit = qb.QuantumCircuit(1, metadata={"opaque": CopyBomb()}, global_phase=.2)
    circuit.ry(.3, 0)
    if action == "device":
        actual = qb.StatevectorDevice().statevector(circuit)
        np.testing.assert_allclose(actual, np.exp(.2j)*np.array([np.cos(.15),np.sin(.15)]), atol=1e-12, rtol=0)
    elif action == "qnode":
        assert QNode.from_circuit(circuit,qb.PauliZ(0))() == pytest.approx(np.cos(.3),abs=1e-12)
    else:
        result = circuit if action == "operator" else native_transpile(circuit) if action == "compile" else getattr(circuit,action)()
        expected = np.exp(.2j)*np.array([[np.cos(.15),-np.sin(.15)],[np.sin(.15),np.cos(.15)]])
        if action == "inverse":expected = expected.conj().T
        np.testing.assert_allclose(Operator(result).data,expected,atol=1e-12,rtol=0)


@pytest.mark.parametrize("action", ["copy", "empty", "bind", "qpy", "ir"])
def test_managed_user_copy_and_serialization_reject_foreign_callbacks_atomically(action):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.serialization import qpy_dump, UnsupportedFeature as FormatUnsupported
    circuit, p, data = source()
    data["opaque"] = CopyBomb()
    output = io.BytesIO(b"existing"); output.seek(0)
    with ResourceScope(UnifiedResourceLedger()), pytest.raises((qb.UnsupportedFeature,FormatUnsupported)):
        if action == "copy":circuit.copy()
        elif action == "empty":circuit.copy_empty_like()
        elif action == "bind":circuit.assign_parameters({p:.3},inplace=True)
        elif action == "qpy":qpy_dump(circuit,output)
        else:circuit.to_ir().to_json()
    assert output.getvalue() == b"existing"
    assert circuit.metadata is data and circuit.parameters == (p,) and circuit.data[0].params == [p]


def test_classical_scope_survives_userdata_replacement_and_typed_ir_without_fake_qpy():
    from quantumbridge.core import classical as ce
    from quantumbridge.serialization import UnsupportedFeature, qasm3_dumps
    circuit = qb.QuantumCircuit(1,metadata={"scope":"user"},global_phase=.2)
    variable = ce.Var.new("input",ce.Bool())
    circuit.add_input(variable);circuit.ry(.3,0)
    circuit.metadata={"opaque":Token(),"classical_scope":"not a declaration"}
    for result in (circuit,circuit.copy_empty_like(vars_mode="captures"),circuit.decompose(),circuit.inverse()):
        assert len(list(result.iter_input_vars()))+len(list(result.iter_captured_vars())) == 1
    for call in (lambda:qpy_dumps(circuit),lambda:qasm3_dumps(circuit,allow_metadata_loss=True)):
        with pytest.raises(UnsupportedFeature):call()
    assert list(circuit.iter_input_vars()) == [variable]
    circuit.metadata={"classical_scope":"user field"}
    restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert restored.metadata == circuit.metadata and list(restored.iter_input_vars()) == [variable]
    assert restored.global_phase == pytest.approx(.2)


@pytest.mark.parametrize("action", ["operator", "device", "compile", "decompose", "convert"])
def test_managed_execution_borrows_opaque_userdata_without_invoking_it(action):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    circuit=qb.QuantumCircuit(1,metadata={"opaque":CopyBomb()},global_phase=.2);circuit.ry(.3,0)
    with ResourceScope(UnifiedResourceLedger()):
        if action=="device":result=qb.StatevectorDevice().statevector(circuit)
        elif action=="operator":result=Operator(circuit).data
        elif action=="compile":result=Operator(native_transpile(circuit)).data
        elif action=="decompose":result=Operator(circuit.decompose()).data
        else:result=Operator(circuit.to_gate()).data
    assert np.isfinite(result).all()


def test_public_copy_decompose_inverse_keeps_userdata_contract_and_full_complex_phase():
    token=Token();metadata={"token":token,"again":token,"nested":[1]}
    circuit=qb.QuantumCircuit(1,metadata=metadata,global_phase=.2);circuit.ry(.3,0)
    copied=circuit.copy();lowered=copied.decompose();inverse=lowered.inverse()
    assert copied.metadata is not metadata and copied.metadata["token"] is not token
    assert copied.metadata["token"] is copied.metadata["again"]
    assert lowered.metadata is copied.metadata and inverse.metadata=={}
    np.testing.assert_allclose(Operator(inverse).data,Operator(circuit).data.conj().T,atol=1e-12,rtol=0)


def test_live_parameter_operator_and_hvp_never_copy_opaque_user_callbacks():
    p=qb.Parameter("angle")
    circuit=qb.QuantumCircuit(1,metadata={"opaque":CopyBomb()},global_phase=p/5);circuit.ry(p,0)
    node=QNode.from_circuit(circuit,qb.PauliZ(0),max_diff=2,diff_method="parameter-shift")
    assert node(.3)==pytest.approx(np.cos(.3),abs=1e-12)
    assert node.compute_jacobian(.3)==pytest.approx(-np.sin(.3),abs=1e-10)
    assert node.compute_hvp(.7,.3)==pytest.approx(-.7*np.cos(.3),abs=1e-10)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit,parameters={p:.3}),
        np.exp(.06j)*np.array([np.cos(.15),np.sin(.15)]),atol=1e-12,rtol=0)


def test_managed_public_copy_admits_all_nested_userdata_before_any_copy_callback():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    body=qb.QuantumCircuit(1);body.ry(.3,0)
    owner=qb.Gate("custom",1,definition=body)
    owner.definition.metadata={"opaque":CopyBomb()}
    circuit=qb.QuantumCircuit(1);circuit.append(owner,[0],copy=False)
    with ResourceScope(UnifiedResourceLedger()),pytest.raises(qb.UnsupportedFeature):circuit.copy()
    assert circuit.data[0].operation is owner and len(owner.definition.data)==1


def test_opaque_metadata_type_comparisons_do_not_invoke_foreign_metaclass_equality():
    from quantumbridge.serialization import UnsupportedFeature
    class Meta(type):
        def __eq__(cls,other):pytest.fail("transport invoked foreign type equality")
        __hash__=type.__hash__
    class Opaque(metaclass=Meta):pass
    circuit=qb.QuantumCircuit(1,metadata={"opaque":Opaque()});circuit.x(0)
    for call in (lambda:qpy_dumps(circuit),lambda:circuit.to_ir().to_json()):
        with pytest.raises(UnsupportedFeature):call()
    np.testing.assert_allclose(Operator(circuit).data,[[0,1],[1,0]],atol=1e-12,rtol=0)


@pytest.mark.parametrize("format",["qasm3","qpy","ir-json"])
def test_explicit_external_artifact_preserves_reserved_userdata_not_execution_sidecars(format):
    from quantumbridge.serialization import serialize_circuit,deserialize_circuit
    circuit,p,data=source();circuit=circuit.assign_parameters({p:.3})
    artifact=serialize_circuit(circuit,format,metadata_policy="external")
    assert artifact.sidecar["metadata"]==data
    restored=deserialize_circuit(artifact)
    assert restored.metadata==data and restored.global_phase==pytest.approx(.06)
    np.testing.assert_allclose(Operator(restored).data,Operator(circuit).data,atol=1e-12,rtol=0)


@pytest.mark.parametrize("mutation", ["unknown", "version", "scope", "phase"])
def test_malformed_typed_execution_record_refuses_without_rewriting_userdata(mutation):
    circuit,p,data=source();payload=circuit.to_ir().to_dict()
    if mutation=="unknown":payload["execution"]["arbitrary"]={}
    elif mutation=="version":payload["execution"]["version"]=True
    elif mutation=="scope":payload["execution"]["classical_scope"]={"version":1,"identifiers":"wrong"}
    else:payload["execution"]["global_phase"]="not a phase"
    with pytest.raises((TypeError,ValueError)):IRProgram.from_dict(payload)
    assert circuit.metadata is data and circuit.parameters==(p,)
