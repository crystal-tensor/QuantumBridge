# Remaining Full Functional Parity Gaps

## Current Audit: 2026-10-26

Latest directed checkpoint is R2-DYN1-B/e45d079f/1648files. Real native public
ControlFlowOp/IfElseOp/ForLoopOp/WhileLoopOp/SwitchCaseOp and Instruction-only
BreakLoopOp/ContinueLoopOp owners now inhabit the existing Circuit store.
Circuit.data exposes their live blocks/params; actual mutation, parameter
binding/copy, noncontiguous composition, captured-variable identity and final
enclosing-loop jump resources reach the existing execution path. Both actual
SDKs pass16 new owner comparisons;11 new native owner/lifetime/admission tests
pass. Directed Main2.4.1/Alternate2.6.0 each1157PASS/4same-pending-old-contractFAIL
retain every1134 previous ID; strict476PASS/4sameFAIL retains every469 ID with
no SDK/TF/JAX resolution/import. The unchanged four control/transport diagnostics
are now1PASS/3FAIL: public owner/operands passes, standard QPY both directions
and direct public-reference QASM still fail. This is not full control ABI,
standard transport, dynamic Job admission or full SDK parity. See
tmp/r2-dyn1b-audit.json and the existing DYN1-B journal section. Full replacement
remains ACTIVE/INCOMPLETE and its denominator UNKNOWN; all original full gates
and the QNode broadcast/UCCSD gaps remain OPEN.

Earlier R2-DYN1/85acd94c/1645files: real public lexical
if/else/for/while/switch/jump builders now construct existing native blocks,
preserving nested scopes, UUIDs, exception rollback and captured gate handles.
Measurement feedback actually runs on four native simulation methods and
through Compiler/IR; classical dispatch/loop checks consume the shared runtime
work account. Actual Main/Alternate1130PASS/4unchanged-old-contractFAIL each
retain all821 E2 affected IDs; strict465PASS/4sameFAIL retains all169 E2 IDs.
The three original DYN1 reds now PASS. Four additional actual diagnostics still
FAIL in both versions: real public control-op owner/ABI, native->public QPY,
public->native QPY, and direct public-reference QASM output. Explicitly lowered
QASM3 works only with explicit nonsemantic metadata-loss permission. Full
dynamic multi-PUB/max-work/classical-memory admission and typed packed backend
results are not proved. DYN1 and B4 NOT_ACCEPTED; complete independent full
replacement remains ACTIVE/INCOMPLETE. See tmp/r2-dyn1-audit.json and the
existing DYN1 journal section for exact scope, source/archive and retained reds.

Earlier R2-PV2-B4-E2/a59bab8d/1642files: real native
SparseObservable, typed ObservablesArray, compiled-layout Estimator execution,
bounded sparse projector composition and reentrant local admission are now
implemented and independently/dual-SDK tested. Main2.4.1 and isolated2.6.0
each817PASS/4same-old-contractFAIL, including128 new public differential cases;
strict SDK-free165PASS/4sameFAIL. All669 E1 affected IDs and every E1 test file
are preserved; the four Human-pending old assertions remain unchanged. Original
GAP1 complete12 stays6PASS/6FAIL and public-corrected12 stays10PASS/2FAIL in both
versions, including real QNode broadcast/UCCSD gaps. Evidence and exact current
source/archive are in tmp/r2-pv2-e2-audit.json and the E2 journal section.
Full TranspileLayout, complete helper/error/raw-mutation ownership contracts,
general dynamic primitives, asynchronous/remote provider semantics and original
full gates remain OPEN. The shared admission lock serializes local primitive
execution; it is not a parallel-performance claim. B4 is still NOT_ACCEPTED.

Earlier R2-PV2-B4-E1/d687577e/1637files and B1/B2/B3/
canonical-only statuses are retained as chronological evidence, not current
default-entry verdicts. Full independent replacement remains incomplete.

The dated Stage11O checkpoint below is retained as history, not the current
capability verdict. Stage12 has since added real bounded native symbolic,
composite/circuit, compiler, quantum-info, four-framework differentiation,
TF/MPS and QPY13 capabilities. In particular JAX/TF, classical shadows,
fermionic excitation and metric/QNG helpers must not be described as wholly
absent. Their complete public SDK contracts are still not accepted.

The current R2-GAP1 functional accounting is in the existing
[implementation journal](stage12_b_p4u3d_bits_registers_progress.md#r2-gap1-functional-accounting-and-actual-public-contract-reds).
Raw source/JUnit/node/origin-linked evidence is
`tmp/r2-gap1-functional-accounting.json`. It maps all28 original named matrix
lane purposes in order, but it is NOT an exhaustive all-public-method/behavior
inventory. The full SDK denominator and completion percentage remain UNKNOWN.

The prior GAP1 selected candidate was5a47a0ec/1619files, not committed HEADb443430.
Fresh actual curated runs:105PASS Main,105PASS isolatedAlternate,99PASS strict
SDK-free; lane samples16PASS; native structural/AD104PASS. Fresh actual public
gap probes give3PASS/9FAIL in BOTH Qiskit2.4.1/PL0.44.1 and2.6.0/0.42.3. These
overlapping counts do not measure completed APIs. Seven failures concern public
Primitives constructor/register/broadcast/observable/precision metadata/job
contracts; the other two are QNode operation broadcasting and absent public
UCCSD template entry. Existing native scalar physics controls pass.

Remaining broad domains: complete Circuit/library/quantum_info/compiler public
families, full Primitives/Provider/Backend/Job, full formats, Aer/noise/general
MPS, complete QNode/devices/transforms/AD/templates/qchem/plugins, algorithms
and industry families, plus truthful authorized hardware service validation.
Old defaultOperator56, annotation-index2, public QASM loss and other recorded
version/alias/format/gradient differences remain OPEN, not hidden behind greens.

Owner has now explicitly approved option B: the StatevectorSampler/Estimator
defaults will implement public V2, with the original Sampler/Estimator/backend
and explicit Legacy behavior preserved. Only the precisely listed three alias
tests may migrate, retaining their original math and Legacy assertions. This
authorization is received, not a continuing blocker or blanket old-test waiver.

The first production input-container increment is74b56a1e/1623files: native
BindingsArray/SamplerPub support shaped binding, existing Circuit execution,
coercion and bounded owned storage. Actual strict primitives62PASS and actual
Main/isolatedAlternate affected496PASS each (including21 real public input
comparisons), zero skip/xfail. All original test files remain byte-identical.
Initial affected runs omitted JAX x64 and gave five float32 failures each;
the exact same496 IDs pass under the established x64 runner configuration,
with both original failing receipts retained. See the existing journal's
R2-PV2-B section and `tmp/r2-pv2-b-bindings-audit.json`.

This is NOT public V2 execution acceptance: target defaults still point to
Legacy, the three old tests have not migrated, all original7 Primitive reds
remain (complete GAP1 still3PASS/9FAIL in both environments), and container
acceptance/timing differs for duplicate/nonfinite/foreign-owner inputs. Next
production work must resolve that public/safety boundary and implement actual
packed sampling, observable broadcasts, precision/trajectories, Job and whole
PUB admission. No final broad/411TF/full28matrix/FULL/coverage/legal/Git gate is
claimed from this directed increment. No dependency/Git/cloud/hardware/UI
changes. Full independent native replacement remains ACTIVE / INCOMPLETE.

Latest B2 increment is5fffca70/1626files. Representation versus safe bind/Job
admission is now separate; the explicit in-progress primitives.v2 module runs
real Native unitary Sampler PUBs with true shot memory, named/ND packed bytes,
local Job/cache/errors and shared-ledger lifecycle checks. Actual current
Main/isolatedAlternate directed539PASS each include39 actual public cases;
strict SDK-free87PASS. The prior496 IDs are retained. This is not the default
API yet and must not be treated as the final opt-in replacement strategy.
Original GAP1 remains3PASS/9FAIL in both SDK environments, without deselection.
Next: reset trajectories and full public result/helper/export contracts, then
the approved default Sampler/two-test migration and frozen protection gates,
followed by Estimator. Public duplicate explicit reordering has uninitialized
upstream columns and is precisely rejected natively; full owner/error behavior
also remains OPEN. Detailed scope and original failed oracle/race receipts are
in the existing journal's R2-PV2-B2 section, with
`tmp/r2-pv2-b2-audit.json`. No FULL/final acceptance follows from these counts.

Historical B3 candidate0145747f/1631files DOES migrate the StatevectorSampler
default to actual Native public V2, preserving explicit Sampler/LegacySampler/
BackendSampler. Exactly two approved old tests migrate with original old
bodies independently protected under Legacy; Estimator's third test is intact.
Unconditional reset trajectories and additional packed-result helpers execute
through existing Native kernels/ledger. Actual Main/Alternate592PASS include
73 public differential cases; strict106PASS. Frozen broad gives8710PASS plus
the same4oldXFAIL in each environment; protected SDK-free1836PASS/37oldSKIP;
all nine original examples complete. Both411 TF/MPS gates actually terminate
411PASS/exit0 with all original node IDs preserved. Final source/archive/origin/
old-test/skip/xfail consistency audit tmp/r2_pv2_b3_audit.py actually exits0;
that audit is not full functional acceptance.

Original full GAP1 remains3PASS/9FAIL, but four failures now occur exactly at
the old shots= Legacy constructor in the preserved diagnostic. A distinct
complete public-corrected12 keeps the same physics/tolerances and actually
gives7PASS/5FAIL. Estimator label/broadcast/precision, QNode broadcast and UCCSD
are real remaining gaps; they are not deselected or reclassified as harness
issues. Native StatevectorEstimator is STILL Legacy, not public V2. General
Sampler classical-control/directive/dynamic coverage, complete helpers/types/
errors and original R2/full SDK gates remain OPEN. See the existing B3 journal
section for exact hashes, preserved failures and local-only scope.

Four new actual canonical result-type failures also remain OPEN in both SDK
environments: primitives.BitArray/DataBin/PrimitiveResult/PubResult still export
Legacy classes, not the new default Sampler's result classes. Independent
Public/Native probe gives4FAIL/2PASS (Job/SamplerPubResult pass). These are real
Native export gaps, not LEGACY_HARNESS_ABI_MISMATCH. Extra old container/
isinstance assertions were not changed beyond the exact two approved Sampler
migrations. B3 is not accepted as complete public-container/default parity.

B4 canonical closure supersedes those four public type failures. Historical
dcddd6e2/1633files moves the exact old container class/function bodies to an
explicit Legacy module; internal Sampler/Estimator/backend behavior retains
that path. root/primitives/containers now expose real Native public classes.
The original canonical probe IDs now6PASS each; current full affected gates
611PASS/4FAIL each and strict112PASS/4FAIL, zero deselection/skip/xfail/error.
The four failures are distinct old canonical Legacy type/to_dict/tolist
contracts, all existing assertions unchanged. Exact IDs and requested human
migration authorization are in the B4 journal section. No response has been
applied; this does not block continuing actual Estimator implementation.
All current sources/receipt manifests/Legacy AST preservation are audited in
tmp/r2-pv2-b4-canonical-audit.json. Estimator V2/its three genuine reds and
third authorized alias test remain OPEN. Prior B3 broad/TF results prove only
the old0145747f candidate, not this current edit. B4 NOT_ACCEPTED; full goal
ACTIVE/INCOMPLETE.

Latest B4-E1 d687577e/1637files implements actual Native StatevectorEstimator
V2 and switches its default after directed mathematical/resource/public proof.
ObservablesArray/EstimatorPub, Pauli label wire-order conversion, true complex
three-qubit(3,2,2) broadcasts, per-cell reset/precision RNG, actual Job/data
types and shared-ledger admission/leases execute. Estimator/LegacyEstimator/
BackendEstimator retain their old ensemble/nesting and return contracts.
Exactly the third approved alias test migrated; its original body executes
under Legacy with AST-exact preservation after the entry name change.

Current Main/Alternate affected665PASS/4old-contractFAIL each retain prior615
IDs; directed53PASS each include25 real public cases; strict complete primitives
141PASS/4sameFAIL, no SDK/TF/JAX resolution/import. Complete original12 now
6PASS/6FAIL (four old Sampler ABI + QNode/UCCSD), distinct corrected12 now
10PASS/2FAIL. The original three Estimator real reds are actually green in
both versions, not deselected. Full helper/type/SparseObservable/layout/error/
owner/dynamic contracts remain OPEN. The four additional old test migrations
await actual Human authorization and remain untouched. Current-source final
broad/411TF/protected SDKfree/examples and all original R2 full gates remain
OPEN; earlier B3 passes cannot prove this edit. See the existing B4-E1 journal
and tmp/r2-pv2-b4-e1-audit.json for exact provenance, original failed attempts,
real fixed concurrency deadlock and supported scope. B4 NOT_ACCEPTED; full
goal ACTIVE/INCOMPLETE, completion denominator UNKNOWN.

## Historical Stage11O Checkpoint

Date: 2026-10-20; Stage 11O-B6 checkpoint from local `bd88f88`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This is a remaining-work ledger, not a reduced definition of success.
The pinned public versions used as test oracles do not prove all versions or
all current public APIs. Inventories, adapters and green tests are not parity.

## Prioritized Core Work

| Priority | Capability still required | Existing evidence versus missing final contract |
| --- | --- | --- |
| 1 | Complete measurement/transform semantics | B1-B6 execute real supported graphs. Complete dispatcher, reset/postselection, general classical measurement expressions, conditional MCM, noisy feedback, snapshots/full-state contracts and arbitrary transforms remain incomplete |
| 2 | Full differentiable interfaces | Native first-order CPU Torch/Autograd are tested. JAX/TF end-to-end, simulator backprop, higher-order differentiation, capture/Catalyst and GPU contracts remain unimplemented/unsupported |
| 3 | Full derivative/device protocols | Actual shift/adjoint/Jacobian products exist. Matrix-free VJP, all generators/gradient transforms, metric/QNG semantics, loop-aware differentiation, stochastic and plugin derivative protocols remain incomplete |
| 4 | Complete QNode/devices/plugins | Existing native runtime supports typed trees, sampling and branches. Full constructor options, executors, dynamic-shot/device-vjp/capture and default.qubit/lightning/mixed/remote/plugin contracts remain incomplete |
| 5 | All operations and template families | Eight template families execute. Complete UCCSD/QAOA/arithmetic/state preparation synthesis, broadcasting, all operation families and compatible object/serialization contracts remain incomplete |
| 6 | Complete QuantumCircuit/classical API | Parameter algebra/control flow/compose/control/inverse/power execute bounded subsets. All signatures/types/scopes/conditions, calibration and instruction scheduling remain incomplete |
| 7 | Complete circuit.library | Native bounded gates, ansatz and arithmetic/data encoding are not the full gate/template/synthesis/data-preparation catalog |
| 8 | Complete quantum_info | Native vector/density/operator/Clifford/Pauli/channels/metrics/random/MPS subsets exist. All dimensions/subsystems, synthesis, general maps and public containers/options remain incomplete |
| 9 | Complete transpile/PassManager/Target | Real DAG translation/routing/static schedules execute. Arbitrary synthesis, full pass/plugin/flow protocols, full backend calibration schemas and dynamic/pulse timing remain incomplete |
| 10 | Complete Aer | CPU vector/density/tableau/MPS and Save/Set/noise subsets execute. Full methods/options/aggregation/readout, optimized performance, GPU/parallelism and extended methods remain incomplete |
| 11 | Complete Primitives V2 | Native PUB/Job/results/counts/observables execute. Full broadcast, precision/shots/containers/errors and provider contracts remain incomplete |
| 12 | Complete Provider/Backend/Job | Native local lifecycle exists. Complete discovery, options, cancellation, true async and authorized remote service behavior remain incomplete |
| 13 | Complete QPY and OpenQASM 2/3 | Real QPY v13 plus bounded QASM2/3 parsing/exporting exist. Other QPY versions, complete languages/types/functions/arrays/includes and all object families remain incomplete |
| 14 | Full algorithms/optimizers | Native bounded eigen/phase/amplitude/VQE/QAOA/Grover slices are not all algorithm families, results, optimizers and execution glue |
| 15 | Full qchem / Nature | Real hydrogen s-shell/RHF/fermionic/JW workflows exist. Differentiable HF, other elements/basis sets/angular momentum, open shells, properties, active spaces/tapering, full UCCSD and all chemistry APIs remain incomplete |
| 16 | Full kernels/QNN/resources/qcut/shadows | Existing executable examples/subsets do not establish complete families, derivative contracts, device integration or public interfaces |
| 17 | Complete industry ecosystem | Finance/Optimization/ML/Experiments/Dynamics and all remaining ecosystem projects need full independent functions, actual composed workflows and validated results; optional upstream object lookup is not completion |
| 18 | Actual authorized remote execution | IBM Runtime full service behavior and real Quafu/QOS-UQCI backend/job/target evidence remain incomplete. A token, offline/mock result or simulator success is not hardware evidence |

The next implementation stage should be selected against these concrete gaps
after the joint review. This ordering does not remove any requirement from the
full goal or declare lower-priority functions complete.

## Explicit B6 Limits Still Open

Coherent deferral currently rejects reset/postselect (including impossible
selection), configured noisy feedback, arbitrary nonunitary/Kraus operations,
conditional measurements, runtime loops, Store/arithmetic, measurement-derived
gate parameters, mid-state snapshots and undefined full-state requests.
Bounded Boolean records and numeric probabilities do not implement the entire
MeasurementValue API. Opaque controls/dense observable remapping, arbitrary
classical memory and full Capture/public dispatcher semantics remain partial.
Fresh ancillas consume actual device/Target capacity. Default output-wire
handling and native `records=` signatures are documented native behavior,
not a claim of identical public API shape. See the B6 implementation report.

## Chemistry And Hardware Truthfulness

Native H2 geometry-dependent energy and gradients do not establish all
molecules, ground-state convergence, complete materials calculations or a
fully differentiable electronic-structure pipeline. Conditional-feedback
chemistry examples need not conserve electrons. Real hardware cannot be
assumed to expose simulator statevector/density APIs or unlimited ancillas;
mapping and measurement limits need actual authorized backend validation.

Industry organization remains the owner's four categories and 19 subdomains:
scientific computing, finance, industrial optimization and quantum security.
That taxonomy is not evidence that their chemistry/biology/materials, financial,
logistics/energy or security workflows have all been implemented and verified.
Core functional implementation remains first priority; Studio remains last.

## Publication And Evidence Gaps

The retained local 11M/11N/11O-C/11O-A/B1-B5 chain is not proof of publication.
Prior workflow OAuth/network limitations have not been bypassed. A fresh
successful fetch, fast-forward verification, ordinary authorized push and
matching new-SHA Actions jobs are still required before claiming remote CI.
The known user untracked Router attribution failure is separate from the
tracked/index snapshot and is not silently repaired or included here.

Final completion must verify every named API/behavior and required workflow.
No local checkpoint, total pytest count, package line coverage or inventory
justifies marking the entire full replacement goal complete.
