# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Declared gate identity takes precedence over execution-name aliases."""

from copy import deepcopy

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import (qasm2_loads,qasm2_dumps,SerializationError,
    SerializationLimits,ResourceLimitError,qpy_dumps,qpy_loads)


X = np.array([[0,1],[1,0]],complex)
INITIAL_INVALID_BODIES = [
    'gate h a { U(pi,0,pi) a; } include "qelib1.inc"; qreg q[1]; h q[0];',
    'include "qelib1.inc"; include "qelib1.inc"; qreg q[1]; h q[0];',
    'qreg h[1]; include "qelib1.inc";',
    'gate p a { p a; } qreg q[1];',
    'gate g(t) a { U(unknown,0,0) a; } qreg q[1];',
    'gate a t { b t; } gate b t { U(pi,0,pi) t; } qreg q[1];',
    'gate g(t) a { U(t,0,0) a[0]; } qreg q[1];',
    'gate g a { U(pi,0,pi) absent; } qreg q[1];',
    'include "qelib1.inc"; gate g a { rx a; } qreg q[1];',
]
INVALID_BODIES = [
    'include "qelib1.inc"; gate h a { U(pi,0,pi) a; } qreg q[1];',
    'gate g a { U(pi,0,pi) a; } gate g a { U(0,0,pi) a; } qreg q[1];',
    'gate g a { U(pi,0,pi) a; } qreg g[1];',
    'gate g a { missing a; } qreg q[1];',
    'gate g(t) a { U(t,0) a; } qreg q[1];',
    'gate g a,b { CX a; } qreg q[2];',
    'gate g a,b { CX a,a; } qreg q[2];',
    'gate inner(t) a { U(t,0,0) a; } gate outer a { inner a; } qreg q[1];',
    'gate inner(t) a { U(t,0,0) a; } gate outer(t) a,b { inner(t) a,b; } qreg q[2];',
    'gate inner(t) a { U(t,0,0) a; } gate outer a { inner(t) a; } qreg q[1];',
    'qreg q[1]; gate g a { U(q,0,0) a; }',
    'qreg q[1]; gate g a { U(pi,0,pi) q; }',
    'gate U a { } qreg q[1];',
    'gate CX a,b { } qreg q[2];',
    'gate measure a { } qreg q[1];',
    'gate reset a { } qreg q[1];',
    'gate barrier a { } qreg q[1];',
    'gate g a { measure a -> a; } qreg q[1];',
    'gate g a { reset a; } qreg q[1];',
]


def program(body):
    return "OPENQASM 2.0; "+body


@pytest.mark.parametrize("name", ["h","x","p","cphase","cnot","cu1"])
def test_literal_gate_definition_precedes_primitive_aliases_without_include(name):
    text = program(f"gate {name} a {{ U(pi,0,pi) a; }} qreg q[1]; {name} q[0];")
    circuit = qasm2_loads(text)
    assert circuit.operations[0].name == name
    assert "gate" in circuit.operations[0].metadata
    np.testing.assert_allclose(Operator(circuit).data,X,atol=2e-15,rtol=0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit),X[:,0],atol=2e-15,rtol=0)
    restored = qasm2_loads(qasm2_dumps(circuit))
    np.testing.assert_allclose(Operator(restored).data,X,atol=2e-15,rtol=0)


@pytest.mark.parametrize("body", INITIAL_INVALID_BODIES)
def test_invalid_unused_or_conflicting_definitions_refuse_before_publication_and_recover(body):
    with pytest.raises(SerializationError):
        qasm2_loads(program(body))
    valid = qasm2_loads(program('gate g a { U(pi,0,pi) a; } qreg q[1]; g q[0];'))
    np.testing.assert_allclose(Operator(valid).data,X,atol=2e-15,rtol=0)


@pytest.mark.parametrize("name", ["p","cphase","cnot"])
def test_previously_declared_alias_gate_is_used_inside_nested_definitions(name):
    text = program(f"gate {name}(t) a {{ U(t,0,0) a; }} "
        f"gate outer(s) b {{ {name}(s/2) b; {name}(s/2) b; }} "
        "qreg q[3]; outer(.37) q[2];")
    circuit = qasm2_loads(text)
    angle = .37/2
    ry = np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    expected = np.kron(np.eye(4),ry)
    np.testing.assert_allclose(Operator(circuit).data,expected,atol=3e-15,rtol=0)
    np.testing.assert_allclose(Operator(qasm2_loads(qasm2_dumps(circuit))).data,expected,atol=3e-15,rtol=0)


@pytest.mark.parametrize("body",INVALID_BODIES)
def test_definition_names_signatures_and_local_scope_are_admitted_before_use(body):
    with pytest.raises(SerializationError):
        qasm2_loads(program(body))


def definition_chain(count,branching=1):
    declarations = ['gate g0 a { U(pi,0,pi) a; }']
    for index in range(1,count):
        declarations.append(f'gate g{index} a {{ '+f'g{index-1} a;'*branching+' }')
    return program(' '.join(declarations)+' qreg q[1];')


@pytest.mark.parametrize("branching",[1,2])
def test_unused_definition_depth_is_checked_before_publication(branching):
    with pytest.raises(ResourceLimitError,match="max_nesting_depth"):
        qasm2_loads(definition_chain(7,branching),limits=SerializationLimits(max_nesting_depth=3))


def test_unused_exponential_definition_work_is_bounded_without_expansion(monkeypatch):
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**k: pytest.fail("Admission constructed a Gate"))
    with pytest.raises(ResourceLimitError,match="max_gate_expansion"):
        qasm2_loads(definition_chain(12,2),limits=SerializationLimits(max_gate_expansion=1000))


def test_unused_definition_reuses_gate_circuit_depth_budget():
    from quantumbridge.core import GateCircuitLimits,gate_circuit_scope
    with gate_circuit_scope(GateCircuitLimits(max_definition_depth=3)):
        with pytest.raises(MemoryError,match="max_definition_depth"):
            qasm2_loads(definition_chain(7))


def test_invalid_definition_does_not_publish_or_mutate_prior_ast(monkeypatch):
    from quantumbridge.serialization.text_parser import SourceParser
    from quantumbridge.serialization.text_lowering import Lowerer
    source = program('gate valid a { U(pi,0,pi) a; } '
        'gate invalid(t) a { valid a; U(absent,0,0) a; } qreg q[1];')
    limits = SerializationLimits()
    ast = SourceParser(source,2,limits).parse()
    snapshot = deepcopy(ast)
    lowerer = Lowerer(ast,limits)
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**k: pytest.fail("Invalid body was expanded"))
    with pytest.raises(SerializationError,match="Undefined"):
        lowerer.lower()
    assert set(lowerer.definitions) == {"valid"}
    assert ast == snapshot
    assert lowerer.definitions["valid"] == ast.statements[0].data


def embed(matrix,wires,width):
    result = np.zeros((1<<width,1<<width),complex)
    for column in range(1<<width):
        bits = [int(value) for value in f"{column:0{width}b}"]
        local_column = int(''.join(str(bits[wire]) for wire in wires),2)
        for local_row in range(1<<len(wires)):
            output = bits.copy()
            for wire,value in zip(wires,f"{local_row:0{len(wires)}b}"):
                output[wire] = int(value)
            result[int(''.join(map(str,output)),2),column] = matrix[local_row,local_column]
    return result


def complex_nested_source_and_oracle():
    text = program('gate p(t) a { U(t,0,0) a; } '
        'gate h(t) a,b { p(t/2) a; CX a,b; U(0,0,t) b; p(-t/2) a; } '
        'qreg q[3]; U(pi/2,0,pi) q[1]; h(.37) q[2],q[0]; U(0,0,-.19) q[2];')
    def ry(t): return np.array([[np.cos(t/2),-np.sin(t/2)],[np.sin(t/2),np.cos(t/2)]])
    h = np.array([[1,1],[1,-1]])/np.sqrt(2)
    cx = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
    expected = np.eye(8,dtype=complex)
    for matrix,wires in [(h,(1,)),(ry(.37/2),(2,)),(cx,(2,0)),
                         (np.diag([1,np.exp(.37j)]),(0,)),(ry(-.37/2),(2,)),
                         (np.diag([1,np.exp(-.19j)]),(2,))]:
        expected = embed(matrix,wires,3)@expected
    return text,expected


@pytest.mark.parametrize("variant",["original","copy","inverse"])
@pytest.mark.parametrize("transport",["qasm2","qpy13","json-ir","compiler"])
def test_complex_nested_definition_order_survives_execution_and_transport(variant,transport):
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.compiler import transpile
    from quantumbridge.ir.qb_ir import IRProgram
    text,expected = complex_nested_source_and_oracle()
    source = qasm2_loads(text)
    before = source.to_ir().to_json()
    circuit = source.copy() if variant == "copy" else source.inverse() if variant == "inverse" else source
    if variant == "inverse": expected = expected.conj().T
    if transport == "qasm2":
        if variant == "inverse":
            with pytest.warns(UserWarning,match="circuit-name"):
                text = qasm2_dumps(circuit,allow_metadata_loss=True)
        else: text = qasm2_dumps(circuit)
        circuit = qasm2_loads(text)
    elif transport == "qpy13": circuit = qpy_loads(qpy_dumps(circuit))[0]
    elif transport == "json-ir": circuit = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    else: circuit = transpile(circuit,basis_gates=["u","ry","rz","h","cx"],optimization_level=0)
    np.testing.assert_allclose(Operator(circuit).data,expected,atol=8e-15,rtol=0)
    for device in [qb.StatevectorDevice(),qb.MatrixProductStateDevice(cutoff=0)]:
        np.testing.assert_allclose(device.statevector(circuit),expected[:,0],atol=8e-15,rtol=0)
    assert source.to_ir().to_json() == before


def test_bound_native_parameter_identity_before_qasm2_numeric_roundtrip():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    p = qb.Parameter("theta")
    body = qb.Circuit(1,name="p").ry(p,0).phase(p/3,0)
    source = qb.Circuit(1).append(body.to_gate(),[0])
    for restore in [lambda c:qpy_loads(qpy_dumps(c))[0],lambda c:circuit_from_ir(c.to_ir())]:
        restored = restore(source)
        assert restored.parameters == (p,)
        numeric = qasm2_loads(qasm2_dumps(restored.assign_parameters({p:.37})))
        ry = np.array([[np.cos(.37/2),-np.sin(.37/2)],[np.sin(.37/2),np.cos(.37/2)]])
        expected = np.diag([1,np.exp(.37j/3)])@ry
        np.testing.assert_allclose(Operator(numeric).data,expected,atol=3e-15,rtol=0)


def test_nonconflicting_include_after_definition_keeps_definition_and_standard_math():
    text = program('gate custom a { U(pi,0,pi) a; } include "qelib1.inc"; '
        'qreg q[1]; custom q[0]; h q[0];')
    expected = np.array([[1,1],[1,-1]])@X/np.sqrt(2)
    np.testing.assert_allclose(Operator(qasm2_loads(text)).data,expected,atol=3e-15,rtol=0)


def test_empty_definition_and_local_barrier_are_not_dynamic_primitives():
    text = program('gate identity a { } gate g a { U(pi,0,pi) a; barrier a; } '
        'qreg q[1]; identity q[0]; g q[0];')
    circuit = qasm2_loads(text)
    assert any(op.metadata.get("directive") for op in circuit.operations)
    np.testing.assert_allclose(Operator(circuit).data,X,atol=3e-15,rtol=0)
