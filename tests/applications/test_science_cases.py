# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Numerical and reporting contracts for the offline scientific tutorials."""

import numpy as np
import pytest

from quantumbridge.applications.common import (
    diagonal_cost_hamiltonian,
    diagonal_qaoa_circuit,
    run_local_case,
)
from quantumbridge.applications.science import (
    BUILDERS,
    dynamics_circuit,
    hubbard_hamiltonian,
)
from quantumbridge.devices import StatevectorDevice


@pytest.fixture(scope="module", params=list(BUILDERS))
def study(request):
    case = BUILDERS[request.param]()
    return case, run_local_case(case)


def test_case_evidence_is_offline_reproducible_and_shot_conserving(study):
    case, evidence = study
    assert evidence == run_local_case(case)
    assert evidence["hardware_access"] is False
    assert evidence["new_cloud_tasks"] == 0
    for observation in evidence["experiments"].values():
        assert sum(observation["counts"].values()) == 1024
        assert sum(observation["ideal_probabilities"]) == pytest.approx(1)
        assert observation["openqasm2"].startswith("OPENQASM 2.0;")
        assert observation["bit_order"] == "q0-first"
    for estimate in evidence["estimates"].values():
        assert estimate["standard_error"] >= 0
        assert (
            abs(estimate["estimate"] - estimate["ideal_reference"])
            < 6 * estimate["standard_error"] + 0.01
        )


def test_domain_specific_baselines(study):
    case, evidence = study
    if case.direction == "chemistry":
        assert case.reference["exact_ground_energy_hartree"] == pytest.approx(
            -1.137306, abs=3e-6
        )
        assert 0 <= case.outputs["variational_gap_hartree"] < 1e-6
        assert len(case.experiments) == 14
        assert evidence["summary"]["energy_standard_error_hartree"] > 0
    elif case.direction == "biomedicine":
        assert case.reference["feasible_count"] == 9
        assert case.reference["best_objective"] == -1
        assert evidence["summary"]["observed_objective_gap"] == 0
        for row in case.intermediate["candidates"]:
            if row["feasible"]:
                assert len(set(row["coordinates"])) == 4
                assert all(
                    abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                    for a, b in zip(row["coordinates"], row["coordinates"][1:])
                )
    elif case.direction == "materials":
        for row in case.intermediate["interaction_sweep"]:
            u = row["U_over_t"]
            assert row["energy_N2"] == pytest.approx((u - np.sqrt(u * u + 16)) / 2)
            assert row["double_occupation"] == pytest.approx(
                (1 - u / np.sqrt(u * u + 16)) / 2
            )
        assert evidence["estimates"]["occupation"]["ideal_reference"] == pytest.approx(
            case.reference["U4_double_occupation_analytic"]
        )
    else:
        final = [r for r in case.intermediate["time_evolution"] if r["time"] == 1.5]
        assert final[2]["infidelity"] < final[1]["infidelity"] < final[0]["infidelity"]
        assert (
            np.argmax(abs(StatevectorDevice().statevector(dynamics_circuit(0, 1)))) == 4
        )


def test_hubbard_particle_number_and_hermiticity():
    h = hubbard_hamiltonian(4).matrix()
    number = np.diag([i.bit_count() for i in range(16)])
    np.testing.assert_allclose(h, h.conj().T)
    np.testing.assert_allclose(h @ number, number @ h)


def test_diagonal_pauli_expansion_includes_higher_order_terms_without_qubo_claim():
    costs = np.arange(16, dtype=float) ** 3
    matrix = sum(
        coefficient * pauli.matrix(4)
        for coefficient, pauli in diagonal_cost_hamiltonian(costs).terms
    )
    np.testing.assert_allclose(matrix, np.diag(costs), atol=1e-10)
    circuit = diagonal_qaoa_circuit(costs, 0.03, 0)
    expected = np.exp(-1j * 0.03 * costs) / 4
    actual = StatevectorDevice().statevector(circuit)
    phase = np.vdot(expected, actual)
    np.testing.assert_allclose(actual, phase * expected, atol=1e-10)


@pytest.mark.parametrize("costs", [[1, 2], [float("nan")] * 16])
def test_bad_cost_tables_rejected(costs):
    with pytest.raises(ValueError):
        diagonal_cost_hamiltonian(costs)


@pytest.mark.parametrize("shots", [True, 0, 1, 1024.0, 100001])
def test_bad_shot_budgets_rejected(shots):
    with pytest.raises(ValueError):
        run_local_case(None, shots=shots)
