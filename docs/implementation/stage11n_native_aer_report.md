# Stage 11N Native Simulator And Gate Noise

Date: 2026-10-20. Local starting commit: `76ea07729bb9f5336791785bae96c8f3be37ecad`.
The minimum scoped native execution and local validation gates pass; publication
remains blocked. Full Qiskit/PennyLane and Aer
parity remain incomplete. This batch does not implement Studio or submit any
cloud/hardware jobs, access tokens, create tags or releases, or copy upstream
source/tests/packages. User Studio/Router changes remain untouched.

## Native Architecture And Behavior

`quantumbridge.simulator.NativeAerSimulator` uses the existing Backend/Job,
Result, devices and structured interpreter. It does not call an installed SDK
to compute native results. It selects an actual native vector, density, MPS,
Clifford tableau or bounded matrix method; it never aliases unsupported GPU,
extended-stabilizer or tensor-network modes to an ideal vector.

Circuit Save/Set are executable events, not metadata describing the terminal
state. Intermediate H/save/Z/save produces distinct states; H/save/X/save on
zero input would not, because X leaves the plus state unchanged. Saved values
own copies. Replacements overwrite the full register before later gates.
Labels, method compatibility, state normalization/density positivity/CPTP,
conditional groups and pershot storage are validated. Analytic mixed ensembles
cannot masquerade as a single pure saved vector. Numeric saves use actual
branch/trajectory weights; conditional groups renormalize unless explicitly
unnormalized. Variance uses the second moment, including Hamiltonian cross
terms. Raw finite state saves return the last trajectory; this explicit native
contract does not establish all SDK aggregation variants.

Local Pauli moments contract tensor axes instead of constructing a full Pauli
matrix. MPS amplitudes/local density/tensors are native contractions; tableau
local density uses a bounded five-wire Pauli expansion. Dense saved state or
density requests are checked against dimensions/storage budgets before expansion.
The native tensor/tableau save schema is not the SDK object representation.

The small unitary method actually composes matrices, including global phase.
Superop actually composes column-vectorized channels and reset, not a terminal
density matrix. Maps reject measurement; unitary rejects reset/noise. Maps are
deterministic, so metadata separates requested shots from actual `shots=None`.

## Noise And Physical Semantics

QuantumError owns validated bounded CPTP Kraus operators. Native compose/front,
tensor/expand and ten constructor families have mathematical/public API tests:
Pauli, depolarizing, mixed unitary, coherent unitary, reset, amplitude damping,
phase damping, phase-amplitude damping, thermal relaxation and Kraus. Thermal
constraints and the phase-damping coherence convention are tested. Construction
limits: dimension 64, Kraus count 256; depolarizing width is explicitly 1-4.

NoiseModel dispatches errors after each actually executed matching physical
gate, including each loop iteration and only the selected branch. Specific
qargs override global bindings. Quantum errors on measurement run before
physical projection; reset errors run after reset. Quantum-state collapse is
separate from stored noisy readout bits. Supported correlated readout requires
complete consecutive nonoverlapping groups with distinct classical destinations;
partial, overlapping, conditional or implicit correlated measurement fails.
The public-style positional add-readout call and old wire/error call work;
complete SDK keyword/signature compatibility is not claimed.

Native circuit/results are wire/classical-zero first. QuantumError matrices
use little-endian qargs, explicitly adapted at dispatch. Physical noise binds
to emitted instructions after native Target compilation. Decomposition/routing
can change the noisy computation; arbitrary before/after noisy equivalence is
not claimed. Legacy terminal channels retain their prior meaning.

## Supported API Tables

Every row is a supported subset, not a complete SDK signature/object contract.
`V/D/M/T/U/S` below mean vector, density, MPS, tableau, unitary and superop.

| Save API | Actual supported representation/shape |
| --- | --- |
| save_state | Actual selected-method state |
| save_statevector | V/M/T bounded full vector |
| save_statevector_dict | V/M/T native hex-index dictionary |
| save_density_matrix | V/D/M ordered local matrix; T at most five saved wires |
| save_matrix_product_state | M native tensor dictionary |
| save_stabilizer | T native Clifford/tableau dictionary |
| save_clifford | T native Clifford/tableau dictionary |
| save_unitary | U bounded actual matrix |
| save_superop | S bounded actual channel matrix |
| save_probabilities | V/D/M/T bounded ordered marginal vector |
| save_probabilities_dict | V/D/M/T bounded native hex-index dictionary |
| save_amplitudes | V/M/T selected complex indices |
| save_amplitudes_squared | V/M/T selected squared amplitudes; D diagonal probabilities |
| save_expectation_value | V/D/M/T Hermitian local matrix or native Pauli sum |
| save_expectation_value_variance | Same, with actual first/second moments |

Conditional/pershot and unnormalized modes are method/kind-validated subsets.
Raw pure state analytic mixtures and map pershot reject. Unnormalized raw
states reject; numeric saves support explicit sum versus normalized average.

| Set API | Replacement contract |
| --- | --- |
| set_statevector | V/D/M, normalized full vector |
| set_density_matrix | D, positive trace-one full density |
| set_matrix_product_state | M, native normalized tensor schema |
| set_stabilizer | T, native valid tableau schema |
| set_unitary | U, bounded full unitary |
| set_superop | S, bounded full CPTP superoperator |

| Simulator method | Scope |
| --- | --- |
| automatic | Real representation selection, metadata identifies selected method |
| statevector | Native vector, analytic ensembles and finite trajectories |
| density_matrix | Exact bounded CPTP/dynamic ensemble and shots |
| matrix_product_state | Native tensor evolution/trajectories and documented truncation |
| stabilizer | Clifford/tableau plus applicable mixtures |
| unitary | Small actual ideal unitary composition |
| superop | Small actual channel composition including reset |
| extended_stabilizer | UNSUPPORTED |
| tensor_network | UNSUPPORTED |

| NoiseModel API | Native contract |
| --- | --- |
| add_all_qubit_quantum_error | Attach after each matching executed physical gate |
| add_quantum_error | Specific physical qargs override global; repeated additions compose |
| add_all_qubit_readout_error | All-qubit single-wire stochastic readout |
| add_readout_error | Specific single wire or complete correlated group |

| QuantumError constructor | Mathematical native behavior |
| --- | --- |
| pauli_error | Finite normalized Pauli mixture |
| depolarizing_error | Full n-wire Aer-lambda depolarization, bounded width |
| mixed_unitary_error | Validated finite normalized unitary mixture |
| coherent_unitary_error | Unitary channel |
| reset_error | Identity/zero/one reset mixture |
| amplitude_damping_error | Excitation/relaxation with equilibrium population |
| phase_damping_error | Square-root coherence attenuation |
| phase_amplitude_damping_error | Combined six-Kraus physical channel |
| thermal_relaxation_error | T1/T2/time/population constrained relaxation |
| kraus_error | CPTP Kraus with optional bounded Choi canonicalization |

Each constructor has a public SDK channel comparison. Choi canonicalization
rejects more than four wires rather than allocating an oversized eigenproblem.
Readout supports asymmetric 0-to-1/1-to-0, specific/global, classical remapping,
repeated supported measurement and feedback. Correlated groups require distinct
classical destinations across the whole consecutive block to prevent reorder
of overwriting writes; unsupported ambiguous blocks explicitly reject.

## Resources And Integration

AerExecutionLimits bounds shots, trajectories, dense width/state bytes,
snapshot bytes/count, pershot bytes, conditional groups, saved dimensions,
Kraus/channel counts, branches and map dimensions. CPU/double and MPS bond/cutoff
options are validated; unsupported options are rejected, not silently ignored.
MPS metadata retains observed bond/truncation, tensor storage and snapshot bytes.
Analytic mixed MPS/tableau terminal ensembles are not promoted to one pure state;
save density/local observables or conditional/pershot states instead.

Native IR preserves events and Result JSON preserves actual complex snapshots.
Standard QASM2/3 and QPY reject these unsupported simulator-specific operations;
no private fields are claimed to be standard format support. Stage 11M QPY13,
dynamic QASM3, compiler/phase and differentiation suites remain regression gates.
Fixed-noise shift/finite-difference derivatives remain native; noisy adjoint
explicitly rejects. Full JAX/TF/capture/higher-order work is still outstanding.

## Verification Receipts

Final clean tracked-tree snapshot:
`/tmp/qb-stage11n-final-checkpoint-Q2caYD`. It contains HEAD plus the explicitly
staged batch, excluding unrelated untracked/user Studio and Router work. The
matrix's generated inventories stay in the temporary snapshot, not the commit.

| Gate | Actual result |
| --- | --- |
| SDK-free full pytest | 1120 passed, 118 optional skips |
| Qiskit 2.4.1 / Aer 0.17.2 / PennyLane 0.44.1 full pytest | 1366 passed, 4 skips |
| Qiskit 2.6.0 / Aer 0.17.2 / PennyLane 0.42.3 full pytest | 1330 passed, 40 skips |
| New independent tests | 114: 73 native simulator + 17 noise mathematical/runtime + 24 public comparisons |
| Public comparisons | Both SDK versions pass; SDK-free skips optional public module |
| Overall coverage | 88.18100757913508%, 19779/22430 statements |
| Previous baseline | 87.88018645866987%; no new exclusions, existing 68 unchanged |
| Native simulator module coverage | aer 98.18%, instructions 100%, limits 95.83%, snapshots 96.41% |
| Native QuantumError coverage | 92.11% |
| Full local matrix | Exit 0 on final checkpoint |
| compileall | Exit 0 |
| Legal/no-vendor/no-token selected regression | 9 passed; full suite also passes |
| Four SDK-free examples | All exit 0 with assertions |
| SDK-free and alternate pip check | Exit 0, no broken requirements |
| Existing global pip check | Exit 1: preexisting pyquafu/NumPy and WeasyPrint/tinycss2 conflicts |
| Staged safety scan | 30 scoped files; no environment/wheel/bytecode/private-key paths or credential signatures |
| Diff whitespace checks | Working and staged checks exit 0 |

All runs use Python 3.12.6. Installed environment also exercises Torch 2.12.0
and Autograd 1.8.0; alternate has Autograd 1.9.1 and no Torch. Both SDK
environments have optional qiskit-qasm3-import 0.6.0 for Stage 11M regression.
The SDK-free environment has neither upstream SDK nor Torch/Autograd. Optional
skips are reported, never counted as successful parity tests.

Native tests cover more than ten real Save/Set/grouping cases, at least eight
dynamic noisy cases and at least eight distinct resource/error scenarios.
The first twelve noise tests separately establish mathematical/CPTP/domain
behavior. Their channel helper also executes constructors through an actual
gate-bound native simulator, comparing to direct Kraus mathematics; the SDK
oracle tests separately compare ten constructor families to public channels.
No constructor is marked implemented from a schema/name inventory alone.

The 100-wire test disables full MPS/statevector/density APIs, saves tensors,
executes a later Z and contracts the changed GHZ amplitudes/local density.
The separate finite-shot noisy test retains per-shot tensors and correlated
GHZ measurement outcomes. Compiler noise is compared with explicit inline
Kraus at every emitted physical CX and is different from the ideal result.
Fixed gate-bound damping derivatives agree with analytic shift and finite
difference and reject noisy adjoint. Existing Torch/Autograd, QPY13 bilateral,
dynamic QASM3, compiler, primitives and devices regressions are in the full runs.

Examples (all perform assertions on actual results):

```bash
python -m examples.native_aer_save_set
python -m examples.native_aer_gate_noise
python -m examples.native_aer_density_mps
python -m examples.native_aer_dynamic_snapshots
```

The 100-wire GHZ tensor/noise/shot example observes bond 2, 12672 tensor bytes,
12910 snapshot bytes and zero discarded weight for the stated seeded run.
These are this low-entanglement example's measurements, not general complexity
or hardware evidence.

## Publication And Remaining Work

Stage 11M remains locally committed. Existing ordinary GitHub HTTPS authorization
lacks workflow scope and existing SSH authentication is unavailable. Do not
rewrite/amend commits, remove the workflow change, alter TLS/authentication or
force push to bypass this. Owner must repair normal local authorization without
sharing tokens in chat. There is no new exact-SHA CI receipt for Stage 11M/11N;
prior Stage 11L CI is not evidence for these changes.

At final validation, fetched origin/main is still
`45fe338fc0f02de9c19e0af89723755952e5fc98` and local starting HEAD is
`76ea07729bb9f5336791785bae96c8f3be37ecad`, ahead one/behind zero. The ending
feature commit is the commit containing this report, with subject
`feat: implement native aer save set and gate noise execution`; its exact SHA
and ordinary push outcome are reported in the execution handoff. The Stage
11M ancestor is preserved. No CI success is claimed for unpublished commits.

Answer: this batch genuinely adds independently executing simulator methods,
Save/Set and gate-attached noise, not just Result wrappers or upstream calls.
Answer: complete Aer functional parity has NOT been achieved. The minimum
local Stage 11N batch is tested; full package parity and publication remain
separate incomplete outcomes.

Remaining Aer scope includes all GPU/parallel/fusion/blocking options, extended
stabilizer/general tensor-network, backend-derived noise/transformation helpers,
general correlated measurement and complete SDK signatures/result/container
semantics. Full replacement remains PARTIAL. Later core priorities include full
PennyLane templates/transforms/qchem, interfaces and remaining API families;
Studio stays last and hardware requires its separate authorized verification.

## Public References

- [AerSimulator API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)
- [QuantumError API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.QuantumError.html)
- [SaveStatevector API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.library.SaveStatevector.html)

Public documentation currently labels itself Aer 0.17.1; installed public
black-box comparisons use Aer 0.17.2. These references are not copied source or
evidence that every documented function was implemented.
