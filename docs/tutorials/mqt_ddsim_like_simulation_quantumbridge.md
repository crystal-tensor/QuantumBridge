# DDSIM-Like Educational Simulation With QuantumBridge

This tutorial shows the Stage 9J clean-room educational DDSIM-like path. It is
not a decision-diagram simulator parity claim and is not production simulation.

```python
from quantumbridge.compat.mqt.examples import run_mqt_ddsim_like_example

result = run_mqt_ddsim_like_example(shots=128, seed=11)
print(result["statevector"].to_json())
print(result["counts"].to_json())
print(result["comparison"].comparison)
```

The workflow executes a small Bell circuit with QuantumBridge native
simulation, returns statevector and counts data, and adds
decision-diagram-inspired metadata such as support bitstrings and unique
amplitude counts.

No cloud, token, or hardware access is performed.
