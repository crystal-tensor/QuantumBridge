from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.openqasm_bridge import (
    build_openqasm_compatibility_artifact,
    validate_openqasm_compatibility_artifact,
)


def test_qos_openqasm_compatibility_artifact_exists():
    artifact = build_openqasm_compatibility_artifact(qos_uqci_bell_circuit())
    assert validate_openqasm_compatibility_artifact(artifact)
    assert "OPENQASM 2.0" in artifact["qasm"]
    assert artifact["canonical_ir"] == "qos_uqci_clean_room_ir"
