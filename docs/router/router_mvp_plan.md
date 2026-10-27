# QuantumBridge Router MVP

QuantumBridge Router is the first commercial demo layer on top of the existing
QOS-UQCI compatibility work. It is not a visual SDK clone. It is a local
fidelity-aware routing and benchmark evidence system.

## Product Claim

Given a QASM/UQCI workload and a user SLA, the router selects a backend using
circuit features, calibration freshness, estimated queue wait, cost, and
multi-programming capacity. It returns an auditable decision trace and produces
benchmark reports against round-robin, least-queue, and best-fidelity-only
baselines.

## Current Boundary

- Local demo only.
- No cloud access.
- No token reads.
- No hardware submission.
- Real backend adapters are represented as dry-run metadata boundaries until an
  authorized customer or partner supplies credentials outside the repository.

## Demo Command

```bash
python3 -m quantumbridge.router demo --output-dir output/router_demo --jobs 100
```

Open `output/router_demo/index.html` to view the static demo.

## Quafu Task Evidence Command

```bash
python3 -m quantumbridge.router quafu-tasks \
  --input examples/quafu_tasks_sample.json \
  --route-workload bell
```

The sample file is only a format demo. The hard proof path is to replace it
with an authorized `/api/tasks` JSON export from Quafu, then compare per-chip
active queue pressure before choosing a backend.
