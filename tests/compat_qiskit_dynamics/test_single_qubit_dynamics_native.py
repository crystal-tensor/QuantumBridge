from quantumbridge.compat.qiskit_dynamics import (
    build_single_qubit_hamiltonian,
    run_dephasing_metadata_simulation_native,
    run_rabi_drive_dynamics_native,
    run_z_precession_native,
)


def test_single_qubit_hamiltonian_shape():
    model = build_single_qubit_hamiltonian(axis="z", frequency=1.0)
    assert model["axis"] == "z"
    assert model["frequency"] == 1.0
    assert len(model["matrix_serialized"]) == 2


def test_native_dynamics_workflows_run():
    assert run_z_precession_native().workflow == "z_precession_native"
    assert run_rabi_drive_dynamics_native().workflow == "rabi_drive_dynamics_native"
    assert run_dephasing_metadata_simulation_native(gamma=0.05).workflow == "dephasing_metadata_simulation_native"
