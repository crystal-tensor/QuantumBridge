# Studio Frontend Local Prototype Tutorial

Generate local Studio seed data:

```bash
python3 examples/studio_generate_frontend_seed_data_quantumbridge.py
```

Run the frontend smoke check:

```bash
node studio/scripts/smoke-check.mjs
```

Open the static prototype from:

```text
studio/index.html
```

The prototype displays local catalog records, workflow registry entries,
workflow details, sample execution results, warnings, provenance, benchmark
reports, and export payloads. It does not start a server and does not access
cloud services, credentials, or hardware.
