# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent business-constraint checks for all five industrial models."""

import pytest

from quantumbridge.applications.common import run_local_case
from quantumbridge.applications.industry import BUILDERS


@pytest.fixture(scope="module", params=list(BUILDERS))
def study(request):
    case = BUILDERS[request.param]()
    return case, run_local_case(case)


def test_exact_minimum_and_sampled_candidate(study):
    case, evidence = study
    rows = case.intermediate["candidates"]
    assert len(rows) == 16
    assert min(rows, key=lambda row: row["penalized_cost"])["feasible"]
    assert case.reference["best_objective"] == pytest.approx(
        {
            "routing-scheduling": 7,
            "supply-chain": 3,
            "energy": 10,
            "combinatorial": -6,
            "integer-multiobjective": -2.6,
        }[case.direction]
    )
    assert evidence["summary"]["best_observed_feasible"]["feasible"]
    assert evidence["summary"]["observed_objective_gap"] == pytest.approx(0)
    assert evidence["hardware_access"] is False
    assert evidence["new_cloud_tasks"] == 0
    assert sum(evidence["experiments"]["qaoa"]["counts"].values()) == 1024


def test_decoded_original_constraints(study):
    case, _ = study
    for row in case.intermediate["candidates"]:
        if case.direction == "routing-scheduling":
            a1, a2, b1, b2 = [r["start"] for r in row["operations"]]
            assert row["feasible"] == (
                a1 + 1 <= a2 and b1 + 1 <= b2 and a1 != b1 and a2 != b2
            )
        elif case.direction == "supply-chain":
            matrix = row["shipping_matrix"]
            assert row["feasible"] == (
                all(sum(matrix[i][j] for i in range(2)) == 1 for j in range(2))
                and all(sum(r) <= 1 for r in matrix)
            )
        elif case.direction == "energy":
            assert row["feasible"] == all(
                2 * state[0] + state[1] >= demand
                for state, demand in zip(row["commitment_by_time"], [2, 3])
            )
        elif case.direction == "combinatorial":
            assert row["objective"] == -sum(
                w
                for a, b, w in case.inputs["edges"]
                if row["bitstring"][a] != row["bitstring"][b]
            )
            assert case.intermediate["cost_pauli_degree"] == 2
        else:
            assert row["feasible"] == (
                2 * row["allocation_A"] + row["allocation_B"] <= 5
            )
    if "pareto_front" in case.intermediate:
        for row in case.intermediate["pareto_front"]:
            assert not any(
                other["feasible"]
                and other["profit"] >= row["profit"]
                and other["emissions"] <= row["emissions"]
                and (
                    other["profit"] > row["profit"]
                    or other["emissions"] < row["emissions"]
                )
                for other in case.intermediate["candidates"]
            )
