# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_finance.result_adapter import wrap_finance_result
from quantumbridge.schema import FinanceResult


def test_finance_result_schema():
    result = wrap_finance_result({"application": "portfolio-smoke"})
    assert isinstance(result, FinanceResult)
    assert result.capability_level == 2