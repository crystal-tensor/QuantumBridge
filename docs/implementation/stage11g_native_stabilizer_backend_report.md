# Stage 11G Native Stabilizer Backend And Ordered Execution

Date: 2026-10-19

## Purpose

Stage 11F supplied native tableau algebra but execution still passed through
dense statevector probabilities. Circuit measurements were stored separately
from gates without timing, conditional metadata was not executed, and V2
sample memory was reconstructed by sorting counts. These prevented actual
stabilizer backend and dynamic-circuit behavior.

This change integrates real tableau execution into the existing Backend/Job,
Sampler/Estimator and Aer-adjacent interfaces. It is shared SDK infrastructure
under the existing four industry categories and 19 subdomains. No Studio
implementation or architecture taxonomy change is included.

## Executable Capabilities

- StabilizerDevice constructs and validates native Clifford programs, binds
  numeric parameters and samples trajectories without probability enumeration.
- Ordered computational-basis measurement, repeated writes to classical bits,
  reset, single/multi-bit conditions, nested if/else and branch-entry snapshots.
  A branch does not switch when its body overwrites the tested classical bit.
- Circuit copy, binding, compose/front-compose, defined instructions and IR
  preserve measurement positions. QASM and basic Qiskit bridge roundtrips
  preserve mid-circuit measurement order; reset is supported.
- A native StabilizerBackend is discoverable through Provider. Backend.run
  returns the existing Job contract with circuit batches, parameter bindings,
  seed, memory and per-run noise options. Per-run noise does not mutate defaults.
- BackendSampler V2 preserves real shot memory and classical register width.
  The ordinary statevector sampler also now maps measured wires into classical
  bits correctly. BackendEstimator V2 executes native Pauli observables and
  reports the actual simulation method rather than always saying statevector.
- Pauli, sparse-Pauli, PauliString and Hamiltonian expectations and variances.
  Dense output is explicit; mixed-state density matrices are formed from an
  exact stabilizer ensemble when requested.
- Native NoiseModel single-wire Clifford-unitary mixtures, bit/phase flip,
  depolarizing and phase damping, with asymmetric readout errors. Shot mode
  samples errors and measurements; analytic mode sums their exact branches.
- The Aer-adjacent run_stabilizer_simulator_native and backend='stabilizer'
  dispatch accept native circuits or IR without the old four-qubit limit.
- Compiler transformations retain terminal read positions. PassManager
  separates dynamic execution boundaries and restores branch metadata after
  gate decomposition, preventing cancellation across a measurement or branch.

## Runtime Contracts And Limits

- Quantum wire and observable labels follow existing native wire-zero-first
  conventions. Recorded memory is classical-bit-zero-first; unused classical
  bits are zero and a later write replaces the previous value. For a single
  Qiskit register, reverse printed bitstrings for comparison. This is not a
  claim of full multi-register Qiskit display/BitArray parity.
- Measurements created by Circuit.measure retain an operation_index in their
  metadata. Legacy measurements without this field remain terminal. IR keeps
  this optional metadata. remove_final_measurements now retains mid-circuit
  reads instead of deleting every read.
- Circuit.c_if/with_condition retain their existing circuit-wide operation
  semantics, not an InstructionSet return protocol. Use if_else for scoped
  feedback. Arbitrary classical expressions, loops, switch/case, stores and
  arbitrary upstream control-flow instructions are not implemented.
- Native NoiseModel channels apply once after the operation stream and before
  terminal readout; readout errors affect recorded bits, including feedback.
  These are not Aer gate-attached QuantumError/NoiseModel semantics. General
  amplitude damping and non-Clifford noise are rejected, not silently dropped.
  Phase damping has an equivalent native Pauli-mixture representation.
- Single stabilizer-state/statevector conversion requires a noiseless unitary
  circuit after removing terminal reads. Analytic mixed execution can grow
  exponentially; max_branches bounds explicit ensembles and raises with a
  recommendation to use shots. Shot execution does not have that branch cap.
  Explicit dense conversions and full output distributions remain exponential.
- Dynamic transpilation supports local gate conversion and optimization while
  retaining measurement/reset/branch boundaries. Dynamic coupling-map routing
  is explicitly unsupported. Direct static transformation passes reject dynamic
  input; use PassManager. This does not establish general compiler parity.
- StatevectorDevice and Operator now reject dynamic circuits instead of
  silently ignoring measurement/control effects. The statevector backend's
  conditional capability flag is corrected. Terminal reads remain accepted.
- Qiskit conditional blocks can be imported within the tested tuple-condition
  subset. Exporting conditional blocks to Qiskit/QASM is explicitly rejected
  until block reconstruction is implemented, rather than stripping conditions.

## Verification

Native tests execute branch snapshots, nested/repeated blocks, remapped
classical conditions, measurement/reset, exact noise, seeded memory, result
serialization, parameter batches and backend options. Compiler levels 0-3
preserve tested dynamic behavior. Optional installed Qiskit/Aer tests compare
ordered circuit import/export, nested if/else, mid-circuit measurement/reset
counts and Clifford-noise/readout statistics.

A 64-qubit uniform-superposition test blocks dense conversion and probability
enumeration while running Backend/Job, ShotSampler and Estimator V2. A 32-qubit
GHZ workflow exercises native Aer-adjacent dispatch and circuit/IR roundtrips.

```bash
python -m examples.native_stabilizer_backend_quantumbridge
```

Clean tracked-tree regression measurements:

| Check | Result |
| --- | --- |
| Core-only environment without Qiskit/PennyLane | 626 passed, 77 optional skips |
| Complete installed-ecosystem suite | 767 passed, 4 skips |
| Overall statement coverage | 85.58% |
| StabilizerDevice / StabilizerBackend coverage | 96.47% / 100% |
| Ordered PassManager coverage | 95.52% |
| Focused Qiskit 2.6.0 / PennyLane 0.42.3 environment | 133 passed, 3 optional Aer skips |
| Existing local matrix script | Exit 0; all available profiles passed |
| Runnable native backend example without upstream SDKs | Exit 0; 64-qubit shots and parity, feedback memory, noisy expectation |

The full installed oracle environment includes Qiskit 2.4.1, Aer 0.17.2 and
PennyLane 0.44.1. The separate Qiskit 2.6.0 environment also passes the nested
condition import and compiler/primitive integration checks. The four full-suite
skips concern the separate pyquafu NumPy environment, absent Qiskit Dynamics
and absent Qiskit Optimization. Missing optional matrix profiles are skipped.

All regression validation used a clean tracked archive plus this staged
change, excluding unrelated Router/Studio worktree changes. Coverage was
measured explicitly because the existing matrix's coverage-plugin detection
skips that step. Statement coverage is not SDK API-completeness coverage.

## Remaining Goal

The requested complete Qiskit/PennyLane replacement is not achieved. Full Aer
methods and save instructions, complete noise APIs, arbitrary dynamic circuits,
full primitive broadcasting/precision protocols, compiler/layout/scheduling,
broader ecosystems and PennyLane interfaces remain open. No new Quafu hardware
job is submitted or claimed by this classical simulator work. No tag, release,
third-party source or environment artifact is created.

## References

- [AerSimulator public methods and options](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- [BackendSamplerV2 public contract](https://quantum.cloud.ibm.com/docs/api/qiskit/2.3/qiskit.primitives.BackendSamplerV2)

These are API references; the implementations and tests are independent.
