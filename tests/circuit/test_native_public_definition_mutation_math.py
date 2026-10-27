# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Distinct mutable definition graphs, independent math and actual public ABI."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps,qpy_loads


MUTATIONS=("replace_root","nested_leaf","append_x","delete_rz","reverse","phase","compose_h","data_replace")
X=np.array([[0,1],[1,0]]);H=np.array([[1,1],[1,-1]])/np.sqrt(2);I=np.eye(2)
CX=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])


def rx(x):return np.array([[np.cos(x/2),-1j*np.sin(x/2)],[-1j*np.sin(x/2),np.cos(x/2)]])
def ry(x):return np.array([[np.cos(x/2),-np.sin(x/2)],[np.sin(x/2),np.cos(x/2)]])
def rz(x):return np.diag([np.exp(-.5j*x),np.exp(.5j*x)])


def oracle(mutation,x,annotated=False):
    initial=np.kron(rx(x),I);second=np.kron(rz(2*x),I);phase=x/5
    if mutation=="replace_root":matrix=np.kron(I,ry(3*x));phase=x/7
    elif mutation=="nested_leaf":matrix=CX@second@np.kron(ry(3*x),I)
    elif mutation=="append_x":matrix=np.kron(I,X)@CX@second@initial
    elif mutation=="delete_rz":matrix=CX@initial
    elif mutation=="reverse":matrix=initial@second@CX
    elif mutation=="phase":matrix=CX@second@initial;phase=x/7
    elif mutation=="compose_h":matrix=np.kron(I,H)@CX@second@initial
    elif mutation=="data_replace":matrix=CX@np.kron(I,rz(4*x))@initial
    else:matrix=CX@second@initial
    matrix=np.exp(1j*phase)*matrix
    if annotated:
        result=np.eye(8,dtype=complex);result[:4,:4]=matrix;return result
    return matrix


def build(api,kind,mutation,copy=False):
    p=api.P("p");leaf=api.QC(1,name="leaf");leaf.rx(p,0)
    body=api.QC(2,name="body",global_phase=p/5)
    body.append(leaf.to_gate(),[0]);body.rz(2*p,0);body.cx(0,1)
    base=body.to_instruction() if kind=="instruction" else body.to_gate()
    source=api.A(base,api.C(1,0)) if kind=="annotated" else base
    parent=api.QC(source.num_qubits);parent.append(source,range(source.num_qubits),copy=copy)
    if mutation=="replace_root":
        replacement=api.QC(2,name="replacement",global_phase=p/7);replacement.ry(3*p,1)
        base.definition=replacement
    elif mutation=="nested_leaf":
        replacement=api.QC(1,name="replacement_leaf");replacement.ry(3*p,0)
        base.definition.data[0].operation.definition=replacement
    elif mutation=="append_x":base.definition.x(1)
    elif mutation=="delete_rz":del base.definition.data[1]
    elif mutation=="reverse":base.definition.data=list(reversed(base.definition.data))
    elif mutation=="phase":base.definition.global_phase=p/7
    elif mutation=="compose_h":
        tail=api.QC(2);tail.h(1);base.definition.compose(tail,inplace=True,copy=False)
    elif mutation=="data_replace":
        replacement=api.QC(1);replacement.rz(4*p,0)
        base.definition.data[1]=base.definition.data[1].replace(operation=replacement.to_gate(),qubits=(base.definition.qubits[1],))
    return parent,p


def native_api():return SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter,A=qb.AnnotatedOperation,C=qb.ControlModifier)


@pytest.mark.parametrize("kind",["gate","instruction","annotated"])
@pytest.mark.parametrize("mutation",MUTATIONS)
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_distinct_definition_mutations_keep_complex_operator_parameter_index_and_real_ad(kind,mutation,transport):
    circuit,p=build(native_api(),kind,mutation)
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    assert len(circuit.parameters)==1 and circuit.parameters[0].uuid==p.uuid
    x=.37
    np.testing.assert_allclose(Operator(circuit.assign_parameters({circuit.parameters[0]:x})).data,
        oracle(mutation,x,kind=="annotated"),atol=2e-12,rtol=0)
    wire=(1 if mutation=="replace_root" else 0)+int(kind=="annotated")
    frequency=3 if mutation in {"replace_root","nested_leaf"} else 1
    node=QNode.from_circuit(circuit,qb.PauliZ(wire),diff_method="parameter-shift",max_diff=2)
    assert node(x)==pytest.approx(np.cos(frequency*x),abs=3e-12)
    assert node.compute_jacobian(x)==pytest.approx(-frequency*np.sin(frequency*x),abs=4e-10)
    assert node.compute_hessian(x)==pytest.approx(-frequency**2*np.cos(frequency*x),abs=6e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(-.7*frequency**2*np.cos(frequency*x),abs=6e-10)


@pytest.mark.parametrize("kind",["gate","instruction","annotated"])
@pytest.mark.parametrize("mutation",MUTATIONS)
@pytest.mark.parametrize("copy",[False,True])
def test_actual_public_definition_graph_mutation_math_and_copy_isolation(kind,mutation,copy,record_property):
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter,AnnotatedOperation,ControlModifier
    from qiskit.quantum_info import Operator as PublicOperator
    api=SimpleNamespace(QC=public.QuantumCircuit,P=Parameter,A=AnnotatedOperation,C=ControlModifier)
    actual=[]
    for a,operator in ((native_api(),Operator),(api,PublicOperator)):
        circuit,p=build(a,kind,mutation,copy)
        assert tuple(value.name for value in circuit.parameters)==("p",)
        matrix=operator(circuit.assign_parameters({p:.37})).data
        if a is api:
            width=circuit.num_qubits;order=[int(format(index,"0"+str(width)+"b")[::-1],2) for index in range(1<<width)]
            matrix=matrix[np.ix_(order,order)]
        actual.append(matrix)
    expected=oracle("unchanged" if copy else mutation,.37,kind=="annotated")
    np.testing.assert_allclose(actual[0],expected,atol=2e-12,rtol=0)
    np.testing.assert_allclose(actual[1],expected,atol=2e-12,rtol=0)
    record_property("contract","MATCH")


def mutation_control_annotation_chain(width=2):
    p=qb.ParameterVector("chain",1)[0]
    body=qb.QuantumCircuit(1,name="initial",global_phase=p/5);body.rx(p,0)
    source=body.to_gate();parent=qb.QuantumCircuit(1);parent.append(source,[0],copy=False)
    replacement=qb.QuantumCircuit(1,name="replacement",global_phase=p/7);replacement.ry(3*p,0)
    source.definition=replacement
    owned=parent.copy().to_gate().control(ctrl_state=0)
    annotation=qb.AnnotatedOperation(owned,[qb.InverseModifier(),qb.PowerModifier(2)])
    result=qb.QuantumCircuit(width);result.h(0);result.append(annotation,[0,width-1])
    return result,p


def chain_second(x):
    k=2/7
    return -(9+k*k)*np.cos(3*x)*np.cos(k*x)+6*k*np.sin(3*x)*np.sin(k*x)


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_replaced_definition_copy_open_control_ordered_annotation_transport_and_native_hessian(transport):
    circuit,p=mutation_control_annotation_chain()
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    assert len(circuit.parameters)==1 and circuit.parameters[0].uuid==p.uuid
    x=.37;block=np.eye(4,dtype=complex);block[:2,:2]=np.exp(-2j*x/7)*ry(-6*x)
    np.testing.assert_allclose(Operator(circuit.assign_parameters({circuit.parameters[0]:x})).data,
        block@np.kron(H,I),atol=3e-12,rtol=0)
    node=QNode.from_circuit(circuit,qb.PauliX(0),diff_method="parameter-shift",max_diff=2)
    assert node(x)==pytest.approx(np.cos(3*x)*np.cos(2*x/7),abs=4e-12)
    assert node.compute_jacobian(x)==pytest.approx(-3*np.sin(3*x)*np.cos(2*x/7)-2/7*np.cos(3*x)*np.sin(2*x/7),abs=6e-10)
    assert node.compute_hessian(x)==pytest.approx(chain_second(x),abs=8e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*chain_second(x),abs=8e-10)


@pytest.mark.parametrize("transport",["ir","qpy"])
def test_replaced_definition_control_annotation_chain_on_hundred_wire_mps_has_no_dense_escape(transport,monkeypatch):
    from quantumbridge.information.matrix_product_state import MatrixProductState
    circuit,p=mutation_control_annotation_chain(100)
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    else:circuit=qpy_loads(qpy_dumps(circuit))[0]
    def forbidden(*args,**kwargs):pytest.fail("mutated control/annotation used a dense escape")
    for cls,name in ((qb.Gate,"to_matrix"),(qb.StatevectorDevice,"statevector"),
            (qb.DensityMatrixDevice,"density_matrix"),(MatrixProductState,"statevector")):
        monkeypatch.setattr(cls,name,forbidden)
    node=QNode.from_circuit(circuit,qb.PauliX(0),diff_method="parameter-shift",max_diff=2,
        device=qb.MatrixProductStateDevice(max_memory_mb=2,max_bond_dim=4,cutoff=0))
    x=.37
    assert node(x)==pytest.approx(np.cos(3*x)*np.cos(2*x/7),abs=4e-12)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*chain_second(x),abs=8e-10)


@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
def test_replaced_definition_control_annotation_has_actual_framework_second_derivative(framework):
    module=pytest.importorskip(framework);circuit,_=mutation_control_annotation_chain();x=.37
    node=QNode.from_circuit(circuit,qb.PauliX(0),interface=framework,diff_method="parameter-shift",max_diff=2)
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
    assert actual==pytest.approx(chain_second(x),abs=8e-10)


def test_mutated_definition_portable_failure_does_not_write_partial_output_or_mutate_source():
    import io
    from quantumbridge.serialization import qpy_dump,UnsupportedFeature
    circuit,_=mutation_control_annotation_chain()
    circuit.metadata={"foreign":object()};before=circuit.parameters
    output=io.BytesIO(b"unchanged");output.seek(0)
    with pytest.raises(UnsupportedFeature):qpy_dump(circuit,output)
    assert output.getvalue()==b"unchanged" and circuit.parameters==before


@pytest.mark.parametrize("corruption",["cycle","width","work"])
def test_mutated_public_definition_graph_is_admitted_before_circuit_copy(corruption,monkeypatch):
    from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
    import quantumbridge.execution.array_ownership as arrays
    body=qb.QuantumCircuit(1);body.ry(.2,0);owner=body.to_gate()
    circuit=qb.QuantumCircuit(1);circuit.append(owner,[0],copy=False)
    if corruption=="cycle":owner.definition.operations.append(circuit.operations[0])
    elif corruption=="width":object.__setattr__(owner.definition,"num_qubits",2)
    else:
        for _ in range(6):owner.definition.x(0)
    monkeypatch.setattr(arrays,"native_configuration_copy",lambda *a,**kw:pytest.fail("unadmitted definition copied"))
    limit=5 if corruption=="work" else 1000000
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=limit)):
        with pytest.raises(MemoryError if corruption=="work" else ValueError):circuit.copy()


@pytest.mark.parametrize("annotated",[False,True])
def test_mutated_control_base_cycle_is_admitted_before_public_circuit_copy(annotated,monkeypatch):
    import quantumbridge.execution.array_ownership as arrays
    body=qb.QuantumCircuit(1);body.ry(.2,0);owner=body.to_gate().control(ctrl_state=0)
    operation=qb.AnnotatedOperation(owner,qb.InverseModifier()) if annotated else owner
    circuit=qb.QuantumCircuit(2);circuit.append(operation,[0,1],copy=False)
    object.__setattr__(owner,"base_gate",owner)
    monkeypatch.setattr(arrays,"native_configuration_copy",lambda *a,**kw:pytest.fail("cyclic control base copied"))
    with pytest.raises(ValueError,match="Cyclic"):circuit.copy()
