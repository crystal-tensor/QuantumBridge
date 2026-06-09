from quantumbridge.studio.workflow_registry import get_workflow, get_workflow_examples, list_workflows, search_workflows


def test_workflows_can_be_listed_and_have_required_contract():
    workflows = list_workflows()
    assert len(workflows) >= 30
    required = {
        "finance.portfolio_optimization_native",
        "aer.qasm_counts_native",
        "benchpress.basic_suite",
        "quafu.mock_backend",
    }
    ids = {workflow.workflow_id for workflow in workflows}
    assert required.issubset(ids)
    for workflow in workflows:
        assert workflow.local_only is True
        assert workflow.cloud_access is False
        assert workflow.token_access is False
        assert workflow.hardware_access is False


def test_workflow_detail_examples_and_search():
    detail = get_workflow("aer.qasm_counts_native")
    assert detail.input_schema.workflow_id == detail.workflow_id
    assert get_workflow_examples(detail.workflow_id)
    assert search_workflows("aer")
