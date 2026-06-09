# Mitiq-Style ZNE With QuantumBridge

This clean-room tutorial shows the Stage 9G educational native zero-noise
extrapolation workflow. It does not copy Mitiq tutorial prose or source code,
and it is not production error mitigation.

```python
from quantumbridge.compat.mitiq.examples import bell_circuit
from quantumbridge.compat.mitiq import run_zne_native

circuit = bell_circuit()
result = run_zne_native(circuit, observable="ZZ", shots=256, seed=13)

print(result.mitigated_expectation_value)
print(result.to_json())
print(result.warnings)
print(result.provenance)
```

The native path uses the Stage 9F educational simulator to generate noisy
counts, converts counts to expectation values, applies linear extrapolation,
and returns a `ZNEResult`.

Boundaries:

- no cloud access;
- no token reads;
- no hardware access;
- no full Mitiq replacement claim;
- no production error-mitigation claim.
