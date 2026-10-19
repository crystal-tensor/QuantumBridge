# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Bounded in-program observation; no final-state substitution for snapshots.
from copy import deepcopy
from itertools import product
import json
import numpy as np
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.ir.qb_ir import matrix_from_ir
from .limits import AerExecutionLimits


def encode(value):
    if isinstance(value,np.ndarray):
        return {"qb_simulator_array":True,"real":value.real.tolist(),"imag":value.imag.tolist(),"complex":bool(np.iscomplexobj(value))}
    if isinstance(value,np.generic): return encode(value.item())
    if isinstance(value,complex): return {"qb_simulator_complex":[value.real,value.imag]}
    if isinstance(value,dict): return {key:encode(child) for key,child in value.items()}
    if isinstance(value,(tuple,list)): return [encode(child) for child in value]
    return value


def decode(value):
    if isinstance(value,dict):
        if value.get("qb_simulator_array") is True:
            if set(value)!={"qb_simulator_array","real","imag","complex"}: raise ValueError("Malformed simulator array.")
            real,imag=np.asarray(value["real"],float),np.asarray(value["imag"],float)
            if real.shape!=imag.shape or not np.all(np.isfinite(real)) or not np.all(np.isfinite(imag)): raise ValueError("Invalid simulator array values.")
            if not isinstance(value["complex"],bool) or not value["complex"] and np.any(imag):raise ValueError("Invalid simulator array type.")
            return real+1j*imag if value["complex"] else real
        if set(value)=={"qb_simulator_complex"}:
            result=complex(*value["qb_simulator_complex"])
            if not np.isfinite(result):raise ValueError("Invalid simulator complex value.")
            return result
        return {key:decode(child) for key,child in value.items()}
    if isinstance(value,list): return [decode(child) for child in value]
    return value


class SnapshotContext:
    def __init__(self,circuit,method,limits=None,*,finite_shots=False):
        self.circuit,self.method,self.limits=circuit,method,limits or AerExecutionLimits()
        self.finite_shots=finite_shots
        self.cells,self.labels,self.bytes,self.peak_bytes={},{},0,0
        self.count,self.groups=0,set()
        def visit(body):
            for item in body.operations:
                node=item.metadata.get("control_node")
                if node is not None:
                    for child in node.bodies: visit(child)
                spec=item.metadata.get("simulator_instruction")
                if spec is None: continue
                if item.controls or item.name!=spec.get("kind"): raise ValueError("Malformed simulator instruction.")
                from quantumbridge.devices.execution import validate_wires
                if not item.wires or tuple(item.wires)!=validate_wires(item.wires,circuit.num_qubits):raise ValueError("Invalid simulator wires.")
                if item.name.startswith("save_"):
                    if any(not isinstance(spec.get(flag),bool) for flag in ("pershot","conditional","unnormalized")):raise ValueError("Malformed snapshot modes.")
                    label=spec.get("label")
                    if not isinstance(label,str) or not label or label in self.labels: raise ValueError("Missing or duplicate snapshot label.")
                    self.labels[label]=spec
                    if "paulis" in spec and any(not isinstance(local,str) or len(local)!=len(item.wires) or set(local)-set("IXYZ") or not np.isfinite(coefficient) or not np.isreal(coefficient) for local,coefficient in spec["paulis"]):raise ValueError("Invalid saved Pauli observable.")
                    if "indices" in spec:
                        from numbers import Integral
                        if not spec["indices"] or any(isinstance(i,bool) or not isinstance(i,Integral) or not 0<=i<1<<circuit.num_qubits for i in spec["indices"]):raise ValueError("Invalid saved amplitude indices.")
                    self.limits.check("max_snapshot_count",len(self.labels))
                    if method in {"unitary","superop"} and spec["pershot"]:raise UnsupportedFeature("map_pershot","Linear-map snapshots are deterministic, not per-shot state trajectories.")
                    if spec["unnormalized"] and spec["kind"] not in {"save_density_matrix","save_probabilities","save_probabilities_dict","save_expectation_value","save_expectation_value_variance","save_amplitudes_squared"}:
                        raise UnsupportedFeature("unnormalized_save_kind")
        visit(circuit)

    def _density(self,state,wires):
        size=1<<len(wires)
        self.limits.check("max_saved_density_dimension",size)
        self.limits.check("max_snapshot_bytes",16*size*size)
        if self.method=="matrix_product_state": return state.reduced_density_matrix(wires)
        if self.method=="density_matrix":
            from quantumbridge.information.partial_trace import partial_trace
            return partial_trace(state,wires,self.circuit.num_qubits)
        if self.method=="statevector":
            rest=tuple(q for q in range(self.circuit.num_qubits) if q not in wires)
            partition=state.reshape((2,)*self.circuit.num_qubits).transpose(wires+rest).reshape(size,-1)
            return partition@partition.conj().T
        if self.method=="stabilizer":
            if len(wires)>5: raise UnsupportedFeature("tableau_reduced_density","Tableau Pauli expansion is bounded to five saved wires.")
            from quantumbridge.utils.math import pauli_matrix
            from quantumbridge.operators import Pauli
            result=np.zeros((size,size),complex)
            for local in product("IXYZ",repeat=len(wires)):
                label=["I"]*self.circuit.num_qubits; matrix=np.ones((1,1),complex)
                for wire,char in zip(wires,local): label[wire]=char; matrix=np.kron(matrix,pauli_matrix(char))
                result+=state.expectation_value(Pauli("".join(label)))*matrix/size
            return result
        raise UnsupportedFeature("density_snapshot_method")

    def _vector(self,state):
        self.limits.check("max_saved_state_dimension",1<<self.circuit.num_qubits)
        self.limits.check("max_snapshot_bytes",16*(1<<self.circuit.num_qubits))
        if self.method=="statevector": return state.copy()
        if self.method=="matrix_product_state": return state.statevector()
        if self.method=="stabilizer": return state.to_statevector().data
        raise UnsupportedFeature("statevector_snapshot_method","A mixed-state method cannot save a single pure statevector.")

    def _amplitudes(self,state,indices):
        if self.method=="matrix_product_state":
            values=[]
            for index in indices:
                vector=np.ones(1,complex)
                for wire,tensor in enumerate(state._tensors): vector=vector@tensor[:,(index>>(self.circuit.num_qubits-1-wire))&1,:]
                values.append(vector[0])
            return np.asarray(values)
        return self._vector(state)[indices]

    def _moments(self,state,wires,spec):
        if "paulis" in spec:
            from quantumbridge.operators import SparsePauliOperator,Pauli
            terms=[]
            for local,coefficient in spec["paulis"]:
                label=["I"]*self.circuit.num_qubits
                for wire,char in zip(wires,local): label[wire]=char
                terms.append(("".join(label),coefficient))
            operator=SparsePauliOperator(terms)
            if self.method in {"matrix_product_state","stabilizer"}:
                def expectation(op):
                    return float(sum(c*(state.expectation_pauli(label) if self.method=="matrix_product_state" else state.expectation_value(Pauli(label))) for label,c in op.terms).real)
                return expectation(operator),expectation(operator.dot(operator))
            from quantumbridge.utils.math import pauli_matrix,apply_unitary
            if self.method not in {"statevector","density_matrix"}:raise UnsupportedFeature("expectation_snapshot_method")
            # Act on vector/row tensor axes, never allocate an exponential Pauli matrix.
            def expectation(op):
                total=0j
                for label,coefficient in op.terms:
                    evolved=state.reshape(-1)
                    width=self.circuit.num_qubits*(2 if self.method=="density_matrix" else 1)
                    for wire,char in enumerate(label):
                        if char!="I":evolved=apply_unitary(evolved,pauli_matrix(char),(wire,),width)
                    value=np.trace(evolved.reshape(state.shape)) if self.method=="density_matrix" else np.vdot(state,evolved)
                    total+=coefficient*value
                return float(total.real)
            return expectation(operator),expectation(operator.dot(operator))
        self.limits.check("max_saved_density_dimension",1<<len(wires))
        self.limits.check("max_snapshot_bytes",16*(1<<(2*len(wires))))
        matrix=matrix_from_ir(spec["observable"])
        if matrix.shape!=(1<<len(wires),)*2 or not np.all(np.isfinite(matrix)) or not np.allclose(matrix,matrix.conj().T):raise ValueError("Invalid saved observable.")
        rho=self._density(state,wires)
        return float(np.trace(rho@matrix).real),float(np.trace(rho@matrix@matrix).real)

    def observe(self,item,branch,rng):
        spec=item.metadata["simulator_instruction"]; kind=spec["kind"][5:]
        if spec["pershot"] and not self.finite_shots: raise UnsupportedFeature("analytic_pershot","pershot saves require finite-shot trajectories.")
        wires=tuple(item.wires);state=branch.state
        if kind=="state": kind={"statevector":"statevector","density_matrix":"density_matrix","matrix_product_state":"matrix_product_state","stabilizer":"stabilizer","unitary":"unitary","superop":"superop"}[self.method]
        full={"statevector","statevector_dict","matrix_product_state","stabilizer","clifford","unitary","superop","amplitudes","amplitudes_squared"}
        if kind in full and wires!=tuple(range(self.circuit.num_qubits)): raise ValueError("This save instruction requires the full ordered register.")
        raw=kind in {"statevector","statevector_dict","matrix_product_state","stabilizer","clifford","unitary","superop","amplitudes"}
        if kind=="statevector": value=self._vector(state)
        elif kind=="statevector_dict": value={hex(i):complex(v) for i,v in enumerate(self._vector(state)) if abs(v)>1e-15}
        elif kind=="density_matrix": value=self._density(state,wires)
        elif kind in {"probabilities","probabilities_dict"}:
            self.limits.check("max_saved_state_dimension",1<<len(wires))
            if self.method=="matrix_product_state": probabilities=state.probabilities(wires)
            elif self.method=="statevector":
                rest=tuple(q for q in range(self.circuit.num_qubits) if q not in wires)
                partition=state.reshape((2,)*self.circuit.num_qubits).transpose(wires+rest).reshape(1<<len(wires),-1)
                values=np.sum(abs(partition)**2,axis=1)
                probabilities={format(i,f"0{len(wires)}b"):float(v) for i,v in enumerate(values)}
            else:
                rho=self._density(state,wires); probabilities={format(i,f"0{len(wires)}b"):float(v.real) for i,v in enumerate(np.diag(rho))}
            value=np.array([probabilities.get(format(i,f"0{len(wires)}b"),0.) for i in range(1<<len(wires))])
            if kind.endswith("dict"): value={hex(i):float(v) for i,v in enumerate(value) if v>0}
        elif kind in {"amplitudes","amplitudes_squared"}:
            if kind=="amplitudes_squared" and self.method=="density_matrix":value=np.diag(state).real[spec["indices"]].copy()
            else:
                value=self._amplitudes(state,spec["indices"])
                if kind.endswith("squared"): value=abs(value)**2
        elif kind in {"expectation_value","expectation_value_variance"}:
            first,second=self._moments(state,wires,spec)
            value=np.array([first,max(0.,second-first*first)]) if kind.endswith("variance") else first
        elif kind=="matrix_product_state" and self.method==kind:
            self.limits.check("max_snapshot_bytes",4*sum(t.nbytes for t in state._tensors))
            value=state.to_dict()
        elif kind in {"stabilizer","clifford"} and self.method=="stabilizer": value=state.clifford.to_dict()
        elif kind==self.method and kind in {"unitary","superop"}: value=state.copy()
        else: raise UnsupportedFeature("save_method",f"save_{kind} is unsupported by {self.method}.")
        group=hex(sum(bit<<index for index,bit in enumerate(branch.store.bits))) if spec["conditional"] else ""
        key=(spec["label"],group)
        if spec["conditional"]:self.groups.add(key)
        self.limits.check("max_conditional_groups",len(self.groups))
        size=len(json.dumps(encode(value),allow_nan=False).encode())
        cell=self.cells.setdefault(key,{"weight":0.,"value":None,"bytes":0})
        if spec["pershot"]:
            self.bytes+=size;self.limits.check("max_pershot_snapshot_bytes",self.bytes)
            if cell["value"] is None:cell["value"]=[]
            cell["value"].append(deepcopy(value))
        elif raw:
            if not self.finite_shots and cell["value"] is not None and json.dumps(encode(cell["value"]))!=json.dumps(encode(value)):
                raise UnsupportedFeature("mixed_pure_snapshot","An analytic mixed ensemble cannot be saved as one pure state; use density or pershot.")
            self.bytes+=size-cell["bytes"];cell["bytes"]=size;cell["value"]=deepcopy(value)
        else:
            if cell["value"] is None:cell["value"]={k:0. for k in value} if isinstance(value,dict) else np.zeros_like(value)
            if isinstance(value,dict):
                for k,v in value.items(): cell["value"][k]=cell["value"].get(k,0.)+branch.weight*v
            else: cell["value"]+=branch.weight*value
            actual=len(json.dumps(encode(cell["value"]),allow_nan=False).encode())
            self.bytes+=actual-cell["bytes"];cell["bytes"]=actual
        cell["weight"]+=branch.weight
        self.limits.check("max_snapshot_bytes",self.bytes);self.peak_bytes=max(self.peak_bytes,self.bytes)
        cell["raw"]=raw
        return [branch]

    def replace(self,item,branch):
        spec=item.metadata["simulator_instruction"]; kind=spec["kind"][4:]
        if tuple(item.wires)!=tuple(range(self.circuit.num_qubits)):raise ValueError("Set requires the full ordered register.")
        if kind=="matrix_product_state" and self.method==kind:
            from quantumbridge.information import MatrixProductState
            state=MatrixProductState.from_dict(spec["value"],max_memory_mb=self.limits.max_state_bytes/1024**2)
        elif kind=="stabilizer" and self.method==kind:
            from quantumbridge.information import StabilizerState,Clifford
            state=StabilizerState(Clifford.from_dict(spec["value"]))
        elif kind in {"statevector","density_matrix","unitary","superop"}:
            state=matrix_from_ir(spec["value"])
            self.limits.check("max_state_bytes",state.nbytes)
            # Revalidate IR-deserialized payloads rather than trusting builder validation.
            from quantumbridge.core import Circuit
            from .instructions import set_state
            set_state(Circuit(self.circuit.num_qubits),kind,state)
            if kind=="statevector" and self.method=="density_matrix":state=np.outer(state,state.conj())
            elif kind=="statevector" and self.method=="matrix_product_state":
                from quantumbridge.information import MatrixProductState
                state=MatrixProductState.from_statevector(state)
            elif kind!=self.method:raise UnsupportedFeature("set_method",f"set_{kind} is unsupported by {self.method}.")
        else: raise UnsupportedFeature("set_method",f"set_{kind} is unsupported by {self.method}.")
        if kind in {"matrix_product_state","stabilizer"} and state.num_qubits!=self.circuit.num_qubits:raise ValueError("Replacement state width mismatch.")
        branch.state=state
        return [branch]

    def metadata(self):
        result={}
        for (label,group),cell in self.cells.items():
            spec=self.labels[label];value=deepcopy(cell["value"])
            if not spec["pershot"] and not cell["raw"] and not spec["unnormalized"]:
                value={k:v/cell["weight"] for k,v in value.items()} if isinstance(value,dict) else value/cell["weight"]
            if spec["conditional"]: result.setdefault(label,{})[group]=encode(value)
            else:result[label]=encode(value)
        return {"saved_snapshots":result,"snapshot_storage_bytes":self.peak_bytes,"snapshot_labels":list(self.labels),
                "snapshot_aggregation":"trajectory/branch-weight average; raw states use last finite trajectory; conditional groups renormalized"}
