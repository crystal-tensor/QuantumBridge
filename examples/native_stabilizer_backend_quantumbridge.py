# Independently implemented QuantumBridge example; no upstream source copied.
"""Run native Backend/Job, dynamic feedback and V2 primitive workflows."""

from quantumbridge import BackendEstimator, BackendSampler, Circuit, StabilizerBackend, StabilizerDevice
from quantumbridge.noise import BitFlipChannel, NoiseModel
from quantumbridge.operators import Pauli


def main():
    circuit = Circuit(64)
    for wire in range(64):
        circuit.h(wire)
    backend = StabilizerBackend()
    result = backend.run(circuit, shots=16, seed_simulator=2026, memory=True).result()
    print("64-qubit shots:", sum(result.counts().values()))
    print("Distinct outcomes:", len(result.counts()))
    estimator = BackendEstimator(backend).run([(circuit, Pauli("X" * 64))])
    print("X parity:", estimator[0].data.evs)
    feedback = Circuit(1, 2).h(0).measure(0, 0)
    feedback.if_else((0, 1), Circuit(1).x(0), inplace=True)
    feedback.measure(0, 1)
    print("Feedback records:", StabilizerDevice().run(feedback).probabilities())
    sampled = BackendSampler(backend, options={"shots": 8, "seed_simulator": 4}).run([(feedback,)])
    print("Ordered V2 memory:", list(sampled[0].data.meas))
    noise = NoiseModel().add_channel(BitFlipChannel(.2))
    print("Noisy Z expectation:", backend.run(Circuit(1), observable=Pauli("Z"), noise_model=noise).result().expectation_value())


if __name__ == "__main__":
    main()
