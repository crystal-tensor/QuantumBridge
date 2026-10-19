# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Run native phase-preserving Pauli algebra and a quantum expectation."""

import json

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.information import random_pauli, random_pauli_list
from quantumbridge.operators import Pauli, PauliList


def run_example():
    operators = PauliList(["XX", "YY", "ZZ", "IX", "ZI"])
    groups = operators.group_commuting()
    circuit = Circuit(2).h(0).cx(0, 1)
    return {
        "implementation": "quantumbridge_native",
        "product_xy": (Pauli("X") @ Pauli("Y")).to_label(),
        "composition_xy": Pauli("X").compose("Y").to_label(),
        "bell_expectation_minus_xx": StatevectorDevice().expectation(circuit, Pauli("-XX")),
        "commuting_groups": [group.to_labels() for group in groups],
        "seeded_pauli": random_pauli(3, group_phase=True, seed=11).to_label(),
        "seeded_pauli_list": random_pauli_list(3, size=4, seed=11).to_labels(),
    }


if __name__ == "__main__":
    print(json.dumps(run_example(), indent=2))
