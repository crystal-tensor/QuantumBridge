# MQT Core-Like Circuit Compatibility With QuantumBridge

This tutorial shows the Stage 9J clean-room educational MQT Core-like path.
It does not copy MQT source or docs and does not claim full MQT Core parity.

```python
from quantumbridge.compat.mqt.examples import run_mqt_core_like_example

result = run_mqt_core_like_example()
native = result["native"]
print(native.to_json())
print(result["qasm"])
```

The workflow converts a QuantumBridge Bell circuit to an MQT Core-like
dictionary, exports a small QASM subset artifact, imports it back, and records
optional upstream dependency metadata when local MQT packages are installed.

No cloud, token, or hardware access is performed.
