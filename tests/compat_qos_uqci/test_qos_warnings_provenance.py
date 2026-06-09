from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.mock_runtime import run_qos_uqci_mock_runtime


def test_qos_warnings_and_provenance_are_clear():
    result = run_qos_uqci_mock_runtime(qos_uqci_bell_circuit())
    joined = " ".join(result.warnings).lower()
    assert "mock backend" in joined
    assert "token" in joined
    assert result.provenance["official_endorsement_claim"] is False
    assert result.provenance["production_backend_claim"] is False
