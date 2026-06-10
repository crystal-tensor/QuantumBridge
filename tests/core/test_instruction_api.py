# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit, Instruction, StatevectorDevice
from quantumbridge.information import Operator


def test_circuit_to_instruction_appends_definition_on_mapped_qubits():
    bell_block = Circuit(2, name="bell_block").h(0).cx(0, 1).to_instruction()
    circuit = Circuit(3).x(0).append(bell_block, [1, 2])

    probabilities = StatevectorDevice().probabilities(circuit)

    assert [op.metadata["instruction"]["name"] for op in circuit.operations[-2:]] == ["bell_block", "bell_block"]
    assert abs(probabilities["100"] - 0.5) < 1e-12
    assert abs(probabilities["111"] - 0.5) < 1e-12


def test_instruction_control_inverse_and_power_are_executable():
    block = Circuit(1).rx(0.2, 0).h(0).to_instruction("rxh")
    controlled = block.control()
    circuit = Circuit(2).x(0).append(controlled, [0, 1])
    identity = Circuit.from_instruction(block.power(2)).compose(Circuit.from_instruction(block.power(2)).inverse())

    assert controlled.num_qubits == 2
    assert circuit.operations[0].name == "x"
    assert np.isclose(np.linalg.norm(StatevectorDevice().statevector(circuit)), 1.0)
    np.testing.assert_allclose(Operator.from_circuit(identity).to_matrix(), np.eye(2), atol=1e-12)


def test_opaque_instruction_uses_matrix_metadata_and_roundtrips_to_circuit():
    matrix = np.array([[0, 1], [1, 0]], dtype=complex)
    instruction = Instruction("custom_x", 1, metadata={"matrix": matrix, "source": "unit-test"})
    circuit = Circuit(1).append(instruction, [0])
    restored = Circuit.from_instruction(instruction.inverse("custom_x_dg"))

    assert StatevectorDevice().probabilities(circuit)["1"] == 1.0
    assert restored.operations[0].name == "custom_x_dg"
    np.testing.assert_allclose(restored.operations[0].metadata["matrix"], matrix.conj().T)


def test_instruction_append_preserves_clbit_mapping_for_defined_measurements():
    measure_block = Circuit(1, 1).x(0).measure(0, 0).to_instruction("prepare_and_measure")
    circuit = Circuit(2, 2).append(measure_block, [1], clbits=[0])

    assert circuit.operations[0].targets == (1,)
    assert circuit.measurements[0].wire == 1
    assert circuit.measurements[0].bit == 0
