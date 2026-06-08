# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_nature.result_adapter import wrap_chemistry_result
from quantumbridge.schema import ChemistryResult


def test_chemistry_result_schema_and_provenance():
    result = wrap_chemistry_result({"molecule": "H2", "energy": -1.0})
    assert isinstance(result, ChemistryResult)
    assert result.capability_level == 2
    assert result.provenance["source_policy"] == "optional_dependency_no_vendored_source"