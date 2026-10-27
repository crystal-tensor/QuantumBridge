# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Controlled and annotated source owners share the native executable frame ABI."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.qml import QNode


def make(kind,symbolic=True,state=0):
    p=qb.ParameterVector("angle",1)[0]
    body=qb.QuantumCircuit(1,name="body",global_phase=p/5);body.ry(2*p,0)
    base=body.to_gate(parameter_map=None if symbolic else {p:.25})
    owner=base.control(ctrl_state=state) if kind=="controlled" else qb.AnnotatedOperation(base,qb.ControlModifier(1,state))
    circuit=qb.QuantumCircuit(2,global_phase=.13,metadata={"global_phase":"user value"})
    handle=circuit.append(owner,[0,1],copy=False)
    return circuit,owner,base,p,handle


def oracle(x,state=0):
    u=np.exp(1j*x/5)*np.array([[np.cos(x),-np.sin(x)],[np.sin(x),np.cos(x)]])
    result=np.eye(4,dtype=complex);start=2*state;result[start:start+2,start:start+2]=u
    return np.exp(.13j)*result


@pytest.mark.parametrize("kind",["controlled","annotated"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("state",[0,1])
@pytest.mark.parametrize("action",["direct","copy","compose","bind","reinsert","inverse","handle","from","ir","qpy"])
def test_cached_control_annotation_frames_bind_factory_format_and_inverse_math(kind,symbolic,state,action):
    circuit,owner,base,p,handle=make(kind,symbolic,state)
    (base if kind=="annotated" else owner).params=[.7]
    assert circuit.data[0].params==[p if symbolic else .25]
    assert circuit.parameters==((p,) if symbolic else ())
    x=.3 if symbolic else .25
    if action=="copy":result=circuit.copy()
    elif action=="compose":result=qb.QuantumCircuit(2).compose(circuit)
    elif action=="bind":result=circuit.assign_parameters({p:.3} if symbolic else {})
    elif action=="reinsert":circuit.data[0]=circuit.data[0].replace();result=circuit;x=.7
    elif action=="inverse":result=circuit.inverse()
    elif action=="handle":
        handle.inverse();result=circuit
    elif action=="from":
        result=qb.QuantumCircuit.from_instructions(circuit.data,global_phase=.13,metadata=circuit.metadata)
    elif action=="ir":result=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif action=="qpy":result=qpy_loads(qpy_dumps(circuit))[0]
    else:result=circuit
    if result.parameters:result=result.assign_parameters({result.parameters[0]:x})
    expected=oracle(x,state)
    if action=="inverse":expected=expected.conj().T
    elif action=="handle":expected=np.exp(.26j)*expected.conj().T
    np.testing.assert_allclose(Operator(result).data,expected,atol=2e-12,rtol=0)
    assert (base if kind=="annotated" else owner).params==[.7]


@pytest.mark.parametrize("kind",["controlled","annotated"])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_cached_control_annotation_frames_reach_real_jacobian_hvp_after_source_change(kind,transport):
    circuit,owner,base,p,_=make(kind)
    (base if kind=="annotated" else owner).params=[qb.Parameter("source_only")]
    assert circuit.parameters==(p,)
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    node=QNode.from_circuit(circuit,qb.PauliZ(1),diff_method="parameter-shift",max_diff=2)
    assert node(.3)==pytest.approx(np.cos(.6),abs=3e-12)
    assert node.compute_jacobian(.3)==pytest.approx(-2*np.sin(.6),abs=3e-10)
    assert node.compute_hvp(.7,.3)==pytest.approx(-2.8*np.cos(.6),abs=5e-10)


def test_control_base_parameter_view_is_authoritative_but_stored_frame_remains_bindable():
    circuit,owner,base,p,_=make("controlled")
    owner.base_gate.params=[.7]
    assert list(owner.params)==[.7] and circuit.data[0].params==[p]
    np.testing.assert_allclose(Operator(circuit.assign_parameters({p:.3})).data,oracle(.3),atol=2e-12,rtol=0)


@pytest.mark.parametrize("kind",["controlled","annotated"])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_post_bind_numeric_frame_source_mutation_and_explicit_data_rebinding(kind,transport):
    circuit,owner,base,p,_=make(kind)
    bound=circuit.assign_parameters({p:.3})
    exposed=bound.data[0].operation;q=qb.Parameter("replacement")
    exposed.params=[q]
    assert bound.parameters==() and bound.data[0].params==[.3]
    np.testing.assert_allclose(Operator(bound).data,oracle(.3),atol=2e-12,rtol=0)
    bound.data[0]=bound.data[0].replace()
    assert bound.parameters==(q,)
    if transport=="ir":bound=circuit_from_ir(IRProgram.from_json(bound.to_ir().to_json()))
    elif transport=="qpy":bound=qpy_loads(qpy_dumps(bound))[0]
    np.testing.assert_allclose(Operator(bound.assign_parameters({bound.parameters[0]:.4})).data,oracle(.4),atol=2e-12,rtol=0)
    assert (base if kind=="annotated" else owner).params==[p]


@pytest.mark.parametrize("kind",["controlled","annotated"])
def test_annotated_inverse_factory_captures_a_new_owned_base_and_frame(kind):
    circuit,owner,base,p,_=make(kind)
    result=circuit.inverse(annotated=True)
    exposed=result.data[0].operation
    assert exposed.base_op is not owner if kind=="controlled" else exposed.base_op is not base
    (base if kind=="annotated" else owner).params=[.7]
    assert result.parameters==(p,) and result.data[0].params==[p]
    np.testing.assert_allclose(Operator(result.assign_parameters({p:.3})).data,oracle(.3).conj().T,atol=2e-12,rtol=0)


def test_control_base_cycle_is_refused_before_any_owner_copy(monkeypatch):
    from quantumbridge.core.operations import execution_operation
    circuit,owner,_,_,_=make("controlled")
    object.__setattr__(owner,"base_gate",owner)
    monkeypatch.setattr(qb.ControlledGate,"copy",lambda *a,**kw:pytest.fail("cyclic base copied"))
    with pytest.raises(ValueError,match="Cyclic"):execution_operation(circuit.operations[0])


@pytest.mark.parametrize("kind",["controlled","annotated"])
def test_control_annotation_rebind_work_and_width_admission_precede_copy(kind,monkeypatch):
    from quantumbridge.core.operations import execution_operation
    from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
    circuit,owner,base,p,_=make(kind)
    (base if kind=="annotated" else owner).params=[.7]
    monkeypatch.setattr(type(owner),"copy",lambda *a,**kw:pytest.fail("unadmitted frame copied"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=1)),pytest.raises(MemoryError):
        execution_operation(circuit.operations[0])
    object.__setattr__(circuit.operations[0],"targets",(0,))
    with pytest.raises(ValueError,match="width"):execution_operation(circuit.operations[0])


def test_live_annotation_modifier_parameters_bind_without_losing_captured_base_slots():
    circuit,owner,base,p,_=make("annotated")
    q=qb.Parameter("power");owner.modifiers[:]=[qb.InverseModifier(),qb.ControlModifier(1,0),qb.PowerModifier(q)]
    base.params=[.7]
    assert set(circuit.parameters)=={p,q}
    prepared=circuit.assign_parameters({q:2})
    assert prepared.parameters==(p,)
    np.testing.assert_allclose(Operator(prepared.assign_parameters({p:.3})).data,oracle(-.6),atol=2e-12,rtol=0)


@pytest.mark.parametrize("name",["renamed","literal_o0","literal_o0_o0"])
@pytest.mark.parametrize("state",[0,1])
@pytest.mark.parametrize("transport",["ir","qpy"])
def test_renamed_generic_control_keeps_literal_name_suffix_and_full_math(name,state,transport):
    circuit,owner,_,p,_=make("controlled",state=state)
    owner.name=name
    expected_name=name+("_o0" if state==0 else "")
    if transport=="ir":restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    else:restored=qpy_loads(qpy_dumps(circuit))[0]
    assert restored.operations[0].metadata["gate"].name==expected_name
    np.testing.assert_allclose(Operator(restored.assign_parameters({restored.parameters[0]:.3})).data,
        oracle(.3,state),atol=2e-12,rtol=0)


@pytest.mark.parametrize("field,value",[("closed_control_name",None),("closed_control_name",[]),
    ("closed_control_name","different"),("name",None),("name",[]),("name",""),("label",3),("label",{})])
def test_malformed_controlled_ir_names_and_labels_are_rejected(field,value):
    circuit,_,_,_,_=make("controlled")
    payload=circuit.to_ir().to_dict()
    payload["instructions"][0]["metadata"]["gate"][field]=value
    with pytest.raises(ValueError):IRProgram.from_dict(payload)


def test_legacy_generic_control_ir_without_closed_name_keeps_canonical_open_name():
    circuit,owner,_,p,_=make("controlled")
    payload=circuit.to_ir().to_dict()
    del payload["instructions"][0]["metadata"]["gate"]["closed_control_name"]
    restored=circuit_from_ir(IRProgram.from_dict(payload))
    assert restored.operations[0].metadata["gate"].name==owner.name
    np.testing.assert_allclose(Operator(restored.assign_parameters({restored.parameters[0]:.3})).data,
        oracle(.3),atol=2e-12,rtol=0)


def changed_definition_case(kind,symbolic,copy):
    p=qb.Parameter("p");body=qb.QuantumCircuit(1,name="body",global_phase=p/5);body.ry(2*p,0)
    base=getattr(body,"to_instruction" if kind=="instruction" else "to_gate")(
        parameter_map=None if symbolic else {p:.25})
    owner=base.control(ctrl_state=0) if kind=="controlled" else qb.AnnotatedOperation(base,qb.ControlModifier(1,0)) if kind=="annotated" else base
    circuit=qb.QuantumCircuit(owner.num_qubits);handle=circuit.append(owner,range(owner.num_qubits),copy=copy)
    target=base if kind=="annotated" else owner;value=p if symbolic else .25
    replacement=qb.QuantumCircuit(target.num_qubits,global_phase=value/7);replacement.rz(3*value,target.num_qubits-1)
    target.definition=replacement
    x=.3 if symbolic else .25;changed=not (symbolic and copy)
    local=np.exp(1j*x/(7 if changed else 5))*(np.diag([np.exp(-1.5j*x),np.exp(1.5j*x)]) if changed else
        np.array([[np.cos(x),-np.sin(x)],[np.sin(x),np.cos(x)]]))
    if kind=="controlled" and changed:expected=np.kron(np.eye(2),local)
    elif kind in {"controlled","annotated"}:expected=np.eye(4,dtype=complex);expected[:2,:2]=local
    else:expected=local
    return circuit,p,handle,expected


def test_source_definition_replacement_updates_only_the_derived_instruction_name_atomically():
    original=qb.QuantumCircuit(1,name="original");original.x(0)
    owner=original.to_instruction();previous=owner.definition
    illegal=qb.QuantumCircuit(2,name="illegal")
    with pytest.raises(ValueError):owner.definition=illegal
    assert owner.definition is previous and owner.metadata["definition_name"]=="original"
    replacement=qb.QuantumCircuit(1,name="replacement");replacement.h(0)
    owner.definition=replacement
    assert owner.metadata["definition_name"]=="replacement" and owner.definition is not replacement
    owner.metadata["definition_name"]="user annotation";owner.definition=original
    assert owner.metadata["definition_name"]=="user annotation"


def test_source_definition_replacement_does_not_invoke_foreign_metadata_equality():
    class Foreign:
        def __eq__(self,other):pytest.fail("foreign equality used for a derived name")
    original=qb.QuantumCircuit(1,name="original");original.x(0)
    owner=original.to_instruction();foreign=Foreign();owner.metadata["definition_name"]=foreign
    owner.definition=qb.QuantumCircuit(1,name="replacement")
    assert owner.metadata["definition_name"] is foreign


@pytest.mark.parametrize("kind",["gate","instruction","controlled","annotated"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("action",["bind","copy","inverse","handle","ir","qpy"])
def test_changed_source_definition_binding_factory_and_transport_follow_actual_complex_operator(kind,symbolic,copy,action):
    circuit,p,handle,expected=changed_definition_case(kind,symbolic,copy)
    if action=="copy":result=circuit.copy()
    elif action=="inverse":result=circuit.inverse();expected=expected.conj().T
    elif action=="handle":handle.inverse();result=circuit;expected=expected.conj().T
    elif action=="ir":result=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif action=="qpy":result=qpy_loads(qpy_dumps(circuit))[0]
    else:result=circuit
    values={result.parameters[0]:.3} if symbolic else {}
    np.testing.assert_allclose(Operator(result.assign_parameters(values)).data,expected,atol=2e-12,rtol=0)


@pytest.mark.parametrize("kind",["controlled","annotated"])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_hundred_wire_cached_control_annotation_mps_has_no_dense_escape(kind,transport,monkeypatch):
    from quantumbridge.information.matrix_product_state import MatrixProductState
    _,owner,base,p,_=make(kind)
    circuit=qb.QuantumCircuit(100);circuit.h(0);circuit.append(owner,[0,99],copy=False)
    (base if kind=="annotated" else owner).params=[.7]
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    def forbidden(*args,**kwargs):pytest.fail("hundred-wire MPS used a dense escape")
    for cls,name in ((qb.Gate,"to_matrix"),(qb.StatevectorDevice,"statevector"),
            (qb.DensityMatrixDevice,"density_matrix"),(MatrixProductState,"statevector")):
        monkeypatch.setattr(cls,name,forbidden)
    node=QNode.from_circuit(circuit,qb.PauliX(0),device=qb.MatrixProductStateDevice(max_memory_mb=2,
        max_bond_dim=4,cutoff=0),max_diff=2,diff_method="parameter-shift")
    x=.3;k=.2
    assert node(x)==pytest.approx(np.cos(x)*np.cos(k*x),abs=3e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(x)*np.cos(k*x)-k*np.cos(x)*np.sin(k*x),abs=3e-10)
    second=-(1+k*k)*np.cos(x)*np.cos(k*x)+2*k*np.sin(x)*np.sin(k*x)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*second,abs=5e-10)


@pytest.mark.parametrize("kind",["controlled","annotated"])
@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
def test_cached_control_annotation_frames_have_actual_framework_second_derivatives(kind,framework):
    circuit,owner,base,p,_=make(kind)
    (base if kind=="annotated" else owner).params=[.7]
    node=QNode.from_circuit(circuit,qb.PauliZ(1),interface=framework,max_diff=2,diff_method="parameter-shift")
    module=pytest.importorskip(framework);x=.3
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True)
        first=module.autograd.grad(node(value),value,create_graph=True)[0]
        actual=float(module.autograd.grad(first,value)[0])
    elif framework=="autograd":actual=float(module.grad(module.grad(node))(x))
    elif framework=="jax":actual=float(module.grad(module.grad(node))(module.numpy.asarray(x,dtype=module.numpy.float64)))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as outer:
            with module.GradientTape() as inner:result=node(value)
            first=inner.gradient(result,value)
        actual=float(outer.gradient(first,value))
    assert actual==pytest.approx(-4*np.cos(2*x),abs=5e-10)
