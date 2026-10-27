# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent derived-matrix mathematics and standard QPY transport."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gates import Gate
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.information import Operator,Statevector
from quantumbridge.serialization import qpy_dumps,qpy_loads


def matrix(width):
    rng = np.random.default_rng(92177+width)
    size = 1<<width
    value,_ = np.linalg.qr(rng.normal(size=(size,size))+1j*rng.normal(size=(size,size)))
    return np.asarray(value,dtype=np.complex128)


def reverse_local(value,width):
    order = [int(f"{i:0{width}b}"[::-1],2) for i in range(1<<width)]
    return value[np.ix_(order,order)]


def embed(value,wires,width):
    result = np.zeros((1<<width,1<<width),complex)
    for column in range(1<<width):
        source = [int(b) for b in f"{column:0{width}b}"]
        local = int(''.join(str(source[wire]) for wire in wires),2)
        for row in range(1<<len(wires)):
            target = source.copy()
            for wire,bit in zip(wires,f"{row:0{len(wires)}b}"): target[wire]=int(bit)
            result[int(''.join(map(str,target)),2),column] = value[row,local]
    return result


def primitive_case(width,variant):
    U=matrix(width)
    body=qb.Circuit(width,name="primitive").unitary(U,range(width))
    body.global_phase=.17
    owner=body.to_gate(label="source")
    base=np.exp(.17j)*U
    if variant=="inverse": derived,local=owner.inverse(),base.conj().T
    elif variant=="double_inverse": derived,local=owner.inverse().inverse(),base
    elif variant=="copy_inverse": derived,local=owner.copy().inverse(),base.conj().T
    elif variant=="repeat_inverse": derived,local=owner.repeat(2).inverse(),np.linalg.matrix_power(base,2).conj().T
    else: raise AssertionError(variant)
    wires=(2,) if width==1 else (2,0)
    source=qb.Circuit(3).h(1).append(derived,wires)
    source.global_phase=.23
    H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    expected=np.exp(.23j)*embed(local,wires,3)@embed(H,(1,),3)
    return owner,source,expected


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("variant",["inverse","double_inverse","copy_inverse","repeat_inverse"])
def test_primitive_matrix_derived_qpy_retains_full_native_math_and_source(width,variant):
    original,source,expected=primitive_case(width,variant)
    original_record=original.definition.to_ir().to_json()
    original_matrix=original.definition.operations[0].metadata["matrix"].copy()
    before=source.to_ir().to_json()
    np.testing.assert_allclose(Operator(source).data,expected,atol=3e-14,rtol=0)
    payload=qpy_dumps(source,version=13)
    assert payload.startswith(b"QISKIT\r") and b"UnitaryGate" in payload
    assert b"inverse_of" not in payload
    restored=qpy_loads(payload)[0]
    np.testing.assert_allclose(Operator(restored).data,expected,atol=3e-14,rtol=0)
    value=np.arange(1,9)+1j*np.arange(8,0,-1)
    value=value/np.linalg.norm(value)
    np.testing.assert_allclose(Statevector(value).evolve(restored).data,expected@value,atol=3e-14,rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(initial_state=value,cutoff=0).statevector(restored),expected@value,atol=3e-14,rtol=0)
    assert source.to_ir().to_json()==before
    np.testing.assert_array_equal(original.definition.operations[0].metadata["matrix"],original_matrix)
    assert original.definition.to_ir().to_json()==original_record
    assert original.label=="source" and original.name=="primitive" and original.metadata=={}


def acyclic_definition_graph(owner):
    """Inspect owned source edges, never execution snapshots or integer-only paths."""
    nodes,edges={},[]
    def visit(value,active):
        assert not any(value is prior for prior in active),"source object graph has a real cycle"
        nodes[id(value)]=value
        if type(value) is UnitaryGate: return
        if type(value) is Gate:
            child=object.__getattribute__(value,"_definition")
            if child is not None:
                edges.append((id(value),id(child)));visit(child,active+(value,))
        elif type(value) in (qb.Circuit,qb.QuantumCircuit):
            for operation in value.operations:
                child=operation.metadata.get("gate")
                if child is not None:
                    edges.append((id(value),id(child)));visit(child,active+(value,))
        else: raise AssertionError(type(value))
    visit(owner,())
    return nodes,edges


@pytest.mark.parametrize("width",[1,2])
def test_public_matrix_owner_repeat_accepts_proven_acyclic_definitions(width):
    U=matrix(width)
    body=qb.QuantumCircuit(width)
    body.unitary(U,range(width))
    owner=body.to_gate()
    nodes,edges=acyclic_definition_graph(owner)
    assert len(nodes)>=3 and len(edges)>=2
    expected=reverse_local(U,width)
    # Repeated validation must be independent of temporary snapshot allocation IDs.
    for _ in range(24):
        repeated=owner.repeat(2)
        np.testing.assert_allclose(repeated.to_matrix(),expected@expected,atol=3e-14,rtol=0)
        np.testing.assert_allclose(repeated.inverse().to_matrix(),(expected@expected).conj().T,atol=3e-14,rtol=0)
    assert acyclic_definition_graph(owner)[1]==edges


@pytest.mark.parametrize("width",[1,2])
def test_already_supported_raw_unitary_inverse_qpy_remains_standard(width):
    U=matrix(width)
    owner=UnitaryGate(U).inverse()
    assert type(owner) is UnitaryGate and owner.name=="unitary"
    source=qb.Circuit(width).append(owner,range(width))
    restored=qpy_loads(qpy_dumps(source))[0]
    np.testing.assert_allclose(Operator(restored).data,U.conj().T,atol=3e-14,rtol=0)


def principal_power(value,exponent):
    eigenvalues,vectors=np.linalg.eig(value)
    return vectors@np.diag(np.exp(1j*exponent*np.angle(eigenvalues)))@np.linalg.inv(vectors)


def controlled_case(width,controls,state,variant):
    U=matrix(width)
    body=qb.Circuit(width,name="controlled_source").unitary(U,range(width))
    body.global_phase=.17
    owner=body.to_gate(label="base")
    base=np.exp(.17j)*U
    if variant=="inverse_control":
        derived=owner.inverse().control(controls,ctrl_state=state,label="controlled")
        local=base.conj().T
    elif variant=="control_inverse":
        derived=owner.control(controls,ctrl_state=state).inverse()
        local=base.conj().T
    elif variant=="repeat_inverse":
        derived=owner.repeat(2).inverse().control(controls,ctrl_state=state)
        local=np.linalg.matrix_power(base,2).conj().T
    elif variant=="integer_power_inverse":
        derived=owner.power(2).inverse().control(controls,ctrl_state=state)
        local=np.linalg.matrix_power(base,2).conj().T
    elif variant=="fractional_power_inverse":
        derived=owner.power(.37).inverse().control(controls,ctrl_state=state)
        local=principal_power(base,.37).conj().T
    elif variant=="annotated_inverse":
        derived=owner.inverse(annotated=True).control(controls,ctrl_state=state,annotated=True)
        local=base.conj().T
    elif variant=="annotated_power_inverse":
        derived=owner.power(.37,annotated=True).inverse().control(controls,ctrl_state=state,annotated=True)
        local=principal_power(base,.37).conj().T
    else: raise AssertionError(variant)
    local_width=width+controls
    block=np.eye(1<<local_width,dtype=complex)
    index=sum(((state>>wire)&1)<<(controls-1-wire) for wire in range(controls))
    start=index*(1<<width)
    block[start:start+(1<<width),start:start+(1<<width)]=local
    wires=(3,0,2,1)[:local_width]
    source=qb.Circuit(4).h(1).append(derived,wires)
    source.global_phase=.23
    H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    expected=np.exp(.23j)*embed(block,wires,4)@embed(H,(1,),4)
    return source,expected


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("controls,state",[(1,0),(1,1),(2,1),(2,2)])
@pytest.mark.parametrize("variant",["inverse_control","control_inverse","repeat_inverse","integer_power_inverse",
    "fractional_power_inverse","annotated_inverse","annotated_power_inverse"])
def test_controlled_and_annotated_derived_qpy_preserves_full_local_basis(width,controls,state,variant):
    source,expected=controlled_case(width,controls,state,variant)
    before=source.to_ir().to_json()
    np.testing.assert_allclose(Operator(source).data,expected,atol=5e-13,rtol=0)
    restored=qpy_loads(qpy_dumps(source))[0]
    np.testing.assert_allclose(Operator(restored).data,expected,atol=5e-13,rtol=0)
    value=np.arange(1,17)+1j*np.arange(16,0,-1)
    value=value/np.linalg.norm(value)
    np.testing.assert_allclose(Statevector(value).evolve(restored).data,expected@value,atol=5e-13,rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(initial_state=value,cutoff=0).statevector(restored),expected@value,atol=5e-13,rtol=0)
    assert source.to_ir().to_json()==before


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("entry",["append","unitary"])
@pytest.mark.parametrize("inverse_before",[False,True])
def test_detached_qpy_matrix_owner_is_not_reversed_again_in_public_circuit(width,entry,inverse_before):
    U=matrix(width)
    source=qb.Circuit(width).unitary(U,range(width))
    if inverse_before: source=source.inverse()
    detached=qpy_loads(qpy_dumps(source))[0].operations[0].metadata["gate"]
    if not inverse_before: detached=detached.inverse()
    wires=(2,) if width==1 else (2,0)
    target=qb.QuantumCircuit(3,global_phase=.23)
    target.h(1)
    getattr(target,entry)(detached,wires)
    H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    expected=np.exp(.23j)*embed(U.conj().T,wires,3)@embed(H,(1,),3)
    np.testing.assert_allclose(Operator(target).data,expected,atol=3e-14,rtol=0)
    restored=qpy_loads(qpy_dumps(target))[0]
    np.testing.assert_allclose(Operator(restored).data,expected,atol=3e-14,rtol=0)


def test_control_inverse_respects_a_changed_definition_instead_of_replacing_it_from_base():
    owner=qb.Circuit(1).unitary(matrix(1),[0]).to_gate().control(1,ctrl_state=0)
    owner.definition.x(1)
    before=owner.to_matrix()
    np.testing.assert_allclose(owner.inverse().to_matrix(),before.conj().T,atol=3e-14,rtol=0)


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("variant",["inverse","double_inverse","copy_inverse","repeat_inverse"])
def test_derived_qpy_ir_and_compiler_reuse_the_same_local_matrix(width,variant):
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    _,source,expected=primitive_case(width,variant)
    for restored in [qpy_loads(qpy_dumps(source))[0],circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))]:
        compiled=qb.transpile(restored,basis_gates=["unitary","h","rx","ry","rz","cx"],optimization_level=1)
        np.testing.assert_allclose(Operator(compiled).data,expected,atol=5e-13,rtol=0)
        np.testing.assert_allclose(qb.StatevectorDevice().statevector(compiled),expected[:,0],atol=5e-13,rtol=0)
        np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0).statevector(compiled),expected[:,0],atol=5e-13,rtol=0)
