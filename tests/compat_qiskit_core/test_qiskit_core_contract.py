# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

from quantumbridge.compat import qiskit_core
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_core_contract_and_basic_circuit_bridge():
    assert_qiskit_contract(qiskit_core)
    from quantumbridge.core import Circuit
    from quantumbridge.compat.qiskit_core.circuit_adapter import (
        basic_gate_inventory,
        quantum_circuit_metadata,
        quantumbridge_ir_to_qiskit_circuit,
        qiskit_circuit_to_quantumbridge_ir,
    )

    circuit = Circuit(2, 1)
    circuit.h(0).x(1).y(0).z(1).rx(0.1, 0).ry(0.2, 1).rz(0.3, 0).phase(0.4, 1).cx(0, 1).cz(1, 0).swap(0, 1).measure(0, 0)
    qiskit_circuit = quantumbridge_ir_to_qiskit_circuit(circuit.to_ir())
    metadata = quantum_circuit_metadata(qiskit_circuit)
    roundtrip_ir = qiskit_circuit_to_quantumbridge_ir(qiskit_circuit).to_dict()
    assert metadata["num_qubits"] == 2
    assert "swap" in metadata["operations"]
    assert roundtrip_ir["instructions"][0]["op"] == "h"
    assert {"phase", "swap", "measure"} <= {row["name"] for row in basic_gate_inventory()}
