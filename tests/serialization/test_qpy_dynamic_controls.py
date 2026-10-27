# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real variable-width QPY controls, including custom annotation base records."""
import io
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads,FormatValidationError,ResourceLimitError
from quantumbridge.serialization.qpy import Reader
from quantumbridge.serialization.limits import SerializationLimits
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope


@pytest.mark.parametrize("kind",["phase","x"])
@pytest.mark.parametrize("count,state",[(2,0),(2,1),(2,3),(3,0),(3,1),(3,7)])
@pytest.mark.parametrize("context",["root","custom","annotated"])
def test_actual_public_variable_width_control_records_bind_and_execute(kind,count,state,context,record_property):
    public=pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.circuit import Parameter,AnnotatedOperation,InverseModifier
    from qiskit.circuit.library import MCPhaseGate,MCXGate
    from qiskit.quantum_info import Operator as PublicOperator
    p=Parameter("phase");gate=MCPhaseGate(2*p,count,label="dynamic",ctrl_state=state) if kind=="phase" else MCXGate(count,label="dynamic",ctrl_state=state)
    width=count+1;source=public.QuantumCircuit(width)
    if context=="annotated":gate=AnnotatedOperation(gate,[InverseModifier()])
    source.append(gate,range(width))
    if context=="custom":
        outer=public.QuantumCircuit(width);outer.append(source.to_gate(),range(width));source=outer
    stream=io.BytesIO();qpy.dump(source,stream,version=13)
    restored=qpy_loads(stream.getvalue())[0]
    assert tuple(value.uuid for value in restored.parameters)==((str(p.uuid),) if kind=="phase" else ())
    bound=restored.assign_parameters({restored.parameters[0]:.37} if kind=="phase" else {})
    expected=np.eye(1<<width,dtype=complex)
    start=int(format(state,"0"+str(count)+"b")[::-1],2)*2
    local=np.diag([1,np.exp(1j*.74)]) if kind=="phase" else np.array([[0,1],[1,0]])
    if context=="annotated":local=local.conj().T
    expected[start:start+2,start:start+2]=local
    np.testing.assert_allclose(Operator(bound).data,expected,atol=3e-12,rtol=0)
    order=[int(format(i,"0"+str(width)+"b")[::-1],2) for i in range(1<<width)]
    matrix=PublicOperator(source.assign_parameters({p:.37} if kind=="phase" else {})).data
    np.testing.assert_allclose(matrix[np.ix_(order,order)],expected,atol=3e-12,rtol=0)
    payload=qpy_dumps(restored)
    if kind=="x" and count==2 and state!=3:
        # Both measured SDKs fail on their own labeled open CCX payload too.
        # This is an explicit failed host transport, not an implemented path.
        with pytest.raises(TypeError,match="immutable"):qpy.load(io.BytesIO(stream.getvalue()))
        with pytest.raises(TypeError,match="immutable"):qpy.load(io.BytesIO(payload))
        native_back=qpy_loads(payload)[0]
        np.testing.assert_allclose(Operator(native_back).data,expected,atol=3e-12,rtol=0)
        record_property("public_return_transport","UPSTREAM_DEFECT: labeled open CCX immutable in QPY load")
    else:
        back=qpy.load(io.BytesIO(payload))[0]
        if kind=="phase" and context=="annotated":
            public_self=qpy.load(io.BytesIO(stream.getvalue()))[0]
            assert len(public_self.parameters)==len(back.parameters)==0
            assert len(restored.parameters)==1
            # Binding in the native parameter graph first is executable;
            # the symbolic public return path remains explicitly unsupported.
            back=qpy.load(io.BytesIO(qpy_dumps(bound)))[0]
            record_property("public_return_transport","UPSTREAM_DEFECT: symbolic annotation parameter index missing; numeric return verified")
        elif kind=="phase":back=back.assign_parameters({next(iter(back.parameters)):.37})
        matrix=PublicOperator(back).data
        np.testing.assert_allclose(matrix[np.ix_(order,order)],expected,atol=3e-12,rtol=0)
    record_property("native_import_math","MATCH; generic ControlledGate for dynamic classes, not MCPhaseGate/MCXGate ABI parity")


@pytest.mark.parametrize("field,value",[("width",2),("controls",0),("state",4),("clbits",1),("params",()),("params",(True,))])
def test_dynamic_control_signature_refuses_before_any_native_gate_constructor(field,value,monkeypatch):
    values=dict(width=3,controls=2,state=3,clbits=0,params=(.37,));values[field]=value
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**kw:pytest.fail("invalid dynamic QPY gate constructed"))
    with pytest.raises(FormatValidationError):Reader(b"",SerializationLimits()).dynamic_controlled_operation(
        "MCPhaseGate","",values["params"],values["width"],values["controls"],values["state"],values["clbits"])


@pytest.mark.parametrize("budget",["work","controls","matrix"])
def test_dynamic_control_admission_precedes_formal_owner_construction(budget,monkeypatch):
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**kw:pytest.fail("dynamic QPY gate constructed before admission"))
    limits=SerializationLimits(max_gate_expansion=4) if budget=="work" else SerializationLimits()
    with gate_circuit_scope(GateCircuitLimits(max_control_qubits=1 if budget=="controls" else 16,
            max_matrix_dimension=4 if budget=="matrix" else 256)),pytest.raises((MemoryError,ResourceLimitError)):
        Reader(b"",limits).dynamic_controlled_operation("MCPhaseGate","",(.37,),3,2,3,0)
