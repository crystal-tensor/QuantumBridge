# TorchQuantum-like Batch Forward with QuantumBridge

This clean-room example runs batch forward execution over a deterministic toy
dataset.

```bash
python3 examples/torchquantum_like_batch_forward_quantumbridge.py
```

The native path accepts Python lists or NumPy arrays. If torch is installed, the
example also demonstrates the optional torch tensor interop path. Torch remains
optional and is not a required dependency.

The result includes batch size, feature dimension, outputs, probabilities,
predictions, warnings, and provenance.
