from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.payload_adapter import (
    quantumbridge_ir_to_quafu_payload,
    quafu_payload_to_quantumbridge_ir,
    validate_quafu_payload,
)


def test_quafu_payload_roundtrip():
    payload = quantumbridge_ir_to_quafu_payload(quafu_bell_circuit())
    assert validate_quafu_payload(payload)
    assert payload["gates"][0]["name"] == "h"
    roundtrip = quafu_payload_to_quantumbridge_ir(payload)
    assert roundtrip["instructions"][1]["op"] == "cx"
