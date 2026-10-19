# Stage 11N Native Aer Gap Audit

Date: 2026-10-19. Audit baseline/local main:
`76ea07729bb9f5336791785bae96c8f3be37ecad`.
This is an initial implementation audit, not a Stage 11N completion report.
Full Qiskit/PennyLane functional replacement remains active and incomplete.

## Git And Validation Baseline

Stage 11M is committed locally and must be preserved. origin/main remains
`45fe338fc0f02de9c19e0af89723755952e5fc98`; local main is ahead one, behind zero.
The ordinary HTTPS push was rejected because the existing OAuth app lacks
workflow permission. Existing SSH authentication was also unavailable. The
owner was asked to restore normal local authorization without sending tokens
in chat. There is no new Stage 11M/11N exact-SHA CI evidence.

Do not amend/reset/rebase, remove workflow changes, change TLS, force push or
alter credentials to circumvent this. Local development may continue. Keep
user Studio/Router changes and unrelated untracked files untouched.

Stage 11M clean tracked-tree baseline: SDK-free 1030 passed/117 optional skips;
installed SDKs 1252/4; alternate SDKs 1216/40; coverage 87.88018645866987%;
full local matrix exit zero. QPY v13 standard bilateral subset is real, but the
whole format remains PARTIAL. See the Stage 11M report for exact limitations.

## Existing Architecture

| Area | Actual existing behavior | Missing/risky behavior |
| --- | --- | --- |
| StatevectorDevice | Native unitary evolution, dynamic projection/feedback, finite shots and memory | No native in-program snapshot/state replacement contract |
| DensityMatrixDevice | Native mixed/CPTP/reset execution, analytic classical branches, readout and shots | No labelled intermediate save/set aggregation |
| MatrixProductStateDevice | Native tensor evolution, reductions, nonlocal gates, Kraus trajectories, shot sampling and truncation metadata | Save/set tensors not represented as executable instructions; dense save budgets needed |
| StabilizerDevice | Native Clifford/tableau operations, reset/measurement, applicable Clifford-mixture noise | Tableau save/set instruction validation and method-aware compatibility missing |
| DynamicExecutionEngine | Unified native state adapters, scoped classical storage, if/for/while/switch, break/continue and budgets | No snapshot store or state replacement event; operation-attached noise dispatch missing |
| Native NoiseModel | Explicit channel list and per-wire asymmetric binary readout errors | No global/specific gate bindings, correlated readout, general QuantumError composition or thermal constructor |
| prepare_program | Validates and orders gate/channel/measurement events | Configured channel list is inserted once near terminal measurements/end, not after each matching gate |
| Dynamic noise setup | Builds noise from the existing channel list and preserves physical collapse vs noisy stored bit | Also inserts that list at top-level terminal boundary, not per actual loop/conditional gate execution |
| Existing channel classes | Bit/phase flips, depolarizing, native Kraus, amplitude/phase damping | General constructor domains, multiqubit composition/tensor, Aer parameter conventions need public differential evidence |
| NoisyEstimator / ShotSampler | Native devices with noise and real observable reductions | Must verify new fixed-noise differentiation and per-operation dispatch; not assume existing result proves them |
| Backend / Job | Existing local run/batches/options and result/status protocol | Add simulator selection and snapshots without a conflicting job framework; validate options instead of ignoring them |
| Result | Terminal vector/density/MPS, counts/probabilities/expectation, memory and JSON | No labelled in-program conditional/pershot snapshot storage or Aer-style experiment data retrieval |
| Sampler V2 | Native PUB parameter batches, BitArray/DataBin/counts/memory | New method/noise/resource metadata needs integration, not a replacement primitive model |
| Native Aer compatibility helpers | Executable native vector/counts/density/MPS/tableau subsets | Statevector helper still has legacy four-qubit cap and narrow gate validation; not an AerSimulator facade |
| Aer upstream adapter | Explicit optional calls to installed public SDK | Passthrough is not native computation or parity evidence |
| Quantum information | Existing Operator/SuperOp/Kraus and mathematical channel algebra | No incremental simulator unitary/superop method; a final density is not a superoperator |
| Native compiler/Target | Exact-phase translation, directed routing/layout and physical timing | Noise binding contract must be defined on emitted physical operations, not assumed invariant through decomposition |
| Native QASM/QPY/IR | Real versioned serialization subsets and structured executable IR | Aer-specific Save/Set must be preserved by a genuinely supported format or explicitly rejected; private sidecar is not standard syntax |

The existing devices and control-flow engine are the implementation foundation.
Do not create a second standalone simulator that bypasses native Backend/Job,
typed runtime control flow or the existing tensor/tableau representations.

## Implementation Priorities And Proof Obligations

1. Add validated execution events for true intermediate Save/Set and a bounded
   snapshot store. Snapshots must own copies and correspond to actual execution
   positions, classical groups and shot/ensemble aggregation semantics.
2. Define native QuantumError/ReadoutError and physical gate-noise dispatch.
   Every actually executed matching gate in a loop/branch must apply its error;
   quantum-state collapse and noisy classical readout remain distinct.
3. Reuse each native method's state representation. Add bounded unitary and
   superoperator evolution where feasible; reject unsupported/GPU/extended
   stabilizer/tensor-network methods rather than aliasing them to a vector.
4. Integrate methods/options/results with existing Backend/Job and preserve
   Stage 11H/I/J/K/L/M regressions, especially noisy derivatives and QPY v13.
5. Verify 100-qubit MPS compact saves, local reductions and noise with dense
   expansion APIs forbidden. Check state, snapshot, branch and trajectory limits.

The incoming prompt's initial H -> save -> X -> save example is degenerate on
the default zero state: X|+> equals |+>. Its final clarification correctly says
to use Z/RZ or an asymmetric input. A native probe confirmed equality for H/X
and distinct states for H/Z. Tests must demonstrate true snapshot timing with
nondegenerate physics, not demand an incorrect numerical result.

All capability/status claims remain scoped. Stage 11N has not yet implemented
Save/Set or the new noise/method facade at this audit checkpoint. No cloud,
token, hardware, release/tag or Studio work is part of this batch.

## Public References

- [AerSimulator public API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- [Aer instruction library](https://qiskit.github.io/qiskit-aer/apidocs/aer_library.html)
- [NoiseModel public API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.NoiseModel.html)

These public behavioral contracts and isolated public SDK calls are references
only. No upstream implementation/test source is to be copied or vendored.
