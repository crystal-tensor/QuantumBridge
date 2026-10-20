# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Repeated native transformed QNode calls with auditable parameter rebinding."""
import numpy as np
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, split_hamiltonian, merge_rotations
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def main():
    hamiltonian = Hamiltonian([(.7,PauliZ(0)),(.2,PauliX(1)),(-.1,PauliZ(0).tensor(PauliZ(1)))])
    def circuit(tape,theta):
        tape.ry(theta,0)
        tape.ry(2*theta,0)
        tape.h(1)
        tape.cx(0,1)
        return tape.expval(hamiltonian)
    original = QNode(circuit,2)
    node = TransformProgram([split_hamiltonian,merge_rotations])(original)
    ids = set()
    for theta in [.2,.7]:
        value = node(theta)
        assert abs(value-(.7*np.cos(3*theta)+.2)) < 1e-12
        assert abs(value-original(theta)) < 1e-12
        current = {row["execution_id"] for row in node.last_metadata["executions"]}
        assert len(current) == 3 and not current & ids
        ids.update(current)
        print({"theta":theta,"value":value,"child_tapes":3,"execution_ids":sorted(current)})
    print("Current inputs reconstruct new batches; transformed native VJP remains pending.")


if __name__ == "__main__":
    main()
