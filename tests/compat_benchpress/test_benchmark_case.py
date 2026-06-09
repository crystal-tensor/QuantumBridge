from quantumbridge.compat.benchpress.benchmark_case import (
    benchmark_case_from_dict,
    benchmark_case_to_dict,
    create_benchmark_case,
    validate_benchmark_case,
)


def test_benchmark_case_roundtrip():
    case = create_benchmark_case("Bell", "circuit", {"qubits": 2}, {"passed": True}, runner=lambda: {})
    assert validate_benchmark_case(case)
    payload = benchmark_case_to_dict(case)
    restored = benchmark_case_from_dict(payload)
    assert restored.case_id == case.case_id
    assert restored.production_ready is False
