"""Independent statistical checks, never fake hardware qualification."""

import copy

import numpy as np
import pytest

from quantumbridge.finance import build_finance_cases, run_local
from quantumbridge.finance.acceptance import analyze_case_evidence
from quantumbridge.finance.statistics import distribution_diagnostics, optimization_diagnostics, risk_sampling_diagnostics, wilson_interval


@pytest.fixture(scope="module")
def cases():
    return build_finance_cases()


def test_wilson_endpoint_has_nonzero_unseen_event_upper_bound():
    z = 1.959963984540054
    lo, hi = wilson_interval(0, 1024)
    assert lo == pytest.approx(0, abs=1e-15)
    assert hi == pytest.approx(z * z / (1024 + z * z))
    one = wilson_interval(1024, 1024)
    assert one == pytest.approx([1 - hi, 1])
    assert wilson_interval(512, 1024)[0] < 0.5 < wilson_interval(512, 1024)[1]


@pytest.mark.parametrize("k,n,c", [(-1, 10, .95), (11, 10, .95), (0, 0, .95), (True, 10, .95), (1, 10, 1), (1, 10, np.nan)])
def test_invalid_binomial_arguments(k, n, c):
    with pytest.raises(ValueError):
        wilson_interval(k, n, confidence=c)


def test_distribution_distance_and_not_arbitrary_hardware_pass():
    diagnostic = distribution_diagnostics({"0": 768, "1": 256}, [.5, .5])
    assert diagnostic["total_variation_distance"] == pytest.approx(.25)
    assert diagnostic["status"] == "INCONCLUSIVE"
    assert len(diagnostic["simultaneous_probability_intervals"]) == 2


def test_conditional_and_unconditional_optimization_are_not_confused(cases):
    case = cases["constraints"]
    result = optimization_diagnostics(case, {"1010": 128, "1001": 128, "0000": 768})
    assert result["feasible_probability"] == .25
    assert result["conditional_optimum_probability"] == .5
    assert result["unconditional_optimum_probability"] == .125
    assert result["conditional_mean_objective"] == pytest.approx(
        np.mean([r["objective"] for r in case.intermediate["candidates"] if r["bitstring"] in {"1010", "1001"}]))
    empty = optimization_diagnostics(case, {"0000": 1024})
    assert empty["conditional_optimum_probability"] is None
    assert empty["conditional_mean_objective"] is None


def test_empirical_risk_bootstrap_preserves_quantile_atoms_and_warns_unseen_tail():
    result = risk_sampling_diagnostics([0, 10, 20, 30], {"00": 800, "01": 150, "10": 74}, confidence=.9, bootstrap_samples=100)
    assert result["point"]["VaR"] == 10
    assert result["point"]["CVaR_expected_shortfall"] == pytest.approx(10 + 10 * (74/1024) / .1)
    assert result["dkw_95_var_range"][0] <= 10 <= result["dkw_95_var_range"][1]
    assert result["unseen_loss_states"] == [3]
    assert "unseen tails" in result["limitations"]
    assert result == risk_sampling_diagnostics([0, 10, 20, 30], {"00": 800, "01": 150, "10": 74}, confidence=.9, bootstrap_samples=100)


def test_actual_local_outputs_never_become_hardware_pass(cases):
    for case in cases.values():
        report = analyze_case_evidence(case, run_local(case), bootstrap_samples=100)
        assert report["hardware_status"] == "NOT_EXECUTED"
        assert all(row["total_variation_distance"] >= 0 for row in report["experiment_diagnostics"].values())
    assert analyze_case_evidence(cases["risk"])["hardware_results"] is None


@pytest.mark.parametrize("corrupt", ["counts", "hash", "shots", "order"])
def test_acceptance_rejects_corrupted_receipts(cases, corrupt):
    case = cases["derivatives"]
    results = copy.deepcopy(run_local(case))
    row = results["risk_neutral_paths"]
    if corrupt == "counts":
        row["counts"] = {"000": 1024}
    elif corrupt == "hash":
        row["artifact"]["sha256"] = "f" * 64
    elif corrupt == "shots":
        row["shots"] = 1023
    else:
        row["bit_order"] = "q0-last"
    with pytest.raises(ValueError):
        analyze_case_evidence(case, results)


def test_exact_submitted_source_survives_one_ulp_environment_difference(tmp_path, cases):
    import json
    from dataclasses import replace

    from quantumbridge.compat.quafu import QuafuCloudBackend
    from quantumbridge.finance import FinanceCloudSession
    from quantumbridge.finance.acceptance import restore_submitted_circuits
    from quantumbridge.finance.execution import circuit_artifact

    class Transport:
        transport_name = "protocol-test-only"

        def __init__(self):
            self.count = 0

        def submit(self, *args, **kwargs):
            self.count += 1
            return f"test-{self.count}"

        def retrieve(self, task_id):
            return {"counts": {"10": 1024}} if task_id == "test-1" else {"counts": {"000": 1024}}

    original = cases["derivatives"]
    submitted = copy.deepcopy(original)
    circuit = submitted.experiments["risk_neutral_paths"]
    op = circuit.operations[1]
    circuit.operations[1] = replace(op, params=(float(np.nextafter(op.params[0], np.inf)),))
    digest = circuit_artifact(circuit)["sha256"]
    assert digest != circuit_artifact(original.experiments["risk_neutral_paths"])["sha256"]
    path = tmp_path / "session.json"
    session = FinanceCloudSession(QuafuCloudBackend(transport=Transport()), journal=path)
    session.run(submitted, poll_interval=0)
    plan_path = path.with_name("plan.json")
    plan_path.write_text(json.dumps({"derivatives": {"risk_neutral_paths": digest}}))
    restored = restore_submitted_circuits(original, path)
    assert circuit_artifact(restored.experiments["risk_neutral_paths"])["sha256"] == digest
    changed = copy.deepcopy(original)
    changed.experiments["risk_neutral_paths"].x(0)
    with pytest.raises(ValueError, match="financial reference"):
        restore_submitted_circuits(changed, path)
    plan_path.write_text(json.dumps({"derivatives": {"risk_neutral_paths": "f" * 64}}))
    with pytest.raises(ValueError, match="plan hash"):
        restore_submitted_circuits(original, path)
