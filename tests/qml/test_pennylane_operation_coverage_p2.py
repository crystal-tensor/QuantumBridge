import warnings

import pytest

from quantumbridge.compat.pennylane_adapter import circuit_and_observable_from_pennylane_tape

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_p2_operation_bridge():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tape = qml.tape.QuantumScript(
            [qml.PhaseShift(0.1, 0), qml.Rot(0.1, 0.2, 0.3, 0), qml.SWAP([0, 1])],
            [],
        )
    circuit, _ = circuit_and_observable_from_pennylane_tape(tape)
    assert [op.name for op in circuit.operations] == ["phase", "rz", "ry", "rz", "swap"]
