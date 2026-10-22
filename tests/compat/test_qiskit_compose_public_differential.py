# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent public API observations; native execution never calls upstream."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core import classical as native_expr
from quantumbridge.core.errors import CircuitError
from quantumbridge.information import Operator

public=pytest.importorskip("qiskit")
from qiskit.circuit.classical import expr,types
from qiskit.quantum_info import Operator as PublicOperator


def signatures(circuit,native):
    result={}
    for method in ("iter_input_vars","iter_captured_vars","iter_declared_vars","iter_captured_stretches","iter_declared_stretches"):
        result[method]=[(v.name,(v.type.kind,v.type.width) if native else
            ("bool",1) if isinstance(v.type,types.Bool) else ("uint",v.type.width) if isinstance(v.type,types.Uint) else ("duration",1)) for v in getattr(circuit,method)()]
    return result


def scenario(name,native):
    Circuit=qb.Circuit if native else public.QuantumCircuit
    if name=="direct-annotation":
        from qiskit.circuit import AnnotatedOperation as PublicAnnotation,InverseModifier as PublicInverse
        from qiskit.circuit.library import RYGate as PublicRY
        from quantumbridge.core.standard_gates import RYGate
        operation=qb.AnnotatedOperation(RYGate(.3),[qb.InverseModifier()]) if native else PublicAnnotation(PublicRY(.3),[PublicInverse()])
        out=Circuit(1).compose(operation)
        actual=out.operations[0].metadata["annotated_operation"] if native else out.data[0].operation
        return [actual is operation,type(actual).__name__]
    if name.startswith("direct-"):
        from qiskit.circuit import Gate as PublicGate
        gate=(qb.Gate if native else PublicGate)("opaque",1,[.2])
        out=Circuit(1).compose(gate,copy="copytrue" in name,wrap="wraptrue" in name)
        operation=out.operations[0].metadata["gate"] if native else out.data[0].operation
        gate.params[0]=.7
        return [operation is gate,type(operation).__name__,operation.name,list(operation.params)]
    if name in {"default-new","inplace","explicit-new","front-order","wrapped-unitary","wrapped-reset","wrapped-measure"}:
        measured=name=="wrapped-measure"
        source=Circuit(1,int(measured),name="inner");source.x(0)
        if name=="wrapped-reset":source.reset(0)
        elif measured:source.measure(0,0)
        else:source.h(0)
        target=Circuit(2,2,name="outer");target.z(0)
        kwargs={"qubits":[1],"clbits":[1] if measured else []}
        if name.startswith("wrapped"):kwargs["wrap"]=True
        if name=="inplace":kwargs["inplace"]=True
        if name=="explicit-new":kwargs["inplace"]=False
        if name=="front-order":kwargs["front"]=True
        out=target.compose(source,**kwargs);result=target if out is None else out
        items=result.operations if native else result.data
        operation_names=[item.name if native else item.operation.name for item in items]
        record={"none":out is None,"names":operation_names,"original_size":len(target.operations if native else target.data)}
        if name.startswith("wrapped"):
            operation=(items[-1].metadata.get("gate",items[-1].metadata.get("instruction_object")) if native else items[-1].operation)
            record["wrapper_type"]=type(operation).__name__
            record["body_names"]=["measure" if isinstance(x,qb.Measurement) else x.name for x in operation.definition.iter_instructions()] if native else [x.operation.name for x in operation.definition.data]
        return record
    if name.startswith("wire-"):
        specs={"scalar":1,"negative":-1,"slice":slice(0,3,2),"nested":[[2],[0]],"float":.5,"duplicate":[0,0],"too-many":[0,1,2],"boolean":True}
        kind=name[5:];width=2 if kind in {"slice","nested","duplicate","too-many"} else 1
        source=Circuit(width);source.x(0)
        if width==2:source.cx(0,1)
        out=Circuit(3).compose(source,qubits=specs[kind])
        return [list(item.wires) for item in out.operations] if native else [[out.find_bit(q).index for q in item.qubits] for item in out.data]
    if name in {"classical-negative","classical-scalar","classical-slice"}:
        source=Circuit(1,1);source.measure(0,0)
        spec=-1 if name=="classical-negative" else 1 if name=="classical-scalar" else slice(1,2)
        out=Circuit(3,3).compose(source,qubits=2,clbits=spec)
        return [[out.measurements[0].wire],[out.measurements[0].bit]] if native else [[out.find_bit(q).index for q in out.data[0].qubits],[out.find_bit(c).index for c in out.data[0].clbits]]
    E=native_expr if native else expr
    bool_type=native_expr.Bool() if native else types.Bool()
    uint_type=native_expr.UInt(2) if native else types.Uint(2)
    if name in {"local","input","capture","remap-name","remap-object-name","remap-typed","remap-wrong-type","remap-kind","unused-remap","capture-inline","capture-missing","capture-redeclare","capture-remap-inline","input-capture-conflict"}:
        source=Circuit(1);a=E.Var.new("a",bool_type);target=Circuit(1)
        if name=="input":source.add_input(a)
        elif name.startswith("capture-") or name=="capture":source.add_capture(a)
        else:source.add_var(a,True)
        kwargs={}
        if name=="remap-name":kwargs["var_remap"]={"a":"b"}
        elif name=="remap-object-name":kwargs["var_remap"]={a:"b"}
        elif name=="remap-typed":kwargs["var_remap"]={a:E.Var.new("b",bool_type)}
        elif name=="remap-wrong-type":kwargs["var_remap"]={a:E.Var.new("b",uint_type)}
        elif name=="remap-kind":kwargs["var_remap"]={a:E.Stretch.new("b")}
        elif name=="unused-remap":kwargs["var_remap"]={"unused":"b"}
        elif name in {"capture-inline","capture-redeclare"}:
            target.add_var(a,False);kwargs["inline_captures"]=name=="capture-inline"
        elif name=="capture-missing":kwargs["inline_captures"]=True
        elif name=="capture-remap-inline":
            b=target.add_var("b",False);kwargs={"var_remap":{a:b},"inline_captures":True}
        elif name=="input-capture-conflict":
            target.add_input("input",bool_type);target.add_capture(E.Var.new("capture",bool_type))
        return signatures(target.compose(source,**kwargs),native)
    if name in {"empty-alike","empty-captures","empty-drop","empty-invalid"}:
        source=Circuit(1,name="source");source.add_var("a",True);source.add_stretch("s")
        out=source.copy_empty_like(vars_mode=name[6:])
        return [out.name,len(out.operations if native else out.data),signatures(out,native)]
    if name=="copy-name":
        source=Circuit(1,name="old");out=source.copy(name="new")
        return [source.name,out.name]
    if name=="copy-var-identity":
        source=Circuit(1);a=source.add_var("a",True)
        return source.copy().get_var("a") is a
    if name=="get-default":return Circuit(1).get_identifier("missing",7)
    if name=="get-missing":return Circuit(1).get_var("missing")
    raise AssertionError(name)


CASES=["default-new","inplace","explicit-new","front-order","wrapped-unitary","wrapped-reset","wrapped-measure",
    "wire-scalar","wire-negative","wire-slice","wire-nested","wire-float","wire-duplicate","wire-too-many","wire-boolean",
    "classical-negative","classical-scalar","classical-slice","local","input","capture","remap-name","remap-object-name",
    "remap-typed","remap-wrong-type","remap-kind","unused-remap","capture-inline","capture-missing","capture-redeclare",
    "capture-remap-inline","input-capture-conflict","empty-alike","empty-captures","empty-drop","empty-invalid",
    "copy-name","copy-var-identity","get-default","get-missing",
    "direct-copytrue-wraptrue","direct-copytrue-wrapfalse","direct-copyfalse-wraptrue","direct-copyfalse-wrapfalse","direct-annotation"]


@pytest.mark.parametrize("name",CASES)
def test_real_public_literal_returns_errors_and_scope_contracts(name):
    try:expected=scenario(name,False)
    except Exception as error:
        with pytest.raises(Exception) as actual:scenario(name,True)
        assert type(actual.value).__name__==type(error).__name__
    else:assert scenario(name,True)==expected


def test_public_noncontiguous_front_operator_matches_native_full_complex_matrix():
    expected=public.QuantumCircuit(3);expected.cx(0,2);expected.global_phase=.13
    inner=public.QuantumCircuit(2);inner.rx(.31,0);inner.cx(0,1);inner.global_phase=.07
    expected=expected.compose(inner,qubits=[2,0],front=True)
    native=qb.Circuit(3).cx(0,2);native.global_phase=.13
    source=qb.Circuit(2).rx(.31,0).cx(0,1);source.global_phase=.07
    np.testing.assert_allclose(Operator(native.compose(source,qubits=[2,0],front=True)).data,
        PublicOperator(expected.reverse_bits()).data,atol=4e-13,rtol=0)


def test_actual_public_qpy_reads_native_wrapped_composition_and_full_phase():
    import io
    from qiskit import qpy
    from quantumbridge.serialization import qpy_dumps
    inner=qb.Circuit(1,name="inner").ry(.3,0);inner.global_phase=.17
    native=qb.Circuit(2).compose(inner,qubits=[1],wrap=True)
    restored=qpy.load(io.BytesIO(qpy_dumps(native)))[0]
    np.testing.assert_allclose(PublicOperator(restored.reverse_bits()).data,Operator(native).data,atol=5e-13,rtol=0)


def test_actual_public_wrapped_qpy_loads_binds_and_executes_natively():
    import io
    from qiskit import qpy
    from qiskit.circuit import Parameter
    from quantumbridge.serialization import qpy_loads
    p=Parameter("p");inner=public.QuantumCircuit(1,name="inner");inner.ry(p,0);inner.global_phase=p/3
    outer=public.QuantumCircuit(2).compose(inner,qubits=[1],wrap=True)
    stream=io.BytesIO();qpy.dump(outer,stream,version=13)
    native=qpy_loads(stream.getvalue())[0].bind({"p":.3})
    expected=PublicOperator(outer.assign_parameters({p:.3}).reverse_bits()).data
    np.testing.assert_allclose(Operator(native).data,expected,atol=5e-13,rtol=0)


def test_public_qpy_metadata_cannot_smuggle_a_fake_native_classical_scope():
    import io
    from qiskit import qpy
    from quantumbridge.serialization import qpy_loads,UnsupportedFeature
    source=qb.Circuit(1);source.add_var("a",True)
    fake=public.QuantumCircuit(1);fake.metadata=source.metadata
    stream=io.BytesIO();qpy.dump(fake,stream,version=13)
    with pytest.raises(UnsupportedFeature,match="classical"):qpy_loads(stream.getvalue())
