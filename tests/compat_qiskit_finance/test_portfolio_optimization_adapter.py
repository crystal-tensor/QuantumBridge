import pytest

from quantumbridge.compat import qiskit_finance
from quantumbridge.compat.qiskit_finance.portfolio_examples import tutorial_synthetic_portfolio_problem
from quantumbridge.compat.qiskit_finance.portfolio_native import (
    enumerate_budget_selections,
    portfolio_objective_value,
)
from quantumbridge.compat.qiskit_finance.portfolio_optimization_adapter import (
    compare_native_and_upstream_exact,
    run_portfolio_optimization_exact_upstream,
    run_portfolio_optimization_native,
    validate_portfolio_dependencies,
)
from quantumbridge.compat.qiskit_finance.portfolio_result import PortfolioOptimizationResult
from quantumbridge.compat.qiskit_finance.result_adapter import wrap_portfolio_optimization_result
from quantumbridge.schema import FinanceResult


def test_native_portfolio_optimization_runs_tutorial_synthetic_subset():
    result = run_portfolio_optimization_native()
    assert isinstance(result, PortfolioOptimizationResult)
    assert result.selection == (1, 0, 0, 1)
    assert result.budget == 2
    assert result.path == "quantumbridge-native"
    assert result.method == "exact-enumeration"
    assert result.probabilities == {"1001": 1.0}
    assert result.validate() is True
    assert "production finance" in result.warnings[0]


def test_native_portfolio_samples_are_feasible_and_sorted():
    problem = tutorial_synthetic_portfolio_problem()
    result = run_portfolio_optimization_native(problem)
    assert len(result.samples) == 6
    values = [row["objective_value"] for row in result.samples]
    assert values == sorted(values)
    assert all(sum(row["selection"]) == problem.budget for row in result.samples)


def test_portfolio_objective_and_budget_enumeration_contract():
    selections = enumerate_budget_selections(4, 2)
    assert selections[0] == (1, 1, 0, 0)
    assert selections[-1] == (0, 0, 1, 1)
    problem = tutorial_synthetic_portfolio_problem()
    objective = portfolio_objective_value(
        (1, 0, 0, 1),
        problem.expected_returns,
        problem.covariances,
        problem.risk_factor,
    )
    assert objective == pytest.approx(-0.0278)


def test_portfolio_result_round_trip_and_finance_schema_wrapper():
    result = run_portfolio_optimization_native()
    restored = PortfolioOptimizationResult.from_dict(result.to_dict())
    assert restored == result
    wrapped = wrap_portfolio_optimization_result(result)
    assert isinstance(wrapped, FinanceResult)
    payload = wrapped.to_dict()
    assert payload["data"]["selection"] == [1, 0, 0, 1]
    assert payload["metadata"]["method"] == "exact-enumeration"


def test_portfolio_dependency_report_is_offline_and_non_production():
    report = validate_portfolio_dependencies()
    assert report["network_required"] is False
    assert report["cloud_required"] is False
    assert report["credentials_required"] is False
    assert report["production_ready"] is False
    assert "qiskit_finance" in report["modules"]


def test_native_portfolio_requires_complete_explicit_inputs():
    with pytest.raises(ValueError, match="missing portfolio inputs"):
        run_portfolio_optimization_native(covariances=((1.0,),))


def test_qiskit_finance_facade_exports_executable_portfolio_subset():
    result = qiskit_finance.run_portfolio_optimization_native()
    assert result.selection == (1, 0, 0, 1)
    assert qiskit_finance.PortfolioOptimizationResult is PortfolioOptimizationResult
    assert callable(qiskit_finance.validate_portfolio_dependencies)


def test_upstream_exact_path_runs_or_reports_clear_optional_dependency_gap():
    report = validate_portfolio_dependencies()
    if not report["ready_for_upstream_exact"]:
        with pytest.raises(ImportError, match="qiskit-finance|Qiskit Finance"):
            run_portfolio_optimization_exact_upstream()
        return
    comparison = compare_native_and_upstream_exact()
    assert comparison["same_selection"] is True
    assert comparison["same_objective"] is True
