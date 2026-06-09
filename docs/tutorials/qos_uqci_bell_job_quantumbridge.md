# QOS-UQCI Bell Job With QuantumBridge

Run:

```bash
python3 examples/qos_uqci_bell_job_quantumbridge.py
```

The example builds a QuantumBridge Bell circuit, converts it to a clean-room
QOS-UQCI job spec, prints warnings and provenance, and records the optional
upstream boundary. It does not access cloud, tokens, or hardware.
