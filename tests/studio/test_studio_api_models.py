from quantumbridge.studio.api_models import StudioAPIResponse, StudioExecutionRequest, StudioInputField, StudioProvenance


def test_studio_api_models_roundtrip():
    field = StudioInputField(name="shots", field_type="integer", default=64)
    assert field.to_dict()["name"] == "shots"
    request = StudioExecutionRequest(workflow_id="aer.qasm_counts_native", inputs={"shots": 64})
    assert StudioExecutionRequest.from_dict(request.to_dict()).workflow_id == request.workflow_id
    response = StudioAPIResponse(data={"ok": True})
    assert response.validate()


def test_studio_provenance_rejects_cloud_token_hardware():
    provenance = StudioProvenance()
    assert provenance.validate()
    bad = StudioProvenance(token_access=True)
    try:
        bad.validate()
    except ValueError as exc:
        assert "tokens" in str(exc)
    else:
        raise AssertionError("token access must be rejected")
