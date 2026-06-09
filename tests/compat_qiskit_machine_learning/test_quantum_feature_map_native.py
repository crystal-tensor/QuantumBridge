import numpy as np

from quantumbridge.compat.qiskit_machine_learning import (
    build_angle_feature_map,
    describe_feature_map,
    feature_map_statevector,
    feature_map_to_quantumbridge_ir,
)


def test_feature_map_produces_circuit_metadata_and_statevector():
    circuit = build_angle_feature_map([0.25, -0.5])
    state = feature_map_statevector([0.25, -0.5])
    description = describe_feature_map([0.25, -0.5])

    assert circuit.num_qubits == 2
    assert circuit.operations
    assert np.isclose(np.sum(np.abs(state) ** 2), 1.0)
    assert description["metadata"]["provenance"]["cloud_access"] is False


def test_feature_map_to_ir():
    ir = feature_map_to_quantumbridge_ir([0.1, 0.2])

    assert ir is not None
