# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.devices import StatevectorDevice
from quantumbridge.information import Operator


def test_circuit_compose_maps_qubits_and_classical_bits():
    base = Circuit(2, 2).h(0)
    sub = Circuit(1, 1).x(0).measure(0, 0)

    composed = base.compose(sub, qubits=[1], clbits=[1])

    assert [op.name for op in composed.operations] == ["h", "x"]
    assert composed.operations[-1].targets == (1,)
    assert composed.measurements[-1].wire == 1
    assert composed.measurements[-1].bit == 1
    assert base.operations[-1].name == "h"


def test_circuit_inverse_and_power_execute_as_unitary_identities():
    circuit = Circuit(1).h(0).rx(0.25, 0).s(0)
    combined = circuit.compose(circuit.inverse())
    matrix = Operator.from_circuit(combined).to_matrix()

    np.testing.assert_allclose(matrix, np.eye(2), atol=1e-12)

    repeated = Circuit(1).x(0).power(2)
    assert [op.name for op in repeated.operations] == ["x", "x"]
    assert StatevectorDevice().probabilities(repeated) == {"0": 1.0, "1": 0.0}


def test_circuit_control_generates_executable_controlled_unitary():
    controlled_h = Circuit(1).h(0).control()
    circuit = Circuit(2).x(0).compose(controlled_h)

    probabilities = StatevectorDevice().probabilities(circuit)

    assert controlled_h.num_qubits == 2
    assert controlled_h.operations[0].metadata["controlled_operation"] == "h"
    assert abs(probabilities["10"] - 0.5) < 1e-12
    assert abs(probabilities["11"] - 0.5) < 1e-12


def test_circuit_condition_and_calibration_are_preserved_in_ir_metadata():
    circuit = Circuit(1, 1).x(0).c_if(0, 1)
    circuit.add_calibration("x", [0], schedule={"pulse": "drag"}, params=())

    ir = circuit.to_ir().to_dict()

    assert ir["instructions"][0]["metadata"]["condition"] == {"bits": [0], "value": 1}
    assert circuit.get_calibration("x", [0]) == {"pulse": "drag"}


def test_circuit_metrics_barrier_delay_and_measurement_helpers():
    circuit = Circuit(2).h(0).barrier().delay(4, 1).cx(0, 1).measure_all()

    assert circuit.size() == 6
    assert circuit.count_ops() == {"h": 1, "barrier": 1, "delay": 1, "cx": 1, "measure": 2}
    assert circuit.depth() == 3

    probabilities = StatevectorDevice().probabilities(circuit.remove_final_measurements())
    assert abs(probabilities["00"] - 0.5) < 1e-12
    assert abs(probabilities["11"] - 0.5) < 1e-12


def test_circuit_if_else_records_condition_and_branch_metadata_in_ir():
    true_body = Circuit(1, 1, name="true").x(0)
    false_body = Circuit(1, 1, name="false").z(0)
    circuit = Circuit(1, 1).if_else((0, 1), true_body, false_body, inplace=False)

    ir = circuit.to_ir().to_dict()

    assert circuit.metadata["control_flow"][0]["type"] == "if_else"
    assert ir["instructions"][0]["metadata"]["condition"] == {"bits": [0], "value": 1}
    assert ir["instructions"][0]["metadata"]["control_flow"]["branch"] == "true"
    assert ir["instructions"][1]["metadata"]["control_flow"]["branch"] == "false"
