# QuantumBridge Studio Backend API Contract v0.1

Stage 10C exposes local Python services for catalog, workflow registry, input
schemas, execution, results, exports, benchmarks, warnings, and provenance.
The contract is backend-only and local-only. It does not start a production
server, open ports, access cloud services, read tokens, or execute hardware.

Primary modules:

- `quantumbridge.studio.catalog_service`
- `quantumbridge.studio.workflow_registry`
- `quantumbridge.studio.execution_service`
- `quantumbridge.studio.result_store`
- `quantumbridge.studio.export_service`
- `quantumbridge.studio.benchmark_service`
- `quantumbridge.studio.local_router`

Every response uses JSON-safe payloads, warnings, provenance, and explicit
clean-room boundaries.
