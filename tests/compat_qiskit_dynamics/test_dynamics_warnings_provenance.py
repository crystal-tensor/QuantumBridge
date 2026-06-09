from quantumbridge.compat.qiskit_dynamics import run_rabi_drive_dynamics_native


def test_dynamics_warnings_and_provenance_are_explicit():
    result = run_rabi_drive_dynamics_native()
    joined = " ".join(result.warnings).lower()
    assert "not a full qiskit dynamics replacement" in joined
    assert "not production dynamics simulation software" in joined
    assert result.provenance["stage"] == "9I"
    assert result.provenance["source"] == "clean_room_native"
