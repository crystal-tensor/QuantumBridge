from quantumbridge.studio.examples import (
    run_benchmark_api_example,
    run_catalog_api_example,
    run_export_api_example,
    run_workflow_execution_example,
)


def test_studio_examples_run():
    assert run_catalog_api_example()["workflow_count"] >= 30
    execution = run_workflow_execution_example()
    assert execution["execution"].status == "succeeded"
    benchmark = run_benchmark_api_example()
    assert benchmark["benchmark"].suite_id == "circuit_basic"
    export = run_export_api_example()
    assert "execute_workflow" in export["python_snippet"]
