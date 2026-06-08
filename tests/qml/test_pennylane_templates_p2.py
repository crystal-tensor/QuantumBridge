from quantumbridge.core import Circuit
from quantumbridge.qml import amplitude_embedding, basic_entangler_layers, hardware_efficient_ansatz, strongly_entangling_layers


def test_qml_p2_templates_are_native_and_marked():
    circuit = Circuit(2)
    basic_entangler_layers(circuit, [[0.1, 0.2]])
    strongly_entangling_layers(circuit, [[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]])
    hardware_efficient_ansatz(circuit, [[0.1, 0.2]])
    amplitude_embedding(circuit, [1, 0, 0, 0])
    assert circuit.operations
    assert circuit.metadata["amplitude_embedding"]["status"] == "planned-native-state-preparation"
