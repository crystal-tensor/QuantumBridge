# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Generated molecular Hamiltonian, exact excitation circuit and native gradients."""
from quantumbridge import qchem
from quantumbridge.qml import QNode


def main():
    molecule = qchem.Molecule(['H','H'],[(0,0,0),(0,0,1.4)],unit='bohr')
    problem = qchem.molecular_hamiltonian_native(molecule)
    def ansatz(tape,theta):
        tape.x(0);tape.x(1)
        qchem.apply_fermionic_excitation(tape,theta,[0,1,2,3])
        return tape.expval(problem.hamiltonian.to_quantumbridge())
    node, theta = QNode(ansatz,4),0.
    initial = node(theta)
    for _ in range(70):
        theta -= .4*node.gradient(theta,method='adjoint')
    energy, exact = node(theta),problem.exact_ground_energy()
    assert energy < initial-.01 and abs(energy-exact) < 1e-7
    print({'HF':initial,'VQE':energy,'exact':exact,'optimization_error':energy-exact,'theta':theta,
           'gradient':'native adjoint','geometry_differentiable':False})


if __name__ == '__main__':
    main()
