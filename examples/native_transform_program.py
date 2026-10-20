# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free real multi-Tape execution with reverse result reconstruction."""

from quantumbridge import StatevectorDevice
from quantumbridge.core import Parameter
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import TransformProgram, execute_transform, merge_rotations, split_hamiltonian
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def main():
    theta = Parameter("theta")
    hamiltonian = Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(1)), (-.1, PauliZ(0).tensor(PauliZ(1)))])
    tape = Tape(2)
    tape.ry(theta, 0)
    tape.ry(.13, 0)
    tape.h(1)
    tape.cx(0, 1)
    tape.expval(hamiltonian)
    transforms = TransformProgram([split_hamiltonian, merge_rotations])
    value, metadata = execute_transform(tape, transforms, bindings={theta: .41}, return_metadata=True)
    expected = StatevectorDevice().expectation(tape.circuit.bind({theta:.41}), hamiltonian)
    for execution in metadata["executions"]:
        print("executed", execution["tape_index"], execution["execution_id"],
              "operations", execution["operation_count"])
    print("postprocessing_order", metadata["postprocessing_order"])
    print("reconstructed", value, "unsplit", expected, "absolute_error", abs(value-expected))
    assert metadata["executed_tape_count"] == 3 and abs(value-expected) < 1e-10
    print("B1 checkpoint only; QWC, shot allocation and transformed autodiff remain incomplete.")


if __name__ == "__main__":
    main()
