from quantumbridge.studio.execution_service import execute_workflow
from quantumbridge.studio.export_service import (
    export_catalog_json,
    export_result_json,
    export_result_markdown,
    export_workflow_notebook_stub,
    export_workflow_python_snippet,
    export_workflow_registry_json,
)


def test_export_json_markdown_python_snippet_and_registry():
    result = execute_workflow("aer.qasm_counts_native", {"shots": 16})
    assert "aer.qasm_counts_native" in export_result_json(result).content
    assert "QuantumBridge Studio Result" in export_result_markdown(result).content
    snippet = export_workflow_python_snippet("aer.qasm_counts_native", {"shots": 16})
    assert "execute_workflow" in snippet.content
    assert "nbformat" in export_workflow_notebook_stub("aer.qasm_counts_native").content
    assert "project_id" in export_catalog_json().content
    assert "workflow_id" in export_workflow_registry_json().content
