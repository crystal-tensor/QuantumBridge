# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_machine_learning.result_adapter import wrap_ml_result
from quantumbridge.compat.qiskit_machine_learning import (
    run_kernel_classifier_native,
    run_qnn_classifier_native,
    run_quantum_kernel_native,
)
from quantumbridge.schema import MLResult
from quantumbridge.schema.ml_results import (
    KernelClassifierResult,
    QNNClassifierResult,
    QuantumKernelResult,
)


def test_ml_result_schema():
    result = wrap_ml_result({"prediction": [0, 1]})
    assert isinstance(result, MLResult)
    assert result.capability_level == 2


def test_quantum_kernel_result_schema_roundtrip():
    result = run_quantum_kernel_native()
    restored = QuantumKernelResult.from_dict(result.to_dict())

    assert restored.validate() is True
    assert restored.kernel_matrix == result.kernel_matrix


def test_kernel_classifier_result_schema_roundtrip():
    result = run_kernel_classifier_native()
    restored = KernelClassifierResult.from_dict(result.to_dict())

    assert restored.validate() is True
    assert restored.predictions == result.predictions
    assert restored.accuracy == result.accuracy


def test_qnn_classifier_result_schema_roundtrip():
    result = run_qnn_classifier_native()
    restored = QNNClassifierResult.from_dict(result.to_dict())

    assert restored.validate() is True
    assert restored.weights == result.weights
    assert restored.predictions == result.predictions
