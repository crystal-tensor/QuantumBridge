# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent finance identities and actual optional SDK execution."""
from math import cos, sin

import numpy as np
import pytest

from quantumbridge import StatevectorDevice
from quantumbridge.finance import load_stock_history, build_portfolio_cqm, solve_portfolio
from quantumbridge.finance.cqm_portfolio import diagonal_qaoa
from quantumbridge.finance.quantum_monte_carlo import (
    expectation_problem, estimate_expectation, pennylane_qmc, pricing_case, risk_case,
)


def test_real_source_is_aligned_immutable_and_hash_verified():
    history = load_stock_history()
    assert history.dates[0] == "2015-01-02" and history.dates[-1] == "2015-12-31"
    assert history.prices.shape == (252, 4)
    np.testing.assert_array_equal(history.prices[-1], [55.084498, 136.22849, 59.834461, 104.691918])
    assert len(history.provenance["sha256"]) == 64
    assert not history.prices.flags.writeable


@pytest.mark.parametrize("options", [dict(start="2030-01-01", end="2030-01-02"),
                                     dict(symbols=("FAKE",)), dict(symbols=("IBM", "IBM")),
                                     dict(start="2016-01-01", end="2015-01-01")])
def test_no_synthetic_fallback_or_date_inversion(options):
    with pytest.raises(ValueError):
        load_stock_history(**options)


def test_cqm_all_16_energies_constraints_and_independent_optimum():
    pytest.importorskip("dimod")
    result = solve_portfolio(shots=128, grid=3)
    assert result["hardware_jobs"] == 0 and result["status"] == "solved"
    assert len(result["candidates"]) == 16
    candidates = [r for r in result["candidates"] if r["feasible"]]
    assert result["optimum"] == min(candidates, key=lambda r: r["objective"])
    assert result["optimum"]["cost"] <= 220
    assert sum(result["qaoa"]["counts"].values()) == 128
    assert result["holdout"]["dates"][0] > result["training_dates"][-1]


def test_infeasible_cqm_is_not_silently_relaxed():
    pytest.importorskip("dimod")
    output = solve_portfolio(build_portfolio_cqm(budget=1), grid=3, shots=32)
    assert output["status"] == "infeasible" and output["optimum"] is None
    assert output["qaoa"] is None


@pytest.mark.parametrize("budget", [1., 220.])
def test_cqm_crosscheck_does_not_accept_a_materially_changed_objective(budget):
    pytest.importorskip("dimod")
    problem = build_portfolio_cqm(budget=budget)
    changed = max(problem.candidates, key=lambda row: abs(row["objective"]))
    changed["objective"] += 1e-7*max(1., abs(changed["objective"]))
    with pytest.raises(RuntimeError, match="CQM disagrees"):
        solve_portfolio(problem, grid=3, shots=32)


def test_higher_order_phase_synthesis_matches_dense_definition():
    costs = np.random.default_rng(13).normal(size=16)
    gamma, beta = .31, -.26
    actual = StatevectorDevice().statevector(diagonal_qaoa(costs, gamma, beta))
    rx = np.array([[cos(beta), -1j*sin(beta)], [-1j*sin(beta), cos(beta)]])
    mixer = np.kron(np.kron(np.kron(rx, rx), rx), rx)
    expected = mixer@(np.exp(-1j*gamma*costs)/4)
    np.testing.assert_allclose(actual, expected, atol=2e-13, rtol=0)


@pytest.mark.parametrize("values", [[-3., -1., 2., 7.], [4.]*4])
def test_real_payoff_encoder_keeps_offset_signed_values_and_probability(values):
    p = np.array([.1, .2, .3, .4])
    problem, offset, scale = expectation_problem(p, values)
    state = StatevectorDevice().statevector(problem.state_preparation)
    probability = np.sum(np.abs(state.reshape(4, 2)[:, 1])**2)
    assert offset+scale*probability == pytest.approx(p@values, abs=1e-12)
    assert problem.state_preparation.num_bits == 0


def test_amplitude_estimation_retains_real_counts_and_queries():
    result = estimate_expectation([.25]*4, [0., .2, .4, 1.], shots=512)
    assert abs(result["estimate"]-.4) < .03
    assert all(sum(c.values()) == 512 for c in result["counts"])
    assert result["grover_queries"] == 7*512
    assert result["preparation_queries"] == 18*512
    assert result["total_shots"] == 4*512
    assert len(result["circuits"]) == 4 and result["hardware_jobs"] == 0


@pytest.mark.parametrize("p,values", [([.5,.5], [-2.,3.]), ([.25]*4, [-1.,.2,.4,1.]),
                                     ([.125]*8, list(range(8)))])
def test_gate_decomposed_reflection_matches_existing_native_grover_including_phase(p, values):
    from quantumbridge import EstimationProblem
    problem, _, _ = expectation_problem(p, values)
    original = EstimationProblem(problem.state_preparation, problem.objective_qubits)
    width = problem.state_preparation.num_qubits
    device = StatevectorDevice()
    for bits in range(1 << width):
        from quantumbridge import Circuit
        prefix = Circuit(width)
        for wire in range(width):
            if bits & (1 << (width-1-wire)):
                prefix.x(wire)
        np.testing.assert_allclose(device.statevector(prefix.compose(problem.grover_operator)),
                                   device.statevector(prefix.compose(original.grover_operator)),
                                   atol=3e-13, rtol=0)


@pytest.mark.parametrize("p", [[.25]*4, [.1,.1,.1,.7]])
def test_actual_pennylane_qmc_grid_including_mean_above_half(p):
    pytest.importorskip("pennylane")
    result = pennylane_qmc(p, [0., .2, .4, 1.])
    assert abs(result["estimate"]-np.dot(p, [0., .2, .4, 1.])) < .06
    assert sum(result["probabilities"]) == pytest.approx(1, abs=1e-12)


@pytest.mark.parametrize("p,values", [([1., 0.], [2., -3.]),
                                     ([0., 1.], [-3., 2.]),
                                     ([.5, .5], [4., 4.])])
def test_actual_pennylane_qmc_zero_mass_and_constant_payoffs(p, values):
    pytest.importorskip("pennylane")
    result = pennylane_qmc(p, values)
    assert result["estimate"] == pytest.approx(np.dot(p, values), abs=1e-12, rel=0)
    assert np.isfinite(result["probabilities"]).all()
    assert sum(result["probabilities"]) == pytest.approx(1, abs=1e-12, rel=0)
    assert result["hardware_jobs"] == 0


def test_stock_calibrated_option_price_separates_grid_and_shot_error():
    pytest.importorskip("scipy")
    result = pricing_case(shots=128)
    assert result["dates"][-1] == "2015-12-31" and result["spot"] > 0
    assert result["black_scholes"]["call"] > 0
    assert abs(result["call"]["estimate"]-result["call"]["exact_discrete"]) < .5
    discount = np.exp(-result["rate"]*30/252)
    parity = np.array(result["call_payoffs"])-np.array(result["put_payoffs"])
    np.testing.assert_allclose(parity, discount*(np.array(result["scenario_prices"])-result["strike"]), atol=1e-12)


def test_risk_tail_mean_preserves_empirical_cvar_not_centroid_quantile():
    result = risk_case(shots=128)
    p = np.array(result["probabilities"])
    assert p@result["bin_values"] == pytest.approx(np.mean(result["losses"]), abs=1e-12)
    reference = result["raw_reference"]
    assert reference["VaR"]+p@result["excess_values"]/.05 == pytest.approx(reference["CVaR_expected_shortfall"])
    assert result["probability_measure"].startswith("Empirical")


def test_actual_pennylane_qmc_estimates_real_stock_tail_excess():
    pytest.importorskip("pennylane")
    risk = risk_case(shots=128)
    result = pennylane_qmc(risk["probabilities"], risk["excess_values"], estimation_wires=5)
    reference = risk["raw_reference"]
    assert reference["VaR"]+result["exact_discrete"]/(1-risk["confidence"]) == pytest.approx(
        reference["CVaR_expected_shortfall"], abs=1e-12)
    probabilities = np.array(result["probabilities"])
    assert probabilities.shape == (32,) and probabilities.sum() == pytest.approx(1.)
    # Bound by the phase-grid resolution, not the unrelated native MLAE interval.
    amplitude = (result["exact_discrete"]-result["normalization"]["offset"])/result["normalization"]["scale"]
    exact_phase = np.arccos(1-2*amplitude)/np.pi
    assert abs(result["phase"]-exact_phase) <= 1/32
    amount_bound = result["normalization"]["scale"]*np.pi/(2*32)
    assert abs(result["estimate"]-result["exact_discrete"]) <= amount_bound
    assert result["qubits"] == 9 and result["hardware_jobs"] == 0


def test_hybrid_really_differentiates_and_uses_chronological_holdout():
    pytest.importorskip("torch")
    from quantumbridge.finance import hybrid_volatility_case
    result = hybrid_volatility_case(epochs=2)
    assert result["train_dates"][-1] < result["validation_dates"][0]
    assert len(result["train_mse"]) == 2 and min(result["circuit_gradient_norms"]) > 0
    assert len(result["predictions"]) == len(result["actual"]) == len(result["dates"])
    assert np.isfinite(result["validation_mse"]) and result["hardware_jobs"] == 0


def test_hybrid_published_tape_path_is_native_differentiable_and_explicit(monkeypatch):
    pytest.importorskip("torch")
    from quantumbridge import qml
    from quantumbridge.finance import hybrid_volatility_case
    monkeypatch.delattr(qml, "qnode", raising=False)
    result = hybrid_volatility_case(epochs=2)
    assert "Native Tape adjoint" in result["backend"]
    assert min(result["circuit_gradient_norms"]) > 0
    assert result["train_dates"][-1] < result["validation_dates"][0]
    assert np.isfinite(result["predictions"]).all()
    assert result["hardware_jobs"] == 0


@pytest.mark.parametrize("generator", [False, True])
def test_financial_amplitude_sampling_preserves_objective_register_for_both_seed_forms(generator):
    from quantumbridge import EstimationProblem, MaximumLikelihoodAmplitudeEstimation, StatevectorSampler
    from quantumbridge.core import Circuit
    source = Circuit(1).ry(2*np.arcsin(np.sqrt(.2)), 0)
    seed = np.random.default_rng(42) if generator else 42
    sampler = StatevectorSampler(default_shots=128, seed=seed)
    result = MaximumLikelihoodAmplitudeEstimation([0, 1, 2], sampler=sampler).estimate(EstimationProblem(source, [0]))
    assert len(result.primitive_result) == 3
    assert all(pub.data.meas.num_shots == 128 for pub in result.primitive_result)
    assert all(sum(row.values()) == 128 for row in result.circuit_results)
    assert abs(result.estimation-.2) < .04
    assert source.num_clbits == 0 and not source.measurements


@pytest.mark.parametrize("options", [dict(budget=-1), dict(budget=float("nan")),
                                     dict(holdings=True), dict(tech_cap=4), dict(fee=-.1)])
def test_cqm_invalid_financial_constraints_are_rejected(options):
    pytest.importorskip("dimod")
    with pytest.raises(ValueError):
        build_portfolio_cqm(**options)


@pytest.mark.parametrize("p,v", [([.2,.2], [1,2]), ([1,-.1,.1,0], [1,2,3,4]),
                                 ([.5,.5], [1,float("nan")]), ([1], [1]),
                                 (np.array([.5+.1j,.5-.1j]), [1,2]),
                                 ([.5,.5], np.array([1+1j,2-1j]))])
def test_bad_amplitude_inputs_do_not_silently_clip_or_normalize(p, v):
    with pytest.raises(ValueError):
        expectation_problem(p, v)


def test_gate_model_artifacts_are_actual_roundtrippable_qasm_not_cloud_receipts():
    from quantumbridge.finance.gate_exports import measurement_artifact
    from quantumbridge.serialization import qasm2_loads
    circuits = [diagonal_qaoa(np.arange(16)/15, .31, .2)]
    circuits += estimate_expectation([.25]*4, [0., .2, .4, 1.], shots=32)["circuits"]
    for circuit in circuits:
        artifact = measurement_artifact(circuit)
        restored = qasm2_loads(artifact["openqasm"])
        assert restored.num_qubits == circuit.num_qubits
        device = StatevectorDevice()
        np.testing.assert_allclose(np.abs(device.statevector(restored))**2,
                                   np.abs(device.statevector(circuit))**2, atol=1e-11, rtol=0)
