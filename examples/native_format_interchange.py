"""Standard payloads with separately identified external provenance metadata."""
from quantumbridge import Circuit,Parameter,PauliZ
from quantumbridge.qml import QNode
from quantumbridge.serialization import serialize_circuit,deserialize_circuit,convert_circuit_format


def main():
    theta = Parameter('theta')
    circuit = Circuit(1,name='training',metadata={'purpose':'explicit external sidecar'}).ry(theta*theta+theta,0)
    source = serialize_circuit(circuit,'qasm3',metadata_policy='external')
    binary = convert_circuit_format(source,'qasm3','qpy',target_options={'metadata_policy':'external'})
    restored = deserialize_circuit(binary)
    original_node = QNode.from_circuit(circuit,PauliZ(0))
    restored_node = QNode.from_circuit(restored,PauliZ(0))
    assert abs(original_node.gradient(.3,method='adjoint')-restored_node.gradient(.3,method='adjoint')) < 1e-12
    assert restored.name == 'training' and restored.metadata['purpose'] == circuit.metadata['purpose']
    print('QASM3 -> real QPY; sidecar keys:',sorted(binary.sidecar))
    print('Restored native QNode value/gradient:',restored_node(.3),restored_node.gradient(.3,method='adjoint'))


if __name__ == '__main__': main()
