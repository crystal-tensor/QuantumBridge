"""Independent analytic checks; these tests never access hardware or credentials."""

import json
from math import exp, sqrt

import numpy as np
import pytest

from quantumbridge.compat.quafu import QuafuCloudBackend
from quantumbridge.devices import StatevectorDevice
from quantumbridge.finance import FinanceCloudSession, build_finance_cases, run_local
from quantumbridge.finance.execution import circuit_artifact, probabilities_from_counts
from quantumbridge.finance.kernels import prepare_real_state, probability_circuit, qaoa_circuit, risk_measures


@pytest.fixture(scope="module")
def cases():
    return build_finance_cases()


@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_signed_state_preparation_matches_independent_vector(width, seed):
    amplitudes = np.random.default_rng(seed).normal(size=1 << width)
    circuit = prepare_real_state(amplitudes)
    actual = StatevectorDevice().statevector(circuit)
    np.testing.assert_allclose(actual, amplitudes / np.linalg.norm(amplitudes), atol=2e-14)
    assert {op.name for op in circuit.operations} <= {"ry", "cx"}


@pytest.mark.parametrize("data", [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, -2]])
def test_preparation_zero_branches_and_global_sign(data):
    actual = StatevectorDevice().statevector(prepare_real_state(data))
    np.testing.assert_allclose(actual, np.array(data) / np.linalg.norm(data), atol=1e-14)


@pytest.mark.parametrize("data", [[0, 0], [1, 2, 3], [np.nan, 1], [1j, 0], list(range(32))])
def test_preparation_invalid_or_unbounded_inputs(data):
    with pytest.raises(ValueError):
        prepare_real_state(data)


@pytest.mark.parametrize("data", [[1, -1], [0.2, 0.2], [np.inf, 0]])
def test_probability_validation(data):
    with pytest.raises(ValueError):
        probability_circuit(data)


def test_var_expected_shortfall_uses_fraction_of_boundary_atom():
    result = risk_measures([0, 10, 20], [0.8, 0.15, 0.05], 0.9)
    assert result["VaR"] == 10
    assert result["CVaR_expected_shortfall"] == pytest.approx(15)
    assert result["expected_loss"] == pytest.approx(2.5)


def test_qaoa_phase_and_mixer_match_dense_independent_formula():
    costs = np.array([0.2, 0.4, -0.5, 2.0])
    gamma, beta = 0.7, 0.2
    mixer = np.array([[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]])
    reference = np.kron(mixer, mixer) @ (np.exp(-1j * gamma * costs) / 2)
    actual = StatevectorDevice().statevector(qaoa_circuit(costs, gamma, beta))
    phase = np.vdot(reference, actual)
    np.testing.assert_allclose(actual, reference * phase, atol=1e-13)


def test_case_registry_and_no_hidden_classical_solution_preparation(cases):
    assert list(cases) == ["allocation", "risk", "derivatives", "constraints", "correlation"]
    assert sum(len(case.experiments) for case in cases.values()) == 8
    for key in ("allocation", "constraints"):
        case = cases[key]
        assert case.reference["penalized_global_minimum_is_feasible"]
        trace = case.intermediate["local_optimizer_trace"]
        assert trace[-1]["expected_cost"] < trace[0]["expected_cost"]
        assert set(op.name for op in case.experiments["qaoa"].operations) <= {"h", "cx", "rz", "rx"}


def _ideal_results(case):
    device = StatevectorDevice()
    return {name: {"probabilities": [device.probabilities(circuit).get(format(i, f"0{circuit.num_qubits}b"), 0)
                                     for i in range(1 << circuit.num_qubits)], "shots": 1024}
            for name, circuit in case.experiments.items()}


def test_risk_probabilities_and_stress_match_exact_oracle(cases):
    case = cases["risk"]
    actual = case.analyze(_ideal_results(case))
    for name in ("base", "stress"):
        for field in ("expected_loss", "VaR", "CVaR_expected_shortfall"):
            assert actual[name][field] == pytest.approx(case.reference[name][field])
    assert actual["stress"]["expected_loss"] > actual["base"]["expected_loss"]


def test_derivative_price_delta_parity_and_static_hedge(cases):
    case = cases["derivatives"]
    actual = case.analyze(_ideal_results(case))
    assert actual["call_price"] == pytest.approx(case.reference["call_price"])
    assert actual["delta"] == pytest.approx(case.reference["delta"])
    assert abs(actual["put_call_parity_residual"]) < 1e-12
    assert actual["hedged_pnl_std"] < actual["unhedged_pnl_std"]
    # Check the risk-neutral martingale, independently of payoff evaluation.
    terminal = np.array(case.intermediate["terminal_prices"])
    assert terminal @ np.array(case.inputs["probabilities"]) == pytest.approx(100 * exp(0.03))


def test_correlation_preserves_negative_sign_and_historical_volatility(cases):
    case = cases["correlation"]
    actual = case.analyze(_ideal_results(case))
    for name in ("positive_correlation", "negative_correlation"):
        assert actual[name]["correlation"] == pytest.approx(case.reference[name])
    assert actual["negative_correlation"]["correlation"] < -0.9
    assert actual["daily_volatility"] == pytest.approx(case.reference["daily_volatility"])
    assert actual["annualized_volatility_252"] == pytest.approx(actual["daily_volatility"] * sqrt(252))


def test_local_results_have_measured_counts_actual_circuits_and_reproducibility(cases):
    for case in cases.values():
        first = run_local(case)
        assert first == run_local(case)
        assert set(first) == set(case.experiments)
        for result in first.values():
            assert result["hardware_access"] is False
            assert result["execution_mode"] == "local_simulator"
            assert sum(result["counts"].values()) == 1024
            assert result["artifact"]["openqasm"].startswith("OPENQASM 2.0;")
            assert "measure" in result["artifact"]["openqasm"]
        json.dumps(case.analyze(first))


@pytest.mark.parametrize("counts", [{}, {"a": 10}, {"01": -1}, {"01": True}, {"01": 0.5}, {"01": 1}])
def test_bad_counts_do_not_silently_turn_into_financial_results(counts):
    with pytest.raises(ValueError):
        probabilities_from_counts(counts, 2)


def test_explicit_bit_order_normalization():
    counts, probs, total = probabilities_from_counts({"001": 1024}, 3, bit_order="q0-last")
    assert counts == {"100": 1024}
    assert probs[4] == 1 and total == 1024


@pytest.mark.parametrize("confidence", [0, 1, -0.1, np.nan])
def test_invalid_risk_confidence(confidence):
    with pytest.raises(ValueError):
        risk_measures([0, 10], [0.5, 0.5], confidence)


@pytest.mark.parametrize("probabilities", [[0.2], [np.nan] * 8, [-1] + [2/7] * 7, [0.1] * 8])
def test_analysis_refuses_corrupted_results(cases, probabilities):
    result = _ideal_results(cases["risk"])
    result["base"]["probabilities"] = probabilities
    with pytest.raises(ValueError, match="probabilities"):
        cases["risk"].analyze(result)


def test_analysis_requires_all_results_and_actual_shots(cases):
    with pytest.raises(ValueError, match="every experiment"):
        cases["risk"].analyze({})
    result = _ideal_results(cases["risk"])
    result["base"]["shots"] = True
    with pytest.raises(ValueError, match="shots"):
        cases["risk"].analyze(result)


class ProtocolTransport:
    """Protocol-only fake: never used for hardware evidence or notebook outputs."""
    transport_name = "test-transport"

    def __init__(self):
        self.submissions = []

    def submit(self, openqasm, **kwargs):
        self.submissions.append((openqasm, kwargs))
        return str(len(self.submissions))

    def retrieve(self, task_id):
        if task_id == "1":
            return {"count": {"01": 1024}}
        return {"count": {"000": 512, "111": 512}}


def test_cloud_protocol_budget_receipts_resume_and_calibration(tmp_path, cases):
    transport = ProtocolTransport()
    backend = QuafuCloudBackend("test-only", transport=transport)
    journal = tmp_path / "receipts.json"
    session = FinanceCloudSession(backend, journal=journal)
    assert session.preflight(list(cases.values()))["total_tasks_including_existing"] == 9
    result = session.run(cases["risk"], poll_interval=0)
    assert session.data["bit_order"] == "q0-last"
    assert len(transport.submissions) == 3
    assert result["base"]["task_id"] == "2"
    assert result["base"]["hardware_access"] is False
    assert result["base"]["execution_mode"] == "injected_transport"
    resumed = FinanceCloudSession(backend, journal=journal)
    assert resumed.run(cases["risk"], poll_interval=0) == result
    assert len(transport.submissions) == 3
    assert all(item[1]["shots"] == 1024 for item in transport.submissions)
    with pytest.raises(ValueError, match="budget"):
        FinanceCloudSession(backend, journal=tmp_path / "small.json", max_tasks=2).preflight(list(cases.values()))


@pytest.mark.parametrize("kwargs", [{"shots": 2048}, {"max_tasks": 21}, {"max_qubits": 7}])
def test_cloud_cannot_exceed_approved_limits(tmp_path, kwargs):
    with pytest.raises(ValueError):
        FinanceCloudSession(QuafuCloudBackend(transport=ProtocolTransport()), journal=tmp_path / "j.json", **kwargs)


def test_all_artifacts_only_use_bound_qasm2_supported_gates(cases):
    for case in cases.values():
        for circuit in case.experiments.values():
            assert circuit.num_parameters == 0
            assert circuit.num_qubits <= 4
            assert set(op.name for op in circuit.operations) <= {"ry", "rx", "rz", "cx", "h"}
            assert circuit_artifact(circuit)["two_qubit_gates"] >= 0


def test_cloud_timeout_is_durable_and_rerun_only_retrieves(tmp_path, cases):
    from quantumbridge.providers import JobTimeoutError

    class Pending(ProtocolTransport):
        ready = False

        def retrieve(self, task_id):
            return super().retrieve(task_id) if self.ready else {"status": "pending"}

    transport = Pending()
    backend = QuafuCloudBackend("test-only", transport=transport)
    path = tmp_path / "durable.json"
    session = FinanceCloudSession(backend, journal=path)
    with pytest.raises(JobTimeoutError):
        session.run(cases["risk"], timeout=0, poll_interval=0)
    assert len(transport.submissions) == 1
    assert json.loads(path.read_text())["jobs"]["calibration/bit-order"]["job"]["job_id"] == "1"
    transport.ready = True
    FinanceCloudSession(backend, journal=path).run(cases["risk"], timeout=1, poll_interval=0)
    assert len(transport.submissions) == 3  # original calibration + two business circuits


def test_cloud_rejects_changed_circuit_and_backend_journal(tmp_path, cases):
    transport = ProtocolTransport()
    backend = QuafuCloudBackend("test-only", transport=transport)
    path = tmp_path / "durable.json"
    session = FinanceCloudSession(backend, journal=path)
    session.run(cases["risk"], poll_interval=0)
    from copy import deepcopy
    changed = deepcopy(cases["risk"])
    changed.experiments["base"].x(0)
    with pytest.raises(ValueError, match="changed circuit"):
        session.run(changed, poll_interval=0)
    assert len(transport.submissions) == 3
    with pytest.raises(ValueError, match="different backend"):
        FinanceCloudSession(QuafuCloudBackend("other", transport=transport), journal=path)


def test_inconclusive_calibration_stops_before_finance_jobs(tmp_path, cases):
    class Uncertain(ProtocolTransport):
        def retrieve(self, task_id):
            return {"count": {"00": 1024}}

    transport = Uncertain()
    session = FinanceCloudSession(QuafuCloudBackend(transport=transport), journal=tmp_path / "uncertain.json")
    with pytest.raises(ValueError, match="inconclusive"):
        session.run(cases["risk"], poll_interval=0)
    assert len(transport.submissions) == 1


def test_concurrent_notebook_kernel_cannot_double_submit(tmp_path, cases):
    import fcntl

    transport = ProtocolTransport()
    path = tmp_path / "locked.json"
    session = FinanceCloudSession(QuafuCloudBackend(transport=transport), journal=path)
    with path.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(RuntimeError, match="already in use"):
            session.run(cases["risk"], poll_interval=0)
    assert not transport.submissions


def test_shot_mismatch_stops_before_finance_jobs(tmp_path, cases):
    class WrongShots(ProtocolTransport):
        def retrieve(self, task_id):
            return {"count": {"01": 1023}}

    transport = WrongShots()
    session = FinanceCloudSession(QuafuCloudBackend(transport=transport), journal=tmp_path / "wrong.json")
    with pytest.raises(ValueError, match="shots differ"):
        session.run(cases["risk"], poll_interval=0)
    assert len(transport.submissions) == 1
