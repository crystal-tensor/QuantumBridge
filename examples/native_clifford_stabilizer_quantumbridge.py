# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Execute a 64-qubit GHZ state without dense statevector simulation."""

from quantumbridge import Circuit
from quantumbridge.information import Clifford, StabilizerState, random_clifford
from quantumbridge.operators import Pauli


def main():
    width = 64
    circuit = Circuit(width).h(0)
    for wire in range(1, width):
        circuit.cx(0, wire)
    clifford = Clifford(circuit)
    state = StabilizerState(clifford)
    state.seed(2026)
    print("Tableau bytes:", clifford.tableau.nbytes)
    print("GHZ probabilities:", state.probabilities_dict())
    print("X parity:", state.expectation_value(Pauli("X" * width)))
    print("Samples:", state.sample_counts(8))
    print("Synthesized circuit roundtrip:", Clifford(clifford.to_circuit()) == clifford)
    random_gate = random_clifford(8, seed=73)
    print("Random Clifford inverse:", random_gate.compose(random_gate.adjoint()) == Clifford.identity(8))


if __name__ == "__main__":
    main()
