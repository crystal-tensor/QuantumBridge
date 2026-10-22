# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Observe public circuit/gate calls only; no upstream implementation access."""

import json
import warnings

import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit import Gate, Instruction, Parameter
from qiskit.quantum_info import Operator


def observe(name, function):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = function()
        print(json.dumps({"scenario": name, "result": result}, sort_keys=True))
    except Exception as error:
        print(json.dumps({"scenario": name, "error_type": type(error).__name__, "message": str(error)}, sort_keys=True))


def description(value):
    definition = getattr(value, "definition", None)
    return {"type": type(value).__name__, "gate": isinstance(value, Gate),
            "instruction": isinstance(value, Instruction), "name": value.name,
            "label": getattr(value, "label", None), "num_qubits": value.num_qubits,
            "num_clbits": value.num_clbits, "params": [str(p) for p in value.params],
            "definition_names": None if definition is None else [item.operation.name for item in definition.data]}


if __name__ == "__main__":
    print(json.dumps({"qiskit_version": qiskit.__version__}))
    p, q = Parameter("p"), Parameter("q")
    circuit = QuantumCircuit(1, name="unit")
    circuit.rx(p, 0)
    circuit.global_phase = p / 3
    observe("to_gate.default", lambda: description(circuit.to_gate()))
    observe("to_gate.label", lambda: description(circuit.to_gate(label="label")))
    for name, mapping in (("partial", {}), ("numeric", {p: .4}), ("symbolic", {p: q}), ("expression", {p: q.sin()}), ("unknown", {q: p})):
        observe("to_gate.map." + name, lambda mapping=mapping: description(circuit.to_gate(parameter_map=mapping)))
    for name in ("classical", "measure", "reset", "barrier", "delay"):
        sample = QuantumCircuit(1, 1 if name in {"classical", "measure"} else 0)
        if name == "measure": sample.measure(0, 0)
        elif name == "reset": sample.reset(0)
        elif name == "barrier": sample.barrier()
        elif name == "delay": sample.delay(10, 0)
        observe("to_gate." + name, lambda sample=sample: description(sample.to_gate()))
    gate = circuit.to_gate()
    for n in (-1, 0, 1, 2, 1.5, True):
        observe("gate.repeat." + str(n), lambda n=n: description(gate.repeat(n)))
        observe("circuit.repeat." + str(n), lambda n=n: [item.operation.name for item in circuit.repeat(n).data])
    for annotated in (False, True):
        observe("control." + str(annotated), lambda annotated=annotated: description(gate.control(annotated=annotated)))
    for ctrl in ("0", "1", "10", 0, 1, 2, -1):
        observe("control.state." + repr(ctrl), lambda ctrl=ctrl: description(gate.control(1, ctrl_state=ctrl, annotated=False)))
    a, b = QuantumCircuit(1, name="a"), QuantumCircuit(1, name="b")
    a.x(0)
    b.h(0)
    observe("tensor.order", lambda: Operator(a.tensor(b)).data.real.tolist())
    observe("tensor.inplace_return", lambda: a.copy().tensor(b, inplace=True) is None)
    middle = QuantumCircuit(1, name="middle")
    middle.append(gate, [0])
    outer = QuantumCircuit(1)
    outer.append(middle.to_gate(), [0])
    for reps in (0, 1, 2, -1, 1.5):
        observe("decompose.reps." + str(reps), lambda reps=reps: [item.operation.name for item in outer.decompose(reps=reps).data])
    observe("decompose.selected", lambda: [item.operation.name for item in outer.decompose("unit").data])
