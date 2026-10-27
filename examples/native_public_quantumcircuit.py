# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free public builders and real counts in four native devices."""
import json
import quantumbridge as qb


def main():
    qubits=qb.QuantumRegister(2,"data");bits=qb.ClassicalRegister(2,"readout")
    circuit=qb.QuantumCircuit(qubits,bits)
    handle=circuit.x([qubits[0],qubits[1]])
    assert type(handle) is qb.InstructionSet and len(handle)==2
    circuit.measure(qubits,bits)
    counts={}
    for kind in (qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice):
        result=kind().run_shots(circuit,shots=4,seed=7).counts()
        assert result=={"11":4};counts[kind.__name__]=result
    assert len(circuit.data)==4 and len(circuit.operations)==4
    print(json.dumps({"devices":counts,"instruction_handles":len(handle),"full_sdk_parity":False},sort_keys=True))


if __name__=="__main__":main()
