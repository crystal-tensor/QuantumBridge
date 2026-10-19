# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native example without upstream SDKs or hardware calls.

from quantumbridge import Circuit, DensityMatrixDevice
from quantumbridge.core.classical import UInt


def main():
    circuit = Circuit(1, 1)
    counter = circuit.add_var("counter", UInt(4), 0)
    body = Circuit(1, 1).store(counter, counter + 1)
    body.if_else(counter == 2, Circuit(1, 1).continue_loop(), inplace=True)
    body.x(0)
    circuit.while_loop(counter < 4, body, inplace=True).measure(0, 0)
    result = DensityMatrixDevice().run(circuit)
    print("Runtime loop probabilities:", result.probabilities())
    print("Final classical storage:", result.metadata()["classical_ensemble"])


if __name__ == "__main__": main()
