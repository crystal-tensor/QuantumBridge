# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.chemistry import Molecule
from quantumbridge.chemistry.adapters import PySCFDriverAdapter


@pytest.mark.slow
def test_lih_installed_workflow_smoke_records_provenance():
    pytest.importorskip("qiskit_nature", reason="optional dependency unavailable: qiskit-nature")
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")

    from qiskit_nature.second_q.drivers import PySCFDriver

    molecule = Molecule(["Li", "H"], [(0, 0, 0), (0, 0, 1.6)], basis="sto3g")
    driver = PySCFDriver(atom="Li 0 0 0; H 0 0 1.6", basis="sto3g", max_cycle=1)
    adapter_result = PySCFDriverAdapter(molecule).run()

    assert driver is not None
    assert adapter_result.provenance["dependency"] == "pyscf"
    assert "Li" in adapter_result.metadata["molecule"]
