from quantumbridge.compat.qiskit_experiments import run_t1_experiment_native


def test_experiments_warnings_and_provenance_are_explicit():
    result = run_t1_experiment_native()
    joined = " ".join(result.warnings).lower()
    assert "not a full qiskit experiments replacement" in joined
    assert "not hardware experiment results" in joined
    assert result.provenance["stage"] == "9I"
    assert result.provenance["source"] == "clean_room_native"
