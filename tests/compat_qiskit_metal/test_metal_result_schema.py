# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_metal.result_adapter import wrap_metal_result
from quantumbridge.schema import MetalDesignResult


def test_metal_result_schema_has_no_fabrication_claim():
    result = wrap_metal_result(
        {"design": "offline-smoke"},
        metadata={"fabrication_ready": False, "external_em_solver_used": False},
    )
    assert isinstance(result, MetalDesignResult)
    assert result.metadata["fabrication_ready"] is False