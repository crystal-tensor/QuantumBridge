import json

from quantumbridge.compat.qiskit_nature import run_h2_native, run_lih_native
from quantumbridge.schema.chemistry_results import ChemistryResult, H2WorkflowResult, LiHWorkflowResult


def test_h2_result_schema_roundtrip():
    result = run_h2_native()
    payload = result.to_dict()
    restored = H2WorkflowResult.from_dict(payload)

    assert restored.validate() is True
    assert restored.to_dict() == payload
    assert json.loads(restored.to_json())["workflow"] == "h2_native_exact"


def test_lih_result_schema_roundtrip_via_base_class():
    result = run_lih_native()
    restored = ChemistryResult.from_dict(result.to_dict())

    assert restored.validate() is True
    assert isinstance(result, LiHWorkflowResult)
    assert restored.workflow == "lih_native_exact"
    assert restored.ecosystem == "quantumbridge_native_chemistry"
