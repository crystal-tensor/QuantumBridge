from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.job_adapter import build_quafu_job_spec, validate_quafu_job_spec


def test_quafu_job_spec_validates():
    spec = build_quafu_job_spec(quafu_bell_circuit(), shots=128, seed=23)
    assert validate_quafu_job_spec(spec)
    assert spec["target"] == "quafu"
    assert spec["execution_mode"] == "offline_mock"
