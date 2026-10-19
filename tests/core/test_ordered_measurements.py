# Independently implemented QuantumBridge tests; no upstream source copied.

import numpy as np
import pytest

from quantumbridge import Circuit, Measurement, StabilizerDevice, StatevectorDevice
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.qasm import loads


def names(circuit):
    return ["measure" if isinstance(item, Measurement) else item.name for item in circuit.iter_instructions()]


def test_measurement_order_survives_copy_binding_and_ir_roundtrip():
    circuit = Circuit(1, 2).h(0).measure(0, 0).h(0).measure(0, 1)
    assert names(circuit) == ["h", "measure", "h", "measure"]
    for candidate in (circuit.copy(), circuit.assign_parameters({}), circuit_from_ir(circuit.to_ir())):
        assert names(candidate) == names(circuit)
        assert StabilizerDevice().run(candidate).probabilities() == {"00": .25, "01": .25, "10": .25, "11": .25}
    assert circuit.to_ir().to_dict()["measurements"][0]["metadata"]["operation_index"] == 1
    assert len(circuit.remove_final_measurements().measurements) == 1
    assert names(circuit.remove_final_measurements()) == ["h", "measure", "h"]


def test_compose_front_append_and_instruction_preserve_read_positions():
    first = Circuit(1, 2).x(0).measure(0, 0)
    second = Circuit(1, 1).x(0).measure(0, 0)
    appended = first.compose(second, clbits=[1])
    prepended = first.compose(second, clbits=[1], front=True)
    assert names(appended) == names(prepended) == ["x", "measure", "x", "measure"]
    assert StabilizerDevice().run(appended).probabilities() == {"10": 1}
    assert StabilizerDevice().run(prepended).probabilities() == {"01": 1}
    defined = Circuit(1, 2).append(appended.to_instruction(), [0], clbits=[1, 0])
    assert names(defined) == names(appended)
    assert StabilizerDevice().run(defined).probabilities() == {"01": 1}


def test_classical_condition_remapping_and_dependency_depth():
    block = Circuit(1, 1).x(0).c_if(0, 1)
    circuit = Circuit(2, 3).x(0).measure(0, 2).compose(block, qubits=[1], clbits=[2])
    assert circuit.operations[-1].metadata["condition"]["bits"] == [2]
    assert StabilizerDevice().probabilities(circuit) == {"11": 1}
    assert circuit.depth() == 3


def test_qasm_roundtrip_retains_midcircuit_measurement_and_reset():
    circuit = Circuit(1, 2).h(0).measure(0, 0).reset(0).x(0).measure(0, 1)
    restored = loads(circuit.to_openqasm())
    assert names(restored) == names(circuit)
    assert StabilizerDevice().run(restored).probabilities() == {"01": .5, "11": .5}


def test_non_dynamic_devices_no_longer_ignore_midcircuit_operations():
    for circuit in (Circuit(1, 1).h(0).measure(0, 0).h(0), Circuit(1).reset(0), Circuit(1, 1).x(0).c_if(0, 1)):
        with pytest.raises(ValueError):
            StatevectorDevice().statevector(circuit)
        with pytest.raises(ValueError):
            Operator.from_circuit(circuit)
    np.testing.assert_allclose(StatevectorDevice().statevector(Circuit(1, 1).x(0).measure(0, 0)), [0, 1])


def test_legacy_terminal_measurements_and_invalid_positions():
    circuit = Circuit(1, 1).x(0)
    circuit.measurements.append(Measurement(0, 0))
    assert names(circuit) == ["x", "measure"]
    assert StabilizerDevice().run(circuit).probabilities() == {"1": 1}
    circuit.measurements[0].metadata["operation_index"] = 20
    with pytest.raises(ValueError, match="operation_index"):
        list(circuit.iter_instructions())
