from quantumbridge.compat.benchpress.benchmark_registry import (
    filter_benchmark_cases,
    list_default_benchmark_cases,
    list_default_benchmark_suites,
)


def test_benchmark_registry_lists_default_suites():
    suites = list_default_benchmark_suites()
    assert {"circuit_basic", "simulator", "algorithms", "backend", "bridge"}.issubset(suites)
    assert len(list_default_benchmark_cases()) >= 9
    assert filter_benchmark_cases(category="backend")
