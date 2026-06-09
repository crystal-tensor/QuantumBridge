from quantumbridge.studio.execution_service import execute_workflow
from quantumbridge.studio.result_store import InMemoryResultStore


def test_result_store_save_get_list_export_clear():
    store = InMemoryResultStore()
    result = execute_workflow("aer.qasm_counts_native", {"shots": 16})
    store.save_result(result)
    assert store.get_result(result.execution_id).workflow_id == result.workflow_id
    assert store.list_results()
    assert "execution_id" in store.export_result(result.execution_id, format="json")
    assert "Studio Execution Result" in store.export_result(result.execution_id, format="markdown")
    store.clear_results()
    assert store.list_results() == []
