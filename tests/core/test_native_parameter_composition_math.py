# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent full-complex parameterized circuit/instruction algebra."""

from itertools import product

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter
from quantumbridge.execution import UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


VALUES=[(.2,-.3),(-.7,.5),(.8,1.1)]
EXPRESSIONS=[
    (lambda p,q:p+q,lambda p,q:p+q),
    (lambda p,q:p-q,lambda p,q:p-q),
    (lambda p,q:p*q,lambda p,q:p*q),
    (lambda p,q:(p+q)/2,lambda p,q:(p+q)/2),
    (lambda p,q:p**2+q**3,lambda p,q:p*p+q*q*q),
    (lambda p,q:(p-q)*(p+q),lambda p,q:p*p-q*q),
    (lambda p,q:p/(2+q),lambda p,q:p/(2+q)),
    (lambda p,q:-p+3*q,lambda p,q:3*q-p),
    (lambda p,q:2**p/3,lambda p,q:np.exp(np.log(2)*p)/3),
    (lambda p,q:(p+q)**2/(3-p*q),lambda p,q:(p*p+2*p*q+q*q)/(3-p*q)),
]
CX=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)


def rotation(axis,angle):
    c,s=np.cos(angle/2),np.sin(angle/2)
    if axis=="x":return np.array([[c,-1j*s],[-1j*s,c]])
    if axis=="y":return np.array([[c,-s],[s,c]],complex)
    return np.diag([np.exp(-.5j*angle),np.exp(.5j*angle)])


def dense_reference(sequence,width,phase):
    """Independent basis enumeration and matrix products."""
    result=np.eye(1<<width,dtype=complex)
    for gate,wires in sequence:
        embedded=np.zeros_like(result)
        for column,bits in enumerate(product((0,1),repeat=width)):
            local=sum(bits[wire]*(1<<(len(wires)-1-position)) for position,wire in enumerate(wires))
            for index,replacement in enumerate(product((0,1),repeat=len(wires))):
                output=list(bits)
                for wire,bit in zip(wires,replacement):output[wire]=bit
                row=sum(bit*(1<<(width-1-position)) for position,bit in enumerate(output))
                embedded[row,column]=gate[index,local]
        result=embedded@result
    return np.exp(1j*phase)*result


def contract_gate(tensor,gate,axes):
    """Local tensor action without a full-system operator."""
    count=len(axes)
    output=np.tensordot(gate.reshape((2,)*(2*count)),tensor,
        axes=(tuple(range(count,2*count)),axes))
    order=axes+tuple(axis for axis in range(tensor.ndim) if axis not in axes)
    return output.transpose(tuple(order.index(axis) for axis in range(tensor.ndim)))


def state_reference(source,sequence,width,phase):
    tensor=source.reshape((2,)*width)
    for gate,wires in sequence:tensor=contract_gate(tensor,gate,wires)
    return np.exp(1j*phase)*tensor.reshape(-1)


def density_reference(source,sequence,width):
    tensor=source.reshape((2,)*(2*width))
    for gate,wires in sequence:
        tensor=contract_gate(tensor,gate,wires)
        tensor=contract_gate(tensor,gate.conj(),tuple(wire+width for wire in wires))
    return tensor.reshape(source.shape)


def source(width):
    indices=np.arange(1,(1<<width)+1)
    first=np.cos(indices)+1j*np.sin(2*indices)
    first/=np.linalg.norm(first)
    second=np.sin(3*indices)+1j*np.cos(2*indices)
    second/=np.linalg.norm(second)
    return first,.3*np.outer(first,first.conj())+.7*np.outer(second,second.conj())


def child(p,q):
    circuit=Circuit(2).rx(p+q,0).ry(p*q,1).cx(0,1).rz(q,0)
    circuit.global_phase=p/7
    return circuit


def child_reference(p,q,wires):
    return [(rotation("x",p+q),(wires[0],)),(rotation("y",p*q),(wires[1],)),
        (CX,wires),(rotation("z",q),(wires[0],))]


@pytest.mark.parametrize("pvalue,qvalue",VALUES)
@pytest.mark.parametrize("expression,numeric",EXPRESSIONS)
def test_ten_distinct_expression_algebras_bind_and_execute_with_two_oracles(expression,numeric,pvalue,qvalue):
    p,q=Parameter("p"),Parameter("q")
    circuit=Circuit(2).rx(expression(p,q),0).ry(p*q,1).cx(0,1).rz(q,0)
    circuit.global_phase=p/7
    before=circuit.to_ir().to_dict()
    partial=circuit.assign_parameters({p:pvalue})
    bound=partial.assign_parameters({q:qvalue},strict=False)
    expected=[(rotation("x",numeric(pvalue,qvalue)),(0,)),(rotation("y",pvalue*qvalue),(1,)),
        (CX,(0,1)),(rotation("z",qvalue),(0,))]
    dense=dense_reference(expected,2,pvalue/7)
    initial,mixed=source(2)
    vector=state_reference(initial,expected,2,pvalue/7)
    density=density_reference(mixed,expected,2)
    np.testing.assert_allclose(dense@initial,vector,atol=4e-15,rtol=0)
    np.testing.assert_allclose(dense@mixed@dense.conj().T,density,atol=5e-15,rtol=0)
    with ResourceScope(Ledger()):
        operator=Operator(bound)
        state=Statevector(initial).evolve(bound.to_instruction())
        result=DensityMatrix(mixed).evolve(bound.to_instruction())
    np.testing.assert_allclose(operator.data,dense,atol=5e-15,rtol=0)
    np.testing.assert_allclose(state.data,vector,atol=5e-15,rtol=0)
    np.testing.assert_allclose(result.data,density,atol=6e-15,rtol=0)
    assert circuit.to_ir().to_dict()==before


COMPOSITES=["plain","nested","reuse_same","reuse_overlapping","copy","parameter_map","partially_bound","phase_only"]


def composite_case(kind,pvalue,qvalue):
    p,q=Parameter("p"),Parameter("q")
    sub=child(p,q)
    original=sub.to_ir().to_dict()
    parent=Circuit(3)
    mapping={p:pvalue,q:qvalue}
    if kind=="phase_only":
        sub=Circuit(2);sub.global_phase=p/7
        parent.append(sub.to_instruction(),(2,0))
        mapping={p:pvalue}
        sequence=[];phase=pvalue/7
    elif kind=="parameter_map":
        target=Parameter("target")
        instruction=sub.to_instruction(parameter_map={p:2*target,q:target*target})
        parent.append(instruction,(2,0))
        mapping={target:pvalue}
        sequence=child_reference(2*pvalue,pvalue*pvalue,(2,0));phase=2*pvalue/7
    elif kind=="partially_bound":
        parent.append(sub.assign_parameters({p:.3}).to_instruction(),(2,0))
        mapping={q:qvalue}
        sequence=child_reference(.3,qvalue,(2,0));phase=.3/7
    elif kind=="nested":
        inner=Circuit(2).append(sub.to_instruction(),(1,0))
        inner.rz(p*q,0)
        parent.append(inner.to_instruction(),(2,0))
        sequence=child_reference(pvalue,qvalue,(0,2))+[(rotation("z",pvalue*qvalue),(2,))]
        phase=pvalue/7
    else:
        instruction=sub.to_instruction()
        parent.append(instruction,(2,0))
        sequence=child_reference(pvalue,qvalue,(2,0));phase=pvalue/7
        if kind in {"reuse_same","reuse_overlapping"}:
            wires=(2,0) if kind=="reuse_same" else (0,1)
            parent.append(instruction,wires)
            sequence+=child_reference(pvalue,qvalue,wires);phase*=2
        if kind=="copy":parent=parent.copy()
    if kind!="phase_only":assert sub.to_ir().to_dict()==original
    return parent,mapping,sequence,phase


@pytest.mark.parametrize("kind",COMPOSITES)
@pytest.mark.parametrize("pvalue,qvalue",VALUES)
def test_eight_composite_identity_reuse_and_mapping_scenarios(kind,pvalue,qvalue):
    circuit,mapping,sequence,phase=composite_case(kind,pvalue,qvalue)
    before=circuit.to_ir().to_dict()
    bound=circuit.assign_parameters(mapping)
    expected=dense_reference(sequence,3,phase)
    initial,mixed=source(3)
    vector=state_reference(initial,sequence,3,phase)
    density=density_reference(mixed,sequence,3)
    with ResourceScope(Ledger()):
        actual=Operator(bound)
        evolved=Statevector(initial).evolve(bound.to_instruction())
        result=DensityMatrix(mixed).evolve(bound.to_instruction())
    np.testing.assert_allclose(actual.data,expected,atol=6e-15,rtol=0)
    np.testing.assert_allclose(evolved.data,vector,atol=6e-15,rtol=0)
    np.testing.assert_allclose(result.data,density,atol=7e-15,rtol=0)
    np.testing.assert_allclose(expected@mixed@expected.conj().T,density,atol=6e-15,rtol=0)
    assert circuit.to_ir().to_dict()==before


STRUCTURES=["compose_back","compose_front","inverse","power_negative","power_zero","power_positive"]


@pytest.mark.parametrize("kind",STRUCTURES)
@pytest.mark.parametrize("pvalue,qvalue",VALUES)
def test_six_existing_structural_operations_keep_parameter_and_phase_algebra(kind,pvalue,qvalue):
    p,q=Parameter("p"),Parameter("q")
    first=child(p,q)
    u=dense_reference(child_reference(pvalue,qvalue,(0,1)),2,pvalue/7)
    other=Circuit(2).h(1).rx(q-p,0).cx(1,0).rz(p*q,1)
    other.global_phase=q/5
    v=dense_reference([(H,(1,)),(rotation("x",qvalue-pvalue),(0,)),(CX,(1,0)),(rotation("z",pvalue*qvalue),(1,))],2,qvalue/5)
    if kind=="compose_back":result,expected=first.compose(other),v@u
    elif kind=="compose_front":result,expected=first.compose(other,front=True),u@v
    elif kind=="inverse":result,expected=first.inverse(),u.conj().T
    elif kind=="power_negative":result,expected=first.power(-2),u.conj().T@u.conj().T
    elif kind=="power_zero":result,expected=first.power(0),np.eye(4,dtype=complex)
    else:result,expected=first.power(3),u@u@u
    mapping={parameter:value for parameter,value in ((p,pvalue),(q,qvalue)) if parameter in result.parameters}
    actual=Operator(result.assign_parameters(mapping))
    np.testing.assert_allclose(actual.data,expected,atol=8e-15,rtol=0)
    np.testing.assert_allclose(Operator(first.bind({p:pvalue,q:qvalue})).data,u,atol=4e-15,rtol=0)


@pytest.mark.parametrize("pvalue,qvalue",VALUES)
def test_two_real_parameterized_chains_end_in_complex_expectation_and_mixed_purity(pvalue,qvalue):
    p,q=Parameter("p"),Parameter("q")
    circuit=child(p,q)
    bound=circuit.assign_parameters({p:pvalue}).assign_parameters({q:qvalue})
    initial,_=source(2)
    sequence=child_reference(pvalue,qvalue,(0,1))
    expected=state_reference(initial,sequence,2,pvalue/7)
    observable=np.diag([1.,-2.,.5,3.])+1j*np.eye(4,k=1)
    with ResourceScope(Ledger()):
        state=Statevector(initial).evolve(Operator(bound))
        expectation=state.expectation_value(Operator(observable))
    assert expectation==pytest.approx(expected.conj()@observable@expected,abs=1e-14)
    parent=Circuit(3).append(circuit.to_instruction(),(2,0)).append(circuit.to_instruction(),(0,1))
    initial3,mixed=source(3)
    gates=child_reference(pvalue,qvalue,(2,0))+child_reference(pvalue,qvalue,(0,1))
    expected_density=density_reference(mixed,gates,3)
    tensor=expected_density.reshape((2,)*6)
    reduced_reference=np.trace(tensor,axis1=1,axis2=4).reshape(4,4)
    with ResourceScope(Ledger()):
        density=DensityMatrix(mixed).evolve(parent.bind({p:pvalue,q:qvalue}).to_instruction())
        reduced=density.partial_trace([2,0])
        purity=reduced.purity()
        expectation_b=reduced.expectation_value(Operator(np.diag([1.,-2.,.5,3.])))
    np.testing.assert_allclose(density.data,expected_density,atol=7e-15,rtol=0)
    np.testing.assert_allclose(reduced.data,reduced_reference,atol=7e-15,rtol=0)
    assert purity==pytest.approx(np.trace(reduced_reference@reduced_reference),abs=1e-14)
    assert expectation_b==pytest.approx(np.trace(reduced_reference@np.diag([1.,-2.,.5,3.])),abs=1e-14)


@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
@pytest.mark.parametrize("pvalue,qvalue",VALUES)
def test_shared_nonlinear_binding_composes_with_existing_native_derivative_execution(method,pvalue,qvalue):
    from quantumbridge import PauliZ
    from quantumbridge.qml import QNode
    p,q=Parameter("p"),Parameter("q")
    circuit=Circuit(2).rx(p*q+p*p,0).ry(2*p+q,0).cx(0,1).rz(p*q,1)
    circuit.global_phase=p*p/3
    node=QNode.from_circuit(circuit,PauliZ(0),diff_method=method,max_diff=2)
    point=np.array([pvalue,qvalue])
    a,b=pvalue*qvalue+pvalue*pvalue,2*pvalue+qvalue
    ga,gb=np.array([qvalue+2*pvalue,pvalue]),np.array([2.,1.])
    expected=np.cos(a)*np.cos(b)
    gradient=-np.sin(a)*np.cos(b)*ga-np.cos(a)*np.sin(b)*gb
    hessian=(-np.cos(a)*np.cos(b)*(np.outer(ga,ga)+np.outer(gb,gb))
        +np.sin(a)*np.sin(b)*(np.outer(ga,gb)+np.outer(gb,ga))
        -np.sin(a)*np.cos(b)*np.array([[2.,1.],[1.,0.]]))
    assert node(point)==pytest.approx(expected,abs=2e-14)
    np.testing.assert_allclose(node.compute_jacobian(point),gradient,atol=2e-11,rtol=0)
    step=1e-6
    finite=[]
    for axis in range(2):
        shift=np.eye(2)[axis]*step
        finite.append((node(point+shift)-node(point-shift))/(2*step))
    np.testing.assert_allclose(gradient,finite,atol=3e-9,rtol=0)
    partial=circuit.assign_parameters({p:pvalue})
    reduced_node=QNode.from_circuit(partial,PauliZ(0),diff_method=method)
    assert reduced_node(qvalue)==pytest.approx(expected,abs=2e-14)
    assert reduced_node.compute_jacobian(qvalue)==pytest.approx(gradient[1],abs=2e-11)
    tangent=np.array([.4,-.2])
    np.testing.assert_allclose(node.compute_hvp(tangent,point),hessian@tangent,atol=2e-10,rtol=0)


@pytest.mark.parametrize("value",[.2,-.7,.8])
def test_compiled_internal_parameter_identity_replacement_preserves_symbolic_phase(value):
    from quantumbridge.diff.compiled_parameters import record_compiled_parameters
    from quantumbridge.diff.qnode_engine import AngleRecorder
    original=AngleRecorder()
    parameter=original(value)
    circuit=Circuit(1).rx(parameter,0).ry(2*parameter,0)
    circuit.global_phase=parameter/3
    compiled,recorder=record_compiled_parameters(circuit,original)
    assert set(compiled.parameters)==set(recorder.parameters)
    assert set(compiled.parameters).isdisjoint(original.parameters)
    mapping=dict(zip(recorder.parameters,recorder.native_values()))
    actual=Operator(compiled.bind(mapping)).data
    expected=np.exp(1j*value/3)*rotation("y",2*value)@rotation("x",value)
    np.testing.assert_allclose(actual,expected,atol=3e-15,rtol=0)
    assert circuit.parameters==(parameter,)
