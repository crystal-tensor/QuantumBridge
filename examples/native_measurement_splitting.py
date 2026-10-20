# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""One Tape with distinct Pauli measurements, not hardware QWC grouping."""
import numpy as np
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import split_to_single_terms, execute_transform
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliZ


def main():
    tape = Tape(2,seed=7)
    tape.ry(.3,0)
    first = tape.expval(Hamiltonian([(1.,PauliZ(0)),(2.,PauliString([])),(0.,PauliX(1)),(1.,PauliZ(0))]))
    second = tape.expval(PauliZ(0))
    tape.set_output({"energy":first,"z":second})
    children,_ = split_to_single_terms(tape)
    value, metadata = execute_transform(tape,split_to_single_terms,return_metadata=True)
    assert len(children) == 1 and len(children[0].measurements) == 2
    assert abs(value["energy"]-(2+2*np.cos(.3))) < 1e-12
    sampled = execute_transform(tape,split_to_single_terms,shots=[128,256])
    print({"child_tapes":len(children),"unique_measurements":2,"analytic":value,
           "sampled_partitions":sampled,"execution_id":metadata["executions"][0]["execution_id"]})
    print("Per-measurement sampling only; joint QWC samples and total-shot allocation remain pending.")


if __name__ == "__main__":
    main()
