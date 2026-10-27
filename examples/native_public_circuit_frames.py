# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free borrowed owners, stored frames, factories, interchange and real AD."""
import json
from unittest.mock import patch
import numpy as np
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.circuit_library import UnitaryGate
from quantumbridge.information.matrix_product_state import MatrixProductState


def rotation(angle):return np.array([[np.cos(angle/2),-np.sin(angle/2)],[np.sin(angle/2),np.cos(angle/2)]])


def main():
    p=qb.ParameterVector("angle",1)[0]
    vector=p.vector;live_params=vector.params
    vector.resize(0);vector.resize(1)
    assert live_params is vector.params and vector[0]==p
    body=qb.QuantumCircuit(1,name="nonlinear");body.ry(2*p+p.sin(),0);body.global_phase=p/5
    owner=body.to_gate();r=qb.QuantumRegister(1,"data")
    user_metadata={"global_phase":"user label","classical_scope":{"user":True},"registers":["note"]}
    circuit=qb.QuantumCircuit(r,qb.QuantumRegister(name="alias",bits=[r[0]]),metadata=user_metadata)
    circuit.append(owner,[r[0]],copy=False);cached=circuit.data[0]
    owner.params[0]=.7;owner.name="source_changed"
    assert circuit.data[0].operation is owner and circuit.data[0].params==[p]
    x=.3
    np.testing.assert_allclose(Operator(circuit.assign_parameters({p:x})).data,
        np.exp(1j*x/5)*rotation(2*x+np.sin(x)),atol=5e-13,rtol=0)

    replacement=qb.QuantumCircuit(1,name="replacement");replacement.ry(3*p,0);replacement.global_phase=p/5
    new_owner=replacement.to_gate();circuit.data[0]=cached.replace(operation=new_owner)
    copied=circuit.copy();inverse=circuit.inverse()
    assert type(copied) is qb.QuantumCircuit and type(inverse) is qb.QuantumCircuit
    assert len(copied.find_bit(copied.qubits[0]).registers)==2
    np.testing.assert_allclose(Operator(inverse.assign_parameters({p:x})).data,
        np.exp(-1j*x/5)*rotation(-3*x),atol=5e-13,rtol=0)
    restored=qpy_loads(qpy_dumps(copied))[0]
    restored_ir=circuit_from_ir(IRProgram.from_json(copied.to_ir().to_json()))
    for candidate in (restored,restored_ir):
        assert candidate.metadata==user_metadata
        np.testing.assert_allclose(Operator(candidate.assign_parameters({candidate.parameters[0]:x})).data,
            np.exp(1j*x/5)*rotation(3*x),atol=5e-13,rtol=0)
    other=qb.QuantumCircuit(1);other.x(0)
    tensor=copied.tensor(other);lowered=copied.decompose()
    assert type(tensor) is type(lowered) is qb.QuantumCircuit
    np.testing.assert_allclose(Operator(tensor.assign_parameters({p:x})).data,
        np.kron(np.array([[0,1],[1,0]]),np.exp(1j*x/5)*rotation(3*x)),atol=6e-13,rtol=0)
    np.testing.assert_allclose(Operator(lowered.assign_parameters({p:x})).data,
        np.exp(1j*x/5)*rotation(3*x),atol=5e-13,rtol=0)

    scalar=qb.QuantumCircuit();scalar.append(UnitaryGate([[np.exp(.3j)]]),[])
    scalar=qpy_loads(qpy_dumps(scalar))[0]
    np.testing.assert_allclose(Operator(scalar.to_gate().control()).data,
        np.diag([1,np.exp(.3j)]),atol=4e-13,rtol=0)
    for annotated in (False,True):
        base=replacement.to_gate()
        controlled=qb.AnnotatedOperation(base,qb.ControlModifier(1,0)) if annotated else base.control(ctrl_state=0)
        parent=qb.QuantumCircuit(2);parent.append(controlled,[0,1],copy=False)
        if annotated:base.params=[.7]
        else:controlled.params=[.7]
        assert parent.parameters==(p,) and parent.data[0].params==[p]
        expected=np.eye(4,dtype=complex);expected[:2,:2]=np.exp(1j*x/5)*rotation(3*x)
        for candidate in (parent,circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json())),qpy_loads(qpy_dumps(parent))[0]):
            np.testing.assert_allclose(Operator(candidate.assign_parameters({candidate.parameters[0]:x})).data,
                expected,atol=7e-13,rtol=0)
            controlled_node=QNode.from_circuit(candidate,qb.PauliZ(1),diff_method="parameter-shift",max_diff=2)
            np.testing.assert_allclose(controlled_node.compute_jacobian(x),-3*np.sin(3*x),atol=3e-10,rtol=0)
            np.testing.assert_allclose(controlled_node.compute_hvp(.7,x),-.7*9*np.cos(3*x),atol=5e-10,rtol=0)
    changed=body.to_gate();chain=qb.QuantumCircuit(1);chain.append(changed,[0],copy=False)
    definition=qb.QuantumCircuit(1,name="changed",global_phase=p/7);definition.ry(3*p,0)
    changed.definition=definition
    annotation=qb.AnnotatedOperation(chain.copy().to_gate().control(ctrl_state=0),[qb.InverseModifier(),qb.PowerModifier(2)])
    chain=qb.QuantumCircuit(2);chain.h(0);chain.append(annotation,[0,1])
    chain=qpy_loads(qpy_dumps(chain))[0]
    expected=np.eye(4,dtype=complex);expected[:2,:2]=np.exp(-2j*x/7)*rotation(-6*x)
    np.testing.assert_allclose(Operator(chain.assign_parameters({chain.parameters[0]:x})).data,
        expected@np.kron(np.array([[1,1],[1,-1]])/np.sqrt(2),np.eye(2)),atol=9e-13,rtol=0)
    chain_node=QNode.from_circuit(chain,qb.PauliX(0),diff_method="parameter-shift",max_diff=2)
    second=-(9+4/49)*np.cos(3*x)*np.cos(2*x/7)+12/7*np.sin(3*x)*np.sin(2*x/7)
    np.testing.assert_allclose(chain_node.compute_hessian(x),second,atol=8e-10,rtol=0)
    np.testing.assert_allclose(chain_node.compute_hvp(.7,x),.7*second,atol=8e-10,rtol=0)
    coherent=qb.QuantumCircuit(1,global_phase=p/5);coherent.rx(2*p,0)
    controlled=coherent.to_gate().control(2,ctrl_state="01")
    two_control=qb.QuantumCircuit(3);two_control.h(0);two_control.append(controlled,[0,1,2],copy=False)
    parameter_view=two_control.parameters;view_copy=parameter_view.copy()
    parameter_view.remove(parameter_view[0]);parameter_view.data.append(qb.Parameter("snapshot_only"))
    assert list(two_control.parameters)==[p] and list(view_copy)==[p]
    assert view_copy&{p}==[p] and view_copy|{p}=={p}
    changed_base=qb.QuantumCircuit(1);changed_base.ry(7*p,0)
    controlled.base_gate.definition=changed_base
    block=np.eye(8,dtype=complex)
    block[4:6,4:6]=np.exp(1j*x/5)*np.array([[np.cos(x),-1j*np.sin(x)],[-1j*np.sin(x),np.cos(x)]])
    expected=block@np.kron(np.array([[1,1],[1,-1]])/np.sqrt(2),np.eye(4))
    for candidate in (two_control,circuit_from_ir(IRProgram.from_json(two_control.to_ir().to_json())),qpy_loads(qpy_dumps(two_control))[0]):
        np.testing.assert_allclose(Operator(candidate.assign_parameters({candidate.parameters[0]:x})).data,
            expected,atol=2e-12,rtol=0)
        for method in ("parameter-shift","adjoint"):
            controlled_node=QNode.from_circuit(candidate,qb.PauliX(0),max_diff=2,diff_method=method)
            first=-np.sin(x)*np.cos(x/5)-.2*np.cos(x)*np.sin(x/5)
            second=-1.04*np.cos(x)*np.cos(x/5)+.4*np.sin(x)*np.sin(x/5)
            np.testing.assert_allclose(controlled_node.compute_jacobian(x),first,atol=5e-10,rtol=0)
            np.testing.assert_allclose(controlled_node.compute_hessian(x),second,atol=8e-10,rtol=0)
            np.testing.assert_allclose(controlled_node.compute_hvp(.7,x),.7*second,atol=8e-10,rtol=0)
    numeric=coherent.to_gate(parameter_map={p:x});numeric.definition.rz(.23,0)
    numeric_parent=qb.QuantumCircuit(1);numeric_parent.append(numeric,[0],copy=False)
    numeric_payload=numeric_parent.to_ir().to_dict()
    assert numeric_payload["instructions"][0]["metadata"]["gate"]["parameter_binding"]["invalidated"] is True
    numeric_restored=circuit_from_ir(IRProgram.from_dict(numeric_payload))
    np.testing.assert_allclose(Operator(numeric_restored).data,Operator(numeric_parent).data,atol=6e-13,rtol=0)
    for operation in (numeric,numeric_restored.operations[0].metadata["gate"]):
        try:operation.params=[.7]
        except ValueError:pass
        else:raise AssertionError("An invalidated numeric formal history was used for rebinding.")
    readout=qb.QuantumCircuit(2,2,name="readout",global_phase=.2)
    readout.reset(0);readout.x(0);readout.measure(0,1)
    readout_instruction=readout.to_instruction()
    parent=qb.QuantumCircuit(3,3);parent.append(readout_instruction,[2,0],[1,2],copy=False)
    readout_instruction.definition=readout.copy(name="updated_readout")
    assert readout_instruction.metadata["definition_name"]=="updated_readout"
    classical_restored=qpy_loads(qpy_dumps(parent))[0]
    for device in (qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice):
        assert device().run_shots(classical_restored,shots=3).counts()=={"001":3}
    deferred=qb.AnnotatedOperation(readout.to_instruction(),qb.InverseModifier())
    parent=qb.QuantumCircuit(2,2);parent.append(deferred,[0,1],[0,1])
    deferred_restored=qpy_loads(qpy_dumps(parent))[0]
    try:deferred_restored.lowered()
    except ValueError:pass
    else:raise AssertionError("Nonunitary annotation was executed as a unitary gate.")
    node=QNode.from_circuit(restored,qb.PauliZ(0),diff_method="parameter-shift",max_diff=2)
    restored.metadata={"global_phase":object(),"classical_scope":object(),"registers":object()}
    np.testing.assert_allclose(node(x),np.cos(3*x),atol=3e-12,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(x),-3*np.sin(3*x),atol=3e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(.7,x),-.7*9*np.cos(3*x),atol=5e-10,rtol=0)
    try:new_owner.params=[.2,.3]
    except ValueError:pass
    else:raise AssertionError("An invalid owner update was accepted.")
    assert new_owner.params==[p] and circuit.parameters==(p,)
    before=circuit.to_ir().to_json()
    try:circuit.assign_parameters({p:1j},inplace=True)
    except (TypeError,ValueError):pass
    else:raise AssertionError("A complex physical angle was accepted.")
    assert circuit.to_ir().to_json()==before

    register=qb.QuantumRegister(100,"large")
    wide=qb.QuantumCircuit(register,qb.QuantumRegister(name="last",bits=[register[-1]]))
    wide.append(new_owner,[register[-1]])
    def forbidden(*args,**kwargs):raise AssertionError("Hundred-wire MPS used a dense fallback.")
    with patch.object(qb.Gate,"to_matrix",forbidden),patch.object(qb.StatevectorDevice,"statevector",forbidden),\
            patch.object(qb.DensityMatrixDevice,"density_matrix",forbidden),patch.object(MatrixProductState,"statevector",forbidden):
        wide_node=QNode.from_circuit(wide,qb.PauliZ(99),device=qb.MatrixProductStateDevice(
            max_memory_mb=2,max_bond_dim=4,cutoff=0),diff_method="parameter-shift",max_diff=2)
        wide_gradient=float(wide_node.compute_jacobian(x));wide_hvp=float(wide_node.compute_hvp(.7,x))
        np.testing.assert_allclose(wide_node(x),np.cos(3*x),atol=3e-12,rtol=0)
        np.testing.assert_allclose(wide_gradient,-3*np.sin(3*x),atol=3e-10,rtol=0)
        np.testing.assert_allclose(wide_hvp,-.7*9*np.cos(3*x),atol=5e-10,rtol=0)
    print(json.dumps({"source_owner_changed":True,"stored_parameter_retained":True,
        "actual_data_replacement":True,"public_factories":True,"qpy_ir_numeric_roundtrip":True,
        "gradient":float(np.asarray(node.compute_jacobian(x))),"hvp":float(node.compute_hvp(.7,x)),
        "scalar_qpy_control":True,"hundred_wire_mps_no_dense":True,
        "cached_control_annotation_operator_ad_ir_qpy":True,
        "definition_mutation_open_control_annotation_qpy_hessian_hvp":True,
        "two_control_phase_ir_qpy_shift_adjoint_hessian_hvp":True,
        "public_parameter_view_snapshot_not_circuit_state":True,
        "invalidated_numeric_history_explicit_ir_atomic_rebind_refusal":True,
        "classical_instruction_qpy_four_devices":True,"deferred_nonunitary_resolution_rejected":True,
        "hundred_wire_gradient":wide_gradient,"hundred_wire_hvp":wide_hvp,
        "user_metadata_separate_from_execution":True,"opaque_userdata_ad":True,
        "failed_binding_atomic":True,"invalid_update_rejected":True,"full_sdk_parity":False},sort_keys=True))


if __name__=="__main__":main()
