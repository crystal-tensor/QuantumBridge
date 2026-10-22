# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Parameter identity, ordered vector binding and real composite execution."""

from copy import deepcopy
from uuid import UUID

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, ParameterVector
from quantumbridge.information import Operator, Statevector


def test_scalar_identity_is_not_just_a_name_and_copies_preserve_identity():
    first,second=Parameter("angle"),Parameter("angle")
    assert first!=second
    assert len({first,second})==2
    assert first.uuid!=second.uuid
    assert str(UUID(str(first.uuid)))==str(first.uuid)
    assert deepcopy(first)==first
    assert Parameter(first.name,str(first.uuid))==first


def test_equal_uuid_different_name_is_not_the_same_parameter():
    uid="12345678-1234-5678-1234-567812345678"
    assert Parameter("a",uid)==Parameter("a",uid)
    assert Parameter("a",uid)!=Parameter("b",uid)


def test_wrong_same_name_object_cannot_bind_a_different_circuit_parameter():
    parameter,other=Parameter("angle"),Parameter("angle")
    circuit=Circuit(1).ry(parameter,0)
    with pytest.raises(ValueError):circuit.assign_parameters({other:.7})
    unchanged=circuit.assign_parameters({other:.7},strict=False)
    assert unchanged.parameters==(parameter,)
    np.testing.assert_allclose(Operator(unchanged.bind({parameter:.3})).data,Operator(circuit.bind({parameter:.3})).data,atol=1e-15,rtol=0)


def test_vector_natural_index_order_and_sequence_binding():
    vector=ParameterVector("angles",12)
    circuit=Circuit(1)
    for index,parameter in enumerate(vector):
        getattr(circuit,("rx","ry","rz")[index%3])(parameter,0)
    assert circuit.parameters==tuple(vector)
    values=[.07*(index+1) for index in range(12)]
    bound=circuit.assign_parameters(values)
    np.testing.assert_array_equal([op.params[0] for op in bound.operations],values)
    state=np.array([1,0],complex)
    for index,angle in enumerate(values):
        c,s=np.cos(angle/2),np.sin(angle/2)
        matrix=(np.array([[c,-1j*s],[-1j*s,c]]) if index%3==0 else
            np.array([[c,-s],[s,c]]) if index%3==1 else np.diag([np.exp(-.5j*angle),np.exp(.5j*angle)]))
        state=matrix@state
    np.testing.assert_allclose(Statevector(bound).data,state,atol=3e-15,rtol=0)


def test_vector_binding_by_container_and_resize_identity():
    vector=ParameterVector("angles",12)
    circuit=Circuit(1)
    for parameter in vector:circuit.ry(parameter,0)
    bound=circuit.assign_parameters({vector:list(range(12))})
    assert [op.params[0] for op in bound.operations]==list(range(12))
    original=vector[11]
    vector.resize(3)
    vector.resize(12)
    assert vector[11]==original and vector[11].uuid==original.uuid
    assert vector[11].index==11 and vector[11].vector is vector


def test_distinct_vectors_do_not_share_parameter_identities():
    first,second=ParameterVector("angles",3),ParameterVector("angles",3)
    assert set(first).isdisjoint(second)


def test_partial_assignment_is_distinct_from_strict_numeric_binding():
    first,second=Parameter("a"),Parameter("b")
    circuit=Circuit(2).rx(first+second,0).ry(second*second,1)
    circuit.global_phase=first/3
    partial=circuit.assign_parameters({first:.2})
    assert partial.parameters==(second,)
    assert circuit.parameters==(first,second)
    bound=partial.assign_parameters({second:-.3})
    assert bound.parameters==()
    np.testing.assert_allclose(Operator(bound).data,Operator(circuit.bind({first:.2,second:-.3})).data,atol=2e-15,rtol=0)
    assert circuit.assign_parameters({}).parameters==circuit.parameters
    with pytest.raises(ValueError):circuit.bind({first:.2})


def test_symbolic_substitution_is_simultaneous_and_remains_bindable():
    first,second=Parameter("a"),Parameter("b")
    circuit=Circuit(1).rx(first+second,0).ry(first*second,0)
    renamed=circuit.assign_parameters({first:second,second:first})
    bound=renamed.assign_parameters({first:.2,second:-.3})
    np.testing.assert_allclose(Operator(bound).data,Operator(circuit.bind({first:-.3,second:.2})).data,atol=2e-15,rtol=0)
    expression=circuit.assign_parameters({first:2*second})
    assert expression.parameters==(second,)
    values=expression.assign_parameters({second:.4})
    np.testing.assert_allclose(Operator(values).data,Operator(circuit.bind({first:.8,second:.4})).data,atol=2e-15,rtol=0)


def test_failed_inplace_binding_cannot_install_an_opaque_gate_parameter():
    first,second=Parameter("a"),Parameter("b")
    circuit=Circuit(1).rx(first,0).ry(second,0)
    before=circuit.to_ir().to_dict()
    with pytest.raises((TypeError,ValueError)):circuit.assign_parameters({first:.2,second:object()},inplace=True)
    assert circuit.to_ir().to_dict()==before
    assert circuit.bind({first:.2,second:.3}).parameters==()


def test_parameterized_instruction_exposes_its_actual_parameters_and_full_map():
    first,second,target=Parameter("a"),Parameter("b"),Parameter("target")
    child=Circuit(2).rx(first+second,0).ry(second*second,1)
    child.global_phase=first/3
    instruction=child.to_instruction()
    assert instruction.params==child.parameters
    mapped=child.to_instruction(parameter_map={first:2*target,second:target})
    parent=Circuit(3).append(mapped,(2,0)).append(mapped,(0,2))
    assert parent.parameters==(target,)
    for value in (.2,-.3,.7):
        native=parent.assign_parameters({target:value})
        direct=Circuit(3).compose(child.bind({first:2*value,second:value}),qubits=(2,0)).compose(child.bind({first:2*value,second:value}),qubits=(0,2))
        np.testing.assert_allclose(Operator(native).data,Operator(direct).data,atol=4e-15,rtol=0)
    assert child.parameters==(first,second)


def test_ir_vector_roundtrip_keeps_vector_order_and_object_key_binding():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    vector=ParameterVector("angles",12)
    circuit=Circuit(1)
    for index,parameter in enumerate(vector):getattr(circuit,("rx","ry")[index%2])(parameter,0)
    restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert restored.parameters==tuple(vector)
    assert all(parameter.vector is restored.parameters[0].vector for parameter in restored.parameters)
    values=[.03*(index+1) for index in range(12)]
    np.testing.assert_allclose(Operator(restored.assign_parameters({vector:values})).data,Operator(circuit.assign_parameters(values)).data,atol=3e-15,rtol=0)


def test_ir_parameterized_composite_provenance_is_executable_not_an_opaque_object():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    parameter=Parameter("angle")
    child=Circuit(2).ry(parameter,0).cx(0,1)
    parent=Circuit(3).append(child.to_instruction(),(2,0))
    restored=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    assert restored.parameters==(parameter,)
    np.testing.assert_allclose(Operator(restored.bind({parameter:.2})).data,Operator(parent.bind({parameter:.2})).data,atol=2e-15,rtol=0)


def test_ir_loop_local_parameter_identity_stays_local_and_executes():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.information import DensityMatrix
    from quantumbridge.ir.qb_ir import IRProgram
    parameter=Parameter("loop_angle")
    body=Circuit(1).ry(.2*parameter,0)
    parent=Circuit(1).for_loop([1,2],parameter,body)
    restored=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    assert restored.parameters==parent.parameters==()
    state=np.array([np.cos(.3),np.sin(.3)])
    np.testing.assert_allclose(DensityMatrix.from_circuit(restored).data,np.outer(state,state),atol=2e-15,rtol=0)


def test_early_name_collision_is_atomic_but_copied_identity_can_be_shared():
    first,second=Parameter("angle"),Parameter("angle")
    circuit=Circuit(1).rx(first,0)
    before=circuit.to_ir().to_dict()
    with pytest.raises(ValueError,match="identities"):circuit.ry(second,0)
    assert circuit.to_ir().to_dict()==before
    circuit.ry(deepcopy(first),0)
    assert circuit.parameters==(first,)


def test_ir_vector_element_loop_parameter_keeps_type_locality_and_execution():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.information import DensityMatrix
    from quantumbridge.ir.qb_ir import IRProgram
    vector=ParameterVector("angles",2)
    body=Circuit(1).rx(.2*vector[0],0).ry(vector[1],0)
    parent=Circuit(1).for_loop([1,2],vector[0],body)
    restored=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    assert restored.parameters==parent.parameters==(vector[1],)
    loop=restored.operations[0].metadata["control_node"]
    assert type(loop.data["parameter"]) is type(vector[0])
    assert loop.data["parameter"]==vector[0]
    for angle in (.2,-.3,.7):
        initial=np.array([1,0],complex)
        c,s=np.cos(angle/2),np.sin(angle/2)
        ry=np.array([[c,-s],[s,c]],complex)
        expected=initial
        for local in (1,2):
            c,s=np.cos(.1*local),np.sin(.1*local)
            expected=ry@np.array([[c,-1j*s],[-1j*s,c]])@expected
        actual=DensityMatrix.from_circuit(restored.bind({vector[1]:angle})).data
        np.testing.assert_allclose(actual,np.outer(expected,expected.conj()),atol=3e-15,rtol=0)
