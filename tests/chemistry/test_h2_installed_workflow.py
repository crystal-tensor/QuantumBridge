# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import math
import numpy as np
import pytest

from quantumbridge.chemistry import ExactDiagonalizationSolver, Molecule, VQEChemistrySolver
from quantumbridge.chemistry.adapters.qiskit_nature_adapter import hamiltonian_from_qiskit_nature
from quantumbridge.chemistry.ansatz import hardware_efficient_chemistry_ansatz
from quantumbridge.chemistry.result import ChemistryResult
from quantumbridge.chemistry.solvers import minimal_h2_qubit_hamiltonian


def test_h2_installed_qiskit_nature_to_quantumbridge_workflow():
    pytest.importorskip("qiskit_nature", reason="optional dependency unavailable: qiskit-nature")
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")

    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.mappers import JordanWignerMapper

    driver = PySCFDriver(atom="H 0 0 0; H 0 0 0.735", basis="sto3g")
    problem = driver.run()
    second_q_ops = problem.second_q_ops()
    electronic_op = second_q_ops[0] if isinstance(second_q_ops, tuple) else next(iter(second_q_ops.values()))
    upstream_qubit_op = JordanWignerMapper().map(electronic_op)
    qb_hamiltonian = hamiltonian_from_qiskit_nature(upstream_qubit_op)

    result = ExactDiagonalizationSolver().solve(
        qb_hamiltonian,
        molecule=Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.735)]),
        nuclear_repulsion_energy=float(problem.nuclear_repulsion_energy),
    )

    assert isinstance(result, ChemistryResult)
    assert math.isfinite(result.total_energy)
    assert result.num_qubits == upstream_qubit_op.num_qubits
    assert result.provenance["mode"] == "Native Core"


def test_h2_installed_vqe_chemistry_solver_returns_finite_number():
    pytest.importorskip("qiskit_nature", reason="optional dependency unavailable: qiskit-nature")
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")

    hamiltonian = minimal_h2_qubit_hamiltonian()
    solver = VQEChemistrySolver(hardware_efficient_chemistry_ansatz(2), np.array([0.1, 0.2]), steps=3)
    result = solver.solve(
        hamiltonian,
        molecule=Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.735)]),
        nuclear_repulsion_energy=0.7151043390810812,
    )

    assert isinstance(result, ChemistryResult)
    assert math.isfinite(result.total_energy)
    assert result.provenance["component"] == "quantumbridge.chemistry.solvers"
