# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Compute actual atomic-orbital integrals, without any external chemistry SDK."""
import numpy as np
from quantumbridge import qchem


def main():
    molecule = qchem.Molecule(['H','H'],[(0,0,0),(0,0,1.4)],unit='bohr')
    ao = qchem.molecular_integrals(molecule)
    np.testing.assert_allclose(ao.overlap.diagonal(),[1,1],atol=1e-12)
    assert ao.two_body.shape == (2,2,2,2)
    print('Overlap:',ao.overlap)
    print('Kinetic:',ao.kinetic)
    print('Nuclear attraction:',ao.nuclear_attraction)
    print('Chemist ERI:',ao.two_body)
    print('Nuclear repulsion:',ao.nuclear_repulsion_energy,'Hartree')


if __name__ == '__main__':
    main()
