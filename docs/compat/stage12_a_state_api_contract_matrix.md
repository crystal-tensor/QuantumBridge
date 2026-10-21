# Stage 12-A State API Contract Matrix

Date: 2026-10-21. Status: AUDIT STARTED; P0 native implementation NOT DONE.
Native baseline: b1d345b3731276f5f2721cb42c2397d98981ac5c.
This is a bounded initial matrix, not the complete SDK/API inventory.

## Evidence And Limits

- `qb-stage11pc3r2-tableau-v2-next-api-survey.log/.exit`: native versus public
  Qiskit 2.4.1 signatures and from_int probes, exit 0.
- `qb-stage12a-public-state-contracts-{qiskit241,qiskit260}`: initial probes
  exit 1 because the harness did not capture the public empty-tuple construction
  failure. They are incomplete surveys, not native product red tests.
- `qb-stage12a-public-state-contracts-corrected-{qiskit241,qiskit260}`: public
  numerical API probes with per-case exceptions captured, both process exits 0.
  Each records 158 case results. Structured JSON case comparison exits 0;
  this sampled set shows no version difference. It is not 158 passing native
  tests, nor proof that the versions never differ elsewhere.
- Public packages were called as reference oracles only; no upstream execution
  is added to QuantumBridge, and no implementation/test source was ported.

## Initial Function Matrix

| Contract | Public 2.4.1 / 2.6 Observed Behavior | Native Baseline | Status |
| --- | --- | --- | --- |
| Statevector.from_int(5,(2,4)) | Dimension 8, dims (2,4), num_qubits None, nonzero amplitude index 5 | Dimensions flattened to (2,2,2), num_qubits 3 | Partial; real representation gap |
| DensityMatrix.from_int(5,(3,2)) | Dimension 6, dims (3,2), num_qubits None, populated element (5,5) | Rejects non-power-of-two size | Missing nonbinary construction |
| Explicit (2,3,2) and single dimension 6 | Actual basis states and subsystem metadata retained | General subsystem metadata unsupported | Partial / Missing |
| dims(qargs) | Returns selected declared subsystem dimensions; qarg0 of (3,2) has dimension 3 | Reports only binary dimensions by qubit count | Partial |
| Statevector.tensor with a 2-state | Example (2,4) tensor (2) yields dims (2,2,4), dimension 16, populated index 11 | Existing numerical tensor; no mixed-radix metadata invariant | Partial; verify native ordering separately |
| expand / reverse_qargs | Sampled numerical and dimension propagation recorded | Existing binary implementation | Partial; mixed-radix not implemented |
| evolve raw/typed identity | Sampled (2,4) dimensions and amplitudes preserved for both numeric and explicitly dimensioned Operator inputs | Existing matrix evolution, binary metadata | Partial; audit general subsystem map next |
| probabilities | Public ndarray with selected subsystem probabilities | Existing native dict and q0-first contract | Partial public compatibility; preserve native |
| sample_memory | Public ndarray; sampled basis-state labels recorded | Existing native list / explicit per-call seed | Partial public compatibility; RNG is a later batch |
| DensityMatrix.dim | Public scalar 6 for a 6x6 matrix | Existing native shape tuple | Deliberate native contract; public boundary missing |
| from_int with explicit (1,) | Dimension 1, dims (1,), num_qubits None | Existing generic dimension-1 state is treated as zero qubits | Partial; distinguish one trivial subsystem from none |
| from_int with () | Both versions raise TypeError in these probes | Existing legal zero-qubit native paths must not be broken | Versioned public edge; do not generalize to every constructor |
| Public partial_trace | Public function traces OUT specified subsystems, unlike native keep-style convenience method | Existing binary keep-style native method/function | Partial; explicit ordering/keep-versus-discard boundary needed |
| Object seed / state arithmetic / Statevector.purity | Actual public methods exist | Known missing or partial methods | Deferred P1/P2/P3, not P0 implementation |
| Public state variance method | Absent on both classes in the signature survey | Not an actual missing public method | No speculative implementation |

The public single-qudit Statevector partial_trace-all probe also reports
ValueError in both sampled versions. Preserve the actual record; do not copy
upstream internals or infer that all partial-trace/empty-system paths should
fail. Broader legal/illegal inputs, zero-register constructors, nontrivial
complex superpositions, channels and reduction numerics still need audits and
independent mathematics before implementing the bounded compatibility contract.

## Implementation Boundary

Native q0-first, dictionary probabilities and density shape tuples remain
backward-compatible. Shared native numeric arrays must genuinely support the
declared mixed-radix state. Existing compatibility entry points should expose
verified public order/containers/properties explicitly. Neither a facade nor
upstream passthrough is the mathematical implementation. Maintain separate
native and compatibility test sets and prove composed execution without an
upstream SDK installed. The P0 implementation and its red/fix/full gates remain
open under the [execution contract](../implementation/stage12_a_native_state_api_execution_prompt.md).
