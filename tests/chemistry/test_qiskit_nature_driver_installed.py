# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.chemistry.adapters import QiskitNatureDriverAdapter


def test_qiskit_nature_driver_installed_constructs_problem_object():
    pytest.importorskip("qiskit_nature", reason="optional dependency unavailable: qiskit-nature")
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")

    from qiskit_nature.second_q.drivers import PySCFDriver

    upstream_driver = PySCFDriver(atom="H 0 0 0; H 0 0 0.735", basis="sto3g")
    result = QiskitNatureDriverAdapter(upstream_driver).run()

    assert result.metadata["upstream_result_type"] == "ElectronicStructureProblem"
    assert result.provenance["dependency"] == "qiskit-nature"
