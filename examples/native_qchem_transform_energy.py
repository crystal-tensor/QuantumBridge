# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Generate H2 once, then run native compiler/measurement transforms repeatedly."""
from quantumbridge import qchem, StatevectorDevice
from quantumbridge.qml import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import TransformProgram, cancel_inverses, decompose, compile, split_to_single_terms


def main():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr"))
    def circuit(tape,theta):
        tape.x(0)
        tape.x(0)
        tape.x(0)
        tape.x(1)
        qchem.apply_fermionic_excitation(tape,theta,[0,1,2,3])
        return tape.expval(problem.hamiltonian)
    node = TransformProgram([cancel_inverses,decompose(gate_set={"RX","RZ","CNOT"}),
        compile(basis_set={"RX","RZ","CNOT"}),split_to_single_terms])(QNode(circuit,4))
    for theta in [.1,.3]:
        tape = Tape(4)
        circuit(tape,theta)
        expected = StatevectorDevice().expectation(tape.circuit,problem.hamiltonian.to_quantumbridge())
        value = node(theta)
        assert abs(value-expected) < 2e-11
        print({"theta":theta,"energy":value,"unsplit":expected,"error":abs(value-expected),
               "child_tapes":node.last_metadata["executed_tape_count"],
               "postprocessing_order":node.last_metadata["postprocessing_order"]})
    print("No fixed Hamiltonian lookup or per-angle integral recomputation; transformed VJP is not yet delivered.")


if __name__ == "__main__":
    main()
