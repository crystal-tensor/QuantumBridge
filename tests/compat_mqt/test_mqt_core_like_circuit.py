from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import (
    build_mqt_core_like_circuit_from_quantumbridge_ir,
    mqt_core_like_dict_to_quantumbridge_ir,
    quantumbridge_ir_to_mqt_core_like_dict,
    validate_mqt_core_like_circuit,
)


def test_mqt_core_like_circuit_validates_and_roundtrips_ir():
    circuit = Circuit(2, 2).h(0).cx(0, 1).measure(0, 0).measure(1, 1)

    data = quantumbridge_ir_to_mqt_core_like_dict(circuit.to_ir())
    validate_mqt_core_like_circuit(data)
    restored = mqt_core_like_dict_to_quantumbridge_ir(data)
    result = build_mqt_core_like_circuit_from_quantumbridge_ir(restored)

    assert result.num_qubits == 2
    assert [op["name"] for op in result.operations] == ["h", "cx"]
    assert len(restored.instructions) == 2
    assert result.production_ready is False
