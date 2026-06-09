# QuantumBridge Studio Local Router Contract v0.1

`quantumbridge.studio.local_router.route_request(path, method, body)` maps
REST-like paths to local Python service calls. It does not start an HTTP server.

Supported paths include:

- `GET /catalog/projects`
- `GET /workflows`
- `GET /workflows/{workflow_id}`
- `GET /workflows/{workflow_id}/schema`
- `POST /execute/{workflow_id}`
- `GET /results/{execution_id}`
- `GET /benchmarks`
- `POST /benchmarks/{suite_id}`
- `GET /export/catalog`
- `GET /export/workflows`
