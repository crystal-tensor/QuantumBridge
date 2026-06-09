# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import (
    compare_algorithm_results,
    run_grover_native,
    run_qaoa_native_maxcut,
    run_vqe_native,
    wrap_native_algorithm_result,
)
from quantumbridge.schema.algorithms_results import (
    AlgorithmComparisonResult,
    AlgorithmsResult,
    GroverResult,
    NativeAlgorithmResult,
    QAOAResult,
    VQEResult,
)


def test_algorithms_result_schema_roundtrip():
    result = run_grover_native(["11"], 2)
    payload = result.to_dict()
    restored = GroverResult.from_dict(payload)
    assert restored.to_dict() == payload
    assert restored.to_json()


def test_specific_result_classes_are_algorithms_results():
    assert isinstance(run_vqe_native(parameter_grid=(0.0, 3.141592653589793)), VQEResult)
    assert isinstance(run_qaoa_native_maxcut(((0, 1),), 2), QAOAResult)
    assert isinstance(run_grover_native(["11"], 2), GroverResult)
    assert isinstance(run_grover_native(["11"], 2), AlgorithmsResult)


def test_native_wrapper_and_comparison_result():
    native = run_grover_native(["11"], 2)
    wrapped = wrap_native_algorithm_result(native)
    comparison = compare_algorithm_results(native, None)
    assert isinstance(wrapped, NativeAlgorithmResult)
    assert isinstance(comparison, AlgorithmComparisonResult)
    assert comparison.metadata["upstream_available"] is False
