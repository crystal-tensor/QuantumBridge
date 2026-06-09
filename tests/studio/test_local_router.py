from quantumbridge.studio.local_router import list_routes, route_request


def test_local_router_workflow_and_execution_paths():
    assert any(route["path"] == "/workflows" for route in list_routes())
    workflows = route_request("/workflows")
    assert workflows.success
    detail = route_request("/workflows/aer.qasm_counts_native")
    assert detail.success
    schema = route_request("/workflows/aer.qasm_counts_native/schema")
    assert schema.success
    executed = route_request("/execute/aer.qasm_counts_native", method="POST", body={"shots": 16, "seed": 3})
    assert executed.success
    execution_id = executed.data["execution_id"]
    assert route_request(f"/results/{execution_id}").success


def test_local_router_catalog_benchmark_export_and_missing_route():
    assert route_request("/catalog/projects").success
    assert route_request("/benchmarks").success
    assert route_request("/benchmarks/circuit_basic", method="POST").success
    assert route_request("/export/catalog").success
    assert route_request("/missing").success is False
