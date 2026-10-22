# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Installed public parameter/structure calls, not implementation inspection."""
import copy
import inspect
import json
from uuid import UUID
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction,Gate,Parameter,ParameterExpression,ParameterVector
from qiskit.quantum_info import Operator,Statevector,DensityMatrix


def encoded(value):
    if isinstance(value,(Parameter,ParameterExpression)):
        return {"type":type(value).__name__,"text":str(value),"free_parameters":sorted(p.name for p in value.parameters),"uuid":str(value.uuid) if isinstance(value,Parameter) else None}
    if isinstance(value,np.ndarray):return {"shape":value.shape,"real":value.real.tolist(),"imag":value.imag.tolist()}
    if isinstance(value,QuantumCircuit):return {"type":"QuantumCircuit","parameters":[p.name for p in value.parameters],"phase":encoded(value.global_phase),"params":[[encoded(p) for p in item.operation.params] for item in value.data]}
    if isinstance(value,(Instruction,Gate)):return {"type":type(value).__name__,"name":value.name,"params":[encoded(p) for p in value.params],"definition":encoded(value.definition)}
    if isinstance(value,dict):return {str(key):encoded(item) for key,item in value.items()}
    if isinstance(value,(tuple,list)):return [encoded(item) for item in value]
    if isinstance(value,np.generic):return value.item()
    return value


def record(name,call):
    try:print(json.dumps({"name":name,"result":encoded(call())},sort_keys=True))
    except Exception as error:print(json.dumps({"name":name,"exception":type(error).__name__,"message":str(error)},sort_keys=True))


print(json.dumps({"qiskit_version":qiskit.__version__}))
for cls in (Parameter,ParameterExpression,ParameterVector,QuantumCircuit,Instruction,Gate):
    record(cls.__name__+".signature",lambda cls=cls:str(inspect.signature(cls)))
for cls,names in ((Parameter,("bind","assign","gradient","sin","cos","exp")),(ParameterExpression,("bind","assign","subs","gradient")),(ParameterVector,("resize",)),(QuantumCircuit,("assign_parameters","to_instruction","to_gate","compose","inverse","power","repeat","decompose")),(Instruction,("assign_parameters","bind_parameters","inverse","repeat","power"))):
    for name in names:record(cls.__name__+"."+name+".signature",lambda cls=cls,name=name:str(inspect.signature(getattr(cls,name))))

p,q,r=Parameter("p"),Parameter("p"),Parameter("r")
uid=UUID("12345678-1234-5678-1234-567812345678")
record("identity.same_name_distinct",lambda:{"equal":p==q,"set_size":len({p,q}),"uuid_equal":p.uuid==q.uuid,"copied_equal":p==copy.deepcopy(p)})
record("identity.same_name_same_uuid",lambda:Parameter("a",uuid=uid)==Parameter("a",uuid=uid))
record("identity.different_name_same_uuid",lambda:Parameter("a",uuid=uid)==Parameter("b",uuid=uid))
def collision():
    circuit=QuantumCircuit(1);circuit.rx(p,0);circuit.ry(q,0);return circuit
record("identity.two_same_name_in_circuit",collision)
circuit=QuantumCircuit(1);circuit.rx(p,0)
record("identity.wrong_parameter_bind",lambda:circuit.assign_parameters({q:.7}))
record("identity.wrong_parameter_nonstrict",lambda:circuit.assign_parameters({q:.7},strict=False))
record("identity.string_bind",lambda:circuit.assign_parameters({"p":.7}))
vector=ParameterVector("theta",12)
sequence=QuantumCircuit(1)
for parameter in vector:sequence.rx(parameter,0)
record("vector.circuit_order",lambda:[parameter.name for parameter in sequence.parameters])
record("vector.sequence_bound_gates",lambda:sequence.assign_parameters(list(range(12))))
record("vector.dictionary_binding",lambda:sequence.assign_parameters({vector:list(range(12))}))
def restored_vector():
    original=vector[3];vector.resize(2);vector.resize(12)
    return {"same_element":vector[3]==original,"same_uuid":vector[3].uuid==original.uuid,"index":vector[3].index,"vector_name":vector[3].vector.name}
record("vector.resize_restores_identity",restored_vector)
record("identity.scalar_reconstruction_of_vector_element",lambda:Parameter(vector[0].name,uuid=vector[0].uuid)==vector[0])
def mixed_order():
    mixed=QuantumCircuit(1)
    for item in [Parameter("theta0"),vector[0],Parameter("theta"),Parameter("theta[99]")]:mixed.rx(item,0)
    return [item.name for item in mixed.parameters]
record("vector.mixed_circuit_parameter_order",mixed_order)
literal=QuantumCircuit(1)
for name in ("u[1]","u[2]","u[10]"):literal.rx(Parameter(name),0)
record("literal_bracket_names_lexicographic",lambda:[x.name for x in literal.parameters])
partial=QuantumCircuit(2);partial.rx(p+r,0);partial.ry(r*r,1);partial.global_phase=p/3
record("bind.partial_default_strict",lambda:partial.assign_parameters({p:.2}))
record("bind.empty_default_strict",lambda:partial.assign_parameters({}))
record("bind.partial_then_remaining",lambda:partial.assign_parameters({p:.2}).assign_parameters({r:-.3}))
record("bind.expression_substitution",lambda:partial.assign_parameters({p:2*r}).assign_parameters({r:.4}))
record("bind.unknown_strict",lambda:partial.assign_parameters({Parameter("unknown"):.2}))
record("bind.unknown_nonstrict",lambda:partial.assign_parameters({Parameter("unknown"):.2},strict=False))
record("bind.unknown_string_nonstrict",lambda:partial.assign_parameters({"unknown":.2},strict=False))
record("bind.bool_numeric",lambda:partial.assign_parameters({p:True,r:.2}))
record("bind.complex_numeric",lambda:partial.assign_parameters({p:1j,r:.2}))
record("expression.same_name_identity",lambda:(p+q).bind({p:.2,q:.4}))
record("expression.symbolic_assign",lambda:(p+r*r).assign(p,2*r))
record("expression.nonlinear_math",lambda:(p.sin()+r.cos()*p.exp()).bind({p:.2,r:-.3}))
record("expression.gradient",lambda:(p*r+r*r).gradient(r))
record("instruction.parameter_list",partial.to_instruction)
record("instruction.parameter_map",lambda:partial.to_instruction(parameter_map={p:2*r}))
target=Parameter("target")
record("instruction.complete_parameter_map",lambda:partial.to_instruction(parameter_map={p:2*target,r:target}))
record("gate.parameter_map",lambda:partial.to_gate(parameter_map={p:2*r}))
record("structure.inverse_params",partial.inverse)
record("structure.integer_power",lambda:partial.power(2))
record("structure.repeat",lambda:partial.repeat(3))
record("structure.repeat_decompose",lambda:partial.repeat(3).decompose())
record("structure.parameterized_to_gate",partial.to_gate)
for values in ((.2,-.3),(-.7,.5),(.8,1.1)):
    bound=partial.assign_parameters({p:values[0],r:values[1]})
    record("matrix."+str(values),lambda bound=bound:Operator(bound).reverse_qargs().data)

def inplace_contract():
    changed=partial.copy()
    result=changed.assign_parameters({p:.2},inplace=True)
    return {"return_is_none":result is None,"changed":changed,"original":partial}
record("bind.inplace_copy_contract",inplace_contract)

def copied_instruction():
    original=partial.to_instruction()
    copied=original.copy("copy")
    return {"same_instance":copied is original,"params_equal":copied.params==original.params,
        "definition_is_same":copied.definition is original.definition,"metadata":copied.definition.metadata}
record("instruction.copy_contract",copied_instruction)

mapped=partial.to_instruction(parameter_map={p:2*target,r:target})
mapped_parent=QuantumCircuit(2);mapped_parent.append(mapped,[0,1])
for value in (.2,-.3,.7):
    record("mapped_phase.full_complex."+str(value),
        lambda value=value:Operator(mapped_parent.assign_parameters({target:value})).reverse_qargs().data)
record("mapped_phase.remaining_parameters",lambda:[x.name for x in mapped_parent.parameters])
