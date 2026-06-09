from quantumbridge.compat.benchpress.warnings import (
    BENCHMARK_RESULT_WARNING,
    BENCHPRESS_COMPATIBILITY_WARNING,
    default_benchmark_provenance,
    default_benchmark_warnings,
)


def test_benchpress_warnings_and_provenance():
    warnings = default_benchmark_warnings()
    provenance = default_benchmark_provenance()
    assert BENCHPRESS_COMPATIBILITY_WARNING in warnings
    assert BENCHMARK_RESULT_WARNING in warnings
    assert provenance["copied_upstream_source"] is False
    assert provenance["official_endorsement"] is False
