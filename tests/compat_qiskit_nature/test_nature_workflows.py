# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_nature.driver_adapter import ADAPTER as DRIVER
from quantumbridge.compat.qiskit_nature.openfermion_adapter import ADAPTER as OPENFERMION
from quantumbridge.compat.qiskit_nature.problem_adapter import ADAPTER as PROBLEM


def _pyscf_driver_class():
    if not DRIVER.dependency_available():
        pytest.skip("qiskit-nature drivers unavailable")
    return DRIVER.passthrough_class("PySCFDriver")


def test_pyscf_driver_and_problem_availability():
    PySCFDriver = _pyscf_driver_class()
    assert PySCFDriver is not None
    assert PROBLEM.list_public_api_inventory()


def test_openfermion_availability():
    if not OPENFERMION.dependency_available():
        pytest.skip("openfermion unavailable")
    assert OPENFERMION.list_public_api_inventory()


@pytest.mark.parametrize(
    ("atom", "expected_particles"),
    [
        ("H 0 0 0; H 0 0 0.735", 2),
        ("Li 0 0 0; H 0 0 1.6", 4),
        ("O 0 0 0; H 0.757 0.586 0; H -0.757 0.586 0", 10),
    ],
)
def test_small_molecule_driver_smoke(atom, expected_particles):
    PySCFDriver = _pyscf_driver_class()
    problem = PySCFDriver(atom=atom, basis="sto3g").run()
    assert problem.num_particles[0] + problem.num_particles[1] == expected_particles