# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual intermediate saves and full-state replacement, without an SDK."""
import numpy as np
from quantumbridge import Circuit
from quantumbridge.simulator import NativeAerSimulator, AerResult


def main():
    circuit = (Circuit(1).h(0).save_statevector(label="plus")
               .z(0).save_statevector(label="minus")
               .set_statevector([1, 0]).x(0).save_statevector(label="replaced"))
    result = NativeAerSimulator("statevector", shots=None).run(circuit).result()
    data = AerResult.from_json(result.to_json()).data()
    np.testing.assert_allclose(data["plus"], np.ones(2) / np.sqrt(2))
    np.testing.assert_allclose(data["minus"], np.array([1, -1]) / np.sqrt(2))
    np.testing.assert_allclose(data["replaced"], [0, 1])
    print({label: value.tolist() for label, value in data.items()})


if __name__ == "__main__":
    main()
