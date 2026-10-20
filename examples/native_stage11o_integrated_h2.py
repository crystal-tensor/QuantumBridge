# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""One real geometry-derived Hamiltonian, standard VQE and coherent feedback."""

from quantumbridge import qchem, templates
from quantumbridge.qml import QNode
from quantumbridge.transforms import defer_measurements, split_non_commuting


def main():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
    def prepare(t, theta):
        t.x(0)
        t.x(1)
        qchem.apply_fermionic_excitation(t, theta, [0, 1, 2, 3])
    def standard(t, theta):
        prepare(t, theta)
        return t.expval(problem.hamiltonian)
    def feedback(t, theta):
        prepare(t, theta)
        record = t.measure(0)
        t.h(0)
        t.cond(record, lambda branch: templates.AngleEmbedding([.2], [2], rotation="Y").apply(branch))
        return t.expval(problem.hamiltonian)
    reference = split_non_commuting(QNode(standard, 4))
    standard_energy, standard_gradient = reference.execute_and_compute_derivatives(.3)
    assert abs(standard_energy + 1.0279252771620968) < 2e-11
    assert abs(standard_gradient - .40622294673301496) < 2e-10
    original = QNode(feedback, 4, diff_method="parameter-shift")
    node = split_non_commuting(defer_measurements(QNode(feedback, 4)))
    energy, gradient = node.execute_and_compute_derivatives(.3)
    assert abs(energy - original(.3)) < 2e-11
    assert abs(gradient - original.gradient(.3)) < 2e-10
    theta = .3
    for _ in range(2): theta -= .2 * node.gradient(theta)
    assert node(theta) < energy
    print({"geometry": "H2 1.4 bohr / native Gaussian-RHF-JW", "standard_energy": standard_energy,
           "standard_gradient": standard_gradient, "feedback_energy": energy, "feedback_gradient": gradient,
           "optimized_theta": theta, "optimized_feedback_energy": node(theta),
           "ancillas_per_coherent_child": node.last_metadata["deferred_measurements"][0]["ancilla_count"]})
    print("One integral/SCF construction. Feedback may change electron number; its energy is not claimed to be a molecular ground state.")


if __name__ == "__main__":
    main()
