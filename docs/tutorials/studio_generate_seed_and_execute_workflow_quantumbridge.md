# Generate Studio Seed Data and Execute a Local Workflow

This tutorial uses only QuantumBridge local backend services.

## Generate Frontend Seed Data

```bash
python3 examples/studio_generate_frontend_seed_data_quantumbridge.py
```

This writes local seed files under `studio/src/data/`, including catalog,
workflows, workflow details, sample results, benchmark report, exports, and
schema version metadata.

## Inspect Workflows

```bash
python3 -m quantumbridge.studio list-workflows
```

## Execute a Local Workflow

```bash
python3 -m quantumbridge.studio execute --workflow aer.statevector_native
```

The result is local JSON with warnings and provenance. It does not access cloud
services, tokens, or hardware.

## Export a Result Sample

```bash
python3 -m quantumbridge.studio export --workflow aer.statevector_native --format json
```

Supported formats are JSON, Markdown, Python snippet, and notebook stub. The
Python snippet uses QuantumBridge Studio local APIs.
