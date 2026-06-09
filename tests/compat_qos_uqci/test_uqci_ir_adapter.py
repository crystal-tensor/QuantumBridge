from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.uqci_ir_adapter import (
    quantumbridge_ir_to_uqci_ir,
    uqci_ir_to_quantumbridge_ir,
    validate_uqci_ir,
)


def test_quantumbridge_ir_to_uqci_ir_roundtrip():
    payload = quantumbridge_ir_to_uqci_ir(qos_uqci_bell_circuit())
    assert validate_uqci_ir(payload)
    assert payload["operations"][0]["gate"] == "h"
    roundtrip = uqci_ir_to_quantumbridge_ir(payload)
    assert roundtrip["registers"]["quantum"]["size"] == 2
    assert roundtrip["instructions"][1]["op"] == "cx"
