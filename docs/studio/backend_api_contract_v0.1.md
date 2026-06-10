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

## Stage 10E Frontend Contract

Stage 10E adds `quantumbridge.studio.frontend_contract` as the canonical bridge
from backend services to static frontend seed data. It builds and validates the
catalog, workflow summaries, workflow details, sample results, benchmark report,
exports, and schema metadata consumed by the local frontend prototype.

Stage 10E also adds `python -m quantumbridge.studio` for local structured JSON
commands. The CLI uses the same services and does not start a server, access
cloud services, read tokens, or execute hardware.
