# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Conditional snapshots capture actual feedback and physical collapse."""
import numpy as np
from quantumbridge import Circuit
from quantumbridge.noise import NoiseModel, ReadoutError
from quantumbridge.simulator import NativeAerSimulator


def main():
    model = NoiseModel().add_readout_error(ReadoutError([[0, 1], [0, 1]]), [0])
    circuit = Circuit(2, 2).measure(0, 0)
    circuit = circuit.if_test((0, 1), Circuit(2, 2).x(1)).measure(1, 1)
    circuit.save_density_matrix(label="feedback", conditional=True, pershot=True)
    result = NativeAerSimulator("density_matrix", shots=8, noise_model=model,
                                memory=True, seed_simulator=6).run(circuit).result()
    assert result.get_counts() == {"11": 8}
    snapshots = result.data()["feedback"]["0x3"]
    for snapshot in snapshots:
        np.testing.assert_allclose(snapshot, np.diag([0, 1, 0, 0]))
    print("Stored bits:", result.get_memory(), "actual feedback snapshots:", len(snapshots))


if __name__ == "__main__":
    main()
