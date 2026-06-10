# QuantumBridge Studio API Contract v0.1

**Version**: v0.1 (Planning Stage)
**Date**: 2026-06-06
**Status**: Draft
**Owner**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)

---

## 1. Overview

This document defines the **API contract** between QuantumBridge Studio (frontend) and QuantumBridge SDK (backend). All interactions must go through these APIs.

Stage 8A note: this remains a planning contract only. No Next.js, React, cloud,
hardware, token, or product UI implementation is authorized by this document.

### Key Principles

1. ❌ **No direct upstream package calls** - Frontend calls QuantumBridge adapters only
2. ✅ **Provenance tracking** - Every response includes source info
3. ✅ **Graceful degradation** - Uninstalled packages return clear errors
4. ✅ **Schema validation** - All requests/responses validated against JSON schema
5. ✅ **No token storage** - IBM Cloud tokens never stored
6. ✅ **Adapter contract first** - Studio pages depend on stable adapter and result contracts

---

## 2. API Architecture

### 2.1 Layered Architecture

```
[Frontend (React)]
        ↓ (HTTP/WebSocket)
[API Gateway (FastAPI)]
        ↓
[QuantumBridge SDK Core]
        ↓ (Adapter Layer)
[Ecosystem Adapters (Qiskit/PennyLane/...)]
        ↓ (Optional)
[Upstream Packages (if installed)]
```

### 2.2 Authentication

**Current (MVP)**: No authentication (local only)
**Future (Team/Cloud)**: JWT-based authentication

### 2.3 Versioning

- **API Version**: v0.1 (matches QuantumBridge SDK version)
- **Backwards compatibility**: N/A (pre-release)
- **Deprecation policy**: N/A (pre-release)

---

## 3. Endpoint Definitions

### 3.1 Health & Status

#### `GET /api/v0/health`

**Description**: Check API health.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0rc1",
  "timestamp": "2026-06-06T12:34:56Z"
}
```

#### `GET /api/v0/ecosystem/status`

**Description**: Get installed ecosystem status.

**Response** (200 OK):
```json
{
  "ecosystem": {
    "qiskit": {
      "installed": true,
      "version": "2.4.1",
      "level": 2,
      "adapters": ["circuit", "result", "transpiler"]
    },
    "pennylane": {
      "installed": true,
      "version": "0.44.1",
      "level": 2,
      "adapters": ["tape", "qnode", "observable"]
    },
    "qiskit-finance": {
      "installed": false,
      "version": null,
      "level": 0,
      "adapters": []
    }
  }
}
```

#### `GET /api/v0/ecosystem/catalog`

**Description**: Return the QuantumBridge clean-room ecosystem project catalog.
The response is owned by QuantumBridge and must not be a scraped copy of IBM
Quantum Ecosystem.

**Response** (200 OK):
```json
{
  "catalog_version": "0.1",
  "source_mode": "manual-clean-room",
  "official_endorsement": false,
  "projects": [
    {
      "project_id": "qiskit-algorithms",
      "display_name": "QuantumBridge Algorithms Slice",
      "upstream_name": "Qiskit Algorithms",
      "category": "algorithms",
      "capability_level": 3,
      "clean_room_status": "executable",
      "official_endorsement": false
    }
  ]
}
```

#### `GET /api/v0/ecosystem/catalog/search`

**Description**: Search the QuantumBridge catalog by query, category, tag,
capability level, executable workflow status, or install extra.

The endpoint must return QuantumBridge catalog fields, warnings, and provenance
only. It must not proxy IBM website content or copy IBM UI text.

---

### 3.2 Circuit Builder

#### `POST /api/v0/circuit/build`

**Description**: Build a quantum circuit.

**Request Body**:
```json
{
  "qubits": 3,
  "clbits": 2,
  "operations": [
    {"op": "h", "targets": [0]},
    {"op": "cx", "controls": [0], "targets": [1]},
    {"op": "measure", "wire": 0, "bit": 0}
  ],
  "name": "Bell State"
}
```

**Response** (200 OK):
```json
{
  "circuit_id": "circuit_20260606_123456",
  "ir": {"...": "..."},
  "qasm": "OPENQASM 2.0;...",
  "depth": 2,
  "gate_count": 3,
  "provenance": {
    "source": "quantumbridge_native",
    "adapter": null,
    "official_endorsement": false
  }
}
```

#### `POST /api/v0/circuit/import`

**Description**: Import circuit from QASM or IR.

**Request Body**:
```json
{
  "format": "qasm",
  "source": "OPENQASM 2.0; qreg q[2]; h q[0]; cx q[0],q[1];"
}
```

**Response** (200 OK): Same as `POST /api/v0/circuit/build`

---

### 3.3 Simulator

#### `POST /api/v0/simulator/run`

**Description**: Run circuit on simulator.

**Request Body**:
```json
{
  "circuit_id": "circuit_20260606_123456",
  "simulator": "statevector",
  "shots": 1024,
  "seed": 42,
  "noise_model": null
}
```

**Response** (200 OK):
```json
{
  "job_id": "job_20260606_123456",
  "status": "completed",
  "result": {
    "counts": {"00": 512, "11": 512},
    "probabilities": {"00": 0.5, "11": 0.5},
    "statevector": [0.707, 0, 0, 0.707]
  },
  "provenance": {
    "backend": "quantumbridge_statevector",
    "adapter": "quantumbridge_native",
    "official_endorsement": false
  }
}
```

#### `GET /api/v0/simulator/status`

**Description**: Get simulator status.

**Response** (200 OK):
```json
{
  "simulators": {
    "statevector": {"available": true, "type": "native"},
    "density_matrix": {"available": true, "type": "native"},
    "aer": {"available": true, "type": "qiskit_passthrough", "version": "0.17.2"}
  }
}
```

---

### 3.4 Algorithms

#### `POST /api/v0/algorithms/vqe`

**Description**: Run VQE algorithm.

**Request Body**:
```json
{
  "hamiltonian": {"pauli": "II + ZZ", "coefficients": [0.5, -0.5]},
  "ansatz": "efficient_su2",
  "optimizer": "cobyla",
  "max_iterations": 200
}
```

**Response** (200 OK):
```json
{
  "job_id": "job_20260606_123457",
  "status": "completed",
  "result": {
    "eigenvalue": -1.137,
    "optimal_parameters": [0.123, 0.456],
    "parameter_history": [[0.1, 0.2], [0.05, 0.3], ...],
    "iteration_count": 42
  },
  "provenance": {
    "algorithm": "vqe",
    "adapter": "quantumbridge_native",
    "official_endorsement": false
  }
}
```

---

### 3.5 Chemistry

#### `POST /api/v0/chemistry/h2`

**Description**: Run H2 bond scan.

**Request Body**:
```json
{
  "basis": "sto-3g",
  "driver": "pyscf",
  "bond_lengths": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  "solver": "vqe"
}
```

**Response** (200 OK):
```json
{
  "job_id": "job_20260606_123458",
  "status": "completed",
  "result": {
    "bond_lengths": [0.5, 0.6, ...],
    "energies": [-1.066, -1.118, ...],
    "min_energy": -1.137,
    "min_bond_length": 0.7
  },
  "provenance": {
    "driver": "pyscf",
    "adapter": "qiskit_nature_adapter",
    "official_endorsement": false,
    "warning": "Experimental chemistry. Not for production use."
  }
}
```

---

### 3.6 Results

#### `GET /api/v0/results/{job_id}`

**Description**: Get job result by ID.

**Response** (200 OK):
```json
{
  "job_id": "job_20260606_123456",
  "job_type": "circuit",
  "status": "completed",
  "created_at": "2026-06-06T12:00:00Z",
  "completed_at": "2026-06-06T12:00:05Z",
  "backend": {
    "name": "quantumbridge_statevector",
    "version": "0.1.0rc1",
    "provider": "quantumbridge"
  },
  "input": {"...": "..."},
  "output": {"...": "..."},
  "provenance": {"...": "..."},
  "warnings": [],
  "metadata": {}
}
```

#### `GET /api/v0/results`

**Description**: List all results (paginated).

**Query Parameters**:
- `job_type`: Filter by type (circuit, algorithm, chemistry, etc.)
- `status`: Filter by status (pending, running, completed, failed)
- `limit`: Number of results per page (default: 20)
- `offset`: Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "results": [
    {"job_id": "job_xxx", "job_type": "circuit", "status": "completed", "...": "..."},
    ...
  ]
}
```

---

## 4. Error Handling

### 4.1 Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "DEPENDENCY_NOT_INSTALLED",
    "message": "Qiskit Aer is not installed. Install with: pip install quantumbridge-sdk[qiskit-aer]",
    "details": {
      "package": "qiskit-aer",
      "install_extra": "qiskit-aer",
      "level": 0
    }
  },
  "provenance": {
    "source": "quantumbridge_error_handler",
    "official_endorsement": false
  }
}
```

### 4.2 Error Codes

| Code | HTTP Status | Meaning |
|---|---|---|
| `BAD_REQUEST` | 400 | Invalid request body |
| `UNAUTHORIZED` | 401 | Authentication required (future) |
| `FORBIDDEN` | 403 | Permission denied (future) |
| `NOT_FOUND` | 404 | Resource not found |
| `DEPENDENCY_NOT_INSTALLED` | 400 | Optional dependency not installed |
| `INVALID_CIRCUIT` | 400 | Circuit validation failed |
| `SIMULATION_FAILED` | 500 | Simulator execution error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 5. WebSocket Events (Future)

### 5.1 Job Status Updates

**Event**: `job_status_update`

**Payload**:
```json
{
  "job_id": "job_20260606_123456",
  "status": "running",
  "progress": 0.42,
  "estimated_time_remaining": 12.3
}
```

### 5.2 Circuit Build Progress

**Event**: `circuit_build_progress`

**Payload**:
```json
{
  "circuit_id": "circuit_20260606_123456",
  "progress": 0.75,
  "current_operation": "Adding measurement gates..."
}
```

---

## 6. Rate Limiting (Future)

### 6.1 Default Limits

| Endpoint Type | Limit | Window |
|---|---|---|
| **Read** (GET) | 1000 requests | 1 hour |
| **Write** (POST/PUT/DELETE) | 100 requests | 1 hour |
| **Job Submission** | 10 jobs | 1 hour |

### 6.2 Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997
X-RateLimit-Reset: 2026-06-06T13:34:56Z
```

---

## 7. Schema Validation

### 7.1 Request Validation

All requests validated against JSON Schema before processing.

**Example**: `POST /api/v0/circuit/build`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["qubits", "operations"],
  "properties": {
    "qubits": {"type": "integer", "minimum": 1, "maximum": 100},
    "clbits": {"type": "integer", "minimum": 0, "maximum": 100},
    "operations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["op"],
        "properties": {
          "op": {"type": "string", "enum": ["h", "x", "y", "z", "rx", "ry", "rz", "cx", "cz", "measure"]},
          "targets": {"type": "array", "items": {"type": "integer"}},
          "controls": {"type": "array", "items": {"type": "integer"}},
          "params": {"type": "array", "items": {"type": "number"}}
        }
      }
    }
  }
}
```

### 7.2 Response Validation

All responses validated against JSON Schema before sending.

---

## 8. Security

### 8.1 Input Sanitization

- All string inputs sanitized (no code injection)
- All numeric inputs bounds-checked
- All file uploads validated (future)

### 8.2 CORS Policy

**Development**:
```
Access-Control-Allow-Origin: http://localhost:3000
```

**Production**:
```
Access-Control-Allow-Origin: https://studio.quantumbridge.org
```

### 8.3 No Token Storage

- IBM Cloud tokens: ❌ Never stored
- PennyLane Cloud tokens: ❌ Never stored
- All tokens must be provided per-request (future)

---

## 9. Versioning & Deprecation

### 9.0 Future Backend Compatibility Endpoints

Stage 10A prepares schema data for future Studio backend panels. No UI
implementation is included in Stage 10A.

Planned endpoints:

```text
POST /api/v0/backend/qos-uqci/job-spec
POST /api/v0/backend/qos-uqci/mock-runtime
POST /api/v0/backend/quafu/payload
POST /api/v0/backend/quafu/mock-backend
```

Response payloads must include result schema JSON, counts/probabilities,
warnings, provenance, and explicit flags for `cloud_access=false`,
`token_read=false`, and `hardware_access=false`.

### 9.1 Versioning Strategy

- **URL versioning**: `/api/v0/...`
- **Semantic versioning**: Major.Minor.Patch
- **Backwards compatibility**: Maintain for same major version

### 9.2 Deprecation Policy

**Current status**: N/A (pre-release, v0.x)

**Future policy** (v1.0+):
1. Mark endpoint as `deprecated` in response
2. Add `Sunset` header with deprecation date
3. Maintain for 6 months after deprecation
4. Remove in next major version

---

## 10. Open Questions

### 10.1 Stage 10C Local Backend API Executable Slice

Stage 10C implements the first local Python service layer matching the planned
Studio API shape:

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

These are handled by `quantumbridge.studio.local_router.route_request` without
starting an HTTP server or opening ports. Results are local-only, include
warnings/provenance, and explicitly avoid cloud, token, credential, and real
hardware access. This is backend API preparation, not frontend UI
implementation and not a production API claim.

### 10.2 Stage 10D Frontend Local Data Contract

Stage 10D consumes generated local data from `studio/src/data/`. The frontend
uses a local JS seed data module and a mock execution client. Future server
adapters may connect to the Stage 10C local router or optional FastAPI adapter,
but this prototype does not start a server or open ports.

### 10.3 Stage 10E Backend/Frontend Seed Contract

Stage 10E makes `quantumbridge.studio.frontend_contract` the canonical backend
to frontend bridge. The generated bundle includes catalog, workflow summaries,
workflow details, representative sample results, benchmark report, export
samples, and schema version metadata.

The frontend local client exposes:

- `listCatalogProjects()`
- `listWorkflows()`
- `getWorkflowDetail(workflowId)`
- `getInputSchema(workflowId)`
- `getSampleResult(workflowId)`
- `runMockWorkflow(workflowId, inputs)`
- `getBenchmarkReport()`
- `exportResult(format)`

All calls remain local-only and return structured responses with warnings,
provenance, and no cloud/token/hardware access.

### 10.0 Stage 10B Benchmark API Planning

Future backend endpoints may expose Stage 10B benchmark suites:

- `GET /api/v0/benchmarks/cases`
- `GET /api/v0/benchmarks/suites`
- `POST /api/v0/benchmarks/run`
- `GET /api/v0/benchmarks/reports/{id}`

These endpoints are planning notes only. Stage 10B does not implement UI,
does not expose production benchmark ranking, does not claim official
Benchpress output, and does not access cloud services, tokens, or real
hardware.

1. **REST or GraphQL?**
   - Current: REST (simpler for MVP)
   - Future: Consider GraphQL for flexible queries

2. **WebSocket or Polling?**
   - Current: Polling (simpler)
   - Future: WebSocket for real-time job updates

3. **SQL or NoSQL?**
   - Current: SQLite (local MVP)
   - Future: PostgreSQL (team), MongoDB (results)

4. **How to handle large results (1M+ shots)?**
   - Option A: Paginated results
   - Option B: Async result streaming
   - Option C: Store in file, return URL

---

**Document Version**: v0.1
**Last Updated**: 2026-06-06
**Author**: OpenClaw (QuantumBridge 24-hour R&D Chief of Staff)
