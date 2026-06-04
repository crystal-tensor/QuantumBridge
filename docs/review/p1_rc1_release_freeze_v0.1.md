# P1 RC1 Release Freeze v0.1

Status: P1 RC1 tag created and pushed  
Date: 2026-06-04  

QuantumBridge v0.1.0-p1-rc1 is a release candidate baseline. It is not a
production release and does not claim full Qiskit or PennyLane feature parity.

## 1. Release Tag

- Tag: `v0.1.0-p1-rc1`
- Tag type: annotated Git tag
- Tag message: `QuantumBridge P1 release candidate 1`
- Remote: `https://github.com/crystal-tensor/QuantumBridge`

## 2. Commit SHA

- Frozen commit: `bbd4bbca5c5a04ad009504874b14c8e9387b52c0`
- Short SHA: `bbd4bbc`
- Commit message: `docs: prepare remote CI verification for P1 RC`

## 3. GitHub Actions Run

- Run id: `26938623406`
- Workflow: `QuantumBridge Test Matrix`
- Run URL: `https://github.com/crystal-tensor/QuantumBridge/actions/runs/26938623406`

## 4. Matrix Results

| Matrix profile | Result |
| --- | --- |
| `core-only` | success |
| `qiskit-extra` | success |
| `pennylane-extra` | success |
| `dev` | success |

## 5. Local Test Result

Stage 5.6 local validation:

```text
pytest -q -rs
68 passed in 1.97s
```

## 6. Coverage Result

Stage 5.6 local coverage validation:

```text
pytest --cov=quantumbridge
68 passed in 2.53s
TOTAL 1310 statements, 160 missed, 88% coverage
```

## 7. Current Capability Scope

Included in the P1 RC baseline:

- native circuit, operation, measurement, IR, result, device, gradient, and
  simple algorithm foundation
- statevector and shot-sampler execution for the supported subset
- Pauli/Hamiltonian and sparse operator basics
- OpenQASM-style subset import/export
- optional Qiskit basic circuit import/export and counts result adapter
- optional PennyLane observable/tape/executable bridge subset
- QML-style QNode/Tape/template basics
- NumPy/Torch/JAX array interface helpers
- lightweight provider/backend/job abstractions
- compiler PassManager basics and limited native optimization passes
- basic noise channel objects and noise metadata
- legal, attribution, and CI baseline records

## 8. Unsupported Scope

Not included in the P1 RC baseline:

- full Qiskit feature parity
- full PennyLane feature parity
- full OpenQASM grammar support
- Qiskit Aer execution adapter
- real noisy execution path beyond current metadata/basic channel objects
- production transpiler/routing/layout/decomposition stack
- hardware/cloud provider integration
- production visualization
- production release guarantees

## 9. Legal / License / Trademark Notes

- QuantumBridge uses Apache License 2.0.
- Qiskit and PennyLane license records and third-party notices remain present.
- Qiskit and PennyLane support is optional adapter/compatibility behavior.
- QuantumBridge is independent and is not endorsed by IBM, Qiskit, Xanadu, or
  PennyLane.
- Do not market this release candidate as a full replacement for Qiskit or
  PennyLane.

## 10. Production Readiness

This release candidate is not production ready. It is suitable for internal
review, CI baseline validation, and P2 planning.

## 11. P2 Permission

P2 code development is not allowed on the frozen P1 RC baseline. P2 may begin
only from an explicit new branch after this freeze is accepted.

## 12. P2 Branch Rule

P2 must start from a new branch, such as `p2/planning`, and must not mutate the
P1 RC tag. Any P2 work must preserve the ability to reproduce
`v0.1.0-p1-rc1`.

## 13. Conclusion

The P1 RC1 baseline is frozen at `bbd4bbc` and the tag
`v0.1.0-p1-rc1` is ready for pre-release review. Do not create a production
release from this tag.
