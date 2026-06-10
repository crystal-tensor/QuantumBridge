# QuantumBridge Studio CLI Contract v0.1

Stage 10E adds a small local CLI:

```bash
python -m quantumbridge.studio <command>
```

The CLI uses Python `argparse` and adds no heavy runtime dependency.

## Commands

- `generate-seed`
- `list-workflows`
- `execute --workflow <workflow_id>`
- `benchmark --suite <suite_id>`
- `export --workflow <workflow_id> --format json|markdown|python|notebook`

All commands print structured JSON. The CLI calls the same local Studio backend
services as the frontend seed generator. It does not access cloud services, read
tokens, access hardware, start a server, or open ports.

## Examples

```bash
python -m quantumbridge.studio list-workflows
python -m quantumbridge.studio execute --workflow aer.statevector_native
python -m quantumbridge.studio benchmark --suite basic
python -m quantumbridge.studio export --workflow aer.statevector_native --format json
```
