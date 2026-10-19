# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent native example; no Qiskit/PennyLane dependency or hardware call.

from quantumbridge import Circuit, MatrixProductStateDevice, Result
from quantumbridge.noise import AmplitudeDampingChannel
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def main():
    circuit = Circuit(100).h(0)
    for wire in range(99):
        circuit.cx(wire, wire + 1)
    device = MatrixProductStateDevice(max_memory_mb=2)
    result = device.run(circuit)
    state = result.matrix_product_state()
    print("Qubits:", state.num_qubits)
    print("Maximum bond:", max(state.bond_dimensions))
    print("Tensor bytes:", sum(tensor.nbytes for tensor in state.tensors))
    print("Global X correlation:", state.expectation_pauli("X" * 100).real)
    print("End-wire probabilities:", device.probabilities(circuit, wires=[99, 0]))
    restored = Result.from_json(result.to_json()).matrix_product_state()
    print("JSON roundtrip correlation:", restored.expectation_pauli("X" * 100).real)
    counts = device.run_shots(circuit, shots=16, seed=7).counts()
    print("100-wire shot outcomes:", {label[0] + "..." + label[-1]: count for label, count in counts.items()})

    def program(tape, angle):
        tape.ry(angle, 0)
        tape.channel(AmplitudeDampingChannel(.3), [0])
        return tape.expval(PauliZ(0)), tape.density_matrix([0])

    expectation, density = QNode(program, 1, device=MatrixProductStateDevice())(.7)
    print("Noisy MPS QNode expectation:", expectation)
    print("Noisy MPS reduced density:", density.round(6).tolist())


if __name__ == "__main__":
    main()
