# Mitiq-Style Readout Mitigation With QuantumBridge

This clean-room tutorial shows the Stage 9G educational native readout
mitigation workflow. It does not copy Mitiq tutorial prose or source code, and
it is not hardware calibration parity.

```python
from quantumbridge.compat.mitiq.examples import bell_circuit
from quantumbridge.compat.mitiq import run_readout_mitigation_native

circuit = bell_circuit()
result = run_readout_mitigation_native(
    circuit,
    p0to1=0.05,
    p1to0=0.05,
    shots=256,
    seed=21,
)

print(result.raw_counts)
print(result.noisy_counts)
print(result.mitigated_probabilities)
print(result.to_json())
```

The native path simulates readout bit-flip errors, builds a calibration matrix,
uses a numerically guarded pseudo-inverse, clips negative probabilities, and
normalizes the mitigated distribution.

Boundaries:

- no cloud access;
- no token reads;
- no hardware access;
- no hardware calibration parity;
- no full Mitiq replacement claim;
- no production error-mitigation claim.
