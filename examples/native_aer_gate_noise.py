# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Physical gate-bound damping, not noise applied to final counts."""
import numpy as np
from quantumbridge import Circuit, PauliZ
from quantumbridge.noise import NoiseModel, amplitude_damping_error
from quantumbridge.simulator import NativeAerSimulator


def main():
    model = NoiseModel().add_quantum_error(amplitude_damping_error(.25), "x", [0])
    circuit = (Circuit(1).x(0).save_density_matrix(label="first")
               .x(0).save_density_matrix(label="second")
               .save_expectation_value(PauliZ(0), label="z"))
    data = NativeAerSimulator("density_matrix", shots=None, noise_model=model).run(circuit).result().data()
    np.testing.assert_allclose(data["first"], np.diag([.25, .75]))
    np.testing.assert_allclose(data["second"], np.diag([.8125, .1875]))
    assert abs(data["z"] - .625) < 1e-12
    print("After first/second physical X:", data["first"], data["second"], "Z =", data["z"])


if __name__ == "__main__":
    main()
