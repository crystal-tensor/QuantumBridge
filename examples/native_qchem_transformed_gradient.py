# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Build actual H2 geometry once; differentiate transformed native excitation."""

from quantumbridge import qchem
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram,merge_rotations,split_non_commuting


def main():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr"))
    def circuit(tape,theta):
        tape.x(0)
        tape.x(1)
        qchem.apply_fermionic_excitation(tape,theta,[0,1,2,3])
        return tape.expval(problem.hamiltonian)
    original = QNode(circuit,4)
    node = TransformProgram([merge_rotations,split_non_commuting])(original)
    theta = .3
    energy,gradient = node.execute_and_compute_derivatives(theta)
    assert abs(energy-original(theta)) < 2e-11
    assert abs(gradient-original.gradient(theta)) < 2e-11
    initial = energy
    for _ in range(3): theta -= .3*node.gradient(theta)
    final = node(theta)
    assert final < initial
    print({"initial_energy":initial,"initial_native_gradient":gradient,"final_theta":theta,"final_energy":final,
           "group_count":node.last_metadata["executed_tape_count"],"transform_count":node.last_metadata["transform_count"]})
    print("One geometry/integral construction; no fixed-Hamiltonian lookup or per-child SCF recomputation.")


if __name__ == "__main__":
    main()
