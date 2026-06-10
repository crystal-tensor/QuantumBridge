from quantumbridge.studio.frontend_contract import build_frontend_seed_bundle
from quantumbridge.studio.workflow_registry import list_workflows


def test_frontend_workflow_coverage_equals_backend_registry():
    bundle = build_frontend_seed_bundle()
    registry_ids = {workflow.workflow_id for workflow in list_workflows()}
    workflow_ids = {workflow["workflow_id"] for workflow in bundle["workflows"]["workflows"]}
    detail_ids = {detail["workflow_id"] for detail in bundle["workflow_details"]["details"]}

    assert workflow_ids == registry_ids
    assert detail_ids == registry_ids
    assert bundle["workflows"]["workflow_count"] == len(registry_ids)
    assert bundle["workflow_details"]["workflow_detail_count"] == len(registry_ids)


def test_each_frontend_workflow_detail_has_schema_defaults_warning_and_provenance():
    bundle = build_frontend_seed_bundle()

    for detail in bundle["workflow_details"]["details"]:
        assert detail["input_schema"]["workflow_id"] == detail["workflow_id"]
        assert "default_inputs" in detail
        assert "output_schema" in detail
        assert detail["result_schema"]
        assert detail["warnings"]
        assert detail["provenance"]
        assert detail["clean_room_notice"]
        assert detail["unsupported_limitations"]
        assert detail["provenance"]["cloud_access"] is False
        assert detail["provenance"]["token_access"] is False
        assert detail["provenance"]["hardware_access"] is False
