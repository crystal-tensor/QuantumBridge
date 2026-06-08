from quantumbridge.chemistry import Molecule


def test_molecule_xyz_and_bond_scan():
    mol = Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.7)])
    assert "H" in mol.to_xyz()
    assert len(mol.bond_scan(0, 1, [0.5, 0.8])) == 2
