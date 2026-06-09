from quantumbridge.studio.execution_service import dry_run_workflow, execute_batch_workflows, execute_workflow, get_execution_result, get_execution_status
from quantumbridge.studio.result_store import clear_results


def test_representative_workflows_execute_successfully():
    clear_results()
    workflow_ids = [
        "finance.portfolio_optimization_native",
        "optimization.quadratic_program_native",
        "algorithms.qaoa_native",
        "nature.h2_native",
        "ml.quantum_kernel_native",
        "aer.qasm_counts_native",
        "mitiq.readout_mitigation_native",
        "pennylane_qiskit.qiskit_to_pennylane",
        "experiments.rabi_native",
        "qos_uqci.mock_runtime",
    ]
    results = [execute_workflow(workflow_id) for workflow_id in workflow_ids]
    assert all(result.status == "succeeded" for result in results)
    assert get_execution_status(results[0].execution_id)["status"] == "succeeded"
    assert get_execution_result(results[0].execution_id).workflow_id == workflow_ids[0]


def test_dry_run_and_batch_execution():
    dry = dry_run_workflow("aer.qasm_counts_native", {"shots": 16})
    assert dry.status == "dry_run"
    batch = execute_batch_workflows([
        {"workflow_id": "aer.qasm_counts_native", "inputs": {"shots": 16}},
        {"workflow_id": "benchpress.basic_suite", "inputs": {}},
    ])
    assert [result.status for result in batch] == ["succeeded", "succeeded"]
