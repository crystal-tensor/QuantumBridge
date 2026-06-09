from pathlib import Path

from quantumbridge.studio.execution_service import execute_workflow
from quantumbridge.studio.workflow_registry import list_workflows


def test_studio_workflows_do_not_access_cloud_tokens_or_hardware():
    for workflow in list_workflows():
        assert workflow.cloud_access is False
        assert workflow.token_access is False
        assert workflow.hardware_access is False
    result = execute_workflow("qos_uqci.mock_runtime")
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_access"] is False
    assert result.provenance["hardware_access"] is False


def test_no_frontend_ui_implementation_files_created():
    forbidden = [
        Path("quantumbridge/studio/frontend"),
        Path("quantumbridge/studio/components"),
        Path("quantumbridge/studio/app"),
    ]
    assert not any(path.exists() for path in forbidden)
