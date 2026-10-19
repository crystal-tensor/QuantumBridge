# Stage 11H Native Mixed-State Execution

Date: 2026-10-19

## Scope And Defects Addressed

The existing device path simulated pure states only. General Kraus channels
could not be inserted into native circuits, QNode.state always requested a
statevector, and NoisyEstimator could silently evaluate X/Y observables on a
noiseless state. PhaseDamping also used a different parameter convention from
the standard PennyLane/Aer channel.

This change adds independent native mixed-state execution and integrates it
with the same Circuit, Backend/Job, V2 primitives and QNode interfaces. It is
shared infrastructure under the existing four categories and 19 subdomains.
There is no Studio implementation or taxonomy change.

## Implemented Behavior

- DensityMatrixDevice applies local gates and Kraus channels by tensor
  contraction, without constructing full-system gate matrices or first
  simulating a pure state. Arbitrary bound unitary gates are supported.
- Circuit.kraus/channel and native quantum_info channel.to_instruction provide
  ordered single/multi-qubit CPTP channels. Invalid/nonfinite or non-TP channel
  instructions are rejected. Native channel representations can feed the
  circuit path, not only standalone mathematical calculations.
- Mixed initial states, reset, mid-circuit reads, nested if/else and classical
  feedback use the existing ordered execution semantics. Analytic execution
  merges equivalent classical branches and discards dead branch snapshots.
  Shot execution does not enumerate all classical measurement histories.
- Native NoiseModel end-of-circuit channels support general single-wire Kraus
  maps, including amplitude damping. Readout errors affect classical records
  and downstream feedback, not an unmeasured quantum density matrix.
- DensityMatrixBackend is discoverable through Provider and supports batches,
  binding, mixed initial-state overrides, noise overrides, memory and V2
  Sampler/Estimator. Shared simulator execution preserves per-run isolation.
- Result.density_matrix is first-class copy-returning data with JSON roundtrip.
  Aer-adjacent density_matrix dispatch and DensityMatrixSimulationResult encode
  matrix data explicitly, without the old helper's four-qubit cap.
- Native QNode returns a matrix for state on DensityMatrixDevice, supports
  inline channel methods, reduced states, expectation, variance, sampling and
  classical shadows. Its default pure-state behavior is unchanged.
- DensityMatrix.from_circuit/evolve execute noisy circuits; reset/measure and
  embedded circuit evolution are callable. Channel evolution dispatches to the
  actual quantum map rather than treating it as a unitary matrix.
- Qiskit unitary/Kraus import and export preserve local wire ordering. Channel
  and unitary matrices serialize as structured real/imag arrays in IR metadata.
  Compiler boundaries preserve inserted Kraus instructions.

## Semantic Corrections And Migration

PhaseDamping(p) now attenuates coherence by sqrt(1-p), matching the standard
channel definition. Previously it attenuated by 1-p. To reproduce old behavior
at p_old, set p_new = 2*p_old - p_old*p_old. The stabilizer-equivalent Pauli
mixture is updated consistently to phase-flip probability
(1-sqrt(1-p))/2. This change was driven by an observed default.mixed parity
failure, not by renaming an unsupported path.

NoisyEstimator now computes Tr(rho O), including X/Y and Hamiltonians, from the
noisy state. It no longer uses diagonal counts for non-diagonal observables or
falls back to noiseless amplitudes. Analytic quantum expectations do not apply
classical readout flips unless feedback has physically changed the state;
sampled/readout records include readout noise. Mixed initial-state validation
uses an absolute trace tolerance rather than accepting a relative trace error.

Native wire indices and bitstrings remain q0-first; classical memory is
c0-first. Qiskit printed-register order and local matrix qargs are explicitly
translated by the bridge. This is not a global promise that every existing
SDK-like namespace already has identical subsystem conventions.

## Verification

Native tests compare local density contractions with explicitly expanded
operators on random mixed states and permuted wire sets. Tests execute all
implemented channel representations as physical instructions, complex IR/JSON
roundtrips, mixed result serialization, non-Clifford feedback, reset, repeated
read/overwrite, branch-liveness merging, seeded memory, backend options,
observable regressions and finite-difference QNode behavior.

Optional Qiskit tests compare random multi-qubit Kraus evolution, provided
unitary/Kraus circuit import/export and dynamic density/counts against Aer.
Optional PennyLane default.mixed tests compare density matrices, reduced
states, expectations and variances at four parameter values.

```bash
python -m examples.native_mixed_state_quantumbridge
```

Validation used a clean archive of the tracked tree plus this staged change;
unrelated user-owned Router/Studio working files were not included or edited.

| Check | Result |
| --- | --- |
| Full suite without Qiskit/PennyLane or other optional SDKs | 662 passed, 83 skipped |
| Full installed-ecosystem suite | 809 passed, 4 skipped |
| Explicit pytest-cov run | 85.82% overall |
| DensityMatrixDevice coverage | 93.12% |
| DensityMatrixBackend coverage | 100% |
| Shared execution helpers coverage | 93.65% |
| Focused Qiskit 2.6.0 / PennyLane 0.42.3 environment | 225 passed, 4 skipped (Aer absent) |
| bash scripts/run_local_matrix.sh | Exit 0 |
| Native mixed-state example without upstream SDKs | Exit 0 |
| git diff --cached --check | Exit 0 |

The full installed environment uses Qiskit 2.4.1, Aer 0.17.2 and PennyLane
0.44.1. Its four skips are the separate pyquafu/NumPy environment, two missing
Dynamics tests and the absent Optimization dependency. The local matrix retains
its optional/advisory dependency skips; exit zero does not certify absent
dependencies or hardware. Its existing pytest-cov detection also skips coverage
despite the installed plugin, so coverage above comes from a separate explicit
`pytest --cov=quantumbridge` invocation, not the matrix script.

The standalone example verifies trace one, a mixed-state purity below one,
Result JSON roundtrip, a noisy QNode expectation and a noisy X expectation.
There is no new cloud/hardware submission in these measurements.

## Resource And API Boundaries

Dense density storage is exponential. max_memory_mb estimates working and
branch buffers and rejects oversized jobs before allocating the state;
max_branches bounds exact classical ensembles. Shot execution avoids the
classical branch cap but still requires a dense quantum state. These are
explicit resource limits, not an efficient simulation claim for arbitrary
large quantum circuits.

Native NoiseModel still means final single-wire channels before terminal
readout; this is not the complete gate-attached Aer NoiseModel/QuantumError
API. In-circuit Kraus instructions are the way to place arbitrary channels at
specific points and wire subsets. Rectangular/non-qubit quantum maps remain
mathematical quantum_info objects, not fixed-width circuit instructions.

This is not full Aer, default.mixed, QNode or SDK parity. MPS/save instructions,
full automatic differentiation across Torch/JAX/Autograd/TensorFlow, arbitrary
classical expressions/loops, general dynamic routing, complete serialization
and all named channel/device APIs remain open. QNode still uses the native
Tape callback contract rather than implementing every PennyLane constructor,
capture and execution protocol. No new cloud or Quafu hardware result is
claimed. No tags/releases or third-party sources/environments are created.

## References

- [PennyLane default.mixed](https://pennylane.ai/devices/default-mixed)
- [PennyLane PhaseDamping mathematical definition](https://docs.pennylane.ai/en/stable/code/api/pennylane.PhaseDamping.html)
- [Aer simulator methods](https://qiskit.github.io/qiskit-aer/tutorials/1_aersimulator.html)

These are API and mathematical references, not source ports.
