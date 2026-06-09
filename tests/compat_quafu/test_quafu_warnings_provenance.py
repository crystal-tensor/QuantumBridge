from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.mock_backend import run_quafu_mock_backend


def test_quafu_warnings_and_provenance_are_clear():
    result = run_quafu_mock_backend(quafu_bell_circuit())
    joined = " ".join(result.warnings).lower()
    assert "mock backend" in joined
    assert "token" in joined
    assert result.provenance["official_endorsement_claim"] is False
    assert result.provenance["production_backend_claim"] is False
