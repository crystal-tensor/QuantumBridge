# TorchQuantum-like Layer with QuantumBridge

This clean-room example runs a small educational quantum layer using
QuantumBridge native circuits and simulation.

```bash
python3 examples/torchquantum_like_layer_quantumbridge.py
```

The example returns a `QuantumLayerResult` containing:

- feature and weight metadata;
- probabilities;
- a forward output score;
- a prediction;
- QuantumBridge circuit metadata;
- warnings and provenance.

This is not a full TorchQuantum or PyTorch replacement and is not production
QML.
