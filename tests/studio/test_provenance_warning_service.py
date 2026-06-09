from quantumbridge.studio.provenance_service import build_clean_room_notice, build_safety_and_boundary_notice
from quantumbridge.studio.warning_service import collect_result_warnings, summarize_warning_levels, workflow_boundary_warnings


def test_provenance_and_warning_helpers():
    clean = build_clean_room_notice("qiskit-aer")
    safety = build_safety_and_boundary_notice("aer.qasm_counts_native")
    assert clean["official_endorsement"] is False
    assert safety["cloud_access"] is False
    warnings = workflow_boundary_warnings("aer.qasm_counts_native", "qiskit-aer")
    assert warnings
    assert summarize_warning_levels(warnings)["info"] == len(warnings)
    assert collect_result_warnings({"warnings": ["x"]}) == ["x"]
