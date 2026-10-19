# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Local mixed state and a compact 100-wire noisy GHZ experiment."""
import numpy as np
from quantumbridge import Circuit, PauliZ
from quantumbridge.information import MatrixProductState
from quantumbridge.noise import NoiseModel, pauli_error
from quantumbridge.simulator import NativeAerSimulator


def main():
    circuit = Circuit(100, 2).h(0)
    for wire in range(99):
        circuit.cx(wire, wire + 1)
    circuit.save_matrix_product_state().save_density_matrix([0], label="local")
    circuit.save_expectation_value(PauliZ(99), label="z").measure(0, 0).measure(99, 1)
    model = NoiseModel().add_quantum_error(pauli_error([("X", 1.)]), "h", [0])
    result = NativeAerSimulator("matrix_product_state", shots=8, noise_model=model,
                                seed_simulator=5, memory=True).run(circuit).result()
    data = result.data()
    state = MatrixProductState.from_dict(data["matrix_product_state"])
    assert state.num_qubits == 100 and state.peak_bond_dimension == 2
    np.testing.assert_allclose(data["local"], np.eye(2) / 2, atol=1e-12)
    assert abs(data["z"]) < 1e-12 and set(result.get_counts()) <= {"00", "11"}
    metadata = result.results[0].metadata()
    print(result.get_counts(), {key: metadata[key] for key in (
        "max_bond_observed", "tensor_storage_bytes", "snapshot_storage_bytes", "max_discarded_weight")})


if __name__ == "__main__":
    main()
