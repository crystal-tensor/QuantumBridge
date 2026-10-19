# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

from quantumbridge import PauliZ
from quantumbridge.qml import NativeQNode


def program(tape, theta):
    tape.ry(theta, 0)
    return {"z": tape.expval(PauliZ(0)), "counts": tape.counts([0])}


def main():
    node = NativeQNode(program, 1, shots=[100, (200, 2)], seed=17)
    values = node(.8)
    print("Independent shot partitions:", values)
    print("Execution metadata:", node.last_metadata)
    assert [sum(part["counts"].values()) for part in values] == [100, 200, 200]


if __name__ == "__main__": main()
