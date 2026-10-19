# Independent QuantumBridge example. No upstream source copied.
"""Run mixed-state circuits through the native backend and QNode."""

import numpy as np

from quantumbridge import Circuit, DensityMatrixBackend, DensityMatrixDevice, Result
from quantumbridge.information import DensityMatrix
from quantumbridge.noise import AmplitudeDampingChannel, NoiseModel, NoisyEstimator
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliX, PauliZ


def main():
    circuit = Circuit(2).ry(.7, 0).cx(0, 1).channel(AmplitudeDampingChannel(.3), [1])
    result = DensityMatrixBackend().run(circuit).result()
    matrix = result.density_matrix()
    print("Trace:", float(np.trace(matrix).real))
    print("Purity:", DensityMatrix(matrix).purity())
    print("JSON roundtrip:", np.allclose(Result.from_json(result.to_json()).density_matrix(), matrix))

    def program(tape, theta):
        tape.ry(theta, 0)
        tape.amplitude_damping(.3, 0)
        return tape.state(), tape.expval(PauliZ(0))

    state, expectation = QNode(program, 1, device=DensityMatrixDevice())(.7)
    print("QNode mixed state:", state.round(6).tolist())
    print("QNode Z expectation:", expectation)
    noise = NoiseModel().add_channel(AmplitudeDampingChannel(.3))
    print("Noisy X expectation:", NoisyEstimator(noise).expectation(Circuit(1).h(0), PauliX(0)))


if __name__ == "__main__":
    main()
