# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Geometry-dependent native RHF and number-sector exact energies."""
from quantumbridge import qchem


def main():
    results = []
    for distance in (1.,1.4,2.,3.):
        molecule = qchem.Molecule(['H','H'],[(0,0,0),(0,0,distance)],unit='bohr')
        problem = qchem.molecular_hamiltonian_native(molecule)
        rhf, exact = problem.scf_result.total_energy,problem.exact_ground_energy()
        assert exact <= rhf+1e-10 and problem.num_qubits == 4
        results.append(exact)
        print({'bond_bohr':distance,'RHF_Hartree':rhf,'exact_Hartree':exact,
               'scf_iterations':len(problem.scf_result.history),'qubits':problem.num_qubits})
    assert len(set(round(value,8) for value in results)) == 4


if __name__ == '__main__':
    main()
