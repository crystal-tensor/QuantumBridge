# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.chemistry import Molecule
from quantumbridge.chemistry.adapters import PySCFDriverAdapter


def test_pyscf_driver_installed_constructs_h2_and_wraps_result():
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")

    from pyscf import gto

    upstream_molecule = gto.Mole()
    upstream_molecule.atom = "H 0 0 0; H 0 0 0.735"
    upstream_molecule.basis = "sto-3g"
    upstream_molecule.build()

    result = PySCFDriverAdapter(Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.735)])).run()

    assert upstream_molecule.natm == 2
    assert result.provenance["mode"] == "Upstream Passthrough"
    assert result.provenance["dependency"] == "pyscf"
