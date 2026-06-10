# QuantumBridge Studio Frontend Prototype v0.1

QuantumBridge Studio frontend v0.1 is a local static prototype for browsing and
calling the Stage 10C backend API outputs. It is independent, local-only, and
does not claim production readiness or official endorsement.

## Screens

- Catalog: clean-room ecosystem project records.
- Workflows: local workflow registry with execution boundaries.
- Workflow Detail: input schema, output schema, warnings, and provenance.
- Execute: mock local JSON execution using Stage 10C seed data.
- Benchmarks: Stage 10B/10C benchmark payload visualization.
- Results: saved sample execution records.
- Exports: JSON, Markdown, Python snippet, and notebook stub payloads.

## Local Data Flow

1. Python generates seed data from `quantumbridge.studio`.
2. The frontend imports `studio/src/data/seedData.js`.
3. The mock client renders catalog, workflows, execution, results, and exports.

No server, cloud service, credential, or hardware is used.
