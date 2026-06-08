from quantumbridge.chemistry import Molecule


def test_h2_bond_scan():
    mol = Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.7)])
    assert [scan.coordinates[1][2] for scan in mol.bond_scan(0, 1, [0.4, 0.6])] == [0.4, 0.6]
