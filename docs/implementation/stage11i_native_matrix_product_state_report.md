# Stage 11I Native Matrix Product State Execution

Date: 2026-10-19

## Objective And Scope

The full Qiskit/PennyLane replacement objective remains active. This increment
implements the previously absent MPS simulation method as a native computation
engine, not an upstream adapter, inventory entry or dense-simulator alias.
It is shared infrastructure for the existing four-category/19-subdomain
architecture. No Studio feature or cloud/hardware result is added.

## Implemented Behavior

- MatrixProductState stores connected (left bond, qubit, right bond) tensors.
  QR sweeps maintain an orthogonality center; local gates contract tensors and
  use Schmidt SVD splits. Nonadjacent and arbitrarily ordered multiwire gates
  use a swap/gather/restore network with the original logical order preserved.
- Initial product states, supplied normalized vectors and existing MPS tensors
  are callable. Compressed state/result JSON roundtrips preserve complex values
  and truncation metadata. Tensor access and result access return copies.
- MatrixProductStateDevice executes bound unitary gates, ordered correlated
  CPTP Kraus instructions, reset, classical measurement, nested if/else snapshots
  and native end-of-circuit noise/readout. Analytic execution uses weighted pure
  MPS ensembles; seeded shot execution samples trajectories and does not
  enumerate all classical/Kraus histories.
- Pauli/Hamiltonian expectation and variance contract tensors without building
  full operators or states. Marginal probabilities and reduced density matrices
  contract only the requested output subsystem, including reordered wires.
  Arbitrary finite Hermitian dense observables are also accepted when resources
  permit; their exponential input/output cost is not hidden.
- MatrixProductStateBackend is discoverable in Provider and supports Job,
  circuit batches, parameter binding, seeds/memory, V2 Sampler/Estimator and
  isolated per-run initial/noise/truncation options.
- Native QNode accepts the MPS device for state, reduced density, expectation,
  variance and sampled measurements. Its reduced-density request no longer
  constructs the global density matrix when the device supports direct reduction.
- Aer-adjacent normalization/dispatch accepts method/backend matrix_product_state,
  native Circuit/IR and the already supported imported Qiskit circuit operations.
  Compressed analytic output is serialized without requesting a statevector.
- Shared ordered program validation is used by both density and MPS devices;
  existing mixed-state semantics and validation tests are retained.
- Analytic Estimator precision=0 is accepted; negative, nonfinite and boolean
  precision values are rejected. This fixes a V2 integration defect discovered
  by the new MPS backend test, not a claim of all precision/shot protocols.
  Estimator PUB metadata carries MPS truncation statistics per parameter set
  and observable; zero sampling standard deviation is not a zero truncation
  error guarantee.

## Precision And Resource Semantics

max_bond_dim limits retained Schmidt rank. cutoff (default 1e-16) bounds the
discarded squared Schmidt weight relative to the current block at each split;
cutoff=0 with no bond cap retains nonzero singular values. max_bond_dim can
force additional truncation. Each split renormalizes retained amplitudes.
discarded_weight sums the discarded fractions across splits; it is NOT a
rigorous final infidelity/error bound. The peak bond and truncation statistics
are propagated in compressed state/result metadata. Analytic ensemble metadata
reports the maximum cumulative discarded weight among its branches.

MPS storage can still grow exponentially with entanglement. max_memory_mb
guards estimated tensor-contraction/SVD buffers and requested dense outputs;
it is not an OS RSS limit. max_branches bounds analytic ensembles, which can
grow exponentially with channels/measurements. Shot execution avoids ensemble
enumeration but does not remove tensor-bond resource costs.

Unmeasured analytic Result contains a compressed MPS (or weighted MPS ensemble),
not an implicit dense statevector or complete probability table. Request
statevector/probabilities/reduced_density_matrix explicitly for those outputs.
Classical records remain c0-first; native wires/bitstrings remain q0-first.
Physical expectations exclude classical readout except through feedback;
recorded/sampled outcomes include readout flips.

## Verification

Independent tests compare random complex vectors and nonadjacent/permuted
multiwire unitaries with dense evolution, correlated complex Kraus channels
with density simulation, and observables, variance, reduced states, dynamic
reset/feedback, readout, branch limits, serialization and truncation with
closed forms or native exact references. Optional installed SDKs are test
oracles only: Aer method=matrix_product_state checks complex statevectors and
dynamic shot statistics; PennyLane default.qubit checks QNode measurements
at four parameter values.

The 100-qubit GHZ test actively replaces dense simulation/statevector calls
with failures. It verifies bond dimension 2, under 20 KB of tensor storage,
global X correlation, end-wire marginals/reduced density, seeded 100-wire
sampling and compressed Result. A 100-qubit QNode reduction is also exercised.
This is evidence for low-bond scalable execution, not arbitrary 100-qubit
quantum advantage or hardware execution.

```bash
python -m examples.native_matrix_product_state_quantumbridge
```

All regression runs use a clean tracked-tree archive plus the staged change;
the unrelated user-owned Studio/Router work is excluded and untouched.

| Check | Result |
| --- | --- |
| Full suite without optional upstream SDKs | 692 passed, 87 skipped |
| Full installed-ecosystem suite, explicit pytest-cov | 843 passed, 4 skipped |
| Overall coverage | 86.18% |
| MatrixProductState coverage | 95.73% |
| MatrixProductStateDevice coverage | 97.89% |
| MatrixProductStateBackend coverage | 100% |
| Qiskit 2.6.0 / PennyLane 0.42.3 focused environment | 256 passed, 7 skipped |
| bash scripts/run_local_matrix.sh | Exit 0 |
| Native 100-qubit MPS example without upstream SDKs | Exit 0 |
| git diff --cached --check | Exit 0 |

The installed full environment uses Qiskit 2.4.1, Aer 0.17.2 and PennyLane
0.44.1. Its skips are the separate pyquafu/NumPy environment, two unavailable
Dynamics tests and absent Optimization dependency. The alternate focused
environment lacks Aer, accounting for its optional Aer skips. Local matrix
advisory/dependency skips remain explicit; passing it does not certify missing
packages or hardware. Its existing pytest-cov detection incorrectly skips the
installed plugin, so coverage was measured with a separate explicit invocation.

The standalone example reports 100 qubits, bond dimension 2, 12,672 tensor
bytes, global X correlation 1.0, correct end-wire marginals, compressed JSON
roundtrip and seeded 100-wire shot outcomes. The noisy QNode expectation is
0.8353895310991418 for the documented channel/angle. No upstream simulator is
invoked by this example or the SDK-free suite.

## Remaining Full-Parity Work

This does not complete AerSimulator or PennyLane device/plugin parity. General
save/set instructions and Aer Gamma/Lambda snapshot interchange, all Aer noise
attachment/optimization APIs, GPU/distributed execution, arbitrary classical
expressions/loops, complete QNode autodiff interfaces/shot vectors/capture and
all other core/ecosystem requirements remain open. The QNode callback still
uses the native Tape contract. DefaultTensor-specific quimb/plugin behavior is
not claimed merely because both support MPS mathematics.

The full replacement goal is not marked complete. No third-party source,
site-packages, wheels or virtual environments are vendored. No tags/releases,
hardware submissions or unrelated Studio/Router changes are part of this work.

## References

- [Aer MPS method](https://qiskit.github.io/qiskit-aer/tutorials/7_matrix_product_state_method.html)
- [PennyLane tensor device API](https://docs.pennylane.ai/en/stable/code/api/pennylane.devices.default_tensor.DefaultTensor.html)
- [StatevectorEstimator precision API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator)

Only mathematical/API behavior was consulted, not upstream implementation
source or test code.
