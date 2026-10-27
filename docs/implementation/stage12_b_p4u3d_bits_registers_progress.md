# Stage 12-B P4-U3D Bit/Register Work Log

Status: IN_PROGRESS / UNCOMMITTED DEVELOPMENT; NOT FROZEN ACCEPTANCE.
The foundation entries below are historical development steps. The U3D2
continuation at the end supersedes their earlier pending-handle/QPY status.
Start HEAD:b443430ec3eb7eac418c22814e08fe6d940bf099, documentation-only
follow-up of implementation2bb61619d15831992364ff81d3ba87b333234a54.
Last accepted GLOBAL baseline91.34108013033072%, exclusions68. This is a
baseline, not coverage of the current candidate. The complete received task
is `stage12_b_p4u3d_bits_registers_execution_prompt.md`.
The previous goal turn made actual progress through terminal31-child R1
verification, scoped commits and a completely read next task. This turn
continues that full independent native replacement goal, not a reduced scope.

## Actual Public Observations

Public-only probes independently ran in actual Qiskit2.4.1 and2.6.0, without
reading implementation/test source. Initial98 cases, then103 including five
Python-view observations. The only observed version differences are wording
of three TypeErrors, not recorded values or error classes. These are behavioral
scenarios, not103 implemented functions.

- Standalone bit logical identities differ; same named/size normal Registers
  recreate equal logical bits. Quantum and classical identities differ.
- Overlapping register aliases retain all memberships and actual wire order.
- Register indexing/iteration returns new Python bit views with equal logical
  identity; Circuit.qubits retains stable cached views. Adopted standalone
  bits compare equal but are not the exact caller-owned Python wrapper.
- add_register can alias existing bits; add_bits has distinct duplicate rules.
  Public duplicate-new-bits insertion can partially mutate before ValueError.
  Native add_bits deliberately remains atomic, as required by this task;
  this observable unsafe-public-mutation difference is not hidden as parity.
- Public numeric direct Gate append reuses its operation even with copy=True;
  InstructionSet.inverse changes the actual inserted owner. Public c_if is
  absent in both observed versions. CircuitInstruction fields are read-only,
  copy retains its operation, and wrong-width construction is not append
  validation. These observations do not mean native handles are implemented.
- Zero-qubit Circuits, scalar phase operators/states, Gate/Instruction
  conversion and QPY are valid in observed cases. Classical-only to_gate
  rejects; from_instructions empty yields a real empty Circuit. An ordinary
  Instruction without operands is not a valid from_instructions entry.

Public QPY2.4 documentation was actually opened for register flag/mapping
semantics: https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.4/qpy . It is
a published protocol reference, not source implementation or proof that the
remaining encoder/decoder work is complete.

## Real Native Implementation So Far

- Immutable Bit/Qubit/Clbit/AncillaQubit logical keys; native quantum,
  classical and ancilla Registers with stable alias membership. Bit keys are
  shared immutable primitive tuples, avoiding per-bit copying of long names.
- Circuit bit collections, qregs/cregs, ancillas, find_bit, add_bits and
  transactional add_register. Logical identity and position are separate.
  Native bit lookup tables feed actual gate/measurement/compose operands.
- Copy/empty-copy/inverse/power/inplace composition retain real bit tables.
  A separate max_circuit_bits construction limit bounds materialized graphs;
  it does not pretend to account for Python allocator/RSS memory.
- Native IR has a recognized version1 structural bit_graph under registers,
  not a metadata-only substitute. It preserves loose identities, aliases,
  membership and real executable operands, rejects malformed records, and
  leaves canonical old integer-circuit IR unchanged.
- Native zero-qubit Circuits and zero-width Gate definitions, scalar full
  complex phase, repeat/compose/tensor/inverse/control and existing
  Statevector/Density behavior are real. IR Gate width zero and canonical
  QPY zero-qubit records are supported. Duration/runtime-input work is not
  implied. No claim is made that every Device supports every zero-width path.
- Tape mid-circuit measurement and conditional branches now grow/adopt actual
  classical bit identities instead of changing num_bits behind its table.
- Managed construction rejects foreign index/iterable/metaclass hooks and
  tampered bit/register graphs before callbacks/copying or partial mutation.

## Actual Development Evidence

Receipts are `/tmp/qb-stage12b-p4u3d-*.log` and matching .exit files.
They are sequential development runs, not final frozen FULLs.

| Prefix suffix | Actual result |
| --- | --- |
| public241 / public260 | each98 public observations, exit0 |
| public-views241 / public-views260 | each103 observations, exit0 |
| initial-baseline | 8failed/1011passed, exit1; command omitted JAX_ENABLE_X64 |
| initial-baseline-x64 | 1019passed/1warning, exit0 with unchanged runtime and x64 |
| foundation-reds | 33failed, exit1 on unchanged runtime |
| foundation-recovery | 1failed/32passed: wrong unmeasured classical-only counts expectation |
| foundation-native | 33passed, exit0 after correcting that fixture |
| foundation-integration | 1744passed/3xfailed/5warnings,18.51s, exit0 |
| public-differential241 / public-differential260 | each63 actual native/public cases passed, exit0 |
| bit-integration-reds | 10failed/18passed, exit1; real graph/mapping/scalar/format defects |
| bit-integration-recovery | 106passed, exit0 after genuine production repairs |
| bit-resource-reds | 5failed/3passed, exit1; actual forbidden callbacks |
| bit-resource-recovery | 114passed, exit0 after admission fixes |
| bit-graph-integration | exit4, collection/import error with nested --cov source selection; no tests ran |
| bit-graph-integration-covroot | 1failed/1977passed/3xfailed/5warnings,117.15s, exit1 |
| qnode-bit-recovery | 158passed, exit0 after actual Tape bit-growth fix |
| standard-alias-loss-reds | 3failed/5deselected, exit1; all three codecs silently lost identity |
| sdkfree-example | exit0 in actual SDK-free runtime |
| bit-focus-final-dev | 2failed/1979passed/3xfailed/5warnings,49.70s, exit1; QASM source normalization still dropped the graph before the guard |
| measure-all-register-red | 1failed, exit1; legacy implicit measurement created loose bits instead of its canonical classical Register |
| bit-focus-dev-r2 | 1982passed/3xfailed/5warnings,49.74s, exit0 after actual preflight/measure-all fixes |
| sdkfree-foundation | 99passed/63skipped,1.26s, exit0; all63 skips are unavailable public Qiskit cases |
| public-differential260-r2 | 118passed,0.30s, exit0; includes actual63 public2.6.0 differentials |
| sdkfree-example-r2 / compileall | exit0 / exit0 on current development source |

The initial JAX failures used float32 because the command omitted the existing
x64 convention. No tolerances/tests were weakened; the corrected baseline
passes. The classical-only fixture correction preserves actual classical
counter3 assertions; native implicit quantum sampling with no measurements
has an empty quantum bitstring, not a two-bit classical readout.

The QASM guard was moved before source normalization; otherwise the graph was
lost before checking it. Legacy measure_all now constructs a real canonical
ClassicalRegister when starting without classical bits, preserving its prior
standard-codec path instead of accepting an avoidable new regression.

The root coverage run is FOCUS and includes unrelated dirty Router in the
package denominator. It is not GLOBAL. At that development point the new
bits module has255/279 lines (91% displayed); later edits invalidate using
that count as final coverage. Its sole failing old QNode test revealed stale
num_bits updates; the test itself was not changed. The nested-module coverage
invocation failed importing NumPy with "cannot load module more than once per
process"; no package installation or environment repair was attempted. The
normal root-source invocation reaches real tests.

SDK-free example: counts11:4; two alias memberships; actual native gradient
-2.3067417183981926; HVP-3.6603564615668756; coherent scalar and controlled
zero-width phase assertions pass. No upstream SDK or cloud is called.

## Remaining Required Work, Not Done

1. Real CircuitInstruction storage/data view and InstructionSet owner handles.
   Native Circuit's existing fluent append remains an explicit extension;
   public append returns/arguments/broadcast/copy semantics are unfinished.
2. Public constructor/builder signatures, from_instructions and all remaining
   name/error/zero-width contracts. Existing constructors are not falsely
   labeled exact QuantumCircuit public ABI.
3. Actual standard QPY native register/loose/alias records and bilateral
   public interoperability. Current standard codecs explicitly reject new
   noncanonical graphs until encoded, not silently rename or drop them.
   This guard is a temporary data-integrity boundary, not implementation of
   those required functions or successful interoperability. Native IR alone
   is insufficient. Continue this substantive work, do not declare U3D done.
4. Full bit/register integration across Compiler/Layout/ControlBlock/Devices,
   mutable data lifetimes, resource/stale-handle/cross-record counterexamples,
   exact observable math, four AD frameworks and100-wire MPS.
5. Typed QPY/QASM declarations, classical custom Instruction records,
   duration execution/runtime inputs and further U3 work remain incomplete.
6. Current candidate three frozen FULLs, all required final FOCUS/framework
   gates, actual original28-section matrix, GLOBAL, legal/origins and
   freeze/worktree/stage/actual commit equality are NOT_RUN. Old U3C scores
   cannot accept this new candidate. No U3D commit/stage/push or remote-CI
   verification is claimed. No U4 or Studio work.

All existing unrelated Studio/Router tracked/untracked changes remain outside
this batch. No token/auth/TLS/fetch/push/cloud/hardware/vendor/PR/tag/release
or history rewrite occurs. Ultimate full native Qiskit/PennyLane parity/full
replacement remains ACTIVE / INCOMPLETE.

## Actually Received Stage-Internal Architecture Review

The real unfrozen foundation progress, failures/repairs, incomplete standard
records and RUNNING80159 were sent to the authorized conversation. Its
completed source message8a6532ab-1a19-4b8b-b7ab-758f348af39a was confirmed
by read_thread. The full rendered review and all16 sections were actually
read through Chrome's later/middle/top virtualized views with completion
controls, not inferred from the truncated stream.

The reviewer agrees to preserve native fluent Circuit and add a real native
QuantumCircuit public ABI with one authoritative operation store and the
existing engines. No global compatibility switch, stack inspection, detached
data or synchronized second Circuit is allowed. This is architecture guidance
from the supplied report, not independent source/CI inspection or foundation
acceptance. The complete stage-internal continuation is saved as
`stage12_b_p4u3d2_quantumcircuit_public_abi_execution_prompt.md`. The80159
wait condition is now fulfilled by actual1982passed/exit0, not by the older
1979passed/2failed candidate. U3D remains uncommitted and IN_PROGRESS.

## U3D2 Public ABI And Interchange Development

Actual HEAD remains b443430; native changes are uncommitted on local main.
No push, auth/TLS/token, cloud/hardware, vendor, PR/tag/release, Studio/Router
edit or history rewrite is performed. Current work is the entire received
U3D2 continuation, not a replacement of the original full SDK goal.

Implemented in this development batch:

- Native QuantumCircuit subclasses Circuit and shares its actual operations,
  measurements, parameter owners, bit graph and existing execution engines.
  Circuit stays fluent; public append/builders return checked InstructionSet.
  CircuitInstruction is a read-only context/replacement value, not a separate
  mutable circuit or a writable pointer to all fields. data mutations stage
  and validate changes before committing to the existing store.
- Actual public constructor/data/handle/builder/from_instructions observations
  now have native/public differential tests. The initial U3D2 public probe
  expanded139 ->158 ->160 cases independently in both installed versions.
  Further direct follow-up calls cover cached frame copy/bind/inverse/compose
  and generic context field snapshots. Scenario counts are not function counts.
- Standard invocation slots retain inserted parameters while exposing the
  measured reused Python owner. Public copy/bind reconstitute cached params;
  actual public inverse/handle inverse instead read the current exposed owner.
  These different semantics were measured in both versions, not inferred.
  Native fluent live-owner behavior remains unchanged. Generic custom-owner
  cached-context semantics require further work; they are not claimed done.
- Existing managed Operator/Statevector/Density/Clifford/channel paths admit
  exactly the two known native circuit classes. Unknown subclasses and array
  hooks remain rejected. Binding now preserves the actual Bit/Register graph.
  Public barrier/delay lower through the existing native engine.
- IGate, S/Sdg, T/Tdg, SX/SXdg and RXX/RYY/RZZ are actual native standard
  classes, not generic Gate objects renamed for display. Independent complex
  matrices, real inverses, QPY class records and public class names are tested.
- QPYv13 has actual normal/loose/alias/external-origin register records,
  noncontiguous/reordered wire mappings, empty registers, quantum/classical
  memberships and real restored measurement execution. Owners are restored
  before aliases independent of wire record order. The parser rejects forged
  duplicate names/owners/maps, negative internal refs, bounds, flags and
  truncation; aggregate membership work has a separate bounded counter.
  This is not a metadata bit_graph sidecar or a duplicate serialization engine.
- QASM2/3 normal named register arrays now emit real declarations and load
  into actual native register tables. Aliases, loose/reordered source graphs,
  ancillas and typed scope transport still explicitly reject rather than
  silently renumber/drop identity. Generic Instruction source refs remain
  unsupported. This is not full source format compatibility.
- Two SDK-free examples execute real public handles, four-device measurement,
  custom Gate/QPY binding, analytic Jacobian/Hessian/HVP and100-wire MPS.
  Instrumented tests forbid dense conversions in the100-wire paths. Actual
  Torch/Autograd/JAX/TF gradient calls pass in the initial new closed-loop run.
  Zero-width Instruction repetition can be staged; a defined scalar phase
  repeats coherently, while an opaque zero-width operation still cannot execute.

Actual current receipts use `/tmp/qb-stage12b-p4u3d2-*.log/.exit`:

| Prefix suffix | Terminal development result |
| --- | --- |
| public-frame-recovery | 135passed/4warnings, exit0 |
| execution-frame-reds | 20failed/7passed, exit1 |
| execution-frame-recovery | 162passed/4warnings, exit0 |
| qpy-register-reds | 37failed, exit1 on missing real records |
| qpy-register-recovery | 1failed/44passed: public measurement ref still needed a standard record |
| qpy-register-r2 | 738passed/3xfailed/8warnings, exit0 including existing serialization tests |
| builder-class-reds | 30failed, exit1 |
| builder-class-recovery | 236passed/4warnings, exit0 |
| closed-loop-reds | 1failed/20passed: standalone InstructionSet missed its append budget |
| qasm-register-reds | 6failed/8passed, exit1 |
| source-and-handles-recovery | 599passed/3xfailed/6warnings, exit0 |
| public-example | exit0, all four Devices counts11:4 |
| qpy-gradient-example | exit0,100-wire MPS gradient-2.306741718398194, HVP-3.660356461566874 |

QPY register public-only binary observations cover10 cases per version.
Ancilla is a real version difference: public2.4.1 emits a register tag that
its own loader rejects;2.6.0 roundtrips AncillaQubit. The current native QPY
subset explicitly rejects ancillas rather than claiming bilateral portability.
Loose Python wrapper UUID/object addresses are not encoded by QPY and are not
a cross-process preservation claim. Within the restored circuit aliases share
the same native logical bits and actual instruction operands.

Remaining: generic custom-owner cached frames/context equality; all remaining
public output factories/data owners; full public
mutation/from_instructions corner cases and limits; further duration/typed
transport/custom classical Instruction work. The complete required frozen
three FULLs, framework/Compiler/QNode/IR/QPY/H2/Aer/MPS focuses, GLOBAL floor
91.34108013033072% with exclusions68, original28-section matrix, legal/origins
and freeze/stage/actual commit equality are NOT_RUN for this candidate. Old
checkpoint numbers cannot accept it. Full native Qiskit/PennyLane parity and
full replacement remain ACTIVE / INCOMPLETE. No U4 or Studio work.

## Later Frame Repairs And Terminal Development Gates

The first broader main-development-focus naturally terminated exit0 with
3503passed/3xfailed/12warnings in316.49s. Its scope includes core/circuit/
compiler/information/serialization/all qml/two public differential modules.
That is the pre-final-repair candidate, not acceptance of subsequent changes.

Further actual public calls in both versions show compose(copy=True) resets
the exposed standard owner to cached invocation params, whereas copy=False
retains the changed source owner. Genuine new reds:3failed/1passed; an inverse
result's own cached frame also has1 genuine failure. Native remapping now
resolves the frame before an owned operation copy, while retaining copy=False
owner borrowing; new standard inverse results retain their own inserted frame.
These repairs do not change fluent Circuit live-owner contracts.

| Prefix suffix | Actual later terminal result |
| --- | --- |
| main-development-focus | 3503passed/3xfailed/12warnings,316.49s, exit0 before the last frame repairs |
| alternate-development-focus | 274passed/6warnings,6.64s, exit0 before those repairs |
| sdkfree-development-focus | 96passed/178skipped/2warnings,1.30s, exit0 before those repairs |
| compose-copy-frame-reds | 3failed/1passed/169deselected, exit1 |
| inverse-result-frame-red | 1failed, exit1 |
| final-development-focus | 3450passed/3xfailed/11warnings,313.81s, exit0; session81798 naturally terminated |
| alternate-final-focus | 279passed/6warnings,7.22s, exit0 |
| sdkfree-final-focus | 99passed/180skipped/2warnings,1.39s, exit0 |
| equal-width-alias-check | 1passed, exit0 after strengthening the alias fixture to equal quantum AND classical widths |
| public-example-final / qpy-gradient-example-final | exit0 / exit0 in the SDK-free runtime after the last runtime repairs |
| compileall / git diff --check | exit0 / exit0 |
| dirty-legal | 1failed/5passed; only unrelated quantumbridge/router/core.py lacks ledger attribution |

Final-development-focus selects three native second-order qml modules instead
of all qml, so3450 vs3503 are different scopes, not a full-suite delta. All
these are development FOCUS, not any of the three required frozen FULLs.
The native runtime was unchanged during that last gate. A serialization test
fixture was strengthened to compare same-width alias vs loose graphs and
separately passed the SDK-free targeted check; no production bug/tolerance or
expected numerical result was hidden by weakening it. SDK-free180 skips are
missing Qiskit public comparisons and unavailable four AD frameworks. They
are not executed native successes or an asserted optional matrix completion.
Main actual imports resolve quantumbridge to this workspace and report
Qiskit2.4.1/PennyLane0.44.1. Current controlled legal/GLOBAL/complete origins/
matrix/frozen-stage-commit checks still await the final candidate. No unrelated
Router attribution is invented and no whole dirty-workspace legal-clean claim
is made. No stage, commit or push occurs in this development batch.

## Actually Received Cached-Frame/Factory Continuation

The real partial results, generic frame/factory gaps and RUNNING81798 were
sent to the user-authorized conversation. Its completed reply
c841feab-a015-45a3-9bf7-4d7ef4c7f141 was confirmed by read_thread and its
actual completed rendered answer was read in full: the later view covered
sections2-13 and completion controls; an actual upward scroll covered the
review and complete sections0-1. The initial interrupted answer was not used.

The collaborator prioritizes generic source-owner/stored-frame/public-view
consistency, checked frame replacement and actual public factory types before
final frozen acceptance. It does not independently inspect source or remote
CI, nor accept the stage. All14 sections are saved in
`stage12_b_p4u3d2r_cached_frames_factories_execution_prompt.md`.
The first condition, waiting for81798 naturally, is now satisfied by actual
3450passed/3xfailed/exit0. This continues the original entire U3D2 scope and
ultimate ACTIVE / INCOMPLETE full native Qiskit/PennyLane replacement goal.

## U3D2-R Generic Frames And Real Factories Development

This entry supersedes earlier statements that all generic frame/factory work
is still absent. It is a supported development slice, NOT U3D2 acceptance.
The old81798 gate actually terminated exit0 before this work. No healthy
process was stopped. All following runtime changes remain local/uncommitted.

### Actual Public Observations

The public-only owner probe observed560 scenarios per version, in installed
Qiskit2.4.1 and2.6.0. It separates generic Gate, generic Instruction, a
nonunitary Instruction and RYGate; source copy/borrow, symbolic/numeric slots,
source name/label/params/definition mutations and output factories. The output
differs only at the version banner. Generic copies retain the mutated Python
display owner and old context slots; standard copies reconstruct the captured
slots. Reassigning a context into data repacks the current owner, whereas
from_instructions preserves its captured slots. Generic same-owner context
equality does not follow the standard captured-scalar equality rule.

The later public factory probe records102 outcomes per version for six circuit
kinds and17 actions: real types, names, register memberships, parameters,
phase, metadata, scope, input mutation, owner reuse and full complex Operator.
Both first runs exit1 because actual public scope.decompose raises a Rust
PanicException. The explicit diagnostic harness records that expected panic
without swallowing SystemExit/KeyboardInterrupt; both second probes exit0.
That means all102 outcomes were observed, NOT that all102 calls succeeded or
are now natively supported. Public typed Store params also differ by version.

UnitaryGate was separately observed in both versions: scalar1x1 is allowed,
CircuitInstruction.params is empty, is_standard_gate is false, and equal
numeric matrices compare equal independently of label, not global phase.
These are real public calls, not upstream implementation inspection.

### Native Implementation

- `_public_frame` captures generic and standard scalar invocation slots on the
  same authoritative Operation store. No second Circuit or stored owner list
  is introduced. Display owner mutation, captured fields and actual native
  execution are deliberately separate, with a checked resolution path.
- Generic stored slots rebind a copied owner through its declared formal
  lineage only after width/definition/cycle/resource admission. Parameter
  indexes, binding, Operator, compiler and AD consume that executable frame.
- Context replace alone is detached. Actual data assignment refreshes slots
  from the chosen owner and commits atomically. Bound InstructionSet inverse
  uses the current indexed store entry and validates all replacements before
  any commit. Read/copy of a context does not copy the entire Circuit.
- Empty public copies preserve numeric/symbolic phase. Public repeat and
  nonnegative integer power retain real repeated Gate/Instruction owners;
  measured/reset examples execute on Statevector/Density/MPS/Stabilizer.
- Tensor preserves other-first bit order, named/alias/loose graphs and the
  measured default-register collapse. Decompose reuses the native engine and
  admits actual public owners into the output, not an empty type shell.
- Zero-qubit UnitaryGate, inverse/fractional Circuit power, complex Operator,
  Statevector, coherent control, IR and standard QPYv13 now carry the scalar.
  Empty/invalid/nonunitary matrices, forged targetless non-scalar matrices
  and matrix resource limits still reject. Bilateral actual public QPY is
  tested separately from SDK-free native roundtrips.
- from_instructions retains cached symbolic slots and real loose bit
  ownership even after source binding; scalar Gate/Instruction generators
  really execute. Zero width cannot bypass aggregate operation limits.

### Actual Red/Green Evidence

All receipts use `/tmp/qb-stage12b-p4u3d2r-<name>.log/.exit`.

| Receipt | Actual terminal result |
| --- | --- |
| generic-frame-reds |42failed/26passed,exit1 |
| generic-frame-r2 |242passed/4warnings,exit0 |
| frame-resource-reds |4failed/29passed,exit1 |
| frame-resource-recovery |237passed/4warnings,exit0 |
| public-factory-reds |14failed/12passed,exit1 |
| public-factory-first-recovery |88passed,exit0 |
| measured-factory-recovery |80passed,exit0 |
| factory-integration |2130passed/3xfailed/11warnings,19.46s,exit0; before scalar/context repairs |
| scalar-unitary-reds |9failed,exit1 |
| scalar-unitary-recovery |8failed/62passed,exit1; exposed zero-wire definition validation |
| scalar-unitary-r2 |80passed,exit0 |
| unitary-context-reds |21failed/71passed,exit1 |
| unitary-context-recovery |558passed/4warnings,5.51s,exit0 |
| from-instructions-native |21passed,0.28s,exit0 |

The current larger core/circuit/compiler/serialization/information/QML/public
differential integration run was launched after the scalar/context repairs.
At this edit it is still RUNNING, not claimed green. This entry will record
its terminal result. SDK-free and alternate checks still need current runs.

### Explicit Compatibility Boundaries And Acceptance Debt

Actual public generic source mutation can leave exposed numeric owner params
but an unbound symbolic definition, including inverse/compose outputs whose
parameter index is empty and whose Operator fails. Native checked formal
lineage intentionally retains a coherent bindable executable frame instead.
This is an observable ABI divergence; it is not presented as full parity.
Numeric definitions without formal lineage cannot be guessed back into
symbolic templates. Public standard inverse retains its separately measured
live-owner behavior; generic behavior is not inferred from that specialization.

Still incomplete: canonical public decomposition recipes/classes; exact
non-inplace binding naming/flat_input signature; public factory metadata;
normalized to_gate/to_instruction definition registers; full typed Store/
control public data owners; generic controls/annotations and all remaining
public context/error/lifetime/resource contracts. Existing native-only
primitives with real definitions are not claimed identical standard classes.

No new frozen SDK-free/main/alternate FULL, GLOBAL coverage, original28 matrix,
final origins/legal/token/vendor audit, staged/committed equality or remote
CI is claimed. GLOBAL floor91.34108013033072% and68 exclusions are unchanged,
not remeasured. Dirty worktree legal still has the unrelated unowned Router
ledger failure; no speculative provenance or broad staging is allowed.
No commit/push, tag/release, auth/TLS/token/cloud/hardware, third-party source,
package installation or Studio/Router change occurs in this continuation.
The complete native Qiskit/PennyLane full replacement goal remains ACTIVE /
INCOMPLETE. Test counts are not feature-completion percentages.

## U3D2-R Terminal Development And Actual R2 Continuation

The previously RUNNING8219 naturally terminated exit0:
`/tmp/qb-stage12b-p4u3d2r-current-main-integration` has3671passed/3xfailed/
12warnings,328.18s. It covers core/circuit/compiler/serialization/information/
qml and three public differential modules, NOT FULL. The later added independent
factory->compiler->three-device analytic complex-matrix cases and real four
framework second derivatives pass in `factory-framework-closure`:
91passed,5.48s,exit0. Those20 added cases were not collected in8219 and have
their own actual terminal receipt; the runtime was unchanged during both runs.

Current alternate Qiskit2.6.0/PL.42.3 development FOCUS:
`/tmp/qb-stage12b-p4u3d2r-current-alternate`379passed/4warnings,6.19s,exit0.
SDK-free FOCUS:`current-sdkfree`84passed/99skipped,0.57s,exit0. Skips are
uninstalled Qiskit and the four AD frameworks, not executed equivalents.
No old FOCUS is called a new FULL or used to accept later runtime changes.

The real results and remaining work were sent to the authorized conversation.
Its actual completed reply7f46dd59-20f3-4add-bff1-c2785c348a0c was read fully,
including the review and all14 sections0-13. The initial interrupted stream
was not treated as complete; an actual UI scroll showed all later sections
and completed-answer controls. The whole normalized instruction is saved in
`stage12_b_p4u3d2r2_public_binding_factories_execution_prompt.md`.
It continues the whole U3D2-R/full SDK goal, prioritizes actual binding,
definition conversion and selective decomposition, explicitly permits recorded
non-parity safety differences, and does not accept a completed stage.
Its first8219-wait condition is satisfied by the real terminal result above.

## U3D2-R2 Public Binding Development

Both actual installed versions have the measured public assign_parameters
signature with keyword-only flat_input/strict, get_parameter default Ellipsis,
and positional-only has_parameter. Independently authored differential calls
cover26 binding inputs with inplace=False/True and16 queries per version.
Public-only observed outcomes in2.4.1 and2.6.0 agree. They include unknown
string KeyError versus unknown Parameter CircuitError, vector arity errors,
flat-input key restrictions, final normalized duplicate-key wins, UUID rather
than name identity, and actual new result naming. These68 scenarios are not
68 newly implemented SDK functions.

Implemented supported native public Parameter/string/vector/ordered-iterable
binding, flat_input/strict checks, bounded sequence/vector/mapping admission,
atomic inplace updates and public non-inplace naming. Query results are native
immutable UUID-preserving value views; a vector view retains the Circuit's
stored vector owner. Symbolic append(copy=True) may copy the original vector
owner, so it is not required to be the caller's original Python object.
The concrete public ParameterView collection type is still not implemented.

Internal definition binding now uses explicit bind_definition rather than
dispatching through public auto-naming. Generic/controlled/standard/annotated
owners, parameter plans, conversion parameter_map and control bodies retain
deterministic definition names. The original complete structural signature
still validates; no fields were excluded or equality/tolerance relaxed.
Native IR tests exercise numeric-bound formal plans, reload, symbolic owner
rebinding and independent rotation math. Other tests combine borrowed owner
mutation, aliases, nested symbolic phase, five binding forms, IR/QPY and an
independent full complex matrix. Managed foreign mapping/array/copy callbacks,
oversized bindings and failed inplace updates still reject before mutation.

Actual receipts use `/tmp/qb-stage12b-p4u3d2r2-<name>.log/.exit`:

| Receipt | Actual terminal result |
| --- | --- |
| binding-reds |62failed/6passed,exit1 |
| binding-first-recovery |179passed,5.35s,exit0 |
| binding-resource-reds |4failed/29passed,exit1; default-query sentinel admission and conversion IR signatures |
| binding-resource-recovery |1failed/360passed,exit1; implementation reds fixed, remaining test incorrectly required original caller vector owner |
| binding-integration |1failed/2361passed/3xfailed/11warnings,22.72s,exit1; same erroneous test assertion |
| binding-integration-r2 |2362passed/3xfailed/11warnings,22.37s,exit0 |
| binding-alternate |329passed,6.44s,exit0 |
| binding-sdkfree |106passed/86skipped,0.95s,exit0; missing Qiskit/four AD frameworks explicit |
| current-frame-example |SDK-free numeric execution exit0; Jacobian -2.349980728882451, HVP -3.916142800105184 |

The incorrect test compared a public query's vector owner to the external
caller's vector after symbolic append(copy=True). The production ownership
policy is intentionally not weakened: the corrected assertion compares to
the actual Circuit-stored parameter vector and still requires exact native
owner identity, element index, type, UUID, equality and distinct query view.
All original red receipts remain retained, not overwritten or hidden.

Compileall for current core and new binding tests exits0. The current larger
main FOCUS adds devices/noise/qchem to core/circuit/compiler/serialization/
information/qml and all four public differential modules. At this edit
session11809 is RUNNING and not claimed green; its eventual terminal state
must be recorded before further runtime edits. No healthy process is stopped.

Still required: public factory JSON-compatible metadata; normalization of
to_gate/to_instruction definition registers; full selective layered decompose
name/label/type and canonical recipe/class differences; further owner/context/
control/annotation lifetime/error boundaries; the R2 example's remaining scalar/
100-wire demonstration additions; final frozen three FULLs/four frameworks/
GLOBAL/original28 matrix and full final audits. Neither current FOCUS nor
earlier3671 results accept these later binding changes or the entire stage.
No staging/commit/push/remote CI, tags/releases, credentials/cloud/hardware,
vendor/package installation or unowned Studio/Router edit occurs. The full
native Qiskit/PennyLane replacement goal remains ACTIVE / INCOMPLETE.

### R2 Latest Terminal Development Results

Session11809 naturally terminates exit0. Its actual receipt is
`/tmp/qb-stage12b-p4u3d2r2-current-main-wide.log/.exit`:
3969passed/3xfailed/13warnings,338.89s. This covers core, circuit, compiler,
serialization, information, qml, devices, noise, qchem and four public
differential modules. It is development FOCUS, not FULL or GLOBAL coverage.
Runtime source remained unchanged throughout this run. The later added bounded
infinite-iterable rejection test was not collected there and passes separately
in `binding-native-final-focus`:34passed,0.53s,exit0, SDK-free.

The expanded SDK-free `examples/native_public_circuit_frames.py` actually runs
exit0 in `expanded-frame-example`. It now asserts inverse/tensor/decompose,
IR/QPY and independent full complex matrices, scalar Unitary->QPY->coherent
control, real100-wire MPS with Gate/dense Statevector/Density/MPS conversions
patched to fail, analytic first/streamed second derivatives and failed inplace
binding atomicity. Its100-wire Jacobian is-2.349980728882451 and HVP
-3.916142800105184. This is local native execution, not a cloud/hardware claim.

SDK-free import-origin checks resolve package/public_circuit/instruction_
parameters to the actual checkout and verify Qiskit/PennyLane are unavailable
and not imported. Current git diff --check exits0; HEAD remainsb443430ec3eb7eac
418c22814e08fe6d940bf099, no staging or commit. Dirty-tree compliance was
actually rerun:1failed/5passed,exit1, solely the pre-existing unowned
quantumbridge/router/core.py source-ledger issue. That is not controlled-clean
acceptance and no provenance was invented to conceal it. All final three
FULL/GLOBAL/original28-matrix/frozen equality requirements and the remaining
R2 factory/metadata/conversion/decompose tasks above are still outstanding.

## R2 Selective Layered Decomposition Development

The completed binding review f4f90768-b36e-4a13-8b87-6b934fbe09f0 was actually
read in full through rendered UI, with all five supplementary sections and
completion controls. It continues the original whole14-section R2 prompt,
does not restart binding work and does not accept the whole stage. The saved
R2 prompt now includes this complete normalized supplement. Priority is
selective layered decompose, then definition conversions, then factory metadata.
Metadata in-memory object rules must not be conflated with portable JSON or
standard-format payload restrictions.

Actual2.4.1/2.6.0 public calls verify name, label, wildcard, class and mixed
selectors plus reps0/1/2. Notably an unselected symbolic owner in the output is
NOT necessarily the source Python object; both public versions copy it. Tests
therefore verify actual classes, parameter/context values, logical identity,
selection/layer depth and input isolation rather than an invented source-owner
identity guarantee.42 additional actual public/native scenarios per version
compare two owner kinds, three repetition counts and seven selectors.

New native tests check28 independent full complex3-wire matrices across
noncontiguous operand2, nested Gate/Instruction layers and phase0.2+0.3+0.1;
real bind->inverse Jacobian/HVP, same-name custom "ry" with actual X definition,
and resource rejection before initial copy. Actual red receipt
`/tmp/qb-stage12b-p4u3d2r2-decompose-reds` is3failed/31passed,exit1: nested
definitions were copied before work admission and selectors were fully
materialized before budget checks. Source gates.py now bounds selector
iteration/list length and preflights the original raw definition graph before
any Circuit copy. It does not change reps1 into recursive basis lowering.

Real terminal development receipts, same prefix with these suffixes:

| Receipt | Actual result |
| --- | --- |
| decompose-recovery |1031passed/1warning,12.87s,exit0 |
| decompose-public241 |157passed,0.84s,exit0 |
| decompose-public260 |157passed,0.85s,exit0 |
| decompose-sdkfree |68passed,0.87s,exit0 |
| decompose-integration |2551passed/3xfailed/11warnings,37.50s,exit0 |
| decompose-frame-example |expanded SDK-free example actually exits0 after current guard changes |

Integration includes core/circuit/compiler/serialization, all four public
differentials and native Gate/noise allocation/configuration ownership tests.
These are FOCUS, not FULL. The earlier3969 broad result predates the new
decomposition guards and is not reused to accept them. Remaining full public
dynamic/annotation/control decomposition and canonical standard recipes stay
explicit rather than being inferred from these selected custom-layer results.
Definition register normalization, public metadata/factory closure and the
original final three FULL/GLOBAL/28-matrix/frozen audits remain outstanding.
No runtime staging/commit/push or remote CI, Studio/Router modification,
token/cloud/hardware, vendor/package, tag/release/history change occurs.
Full independent native SDK replacement remains ACTIVE / INCOMPLETE.

## R2 Definition Conversion And Structural Controlled QPY Development

Completed replye9ff820f-029d-46ac-8aef-debfbecd500f was read in full in actual
UI, all five minimal requirements and completion controls. It continues the
same whole14-section R2, not a new stage or acceptance. It is appended to the
saved R2 prompt. Local register defaults, full parameter maps, wire order,
name/label/phase and illegal Gate versus legal Instruction cases were actually
observed separately in both installed public versions, including0-qubit and
classical-only defaults. Public metadata was also observed, but its full native
in-memory/factory ABI remains separate outstanding work, not an asserted MATCH.

Native conversion now validates raw definition graph/work and bit graph, then
the complete formal map before initial copying. Public outputs install actual
new local default QuantumRegister/ClassicalRegister owners in copied definitions,
not merely renamed aliases. Stored operand indices keep source order, including
noncontiguous maps; original graphs remain unchanged. The parameter-map template
is normalized too, so native IR reload retains further numeric-to-symbolic owner
rebinding. Native QiskitError/CircuitError classes provide public contract names
without importing upstream errors and retain the existing ValueError extension.
The public to_instruction name keyword and to_gate private _name remain native
extensions, not claims of exact complete public method signatures.

New independent complex4-qubit tests use a nested symbolic phase and RY/CX
definition on noncontiguous source/parent wires, open coherent control, binding,
IR/QPY, Operator and analytic Jacobian/HVP. Reset/X/measurement Instruction
conversion executes mapped local q/c operands in all four devices, direct and
native IR. Standard QPY classical custom Instruction headers remain unsupported;
those dynamic tests are not labeled QPY support. Typed identifier conversion
still explicitly rejects rather than deleting scope.

### Actual Public Phase Difference, Not Parity

The initial conversion reds are41failed/72passed. After local graph/error
repairs, first recovery is7failed/170passed. Six failures reveal a real public
version difference, NOT a native failed binding: public2.4.1 to_instruction with
a complete numeric map leaves the symbolic global phase unbound while owner
params become numeric, and PublicOperator raises TypeError for unitary examples.
Actual public2.6.0 correctly binds the phase and executes. to_gate works in both.
The native implementation keeps fully bound executable phase for both targets.

No native oracle, tolerance or failure was removed to imitate that unsafe state.
The differential explicitly records INTENTIONAL_SAFETY_DIFFERENCE for those six
2.4 cases, verifies every other structural field, asserts bound native phase,
and separately proves actual2.4 PublicOperator failure versus independent native
complex math. The same cases are MATCH in2.6.0. This is not full2.4 ABI parity.
Actual final-focus XML properties are:

- 2.4.1:30 conversion MATCH,6 INTENTIONAL_SAFETY_DIFFERENCE, native_result MATCH,
 public_result UPSTREAM_ERROR in the independent dedicated phase example.
- 2.6.0:36 conversion MATCH and both native_result/public_result MATCH.

### Real Structural QPY Repair

The remaining conversion failure exposed unsupported native_controlled in a
custom ControlledGate QPY definition. A raw controlled CX/CZ/Swap now uses real
CCX/CCZ/CSwap standard records for the exact admitted subset. Controlled
RX/RY/RZ/phase with two controls uses a real five-primitive same-axis identity,
restoring the inner control and retaining scalar/nonlinear symbolic angle.
Generated temporary custom Gate params are actual free symbols, not a fake
standard class or a second stored source circuit. Source execution remains the
existing structural engine; neither Gate.to_matrix nor dense export is used.

The bounded helper validates exact descriptor types/keys before equality,
checks aggregate planned work/definitions/instructions and native limits before
constructing the5-op body. A new foreign-equality red caught an intermediate
unsafe metadata comparison, now replaced with exact dictionary/type admission.
The positive25-test module checks actual native/public loads, independent full
complex matrices for three involutions and four rotations with numeric or
nonlinear symbolic angles, forbidden dense export, prior expansion refusal,
foreign callback refusal and valid tight-depth numeric export.

The numeric tight-depth test revealed redundant negative constant AST structure;
constant half angles now resolve natively to finite numeric values, while
symbolic halves retain bounded AST structure. An interim missing local
resolve_parameter import caused10 failures in the r2 reruns; it was fixed, not
hidden or accepted. Original receipts remain retained; no red tests were deleted
or skipped and no tolerance or coverage exclusion was relaxed.

### Actual Conversion Development Receipts

All use `/tmp/qb-stage12b-p4u3d2r2-<suffix>.log/.exit`:

| Suffix | Actual terminal result |
| --- | --- |
| conversion-reds |41failed/72passed,exit1 |
| conversion-first-recovery |7failed/170passed,5.44s,exit1 |
| conversion-r2 |1failed/177passed,5.50s,exit1; remaining structural QPY gap |
| controlled-qpy-reds |18failed/6passed,exit1 |
| controlled-qpy-recovery |202passed,6.06s,exit0; before tight-depth addition |
| qpy-depth-red |1failed,exit1 |
| conversion-integration |1failed/2621passed/3xfailed,39.14s,exit1; numeric depth |
| conversion-alternate |1failed/202passed,7.50s,exit1 |
| conversion-sdkfree |1failed/70passed/27skipped,1.66s,exit1 |
| conversion-integration-r2 |10failed/2612passed/3xfailed,38.81s,exit1; interim import omission |
| conversion-alternate-r2 |10failed/193passed,6.28s,exit1; same omission |
| conversion-sdkfree-r2 |10failed/65passed/23skipped,1.42s,exit1; same omission |
| controlled-qpy-r3 |203passed,6.11s,exit0 |
| conversion-integration-r3 |2622passed/3xfailed/11warnings,39.17s,exit0 |
| conversion-alternate-r3 |203passed,6.51s,exit0 |
| conversion-sdkfree-r3 |71passed/27skipped,1.69s,exit0 |
| conversion-frame-example |expanded SDK-free example actually exits0 on this runtime |

The SDK-free skips are11 actual public loader cases and16 missing four-framework
cases, explicitly unavailable/not executed, not parity passes. Main integration
includes core/circuit/compiler/serialization/four public differential modules
and Gate/noise allocation/configuration ownership. New protocol records and
conversion math pass against actual public2.4.1 and2.6.0 environments. These
are FOCUS; earlier3969/2551 results do not accept the later conversion runtime.
Current native changed modules also pass ruff F821; no linter suppression added.

Remaining original R2 tasks: public metadata visibility/copy/factory semantics
versus portable standard records; remaining generic owner/context/control/
annotation/error API contracts; full canonical definitions/decompose dynamics;
ParameterView concrete ABI; classical custom Instruction QPY and other explicit
unsupported formats; final freeze and all original three FULL/four frameworks/
GLOBAL/28-section matrix/final audits/staged-commit equality. No scoped commit
is claimed from these focused results. No push/CI/tag/release/auth/cloud/token/
hardware/vendor/history change or unowned Studio/Router editing occurred.
Full native Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.

### Next Actually Received Metadata Work

The latest conversion/format results were sent to the same authorized ChatGPT
conversation. Its completed reply87c70a2f-ff3e-47be-ac2f-78e092bac845 was fully
read in actual UI, all five supplementary sections and completed controls.
It continues the original whole R2 prompt, not a new reduced task or acceptance.
The complete normalized supplement is appended to the saved R2 instruction.

Next priority is real separation of public user metadata from execution state,
with both-version reference/deep/shallow/factory observations, no forced JSON
in-memory copy, real JSON standard QPY versus explicit object refusal and typed
IR structural state. Required user-mutation Operator/Jacobian/HVP invariance,
factory/conversion/format loops and typed-scope/foreign-object atomicity must
precede claims of metadata parity. No such runtime separation is claimed yet.
Read-only reconnaissance confirms global_phase/classical_scope are currently
stored in Circuit.metadata and read by core/classical_scope, bind/factories,
compiler layout/scheduling, native IR and QPY/QASM/interchange. Clearing public
metadata to mimic empty dicts would currently drop execution semantics and is
not an acceptable implementation.

All local test/exec sessions for this conversion block have naturally terminated;
staged diff is empty, HEAD unchangedb443430ec3eb7eac418c22814e08fe6d940bf099.
Current compileall and diff-check exit0. Latest dirty compliance remains
1failed/5passed solely unowned router/core.py, not a newly invented provenance
or a claimed clean final gate. No commit/push or final stage acceptance.

## R2 Metadata Domains Development Increment

The preceding reconnaissance is superseded by an actual native implementation,
not a claim of completed R2 or full SDK replacement. The original entire R2
prompt and all its final gates remain required.

### Observed Public Metadata Contracts

Actual installed 2.4.1 and 2.6.0 public calls measured constructor/setter,
dict subclasses, invalid setter atomicity, deep/reference/alias behavior and
13 factories. Constructor/setter preserve the actual mapping reference;
copy/empty/non-inplace compose/bind deep-copy user objects and retain internal
aliases. Inverse/tensor/repeat/power and converted definitions have empty user
metadata; inplace compose preserves the original mapping. Decompose differs:
2.4.1 shares the dictionary; 2.6.0 shallow-copies its outer container. Native
currently follows the 2.4.1 policy. This is an explicit versioned difference,
not complete public ABI parity. The different RY decomposition recipes may
have different explicit phase fields; native tests compare complete complex
operators, not only the phase field or equality up to global phase.

Real XML properties parsed from final focused receipts are 13 MATCH for 2.4.1
and 12 MATCH plus one VERSIONED_SHALLOW_CONTAINER_DIFFERENCE for 2.6.0. The
constructor/setter cases separately compare both actual implementations.

### Actual Native Separation

Public QuantumCircuit retains arbitrary supported Python user dictionaries,
separate from private phase/scope/calibration/compiler execution configuration.
Legacy fluent Circuit metadata remains its original configuration ABI. Real
native intermediate stores inherit the isolated domain without creating a
proxy circuit, second operation/measurement store or parameter graph. Compiler,
bind, compose, decompose, information/device and QNode/Tape paths retain actual
physics when user data changes. Computation borrows only nonsemantic isolated
user data; explicit public copies use their measured memory-copy policy, never
a JSON roundtrip. Managed public copy validates the entire nested graph before
any foreign copy callback, including nested definition user data.

IR has a typed versioned execution record for phase/scope and explicit fields;
old fluent IR remains readable. Parameter AST/UUID, scope and bit graph remain
structural execution records. Formal definition signatures omit only isolated
nonsemantic user data, not physical phase, scope, bits or binding plans.
Standard QPY uses real header phase/register records and JSON user metadata,
including otherwise colliding user keys. No pickle, arbitrary-object decoder
or hidden execution sidecar is added. QPY-decoded internal register descriptors
are no longer exposed as user metadata; the existing register roundtrip test
now checks real qregs/cregs and the actual private configuration. This is an
intentional decoded-metadata ABI correction, not a removed test.

The pre-existing explicitly external artifact API retains its own separate
artifact contract; it is not raw standard QPY. It cannot discard typed scope
as user data. Non-JSON, cyclic or callback-backed transport data explicitly
rejects before output writing; no arbitrary metaclass equality is invoked.

### Real Red-Green And Receipts

New independent tests are test_native_public_metadata_domains.py and
test_qiskit_public_metadata_differential.py. They check user mutation versus
Operator/Jacobian/HVP/frames, copy->decompose->inverse complex phase, bilateral
QPY, typed IR, invalid decode, non-JSON plus input/capture scope, and atomic
callback refusal. Existing conversion/control/format complex-matrix and HVP
tests remain in affected regression. The numerical example now verifies JSON
reserved-key transport and opaque-userdata AD while retaining 100-wire MPS
forbidden-dense execution and analytic gradient/HVP.

All following receipt suffixes are under
`/tmp/qb-stage12b-p4u3d2r2-`, with independent .log/.exit files:

| Suffix | Actual terminal result |
| --- | --- |
| metadata-reds | 31failed/1passed,exit1 |
| metadata-first | 2failed/30passed,exit1 |
| metadata-first-r2 | 13failed/68passed,exit1; typed compiler state missing |
| metadata-first-r3 | 81passed,exit0 |
| metadata-integration | 3failed/2539passed/3xfailed,exit1 |
| metadata-safety | 2failed/87passed,exit1; internal layout copy and a bad copy-policy test |
| metadata-safety-r2 | 1failed/88passed,exit1; test used an unimplemented counter name |
| metadata-safety-r3 | 95passed,exit0 |
| metadata-final-integration | 5failed/2674passed/3xfailed,exit1 |
| metadata-recovery | 60passed,exit0 |
| metadata-final-integration-r2 | 2679passed/3xfailed/11warnings,36.50s,exit0 |
| metadata-nested-copy-red | 1failed,exit1; foreign nested user-copy callback |
| metadata-final-focus | 136passed,0.84s,exit0 |
| metadata-final-integration-r3 | 2681passed/3xfailed/11warnings,37.40s,exit0 |
| metadata-final-focus-r2 | 67passed,0.50s,exit0; after final identity-only type guard |
| metadata-alternate-final | 202passed,2.72s,exit0 |
| metadata-sdkfree-final | 95passed/12skipped,1.85s,exit0 |
| metadata-example | SDK-free numerical example,exit0 |
| metadata-dirty-legal | 1failed/5passed,exit1; only unowned router/core.py |

The five integration regressions were fixed: legacy bind error text, controlled
width-dependent register descriptions, internal external-artifact binding/name
policy, and two legacy Tape ndarray-subclass copy/ownership contracts. No
tolerances, coverage exclusions or actual red tests were removed to pass.
The 12 SDK-free skips are actual missing-Qiskit loader cases, not executed
parity. The larger integration-r3 preceded the last identity-only metaclass
guard; final-focus-r2 and alternate/SDK-free final run after it. None is FULL,
GLOBAL, original28 matrix or final frozen/staged/commit acceptance.

At this checkpoint metadata-main-wide is still healthy and running on the
existing QML/interfaces/transforms/gradient/derivative/device/information/noise/
qchem paths; it started before the final copy/type guards and is not a final
freeze gate. It must be allowed to terminate naturally and its real failures
handled. No healthy test process was killed or restarted. This progress and
the ongoing-test qualification were sent to the same authorized ChatGPT
conversation, requesting the next minimal continuation of the entire R2.

HEAD remains b443430ec3eb7eac418c22814e08fe6d940bf099, no staged changes,
no commit/push/tag/release/vendor/credentials/cloud/hardware/history operation.
Unowned Studio/Router contents are preserved. Full native replacement remains
ACTIVE / INCOMPLETE. Metadata development evidence is not whole-stage acceptance.

The completed ChatGPT reply4de1d5f0-a335-49f6-905b-4e2d137e54c1 has now been
actually read in rendered UI, all five numbered sections and completed controls.
Its entire normalized supplement is saved with the original R2 execution
prompt. It requires the current healthy main-wide to terminate naturally,
repairing actual failures before new generic owner/context lifecycle reds.
The live run has reported failures and continues progressing; no new owner
implementation or freeze acceptance starts ahead of that terminal condition.

### Natural Main-Wide Terminal And Width Recovery

The original main-wide naturally terminated: 2failed/3060passed/1skipped/
2warnings,495.20s,exit1. Both failures are in deferred-measurement tests. One
old fixture directly set num_bits without creating actual Clbits, then Tape
conditional capture silently reduced the inconsistent width via its actual
empty bit collection. The other deliberately oversized a numeric width and
now hits the earlier max_circuit_bits construction guard instead of the later
terminal classical-storage message. Neither outcome is counted as a pass.

Binding and conditional Tape capture now validate the actual bit graph before
copying/capturing, and oversized integer widths refuse before any reconstruction.
Three new negative tests prove invalid widths are not silently trimmed and
source operations/width/bit collections remain unchanged. Positive transform
fixtures now create actual Clbits via add_bits; the excessive-width negative
retains its MemoryError assertion with the specific earlier max_circuit_bits
guard. No limit is raised or exception swallowed. The subsequent focused run
found two additional old width-only control fixtures in basic transforms;
these are migrated to the same real bit API, retaining their cancellation and
shared expansion-budget assertions.

Additional actual receipts:

- metadata-wide-recovery:exit4, a nonexistent requested test path; no tests ran.
- metadata-wide-recovery-r2:2failed/410passed,46.68s,exit1; remaining old basic
  transform fixtures, retained as red evidence.
- metadata-post-wide-integration:2failed/3038passed/3xfailed/11warnings,
  84.34s,exit1; same two already-identified fixture failures, collected before
  their correction.
- metadata-width-fixtures:249passed,7.73s,exit0, after fixture corrections.
- metadata-framework-final:62passed,9.53s,exit0; actual symbolic/second-order/
  second-adjoint framework and mixed-QNode paths on the post-width runtime.

Current post-wide-integration-r2 is running the stable corrected core/circuit/
compiler/serialization/public-differential/resource/transform joint set. These
remain FOCUS and cannot replace the three FULL, independent-framework, GLOBAL,
original28 matrix or staged/commit gates. No generic-owner implementation was
started ahead of resolving these live main-wide failures.

### Stable Post-Repair Joint Terminal

metadata-post-wide-integration-r2 has now naturally completed on the corrected
runtime and fixtures:3040passed/3xfailed/11warnings,83.52s,exit0. It includes
core/circuit/compiler/serialization/five actual public differential modules,
configuration/Gate-noise ownership and all transforms. Final post-width
alternate focus:71passed,0.54s,exit0; post-width SDK-free focus:49passed/
1missing-Qiskit-loader skip,0.33s,exit0. The post-width SDK-free numerical
example exits0. These narrower final focuses supplement, not replace, the
earlier202 alternate and95 SDK-free results. F821 and diff-check remain0.
All test sessions started for this increment are terminal and reaped; no
healthy process was terminated. The earlier495.20s wide remains a real red
receipt, not retroactively relabeled green or treated as final frozen testing.

The entire R2, three final FULLs, independent-framework final acceptance,
GLOBAL/original28 matrix/all examples/controlled legal/origins and source-stage-
commit equality remain pending. Dirty legal still reports the unowned Router
entry, not an owned runtime failure. No files are staged and HEAD is unchanged.
No generic owner/context increment has been implemented in this metadata/width
recovery block; it is the next actual received task.

The terminal/repair report was sent to the same authorized ChatGPT conversation.
Its subsequent completed UI reply has been read in full, confirming the existing
generic owner/context->control/annotation continuation and unchanged final gates.
The summary connector remained cached to the earlier reply; no newer backend
message ID is invented. This confirmation is normalized in the R2 prompt.

## R2 Generic Owner / Control / Annotation Lifecycle Development

The natural main-wide terminal and real width-fixture repairs above preceded
this increment. The entire original R2 prompt remains active. This is not U4,
Studio work, final frozen acceptance or a smaller full-replacement goal.

Actual installed public2.4.1 and2.6.0 probes separately measure64 combinations
of Gate/Instruction/ControlledGate/AnnotatedOperation, numeric/symbolic formals,
copy=True/False and source name/label/params/definition mutation. Source owner,
captured context name/params, current circuit data, parameters and ownership
are checked. Both versions actually return ControlledGate for generic control
with False/None/omitted and AnnotatedOperation for True, notwithstanding the
deprecation warning's future-default wording. Numeric formal maps are explicit;
no original symbolic parameter is guessed from a numeric value. A separate
48-case differential asserts native full complex analytic matrices and actual
public Operator after binding for name/label/params mutations. Six numeric
Instruction cases in2.4.1 retain the observed unbound-phase TypeError as
UPSTREAM_ERROR / INTENTIONAL_SAFETY_DIFFERENCE;2.6.0 executes all48. These
observations are not completion counts, and neither version is inferred from
the other. No upstream implementation/test source is read or copied.

Native execution_operation now restores checked invocation slots for generic
control/annotation owners through the existing Operation store. Circuit queries,
Compiler/Operator/Device/AD and formats read the same effective parameters.
Raw owner/width/work/namespace admission precedes copying. Bounded controlled
base traversal refuses cycles before copy; the actual base parameter view is
authoritative without overwriting captured slots. Annotated inverse factories
own their bases. Explicit data reinsertion intentionally refreshes the captured
frame, including numeric-to-symbolic post-bind source mutation. Generic open
control names retain actual dynamic suffixes; native IR carries an explicit
closed name and validates malformed or inconsistent names/labels. Canonical
legacy open-control records without that new field retain their names/math.

Real standard QPYv13 custom i/a/base/invocation fields now carry supported
classical widths and q/c operands. Defined measurement/reset Instruction
roundtrip preserves noncontiguous classical maps and actual phase, running
with deterministic001 counts on Statevector/Density/MPS/Stabilizer devices.
Reset/measure/defined-nonunitary inverse/control annotations are constructible
and bilateral QPY transportable in both SDK versions. Native IR also retains
their real cargs. They are NOT thereby valid unitary operations: lowering/
resolution refuses them. Conditional, typed-scope, calibration/layout and other
unimplemented format branches remain explicit; no private metadata sidecar.

Additional tests cover independent full complex phase/open-control matrices,
post-bind source mutation/rebinding, direct/IR/QPY Jacobian and streamed HVP,
real Torch/Autograd/JAX/TF second derivatives, modifier order/symbolic power,
owned inverse lifetime, cycle/work/width guards, malformed/renamed controlled
IR and six100-wire controlled/annotation MPS cases with dense Gate/Statevector/
Density/MPS conversions forbidden. The extended SDK-free numerical example
actually asserts the controlled/annotation and classical-device QPY loops.

Actual receipts use prefix /tmp/qb-stage12b-p4u3d2r2-, independent logs/exits:

- owner-reds:96failed/63passed/2warnings,1.60s,exit1.
- owner-first:1failed/158passed/2warnings,3.33s,exit1; base parameter view.
- owner-first-r2:40failed/119passed/2warnings,3.59s,exit1; missing
  parameter_set import caught by F821 and repaired, not relabeled unsupported.
- owner-first-r3:159passed/2warnings,3.28s,exit0.
- owner-integration:2637passed/3xfailed/9warnings,39.79s,exit0; this predates
  the later classical-QPY and lifecycle repairs and is not their acceptance.
- owner-classical-reds:14failed/6passed,0.49s,exit1.
- owner-classical-first:20passed,0.28s,exit0; later native/public splitting
  retains SDK-free execution checks instead of skipping all cases without SDK.
- owner-lifecycle-reds:2failed/105passed,41.77s,exit1; inverse-base alias and
  uncontrolled recursive cycle. Both actual causes were repaired.
- owner-lifecycle-first:205passed/2warnings,42.34s,exit0.
- owner-closed-loops:259passed/2warnings,43.45s,exit0.
- owner-current-integration:exit4, nonexistent tests/config path; no tests ran.
- owner-current-integration-r2:2832passed/3xfailed/13warnings,64.47s,exit0;
  core/circuit/compiler/serialization and six public differential modules.
- owner-main-final:280passed/2warnings,44.51s,exit0; current three new modules.
- owner-alternate:280passed/2warnings,46.53s,exit0; actual2.6.0 environment.
- owner-sdkfree:134passed/26skipped,39.24s,exit0; skips are actual absent
  Qiskit and Torch/Autograd/JAX/TF imports, not native correctness failures.
- owner-example:exit0; SDK-free example, gradient-2.349980728882451,
  HVP-3.916142800105184 plus actual controlled/annotation AD and classical QPY.

These are development FOCUS. The new rename/malformed tests were added after
the broad run collected; current final main/alternate/SDK-free focuses include
them. Runtime did not change between those green runs. The independent JAX/TF
environment focuses are running separately and will be reported by real exit.
F821 is0. Three final FULLs/GLOBAL>=91.34108013033072%/68 exclusions/original28
matrix/all examples/controlled legal/origins/frozen-stage-commit equality remain
pending. No files staged, HEAD unchanged, no push/PR/tag/release/history change,
credentials/cloud/hardware/vendor/package install or Studio/Router edits.
R2 IN_PROGRESS; full independent native Qiskit/PennyLane replacement INCOMPLETE.

### Owner Increment Terminal Framework Receipts

owner-independent-jax:2passed/6 absent-framework skips/126deselected,1.22s,exit0.
owner-independent-tf:2passed/6 absent-framework skips/126deselected,2.87s,exit0.
They execute the installed independent framework, not the unavailable others.
The four interfaces actually execute together in main/alternate owner focuses.
All owner-increment sessions are naturally terminal and reaped. The example's
conditional assignment was simplified without changing its asserted outcomes;
subsequent actual definition-example runs exercise the updated file.

The above results were sent to the authorized ChatGPT conversation. Actual
complete reply aa555dc4-1697-4f37-aab1-0884e9c65b87, including its review and
all seven supplementary sections, was read in Chrome after the initially
interrupted stream. Its R2G label is a continuation inside the original entire
R2, not a new stage or acceptance. The complete supplement is normalized in
the R2 execution prompt. It prioritizes actual definition-mutation mathematics,
copy/factory/transport lifetime and the original final freeze gates.

## R2 Definition-Mutation Mathematics And Copy Admission Development

Actual separate definition-owner241/260 probes cover16 graph/owner/copy cases
with current parameters, source borrowing, direct/bound/inverse full complex
Operator and real errors. Both versions use the replaced defined body for
successful direct/bound execution. Their ControlledGate inverse does not always
invert that actual body: numeric overrides are discarded in favor of the old
base; symbolic inverse can TypeError. Native inverse stays the conjugate
transpose of the actual replaced definition. This is an observable intentional
correctness/safety difference, NOT parity. The32 added public differential
checks explicitly assert28 MATCH and4 controlled-inverse differences per
version; numeric public stale matrices and symbolic TypeError are both observed.

The first96 native changed-definition bind/copy/inverse/handle/IR/QPY cases
found3 real Instruction QPY failures: the to_instruction-derived definition_name
still named its old body after replacement. The setter now validates and owns
the new body before updating the derived name and clearing its obsolete formal
plan. It updates only a tag still equal to its previous native definition name;
unrelated user tags remain, foreign equality is not called, and illegal width
leaves the old definition/tag intact. Native source-definition first then passes
98 cases including the new atomicity and callback tests.

The new definition-mutation module uses eight different structural changes,
each carried through Gate, Instruction and Annotation: replace entire RX body
with RY; replace a nested custom leaf; append X; delete RZ; reverse noncommuting
order; change symbolic phase; compose H; replace a data entry on another wire.
These24 graph/carrier scenarios are not a numeric parameter grid. Independent
analytic Kronecker/complex phase matrices cover72 direct/IR/QPY paths, with
native actual Jacobian/Hessian/streamed HVP. Actual public comparisons also
measure copy=False mutations versus copy=True source isolation,48 per version.
The first reversal fixture mistakenly assigned a context list to a data slice.
Both public versions actually reject it with CircuitError too; it was corrected
to legal whole-data assignment. The native slice ABI was NOT changed to make
the invalid fixture pass. Its15failed/137passed red receipt is retained.

The complete chain now explicitly tests source definition replacement -> owned
copy -> open control with symbolic phase -> ordered inverse/power annotation
-> native IR/QPY -> bind -> full complex Operator -> native Jacobian/Hessian/
HVP. Four actual AD interfaces also compute its second derivative. Two100-wire
IR/QPY MPS versions forbid dense Gate/Statevector/Density/MPS conversion. The
SDK-free example asserts the same numeric chain and a renamed classical
Instruction definition roundtrip on all four native local devices.

Three further real reds found public copy reaching native_configuration_copy
before raw definition graph cycle/width/work admission. Public copy now checks
the actual root bit graph and instruction_definition_work(resolve_frames=False)
before copying. Native definition traversal validates a child circuit's actual
quantum/classical width against its owner. Source cached params remain captured;
this is raw structural admission, not copying or rebinding during preflight.
The3 tripwire tests now pass with high cycle/width work limits and a separate
low work limit, so a width/cycle case cannot pass only by exhausting tiny work.

Actual receipts with the same /tmp/qb-stage12b-p4u3d2r2- prefix:

- definition-owner241 / definition-owner260: each exit0, actual probe logs.
- definition-native-reds:3failed/93passed/134deselected,1.61s,exit1.
- definition-native-first:98passed/134deselected,1.57s,exit0.
- definition-math-reds:15failed/137passed/120deselected,7.76s,exit1;
  all15 are the publicly-invalid reversal fixture, not a native slice defect.
- definition-math-first:152passed/120deselected,8.73s,exit0.
- definition-alternate:152passed/120deselected,8.72s,exit0.
- definition-sdkfree:170passed/182deselected,8.05s,exit0.
- definition-chain-reds:10passed/120deselected,61.87s,exit0; no new chain red.
- definition-current-alternate:540passed/2warnings,120.24s,exit0, before the
  three new copy guards/tests. Not post-guard acceptance.
- definition-current-sdkfree:310passed/78 absent dependency skips,109.17s,
  exit0, also before copy guards/tests.
- definition-copy-reds:3failed/130deselected,0.24s,exit1.
- definition-copy-first:3passed/130deselected,exit0.
- definition-example:exit0, before copy guards; updated numeric assertions real.

The broad definition-joint and post-guard main/alternate/SDK-free, independent
framework and example runs are currently RUNNING; actual terminal receipts will
be appended, not inferred. Broad joint began before the final public-copy guards
and cannot accept those guards even if it passes. No frozen acceptance, staged
or committed equality, remote CI, full SDK, U3/P4 or R2 completion is claimed.

### Definition-Mutation Terminal Receipts And Final Guard Follow-Up

All development processes have now naturally terminated, with actual exit
receipts and reaped sessions. A final adversarial pair found that a controlled
base cycle inside a captured public frame could still reach copy: raw frame
validation skipped its current invocation_params when comparing captured slots.
The graph walker now always admits the actual owner's bounded parameter/base
chain, without equating it to captured slots. This rejects controlled and
annotation-wrapped base cycles before copying while preserving valid changed
source parameters. definition-base-cycle-reds:2failed/133deselected,exit1;
definition-base-cycle-first:5passed/130deselected,exit0 (includes earlier3).

The broader completed runs remain real earlier-version evidence:

- definition-joint:4936passed/3xfailed/13warnings,253.34s,exit0; before the
  public-copy raw admission guards.
- definition-postguards-main:543passed/2warnings,118.14s,exit0.
- definition-postguards-alternate:543passed/2warnings,118.45s,exit0.
- definition-postguards-sdkfree:313passed/78 actual dependency skips,108.14s,
  exit0. These three preceded the final2 controlled-base cycle guards/tests.
- definition-postguards-joint:4939passed/3xfailed/13warnings,253.57s,exit0;
  collected before that final2-case repair, not its final acceptance.

Actual latest runtime results after the final base-chain admission repair:

- definition-final-main-focus:3027passed/15deselected/3xfailed/9warnings,
  96.42s,exit0. This deliberately excludes15 tests matching hundred_wire;
  it is FOCUS, not FULL or a claim that omitted tests executed in main.
  Scope: core/circuit/compiler/serialization/transforms, actual owner differential,
  native configuration ownership and persistent copy protocols.
- definition-final-information-science:1461passed,38.95s,exit0. Actual native
  Information, fixed H2 execution, Aer engine and Gate/noise allocations.
- definition-final-alternate:545passed/2warnings,125.41s,exit0; all four new
  modules, actual Qiskit2.6.0 and all four installed AD frameworks, including
  all new100-wire tests without dense escape.
- definition-final-sdkfree:315passed/78 absent SDK/framework skips,113.38s,
  exit0; native math, HVP/Hessian/format and all100-wire native cases execute.
- definition-final-jax:3passed/9 actual absent-framework skips/355deselected,
  1.83s,exit0. definition-final-tf:3passed/9skipped/355deselected,3.18s,exit0.
- definition-final-example and definition-final-compile:exit0. The SDK-free
  example actually asserts definition replacement/open control/ordered
  annotation/QPY/full Operator/Hessian/HVP, derived Instruction name update,
  four native classical-device execution and the earlier scalar/MPS paths.
- Latest F821 and git diff --check:exit0.
- Current controlled development export legal:6passed,0.39s,exit0;
  source /var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-w28jhzlb/source,
  input tree2b3ec9580ffdbc472322b82d31e3b988742ab1e1, exactly93 owned paths.
  This private-index development export is NOT final FULL/frozen/staged/commit
  acceptance and does not change the real index.
- Fresh dirty-worktree legal:1failed/5passed,0.18s,exit1, solely the already
  unowned quantumbridge/router/core.py missing ledger entry. Its provenance
  is not guessed; the file remains unstaged/unedited by this work.

Actual imported native package/operations/public_circuit/QPY origins are the
working QuantumBridge sources, and public reference versions2.4.1/PL0.44.1
were measured. These current working origins are not frozen import-origin
acceptance. XML parsing confirms the32 replacement Operator/inverse differences
are28 MATCH and4 intentional differences per version (2 numeric stale inverse,
2 symbolic TypeError), not the earlier draft's mistaken24/8 count.

All skips/xfails/deselections stay distinct from passes. None of these FOCUS
receipts substitutes for final three FULL/GLOBAL>=91.34108013033072%/unchanged68
exclusions/original28 matrix/all SDK-free examples/frozen origins/source-stage-
commit equality. Remaining R2 factory/error/metadata/definition-base lifetime
audit still precedes a final freeze decision. HEAD remainsb443430, no real
staging/commit/push/PR/tag/release/history changes, no credentials/cloud/hardware/
vendor/package install or Studio/Router modifications. Full native replacement
remains ACTIVE / INCOMPLETE, not a reduced compatibility-only goal.

The terminal definition-mutation report was sent to the authorized ChatGPT
conversation. Its subsequent actual full UI review and all five Controlled Base /
Namespace / remaining ABI / end-to-end / final-freeze sections were read through
the closing scope and completed reply controls. The initial review-only table
was not accepted as the whole prompt. The subsequent connector read confirms
completed source reply ddc25b6c-6894-49af-ba11-a1651b0bbc0a, matching this
actually read UI reply.
The R2H-labeled supplement is normalized in the original R2 execution prompt;
it does not start a new stage or narrow the replacement goal. Next substantive
work is actual dual-version controlled-base lifetime and namespace atomicity,
then remaining public ParameterView/factory/error/resource audit before freeze.

## R2H Controlled Base / Structural QPY / Native Derivative Continuation

This continues the same original R2 and full independent native replacement
goal. It is development work, not final acceptance. HEAD remains b443430 and
the real index is empty. The owner's latest instruction is to preserve existing
local commits and continue locally: no push or GitHub authorization change.

Actual public2.4.1/2.6.0 calls distinguish external base, exposed owned base,
stored frame and parent definition for symbolic/numeric, copyTrue/False,
replacement/nested mutation, binding, inverse, nested controls and bilateral
QPY. Independent reversed control-block and tensor-projector constructions
agree on full complex matrices, including state01 order and coherent phase.
The control-base probe logs contain explicit public exceptions as observations;
their exit0 is not a claim that every probed action succeeded.

Real new reds and native repairs:
- controlled-base-reds:19failed/81passed/20deselected;17 structural QPY gaps
  and2 previously refused invalidated-history native IR transports.
- invalidated-history-reds:10failed/2passed. Native IR now carries both actual
  edited definition and genuinely stale old formal template with an explicit
  invalidated=true record. Forged markers/signatures refuse. Further ambiguous
  numeric rebind still refuses atomically; no stale plan is activated.
- controlled-qpy-ad-reds:15failed/20passed/140deselected.13 real public-to-native
  records contained MCPhaseGate;2 native controlled gradient paths refused.
  Native dynamic MCPhaseGate/MCXGate import now validates width/params/controls/
  state, aggregate work and native matrix/control bounds before construction.
  It returns native generic ControlledGate, not new public standard subclasses.
- Native structural QPY export supports the measured bounded multi-control
  Pauli-axis/phase rotations and fixed SX/SXdg/X/Y/Z/H via control-parity sums
  and exact elementary conjugations, plus canonical doubly controlled gates.
  Nested descriptors are bounded/validated before copying. Gate.to_matrix is
  forbidden by the positive export tests; no dense or upstream escape is used.
- Native controlled derivatives use zero inactive blocks, native owned matrix
  buffers, bounded descriptor traversal/inverse parity and analytic Pauli
  generators. Controlled Pauli rotations use frequencies1/2 and1, not the
  uncontrolled two-term recipe. Existing adjoint, tangent-over-reverse second
  adjoint, parameter-shift and framework engines remain authoritative.
  Framework shot preflight now counts the actual controlled shift recipe.

Expanded bilateral probes also reconfirm actual upstream defects, not native
functional completions: both versions' own QPY reload of labeled open CCX
raises immutable TypeError; symbolic annotation reload loses Circuit.parameters
despite retaining base expressions. The native import still binds/runs, and
numeric-first annotation return runs, but the failed symbolic/labeled public
return paths are explicitly marked UPSTREAM_DEFECT. These are neither skipped
nor mislabeled MATCH. Original failing probe receipts remain intact.

Namespace checks actually measure both versions' same-name/different-UUID
append/compose/data errors: public circuits can change despite CircuitError.
Native failures retain the complete IR, owner definition, captured params and
formal-plan identity; native safety difference is explicit. Shared vector roots,
partial binding, subsequent base changes and IR/QPY bind to one actual free
parameter. Conflicting repeated formals refuse without state mutation.

Current terminal development receipts, prefix /tmp/qb-stage12b-p4u3d2r2-:
- controlled-qpy-ad-first:35passed/140deselected,2.97s,exit0; first recovery.
- controlled-derivative-regression:164passed,15.09s,exit0; existing gradient,
  second-adjoint/framework and gate-allocation coverage.
- controlled-public260-expanded:300passed,47.76s,exit0; earlier narrower input.
- controlled-expanded-current and controlled-expanded260-current:each442passed/
  3deselected,57.94s/57.81s,exit0. These include actual four-framework first and
  second rules for parameter-shift and adjoint; the3 hundred-wire cases run
  separately. Upstream defect assertions are not supported public transports.
- controlled-sdkfree-current:293passed/149 genuine missing SDK/framework skips/
  3deselected,48.62s,exit0. No dependency installation or fake framework pass.
- controlled-hundred-current:3passed/186deselected,68.55s,exit0. Direct/IR/QPY
  nested open controls execute real100-wire MPS gradient and streamed HVP with
  Gate.to_matrix, Statevector/Density and MPS dense expansion forbidden. Four
  active wires are adjacent to isolate this contract; earlier far-wire routing
  tests remain. An older far-wire stress run is still healthy/pending below.
- controlled-namespace-first and controlled-namespace260:10passed,0.79s/0.83s,
  exit0. controlled-namespace-sdkfree:7passed/3 missing-Qiskit skips,0.67s,exit0.
- controlled-independent-jax:2passed/187deselected,.82s,exit0;
  controlled-independent-tf:2passed/187deselected,2.42s,exit0. Actual separate
  installed framework environments, not additional FULL qualification.
- controlled-sdkfree-example:exit0; executable assertions now cover two-control
  coherent phase, full Operator/IR/QPY, both native derivative engines' Jacobian/
  Hessian/HVP and explicit invalidated-history atomic rebinding refusal.
- controlled-legal-export:6passed,.30s,exit0. Private-index development export
  source /var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-ri_arfoj/source,
  input tree bdb3723a863c3e4fe98c4ce146a7475541960d99,102 exact owned paths.
  It predates this journal append and is not a final freeze or real staging.
- Current F821 and git diff --check:exit0. Real import origins were measured in
  working quantumbridge/__init__.py, serialization/qpy.py and diff/adjoint.py;
  actual reference pairs2.4.1/PL0.44.1 and2.6.0/PL0.42.3. Not frozen origins.

Actually measured remaining public ABI gap: parameter-view241/260 probes exit0
confirm public ParameterView is an independently mutable snapshot with list
slices/copy/remove/data, set algebra and sequence/set equality. Changing the
view does not change the Circuit. Native Circuit.parameters remains a tuple;
the exact public container is NOT implemented by this increment. This is a
remaining gap, not a reason to narrow the full replacement goal or claim ABI
completion. Other ordered/symbolic-power/factory/resource contracts and the
original final freeze audit remain pending.

Still running at this journal update: controlled-expanded-first (older input,
including12 already diagnosed upstream-return test assumption failures and a
healthy slow far-wire QPY MPS case) and controlled-main-broad (current Core/
Circuit/Compiler/Serialization/Gradients/QML/Devices/Noise/DerivativeExecution/
Interfaces development regression). Neither has a fabricated terminal result;
both must be allowed to terminate naturally and their actual exits recorded.
No original three FULL, GLOBAL floor91.34108013033072%, unchanged68 exclusions,
original28 matrix, all examples, frozen-stage-commit equality or final normal
local commit is claimed. No Studio/Router edits, credentials/cloud/hardware,
vendor, installation, tag/release or history rewrite. Full replacement remains
ACTIVE / INCOMPLETE.

## R2H Native Public ParameterView Continuation

Owner's latest direction remains local-only: preserve existing local commits
and continue local work, without push or GitHub authorization changes. HEAD is
still b443430ec3eb7eac418c22814e08fe6d940bf099 on main, ahead51; the real index is
empty. No new commit, push, PR, tag, release or history rewrite occurred.

The prior journal's two pending sessions are now authoritatively INTERRUPTED /
NO TERMINAL RECEIPT, not successful runs: exec handles44074/35172 are missing,
their recorded parent/child PIDs are absent, and neither prefix has an .exit
file. Their partial logs remain intact. They were not relaunched merely on an
observation timeout. A new current broad development regression was started
after actual terminal/missing-handle inspection and substantive native changes.

Actual installed public2.4.1/2.6.0 contract probes agree on independent snapshot
data, local remove/replacement, list slices, sequence/set equality, ordered
duplicate-preserving intersection, reflected operations and copy behavior.
Method copy owns a new list; copy.copy shares the list; deepcopy owns a new
list. Augmented intersection preserves the existing list identity. Generator
consumption and strict-comparison evaluation order are measured, not inferred
from ordinary set algebra. Published IBM QuantumCircuit parameter ordering docs
are also a behavioral reference, not copied implementation or prose.

Independent native core/parameter_view.py now implements these public container
behaviors. Public QuantumCircuit.parameters creates a fresh view over the same
authoritative free-parameter graph; fluent Circuit.parameters remains a tuple.
View mutation cannot change captured invocation slots, owner definitions or
binding plans. to_instruction freezes formal order to a tuple. The parameter
collector bounds aggregate unique identities before sorting/snapshot allocation.
Snapshot construction and one-shot query iteration are bounded; union/xor check
output cardinality before materializing the result set. Managed APIs reject
foreign iteration/equality/hash/index/copy protocols before callback invocation
or mutation. A real negative test found executable metadata-key equality could
run before snapshot construction; public parameter reads now admit the raw
native execution graph before lookup. Opaque user metadata remains separate.

New tests/circuit/test_native_public_parameter_view.py independently exercises
snapshot/order/UUID/vector behavior, public dual-version query/operator/copy
outcomes, native-only algebra and formal plans, raw-key/foreign-callback/size
guards and direct/IR/QPY controlled-phase complex matrices/Jacobian/Hessian/HVP.
IR/QPY decoders still return native Circuit; tests explicitly compose those
results into public QuantumCircuit rather than invent a decoded public class.
The SDK-free numerical example now mutates a parameter snapshot then executes
the existing controlled phase/derivative chain, asserting unchanged execution.

An initial broad regression found the old test still expected the now-supported
two-control RY derivative to refuse. It is strengthened to actual analytic
value/Jacobian/Hessian/HVP under shift and adjoint. Fractional symbolic-power
refusal remains; an actually unknown derivative recipe has an explicit refusal
test at the derivative entry. No supported native behavior is relabeled
Unsupported to conceal a regression. No skip/xfail or numerical tolerance was
added or relaxed.

Development receipts use /tmp/qb-stage12b-p4u3d2r2- prefixes:
- view-contract241/260 and view-mutation241/260:exit0, actual public calls only.
- view-reds:3failed/113deselected; two actual missing-view API errors and one
  overly strong Python-object-is fixture assertion, changed to actual UUID.
- view-first:10failed/106passed; one actual augmented-intersection list identity
  difference and nine fixture assumptions about identity/decoded public class.
- view-second:116passed,2.11s,exit0.
- view-generator-reds:1failed/9passed/123deselected; strict-superset operand
  consumption order. Corrected natively, with bounded one-shot membership.
- view-current:1failed/2827passed/18deselected/3xfailed,88.00s,exit1; old obsolete
  controlled-RY refusal assertion, not a view runtime failure.
- view-aggregate-red and view-raw-key-red:each1failed,exit1; real pre-admission
  construction/callback defects, repaired without raising budgets.
- controlled-old-boundary-repaired:1failed/2passed; the synthetic unknown Gate
  refused earlier for arity, so the recipe refusal is now tested at its real
  derivative entry rather than expecting a different earlier error class.
- view-aggregate-repaired:1failed/213passed,exit1; that invocation omitted
  JAX_ENABLE_X64, producing real float32 accuracy failure. Tolerance unchanged;
  all subsequent framework receipts explicitly use actual x64 execution.
- view-final-main-focus:221passed,9.84s,exit0, before the final raw-key guard.
- view-final260:556passed,135.05s,exit0; view-final-sdkfree:352passed/204 actual
  missing reference-SDK/framework skips,111.17s,exit0. Both include all3 current
  hundred-wire nested-control tests, and predate only final raw-key admission
  and the last added focused snapshot/derivative tests.
- view-postguard-main:3335passed/18deselected/3xfailed/7warnings,139.10s,exit0;
  Core/Circuit/Serialization/Compiler/Transforms development FOCUS, not FULL.
- view-postguard260:222passed,10.42s,exit0; view-postguard-sdkfree:117passed/
  105 actual missing reference-SDK/framework skips,5.37s,exit0. Latest complete
  view plus annotation test modules after raw-key guard.
- view-independent-jax:2passed/187deselected,.89s,exit0;
  view-independent-tf:2passed/187deselected,3.13s,exit0, actual separate installs.
- view-postguard-example:exit0, actual SDK-free assertions including no-dense
  hundred-wire MPS and snapshot mutation, not merely printed capability flags.
- Current working imports resolve to this repo's quantumbridge/__init__.py and
  core/parameter_view.py; actual main reference versions2.4.1/PL0.44.1.
  These are working origins, not frozen/full-qualification origins.
- Current F821 and git diff --check:exit0. Final development legal export and
  remaining live test results are recorded in the completion addendum below.

At this journal append view-main-broad is live (healthy CPU/progress, current
Core/Circuit/Compiler/Serialization/Gradients/QML/Devices/Noise/DerivativeExecution/
Interfaces input, started before final raw-key guard); view-postguard-hundred
is live on the final runtime. Neither is claimed terminal here. No FULL/GLOBAL
floor91.34108013033072%/unchanged68 exclusions/original28 matrix/all examples/
final freeze-stage-commit equality or final commit acceptance is claimed.
Snapshot container completion does not establish all Parameter/ParameterVector
representations, all factories/canonical recipes, every QPY/QASM scope/timing
path or full Qiskit/PennyLane replacement. No SDK source/test copying, vendor,
installation, credentials, cloud/hardware or Studio/Router changes occurred.

Coordination: read_thread confirms completed source reply
afa2c582-8856-42ee-a2dd-223dcbeea1c0, but its message is only a content-reference
placeholder. The available browser session is not logged in and cannot display
that private reply. Its unseen text is NOT treated as a received execution
prompt. The prior fully read R2H/original14-section R2 remains authoritative;
the owner was asynchronously asked for the new reply text. Local native work
continues without changing authorization. Full replacement ACTIVE / INCOMPLETE.

### ParameterView Terminal Development Addendum

All new test/example/diagnostic sessions in this increment have naturally
terminated and been reaped; no healthy process was killed. The two earlier
missing sessions remain interrupted with partial logs, not retroactive greens.

- view-main-broad:4419passed/1skipped/3xfailed/9warnings,677.91s,exit0. It is
  broad development input before the final raw-key guard, NOT final frozen
  FULL. The one skip's reason was not printed by this -q invocation and is
  not attributed to a missing dependency without evidence.
- view-postguard-main:3335passed/18hundred-wire deselected/3xfailed,139.10s,
  exit0, after the final raw-key guard. See the exact scope above.
- view-postguard-hundred:3passed/186deselected,67.52s,exit0, on final runtime:
  actual100-wire direct/IR/QPY nested controls, gradient/streamed HVP and dense
  conversion tripwires. Adjacent active wires isolate this specific contract.
- view-postguard260 and view-postguard-sdkfree remain222passed and117passed/
  105genuine missing SDK/framework skips, respectively, exit0. Their tests
  include the last added view->IR/QPY->native Jacobian/Hessian/HVP chains.
- view-controlled-legal:4passed,.28s,exit0; adding the unchanged no-vendor/
  no-token tests gives view-controlled-legal-no-vendor:6passed,.13s,exit0.
  Exact105-owned-path private-index development export source:
  /var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-ktnd8nol/source
  input tree f26b0431bbddf625013036aceb3b379f6cd7d794;
  production33f03499de1b81cfb3f6645e271bf6955af8940c;
  tests e06abab8600a6d206a63e032809197d13226dc5c;
  examples387e6f4b061138bb597b7fe11f9e9ec356b0cd95.
  The export predates only this documentation addendum; it is not a final
  acceptance freeze or real Git staging. Existing unrelated Router/Studio
  work is excluded without inventing provenance or reverting those files.
- Scoped compileall, F821 and git diff --check:exit0; real index still empty,
  HEAD unchanged. No current GLOBAL/three FULL/original28matrix or final scoped
  commit is claimed. Further original R2 audits and full SDK work remain.

## Actually Received R2J And Native Vector Namespace Continuation

The owner's existing default Chrome session is authenticated. The earlier
automation browser targeted a different Chrome instance; that was not evidence
the owner needed to log in. Native accessibility selected the already-open
"Claude 代码泄漏与应对" tab in the actual default Chrome process, verified the
authorized conversation URL, and read the full completed c4e3d637-b21d-49cb-
b534-0956a3641791 reply including all0-10 sections. No new tab, login request,
authorization/automation-setting change or private ChatGPT endpoint was used.
The actually received R2J supplement is preserved in the existing R2 execution
prompt. This is the same original14-section R2 work, not a new stage or U4.

R2J prioritizes actual scalar/vector identity, snapshot/execution agreement and
cached owner/frame lifecycle before final readiness. The current increment
does not claim complete factories, all symbolic representations, every format
scope/timing path or full replacement. Owner's local-only Git direction remains
in force: main HEAD b443430ec3eb7eac418c22814e08fe6d940bf099, ahead51, no new
commit/push/PR/fetch/OAuth/tag/release/history rewrite.

Actual public2.4.1/2.6.0 namespace-contract241/260 probes exit0. Same name+UUID
identity/hash and scalar-vs-vector inequality already agree and are preserved.
Both public versions expose list params/list slices/read-only names and accept
empty vector names and native integral indexes. Public2.4 list pop changes
vector length;2.6 list pop leaves its cached length stale. Native now uses one
coherent live list: this is MATCH for2.4 and INTENTIONAL_SAFETY_DIFFERENCE for
the measured2.6 cache divergence, not a falsely reported full match. Negative
lengths refuse with OverflowError, not2.4's slice semantics. Public scalar
empty names/UUID object/representation differences remain unfinished.

Independent native parameters.py now provides read-only vector name, live
params/list slices, stable element UUID/root/index across shrink/regrowth,
native integral inputs and staged atomic growth. Gate and symbolic vector
limits check before creating the first element; failed growth leaves all
borrowed list aliases and old identities unchanged. Managed scalar/vector
intake rejects foreign truth/index/equality/hash/iteration before callbacks.
QPY allows empty vector names in ordinary standard vector fields, without
sidecars. Existing parameter equality, formal identity and derivative engines
are retained. README, notices, migration ledger and SDK-free example are updated.

Independent vector tests assert old ParameterView stability/new authoritative
free parameters after in-place partial binding, vector/list mutation and source
definition replacement. Direct/IR/QPY vector->nested Generic->two open controls
->inverse+power annotation->snapshot->partial/full binding is checked against
full complex Operators and analytic Jacobian/Hessian/HVP under shift/adjoint.
The IR/QPY chain now additionally executes real Torch/Autograd/JAX/TensorFlow
graphs, including second and directional derivatives under both methods.
Bilateral actual public QPY vector tests bind/execute and retain the used
element UUID/root/index. Public warns that unused element0 identity is not
restored; that unused object identity is not claimed.

Power-contract241/260 public exploratory probes also exit0, each with72 actual
numeric comparisons. They expose an unfinished noninteger Operator.power and
branch-cut/options ABI gap, and symbolic-annotation cases. No power rewrite,
SciPy dependency or new fractional-symbolic claim was added in this increment;
R2J namespace/lifecycle priority remains authoritative.

Development receipt prefix /tmp/qb-stage12b-p4u3d2r2-:
- vector-reds:18failed/8passed,10.30s,exit1; real list/slice/name/admission/
  empty-name gaps, with tripwires preventing huge allocations.
- vector-first:26passed,10.12s,exit0; before the final5 native tests and16
  additional framework graph tests. No skip/xfail/tolerance relaxation.
- vector-main-regression:3361passed/18hundred-wire deselected/3xfailed/
  7warnings,147.47s,exit0; Core/Circuit/Serialization/Compiler/Transforms
  development FOCUS on the current production runtime, not original FULL.
- vector-current and vector260-current:173passed each,14.49s/14.51s,exit0;
  vector+ParameterView modules before only the final framework tests.
- vector-sdkfree-current:68passed/105genuine missing Qiskit reference skips,
  14.19s,exit0. Actual native math/IR/QPY/first/second chains ran without SDKs.
- vector-framework-main:47passed/1 unused-vector identity warning,66.92s,exit0;
  latest full vector module including16 actual four-framework graph tests.
- vector-framework-sdkfree:68passed/121 genuine missing SDK/framework skips,
  14.78s,exit0; latest vector+ParameterView. The16 added skips are only the
  four absent optional frameworks, not SDK-free native execution failures.
- vector-sdkfree-example:exit0; actual assertion-based native execution,
  vector list/identity/snapshot, matrix/derivatives and existing100-wire no-dense
  MPS chain. No capability flag or log line is substituted for execution.

At this append vector-framework260, vector-shared-regression (Information/
Gradients/QML/Devices/Noise plus fixed H2/device API/independent math and symbolic
four-framework tests), and separate JAX/TF vector-graph sessions are pending
terminal receipt collection. Their results and exact controlled107-owned-path
legal export are recorded only after actual terminal exits below. No latest
original three FULL, GLOBAL floor91.34108013033072%, unchanged68 exclusions,
original28 matrix, all examples, final freeze-stage-commit equality or final
local commit is claimed. No Studio/Router/credentials/cloud/hardware/vendor/
installation work. Full independent Qiskit+PennyLane replacement ACTIVE/INCOMPLETE.

### Vector Terminal Development Receipts

- vector-framework260:189passed,75.05s,exit0, latest complete vector+
  ParameterView modules, including16 actual four-framework first/second/HVP
  graph tests on public Qiskit2.6.0 reference environment.
- vector-independent-jax:4passed/43deselected,19.96s,exit0;
  vector-independent-tf:4passed/43deselected,21.71s,exit0. Separate installed
  environments actually executed both IR/QPY and shift/adjoint graph chains.
- vector-controlled-legal:6passed,.30s,exit0, tests/legal plus unchanged
  no-vendor/no-token checks on the exact107-owned-path private-index export:
  /var/folders/c1/gs7_18954qx7td5_t_lnmf4c0000gn/T/qb-stage12b-p4t-foundation-8_knvl_w/source
  input tree1c4c06d460be6a365c6187303589f0c74fc3141d;
  production fed12fe79621690bd39381ec2383fc2bca7b6af1;
  tests1ddc35ba59281dbbfb8ebda7adaacb8fb8e4a86f;
  examples a460362c2a72368e7aff83b9c25bf90fce6b685a.
  This is a development export, not final acceptance/staging/commit; subsequent
  edits are documentation receipts only. Protected unrelated Studio/Router
  changes are excluded from the export without being reverted.
- Scoped compileall/F821/git diff --check exit0. Real index empty, HEAD
  unchanged. Only vector-shared-regression remains live at this addendum;
  its actual terminal result must be appended, not inferred from progress.

- vector-shared-regression has now naturally finished and been reaped:
  1734passed/2warnings,330.03s,exit0. Exact scope was Information, Gradients,
  QML, Devices, Noise; fixed-H2 execution, device derivative API, independent
  derivative math, and symbolic four-framework interfaces. This is current
  broad development evidence, NOT original frozen FULL/GLOBAL/matrix coverage.
  No new test/example session remains running in this increment.
- The above actual development report and explicit remaining gaps were sent to
  the owner-authorized ChatGPT conversation "Claude 代码泄漏与应对". The shared
  regression was still RUNNING when that report was sent, and has only now
  acquired its terminal green receipt; it was not prematurely counted as green.

The completed next reply fe25098c-38be-4fd0-ad5b-7817a36fb93d was fully read in
the same verified default-Chrome tab (review plus execution sections0-10), not
inferred from its content-reference placeholder. Actually Received R2K is
preserved in the existing execution prompt. Its first condition, letting the
shared regression acquire a natural terminal, is now met. Next priority is
actual dual-public Operator.power/options/branch-cut reds, then reliable native
complex matrix functions/resource boundaries, remaining parameter/factory ABI
and original frozen gates. The exploratory Gate/Annotation power probes are
not substitutes for that Operator contract and no noninteger Operator runtime
implementation or full R2 acceptance is claimed in this increment.

## R2K Operator Power Development And Owner UI Redirect

The preceding goal turn made authoritative progress: vector runtime changes,
actual reference calls and terminal regressions. Current HEAD remains b443430,
with no new staging/commit/push. R2K Operator work began only after the1734-test
shared regression had naturally terminated.

New public Operator-specific probes operator-contract241/260 each exit0:
actual signature/options, integer/fractional/NumPy scalars, branch winding,
singular/nonnormal matrices, dimensions and aliasing. These are separate from
the prior72 Gate/Annotation observations per version. Native reds were
152failed/33passed,1.16s. New native information/matrix_functions.py implements
bounded unitary eigenvector Schur deflation (no inverse eigenvector basis),
triangular square-root scaling, an absolutely convergent binomial expansion,
stable diagonal/first-superdiagonal corrections, integer squaring, complex
branches and separated semisimple-zero blocks. No SDK or SciPy execution or
dependency installation. Arrays reuse the existing ownership and ledger APIs;
preflight covers explicit destinations and a conservative LAPACK policy
envelope, while hidden vendor allocator/RSS remains explicitly unavailable.
Operator.power now revalidates actual numeric shape/subsystem domains and
accepts public exponent/cut/assumption options with strict native intake.

Actual first development result operator-first:37failed/219passed,.76s,exit1.
Near-coincident complex log1p lost scalar precision; replaced independently
with stable real log1p/atan2 and expm1/sine identities. The oracle uses a
separate local derivative series. Dense near-cut fixture similarity rounding
was being amplified by reciprocal spectral separation; near-cut tests now use
exact diagonal buffers, dense tests use separated spectra. Tolerances were
not relaxed. operator-second:280passed,.63s,exit0. Expanded tests add large
integer parity (no float exponent conversion), scalar/strided owner isolation,
analytic dense Jordan6/8,20 actual public/random nonnormal similarities,
near-zero limits, exact output storage and fault cleanup.

Additional actual nearly-normal Jordan reds:2failed/1passed,exit1. A small
commutator alone cannot justify dropping offdiagonal entries. Repaired by
retaining the full triangular matrix function, even for numerically normal
matrices, and checking both the commutator and Schur offdiagonal for an explicit
assume_unitary=True. Current operator-nearnormal-repaired:340passed,.77s,exit0,
including71 existing Operator-copy/resource tests. operator-expanded before
those last3 tests:337passed,.69s,exit0. All these are DEVELOPMENT FOCUS, not FULL or
final R2 acceptance. All numerical test sessions have terminated and been
reaped; no healthy test was stopped.

Current numerical limits remain explicit: unresolved near-zero eigenvalues,
undefined singular Jordan fractional roots, negative singular powers,
unreliable branch-root denominators, nonconvergence/overflow and logical work/
dimension budgets refuse. This is not a proof of every ill-conditioned matrix
function domain, every factory/ABI, final original frozen gates or full SDK
replacement. Further broad/current dual-version/SDK-free/100-wire regression,
native math documentation/legal and remaining R2 gates still need completion.

The owner explicitly redirected work to the four-domain/nineteen-direction
project framework UI. New local studio/framework.html and src/framework/
present the original4/5/5/5 taxonomy, bilingual details, foundation and reference
views, search/filter/export, and target-only labels. This UI increment is
owner-requested and separate from the native R2 scoped export/final freeze;
it does not declare industry implementation complete. Existing Studio work is
preserved; only its sidebar gains the new framework link. Native work remains
unfinished and full replacement ACTIVE/INCOMPLETE; no tag/release/auth/cloud/
hardware/vendor/new installed dependency or remote action is authorized.

### Owner-Requested Framework Preview Verification

Local preview: http://127.0.0.1:8765/framework.html?lang=zh, served by the
existing Studio Node server in its retained preview session. Native accessibility
confirms the owner's actual default Chrome process2383 shows the new framework
URL/title, not a different automation profile. No login or authorization action.
Existing Studio smoke and new framework-check pass: science4/finance5/industry5/
security5,19 unique bilingual directions and5 shared-foundation layers.

Actual Playwright interaction checks: finance filter5; details/3 capabilities/
next-direction/Escape; search VaR1; empty-state/clear restoring19; foundation5;
comparison19; English19; both languages at320/390/768/1024/1500px show19 cards,
no horizontal document overflow or clipped direction/nav/title text. Mobile
dialog fits375px content width without clipping. Exported actual downloaded
JSON has4 domains/19 directions and explicit target-only scope. A real
same-document hash navigation initially failed to open details; repaired with
hashchange handling and verified QRNG deep link. Overview tab now restores all19
after a mobile category filter; bilingual search biology finds biomedicine.
Keyboard ArrowRight switches tabs. Console errors/warnings0 on final page.
Desktop/mobile/detail screenshots are generated under .playwright-mcp, not
native acceptance artifacts. Lucide is a pinned SRI-checked external icon
asset, not vendored SDK source; no new package was installed. The preview
server remains running intentionally for the owner to inspect the page.

## R2M Controlled Power And Public Factory Development

Status: ACTIVE / INCOMPLETE; original R2 and full independent replacement
scope remain intact. Main HEAD remains b443430. No staging, commit, push,
OAuth, tag, release, dependency installation or new hardware task occurred.
The owner-requested home navigation change is separate and already verified;
this increment returns to the core callable API, not additional UI work.

### Actual Remaining API Difference Matrix

Classifications below apply to the observed scenarios, not every overload or
the whole named API. Existing tests are evidence of their explicit assertions
only. The received R2M scope remains in
`stage12_b_next_public_api_closure_received_prompt.md`.

| Surface / observed scenario | Classification / evidence |
| --- | --- |
| Public copy / copy_empty_like / inverse / repeat / power / tensor bit graph, scalar phase and return class | IMPLEMENTED_AND_TESTED for existing `test_native_public_factories.py`, zero-width and metadata test scenarios; not a complete arbitrary-subclass/variable-scope certificate |
| compose / assign_parameters stored frame, inplace / atomicity | Existing public binding, lifecycle and metadata differential suites; unsupported typed/runtime-input cases and public unsafe mutation remain separately tracked |
| decompose matrix primitive then QPY | NATIVE_BUG repaired: factory now owns a real UnitaryGate instead of an opaque generic Gate with a raw matrix body; width0/1/2 and alias/phase roundtrips tested |
| decompose arbitrary unitary synthesis recipe / exact public layer structure | UNSUPPORTED / ABI_DIFFERENCE remains: retaining an executable matrix object is not complete physical-basis synthesis parity |
| to_gate / to_instruction local formals, registers, nonunitary boundaries | Existing definition-factory and serialization tests; ordinary Instruction control/power are native extensions, not missing public APIs |
| Circuit.data / CircuitInstruction replace, copy and captured fields | Existing public frame/factory and context-lifecycle differential suites; single authoritative store retained |
| InstructionSet broadcast / inverse / stale slots | Existing handle/resource and public-context differential suites; no new proxy operation list |
| ParameterView snapshots / sets / copy | Existing public view tests; known public2.6 stale-length discrepancy remains intentional safety difference |
| ParameterVector shrink / regrow / owner / scalar-vs-vector identity | Actual2.4.1/2.6.0 probes retain equal logical regrown identity and a new wrapper, matching current native observation; existing namespace/QPY tests retained |
| Parameter repr / UUID Python type | ABI_DIFFERENCE still open: actual native `Parameter('angle')` / str versus both public versions `Parameter(angle)` / UUID; UUID text and reconstructed equality match |
| CRX / CRY / CRZ numeric and annotated power | NATIVE_BUG repaired, then IMPLEMENTED_AND_TESTED: public return class, label/mutability, full coherent matrix, closed/open control, scalar/integer/fractional powers |
| Fixed self-inverse / UnitaryGate.inverse annotation flag | ABI_DIFFERENCE repaired: actual public specialized class and unlabelled immutable fixed result retained; Unit inverse remains UnitaryGate even when annotated=True |
| CPhaseGate open-control power | OBSERVED_UPSTREAM_DEFECT in actual2.4.1 and2.6.0: public power switches control0 to1. Native retains the correct open block; explicitly not MATCH or bug-for-bug parity |
| General multi-control dedicated classes / flattened names and control hierarchy | UNSUPPORTED / ABI_DIFFERENCE remains: public MCPhaseGate / MCXGate and flattened controlled naming are not all native dedicated-class matches |
| Symbolic fractional-power QNode compilation | UNSUPPORTED: deferred object binds and executes correctly, but unbound QNode compilation still attempts matrix-power resolution too early; directly observed for parameter-shift and adjoint |

### Independent Reds And Fixes

Initial new native suite:171failed/9passed,2.16s. These include object-protocol
and return-type failures, not171 distinct mathematical bugs. A separate actual
numeric probe, after explicit Qiskit/native wire-order conversion, found
theta7.3 half-power errors about1.9357 for CRX/CRY and2.0 for CRZ. Integer powers
were numerically correct but exposed the wrong specialized return class.

The old implementation scaled controlled rotation angles for every exponent;
this is not the principal matrix function when eigenphases wrap. The repair
routes numeric controlled rotations through the existing generic Gate path,
which now reuses native Operator.power with explicit zero branch rotation and
normality validation. It removes the separate inverse-eigenvector fractional
shortcut and allows the existing managed native accounting contract. CPhase
retains its distinct specialized angle-scaling API and its correct control
state. Unbound direct controlled powers now raise the observed TypeError;
annotated=True creates a real deferred object whose parameters can be bound.

After those fixes:12failed/168passed. Six QPY failures exposed the actual public
factory's opaque matrix wrapper; promoted canonical unitary primitives to real
owned UnitaryGate objects. Six metadata assertions were a test-fixture error:
actual public inverse metadata is empty, already correctly implemented. Tests
now require restored metadata to equal the resulting inverse metadata and
separately assert the source metadata remains unchanged; no production
metadata contract or numerical tolerance was weakened. Then180passed,1.85s.

Ten additional checks cover the explicit legal Operator→power→UnitaryGate→
public Circuit→Statevector/Density chain, nonunitary wrapping rejection and
zero/one/two-width unitary factory/QPY promotion. New final native suite has
190 cases. Alias membership, symbolic phase, source isolation, source-owner
immutability, managed output-view leases and memory/dimension/work preflight
are actually asserted. All mathematical oracles use independent projectors,
scalar complex phases or a known Fourier diagonalization, not Qiskit output.

### Terminal Development Evidence

| Scope | Actual result |
| --- | --- |
| Main2.4.1 initial actual public differential | 164passed,1.73s;144 matching controlled powers,6 symbolic error/bind cases,6 deliberately non-matching public open-phase defects,6 fixed inverses,2 unitary inverses |
| Alternate2.6.0 latest native + actual differential | 354passed,3.84s; XML record_property compatibility warnings only |
| SDK-free latest native suite | 190passed,2.01s; no public-reference skips or xfails in this suite |
| Main2.4.1 latest native + actual differential | 354passed,3.88s; xunit1 receipt preserves scenario classifications |
| Main Core/Circuit/Information/Serialization + selected public differentials | 5356passed/3existing xfailed,337.72s; no failures; not a repository FULL |
| SDK-free matrix/state/density example | 6cases; maximum complex error1.5700924586837752e-16; exit0 |
| SDK-free public-frame example | actual controlled/annotation IR/QPY, first/second derivatives and100-wire no-dense MPS all asserted, exit0 |
| Repository attribution tests | 1failed/5passed; unrelated pre-existing untracked `quantumbridge/router/core.py` is missing from the ledger; not a legal acceptance pass |
| Main Compiler/Gradients/QML/Devices/Noise/Interfaces | 727passed/1skipped/2existing warnings,332.96s; natural exit0 |
| Scoped attribution / F821 / diff check | required notice/license checks and all five implementation/test ledger paths pass / pass / pass; not the final controlled export audit |

The broad Main Core/Circuit/Information/Serialization and selected public
differential run completed with JAX_ENABLE_X64=True and explicit BLAS/OpenMP
single-thread settings. It collected the180-case version before the ten newest
test-only additions; the latest354-case focus was rerun separately. The further
Main Compiler/Gradients/QML/Devices/Noise/Interfaces run naturally terminated
with exit0. Its sole skip is the existing missing-JAX-installation contract,
which does not apply because JAX is installed in this runtime; not a new
unsupported-function skip. The repository-wide attribution failure
is not hidden: Router was already untracked/dirty at this increment's start
and is not modified or retroactively attributed without an actual source
audit. Controlled candidate legal/origins gates remain required. This batch's
native files and independent tests are explicitly recorded in the ledger.
These are development checks, not the three frozen FULLs, explicit GLOBAL,
independent AD FOCUS gates or original unmodified28-section local matrix.
Original final gate requirements and staged/committed equality remain NOT_RUN.

The completed next ChatGPT reply was actually read in the already authorized
default-Chrome conversation, not inferred from a content-reference placeholder.
It is archived as `stage12_b_symbolic_fractional_power_received_prompt.md`.
R2N continues the whole original R2: highest priority is a real symbolic
fractional-power QNode compile/bind/execute plus mathematically valid first/
second derivative chain, not cosmetic repr or generic multi-control naming.
Known branch-stable derivative rules must not be replaced with unlabelled
finite differences or unconditional angle scaling; unresolved generators and
branch switches need explicit Unsupported/numerical refusal. The remaining
factory/ABI, formats/resources and original frozen gates still apply. No new
R2N production repair or completed final frozen acceptance is claimed here.

## R2N Symbolic Principal Power Development Increment

2026-10-23: the full independent Qiskit/PennyLane replacement objective remains
ACTIVE/INCOMPLETE. The preceding R2M checkpoint is historical; native R2N
progress begins here. The intervening owner-authorized fourteen local
application notebooks are not counted as native SDK completion. Main HEAD
remains `b443430`; no stage, commit, fetch, push, release, tag, auth change,
cloud task, dependency installation or vendor operation occurred.

### Reproduced Failure And Native Repair

An actual `QNode.from_circuit` call with symbolic
`CRYGate(p).power(.5, annotated=True)` failed in
`record_compiled_parameters -> Circuit.lowered -> resolve_annotated_operation`:
the unbound controlled gate was asked to produce its fractional matrix before
the classical input had been recorded. The formal independent suite initially
reported 38 failed / 1 passed. One initial zero-width test used an invalid
fluent constructor keyword; it was corrected to the existing global_phase
property before the retained red run, which still reported 38 failed / 1 passed.
The one passing scenario was the pre-existing precise refusal for an unknown
noncommuting family, not a successfully executed power.

The structural lowerer now accepts a private annotation resolver used only by
QNode parameter recording. Original circuit/QPY/IR data stays symbolic. Native
fixed-projector spectral phases retain first/second classical traces, including
variable exponent and angle mixed derivatives. Existing native phase gates,
Clifford basis changes and coherent controls implement the actual full complex
operator. Existing shift / adjoint engines compute quantum derivatives; no
finite-difference fallback or unconditional controlled-angle scaling was added.
Inverse/control order, open states, scalar zero-width phase, true global phase,
UUID binding and primitive basis compilation are checked. Ordinary inverse,
control and integer-only annotations retain their existing lowering path.
Edited standard definitions are not assumed to retain their class formula.

The derivative construction is valid for constant eigenprojectors. It does not
use `a*U**(a-1)*U'` for general noncommuting matrix families. Those moving-
projector families still raise precise Unsupported and need a genuine general
Frechet implementation; they are not counted as implemented. Branch switches
are explicitly rejected; points 1e-6 away on either side execute correctly.
The 100-wire MPS example acts only on its two-wire local gate and never requests
a complete state or global operator matrix.

### Large Angle Red And Correction

Additional independent tests at angles `1e6+.37` and `1e12+.37` exposed phase
reduction/cancellation errors around 2.32e-11 and 5.74e-7 in the measured value.
The final rule uses `atan2(sin(phase), cos(phase))`, matching the complex scalar
argument, and preserves the primal without subtracting two large rounded
numbers. Native Dual/SecondDual carry exact unit/zero local derivatives;
Torch/Autograd retain the same identity derivative graph; JAX/TF use guarded
trigonometric phase graphs. Test tolerances were not loosened.

### Current Evidence And Remaining Work

- SDK-free symbolic compile/matrix/derivative/format/compiler/resource suite:
  61 passed before the two additional large-angle cases.
- Actual Main native and four-framework second-order focus after the numerical
  correction: 79 passed in 9.67s (63 native plus 16 Torch/Autograd/JAX/TF tests).
- Previous Main Core/Circuit/Information/Serialization plus public controlled-
  power differential: 5047 passed / 3 existing xfailed / 8 warnings, natural
  exit0, 334.15s. This was before the large-angle correction, not frozen-final
  evidence for that correction.
- Earlier SDK-free native+controlled-power+annotation+annotation-format focus:
  378 passed / 35 optional public-reference skips, exit0, 7.40s; not FULL.
- Main Gradients/Interfaces/Compiler/QML/Devices/Noise naturally terminated as
  session90045: 806 passed / 1 environment-contract skip / 2 existing warnings,
  exit0, 339.01s. This predates the following tensor-frame extension and is not
  frozen-final evidence for that extension.

### Tensor Frame Extension And Final Focus

Six subsequent reds exposed an unsupported real call: a generic Gate containing
commuting RX/RZ rotations on disjoint/permuted wires plus global phase. The
native rule now embeds compatible local projector frames at their actual wire
positions, sums the spectral phases and takes the power of the combined
operator, not the product of separately principal-powered factors. Complete
complex matrices and independent analytic first/second projector derivatives
verify all six scenarios. This is a tensor-product common-frame extension,
not a claim that every commuting or noncommuting family is implemented.
Projector phases remain local to the invocation rather than being extracted
as a global phase; zero-width scalars retain their true global phase. A single
per-recording work counter now accumulates spectrum/embedding/output work
across annotations; large tensor expansion is refused before visiting any
primitive. Existing dimension and retained-storage guards remain active.

One added QPY test incorrectly expected a symbolic modifier exponent to fit
QPY v13. Actual Main Qiskit qpy.dump(version=13) raises struct.error for this
input; the native writer already correctly refuses its float64-only modifier
field. No serializer or runtime was changed for that fixture. Positive QPY
tests retain a symbolic gate angle and numeric exponent; IR additionally
retains a symbolic exponent. An explicit non-lossy v13 refusal test replaces
the invalid expectation. The failed intermediate focuses (441passed/1failed
Alternate;861passed/1failed Main;71passed/1failed SDK-free) are preserved here
as test-domain errors, not falsely reported as production repairs.

Final current-runtime development results:

| Scope | Actual terminal result |
| --- | --- |
| Main new native + four-framework + existing controlled/public powers + Operator/Jordan families | 863 passed,14.22s,exit0 |
| Alternate new native + four-framework + existing controlled/public powers | 443 passed,12.82s,exit0 |
| SDK-free new native symbolic suite | 73 passed,4.58s,exit0; no skip/xfail |
| New independent framework cases | 16 actual Torch/Autograd/JAX/TF second-order cases, including JIT/graph and large angles; included in both environment focuses |
| SDK-free numerical example | Statevector/Density/MPS value/Jacobian/Hessian/HVP asserted; full complex matrix max error2.30604301995351e-16; no Qiskit/PennyLane import or cloud access |
| Source/F821/diff checks | pass; new source/tests/example explicitly attributed |
| Repository attribution check | 1failed/4passed due to the unchanged pre-existing Router ledger omission; not legal acceptance |

The example's actual value/Jacobian/Hessian at7.3 are approximately
0.2514747525260357 / 0.24196596465747605 / -0.015717172032877223. It is located at
`examples/native_symbolic_power_qnode.py` and uses only the native SDK and NumPy.
The final tensor extension has the focused evidence above; the earlier broad
runs are not relabeled as current frozen FULLs. No FULL/GLOBAL/matrix or scoped
commit acceptance is inferred from these development results.

Remaining: general moving-projector fractional derivatives, dedicated public
MCX/MCPhase and factory ABI gaps, Parameter repr/UUID object contract, additional
malicious/roundtrip cases and original three frozen FULL/independent AD/GLOBAL
coverage floor91.34108013033072%/unchanged68 exclusions/original28-section matrix/
all numerical examples/controlled legal/origins/staged-commit equality gates.
No remote CI or final full SDK acceptance is claimed. The unrelated pre-existing
Router ledger omission remains an unresolved repository attribution check.

## R2O Development Checkpoint: Moving-Projector Power Jets

The actual new assistant reply in the existing default-Chrome conversation
"Claude 代码泄漏与应对" was read, not inferred from the thread API's reference
placeholder. Its R2O prompt is retained in
`docs/implementation/stage12_b_general_frechet_received_prompt.md`.
That prompt requires multi-parameter mixed derivatives, general direction
rules, MPS derivatives and the original frozen gates. This checkpoint is a
strict subset, not completion of that prompt or the full replacement goal.

### Red Tests And Native Repair

The first mathematical focus had 32 actual failures for the missing kernel;
after repair it had 32 passes. An independent conjugation family
`RY(p) RZ(p*p+.4) RY(-p)` has a genuinely moving eigenbasis and nonzero
commutator `[U,U']`. Tests include repeated eigenvalues, dimensions 2/4/8,
positive/negative fractional exponents and both sides of scalar phase wraps.
They explicitly distinguish the result from the incorrect commuting shortcut.

`unitary_power_jet` takes actual `(U,U',U'')` and evaluates the existing native
matrix function on a Schur-frame triangular 3-by-3 block operator. The first
off-diagonal block yields the Frechet derivative; twice the second block
includes both `L_f(U,U'')` and the repeated second direction. The same bounded
native Schur/binomial engine and cumulative local work counter are reused.
There are no eigenvector finite differences, frozen-projector approximations,
SDK calls or new production dependencies. Unitary/cut/dimension/workspace
checks precede decomposition, and output/view storage leases are tested.

Next, 27 genuine native QNode tests failed at the old fixed-projector refusal.
The new transient `native_matrix_power` operation stores a bounded native IR
source and its actual parameter UUID, keeping the user's original annotation
symbolic. Analytic Gate-body product/global-phase jets and ordered modifiers
feed the Frechet kernel. The existing first adjoint and tangent-over-reverse
second adjoint use the actual first/second gate derivatives. Explicit
parameter-shift is correctly refused for this general matrix function.
Original fixed-projector shift/MPS paths remain in place.

The expanded native suite checks full complex matrices, open/closed controls,
modifier order, nonconsecutive invocation wires, coherent global phase,
Jacobian/Hessian/HVP, IR/QPY UUID roundtrips, repeated-identity spectra,
precise branch refusal, UTF-8 byte bounds, foreign keys, resource denial,
source nonmutation and output/view lifetime. Constructor value validation
does not differentiate at a dummy point that might lie on a branch cut.

### Intermediate Errors Kept Visible

- One old refusal test still expected the previous generator-error wording;
  the newly supported adjoint domain now has a distinct exact shift refusal.
  The test was updated to explicitly request parameter-shift, not weakened
  into ignoring a numeric discrepancy.
- Initial added framework/source fixtures incorrectly chained public
  `QuantumCircuit.append`/`h`, whose public return object is InstructionSet.
  Correcting the test fixtures, not production return ABI, removed 8 failures
  per framework environment and 3 native fixture failures.
- Two native roundtrip tests exposed that `best` selected shift for second
  derivatives even though this new operation has no shift recipe. A blanket
  change to choose adjoint for all analytic gates then caused 21 real contract
  regressions: shifted-work limits and existing method/evaluation metadata
  changed. The broad run actually ended 21 failed / 846 passed / 1 skipped,
  273.87s. The fix was narrowed to the new general matrix primitive, retaining
  established ordinary-gate shift schedules and their budget tests. No old
  budget/metadata assertions were removed or relaxed.

### Terminal Evidence

| Scope | Actual terminal result |
| --- | --- |
| Final SDK-free native symbolic + moving QNode + Frechet math | 150 passed,16.07s,exit0; no skip/xfail |
| Final Main native/four-framework/controlled-public/Operator-Jordan focus | 975 passed,29.60s,exit0 |
| Final Alternate native/four-framework/controlled-public focus | 555 passed,28.34s,exit0 |
| New four-framework focus in each environment | 24 passed (8 new moving + 16 retained fixed-projector); Main6.68s, Alternate6.55s |
| New public full-complex matrix comparison | 27 passed against each installed Qiskit version; Main1.85s,Alternate1.87s |
| Main Core/Circuit/Information/Serialization and specified public power tests | 5045 passed,3 existing xfailed,8 warnings,345.16s; this run began before final UTF-8/foreign-key and method-selection hardening, so it is not frozen-final FULL |
| Narrow rerun of all three failure-bearing files plus moving QNode | 103 passed,287.97s,exit0 |
| Final Main Gradients/Interfaces/Compiler/QML/Devices/Noise | 869 passed,1 existing environment-contract skip,2 warnings,356.78s,exit0 |
| SDK-free numerical example | All assertions pass; moving-family value/Jacobian/Hessian at1.3 = 0.5375436444574617 / -1.3007148608563786 / -1.8961862476075249 |
| Attribution tests | 1 failed / 3 passed: unchanged Router core missing its ledger entry; not legal acceptance |
| New source/tests/example lint; edited runtime F821; diff whitespace | pass; broad F401 also exposes three pre-existing unused imports, left untouched |

Main actual import origins were inspected: native QuantumBridge comes from
this checkout, Qiskit2.4.1/PennyLane0.44.1 are external installed packages,
JAX0.7.1 and TensorFlow2.21.0 are in the Main virtual environment. Alternate
actually imports Qiskit2.6.0/PennyLane0.42.3/JAX0.6.2 and TensorFlow2.21.0 from
its virtual environment. The native example imports neither SDK and makes no
cloud calls. Existing fixed-projector Statevector/Density/MPS example values
and complete complex matrix error2.30604301995351e-16 are retained.

### Boundaries And Open Work

This increment supports bounded native generic Gate/ControlledGate families
with one free scalar parameter and fixed modifier exponents. It is not a
general multi-input Jacobian/mixed Frechet implementation. Multiple independent
inputs, moving-projector variable exponents, nested power annotations inside
generic bodies, arbitrary multi-angle/custom primitive jets and nonunitary
Frechet families remain incomplete. There is no claim of new general
moving-projector MPS derivatives or 100-wire derivative acceptance. The
existing fixed-projector 100-wire tests are retained, not relabeled as general.

Three final FULLs, independent AD frozen gates, GLOBAL floor91.34108013033072%,
unchanged68 exclusions, original28-section matrix, all SDK-free examples and
controlled legal/staged-commit equality remain NOT_RUN for a final frozen
tree. No stage/commit/push/fetch/auth/TLS/install/vendor/tag/release or new
hardware task was performed. HEAD remains main b443430; the preview server
and previously delivered 14 cases and finance evidence remain untouched.
R2O/R2/P4/full independent SDK replacement all remain ACTIVE / INCOMPLETE.

The terminal results and the 21-regression correction were sent back to the
authorized ChatGPT conversation. Its API indicates a newer reply but returns
only a content reference; the existing default-Chrome tab still exposes the
previous R2O body. Two narrowly matched reload attempts found no matching
AppleScript tab and performed no navigation. No new window, login or auth
change was requested. The newer reply is not claimed as read; continuation
can proceed under the actual fully read R2O prompt already retained above.

## R2O2 Development: Mixed Directions And Native Forward AD

Previous turn classification: progress. Actual source, independent numerical
evidence and regression results changed. The continuation preserves the full
independent Qiskit/PennyLane replacement objective, not a smaller acceptance
target. No R2O/R2/P4/full SDK completion is claimed.

The previously stale browser was refreshed only after checking foreground
PID2383 and the authorized conversation title. The actual R2O2 body was read
and retained in `docs/implementation/stage12_b_mixed_frechet_received_prompt.md`.
No new tab/window, login or authentication change was requested.

### Actual Math And Runtime Changes

The new mixed-direction/native QNode tests first terminated with32 failures.
The mathematical kernel now evaluates the existing analytic matrix function
on a four-block triangular operator in the unitary Schur frame:

```text
[[T, E, G, F],
 [0, T, 0, G],
 [0, 0, T, E],
 [0, 0, 0, T]]
```

The (0,3) block includes `L_f(T,F)` and both ordered E/G second directions.
This is not two copies of the previous repeated E/E direction. The original
three-block rule remains for equal directions. Both share the existing
matrix-function implementation, admission checks and cumulative local work.
Independent full-complex tests cover nonzero source mixed derivatives,
direction exchange, repeated spectra and2/4-dimensional moving bases.

Every source UUID now retains its own scalar occurrence in the existing
QNode recording pipeline. The native descriptor accepts the retained single
UUID format or an explicitly validated ordered multi-UUID list. Native
scalar expressions, circuit products, global phases and ordered modifiers
provide `(U,U_a,U_b,U_ab)` without a parameter-pair matrix cache. Adjoint
Jacobian/reverse tangents handle each local parameter index. Forward and
reverse directional sweeps form `U_v` and `U_iv` directly. The HVP test limits
full Hessian storage to one element and patches the full-Hessian entry to
fail; an eight-free-parameter/two-direction case still executes correctly.
The local dense blocks remain bounded; this is not a100-wire dense matrix.

Tests additionally cover nonlinear `sin(p)`, `exp(q)`, repeated parameters,
`q*q`, both partial-binding orders, vector UUIDs, same-name wrong-UUID
rejection, two-wire entanglers and controlled `p*q` global phases. Twelve
IR/QPY roundtrip scenarios repeat actual derivative execution. The transport
uses original symbolic annotations, not a QPY sidecar or SDK passthrough.

Two independent oracles are used: explicit SU(2) analytic first/second
formulas, and the separately authored test-only mpmath script at70 decimal
digits. Its explicit4x4 matrices, full complex powers, derivatives and
coherent-control expectations are retained as numerical JSON fixtures.
mpmath is pre-installed and is not imported by native production or the
SDK-free numerical example. Finite differences are test-side only.

### Forward-Mode Gap Found And Repaired

The first actual four-framework run ended3 failed /9 passed: Autograd's
native quantum primitive had VJP but no JVP registration. The existing
callback machinery now supplies JVP and directional second-JVP contractions;
public Autograd primitive rules compose forward-over-reverse,
reverse-over-forward and forward-over-forward. They use the real native
derivative graph, not precomputed tensors or a full Hessian. Third order and
max_diff1 second order remain explicit typed refusals. A later new test had
an overly specific error-message regex, causing39p/1f Main,637p/1f Alternate
and920p/1f/1skip in an intermediate broad run; asserting the actual
`higher_order_derivatives` feature fixed the test without changing runtime
or removing the order-limit assertion.

### Near-Cut Numerical Red And Reliability Boundary

An additional genuine red at `q=2*pi-1e-4` exposed a finite first derivative
error4.25482077e-9 against the8e-11 check. A direct probe found second
derivative errors of order1e-4 even though implicit square-root derivative
equation residuals were around1e-15. A tested local Sylvester solve did not
repair that conditioning issue and was not adopted as a production fix.

The jet kernel now screens close spectra on opposite sides of the branch
cut using their cubic second-jet separation sensitivity, exponent branch
jump and double-precision roundoff. It raises a specific LinAlgError when
that conservative screen cannot admit a reliable jet. This is a numerical
refusal, not a claim that those off-cut mathematical derivatives do not
exist, and not a generic Unsupported fallback. False-positive refusals are
possible; arbitrary-precision native jets are not implemented. Function
values can remain available when derivatives are refused. The initial
1e-4 inputs now explicitly test refusal and owner nonmutation; independently
resolvable points at +/-0.03 keep the original8e-11 first/3e-9 second numeric
assertions. No tolerance was loosened, and the original fixed-projector
near-cut paths remain unchanged.

### Current Terminal Evidence

| Scope | Actual result |
| --- | --- |
| Final SDK-free native math/symbolic/moving/mixed focus | 225 passed,31.01s,exit0; no skip/xfail |
| Final Main new/retained native+four-framework+public+Operator/Jordan focus | 1076 passed,52.18s,exit0 |
| Final Alternate corresponding focus without the420 Operator/Jordan family | 656 passed,50.76s,exit0 |
| Final mixed-QNode and both mathematical jet families | 107 passed,14.33s,exit0 |
| Four-framework mixed focus | 17 passed,10.37s before the later separation screen; included again in both final post-screen focuses |
| Native nonlinear/partial-binding/eight-input/intake edge extension | 46 passed,14.38s before the added branch cases; final post-screen native focus includes all53 mixed-QNode cases |
| Main Core/Circuit/Information/Serialization+specified public powers | 5076 passed,3 existing xfailed,8 warnings,346.92s before final separation screen; not frozen-final FULL |
| Main Gradients/Interfaces/Compiler/QML/Devices/Noise | 921 passed,1 existing environment skip,2 warnings,379.52s before the last edge-test additions and separation screen; not frozen-final FULL |
| Main DerivativeExecution/resource ownership | 843 passed,75.20s,exit0, after the final separation screen |
| New source/tests/example lint, edited-runtime F821, diff check | pass |
| Attribution tests | unchanged1 failed/3 passed: Router core ledger omission; not legal acceptance |

The SDK-free example asserts a true two-input HVP with full-Hessian budget1:
`[-0.09937363572243615,-0.0031690688993985805]`. Its independent mixed Hessian
reference has cross derivative `-0.009787820286360958`. All original
fixed-projector device checks and complete-operator error2.30604301995351e-16
remain in that runnable example. No SDK import or cloud call is made.

### Remaining Scope

General moving-exponent jets, generic-body nested powers, arbitrary
multi-angle/custom primitive derivatives, nonunitary Frechet families and
new general MPS derivatives remain incomplete. Source inspection confirms
`MatrixProductState._block_gate` and `_split` normalize branches, so simply
applying a derivative matrix would discard tangent amplitude and give wrong
derivatives. This needs a norm/weight-preserving tangent representation or
an equivalent verified contraction rule. No MPS runtime was changed, no new
general100-wire derivative acceptance is claimed, and the previous
fixed-projector100-wire tests are not relabeled.

Public MCX/MCPhase and further Circuit/Parameter ABI gaps, compiler basis
support for general matrix functions, other named Qiskit/PennyLane core
areas and the original full replacement objective remain open. Three final
frozen FULLs, independent-AD gates, GLOBAL>=91.34108013033072%, unchanged68
exclusions, original28-section matrix, all SDK-free examples, controlled
legal and frozen/worktree/staged/commit equality remain NOT_RUN for a final
tree. HEAD remains main b443430. No stage/commit/push/fetch/auth/TLS/install/
vendor/tag/release, Studio/Router changes, finance evidence edits or new
hardware tasks were performed by this increment.

The complete terminal report was sent to the authorized ChatGPT conversation.
Its actual R2O3 assistant body was subsequently read from the existing default
Chrome tab and saved as
`docs/implementation/stage12_b_mps_tangent_received_prompt.md`. It prioritizes
norm/complex-scale-preserving MPS tangents and mixed-state derivatives, while
retaining the original full objective and final gates. One wording error in
that prompt is noted: the new general derivative evidence is Statevector,
not a claim that general Density/MPS derivatives already passed. No R2O3
implementation or acceptance is inferred from receiving its prompt.

## R2O3-A: Scaled MPS Tangent Foundation

This checkpoint implements the numerical foundation of the received R2O3
request, not the whole R2O3 acceptance. Full functional parity/full
replacement remains ACTIVE / INCOMPLETE. No UI/Studio/Router, finance
receipt, credential, authorization, cloud, Git staging/commit/push/fetch,
dependency, tag or release operation belongs to this increment.

### Actual Red Before Runtime Edits

For theta0.37, the independent RY derivative applied to |0> is
`[-0.09197326676402061,0.49146812531511574]`, norm0.5. The old ordinary MPS
apply entry produced `[-0.18394653352804122,0.9829362506302315]`, norm1.0:
an amplitude ratio2.0. The ordinary normalized-branch contract is intentional
and remains protected by a regression test. Before adding a tangent type,
the new amplitude tests ended12 failed/1 passed (missing module); this is
separate from the actual numerical-loss probe above.

The specified noncommuting body RX(p), RZ(q*q+0.4), RY(-p), power0.5 on
wire99 of a100-wire QNode evaluated to0.9956956533655351 at[0.37,0.82], but
its public Jacobian raised `UnsupportedFeature(matrix_power_parameter_shift)`.
That public integration red remains OPEN at this checkpoint; lower-level
kernel passes below must not be relabeled as a passing public QNode path.

### Implemented Numerical Path

`information/mps_tangent.py` owns a bounded coherent sum of normalized native
MPS chains times finite complex scales. It uses the existing MPS `_apply`,
local contraction, QR/SVD and SWAP gather/restore engine, not another
simulator or a dense fallback. The opt-in MPS path collects local norm and
retained Schmidt factors. Binary exponents are accumulated separately, so
balanced huge/tiny factors need not overflow at an intermediate product.
Zero vectors have no chain and are never normalized into a nonzero state.
Coherent components retain all cross terms, including destructive interference.

The derivative path ignores a user simulation cutoff and retains numerical
rank using8*eps*max(matrix.shape)*largest_singular. A bond cap below that rank
raises before derivative truncation. This removes only numerical-null SVD
directions; relative discarded weights remain visible. It is not a rigorous
global derivative error bound or arbitrary-precision guarantee. Previously
truncated source states are conservatively refused. All exposed component
states are copies; updates make private copies before gauge/routing changes.

`diff/mps_tangent.py` is an internal two-direction propagation kernel:
`psi_ab_next = U_ab psi + U_a psi_b + U_b psi_a + U psi_ab`.
Its fixed Hermitian Pauli moment includes
`2 Re(<psi_ab|O|psi> + <psi_a|O|psi_b>)`. Planned component growth is checked
before copying or applying the next jet. This is not yet registered as a
public QNode gradient method and does not yet claim aggregate QNode/NativeHost
derivative-work admission.

### Range And Ownership Checks

Tests cover zero/tiny1e-300 tangents, complex phases, nonunitary nonadjacent
and reversed-wire maps, repeated coherent contributions, source and exported
copy nonmutation, bond refusal, bad scalar/operator/Pauli/wire inputs and
foreign ndarray/iterator protocol refusal. Underflow/overflow outside the
representable complex128 scale range raises, rather than manufacturing zero.
A local matrix whose dynamic range would lose a nonzero component during
rescaling is also explicitly refused.

Pauli overlap environments are rescaled at every site. A100-wire product
overlap whose unscaled intermediate is around1e-400, balanced by scale1e300j,
now remains finite. An initial oracle compared against the precanonicalized
input product and exposed a1.001e-10 relative difference due to the existing
QR sweep's backward-error behavior in tiny components. The final independent
80-digit Decimal oracle multiplies the represented native tensor entries;
it retains the original8e-13 relative assertion, and no runtime tolerance was
loosened. No claim of componentwise relative accuracy for arbitrary tiny
QR/SVD inputs is made.

New buffers use the existing retained-array leases. Tests check full-chain
copy admission before its first allocation, scale-buffer admission before
the abs kernel, coherent sharing/copy/view lifetimes, and a live exception
traceback retaining real buffers until it dies. Failed nonlocal SVD leaves
the source unchanged; all leases release after their actual owners die.
Hidden NumPy/LAPACK allocator workspace and Python object overhead remain
unobserved, not reported as zero or as a universal process-memory cap.

### Executed Evidence And Pending Acceptance

The focused new numerical/jet/resource suite ended86 passed after the
long-overlap correction, as part of a156 passed/1 existing warning SDK-free
MPS/device/resource regression,5.27s. Later width/dense-failure assertions
are included in the Main broad regression:3137 passed,1 existing warning,
168.55s,exit0. This command covered all DerivativeExecution, Gradients,
Devices and Information tests, three symbolic/moving/mixed four-framework
families and the two existing nondense MPS framework/HVP families. It had
no skips/xfails and is not a frozen-final FULL of the repository.
The same Alternate command ended3135 passed/2 existing xfailed/1 warning,
169.66s,exit0. Both xfails are the already guarded public
PennyLane0.42.3/Autograd complex NotImplementedType oracle failure in
`tests/derivative_execution/test_public_differential.py`; they are not
converted into oracle matches. No new skip/xfail marker was added.
Final SDK-free symbolic/moving/mixed math+QNode and new tangent/kernel/MPS
device/resource focus ended381 passed/1 existing warning,35.03s,exit0,
without skips/xfails. This includes86 new numerical/kernel/resource cases.
New source/test Ruff, edited existing runtime F821 and git diff --check pass.
All required command sessions for this checkpoint have terminated; the
existing homepage server remains PID349 on127.0.0.1:8765. HEAD remains
main b443430, without staging or committing the dirty workspace.
The jet family has22 cases: eight actual100-wire adjacent/distant first/mixed
checks; eight streamed-direction checks with full-Hessian entry forbidden;
four two-layer incoming-state-tangent product rules; global-phase bra/ket
cancellation; and a pre-expansion component-limit refusal. Only bounded
local2x2/4x4 matrices are used. Full MPS/statevector/density/Operator/Gate
materialization entry points are forbidden during these executions.

Still pending: public QNode selection and first/second/HVP dispatch; its
aggregate derivative work/array admission and correct method receipts;
the exact requested noncommuting source's end-to-end derivative path;
four-framework actual graphs, original symbolic UUID/vector/control/phase
IR/QPY roundtrips through the100-wire derivative path; and the requested
near-cut diagnostic fields. Existing near-cut/fixed-projector numerical
contracts must remain protected. These are not completed by having a native
low-level propagation kernel.

The original final three frozen FULLs, independent AD gates,
GLOBAL>=91.34108013033072%, unchanged68 exclusions, original28-section matrix,
all SDK-free examples, controlled legal checks and frozen/worktree/staged/
commit equality remain NOT_RUN for a final tree. The unrelated Router ledger
omission from the preceding checkpoint is not repaired or called accepted.

The terminal report was sent to the authorized existing ChatGPT conversation.
Its completed actual assistant body was read after a PID/focused-window/title-
guarded reload (no new page/login). The R2O3-B prompt is preserved in
`docs/implementation/stage12_b_mps_qnode_integration_received_prompt.md` with
the accessibility line splitting retained. It correctly treats public QNode
integration as OPEN and prioritizes method dispatch, unified Host/Device
resource admission, then real framework/IR/QPY/HVP closure. Receiving the
prompt is not execution or acceptance of those remaining tasks.

## R2O3-B: Public MPS Integration Development Checkpoint

The full independent Qiskit/PennyLane functional parity/full replacement
objective remains ACTIVE / INCOMPLETE. This is not R2O3-B acceptance.
The new public integration has real numerical evidence; two additional
TensorFlow mixed-mode graph requirements remain blocking reds. No skip,
xfail or numerical tolerance is added to hide them.

### Public Red And Implemented Dispatch

Before production dispatch changes, the specified RX(p), RZ(q*q+0.4),
RY(-p), power0.5,100-wire source again failed with the actual
`matrix_power_parameter_shift` traceback. Eight initial public/resource
tests failed, including an earlier full-Gate materialization during
construction and the missing component-budget configuration. These are
separate root causes, not eight independent algorithm failures.

`ExecutionPlan.gradient_capability` now selects `mps-tangent` only for an
analytic noiseless unitary MPS circuit containing a general matrix-power
primitive. Ordinary rotations/fixed-projector paths keep their established
shift schedules. Explicit `mps-tangent` is available for the analytic MPS
device and is not mislabeled adjoint. Shot/noise/dynamic/snapshot paths do
not silently acquire this method.

The new `diff/mps_derivatives.py` reuses `MPSTangentJet`, the native local
matrix-function jets and existing plan structures. Source preprocessing
Jacobian and directional classical second maps seed the four state terms.
It implements Pauli/Hamiltonian means, variance, local probability Walsh
readouts and joint-Pauli terminals, with observable processing left in the
existing transform graph. A derivative primal that differs from an ordinary
truncated forward value is explicitly refused, not normalized or silently
reported exact. Dense/custom observables and noisy/sampled general jets
remain unsupported by this new path.

Unbound transient Gate definitions now validate source structure and width
without evaluating at dummy zero parameters. Bound local values compose
native primitive matrices, controls/inverses/powers, without `Gate.to_matrix`
or `Operator` construction. This change is why tests can forbid even those
whole-object entry points while permitting admitted2x2/4x4 local arithmetic.

### Shared Planning And Resource Evidence

The shared work contract supplies method, direction count, local matrix
dimension, component count, bond/storage bounds, external-workspace allowance,
matrix-function work and tape count to QNode/Host/Device/transform execution.
The legacy `max_adjoint_operations` field acts as the common planned-work cap;
its use does not label this forward algorithm adjoint. Predictable component
growth and work checks precede any MPS update. Matrix jets are also checked
before a forward device evaluation, preserving owner/cache state on a
near-cut numerical refusal.

Actual Device tests cover both `best` and explicit `mps-tangent`, Jacobian,
Hessian and HVP. Consumed tapes equal the admitted sweep count; planned work
is charged once through Device execution, not charged twice by nested MPS
execution. Native Host callbacks without a precharged Device request admit
and charge their own work. Multi-output transpose admission was separately
probed with two output directions: one bound4016928, aggregate8033856, limit
4016928; it refused with zero MPS updates and zero consumed derivative work.

SVD, local matrices, coherent components and retained arrays keep existing
ownership rules. Conservative workspace is explicitly not observed NumPy/
LAPACK/Python allocator peak or process RSS. The conservative work model can
require a larger configured budget for multiple separate general Gates:
the independent eight-input/four-layer case uses max_adjoint_operations100M
and max_hessian_elements1, with no full parameter Hessian. It does not prove
that an arbitrary highly entangled100-wire state is scalable.

### Independent Numerical Checks

`scripts/probe_native_mps_power_oracles.py` uses explicit2x2 rotation matrices,
the SU(2) closed power identity and already installed mpmath1.3.0 at70 digits.
It imports neither QuantumBridge nor an upstream SDK and prints JSON only.
The checked-in numerical fixture covers the exact requested three-rotation
body and a genuinely noncommuting four-layer/eight-input HVP. A generator
typo used nonexistent mp.trace initially; replacing it with the explicit
two diagonal entries fixed the generator before fixture generation.

For the requested power0.5 body at[0.37,0.82], the independent result is
value0.9956956533655352, gradient[-0.022342078168391514,0.026851319249604443],
and mixed Hessian entry0.13981710664338265. Full complex local matrices,
Jacobian, Hessian, streamed HVP, JVP and VJP are compared to that fixture.
Native public tests also cover four distant wire orders; actual peak bond2
is asserted in those two-wire circuits. The eight-input HVP is checked with
the full-Hessian entry patched to fail and Hessian budget1; it streams eight
row/direction sweeps with one input-direction column.

Eight IR/QPY cases retain original symbolic ParameterVector UUIDs, numeric
exponents, an entangling two-wire body, global phase0.13*p*q and open/closed
controls on wires(0,1,99). Restored public100-wire MPS value, first/mixed
second derivatives and HVP match the independent70-digit fixture. Original
IR does not contain the transient matrix-power primitive; no private
sidecar is introduced and the original symbolic-exponent QPY refusal remains.

The numerical near-cut threshold is unchanged. Refusals now expose gap,
direction-norm coupling bound, resolution, screen and threshold diagnostics.
This coupling quantity is an input norm bound, not an exact eigenbasis
coupling or rigorous condition-number certificate. Near-cut MPS tests patch
the first MPS update to fail; the numerical exception occurs first, while
Circuit serialization and Device diagnostic sentinel remain unchanged.

### Framework Evidence And Open Reds

The initial new12-case four-framework family passed: real Torch/Autograd/
JAX-JIT-x64/TF-graph gradients, mixed Hessians, nonlinear external loss HVPs,
JVP and VJP, all through100-wire MPS with dense Gate/Operator/vector/density
entry points forbidden. The nonlinear loss is(value-0.3)^2; no Hessian is
precomputed and wrapped as a framework tensor.

Stronger Torch forward_ad tests then exposed three genuine reds: forward-only
inputs with requires_gradFalse lost their tangent; true forward-over-reverse
and reverse-over-forward lacked custom JVP rules. The existing bridge now
retains live dual inputs and composes native first/mixed rules. Reverse-over-
forward closes the first dual level before its reverse pass, so it does not
also request a third-order forward tangent. No torch.func/vmap/full compiler
support is inferred from this limited forward_ad addition.

The two stronger TensorFlow ForwardAccumulator/GradientTape mixed-mode graph
tests exposed the existing blanket third-order refusal. Several local graph
rule experiments were tested, including legal linear-slot transposes, but
reverse-over-forward still lost the H*direction term. Those TensorFlow runtime
experiments were fully removed; tensorflow_graph.py again matches its HEAD
content. The two blocking tests retain their original numerical assertions
and currently encounter the existing typed refusal. They are not skipped,
xfail-marked or silently accepted with only the classical2*g*g^T contribution.

A separate installed-TensorFlow2.21 probe, with no QuantumBridge imports,
used nested tf.function(sin), loss=(sin(x)-0.3)^2, x0.37 and direction0.4.
Reverse-over-forward returned0.6953874234918352 against the analytic
0.6775625506552614. This is evidence of an installed-framework baseline issue,
not a proof that every TensorFlow configuration is faulty or permission to
return a wrong finite QuantumBridge derivative. A public-API workaround and
complete mixed-mode integration remain required by the original objective.

### Development Validation State

Intermediate native focus:128 passed before the later framework/edge additions.
Public/native resource suite:42 passed,19.78s. Restored-format suite:8 passed,
15.60s in its first complete run. Initial four-framework MPS suite:12 passed,
19.17s, before stronger mixed-mode tests found additional gaps. These are
dated intermediate results, not the latest broad result or final acceptance.
The full latest development broad command includes both blocking TF tests;
it naturally terminated with exit1:7016 passed,2 failed,1 skipped,3 xfailed,
28 warnings,850.79s. The failures are exactly the two new TF mixed-mode
cases, both at the retained tensorflow_graph.py line44 typed third-order
refusal. The one skip is the existing missing-JAX-installation contract in
`tests/interfaces/test_native_qnode_autodiff.py:107`, not a mixed-mode escape.
Existing QPY/OpenQASM public-oracle xfails remain separate from acceptance.
This is a failed development broad regression, not a frozen-final FULL PASS.
The latest Alternate development focus naturally ended exit1:3429 passed,
2 failed,2 existing public-PL oracle xfailed,19 warnings,227.37s. Its failures
are the same two retained TF mixed-mode graph cases, not additional native
numerical mismatches. Scope: all DerivativeExecution/Gradients/Devices/
Information plus the old symbolic/moving/mixed/new-MPS framework families,
old nondense MPS framework/HVP families, restored MPS IR/QPY, native controlled
public powers and public moving-power differential tests. It is FOCUS, not FULL.

Remaining R2O3-B evidence includes both TF mixed modes, broader nested-control/
owner/frame combinations, dense-observable general derivatives and full
framework/budget closure. General moving exponents, nested generic-body
powers and other unsupported primitives remain open. Three frozen FULLs,
independent-AD gates, GLOBAL>=91.34108013033072%, unchanged68 exclusions,
original28-section matrix, all SDK-free examples, controlled legal and full
frozen/worktree/staged/committed runtime equality remain NOT_RUN for a final
tree. The unrelated Router ledger issue is not changed or called accepted.

This increment is local-only: no stage/commit/push/fetch, OAuth/TLS change,
reset/rebase/amend/force, install/vendor, tag/release, Studio/Router edit,
finance13-task evidence change or new hardware task. The full objective is
not narrowed to this MPS subset and is not marked complete.

## R2O3-B-TF: Reproduced Boundary Gap, Not Acceptance

The original full replacement goal remains ACTIVE / INCOMPLETE. The internal
TF mixed-mode feature state is BLOCKED_BY_FRAMEWORK_INTEGRATION / UNRESOLVED;
this also remains a QuantumBridge compatibility gap. It is not proof that
all responsibility belongs to TensorFlow and does not close R2O3-B or R2.

### Completed Diagnostic Matrix

`tests/interfaces/probes/probe_tf_mixed_ad_semantics.py` ran independently in
both installed environments. Main and Alternate each used Python3.12.6 and
TensorFlow2.21.0 and each returned diagnostic exit0 with48 MATCH and12
WRONG_FINITE, no disconnected/nonfinite cases or exceptions. Diagnostic
exit0 means JSON was produced, not that the numerical matrix passed.
Raw results and captured framework stderr are separate files:

- `tests/interfaces/probes/data/tf_mixed_ad_semantics_main.json`
- `tests/interfaces/probes/data/tf_mixed_ad_semantics_alternate.json`

The12 affected combinations are identical: three test functions (scalar
sin, two-parameter sin(p)*cos(q)+p*q, and its public custom-gradient form),
inner_tf_function=True, reverse-over-forward, outer eager/traced, and JVP
read inside/outside the outer Tape. All corresponding first JVP/VJP and
loss-gradient values matched; it was the loss HVP that was wrong. FoR,
Tape-over-Tape and the no-inner-tf.function layouts matched their analytic
oracles in this diagnostic. These small pure-TF matches do not prove the
QuantumBridge NumPy-callback graph can use those layouts safely.

Scalar expected HVP0.6775625506552614, actual0.6953874234918352.
Vector expected[1.5066825207992456,0.21703597826203344],
actual[1.6038122792617742,0.11632321094938619] in the ordinary vector case.
The probe checks all seven result fields, not just a chosen Hessian entry.
It asserts that no QuantumBridge/Qiskit/PennyLane modules were imported.

Two additional independently authored diagnostic scripts explore native-like
NumPy callbacks and public gradient registration, not production rules:
`probe_tf_callback_mixed.py` and `probe_tf_registered_callback.py`.
Their raw results are `tf_callback_mixed_main.json` and
`tf_registered_callback_main.json` in the same data directory. They include
zero/disconnected tangents, scope/type exceptions, and wrong finite RoF
results; they are failed experiments, not successful workarounds. No rules
from them were inserted into the production adapter. The TensorFlow public
custom_gradient documentation was an API reference only; no upstream
implementation or tests were copied or vendored.

### Formal QNode Regression, Two Losses

The existing100-wire four-framework family now also checks
loss=exp(y)+0.2*y**3. Its independent outer chain-rule oracle is
L'(y)*H_f+L''(y)*g*g^T, with L'=exp(y)+0.6*y*y and
L''=exp(y)+1.2*y. There is no loss-specific production implementation.
The original squared loss and its assertions are retained unchanged.

Latest Main single-file focus:32 passed,4 failed,18 warnings,36.60s, exit1.
Latest Alternate single-file focus:32 passed,4 failed,18 warnings,36.48s,
exit1. No skipped or xfailed cases in either run. JUnit evidence:
`tmp/r2o3b-tf-main-mps-framework.xml` and
`tmp/r2o3b-tf-alternate-mps-framework.xml`.
Four failures are exactly square/exponential_cubic x TF FoR/RoF. All fail
at the retained tensorflow_graph.py line44 typed refusal. The32 passing
cases include all three powered-Gate cases in four frameworks with both
losses, real Torch forward_ad first/FoR/RoF, JAX FoR/RoF with both losses,
and the true-third-derivative refusal contract. Full dense100-wire entry
points remain forbidden by the existing assertions. This is FOCUS, not FULL.

Earlier development broad results stay failed: Main7016 passed/2 failed/
1 skipped/3 existing xfailed; Alternate3429 passed/2 failed/2 existing
xfailed. They predate the extra loss and cannot be relabeled as current
all-green broad validation. No broad rerun or frozen final gates were started
while the new blocking tests were still red.

### Adapter Semantics Audit

The present graph callback order0 represents f(x); order1 represents
J(x)^T*u. The order2 pair represents A=sum_i u_i*H_i(x)*v and B=J(x)*v.
A's derivative with respect to x needs a third derivative, but its linear
u/v transposes need only second derivatives. B's derivative with respect
to x needs a second derivative and its v transpose needs only the Jacobian.
Therefore order2.gradient being reached is not by itself evidence that
the user's request is third order. The current unconditional refusal also
rejects legitimate second-order mixed propagation. Preserving it avoids
wrong finite results but is not a completed or correctly classified solution.

### Example And Evidence Limits

The SDK-free native_symbolic_power_qnode example completed with explicit
PYTHONPATH pointing at this workspace. Vector/density/MPS value, Jacobian and
Hessian agree; complete complex-operator max error2.30604301995351e-16, and
streamed mixed HVP[-0.09937363572243615,-0.0031690688993985805]. No upstream
SDK or cloud call is part of that example. The first invocation without
explicit PYTHONPATH imported an unrelated external clean checkout and
failed ImportError for QuantumCircuit. It is recorded as an environment
failure, not hidden as a successful example run.

The prior SDK-free focus session11841 handle was no longer available after
context recovery and no app terminal log was attached. Its terminal status
cannot be reconstructed here; no PASS or431-case count is asserted, and no
healthy process was cancelled/restarted merely because its output was lost.

ChatGPT received the completed results in the existing authorized
conversation. Its actual complete R2O3-B-TF2 reply was read after a guarded
reload and archived as `stage12_b_mps_tf2_boundary_received_prompt.md`.
It prioritizes exact node semantics and public fused-backprop boundary
experiments, not a change to the verified MPS mathematical kernels.
The follow-on pure TF boundary matrix has now completed in both environments;
its actual result is recorded below, separately from native acceptance.

Production tensorflow_graph.py still matches HEAD; no experimental wrong
finite rules are retained. Git remains local-only, with no commit/push,
OAuth/TLS changes, installs, third-party payload, new hardware tasks or
Studio/Router/finance receipt changes. Final FULL/coverage/matrix/legal/
frozen/staged/committed equality gates remain NOT_RUN, not waived.

### R2O3-B-TF2 Boundary Experiment Result

`tests/interfaces/probes/probe_tf_public_boundary.py` independently tests
scalar sin, the two-parameter nonlinear function, and a two-output function
with unequal cotangent weights[0.7,-0.2]. The probe explicitly implements
the analytic first VJP and its point/direction transpose using public nested
custom_gradient; its small analytic Jacobian/Hessian expressions exist only
as test-function mathematics, not precomputed quantum derivative payloads.
It checks square and exponential/cubic losses, outer eager/traced, and FoR/
RoF/Tape-over-Tape under four function-boundary layouts,144 records total.

Main and Alternate independently returned the same diagnostic outcomes:
96 MATCH,12 WRONG_FINITE,36 EXCEPTION, zero disconnected/nonfinite results.
Both used Python3.12.6, TensorFlow2.21.0, global optimizer JIT empty and
explicit jit_compile=False for every tf.function created by this probe.
Every traced successful outer function traced once; inner functions, where
present, traced once. Failed outer traces have count0, not a successful
compiled execution. No XLA execution is claimed.

By layout, each environment observed:

- plain_inline:36 MATCH.
- custom_inline:36 MATCH.
- inner_custom (tf.function wrapping nested custom-gradient boundary):
  36 EXCEPTION, including InternalError construction and inaccessible
  captured FuncGraph tensor errors. This layout is not a working solution.
- custom_outside (public custom-gradient boundary around a forward-only
  tf.function):24 MATCH and12 WRONG_FINITE. All12 errors are RoF across
  scalar/vector/multioutput, two losses, and outer eager/traced. Decorator
  placement therefore did not fix this actual experiment.

Results including complete error messages/tracebacks and framework stderr
are `tests/interfaces/probes/data/tf_public_boundary_main.json` and
`tf_public_boundary_alternate.json`. Error/traceback lines are losslessly
interned: reconstruct each field by joining the diagnostic_lines entries at
its *_line_indices with newline. This avoids duplicating long scope-error
tracebacks dozens of times; it does not drop errors. The first Main output
was truncated by terminal transport, so the diagnostic was repeated with
this lossless output encoding; it was not recorded as a numerical PASS.

The strict144-case diagnostic has numerical/exception failures despite
exit0 meaning successful report generation. The four formal QuantumBridge
mixed-mode tests remain red in each environment. No boundary experiment
was promoted into tensorflow_graph.py, no tolerance/skip/xfail was changed,
and no broader/final acceptance gate was declared successful. Public
mixed-mode integration remains unresolved under the complete original goal.

After these diagnostics, a new SDK-free narrow public MPS validation with
explicit workspace PYTHONPATH completed:50 passed,35.81s, exit0, no skips or
xfails. It covers the24 public moving-power tests,18 Device/admission cases
and8 IR/QPY roundtrips, recorded in
`tmp/r2o3b-native-public-mps-sdkfree.xml`. This is a fresh FOCUS confirmation,
not a recovered result for old session11841 and not SDK-free FULL. Ruff on
all diagnostic scripts and the expanded framework tests passed; git diff
--check passed. Both144-record JSON artifacts parsed with1398 valid interned
diagnostic-line references each. These checks do not make the4 TF red tests
green and do not complete the original full replacement objective.

## R2O3-B-TF3: Explicit VJP Isolation And Directive Admission Repair

Full independent Qiskit/PennyLane functional parity/full replacement remains
ACTIVE / INCOMPLETE. The actual completed TF3 ChatGPT reply was read in the
existing authorized conversation and archived in
`stage12_b_mps_tf3_vjp_received_prompt.md`. It gates production TF changes on
successful pure analytic and host-callback models. That gate did not pass.

### Explicit VJP Analytic Model

The independent probe `tests/interfaces/probes/probe_tf_differentiable_vjp.py`
adds f:R2->R2 with f1=sin(p)*cos(q)+p*q and
f2=exp(0.2*p-q)+sin(p*q). Its VJP primitive has explicit point and upstream
cotangent inputs. Its reverse rule supplies both sum_i u_i*H_i*z and J*z;
its joint directional contract is sum_i u_i*H_i*v+J^T*w. Separate scalar
and one-output/two-input functions protect the same mathematical rules.

`tests/interfaces/test_tf_explicit_vjp_model.py` contains12 point/cotangent/
joint-variation cases,8 multioutput weight cases, and36 actual mixed AD
cases covering eager/traced, FoR/RoF/Tape-over-Tape, scalar/vector/multioutput
and square/exponential-cubic losses. The prototype's initially unconnected
VJP derivative produced56 failures,4.88s, exit1. This was an intentionally
unconnected new mathematical prototype, not56 pre-existing SDK regressions.
After connecting the two analytic rules: Main56 passed,6.48s; Alternate56
passed,6.44s. No skips/xfails or tolerance changes. JUnit receipts are
`tmp/r2o3b-tf3-model-red.xml`, `r2o3b-tf3-model-main.xml` and
`r2o3b-tf3-model-alternate.xml`. A standalone Main run also produced56
analytic matches with no quantum SDK modules imported; numerical output is
`tests/interfaces/probes/data/tf_explicit_vjp_analytic_main.json`.

These passes prove a small mathematical model and its explicit VJP rule,
not a TensorFlow/native QNode integration or native arbitrary third order.
The analytic small Hessians are test-function formulas only, not quantum
Hessian tensors injected into a production graph.

### Host Callback Gate Did Not Pass

The second phase exchanges these analytic values for NumPy host callbacks
with separate value, VJP, JVP, weighted directional Hessian and bilinear
transpose nodes. It transports only contracted outputs, not full Hessian
tensors. True point-third contractions are guarded; zero multilinear
factors give their mathematically zero contraction, not a fabricated
nonzero third derivative. No private global JVP registry is used.

Main and Alternate independently observed20 matches and36 exceptions or
mismatches across the same56 cases. Breakdown: semantics2 pass/10 fail;
multioutput weights0 pass/8 fail; mixed AD18 pass/18 fail. Tape-over-Tape
matched in both execution modes; eager RoF matched in all6 cases; eager
FoR triggered the point-third guard, while traced FoR/RoF and traced VJP
variations had incorrect finite derivatives. Passing eager prototypes are
not promoted into supported native interfaces.

For theta[0.37,0.82], u[0.7,-0.2], v[0.4,-0.3], w[0.2,-0.6],
expected VJP=[0.8437575521123502,0.09815629121493111].
Parameter contribution=[-0.07524302791500206,0.10543577391670647];
cotangent contribution=[-0.23522896954549893,0.09381674223233005];
sum=[-0.310471997460501,0.19925251614903652]. The traced callback variation
returned[0,0], although its reverse point/cotangent transposes matched.
In eager mode the internal third-point transpose guard was actually
evaluated with direction[1,1] and incoming[0.4,-0.3]. This records the
executed internal edge, not a claim that the user's requested first
variation of VJP genuinely needs a third derivative of f.

Complete numerical/error/traceback receipts are
`tests/interfaces/probes/data/tf_explicit_vjp_callback_main.json` and
`tf_explicit_vjp_callback_alternate.json`. The earlier Main diagnostic,
before failure payload enrichment, is preserved separately with `_initial`
in its filename. Error/traceback line interning is lossless as before.
Both environments are TF2.21.0/Python3.12.6, explicit jit_compile=False,
global optimizer JIT empty. No host-graph prototype was inserted into
tensorflow_graph.py or tensorflow_autodiff.py; the four formal mixed-mode
tests remain blocking reds. Feature state remains
BLOCKED_BY_FRAMEWORK_INTEGRATION / UNRESOLVED, a QuantumBridge gap.

### Actual Native Resource Bug Repaired

While protecting TF/MPS admission, a separate actual public regression was
reproduced:100-wire native moving-power circuits with wide barriers were
assigned an entangling Schmidt-rank growth by two resource estimators.
With no bond cap, `_bond_bound` inferred2^50 despite a product-state
circuit. Public native HVP failed its planned-work cap; both actual TF
Tape-over-Tape graph cases failed host status3. These are real endpoint
failures, separate from the four unresolved FoR/RoF graph-edge failures.

`diff/mps_derivatives.py:_bond_bound` and
`execution/derivative_planning.py:device_working_bytes` now skip only
operations marked directive whose name is barrier or delay, matching the
existing noiseless MPS execution path. Unknown directives remain
conservatively bounded; no general directive/opaque operation exemption is
introduced. The MPS numerical kernel, Fréchet formulas, actual work charging
and workspace accounting are unchanged. The corrected bound is1, with the
same storage estimate as the otherwise identical unitary circuit.

New tests cover capped/uncapped bounds, full/external-only workspaces,
unknown directives, actual public HVP, and actual TF nested-reverse graphs
with/without delay. The TF100-wire tests forbid full Gate/Operator/vector/
density materialization. Six low shared-budget cases and two malformed
direction cases additionally require refusal before the first MPS update,
zero tape/shot consumption, released buffers and unchanged source state.

Two initial test-authoring mistakes are not counted as production failures:
an invalid .circuit attribute assumption, then supplying unlowered public
Instruction handles to a planner that consumes lowered native operations.
The bound unit fixture was corrected to the actual native operation store;
the public QNode/TF endpoint tests retain their original public sources.
After the runtime fix the first8-case directive subset passed in3.62s,
before the additional8 atomicity tests and stronger dense-entry guards.

The latest Main protective FOCUS naturally ended exit1:186 passed,4 failed,
18 warnings,83.65s. All new model/directive/atomicity cases and the existing
public MPS/resource/IR-QPY/Torch/Autograd/JAX/TF ordinary-second/ownership
protections passed. Failures are exactly the original two losses x TF
FoR/RoF at tensorflow_graph.py44. Receipt:
`tmp/r2o3b-tf3-main-focus.xml`. Alternate same-scope FOCUS naturally ended
exit1:186 passed,4 failed,18 warnings,83.81s, with exactly the same four
TF mixed-mode failures; receipt `tmp/r2o3b-tf3-alternate-focus.xml`.

The SDK-free targeted64-case native MPS/directive/admission/IR-QPY run
completed64 passed,36.01s, exit0, no skips/xfails; receipt
`tmp/r2o3b-tf3-sdkfree-native-focus.xml`. This includes the final strengthened
zero-consumed-derivative-work and Device-sentinel atomicity assertions.
Those final14 native directive tests were also rerun separately in Main
and Alternate, each14 passed,0.36s; receipts
`tmp/r2o3b-directive-final-main.xml` and
`tmp/r2o3b-directive-final-alternate.xml`.

The SDK-free native_symbolic_power_qnode example completed successfully with
explicit current-workspace PYTHONPATH. Vector/density/MPS values, Jacobians
and Hessians agree; complete complex-operator max error remains
2.30604301995351e-16, and streamed HVP is
[-0.09937363572243615,-0.0031690688993985805]. No upstream SDK or cloud call.
Ruff passed on all probe scripts, new model/directive tests and the MPS
derivative module; shared derivative_planning.py passed F821; git diff
--check passed. These are completed FOCUS/example checks, not frozen FULLs.

No final broad/FULL/coverage/matrix/legal/freeze gate is accepted from this
FOCUS. No push/commit/fetch, auth/TLS change, install/vendor, tag/release,
Studio/Router edit, new hardware task or historical finance evidence change.

The completed TF3 results were sent to the existing authorized ChatGPT
conversation. Its actual complete TF4 reply was then read and archived in
`stage12_b_mps_tf4_native_tensor_received_prompt.md`. It changes the proposed
research direction from callback/decorator experiments to pure public-TF
tensor local operators and stable SU(2) fractional powers, then shared-plan
low-qubit integration and a genuinely nondense100-wire tensor network with
resource admission. Receiving this reply is not implementation evidence:
no such TF specialization has been implemented at this checkpoint. The four
formal mixed-mode reds and full replacement goal remain open. The next work
must first validate the pure TF complex-operator/value/AD layer before any
production routing change or claim of100-wire support.

## R2O3-B-TF4 Pure Tensor Mathematical Checkpoint, 2026-10-24

This is the first, pure-math layer of the actually received TF4 prompt. It
does not implement the second native-QNode layer or the third100-wire
TensorFlow tensor-network layer. Full independent replacement remains
ACTIVE / INCOMPLETE; the formal four TF mixed-mode reds are not waived.

Independently authored prototype:
`tests/interfaces/probes/probe_tf_native_tensor_execution.py`.
It imports neither QuantumBridge nor Qiskit/PennyLane. Public float64 /
complex128 TF ops evaluate RX/RY/RZ, a noncommuting two-qubit entangling
baseline, explicit global phases and coherently controlled local powers.
Noncommuting source families include RZ(q)RX(p) and the requested
RY(-p)RZ(q*q+0.4)RX(p), with powers0.5,-0.5,1.5. Controls0/1, wrapped
global phase, negative trace, a near-identity point and exact identity are
covered. This is not an arbitrary-unitary matrix-function implementation.

For S in SU(2), the prototype represents the principal power by
A*I+B*(S-tr(S)*I/2), using the two scalar principal phases. A canonical
trace sign is accompanied by its determinant/global-phase correction; no
observable-only/global-phase equivalence is substituted for complete matrix
equality. The coalescing-spectrum branch uses regular power-series
coefficients in sin(theta)**2 rather than differentiating sqrt(0). Existing
native-scale unitary/determinant and principal-cut/cubic-separation screens
are retained as conservative validation. Untested general exponents,
near-integer/cut interactions and arbitrary larger matrices are not accepted
from these cases. No generic eig/eigh/logm, custom gradient, stopped quantum
derivative, finite-difference runtime rule or Hessian-tensor callback is used.

The independent generator
`scripts/probe_tf_tensor_execution_oracles.py` uses already installed
mpmath1.3.0 at70 digits and explicit matrices. The checked-in fixture
`tests/information/data/tf_native_tensor_execution_oracles.json` contains12
cases with complete complex states/operators, two expectations, Jacobians,
Hessians and all8 real/imaginary local components' first/second derivatives.
Normalization and unitary residuals are checked below1e-50 before generation.
A generator-authoring mistake in an initial unsaved Kronecker constructor
was corrected before saving the fixture; its zero-state output was never
accepted as an oracle. This turn regenerated the final complete fixture and
compared every field exactly: all12 reproduced, including complex jets.

Intermediate failures are preserved, not relabeled as passes:

- Initial incomplete pure-power implementation:22 failed,2 passed,
 168 deselected,3.12s (`tmp/r2o3b-tf4-tensor-model-red.xml`).
- First192-case mathematical subset:192 passed,99.04s. This preceded the
 full-complex derivative and additional refusal checks.
- Stronger complex forward-over-forward checks exposed11 traced failures
 at assertion-only boolean ops; replacing assertion wrappers alone did not
 repair them. Both11-failure receipts remain in tmp.
- An affine-output validation-function attempt completed212 passed,
 22 failed,146.166s, exit1 (`tmp/r2o3b-tf4-tensor-main-final.xml`). Its
 eager reverse-over-forward calls reported an expected2/received4 gradient
 arity error. The filename does not make this a passing final receipt.

The repaired prototype's compiled validator returns boolean decisions only,
never a trainable matrix/phase. All trainable local quantum math remains in
the caller's TF graph. This avoids differentiating assertion wrappers without
removing validation, installing private TF rules or modifying TF. Main and
Alternate use TF2.21.0/Python3.12.6; these results do not prove every TF version.

Completed numeric/model runs:

| Run | Actual Result | Receipt |
| --- | --- | --- |
| Main pure tensor math |234 passed,144.80s, exit0; no skip/xfail |`tmp/r2o3b-tf4-boolean-main.xml` |
| Alternate pure tensor math |234 passed,148.23s, exit0; no skip/xfail |`tmp/r2o3b-tf4-boolean-alternate.xml` |
| Main added validation-under-AD |38 passed,234 deselected,8.87s, exit0 |`tmp/r2o3b-tf4-validation-main.xml` |
| Alternate added validation-under-AD |38 passed,234 deselected,8.84s, exit0 |`tmp/r2o3b-tf4-validation-alternate.xml` |
| Main original public100-wire four TF mixed modes |4 failed,32 deselected,3.25s, exit1 |`tmp/r2o3b-tf4-original-four-main.xml` |
| Alternate original public100-wire four TF mixed modes |4 failed,32 deselected,3.22s, exit1 |`tmp/r2o3b-tf4-original-four-alternate.xml` |

Each environment has272 disjoint passing pure-model cases across the two
completed runs, not a single272-case run or repository FULL. The new38
checks cover nonunitarity, wrong determinant, nonfinite phase and exact cut
refusal inside eager/traced value/FoR/RoF/TapeTape; integer exponents0,2,-3
also cannot prune validation. These are real expected-error checks, not skips.
Direction-only HVP tests monkeypatch GradientTape.jacobian to fail if called.
Full complex component derivatives additionally use actual nested forward
accumulators; quantum-output J/H/JVP and a nontrivial vector VJP are checked
against the independent fixture. Both external losses use TF's own full
chain rule. Traced value graph/function-library scans forbid PyFunc,
EagerPyFunc, generic eigensolvers and MatrixLogarithm. jit_compile=False.

No production routing or local evaluator was inserted into
`interfaces/tensorflow_graph.py` or `interfaces/tensorflow_autodiff.py`;
both still have no diff from HEAD. No Circuit/IR/Compiler parameter binding,
shared DerivativePlan/Device admission, owner isolation, graph-wide resource
accounting, max_diff policy or nondense100-wire TF contraction is accepted
from this pure prototype. The original native NumPy/Frechet/MPS math was not
rewritten by this increment. Those integrations are the next implementation
work, not checked boxes implied by passing pure tensor tests.
The four original endpoint failures were actually rerun in both environments
after the pure-model work; all still raise the existing blanket third-order
refusal at tensorflow_graph.py44. No assertion/tolerance, skip or xfail was
changed to hide them. Ruff for the three new Python files and git diff
--check pass. These results do not establish remote CI health.

No final SDK-free/Main/Alternate FULL, GLOBAL>=91.34108013033072%, unchanged68
exclusions, original28-section matrix, all SDK-free examples, controlled
legal, five frozen origins or frozen/staged/commit equality was run for this
candidate. No stage/commit/push/fetch, auth/TLS change, dependency installation,
source vendoring, tag/release, cloud task, historical finance change, Studio
or Router edit. HEAD remains b443430; remote CI was not inspected or changed.

The completed TF4 results were sent to the existing authorized ChatGPT
conversation. Its actual completed TF5 reply was read from the same default
Chrome tab and archived in
`stage12_b_mps_tf5_native_qnode_received_prompt.md`. It accepts only the pure
mathematical checkpoint, not native TF integration. Next is actual low-qubit
QNode execution from existing plans, followed by nondense100-wire contraction;
the original four reds and all original final gates remain open. No new
conversation, page or login was created. This receipt is not a production
implementation or independent code/CI review.

### TF5 First Real-QNode Red Baseline

`tests/interfaces/test_native_tf_tensor_execution.py` now supplies actual
two-/four-qubit public QNodes with an unbound native moving-projector
annotated power on the last wire. It reuses the original independent
`native_mixed_power_oracles.json`, not a hand-written TF replacement circuit.
Both external losses are exercised under traced FoR/RoF/TapeTape and compare
directional second derivatives at the original2e-9 tolerance. A finally block
checks unchanged source IR, parameter UUID order and stored operation identity
even when construction/differentiation raises.

The new12-case module completed naturally with exit1 in both environments:
Main4 passed/8 failed,4.15s; Alternate4 passed/8 failed,4.16s. Receipts:
`tmp/r2o3b-tf5-low-qubit-red-main.xml` and
`tmp/r2o3b-tf5-low-qubit-red-alternate.xml`. Four ordinary nested-reverse
cases pass through the existing native callback bridge. All eight FoR/RoF
cases hit the same existing tensorflow_graph.py44 refusal; they are eight
new endpoint reproductions of the known integration gap, not eight new
independent SDK regressions. No skip/xfail or tolerance changes.

This is a red baseline, not a completed TF5 specialization. No production
TensorFlow path has been added. Inspection confirms that source construction
already uses record_compiled_parameters and existing compiler options;
NativeHostKernel owns source snapshots and the validated static plan.
Its current numeric plan/prepare_second and Device admission must not be
bypassed by a standalone TF statevector. Remaining implementation questions
include admitted graph workspace, repeated tracing/runtime checks and
max_diff semantics without recreating the blanket mixed-AD refusal. The
new adapter must preserve these policies before being selected publicly.

Ruff passes for all four TF4/TF5 Python files and git diff --check passes.
TF5B low-qubit integration, TF5C100-wire integration and the full replacement
objective remain ACTIVE / INCOMPLETE. No Git mutation or hardware/UI work.

### TF5 Existing-Plan Local Operator Implementation

The first native implementation boundary now exists inside
`quantumbridge/interfaces/tensorflow_native_execution.py`:
`TensorFlowLocalOperator(plan, compiled_operation_index)`. It consumes an
existing exact ExecutionPlan, lowers it using the existing native engine,
and structurally decodes the selected native_matrix_power occurrence.
Its source is the validated native IR already carried by that occurrence,
not a manually rebuilt TF rotation circuit. `_decode`'s finite numeric ones
are structural argument-count validation only; no quantum matrix/jet is
evaluated at a dummy point. Existing `_source_body`, `_admit`, gate limits,
Parameter identities and record_compiled_parameters are reused.

The kernel owns a snapshot in the existing native Circuit representation,
not an independent Circuit/IR/UUID model. Packed values follow the existing
plan recorder's occurrence order; the same native expression evaluator maps
the source AST to live TF scalars. It evaluates RX/RY/RZ, local scalar phase,
U/P and standard fixed-gate factors, then ordered inverse/integer and one
principal fractional power. Coherent controls are deferred by the matrix-
function identity f(diag(I,U))=diag(I,f(U)), with the existing native bit
reversal for public control states. Multiple sequential fractional powers
and powered source bodies wider than one qubit remain explicit Unsupported;
they are not incorrectly combined or sent to an SDK.

`tensorflow_native_math.py` adapts our own tested TF4 formulas; the separate
pure no-QuantumBridge prototype remains independent as a witness. TensorFlow
is imported only for evaluation, not structural admission. All trainable
matrix/phase math remains live TF ops, and both source and result finiteness
are checked through bool-only compiled validators. This introduces no host
quantum callback, generic eig/logm, private JVP registry, stop-gradient or
complete Hessian injection. Static fixed gate constants reuse the native
primitive matrix helper; it is never called for a trainable matrix.

The new local tests consume actual QNode._construct ExecutionPlans, rather
than substituting hand-written TF circuits. They check complete complex
operators, both output J/H, FoR/RoF/TapeTape with both nonlinear losses,
vector weights, and full real/imaginary matrix J/H with nested forward AD.
Open/closed two-bit controls, integer/inverse modifier order, a moving
determinant phase and partial binding also compare against existing native
Frechet/value evaluators. All gradients remain TF derivatives, not native
jets inserted into the framework graph. Trace/function-library scans check
both values and derivatives for forbidden callbacks/spectral evaluators.

The IR/QPY tests keep ParameterVector UUID order, compiled operation order,
wire indices, original-source immutability and restored-source immutability.
An initial test incorrectly demanded original/restored serialized text be
identical despite permitted format canonicalization;18/44 cases failed that
test, not matrix values. Correcting that assumption then exposed a second
test-authoring error: format loaders return native Circuit, not necessarily
the public QuantumCircuit with .data. The198-case intermediate run completed
176 passed/22 failed,88.31s, solely at that incorrect .data access. The test
now checks the shared native operation store identity and both snapshots,
while retaining all UUID/frame/matrix tests. Final format-only22 passed4.02s.
These intermediate failed receipts remain recorded, not retroactive passes.

Local admission rechecks construction limits and active-scope memory bounds
before TF matrix allocation. It validates operand width, recorder identity
uniqueness, primitive metadata, static dtype/shape and modifier domain.
The runtime-point tests reuse exactly one concrete TF graph for valid,
NaN/Inf/cut, then valid inputs, proving assertions are not trace-only. Owned
kernel results remain unchanged after source/plan mutation. SDK-free import
sentinels forbid even attempting TF/Qiskit/PennyLane imports during admission.
This is not complete graph-wide TF resource accounting: no Device execution,
DerivativePlan, SecondWork consumption, contraction/gauge, native third-order
policy or shared graph ledger is closed by this local matrix kernel.

Completed development evidence before the combined protective run:

- Main initial final local234 passed,93.57s, no skip/xfail; receipt
 `tmp/r2o3b-tf5-local-final-main.xml`. This preceded the24 stronger complex-
 jet/owner checks and final operand/recorder validation additions.
- Main24 additional complex-jet/owner cases passed,44.97s;234 deselected.
 Receipt `tmp/r2o3b-tf5-local-strengthened-main.xml`.
- Alternate267 passed,136.13s, no skip/xfail; receipt
 `tmp/r2o3b-tf5-local-final-alternate.xml`. This preceded the final two
 malformed-frame/duplicate-recorder admission tests and their guards.
- Final SDK-free admission11 passed,0.20s; Alternate admission11 passed,
 0.17s, no skip/xfail. Receipts `tmp/r2o3b-tf5-local-admission-sdkfree-final.xml`
 and `tmp/r2o3b-tf5-local-admission-alternate-final.xml`.
- A separate SDK-free structural smoke confirmed no TF/Qiskit/PennyLane
 import and unchanged source with current-workspace PYTHONPATH.

Public `QNode.__call__`, tensorflow_autodiff.py and tensorflow_graph.py have
not been rerouted or replaced. Native low-qubit whole-QNode execution is
still incomplete; the original four100-wire TF reds are still blocking.
The kernel cannot be marketed as a public TF backend, a100-wire MPS executor
or full SDK parity. Required next work is the admitted executor/contraction
and explicit path selection using the existing Device/derivative plan,
including runtime budgets, max_diff semantics and output/owner contracts.

No final three FULLs/GLOBAL>=91.34108013033072%/unchanged68 exclusions/original
28-section matrix/all examples/legal/frozen origins/staged-commit equality
is accepted from these local development tests. No push/commit/stage/fetch,
install/vendor, auth/TLS change, Studio/Router edit, tag/release, new hardware
task or historical finance edit. The full objective remains ACTIVE/INCOMPLETE.

A separately completed Main numerical snapshot for the high-precision
`controlled1` case (requested noncommuting body, power0.5, phase0.13*p*q)
measured outputs[0.9978478266827673,0.9663859380580584]. Maximum complete local
operator error=1.5700924586837752e-16, output-J error=1.3877787807814457e-17,
output-H error=5.551115123125783e-17. Actual external exponential/cubic-loss
FoR HVP=[-0.045366643578022614,0.010071505886061816], independently expected
[-0.04536664357802258,0.010071505886061698], max error1.1796119636642288e-16.
These are measured errors for this representative case, not a global error
bound for all inputs/branches, nor a public QNode/MPS execution receipt.

The final current-source Main protective FOCUS naturally ended exit1:
577 passed,12 failed,18 warnings,322.23s, no skips/xfails. Receipt:
`tmp/r2o3b-tf5-main-protective-focus.xml`. Structured JUnit inspection gives
220 new local-operator passes +38 local-contract passes +11 framework-free
admission passes +272 retained pure-math passes +32 existing four-framework
MPS passes +4 existing ordinary low-qubit passes. Failures are exactly the
four original public100-wire TF mixed-mode cases and their eight two-/four-
qubit FoR/RoF variants, all at unchanged tensorflow_graph.py44. The new local
kernel's269 tests pass, but the public executor integration remains open.
This is not an all-green run or a repository FULL. Final ruff and git diff
--check pass; both old TF production adapters still have no diff from HEAD.

These actual results were sent to the existing authorized ChatGPT
conversation. Its completed TF6 reply was read in the same default Chrome
tab after transient partial UI output, then archived in
`stage12_b_mps_tf6_whole_qnode_received_prompt.md`. It requires moving next
to whole-QNode plan execution and shared admission, not further standalone
local-kernel test expansion. Receipt of that prompt is not TF6 completion.

TF6's first standalone red-baseline run has also completed:12 failed,
36 deselected,3.86s, exit1, receipt
`tmp/r2o3b-tf6-twelve-public-reds-main.xml`. All12 still terminate in the old
order2 graph-gradient refusal at tensorflow_graph.py44. Repository reference
inspection confirms no production caller selects TensorFlowLocalOperator;
its sole production reference is its own declaration. The old refusal and
all tests remain intact. Whole-QNode M1, unified-planning M2 and100-wire M3
are still unimplemented/partial, not substituted by the new local operator.

### TF6 M1: Actual Low-Qubit Whole-QNode Tensor Execution

Development checkpoint2026-10-24, local main HEAD b443430, no Git mutation.
`tensorflow_autodiff.py` now has a narrowly selected native whole-plan TF
tensor path. `tensorflow_graph.py` and its old typed refusal are unchanged.
The selection consumes the existing NativeHost/ExecutionPlan and lowered
Circuit, not a separately parsed or hardcoded quantum program. Capability
scanning is all-or-nothing before execution. It supports analytic expval
outputs with fixed finite real Pauli/Hamiltonian coefficients, static
float64 occurrence vectors, complex128 state tensors and exact native
StatevectorDevice, widths1 through4. Existing native lowering turns CX into
phase/CRX and H/X into elementary rotations; the specialization follows
those actual compiled primitives, including controlled rotations/phases.

The whole state carries the actual operation/wire ordering, noncontiguous
targets, symbolic expressions, local composite moving-projector fractional
powers, coherent open/closed controls, inverse/integer modifiers and global
phase. Full complex state and every real/imaginary J/H component compare
with four independent70-digit SU(2)/explicit-wire-map fixtures, including
the requested reversed noncommuting body and entangled four-qubit circuits.
Fixture regeneration completed with exact parsed JSON equality and asserts
no QuantumBridge/Qiskit/PennyLane/TF imports. Native Statevector comparisons
and removal/reordering tests additionally show execution follows the plan.

The new independent `tensorflow_native_derivatives.py` retains the live
pure-TF VJP, then computes streamed HVPs via ForwardAccumulator-over-Tape.
A genuine-third boundary is on the quantum second rule's point, not on
the cotangent/direction edges. Thus squared and exponential/cubic external
losses receive the complete real TF chain rule in FoR, RoF and TapeTape,
eager and traced, with two outputs and nontrivial weights. Tests patch host
quantum entry points and PyFunc/numpy_function to fail, and HVP tests forbid
GradientTape.jacobian. Complete J/H comparisons run separately. No complete
quantum Hessian, loss-specific derivative or detached trainable matrix is
injected. Genuine third derivatives still explicitly refuse.

Static shared admission in `derivative_planning.py` checks method/order,
width, measurements, inputs/outputs, native source expression bound,
postprocessing, combined local/state/AD workspace, work and tapes through
existing limits and Device guards. SDK-free tests prohibit even importing
TF/Qiskit/PennyLane and patch quantum execution entrances to fail. Exhausted
parent ledger and HigherOrder/Device budgets reject before TF allocation,
with zero consumed work/tapes/shots and unchanged source.

This is only a conservative native structural envelope. It is NOT measured
TF allocator RSS, arbitrary caller/loss graph accounting, or a shared
cumulative runtime ledger across cached graph calls. Active managed scopes
and QNode unified_limits explicitly refuse. Repeated valid/NaN-or-cut/valid
inputs reuse one concrete TF graph and actually check runtime parameters.
State/output finiteness guards reject poles or overflowing finite-weight
Hamiltonian results instead of returning supported NaN/Inf values.

The current selected methods are best/adjoint, with actual TF VJP/HVP
strategy reported in metadata. Explicit backprop remains unsupported;
moving-projector parameter-shift still has no fixed supported recipe.
Ordinary Pauli best/explicit-shift behavior is compared against the old
selector-disabled path and is unchanged. Trainable observable coefficients
are excluded from the new fixed-coefficient specialization and retain the
existing whole host path. max_diff=1 keeps the old first rule and second
refusal. The native order-two/true-third policy is NOT declared equal to
PennyLane public max_diff semantics.

External single-RY observations completed for both installed SDK versions:
PennyLane0.44.1 and0.42.3, each TF2.21.0/Python3.12.6,48 cases per runtime.
Each independently records28 matches,4 nonfinite,12 disconnected,1 mismatch
and3 exceptions. backprop at max_diff1/2 has correct first/second results but
NaN third results here; adjoint second/third is disconnected; parameter-shift
max_diff2 eager has a correct second result but traced orders1 through3
raise OperatorNotAllowedInGraphError. These are observed environmental API
behaviors, not general SDK mathematics claims or native tests. An initial
Main diagnostic computed nonfinite values but JSON allow_nan=False refused
serialization; it exited1 and was not accepted as a saved observation. The
script now records nonfinite values explicitly as strings and both saved
48-case JSON records are complete.

Completed evidence at this checkpoint (development, not frozen acceptance):

- Original low-qubit tests:12 passed15.59s, formerly4 passed/8 failed;
  `tmp/r2o3b-tf6-low-first-main.xml`.
- Initial new public mixed tests40 passed42.89s; additional order/runtime
  cases6 passed6.46s. These preceded later safety/finite-result checks.
- Initial whole execution/admission38-case run21 failed17 passed because
  tests assumed a dict PauliString constructor, missing lowered CRX support
  and a default compiler basis capable of preserving unresolved powers.
  Native CRX execution was added; tests use the actual native TF-preserving
  compiler basis, without weakening default/hardware compiler rejection.
  Corrected38 passed155.43s; receipt
  `tmp/r2o3b-tf6-whole-execution-main-fixed.xml`.
- Selection check initially1 failed5 passed because the test incorrectly
  assumed ordinary best always means shift. Existing analytic vector best
  may choose adjoint. The corrected old-path comparison7 passed3.00s;
  existing selection policy was not changed to satisfy that assumption.
- Main broad FOCUS241 passed/4 failed,18 warnings,297.86s, exit1;
  `tmp/r2o3b-tf6-main-regression.xml`.
- Alternate broad FOCUS248 passed/4 failed,18 warnings,302.19s, exit1;
  `tmp/r2o3b-tf6-alternate-regression.xml`. The seven-case count difference
  is later safety coverage, not a different failure classification.
- Both broad runs retain exactly the original four100-wire MPS TF FoR/RoF
  failures at unchanged tensorflow_graph.py44. Neither is all-green/FULL.
  Both preceded the final state/output finiteness guards.
- Final finite-output/pole cases3 passed3.09s;
  `tmp/r2o3b-tf6-nonfinite-main.xml`.
- Main combined low-qubit M1 suite107 passed225.01s, no skip/xfail;
  `tmp/r2o3b-tf6-m1-main-current.xml`. This includes the final finite guards
  but precedes the explicit live-observable-coefficient selector exclusion.
- SDK-free static admission24 passed0.33s;
  `tmp/r2o3b-tf6-sdkfree-admission-current.xml`.
- The new live-coefficient test initially used invalid public binding of a
  raw symbolic TF tensor and failed before execution. It now uses existing
  QNode.from_circuit recording rather than weakening public native binding;
  corrected1 passed3.07s before the extra analytic-value/gradient assertions.
- The SDK-free symbolic-power numerical example completed with current
  workspace PYTHONPATH, full-operator error2.30604301995351e-16 and HVP
  [-0.09937363572243615,-0.0031690688993985805], vector/density/MPS matching.

IR and QPY v13 restored executions use the existing Compiler, ParameterVector
root/element UUIDs, operation occurrences and unchanged source owners. Their
explicit TF-preserving native basis does not claim a hardware basis can
execute unresolved powered gates. Partial binding and two controlled states
are included. Unsupported methods/shapes/devices/noise/dynamics/transforms
do not silently become supported, and no100-wire dense fallback exists.

Milestones: M1 LOW_QUBIT_TF_WHOLE_QNODE_SUPPORTED_SUBSET has actual public
execution evidence; M2 Unified Planning remains PARTIAL (runtime shared TF
graph ledger not implemented); M3 Non-Dense100-Wire TF MPS remains
INCOMPLETE (original four red tests retained). No final three FULLs,
GLOBAL>=91.34108013033072%, unchanged68 exclusions, original28-section
matrix, all SDK-free examples, legal/frozen origins or staged/commit equality
is accepted from these development runs. Full independent native Qiskit/
PennyLane functional parity/full replacement remains ACTIVE / INCOMPLETE.

No push/fetch/stage/commit, auth/TLS change, dependency installation/vendor,
new cloud/hardware task, finance receipt modification, Studio/Router edit,
tag/release or historical rewrite. Existing preview server remains untouched.

The Alternate combined M1 suite subsequently completed107 passed230.98s,
no skips/xfails, receipt `tmp/r2o3b-tf6-m1-alternate-current.xml`. Like Main's
107-case collection, it did not include the subsequently added live-
coefficient regression. After the final selector exclusion and analytic
coefficient-value/gradient assertions, the eight selection/method/scope/
coefficient tests passed in BOTH Main3.50s and Alternate3.56s:
`tmp/r2o3b-tf6-selection-final-main.xml` and
`tmp/r2o3b-tf6-selection-final-alternate.xml`. No intervening quantum numeric
change. Final new-code ruff, shared-file F821 checks and git diff --check
pass. These overlapping suites are not added together as a unique FULL.

### TF6-M2: Eager Shared-Ledger Increment, Not M2 Completion

The final pre-M2 Main broad development run completed252 passed/4 failed,
18 warnings,306.80s, exit1, `tmp/r2o3b-tf6-main-current-broad.xml`. This
includes the final M1 guards and live-coefficient selector test; the four
failures are still the original100-wire TF FoR/RoF cases. It predates the
following M2 production changes and is not frozen/post-M2 acceptance.

M1 results were sent to the authorized existing ChatGPT conversation; its
actual full M2 reply was read after partial disconnected output and archived
in `stage12_b_mps_tf6_m2_received_prompt.md`. It explicitly requires M2 before
M3 and distinguishes static bounds, runtime assertions and controlled-call
ledger accounting. There are no actual classes named DerivativePlan or
SecondWork in this checkout: the existing ExecutionPlan and shared planning/
second_work functions provide those roles. No fake second planner was added.

The new eager managed path uses the EXISTING UnifiedResourceLedger and
ResourceScope. `unified_limits` may create a normal child ledger under the
active parent, or the path directly uses that active ledger. Primal, first
VJP and streamed second rules independently reserve the conservative
whole-plan workspace/work before their quantum tensor operations. Attempted
planned work is consumed before an attempt; completed logical tensor
evaluations are committed only on success. Error cleanup releases memory/
unspent reservations, not already spent attempted work. No physical shots,
Host quantum callback, native Device update or measured FLOP count is claimed.
TF output lifetimes/allocator/RSS are explicitly unavailable to the ledger.

Deferred eager derivatives retain the original request account even after
the original scope exits. An unrelated active scope cannot be silently
bypassed. Numeric admission values are privately captured before exposing
mutable metadata, so changing report dictionaries cannot lower a deferred
gradient's reservation. Parent/child accounting and concurrent actual QNode
requests share the existing ledger's RLock rather than a separate TF table.

A real concurrency test exposed duplicate local workspace admission under
an already reserved whole-plan workspace. `matrix_power_jet._admit` now
accepts explicit prepaid workspace bytes; existing native callers retain
the zero/default check. The TF scope passes its actual reservation amount
to the local kernel. No limit or mathematical tolerance was relaxed.

Finite cotangent/direction guards are real TF checks. A cached mixed graph
now explicitly tests valid value/gradient/HVP, NaN, Inf, branch cut, then
valid recovery with tracing_count1 and unchanged source. A direct previously
cached ConcreteFunction called outside the managed Python entrance does
NOT consume Python ledger work; metadata marks controlled_execution as
OUT_OF_SCOPE, and this limitation is tested, not disguised as actual work.
Managed graph construction/execution requests remain explicitly Unsupported.
There is no Python-side-effect, py_function or private-hook accounting.

Plan metadata includes a SHA256 of the native serialized circuit, actual
observables, method/max_diff, requested order and static resource settings.
Managed calls always reconstruct/revalidate their own native plan; no old
managed quantum cache is silently reused for a changed owner/configuration.
The logical per-evaluation charge conservatively uses the admitted maximum
second-order envelope, not measured allocator or exact arithmetic counts.
Complete general multi-direction/full-Hessian request accounting remains
open; external TensorFlow Hessian assembly is not claimed controlled.

Actual development evidence:

- Initial eager tests8 failed/1 passed3.73s; the first fixture accidentally
  selected an ordinary fixed-projector rotation. The corrected moving-
  projector domain still8 failed/1 passed3.32s at the old managed refusals.
- First integration6 passed/3 failed4.23s because tests supplied alphabetical
  phi/theta arguments in the opposite order. ParameterVector fixes the test
  identity order without changing production mathematics. Both runtimes
  then9 passed,4.34/4.36s.
- Strengthened concurrency runs14 passed/1 failed in both environments at
  the proven duplicate-workspace check; corrected15 passed5.07/5.12s.
- The eight-input streamed HVP initially correctly exhausted the DEFAULT
  cumulative50,000,000 work cap (requested58,491,840). Its test now explicitly
  supplies a1,000,000,000 logical work cap to isolate max_hessian_elements=1,
  while retaining zero/tight-budget tests and unchanged production defaults.
  Both runtimes17 passed6.33/6.37s with the corrected isolated budget.
- Two intermediate combined runs97 passed/1 failed68.98/69.15s had already
  collected the old default-cap test before that correction; not accepted
  as final green runs. An earlier combined95 passed/1 failed65.06s retained
  the duplicate-workspace failure. These receipts remain intact.
- Final current low-qubit/method/runtime/ledger/admission combined suites:
  Main99 passed71.30s; Alternate99 passed71.56s; no skips/xfails.
  `tmp/r2o3b-tf6-m2-low-final-main.xml` and
  `tmp/r2o3b-tf6-m2-low-final-alternate.xml`.
- Current SDK-free admission/directive protection38 passed0.56s;
  `tmp/r2o3b-tf6-m2-sdkfree-resource-current.xml`.
- Current SDK-free moving-power/MPS tangent/Frechet protection105 passed
  28.51s; `tmp/r2o3b-tf6-m2-native-protective-sdkfree.xml`.
- New cached mixed-runtime case1 passed4.57s, then included in final99.
  The final17 ledger cases plus this cache case are included in that99,
  not added again as unique tests. Current ruff/F821 and diff --check pass.

M1 remains a proven low-qubit subset. M2 remains PARTIAL: managed eager
support is real, but cached managed graphs still refuse, arbitrary direct
ConcreteFunctions cannot be cumulatively counted through Python scopes,
and complete multi-direction/full-Hessian/graph-construction ownership
contracts are not closed. M3 has NOT started. The original four MPS reds
and all R2 FULL/GLOBAL/matrix/legal/frozen-runtime gates remain open, not
substituted by these99-case suites. No source install/vendor, hardware,
Git mutation or Studio/Router/finance-evidence work was performed.

Final supplemental closure for this increment:

- Whole complex-state/J/H, actual Compiler/IR/QPY/partial-binding/source-
  mutation suite27 passed in Main171.19s and Alternate172.97s, no skip/xfail;
  `tmp/r2o3b-tf6-m2-whole-state-roundtrip-main.xml` and
  `tmp/r2o3b-tf6-m2-whole-state-roundtrip-alternate.xml`.
- A new SDK-free identity test exposed JSON serialization rejecting valid
  np.float32 device limits / np.int64 HigherOrder limits. The test first
  failed at identity serialization, then passed after explicit canonical
  numerical conversion, with no change to mathematical/resource limits.
  Current SDK-free whole/local admission25 passed0.34s, receipt
  `tmp/r2o3b-tf6-m2-identity-admission-sdkfree.xml`.
- Managed eager completion accounting now explicitly refuses asynchronous
  execution before quantum operations/reservations, rather than recording
  queued work as completed. Its focused test changes the queried sync-mode
  result, not the global TF execution mode, and verifies zero consumption.
- Final ledger/runtime/identity/resource33 passed in Main8.55s and
  Alternate8.62s; `tmp/r2o3b-tf6-m2-final-async-identity-main.xml` and
  `tmp/r2o3b-tf6-m2-final-async-identity-alternate.xml`. These contain18 older
  ledger/cache cases plus the new async case, and14 resource cases. They
  overlap the earlier99, so they are not33 additional unique tests.
- The99-case runs preceded the final identity scalar conversion and async
  guard; whole-state27 runs overlapped only these non-mathematical hardening
  edits. The final33 tests cover the changed behavior. No frozen FULL or
  post-M2 repository-wide pass is inferred from overlapping development runs.

This M2 eager checkpoint was sent to the authorized ChatGPT conversation.
Its completed TF6-M2B response was actually read and archived in
`stage12_b_mps_tf6_m2b_received_prompt.md`. It confirms only an eager managed
subset and requires next closing immutable derivative-request budgets and
an explicit owner-safe controlled cached-graph invocation handle, retaining
OUT_OF_SCOPE for arbitrary direct ConcreteFunction calls. It explicitly
forbids proceeding to M3 before M2 is truly accepted. Receipt is not M2B
implementation. Current full native replacement status stays ACTIVE /
INCOMPLETE, M2 PARTIAL, M3 NOT_STARTED. All required exec sessions ended;
final new-code ruff/shared F821/diff --check pass. No Git mutation.

## 2026-10-24 TF6-M2B Controlled Cached Requests Checkpoint

Owner order remains M1 -> M2 -> M3. M1 is a verified low-qubit subset;
M2 remains PARTIAL; M3 NOT_STARTED. Native full independent Qiskit/PennyLane
functional parity/full replacement is ACTIVE / INCOMPLETE. This increment
does not close the original R2 final gates or any100-wire TF MPS failure.

Implemented in this local increment:

- Extended the existing frozen DerivativeExecutionRequest with validated
  operation/order and immutable numerical descriptions: input/output,
  direction/cotangent counts, native parameter UUIDs, plan identity and
  resource limits. No new nominal DerivativePlan/SecondWork class.
- Existing derivative_planning now separates value0, gradient/JVP/VJP/J1,
  directional HVP2 and complete Hessian2 estimates. Complete Hessians check
  max_hessian_elements; streamed HVPs do not allocate that Hessian. Native
  Device scalar-gradient requests reuse the existing derivative execution.
- Added experimental QNode.compile_tensorflow managed handles for one
  explicitly shaped CPU float64 array input. Native Circuit/measurement
  mathematics are captured as an owned snapshot, with a scalar TF input
  mapping and native whole-state tensor execution. No SDK quantum execution,
  numeric quantum callback, complete-Hessian injection, stop_gradient or
  private JVP registration is used.
- Handles retain three controlled symbolic templates (value, VJP, streamed
  second rule) when order2 is approved. There is no dummy numeric warmup.
  Explicit shared queries build/reuse bounded value/gradient/J/JVP/VJP/HVP/
  Hessian graph specializations. Query results deliberately refuse further
  AD; the separate callable is the experimental composable-AD entrance.
- Each controlled synchronous call acquires the current normal native
  ledger or child, reserves before execution, records conservative attempted
  work and commits completed logical evaluations after CPU completion.
  Graph construction is separately charged without fictitious quantum tapes.
  Errors/cancellation release live reservations without refunding attempts.
- Input value guards execute in the cached graph on each call. Bad values
  recover without retracing; wrong signature, async/distributed execution,
  unbounded source mappings, nested/stateful mapping graphs and captured
  variables are refused in this bounded supported domain.
- Owner execution/resource configuration is checked for every request;
  source mathematical edits do not silently update a snapshot. Collected
  owners invalidate their handles. This closes a real tighten-limit-then-GC
  bypass exposed by a new failing test. Method/max_diff/limit changes require
  recompilation. Requests from another owner are rejected.
- Existing ResourceScope hierarchy and UnifiedResourceLedger locks account
  for parent/child/nested scopes, multiple nodes and competing threads.
  No TF private global account or second scheduler exists.

Accounting boundaries are explicit in returned metadata:

- Controlled synchronous CPU handle invocation: LEDGER_ACCOUNTED for known
  logical work. Explicit request counts/budgets match the requested operation.
- Callable opaque outer AD: approved-order conservative envelope, clearly
  labelled approved_callable_order_envelope. Successful primal execution
  records one completed evaluation, not every reserved envelope tape.
- Direct internal ConcreteFunction and external loss operations: OUT_OF_SCOPE.
- TF allocator/RSS and retained-output lifetimes: ESTIMATED_ONLY/unavailable,
  not observed exact bytes. Tensor/packing workspace is a conservative bound.
- Hardware shots, native host quantum callbacks and Device updates: zero in
  this pure-TF specialization, not fabricated simulator/cloud invocations.

Two real resource bugs were reproduced and fixed:

1. The original owner could be tightened then collected, erasing the live
   configuration check. The new regression first failed (DID NOT RAISE), then
   passed after expired-owner execution was explicitly refused.
2. The combined streamed second rule doubles work/workspace and adds a
   projected JVP. Its original aggregation did not recheck HigherOrder limits
   or device memory afterward. Four independent cases (memory, adjoint work,
   logical tapes, device memory) all first failed (DID NOT RAISE),13.86s.
   The post-aggregation guard now checks all four before graph construction.
   Receipt: tmp/r2o3b-tf6-m2b-second-rule-limits-red-main.xml.

Final focused evidence after that resource fix:

- Current budget-attribution30 + lifecycle21 + concurrency10:
  Main61 passed50.52s, Alternate61 passed50.82s, no skip/xfail.
  tmp/r2o3b-tf6-m2b-current-limits-scope-concurrency-main.xml and alternate.xml.
  These include exact/one-below caps, multiple directions/cotangents with
  actual numerical contractions, scalar gradient, order0/1/2 envelopes,
  genuine third-point refusal and async refusal before any work charge.
- Shared native request/Device broader SDK-free regression849 passed,
  25 skipped50.68s; skips are existing optional-dependency cases, not new
  correctness exclusions. tmp/r2o3b-tf6-m2b-native-contract-current.xml.
- Main whole-state/method/runtime/old eager-ledger/admission/contracts plus
  new cached formal suite187 passed /2 failed327.56s. Alternate old-protection
  suite172 passed228.67s; its cached/lifecycle/concurrency/attribution suite
  70 passed /2 failed142.46s. No skip/xfail in these TF suites.
  tmp/r2o3b-tf6-m2b-cached-old-low-current-main.xml,
  tmp/r2o3b-tf6-m2b-old-low-current-alternate.xml,
  tmp/r2o3b-tf6-m2b-managed-cached-current-alternate.xml.
  The long runs imported code before the final post-aggregation resource
  check; the subsequent61-case runs cover that final change. These are
  overlapping development receipts, not a frozen combined/FULL run.
- The original four100-wire TF FoR/RoF cases remain4 failed,32 deselected,
  3.59s, at the existing third-derivative refusal. They were rerun unchanged:
  tmp/r2o3b-tf6-m2b-original-mps-red-current-main.xml. M3 has not started.
- Initial managed API tests17 failed; initial shared-planner tests exposed
  request-variable shadowing, fixed by renaming the measurement loop variable.
  Trial init_scope construction pauses, inner bounded graph composition,
  packed inputs and retained tf.function objects did not close cached RoF.
  Ineffective init_scope/inner-wrapper experiments were removed. No tolerance
  was relaxed. Earlier red receipts remain separate and are not green proof.
- New attribution first run19 passed /5 failed14.19s had test mistakes:
  nonapplicable direction/cotangent descriptor counts are correctly zero;
  three assertions omitted receipt(). Those tests were corrected without
  changing production mathematics, and then strengthened with the four
  genuinely failing production-limit cases above.
- New code Ruff, shared-module F821 and git diff --check passed. No package
  install, vendor, OAuth/TLS edit, cloud task, Git mutation, tag or release.
  HEAD remains main b443430, ahead51 with user dirty files preserved.

Unresolved native correctness boundary, not hidden by the green subsets:

The two cached external nonlinear-loss RoF tests fail in both installed
TF2.21 runtimes. Square and exponential/cubic losses reach an InternalError
at reverse differentiation of a cached forward function (expected1 gradient,
received2). The other cached numerical queries, FoR and TapeTape tests pass.
Metadata and docstrings mark cached_outer_reverse_over_forward as
EXPERIMENTAL_NOT_ACCEPTED. The17-case cached suite is not claimed all green.

Independent public-TF probe:
tests/interfaces/probes/probe_tf_cached_mixed_boundary.py imports no
QuantumBridge/Qiskit/PennyLane. For real/complex functions, inline TapeTape is
only a cross-check; cubic references use elementary exact formulas:
linear-loss HVP=6*x*d; square-loss HVP=(30*x**4-3.6*x)*d. Both installed
runtimes give8 matches,3 RoF mismatches and1 disconnected linear-cubic RoF.
Main cubic linear expected[0.888,-1.476], actual disconnected. Cached real
square expected[4.129919275778119,3.828238731749991], RoF gives
[2.3178048482509492,1.7837073648599926]. Full records and actual TF import
origins are in probes/data/tf_cached_mixed_boundary_main.json and alternate.json.
This isolates a cached-function boundary even without quantum/ledger code;
it is not proof that every TF version has a universal upstream defect.

Next work must address that actual supported correctness boundary and the
remaining M2 acceptance contracts before M3. Original three-environment FULL,
independent four-framework, GLOBAL coverage >=91.34108013033072% with68
unchanged exclusions, original28-section matrix, all numerical examples,
controlled legal and frozen/staged/commit equality gates remain NOT_RUN on
this candidate. No full-replacement or final-release claim is justified.

This CONTROLLED-CACHE-61 checkpoint was sent to the authorized existing
ChatGPT conversation. Its completed full response was actually read and
archived at stage12_b_mps_tf6_m2c_received_prompt.md. It confirms M2 PARTIAL,
preserves both cached-RoF reds and the four MPS reds, and calls for a pure-TF
cached-inner / trace-inline / eager-inline boundary experiment before any
further native integration. The illustrative .value/.hvp names in its table
do not describe existing APIs: this implementation uses execute(request).
Receipt of this prompt is not implementation or acceptance of M2C.

### M2C Independent Boundary Experiment Only

Executed tests/interfaces/probes/probe_tf_trace_inline_boundary.py in both
already installed TF2.21 environments. It imports TF/NumPy only, not QB or
quantum SDKs. All scalar/vector/complex model values, J and H references
are elementary analytic formulas, independent of TensorFlow differentiation.
The18 paired model/loss/AD scenarios compare three execution boundaries,
each at two points using one static signature:

- Cached-inner model inside the outer traced AD function:24 observations
  match,12 RoF observations have finite incorrect HVPs.
- Ordinary callable emitting operations directly into the outer traced
  AD function:36 observations match all value/JVP/VJP/gradient/HVP fields.
- Eager-inline ordinary callable under actual AD containers:36 observations
  match those same analytic fields.

Both square and exponential/cubic losses are tested with correct separate
FoR, RoF and TapeTape nestings; mixed AD is evaluated before any numerical
first-derivative warmup. Public Graph/GraphDef inspection confirms no
inner_model FunctionDefs in the trace-inline route, with outer tracing_count1
after both input points. These are18 paired diagnostic scenarios, not108
independent passing pytest cases or full native acceptance tests. The cached
inner mismatches remain in the raw output, despite the diagnostic CLI exiting0.

Raw receipts:
tests/interfaces/probes/data/tf_trace_inline_boundary_main.json and
tf_trace_inline_boundary_alternate.json, including actual TF origins,
expected/actual arrays, disconnected/mismatched field names and graph metadata.
New probe Ruff and repository diff --check pass. No private gradient-registry
inspection/modification, new dependency, graph callback or quantum execution.

This proves a useful pure-TF boundary distinction on these installed builds,
not a QuantumBridge cached-callable fix. Native production dispatch remains
unchanged. Before native integration, the frozen native parameter-input map
must be emitted without reintroducing a cached classical/quantum function
boundary or rebuilding/copying a Circuit per invocation. Trace-inline external
cached graphs cannot inherit Python per-invocation ledger guarantees: active
scopes requiring them must refuse that separate mode. M2 PARTIAL and original
2 cached-native RoF +4 MPS failures remain open; M3 NOT_STARTED.

Native integration audit finds two concrete reuse issues for the next work:
the managed scalar mapper is itself a cached function, while calling its
python_function would rebuild a Tape/Circuit/kernel via QNode._construct;
the existing whole-plan state method also calls record_compiled_parameters,
which copies circuit operation structures. Neither is silently replaced or
claimed read-only per-invocation reuse. Existing immutable ParameterExpression
and its TF-aware scalar evaluator are candidate building blocks, not an
implemented generic captured-input AST. Public GraphDef import is untested
for live mixed AD and is not assumed correct. These actual source findings
and the TRACE-INLINE-PROBE-18 receipts were sent back to the same authorized
ChatGPT conversation for the next bounded native integration prompt.

The completed M2D response was then actually read in full, including its
final gates and conclusion, and archived as
stage12_b_mps_tf6_m2d_received_prompt.md. Next work is D1 frozen native scalar
binding, D2 read-only whole-plan trace-inline math, D3 resource/old-mode
isolation. It rejects relying on GraphDef import or reverse engineering a
cached TF graph, preserves the two cached-callable and four MPS reds, and
does not authorize M3 or close M2. None of D1/D2/D3 is claimed implemented
merely by receiving that prompt. All required exec sessions have terminated;
the local main HEAD and unrelated dirty files are unchanged.

## 2026-10-24 TF6-M2D Frozen Binding And Native Trace-Inline

Previous goal turn: concrete progress (controlled cached queries and paired
pure-TF boundary evidence). This continuation implements the next native
integration, not a restart or an assertion of complete SDK replacement.
Full independent native Qiskit/PennyLane functional parity/full replacement
remains ACTIVE / INCOMPLETE. M2 remains PARTIAL; M3 NOT_STARTED.

Implemented an explicit QNode.compile_tensorflow_inline entrance for one
static CPU float64 input array and actual native parameter identities.
This does not replace normal QNode invocation or managed cached queries.
The caller may use eager AD or trace AD containers together with the inline
math in an outer tf.function (tested autograph=False, jit_compile=False).

D1, frozen native scalar binding:

- Factored evaluate_compiled_parameter from the existing circuit-copying
  recorder. The same native scalar semantics are reused by compiler recording
  and opt-in read-only local/whole-state evaluation.
- FrozenParameterBinding stores ordered original UUIDs and immutable native
  scalar expressions, not another Circuit/operation store or TF graph parser.
  Native AST construction validates the bounded descriptor once. Same-name
  different-UUID inputs are refused, not merged; missing/surplus/duplicate
  identities, unbounded sequences and malformed syntax refuse explicitly.
- Supports the validated smooth scalar subset, including arithmetic, fixed
  bounded powers, sin/cos/exp and native global phase. Opaque foreign TF
  scalar functions, variable exponents and unvalidated nonsmooth/unary
  expressions remain unsupported in this entrance, not full scalar parity.
- The existing native storage pool owns the binding as well as source,
  observables and device; later vector resizing or source edits cannot
  silently change the snapshot's scalar/quantum mathematics.
- Native symbolic power inputs preserve an existing native power occurrence
  for runtime evaluation instead of deciding a principal phase numerically
  during symbolic construction. Numeric/framework paths are unchanged.

D2, actual native whole-QNode integration:

- TensorFlowLocalOperator and TensorFlowStatevectorPlan accept an opt-in
  read-only route that evaluates existing native ASTs directly. Defaults
  retain the old recorder path and dispatch; no new simulator/compiler.
- A snapshot is built once. Actual calls consume its compiled operations and
  observables, pack live scalar expressions, and emit existing local/whole
  TF operations. No inner cached trainable pack/quantum ConcreteFunction.
  Existing boolean validation functions/TF-generated AD FunctionDefs are
  permitted and are not misrepresented as absent.
- Tests forbid QNode._construct, record_compiled_parameters, Circuit.copy,
  Circuit.lowered, Circuit.assign_parameters and execution_copy after setup.
  Native Host/old GraphKernel, dense Gate fallback and py/numpy quantum
  callbacks are also patched to fail during actual inline execution.
- Independent70-digit SU(2)/basis-state references cover two different valid
  input points, two observables, nonlinear square and exponential/cubic
  losses, real FoR/RoF/TapeTape in eager and outer-traced execution, JVP/VJP,
  complete real/imag state J/H, and full expectation mixed Hessians.
- An entangling4-qubit source with trainable global phase survives native
  Compiler/IR/QPY lineage. Its complete complex state, J and full H are
  checked against the earlier independent fixture. H is checked on the raw
  native compiled source, J/value on raw/IR/QPY restored sources.
- An8-input streamed HVP matches the independent70-digit scalar reference
  while max_hessian_elements=1 and full QNode Hessian/TF Jacobian builders
  are patched to fail. It is not a secretly materialized complete Hessian.

D3, resource and ownership boundaries:

- Static capability/order/method/shape, AST work, combined workspace/work
  and native configured limits are checked before TF quantum math. The
  state view has an explicitly conservative extra output/work envelope.
- Original default limits are unchanged. The entangling full-state and
  eight-parameter mathematical tests explicitly supply1,000,000,000 work
  caps because their conservative full-state envelopes exceed the default
  50,000,000 cap. This is a test request budget, not a production cap change.
- Active managed ResourceScope refuses inline construction/invocation:
  tracing does not provide per-execution Python-ledger accounting.
- Python entry checks live owner existence and resource/method/max_diff
  configuration. Fingerprints include the actual compiled circuit, local
  source bodies, observable values, ordered UUIDs and binding AST. Snapshot
  mathematics are separate from these live execution/resource checks.
- A direct cached outer graph does not reenter Python: accounting and
  post-trace owner/config checks are OUT_OF_SCOPE. This limitation is tested
  directly, including tightened owner limits followed by a raw cached call
  that does not spend a Python ledger. No universal interception is claimed.
- NaN/Inf/branch-cut checks actually run on each cached graph execution,
  recover at a valid point, and do not force retracing. Wrong shape/dtype,
  owner expiry/tightening, plan edits, AST/resource errors and unsupported
  source mappings are refused. Genuine third and unapproved second orders
  are refused without confusing valid nonlinear-loss second derivatives.
- TF allocator/RSS, retained outputs and external loss graphs remain
  ESTIMATED_ONLY/unavailable/OUT_OF_SCOPE, not exact allocator guarantees.
- Mixed AD outside an already cached outer value graph is NOT_ACCEPTED.
  Correct inline AD must be eager or traced together with the emitted math.
  The old two managed cached-callable RoF tests remain unchanged and red.

Authoritative current evidence:

- Final new/native+resource combined: Main110 passed717.46s; Alternate110
  passed721.45s; no skip/xfail. Breakdown14 frozen binding +18 inline math
  +17 inline resource/ownership +30 existing attribution +21 existing scope
  +10 existing concurrency. The49 new tests are included in110, not added
  again. Receipts tmp/r2o3b-tf6-m2d-current-native-ledger-{main,alternate}.xml.
- Complete entangling-state Hessian is expensive in the current eager
  implementation. Both processes were observed actively executing nested
  TF gradient computation, not restarted on an observation timeout. The
  approximately12-minute combined runs include that test. Performance
  improvement remains work; a small-state specialization is not full parity.
- Current default protection, including old M1 mixed math, eager ledger,
  resource contracts, cached formal tests and Torch/Autograd/JAX/TF compiled/
  symbolic/moving/mixed-power cases: Main147 passed /2 failed179.42s;
  Alternate147 passed /2 failed179.00s, no skip/xfail. Only the unchanged
  square/exponential-cubic cached RoF cases fail with TF InternalError
  (expected1 gradient, received2). Receipts
  tmp/r2o3b-tf6-m2d-current-default-protection-{main,alternate}.xml.
- Current original100-wire TF cases:4 failed,32 deselected, Main4.08s and
  Alternate3.28s, still at the old third-derivative refusal. Receipts
  tmp/r2o3b-tf6-m2d-original-mps-red-{main,alternate}.xml. M3 has not started.
- SDK-free native gradients/scalars/frozen binding348 passed46.51s, no skip;
  tmp/r2o3b-tf6-m2d-native-gradient-sdkfree.xml. Earlier overlapping symbolic/
  binding protection92 passed4.60s; not92 additional unique tests.
- New/shared code Ruff, shared-module F821 and git diff --check pass.
  No Git mutation; HEAD main b443430, ahead51; user dirty files preserved.

Development evidence is retained, not silently converted to green:

- Initial26 failures2.84s were missing native APIs/descriptors. First
  integration14 passed/12 failed3.29s exposed symbolic power input handling;
  next14 passed/12 failed5.24s exposed a missing TF reshape adapter in output
  reconstruction. Corrected mixed cases12 passed14.38s.
- Initial resource14 passed3.16s. Supplemental4 failed/1 passed5.04s included
  the two legitimate default-budget refusals, a test using Circuit.data
  instead of QuantumCircuit.data, and foreign TF mapping raising an unclear
  conversion ValueError. The entrance now gives a typed unsupported-source
  error while preserving symbolic resource exceptions.
- The next supplemental5 passed/1 failed9.63s found test code incorrectly
  chaining QuantumCircuit.append (it returns InstructionSet). The test was
  corrected, not the existing public append ABI.
- Intermediate planned-final runs210 passed/6 failed267.49/267.64s had already
  imported those four old tests before the corrections, plus the two original
  cached-RoF reds. Their filenames contain final-focused but they are NOT
  final accepted evidence. The later110 and147/2 receipts supersede them.

No dependency installation, vendor, private gradient registry, stop-gradient,
complete-Hessian/SDK injection, GraphDef import shortcut, cloud task, token,
OAuth/TLS change, financial evidence edit, Studio/Router work, tag or release.
Source port count remains zero; legal/source ledger updated. All exec sessions
used for this checkpoint reached terminal status.

Remaining: M2 method/mode/resource acceptance is not declared closed. The
two cached-callable reds, arbitrary foreign TF scalar capture and unsupported
external cached-value AD boundaries remain explicit; MPS4 remains open. The
original three-environment FULL, independent four-framework full validation,
GLOBAL>=91.34108013033072% with68 exclusions unchanged, original28-section
matrix, all SDK-free examples, controlled legal/import-origins and frozen/
staged/commit equality gates remain NOT_RUN on this candidate. No M2 subset
or110-test result establishes full native SDK replacement.

The NATIVE-INLINE-110 checkpoint was sent to the authorized existing ChatGPT
conversation. Its full completed M2E response was actually read and archived
at stage12_b_mps_tf6_m2e_received_prompt.md. It recognizes only the reported
development-time low-qubit supported subset, not independent source review,
M2 completion or full SDK parity. Next priority is a read-only capability/
method contract separating MANAGED_EXPLICIT_QUERY, TRACE_INLINE_DIFFERENTIABLE
and EXPERIMENTAL_CACHED_CALLABLE; typed refusal at identifiable unsupported
controlled entrances; then request/lifecycle/performance audits. Original
two cached-RoF assertions must remain unchanged and failing until genuinely
fixed. M3 must not start merely from these green subsets. Receipt of the
prompt does not mean capability isolation or M2E is implemented. Full goal
remains ACTIVE / INCOMPLETE, M2 PARTIAL, M3 NOT_STARTED.

### TF6-M2E: Capability Isolation, Request Sequences And Performance

Local-only continuation on2026-10-24. Full independent native Qiskit/PennyLane
functional replacement remains ACTIVE / INCOMPLETE. M2 remains PARTIAL;
M3 NOT_STARTED. No new SDK stage or all-TensorFlow acceptance is declared.

Capability isolation and actual behavior:

- Added immutable per-handle contracts using the existing ExecutionPlan
  method selector and DerivativeExecutionRequest, not a global registry or
  ecosystem inventory level. Supported method names remain best/adjoint for
  these explicitly compiled handles; ordinary Gate parameter-shift dispatch
  is unchanged. Scalar gradient is not advertised for a multi-output plan.
- MANAGED_EXPLICIT_QUERY retains value, scalar gradient, Jacobian, JVP/VJP,
  streamed single/multiple-direction HVP and full Hessian within its approved
  order. It is a synchronous controlled query, not an external AD output.
  Actual native work/cache construction is charged to the shared ledger;
  request/scope limits, concurrency and live owner guards remain active.
- TRACE_INLINE_DIFFERENTIABLE advertises the validated one-through-four-qubit
  dense native subset with frozen scalar syntax, eager or co-traced mixed
  AD. It has SNAPSHOT_MATH, LIVE_GUARD_AT_CONTROLLED_ENTRY and runtime TF
  assertions, not per-external-graph ledger accounting. Direct cached outer
  graph execution does not reenter Python owner checks. Independently
  differentiating an already cached outer value graph is NOT_ACCEPTED.
- EXPERIMENTAL_CACHED_CALLABLE has a configured diagnostic envelope, but at
  most verified order one. Its declared order-two contract is refused before
  tensor execution. It is not automatically selected by best/default QNode
  dispatch. The new differentiable_call checks the declared first-order
  contract; bare legacy handle calls remain explicitly diagnostic. Arbitrary
  implicit external AD is UNGUARANTEED_EXTERNAL_AD, not universally trapped.
- The capability predicate only checks the declared static contract and live
  owner, not numerical finiteness or remaining execution credits. Read-only
  metadata cannot be upgraded by editing returned serializable result copies.
  Inline per-request shots/seed/observable/limits overrides are refused,
  rather than silently ignored; recompile or use a supported managed query.
- No production/full-parity claim follows from this label. The original two
  cached nonlinear-RoF assertions are untouched. Opaque external calls can
  still fail, disconnect or return wrong finite derivatives; no blanket safe
  rejection claim is made. No declared supported second-order cached
  callable path is introduced.

First-order defect exposed and fixed during contract testing:

- A genuine first ForwardAccumulator JVP was incorrectly refused by the old
  order-one boundary. Its custom VJP transposition differentiated the
  cotangent, not the quantum point. The initial native test failed in9.53s
  (tmp/r2o3b-tf6-m2e-first-order-forward-main.xml).
- The independent public-TF-only cubic probe separates a point identity
  guard from cotangent transposition. Both environments match analytic first
  gradient/JVP; genuine point FoR/Tape second requests refuse. Cached RoF
  disconnects: that is negative evidence, not a safe-rejection success.
- The native max_order=1 branch now uses that separation. Checked native
  first JVP/weighted VJP and inline eager/co-traced first JVP work. No
  stop-gradient, private hook, host-computed derivatives or derivative-order
  relaxation. Existing configured order-two mathematics is unchanged.

Request and lifecycle evidence includes value -> gradient -> HVP -> value
-> gradient; valid -> NaN -> valid; graph-construction RuntimeError and
KeyboardInterrupt; spent work is retained, completed tapes are not fabricated,
reservations release, later valid queries recover. Repeated queries charge
missing graph construction only once. Tests assert no physical shots, Host
quantum calls or Device updates. Existing ownership/scope/concurrency tests
cover source/gate/observable mutation, configuration tightening, handle aliases,
active/exited scopes and shared concurrent budgets. ParameterVector shrink/
regrow preserves frozen mathematics. Trainable observable coefficients and
general two-wire powered bodies cannot silently acquire inline capability.

Performance diagnostic, no optimization claim:

`scripts/probe_tf_inline_performance.py` uses four actual native frozen plans
and our existing independent numerical fixtures. Each case runs in its own
process; timing collection overlapped other local regressions, so these are
diagnostic observations, not isolated comparative benchmarks. Eight JSON
records are in tests/interfaces/probes/data/tf_inline_performance_*_{main,
alternate}.json. All measured outputs agree within9e-16; all traced functions
trace once, with no PyFunc/PyFuncStateless/EagerPyFunc nodes. TF-generated AD
FunctionDefs are counted, not incorrectly described as absent.

Main timings below: creation/eager value in milliseconds; first AD trace and
call in seconds; subsequent cached medians in milliseconds. Each AD triplet
is FoR / RoF / TapeTape. Full raw timings/graphs for both environments remain
in the JSON, including value trace/cached calls.

| Actual plan | Create / eager value ms | First AD trace s | Cached AD ms |
| --- | --- | --- | --- |
| 1q noncommuting root, Z | 24.15 / 73.60 | 1.884 / 1.267 / 1.406 | 1.503 / 1.231 / 1.245 |
| 1q same root, two outputs | 23.21 / 73.51 | 1.948 / 1.345 / 1.495 | 1.576 / 1.430 / 1.575 |
| 4q entangling, two outputs | 22.66 / 85.50 | 3.521 / 2.321 / 2.647 | 2.105 / 1.655 / 1.808 |
| 8 parameters, streamed HVP | 47.63 / 81.42 | 5.094 / 2.959 / 3.889 | 4.338 / 2.688 / 2.697 |

Top-level graph nodes / FunctionDefs, value; FoR; RoF; TapeTape respectively:
1qZ311/5;3504/116;3017/194;3931/96.
Two-output341/4;3767/106;3242/183;4211/92.
4q875/5;8367/126;6868/212;8383/110.
8p945/4;10878/104;6824/171;9784/95.
Alternate has matching structural counts, similar timing order and no claimed
cross-environment speedup. Static fingerprint work was0.55-1.08ms/entry;
there is no evidence here that caching its result resolves the much slower
complete-state Hessian regression, so no mathematical path/cache optimization
was made. Input-dependent tensors are never cached by this probe.

TensorFlow CPU allocator observations are unavailable in both installations
(ValueError: Allocator stats not available for device CPU:0). Observed
per-operation peak workspace is null, not inferred from a static bound.
Static plan workspace estimates543008/283936/13496448/648224 bytes are not
observed allocator peaks. Raw cumulative process RSS is separately labeled.
Retained Tensor payloads16/16/16/64 bytes become Python-collectable after
release in all cases; this is not proof of backend allocator release. The
4q probe measures directional output HVP, not the complete real/imag state
Hessian. Prior M2D per-test XML attributed601.392s to the complete-state/format
test; that expensive path remains covered in the current combined rerun.

Verified development results on the current numerical implementation:

- Combined M2D110 plus the initial32 M2E contracts/sequences: Main142 passed
  777.88s; Alternate142 passed772.84s. No skip/xfail. Includes complete
  complex-state Hessian, two independent points, two losses and all61
  attribution/scope/concurrency protections. Receipts
  tmp/r2o3b-tf6-m2e-current-inline-contracts-{main,alternate}.xml.
  Four subsequently added safety tests ran separately and are included in
  the final36-contract suite below. Only a query-refusal doc/error message
  changed after the combined run started; no numerical path was changed.
- Final current contracts/sequences: Main36 passed33.83s; Alternate36 passed
  33.84s, no skips/xfails. Includes all32 earlier cases plus the four actual
  max_diff=1 point-refusal checks. Receipts
  tmp/r2o3b-tf6-m2e-current-contracts-{main,alternate}.xml. Earlier overlapping
  contract and targeted counts below are not additional unique green tests.
- New contracts/sequences Alternate32 passed23.69s. Includes the new first
  JVP fix and four inline request override refusals. Early Main28 passed
  before adding those four tests; do not count it as32.
- Additional actual max_diff=1 owner checks: Main/Alternate each4 passed
  22 deselected8.88s. Checked cached first-order and inline handles refuse
  genuine point FoR/Tape second requests, not merely their declared metadata.
  tmp/r2o3b-tf6-m2e-actual-order-one-refusal-{main,alternate}.xml. Bare unknown
  cached external RoF remains unguaranteed; these refusals do not fix it.
- Original low-qubit M1 twelve cases plus twelve native Compiler/IR/QPY
  restored-HVP cases: Main24 passed15 deselected41.74s; Alternate24 passed
  15 deselected41.86s. No Host/full-Hessian fallback in format tests.
  tmp/r2o3b-tf6-m2e-m1-original-and-formats-{main,alternate}.xml.
- Current default/M1-mixed/ledger/four-framework subset Main147 passed /
  2 failed194.07s; Alternate147 passed /2 failed194.14s. Only the two unchanged
  square/exponential-cubic cached-RoF cases fail with TF InternalError
  (expected1 gradient, received2). Receipts
  tmp/r2o3b-tf6-m2e-current-default-protection-{main,alternate}.xml.
- Original MPS mixed graphs Main4 failed32 deselected4.46s; Alternate4 failed
  32 deselected4.18s. Same old third-derivative refusal, not fixed or xfailed.
  Correct receipts: tmp/r2o3b-tf6-m2e-original-mps-mixed-red-{main,alternate}.xml.
  An earlier selection named original-mps-red actually selected six other
  already-passing MPS tests (6 passed30 deselected each), NOT these four reds.
- Strict isolated SDK-free subset247 passed27.63s, no skips/xfails.
  PYTHONNOUSERSITE=1, Python -s, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1; pre-run
  import specs for Qiskit/PennyLane/TensorFlow/JAX are all absent and post-run
  forbidden imports are empty. Receipt
  tmp/r2o3b-tf6-m2e-native-admission-isolated-sdkfree.xml. The native symbolic
  numerical example also succeeds under these exact isolation settings;
  post-example forbidden imports are empty, complete complex-operator error
  2.31e-16, streamed HVP works with full-Hessian limit one.
- Provenance correction: /private/tmp/qb-core-ci-20261019/bin/python is
  currently a base-Python alias, not an isolated venv (pyvenv.cfg absent).
  Without -s it sees user-site Qiskit/PennyLane. Initial229+18 runs therefore
  are not strict SDK-free evidence; the isolated247 rerun supersedes them.
  Prior reports' SDK-free counts are not reattested by the executable's name.

Initial missing-capability red15 failures4.97s, first implementation15 passed
6.19s, native first-JVP red and corrected11-test targeted Main/Alternate runs
remain preserved as development evidence, not extra unique accepted tests.
The first SDK-free command referenced a nonexistent test_resource_budget.py
and collected no tests; it was corrected, not counted as a test failure.

New-module Ruff, shared-module F821 and git diff --check pass. A broad Ruff
check also encounters10 existing E701 one-line statements in the shared
derivative planner outside this increment; they were not unrelatedly rewritten.
No stage/commit/push/fetch, OAuth/TLS change, install/vendor, private registry,
cloud task, token, financial receipt edit, UI/Studio/Router work, tag/release.
HEAD main b443430 ahead51; dirty user work preserved. Source port count zero.

Current three-environment FULL, independent four-framework FULL, GLOBAL line
coverage>=91.34108013033072% with68 exclusions unchanged, original28-section
matrix, all SDK-free examples, controlled legal/import-origin gate and
frozen/worktree/staged/commit runtime equality remain NOT_RUN. The tests above
do not satisfy those final gates or whole-SDK replacement. Missing broad
Circuit/control-flow/transpiler/Primitives/backend/serialization/Aer/industry
APIs and full PennyLane operations/devices/transforms/measurements/gradient/
qchem/plugin interfaces remain implementation work, not parity-complete.

M2E implementation/measurement checkpoint: capability isolation is effective
at the controlled declared entrances, not a global AD safety mechanism.
Shared explicit queries and the verified inline subset remain distinct.
The unchanged two cached-RoF failures and four MPS failures are still open;
no M3 implementation was started. All execution sessions for this checkpoint
reached terminal status. The completed CAPABILITY-CONTRACT-142 result was
sent to the existing authorized ChatGPT conversation. Its full completed
M2F response was actually read, including the ending, and archived at
stage12_b_mps_tf6_m2f_received_prompt.md. It accepts only the reported
development subset, not an independent source/CI review. M2 remains PARTIAL,
M3 NOT_STARTED. Next is an actual public-entrance/default-selector safety
audit, comprehensive request-sequence/resource counterexamples, and a
test-receipt-backed supported-contract artifact. This receipt does not mean
M2F is implemented or that the original cached-RoF mathematical failures are
fixed. The prompt's combined allocator/RSS shorthand does not change the
actual unavailable-workspace versus observed raw-process-RSS distinction.

### TF6-M2F: Request Integrity And Newly Exposed Default Jacobian Gap

Local-only work on2026-10-24. Prior M2E was concrete implementation/test
progress, not a wait or completion of the full objective. This continuation
fixes actual explicit-query/plan-integrity defects and exposes a further
default-interface failure. M2F and M2 remain PARTIAL; M3 NOT_STARTED. The
original full independent native SDK replacement objective is unchanged.

Real fixes, from failing counterexamples:

- The initial safety suite had16 failures/1 pass10.97s
  (tmp/r2o3b-tf6-m2f-request-integrity-red-main.xml). Contract predicates
  incorrectly accepted missing JVP/HVP tangents, missing VJP cotangents,
  empty batches and irrelevant tangent/cotangent fields. Some execution
  paths silently ignored those fields. They now share _query_seeds for
  declared explicit-query admission, estimation and execution. Applicable
  bounded float64 seeds and positive counts are validated before quantum
  invocation; invalid requests consume no derivative work. Inline remains a
  declared AD contract, not an implicit execute(request) API.
- The managed guard previously compared only a reconstructed parent plan's
  work identity. It missed changes to the actual retained local-body or
  observable store. TensorFlowStatevectorPlan.fingerprint now covers the
  executed circuit, parameter UUIDs, local bodies/bindings/modifiers/control
  states, fixed matrix bytes and structured observable coefficients. Both
  inline and managed guards reuse this descriptor. No second math store is
  created, no input-dependent TF tensor is cached, and no repr-only identity
  is used for observables.
- Managed compiled identity additionally includes the native resource-plan
  identity and a one-time hash of the already-admitted scalar GraphDef
  bytes. This is provenance hashing, not graph reverse-parsing/import or
  mathematical reconstruction. The scalar callable reference is guarded;
  direct external cached graphs still do not reenter Python. This is not
  a hostile Python-introspection security boundary.
- Remaining query-autodiff metadata now explicitly distinguishes checked
  first-order differentiable_call from the separately verified inline
  second-order subset. No implicit/default experimental selection was added.

Actual test-generated request-chain evidence:

`test_native_tf_m2_query_lifecycle.py` writes JSON only after all its numerical
and ownership assertions succeed. Current records are
tmp/r2o3b-tf6-m2f-query-evidence-{main,alternate}.json, each tied to the test
ID, installed TF origin and SHA256 of seven relevant source/test files.
Those hashes were rechecked against the current files after withdrawing
the rejected callback experiments. Both environments record the following
same-plan sequence; each operation is a real controlled query, not inventory.

| Request | Direction / cotangent count | Actual logical work delta |
| --- | --- | --- |
| value | 0 / 0 | 18 |
| scalar gradient | 0 / 1 | 569 |
| JVP | 1 / 0 | 569 |
| VJP | 0 / 1 | 108 |
| HVP | 1 / 1 | 1145 |
| multi-direction HVP | 2 / 1 | 1913 |
| full Hessian | 2 / 1 | 1913 |
| repeated gradient | 0 / 1 | 108 |
| repeated value | 0 / 0 | 18 |

Each child result delta equals its prior estimate and the parent delta once,
not twice. Cumulative parent work6361, completed evaluations11; reservations
release to zero. Actual Host quantum calls / Device updates / physical shots
are zero. Exact scalar RY(p*p+q) value/Jacobian/Hessian references validate
all outputs, including cotangent weighting and both HVP directions. The
second test forbids complete-Hessian/Jacobian entrances, runs multi-direction
HVP under max_hessian_elements=1 and requires a full Hessian to refuse.
Receipts tmp/r2o3b-tf6-m2f-current-query-chain-{main,alternate}.xml:
Main2 passed5.18s, Alternate2 passed5.23s, process exit0 each.

Public entrance capability matrix, based on actual completed tests:

| Actual entrance | State / derivative boundary | Resource boundary | Execution evidence |
| --- | --- | --- | --- |
| managed.execute(request) | VERIFIED_SUPPORTED_SUBSET: value/gradient/Jacobian/JVP/VJP/HVP/Hessian, best/adjoint, approved order0..2 | Shared managed ledger, request/owner/scope guards; logical envelopes, not observed allocator work | query-lifecycle2 plus current combined163; exit0 |
| compile_tensorflow_inline handle, eager/co-traced AD | VERIFIED_SUPPORTED_SUBSET: native low-qubit frozen AST/operation subset through order2; two points, two losses | Static bound + runtime TF assertions; live owner at Python entry only | trace-inline18 + inline-resource17 within combined163; exit0 |
| managed.differentiable_call with declared order1 | Verified first-JVP/VJP subset inside EXPERIMENTAL_UNVERIFIED cached mode; declared order2 UNSUPPORTED | Controlled invocation ledger, not arbitrary outer loss/scheduler accounting | execution-capabilities26 within combined163; exit0 |
| bare managed callable + external nonlinear RoF | KNOWN_FAILING: squared and exp/cubic loss; not a supported second-order API | UNGUARANTEED_EXTERNAL_AD; error is not SAFE_REJECTION | original-cached-rof-red2 each; exit1 |
| raw/user-cached ConcreteFunction | No general AD/configuration promise | OUT_OF_SCOPE_RESOURCE_ACCOUNTING; no Python reentry guarantee | scope-lifecycle raw-graph test within combined163; exit0 validates the boundary, not global support |
| default eager QNode + automatic pfor Jacobian | KNOWN_FAILING: ordinary/Generic/Controlled/fixed-projector/multi-output host path | No new ledger promise or automatic experimental fallback | default-native-pfor-open32:12 pass/20 fail each; exit1 |
| ordinary eager QNode + non-vectorized Jacobian/Hessian | VERIFIED_SUPPORTED_SUBSET for the tested analytic model and best/adjoint/shift | Existing native host contract; no arbitrary cached graph ledger | eager-jacobian-reentry three pfor=False cases; pass inside the red suite |
| native simulator backprop | UNSUPPORTED, not advertised as implemented | Refuses before native quantum work | six explicit backprop counterexamples; pass inside default red suite |
| compiled-handle trainable observable coefficients / general multi-wire power body | UNSUPPORTED here, not silently frozen | Static typed admission refusal | query-contract-sequences tests within combined163; exit0 |

The table references complete passing cases or explicit negative cases, not
partial assertions used to hide a failed test. Native default QNode backprop
is still a full-replacement gap. Trainable-coefficient support in the separate
existing host path is not thereby removed or claimed as inline support.
Every managed/inline second-order declaration is limited to its actual tested
native domain, not inferred just from max_diff=2.

Newly exposed eager/pfor correctness gap, not hidden as a supported subset:

- Expanded default-dispatch tests cover ordinary rotation, GenericGate,
  ControlledGate, fixed-projector power, moving-projector power and multiple
  outputs, with best/adjoint/parameter-shift and explicit backprop refusals.
  Ordinary shift VJP retains its two shifted evaluations. These tests found
  that GradientTape.jacobian's automatic tracing after an eager host forward
  enters a VJP that still reads SymbolicTensor.numpy(), raising AttributeError.
  This existed before the retained M2F query fixes; it is now a formal failure.
- Current tests/interfaces/test_native_tf_default_capability_selection.py:
  9 passed /15 failed. Current eager-jacobian-reentry.py:3 passed /5 failed.
  The additional scope/max_diff tests fail at the missing first-Jacobian
  integration, before proving their intended higher-order assertion. Their
  failure is not counted as a safety refusal.
- Combined current results: Main12 passed /20 failed6.20s; Alternate12 passed
  /20 failed6.18s; process exit1. Receipts
  tmp/r2o3b-tf6-m2f-default-native-pfor-open-{main,alternate}.xml. No skip/xfail
  and no mathematical assertion was removed to make the suite green.
- A proposed reuse of the existing graph callback made first Jacobians pass
  (24 passed7.38/7.30s), but complete Hessian tests exposed wrong finite
  results missing quantum second terms, and max_diff=1 lost a refusal.
  A direct existing-graph-op variant also failed. A public py_function
  variant then triggered TensorList/variant vectorizer errors. Those were
  rejected experiments, not accepted results; all attempted changes to this
  eager/pfor path were withdrawn from tensorflow_autodiff.py. Existing M1
  whole-plan/default behavior and the original cached-RoF tests are preserved.
  Rejected receipts remain m2f-eager-pfor-{first,direct,public-callback}-main.xml
  and m2f-default-selection-pfor-fix-{main,alternate}.xml, NOT final green evidence.

Independent isolation evidence:

`probes/probe_tf_eager_jacobian_boundary.py` imports only public TF and NumPy,
not QuantumBridge/Qiskit/PennyLane. It checks two analytic sin/cos points,
classical map p*p+q, pure-TF control and NumPy/eager callback VJP transports,
with and without pfor. Both actual TF2.21 installations produce8 matches,
2 finite mismatches and2 errors across12 scenarios. The four pure-TF cases
match. Both non-vectorized callback variants match; their pfor variants fail.
JSON: probes/data/tf_eager_jacobian_boundary_{main,alternate}.json. Exit0 means
diagnostic collection completed, NOT twelve mathematical passes.

Reading the installed vectorizer showed it recreates IdentityN nodes; loss
of custom gradient metadata there is a hypothesis, not a proven upstream
root cause or a reason to patch private TF internals. The official
[custom-gradient documentation](https://www.tensorflow.org/api_docs/python/tf/custom_gradient)
also warns that nested callbacks alone do not establish higher-order input
derivatives. No upstream implementation or test source was incorporated.

Performance work remains measurement, not an unverified optimization. The
eight existing M2E JSON records show static fingerprint cost small relative
to complete complex-state Hessians; they do not measure the new, more complete
M2F fingerprint. No speedup claim, input-dependent tensor cache, scalar-constant
substitution or old cached-inner fallback is made.

Completed developer regressions, not FULL gates:

- M2E146 distinct existing cases plus17 new request/integrity cases: Main163
  passed748.17s; Alternate163 passed752.28s; exit0, no skip/xfail. Includes
  all original142 and all final36 (32 overlap), complete complex-state
  Hessian, native transforms/formats, scopes, budgets and concurrency. The
  main mathematical changes were already loaded in these runs; the temporary
  pfor transport experiments were later withdrawn to exactly the previous
  default module contents. These163 do not include the20 new pfor failures.
- Strict isolated SDK-free subset247 passed26.56s; exit0, pre-run forbidden
  import specs absent and post-run imports empty. PYTHONNOUSERSITE=1,
  Python -s and PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 are explicit, not inferred
  from an environment directory name. Numerical example passes under the
  same isolation, forbidden imports empty, operator error2.31e-16. Receipt
  tmp/r2o3b-tf6-m2f-native-admission-isolated-sdkfree.xml.
- Current broader M1/mixed/ledger/four-framework/formats protection: Main174
  passed /2 failed /12 deselected214.75s; Alternate174 passed /2 failed /
  12 deselected215.01s; exit1 because the unchanged cached-RoF failures
  remain. Includes original M1 twelve and Compiler/IR/QPY restored HVP twelve.
  Complete-state and partial-binding cases in that older whole-plan file
  were not selected by this development command; current complete-state
  math is separately covered by163 above. Receipts
  tmp/r2o3b-tf6-m2f-current-default-protection-{main,alternate}.xml. This is
  a selected developer regression, not a full interface acceptance gate.
- Original cached-RoF first runs still2 failed15 deselected each,32.01/32.22s;
  original MPS mixed-mode graphs still4 failed32 deselected each,3.84/3.83s.
  Only actual failed tests are counted; no xfail/replacement.

No stage/commit/push/fetch, OAuth/TLS changes, installs/vendor, credentials,
cloud tasks, financial13 receipts, UI/Studio, Router files, tags or release.
HEAD main b443430 ahead51; dirty user changes preserved. New-code Ruff,
shared-module F821 and git diff --check pass. Source port count remains zero.

M2F acceptance is NOT achieved: the broader default Jacobian audit exposed
20 formal integration failures beyond the2 cached-RoF and4 MPS failures.
The exact default eager/pfor boundary must be repaired and numerically
validated without importing wrong finite Hessian behavior from a callback
adapter. This is concrete next implementation work, not an external blocker.
M2 remains PARTIAL; no M3 recommendation or implementation. All original R2
three-environment FULL / independent four-framework FULL / GLOBAL line
coverage>=91.34108013033072% with68 exclusions unchanged / original28-section
matrix / all SDK-free examples / controlled legal / actual import origins /
frozen/worktree/staged/commit equality remain NOT_RUN on this candidate.
Broad Circuit/transpiler/Primitives/backends/formats/Aer/industry and PennyLane
operations/devices/measurements/transforms/gradients/qchem/plugins still lack
full API-by-API native parity verification; these focused tests cannot prove
the original requested full functional replacement.

The complete M2F-REQUEST-INTEGRITY-163-PFOR-OPEN report was sent to the
authorized existing ChatGPT conversation. Its full completed M2G response,
including the ending, was actually read and archived at
stage12_b_mps_tf6_m2g_received_prompt.md. It recognizes the new20 default
eager-Jacobian/pfor failures as real implementation work, not an accepted
M2F/M2 checkpoint or a reason to enter M3. Next work must prove callback-free
native whole-plan pfor/Jacobian and full second-order mathematics, then
select it through the existing method/operation/resource system without
changing ordinary shift semantics, inventing a second circuit store, or
calling serial pfor=False a final repair. New20 / cached-RoF2 / MPS4 must
remain separately reported. No next-stage implementation is implied by
receiving the prompt. Full native SDK goal remains ACTIVE / INCOMPLETE.

### TF6-M2G: Native Default Eager Pfor And Quantum Curvature

Local-only continuation on2026-10-24. M2G/M2 remain PARTIAL; M3 is
NOT_STARTED. Full independent native Qiskit/PennyLane functional replacement
remains ACTIVE / INCOMPLETE. This section supersedes the M2F *current*
default-pfor failure status, not its retained negative experimental evidence.

Implementation and boundaries:

- The ordinary eager forward and direct eager VJP keep their existing native
  methods. When TF automatically traces an eager backward, the existing
  method/capability planner may select the same lowered native plan and
  readonly whole-plan TF operations. No compiled experimental handle, second
  circuit store, per-operation hybrid, private TF hook or quantum callback
  is introduced in that traced derivative.
- First quantum Jacobians are independent of incoming cotangents. The next
  custom edge differentiates that actual Jacobian before contracting seeds,
  preserving both quantum curvature and outer nonlinear loss terms. This
  fixes the finite-but-wrong Hessians exposed by the rejected M2F adapters.
  Ordinary parameter-shift uses its actual native recipes, including control
  frequencies, not an operation-name heuristic or a backprop relabeling.
  Nested derivatives use TF reverse math on those shifted evaluations.
- Selection is bounded to the admitted static analytic StatevectorDevice
  whole-plan domain,1-4 qubits, real float64 inputs/complex128 state, fixed
  real observable coefficients and approved derivative orders. Unsupported
  plans preserve their former behavior, not a newly advertised working pfor
  path. Default backprop, float32 pfor, arbitrary devices/shots/dynamic or
  trainable-coefficient graphs are NOT thereby implemented.
- Whole-plan budgets and extra shift work are checked before tensor math.
  Method/work decisions are immutable. A live owner configuration change
  refuses before tracing. Genuine third-point derivatives refuse. A public
  TF runtime assertion avoids confusing mere recording of a legal second
  derivative with actual execution of a forbidden third derivative.
- Active shared-ledger contexts explicitly refuse this traced eager path.
  Per-VJP structural work bounds are not external pfor execution counters,
  live allocator bytes or per-cached-call Python accounting. The latter
  remains OUT_OF_SCOPE; no host/device/shot work is fabricated.

Reproducible test evidence (rows overlap; do not sum as unique functions):

| Completed check | Main | Alternate | XML suffix after `tmp/r2o3b-tf6-m2g-` |
| --- | --- | --- | --- |
| Original unchanged red baseline |12 passed /20 failed5.89s |12 passed /20 failed5.90s |`original-pfor-red-{main,alternate}.xml` |
| Default matrix, reentry, actual nonlinear loss Hessian/HVP, method/budget/owner/order contracts |70 passed91.99s |70 passed91.67s |`native-dispatch-complete-{main,alternate}.xml` |
| Additional default ordinary/GenericGate/controlled/fixed-power/multi-output quantum Hessians across3 methods |15 passed25.40s |15 passed25.14s |`default-gate-hessians-{main,alternate}.xml` |
| Post-DLPack complete default/pfor suite, same70+15 cases together |85 passed105.25s |85 passed105.03s |`native-dispatch-combined-85-{main,alternate}.xml` |
| Whole native inline complex-state/pfor/Hessians, open controls, global phase, IR/QPY |24 math passed534.17s +12 complex primal passed4.94s |36 passed513.79s |`inline-pfor-first-main.xml`, `inline-complex-primal-main.xml`, `inline-pfor-all-alternate.xml` |
| Preserved M2F request/ledger/identity/inline contracts |163 passed834.37s |163 passed836.66s |`preserved-inline-contracts-{main,alternate}.xml` |
| Actual nine-query chain and no-full-Hessian directional execution |2 passed5.10s |2 passed5.08s |`current-query-chain-{main,alternate}.xml` |
| Four-framework symbolic/moving/mixed/compiled protection subset |43 passed28.64s |43 passed28.24s |`four-framework-protection-{main,alternate}.xml` |
| Installed Qiskit/PennyLane public numerical differentials |216 passed /2 preexisting xfailed7.89s |216 passed /2 preexisting xfailed7.85s |`sdk-differentials-{main,alternate}.xml` |
| Older default/TF protection including original cached RoF |190 passed /2 failed193.24s |190 passed /2 failed193.36s |`old-default-protection-{main,alternate}.xml` |
| Original100-wire MPS actual mixed-mode cases |4 failed4.23s |4 failed4.07s |`original-mps-{main,alternate}.xml` |

The70+15 rows are disjoint collected test cases, not85 newly implemented SDK
functions. The two preexisting differential xfails concern upstream
transformed QWC Hessians returning unresolved ArrayBox objects; they are not
native mathematical parity evidence and were not added by this increment.
The old cached-RoF failures still report InternalError (expected1 gradient,
received2), and MPS still mistakes legal mixed second order for third order.
Neither is claimed fixed by these new native statevector results.

Two reentry policy assertions were narrowly corrected: automatic TF tracing
may wrap a native error in StagingError/InvalidArgumentError. The tests require
either the exact native feature or a TF-owned carrier plus the exact
QB_UNSUPPORTED feature marker. No mathematical tolerance or expected result
was changed, and no original20 case was skipped, xfailed or converted into
a general Unsupported pass. Eighteen original numerical failures are repaired;
the other two now prove their actual intended order/resource policy.

Independent callback-free controls now cover36 actual scenarios per TF
installation: scalar x0*x0+x1, two-output sin/cos, local complex rotations,
two points, eager/traced, pfor Jacobian/Hessian and FoR/RoF exp-loss HVP.
All36 match independent formulas; all scanned GraphDefs/FunctionDefs are
callback-free. JSON: `tests/interfaces/probes/data/tf_pfor_pure_tensor_complete_`
`{main,alternate}.json`. The earlier24-scenario JSON and the negative M2F
callback probe remain separate evidence. Retracing/complex-cast warnings
are not treated as proof of performance or absence of upstream limitations.

Actual current query evidence was re-exported at
`tmp/r2o3b-tf6-m2g-query-evidence-{main,alternate}.json`: nine executed requests,
complete math/accounting assertions, same6361 cumulative parent work and11
completed evaluations. All seven recorded source SHA256 values were verified
against current files. No tensor-value cache or duplicate accounting added.

Broad strict SDK-free development regression initially completed with
5680 passed /1 failed /846 skipped612.15s. It covers Core/Circuit, Compiler,
Serialization, Information, Gradients/QML, DerivativeExecution, Devices/Noise
and Chemistry, NOT all repository tests. Before and after the actual run,
Qiskit/PennyLane/TF/JAX were absent from module resolution/imports. The
nominal SDK-free interpreter is a base-Python symlink; isolation therefore
requires `PYTHONNOUSERSITE=1`, `-s` and disabled pytest plugin autoload.

The one failure exposed an existing CPU DLPack compatibility defect, not a
new TF numeric failure. NumPy1.26.4 does not accept the copy keyword. The
borrower now chooses the documented pre2.1 borrowing protocol or modern
`copy=False` by parsed NumPy version; it never retries a producer's TypeError
without a copy guard. Tests verify actual shared storage, no ownership copy,
no non-CPU exporter call and exactly one failing exporter invocation. All27
array-reservation tests pass in SDK-free/Main/Alternate after the repair.
See the official [NumPy2.0 protocol](https://numpy.org/doc/2.0/reference/generated/numpy.from_dlpack.html)
and [NumPy2.1 copy contract](https://numpy.org/doc/2.1/reference/generated/numpy.from_dlpack.html).
The complete same11-directory strict regression after this repair completed
with5685 passed /846 skipped /0 failures573.08s, process exit0, receipt
`tmp/r2o3b-tf6-m2g-broad-native-sdkfree-after-dlpack.xml`. The same test process
confirmed `POST_RUN_FORBIDDEN_IMPORTS []`. This is a post-repair development
subset result, not SDK-free FULL; optional-dependency skips remain explicit.
The existing native symbolic Hessian/HVP example also matches its independent
oracle under strict SDK isolation, with no forbidden post-run imports.

Ruff F821/F841 for changed implementation/tests and git diff --check pass.
No Git staging/commit/push/fetch, auth/TLS/dependency change, vendor, hardware
submission, financial receipt change, Studio/Router work, tag or release.
Source port count zero. Final three-environment FULL, independent FULL
four-framework, GLOBAL>=91.34108013033072%, unchanged68 exclusions, original
28-section matrix, all numerical examples, controlled legal/five import
origins and frozen/worktree/staged/commit equality remain NOT_RUN. These
development subsets do not authorize an R2/M2 completion claim.

#### M2G Coordination And M2H Entry

The actual M2G execution report was sent to the owner-authorized existing
ChatGPT conversation. Its completed M2H response, including the ending, was
actually read and archived at `stage12_b_mps_tf6_m2h_received_prompt.md`.
It accepts a bounded native default-pfor development increment, not full M2
or SDK acceptance, and prioritizes cached-RoF2 before M3/MPS4. Its initial
RUNNING status for SDK-free is now superseded by the terminal result above.

The original two cached-RoF tests were rerun unchanged to freeze the next
baseline: Main2 failed33.94s, Alternate2 failed33.88s, process exit1 each;
`tmp/r2o3b-tf6-m2h-original-cached-rof-red-{main,alternate}.xml`. Both still
report InternalError expected1 gradient/received2 at reverse.gradient after
the external ForwardAccumulator. Receiving M2H guidance, or proving a
different explicit inline API, does not repair those original call contracts.
No M2H production change or M3 implementation is claimed by this entry.


#### M2G Terminal Confirmation

The final5685/846/0 SDK-free subset and combined85-case results were sent
to the same authorized ChatGPT conversation. Its complete short reply and
ending were actually read, not inferred from a content reference. It confirms
the unchanged M2H order; no next-stage production implementation is implied.

> 确认，继续执行此前完整的 M2H Prompt，顺序不变。
> 这次终态更新确认了：
> Strict SDK-free 11目录：
>  5,685 passed / 846 skipped / 0 failed，exit 0。属于子集通过，不是 SDK-free FULL。
> 默认 pfor：
>  Main、Alternate 各 85 passed，exit 0。
> Cached RoF：
>  原两条仍各 2 failed，继续作为 M2H 的首要修复目标。
> 100-wire MPS：
>  原四条仍未修复，不提前进入 M3。
> 因此，下一步仍是 
> M2H → 修复旧 Cached RoF → 验证数学、导数阶数和资源合同 → 评估 M2 验收
> 。
> M2：PARTIAL；M3：NOT
> _
> STARTED；完整独立原生 Qiskit/PennyLane replacement：ACTIVE / INCOMPLETE。

### TF6-M2H: Native-Source Managed RoF Repair And Wider Scalar Gap

Local-only work on 2026-10-24. The previous M2G turn was real implementation
and validation progress, not a no-progress wait. The original two managed
cached-RoF mathematical tests now pass through their unchanged public entry,
losses, AD nesting, tolerances and ResourceScope. M2/M2H remain PARTIAL:
expanded source coverage exposes six further formal scalar-capture failures.
M3 is NOT_STARTED. Full independent native SDK replacement remains ACTIVE /
INCOMPLETE; neither these tests nor the following source audit redefine it.

Actual implementation:

- Managed preparation asks the existing QNode constructor to retain native
  scalar provenance when a from_circuit input is passed unchanged. The same
  source construction uses FrozenParameterBinding and the existing native
  compiler; user Python is not invoked twice. Parameter occurrences must
  still match at the end. Remapped inputs or additional trainable occurrences
  do not inherit an assumed native mapping.
- For a complete admitted native binding, the same controlled eager callable
  emits readonly Whole-QNode operations. No internal cached quantum or scalar
  function executes during that AD path. The prebuilt value/VJP/second-VJP
  functions remain real caches for explicit queries. This is an implementation
  change inside the same managed public call contract, not success of another
  explicit API being used to replace the original two failing tests.
- Synchronous invocation and native construction work are conservatively
  reserved through the existing ledger and parent/child scopes. Owner checks,
  completion, attempted/aborted calls and concurrency remain active. Full
  Hessian limits stay separate from directional HVP. Tensor allocator/RSS and
  retained/external outputs remain outside actual-byte observation.
- Guards fingerprint the actual native source, executed local/body/observable
  store, binding and resource plan, without rebuilding/lowering a Circuit on
  invocation. The fingerprint includes measurement kind/wires/shots/seed and
  metadata. The first candidate exposed and repaired a missing snapshot-method
  identity check and an empty-vector shape/dtype defect; measurement-kind
  integrity was also tightened. The resource red suite was5 pass/3 fail before
  these repairs, then13 pass including order checks in each environment.
- A subsequent compatibility counterexample, p**q in an otherwise legal
  native source, showed the optional frozen subset must not revoke an existing
  captured-TF query. Unsupported native syntax now uses that prior query route;
  budget errors never select fallback. Its test proves correct values at both
  points and exactly one invocation of user Python. No broad method switch to
  backprop, sampled-to-exact substitution or partial-operation hybrid is added.

Completed development receipts (overlapping rows are not unique SDK functions):

| Check | Main | Alternate | Suffix after `tmp/r2o3b-tf6-m2h-` |
| --- | --- | --- | --- |
| Original RoF2 plus missing frozen-source assertion, before implementation |3 failed33.44s |3 failed33.62s |`frozen-capture-red-{main,alternate}.xml` |
| First native-source repair, same three cases |3 passed9.37s |Later covered below |`native-inline-first-main.xml` |
| New native math plus original cached17, scope21 and concurrency10 |55 passed85.90s |55 passed85.98s |`native-inline-contract-{main,alternate}.xml` |
| Latest combined new39 and original cached17, after all compatibility fixes |56 passed95.77s |56 passed96.21s |`final-new-contracts-{main,alternate}.xml` |
| Latest default TF/M1/M2G85/four-framework protection group |320 passed244.41s |320 passed244.06s |`final-default-framework-{main,alternate}.xml` |
| Preserved request/inline/budget/identity/scope/concurrency group |163 passed792.73s |163 passed792.46s |`preserved-inline-contracts-{main,alternate}.xml` |
| Latest actual nine-query sequence and directional/no-full-Hessian check |2 passed5.16s |2 passed5.15s |`final-query-chain-{main,alternate}.xml` |
| Installed Qiskit/PennyLane public differentials |216 passed /2 preexisting xfailed8.21s |216 passed /2 preexisting xfailed8.24s |`sdk-differentials-{main,alternate}.xml` |
| Newly expanded TF-only/remapped/mixed source RoF |6 failed29.83s |6 failed31.33s |`wider-scalar-capture-{main,alternate}.xml` |
| Original100-wire MPS mixed AD |4 failed3.87s |4 failed3.91s |`original-mps-{main,alternate}.xml` |

The163 run precedes the last unsupported-variable-exponent compatibility
fallback guard; the latest56/320 groups and strict regression were rerun after
that guard. It is not presented as frozen/worktree/commit equality or the
final latest-source163 gate for the subsequent scalar-lowering increment.
The two existing differential xfails remain upstream ArrayBox issues, not
native mathematical passes. No failure was newly skipped/xfailed and no
original RoF assertion was changed. An initial new order-test setup incorrectly
chained QuantumCircuit.ry(), whose actual return is InstructionSet; that setup
was corrected and is not counted as a product regression or a repaired function.

The new mathematical domain is explicit: static analytic native whole-plan
statevectors with complete scalar provenance, fixed observables, float64 /
complex128 and the already admitted operations/orders. Tests verify both
independent parameter points and nonlinear losses, complete complex primal
phase, full quantum curvature, FoR/RoF/TapeTape, streamed HVP, max_diff1 first
JVP and real second-order refusal, max_diff2 second order and true third refusal.
Additional2/4-qubit cases pass in both environments (4 tests each) using the
real independent whole-plan fixtures, open/closed controls and global phase.
These are assertions about cases and actual math, not counts of implemented
upstream functions or proof of arbitrary cached outer AD.

External cached graphs remain a separate contract. The13-case outer group
checks real co-traced loss/AD graph caching, trace count1 at both points and a
repeat, callback-free GraphDefs and no inner pack. Direct calls to a previously
cached outer ConcreteFunction can still return the frozen math after source
mutation/owner expiry/limit changes without entering Python. Tests explicitly
show zero parent work and OUT_OF_SCOPE metadata, while a direct inline Python
entry checks its owner or refuses an active scope. That mathematical success
is NOT per-execution Python ledger or post-trace-owner enforcement.

Boundary evidence: `probe_tf_managed_boundary_lineage.py` actually observes
cached function invocations for an unfrozen TF scalar source and only plain
native execution functions for the repaired native source. Each environment's
JSON ends with error/match, not two mathematical passes. It records public
cached query signatures with one packed input and1/2/3 outputs, no callbacks,
the actual error text and ledger receipts. The exact private generated TF
gradient root cause is NOT_PROVEN; no private registration/hook or tensor-count
padding was used to conceal it. JSON: `boundary-lineage-{main,alternate}.json`.

Latest strict SDK-free11-directory regression:5685 passed /846 skipped /
0 failures578.34s, process exit0, `final-broad-native-sdkfree.xml`. Both pre-run
resolution and same-process post-run imports exclude Qiskit/PennyLane/TF/JAX.
The earlier same-subset622.92s run is separate, not added to the count. This
is a development subset, not SDK-free FULL. Five existing numerical examples
also completed with their assertions under strict SDK isolation: symbolic
Hessian/HVP, native composition including MPS100, parameterized execution,
Operator branch powers, and native H2 VQE (error about1.15e-14 vs its exact
small-model baseline). No scientific/industry production claim follows.

Query JSON was regenerated after the last source fix, now hashing eight
relevant files including qml/qnode.py. Both `final-query-evidence-*.json`
records have all eight SHA256 values matching the current files. They retain
the actual9 requests, work6361 and11 completed evaluations with single parent
charging, not a fabricated global execution counter. Ruff F821/F841 and
git diff --check pass. No staging/commit/push/fetch/PR/auth/TLS/install/vendor,
cloud job, financial receipt, Studio/Router, tag or release change.

### TF6-M2I Entry: Six Scalar Sources Remain Formal Red

The complete M2H intermediate report was sent to the authorized existing
ChatGPT conversation. Its completed M2I response and ending were actually
read and archived in `stage12_b_mps_tf6_m2i_received_prompt.md`. It permits a
bounded constructor-time scalar-data-to-existing-ParameterExpression lowering,
not a general TF graph interpreter, GraphDef execution import, new parameter
system or quantum runner. No such lowerer is implemented by this checkpoint.

I1 read-only source audits completed in both actual TF environments:

| Actual source | Scalar nodes / bytes | Captured final native operations |
| --- | --- | --- |
| direct tf.sin mapping |17 /1810 |RY |
| tf.reverse before native builder |14 /1194 |SX,RZ,SX,RZ |
| native builder plus trainable RX |18 /1707 |SX,RZ,SX,RZ,RX |

Each source function was constructed exactly once, with no external captures,
variables or function-library entries. The appended RX is already present as
the final native operation with its own scalar occurrence. The RY source is
actually decomposed into SX/RZ operations; its global phase and occurrence
UUIDs are retained in the JSON. No missing quantum append or need to rerun
arbitrary user Python was observed in these three fixtures. Full scalar index
and expression provenance remains unimplemented for them.

JSON: `tmp/r2o3b-tf6-m2i-source-audit-{main,alternate}.json`. The direct source
actually contains Pow with a constant2 exponent, and layout sources contain
integer shape/index constants. Any future admission must distinguish that
bounded square from general Pow, and layout integers from trainable scalar
math, with independent Jacobian/Hessian/index proofs. Reading this source
data is not success of the six RoF cases. They still fail at their first point
with InternalError expected1 gradient/received2, rather than returning a
verified Hessian. M2 remains PARTIAL and M3 NOT_STARTED.

All original R2 final gates remain open: three-environment FULL, independent
full four-framework validation, GLOBAL>=91.34108013033072%, unchanged68
exclusions, unmodified28-section matrix, all numerical examples, controlled
legal/five actual import origins, and frozen/worktree/staged/commit equality.
No subset row authorizes full SDK or M2 completion.

The terminal M2H results and completed I1 source audit were also sent to the
authorized conversation. Its entire short confirmation and ending were read
and appended to the received M2I prompt. It confirms I2 then I3: integer
Const is restricted to static shape/axis/index roles, and only constant2
square may be added after independent J/H/domain/native-AST proofs. General
Pow/Div remain refused by the future native lowerer; an unsupported source
may preserve its existing query path, but resource failures cannot fallback.
This is scoped guidance for further implementation, not a completed lowerer,
repair of the six remaining tests, or permission to enter M3.

### TF6-M2I: Restricted Scalar Import And Six Real RoF Repairs

Local-only implementation on2026-10-24, main HEAD b443430. The preceding
entry describes the earlier source-audit checkpoint; this entry records
actual subsequent implementation. M2 remains PARTIAL, M3 NOT_STARTED and
full independent native Qiskit/PennyLane replacement ACTIVE / INCOMPLETE.

The six original scalar-capture RoF tests were first rerun unchanged:
6 failed27.05s Main and6 failed27.21s Alternate. They then passed unchanged
through the same managed public callable after the following native repair.
No exception-to-success substitution, xfail, tolerance/loss/nesting change,
private TF gradient hook or user-Python replay is involved.

- New `interfaces/tensorflow_scalar_lowering.py` imports only constructor-time
  data from a bounded private GraphDef snapshot. It validates the entire DAG,
  including unused nodes, dtype/attribute/port/shape signatures, acyclicity,
  registered input roots and local CPU placement. Unknown/stateful/resource/
  callback/function operations, control edges, nonfinite constants and dynamic
  layouts cannot become a native binding. Public TensorProto decoding reads
  data only; no GraphDef or captured function executes during lowering.
- An initial shape/tree-work pass bounds DAG-to-tree expansion before native
  AST allocation. A second pass creates existing ParameterExpression nodes and
  FrozenParameterBinding only. The result retains neither a GraphDef nor a
  second parameter/evaluation/circuit system. Native UUID and supplied input
  order are preserved; surplus/unused registered inputs are refused.
- The initial whitelist is static float64 scalar math with Add/AddV2/Sub/Mul,
  Sin/Cos/Exp and literal scalar exponent2 Pow. Pack/Unpack/Reshape/ReverseV2
  and the validated StridedSlice subset preserve index maps. int32/int64 is
  structural metadata only. General Pow, Div, ellipsis/new-axis/dynamic slices
  are outside the new frozen domain, not advertised as implemented here.
- Managed construction first retains existing native AST when available.
  Only incomplete scalar provenance enters the new lowerer. Unsupported
  source syntax preserves the old valid query path; resource failures always
  propagate. The original final native operation store, including appended RX,
  its global phase and compiled occurrences, is reused without reconstruction.
- The existing unified ledger/scopes reserve source snapshot, scan and native
  binding work and release on exceptions. Higher-order, symbolic and bridge
  limits remain separate. Reported Python AST/tensor memory is a conservative
  estimate, not allocator/RSS observation. Runtime source mapping is included
  in the existing execution work bounds; external cached-graph Python account
  enforcement remains OUT_OF_SCOPE.

Completed development evidence so far (rows overlap, not implemented SDK APIs):

| Check | Main | Alternate | Suffix after `tmp/r2o3b-tf6-m2i-` |
| --- | --- | --- | --- |
| Original six plus resource/query preservation |15 passed12.53s |25 passed13.62s including initial10 scalar proofs |`original-six-resources-candidate-{main,alternate}.xml` |
| Scalar J/H20, security/layout/budget52, original6 and M2H39 |117 passed62.52s |117 passed62.87s |`new-contracts-{main,alternate}.xml` |
| Actual nine-query sequence and no-full-Hessian direction check |2 passed4.99s |2 passed4.98s |`query-chain-{main,alternate}.xml` |
| Installed SDK public differentials |216 passed /2 preexisting xfailed7.43s |216 passed /2 preexisting xfailed7.51s |`sdk-differentials-{main,alternate}.xml` |
| Original100-wire MPS TF selection |6 passed /4 failed15.08s |6 passed /4 failed15.00s |`original-mps-{main,alternate}.xml` |
| Strict SDK-free native parameter subset |116 passed0.57s |Not applicable |`native-parameter-sdkfree.xml` |
| Preserved default/four-framework/request/inline/scope/concurrency group |483 passed993.25s, exit0 |483 passed999.04s, exit0 |`preserved-regressions-{main,alternate}.xml` |
| Added full-state/no-rebuild lowered-source AD group |18 passed19.07s |18 passed18.93s |`lowered-quantum-final-{main,alternate}.xml` |

The initial10 scalar-proof candidate failed on an importer scalar-shape bug,
then8 passed/2 failed exposed the pure-permutation test's default unconnected
second derivative (None). The importer scalar-shape handling was repaired.
The new independent scalar test explicitly requests TensorFlow's zero for
unconnected second derivatives; it still compares the full actual Hessian to
the independent zero reference. No original six quantum assertions changed.
The final20 scalar cases include negative/zero inputs, both required positive
points, full Jacobian/Hessian, mixed terms, VJP and directional contraction.

The52 admission cases cover malformed/unused source nodes, NaN/Inf/constants,
attributes, roots, control edges, cycles, shape/index/dtype/placement mismatch,
duplicate reverse axes, integer arithmetic, dynamic/non-square powers, graph
mutation before/during decode, vector UUID order and same-name/different-UUID
refusal, negative-axis/negative-stride/inferred-reshape layouts, exponential
DAG expansion before AST creation, symbolic/bridge/higher/unified budgets,
parent charging once, unrelated scopes, and concurrent independent accounts.
SDK-free checks assert absent SDK resolution before and absent imports after
the same pytest process, including importing the new module without TF.

Query evidence `query-evidence-{main,alternate}.json` now hashes9 source files,
including the new lowerer. Both records match their actual sources and retain
9 executed queries, work6361,11 completed logical evaluations and single
parent charging. The MPS4 failures remain legal second derivatives mistaken
for third by the older callback route, not new lowerer refusals.

The added18 lowered-source quantum checks cover all three source modes,
FoR/RoF/TapeTape and both external nonlinear losses at both points plus a
repeat. They verify the complete complex state against elementary RY/RX
amplitudes, including the phase from native RY decomposition. User source
construction remains exactly once; rebuilding/copying/lowering circuits,
host quantum math, callbacks and inner cached scalar/quantum calls are
actively forbidden during actual execution. Every synchronous AD admission's
work is collected and summed, then compared to the parent delta and child
receipt. The first candidate18 failures were a new test-accounting mistake:
it compared multiple AD entries' total to only the last entry's work record.
That assertion was corrected to the independently collected full sum; no
runtime accounting or mathematical assertion was relaxed to pass the test.

Both483 processes reached terminal exit0, with0 failed/errors/skipped/xfail;
no expensive duplicate batch was started while they were running. The group
combines the previous320 default/four-framework protection and163 preserved
request/inline/budget/scope/concurrency cases. Production sources were not
edited after these processes started; subsequent edits were tests/progress/
notices only. HEAD remains b443430 in the dirty local worktree, not a new
commit. The9-file query hashes still match the current production candidate.
There was no before/after full-worktree manifest in the483 processes, and
their complete same-process import origins were not instrumented. These are
not claimed as frozen-source/commit-equality or final five-origin receipts.

Separate real companion import probes confirmed the configured interpreters:
TF2.21.0 from each `/private/tmp/qb-stage11pb-{main,alternate}-tf-env/lib/`
`python3.12/site-packages/tensorflow/__init__.py`; Main Qiskit2.4.1 and PL0.44.1
from `/Users/avalok/Library/Python/3.12/lib/python/site-packages/`; Alternate
Qiskit2.6.0 and PL0.42.3 from its own environment site-packages. JAX0.7.1/0.6.2
comes from the respective environment; Torch2.12.0 from the system Python3.12
site-packages. Native QuantumBridge resolves to this workspace. These are
actual companion-process imports, not retrospective proof of every import in
the already-running483 process. Strict SDK-free proof is separately scoped.

The135-case checkpoint was sent to the authorized existing ChatGPT
conversation. Its entire completed TF6-M2J response and ending were actually
read from the existing Chrome tab, despite the API read_thread view remaining
stale. Requirements are archived in
`stage12_b_mps_tf6_m2j_received_prompt.md`. M2J starts with these483 terminal
receipts, then requires public-path failure atomicity, identity/method/resource
closure and affected compiler/IR/QPY/strict-native/example regressions. Do not
expand the scalar whitelist or start M3. A later supported-subset review is
not M2_DONE, much less full SDK parity. Same-process provenance and start/end
candidate manifests must be captured prospectively in subsequent gate runs.

The483 terminal report was then sent to the same authorized conversation.
Its full short completed confirmation and ending were actually read and
appended to the received M2J record. It confirms J2->J7 in order, no M3 or
whitelist expansion, and emphasizes failure atomicity/multiple occurrences
and separating legitimate capability misses from resource/safety/domain/
identity refusals. The latter must never select fallback. This confirmation
does not mean those further M2J implementation/validation tasks are complete.

### TF6-M2J: Public Failure Atomicity And Typed Capability Misses

Local-only continuation on2026-10-24. The preceding M2I turn was actual
implementation/verification progress. J1 rechecked both terminal483 XMLs;
they are historical M2I receipts, not latest-source passes after this repair.
HEAD stays b443430, main ahead51 with preexisting dirty work preserved.
M2 PARTIAL, M3 NOT_STARTED, full independent native replacement ACTIVE /
INCOMPLETE; none of these development groups substitutes for the R2 gates.

J2 exposed a real blanket-fallback defect. Nonfinite captured scalar source
constants and unclassified identity UnsupportedFeature errors were swallowed
by managed construction, allowing an old-query handle to be published. Three
initial assertions failed by not raising. Four other first-candidate failures
were a new test-reference mistake (TF matrix@vector rank semantics), not four
product defects; those references were replaced by elementary independent
NumPy Jacobian/Hessian formulas. Native AST capture separately retried an
injected identity refusal twice; its single-call assertion also failed before
the capture boundary was tightened.

Actual fixes, without adding a native scalar operation:

- ScalarGraphCapabilityMiss now identifies only a missing frozen scalar
  capability. Validation/identity/domain/resource errors are not caught as
  capability misses. Unknown source data still never becomes an executable
  native AST. Static ellipsis/new-axis mappings, tan/division/variable powers
  and unused inputs may keep their previous real queries, not new native
  lowering support. The original whitelist and all six RoF assertions remain.
- An old query must independently admit the actual original public captured
  TF graph, including exact source equality, closed numeric inputs, no opaque
  functions/state/resources/control/PyFunc/custom-gradient indirection, local
  CPU, bounded storage and finite constants. A capability miss cannot conceal
  an unused NaN, control edge, callback, mutated GraphDef or a budget failure.
  Reading source GraphDef/TensorProto/fixed eager Tensor data does not execute
  a GraphDef, replay user Python or supply host quantum math/Hessians.
- Fixed immutable eager captures keep valid old queries, but are independently
  checked and content-hashed into the mathematical identity. Nonfinite eager
  captures cannot bypass the scalar-source admission branch. Source-data
  validation work is charged separately from runtime quantum requests.
- Optional native AST capture in qml/qnode.py retries only its actual named
  frozen-expression/power subset misses. Other UnsupportedFeature errors
  propagate before a second record attempt. Existing p**q values/gradients/
  HVP remain correct in the public cached query at both points.

Failure tests inject RuntimeError/MemoryError/KeyboardInterrupt at bounded
snapshot, full audit, layout, tree-cost, ledger admission, partial AST and
binding stages. They also fail partial public compilation/whole-plan creation
and actual quantum invocation. No partial result is published; existing
Circuit/ParameterVector/owner/previous handle remains usable, attempted work
is preserved, unused reservations release, parent/child charges agree, and a
legal retry succeeds. Partial occurrence processing is explicitly exercised.

Identity tests additionally cover multiple native UUID occurrences, vector
shrink/regrow, reversed inputs, open/closed controlled native definitions,
global phase and appended RX with complete independent two-qubit complex
state references. Modifying the original gate definition does not mutate the
already-compiled math. Altered live method/max_diff/limits/function/owner,
binding or observable snapshot is rejected before quantum math or work charge.

Each of the three lowered source modes executes the public request chain
value->gradient->JVP->VJP->HVP(v1)->HVP(v2)->full Hessian->value. Constructor
scalar work is distinct from runtime requests; a max_hessian_elements1 budget
still permits directions but refuses a full Hessian before charging. The new
sequence test initially used wrong ledger event keys (event/amounts instead
of action/flat amounts); its6 setup failures were corrected to the actual
existing structured event API without changing production accounting.

Prospective evidence runner:
`tests/interfaces/probes/run_native_gate_with_provenance.py` executes real
pytest or numerical examples, records exit/outcome counts and actual imports
in that same process, plus before/after manifests for explicitly listed
source/test/config roots. It flags source changes and strict SDK-free import
violations. These selected1556-file manifests are not full-worktree or
staged/commit equality and do not retroactively upgrade the M2I receipts.

| Completed/current gate | Main | Alternate | Prefix `tmp/r2o3b-tf6-m2j-` |
| --- | --- | --- | --- |
| J2 first candidate before special-dtype repair |140 passed35.50s, exit0 |140 passed35.25s, exit0 |`j2-{main,alternate}.{xml,json}` |
| J3 first candidate before special-dtype repair |65 passed74.85s, exit0 |65 passed74.77s, exit0 |`j3-{main,alternate}.{xml,json}` |
| J4 first candidate, deliberately interrupted for new reproduced defect |480 passed, exit2/interrupted611.38s |480 passed, exit2/interrupted610.23s |`j4-{main,alternate}.{xml,json}` |
| J2 latest special-dtype repair candidate |166 passed37.42s, exit0 |166 passed37.20s, exit0 |`j2-v2-{main,alternate}.{xml,json}` |
| J3 latest repair candidate |65 passed75.32s, exit0 |65 passed75.24s, exit0 |`j3-v2-{main,alternate}.{xml,json}` |
| Exact original two cached RoF selectors, latest candidate |2 passed7.95s, exit0 |2 passed7.93s, exit0 |`original-two-v2-{main,alternate}.{xml,json}` |
| Runner strict SDK-free parameter check |116 passed0.60s, exit0 |Not applicable |`runner-sdkfree-check.{xml,json}` |

Both J2 runs have0 failed/skipped/xfail/errors, same-process QB/NumPy/SciPy/
TF/JAX/jaxlib origins, unchanged1556-file manifests, and all recorded hashes
matching this candidate when inspected. Imported does not mean all those
framework APIs were exercised by this subset. The SDK-free runner check has
actual forbidden-package pre-resolution absent and post-imports absent, not
an installed-but-unused SDK claim. All candidate intermediate red/setup
receipts remain under this prefix; they are not relabeled as final passes.

J3 also completed with0 failures/skips/xfails/errors in each environment,
unchanged1556-file manifests and same-process origins. All original six scalar
RoF losses/assertions are unchanged. The actual nine-query JSONs were refreshed
after the typed-refusal/capture-identity fixes; all9 source hashes match this
candidate, and both query sequences still account work6361 and11 logical
evaluations. No inner cached scalar/quantum call or host quantum rebuild was
introduced. J4 was started once per environment only after J3 terminal pass.

During J4, an independent read-only source-dtype probe reproduced a further
real omission: a nonfinite bfloat16 capture published a handle. TensorFlow
classifies it as floating, but its NumPy storage-kind is V, so checking only
NumPy kinds f/c skipped finite validation. This was not inferred from theory:
the actual probe printed actual_finite=false and
HANDLE_PUBLISHED_FOR_NONFINITE_CAPTURE.

The two precisely identified J4 processes were therefore deliberately sent
SIGINT before changing source, to stop spending time on an obsolete candidate,
not because polling expired or runtime was long. Both handles reached actual
exit2; each had completed480 tests, not483. Their manifests are unchanged for
that old candidate. They are INTERRUPTED/INCOMPLETE, not PASS and not three
product mathematical failures. SIGINT also produced TF TensorArray disposal
warnings during interrupted AD; those are not relabeled as passing results.

Formal special-dtype red:4 failed/22 passed/18 deselected6.22s, covering NaN
and Inf in both captured and in-graph bfloat16 source data. Other float16/32/64
and complex64/128 source tests already refused correctly. The fix uses the
public TF dtype's floating/complex classification instead of NumPy kind.
Finite bfloat16 old queries remain numerically correct; no bfloat16 native
scalar operator or general mixed-precision support was added. The expanded
public refusal group then passed44 tests9.49s. Latest-source J2/J3 and J4
must now be repeated, rather than reusing the earlier140/65 or480 receipts.

Latest checkpoint after the dtype repair: J2-v2 has166 passes in each
environment, J3-v2 has65, and the exact original two selectors from
test_native_tf_managed_cached_execution.py were additionally rerun with2
passes each. Each process exited0 with0 failed/skipped/xfail/errors and an
unchanged1556-file selected manifest. Those manifests and the refreshed9-file
query hashes were inspected against the current files and match. Actual
same-process imported-module origins are retained, with absent modules marked
absent rather than forcibly imported for a receipt. The original six scalar
RoF assertions remain unchanged. Existing MPS4 has not been repaired or
reclassified by this work.

The latest-source complete J4 is NOT_RUN after the dtype repair; its old
interrupted480 cases are not reused. The next required operation is one fresh
full J4 per environment, then J5->J6->J7 in the archived order. No expensive
test process remains running at this checkpoint. J5/J6/J7 and all original R2
final gates remain open; this is not M2_SUPPORTED_SUBSET_READY_FOR_REVIEW or
M2_DONE. Ruff F821/F841 and git diff--check pass. The complete broad native
functional replacement goal remains active and unchanged.

The latest166/65/exact2 terminal receipts were sent to the authorized ChatGPT
conversation. Its entire completed short response and ending were actually
read and appended to the received M2J record. It confirms the next action is
fresh latest-source Main/Alternate J4 each483, then J5->J6->J7, retaining
same-process evidence and not promoting interrupted old receipts. This is a
concrete-progress checkpoint with required broad verification still pending,
not a wait/blocker, completion claim or request for owner approval.

J4 latest method/resource broad regression, J5 compiler/IR/QPY/four-framework,
J6 affected strict SDK-free plus numerical examples and J7 MPS status remain
required. No M2_SUPPORTED_SUBSET_READY_FOR_REVIEW claim yet. No new dependency,
vendor, Git/auth/TLS/cloud mutation, financial evidence, Studio/Router, tag or
release change. The active full goal and original R2 final gates stay intact.

### TF6-M2J Verification Continuation: Latest J4 Candidate

The preceding goal turn made actual implementation and red/green evidence
progress, including the special-dtype repair. On2026-10-24 the J2-v2/J3-v2
selected manifests were rechecked against current files and still match.
No obsolete test process was live. One fresh Main J4 and one fresh Alternate
J4 were started, prefix `tmp/r2o3b-tf6-m2j-j4-v2-`, using the existing real
same-process provenance runner and the full483-case method/resource group.
Both reached terminal exit0: Main483 passed986.11s, Alternate483 passed984.50s,
with0 failures/skips/xfails/errors. Each same-process selected1556-file
manifest was unchanged and inspected against current files, still matching.
Actual QB/NumPy/SciPy/TF/Torch/Autograd/JAX/jaxlib origins are captured; the
quantum SDK packages were not imported by this group. Source/test/config
files were not edited while these processes ran. Healthy long-running
handles were polled rather than restarted for observation timeouts.

J5 compiler/IR/QPY/actual framework protection follows only after J4 terminal
success, then J6 strict affected-native regression/examples and J7 original
MPS state confirmation. M2 PARTIAL; M3 NOT_STARTED; full independent native
SDK functional replacement ACTIVE/INCOMPLETE. Existing local-only limits and
all original R2 final gates remain unchanged.

J4-v2 is therefore PASS for this selected development gate, not SDK FULL or
M2_DONE. The earlier480/exit2 old-candidate receipts remain independently
INTERRUPTED/INCOMPLETE. J5 was then started once per environment, covering
the complete compiler and serialization directories, public transpiler and
serialization differential groups, and the existing four SDK differential
files. It reached terminal exit0 in both environments:1184 passed/5 preexisting
xfailed, Main40.96s/Alternate40.84s, prefix `tmp/r2o3b-tf6-m2j-j5-`. Each
same-process1556-file selected manifest was unchanged and matches current
files. No production or test code changes have been made in this verification
continuation.

The5 xfails were inspected individually, not counted as native numerical
passes:2 public QPY-v13 annotation parameter-index losses,1 public QASM2
custom-standard-name definition loss, and2 public PennyLane transformed QWC
Hessian failures (unresolved ArrayBox on Main; NotImplementedType on
Alternate). They were preexisting in the actual test sources and none was
newly added to conceal a native mathematical failure.

J6 was then started under python -s, PYTHONNOUSERSITE=1 and disabled pytest
plugin autoload, with pre-run Qiskit/PennyLane/TF/JAX resolution required to
be absent and post-run imports checked in the same process. The11 affected
directories are core/circuit/compiler/serialization/information/gradients/
qml/derivative_execution/devices/noise/chemistry, not repository FULL. A
separate strict process actually executes the5 existing native numerical
examples (symbolic H/HVP, circuit composition, parameter execution, Operator
branch powers, small H2 VQE). The11-directory run reached terminal exit0:
5685 passed/846 skipped/0 failures,566.42s. Optional-dependency skips are not
native numerical passes. The same-process forbidden pre-resolution and
post-import checks pass; its1556-file selected manifest is unchanged and
matches the current candidate.
The example process completed exit0 with all5 main functions/assertions
actually executed, unchanged1556-file selected manifest, absent forbidden
pre-resolution and no Qiskit/PennyLane/TF/JAX imports afterward. Evidence:
`tmp/r2o3b-tf6-m2j-j6-native-examples-v2.json`.

The first example runner invocation stopped at import before mathematical
execution because runpy lacked the examples sibling-module path
(native_symbolic_circuit_gradient). That setup-error exit1 receipt is retained
as `j6-native-examples.json`, not a native mathematical defect or pass. The
retry set PYTHONPATH to the repo plus examples, matching normal script sibling
imports; neither runner, example nor production code was changed to pass it.

Actual sample outputs retain their caveats: native composition includes the
MPS100 expectation0.9210609940028851; Operator branch-power examples report6
matrix/state/density cases with max matrix error about1.57e-16 and zero hardware
tasks; H2 small-model VQE=-1.1372759437827047 vs exact=-1.1372759437827162,
optimization error about1.15e-14, geometry_differentiable=false. These are not
full SDK or production chemistry claims. J6's selected affected-regression
and5-example requirements are now complete, not SDK-free FULL or ALL
repository examples. Prefixes: `j6-native-sdkfree` and
`j6-native-examples-v2`.

### TF6-M2J Latest-Candidate Integration Result

The J2-v2/J3-v2/exact-original2/J4-v2/J5/J6/J7 records all carry the identical
1556-file selected candidate, equal before/after and matching current files
when inspected. Actual same-process module origins are retained, not inferred
from companion probes. The selected-manifest aggregate SHA256 is
9bd0364a228beae48a5ddf92f7ff798257bf9df63d3848d38eff8a3869e0b4d5
(SHA256 of the sorted-key JSON manifest). HEAD b443430 remains unchanged;
no commit or full worktree/staged equality is claimed. This continuation
changed verification evidence and this existing progress record, not
production or test code.

| Latest-candidate gate | Main | Alternate | Evidence after `tmp/r2o3b-tf6-m2j-` |
| --- | --- | --- | --- |
| J2 source admission/identity/atomicity/math |166 passed37.42s, exit0 |166 passed37.20s, exit0 |`j2-v2-{main,alternate}.{xml,json}` |
| J3 scalar RoF/native state/AD/resources |65 passed75.32s, exit0 |65 passed75.24s, exit0 |`j3-v2-{main,alternate}.{xml,json}` |
| Exact original cached-RoF selectors |2 passed7.95s, exit0 |2 passed7.93s, exit0 |`original-two-v2-{main,alternate}.{xml,json}` |
| J4 selected default/method/pfor/ledger/scope/concurrency |483 passed986.11s, exit0 |483 passed984.50s, exit0 |`j4-v2-{main,alternate}.{xml,json}` |
| J5 compiler/IR/QPY/public differentials |1184 passed/5 old xfailed40.96s, exit0 |1184 passed/5 old xfailed40.84s, exit0 |`j5-{main,alternate}.{xml,json}` |
| J6 strict affected-native11 directories |5685 passed/846 skipped566.42s, exit0 |Not an alternate-environment gate |`j6-native-sdkfree.{xml,json}` |
| J6 strict numerical examples |5 actually completed, exit0 |Not an alternate-environment gate |`j6-native-examples-v2.json` |
| J7 original MPS TF selection |6 passed/4 failed/26 deselected14.16s, exit1 |6 passed/4 failed/26 deselected14.19s, exit1 |`j7-mps-{main,alternate}.{xml,json}` |

J7 ran only after J6 terminal success. Its4 original mathematical failures
are unchanged, unskipped and not xfailed: square/exponential_cubic crossed
with forward_reverse/reverse_forward in
`test_host_framework_actual_mixed_mode_graphs`. The old tensorflow_graph
callback throws third-derivative UnsupportedFeature during a legal
second-order query. It produces no verified HVP there. The6 positive MPS TF
cases remain passes. J7 is a completed status audit, NOT an all-green math
gate, proof of a correct refusal, or repair of100-wire MPS mixed AD.

Supported-subset conclusion, proposed for review only:

- Native-source AST retention and bounded scalar-data import feed the existing
  FrozenParameterBinding/Whole-QNode plan. UUID order, reversed/sliced layouts,
  compiled occurrences, definitions, controls, global phase and later RX are
  exercised with actual complex states and independent derivatives.
- Scalar import whitelist remains Placeholder/finite Const/Identity, validated
  static Pack/Unpack/Reshape/ReverseV2/StridedSlice, Add/AddV2/Sub/Mul,
  Sin/Cos/Exp and literal square only. int32/int64 is structural metadata.
  Import requires one static float64 vector input and vector output. Native
  retained AST has its separately validated existing scalar syntax; these
  two domains are not conflated.
- Original2 and new6 public callable RoF tests pass unchanged. Full complex
  primal, expectation, J/H/mixed terms, FoR/RoF/TapeTape and HVP have actual
  independent-reference evidence. No runtime circuit rebuild, inner cached
  scalar/quantum execution, GraphDef execution import, user-source replay or
  host Hessian injection supplies the admitted frozen-source results.
- Explicit controlled queries use real cached graphs and request-level
  parent/child ledgers; native inline calls use declared synchronous admission.
  External cached ConcreteFunction executions remain OUT_OF_SCOPE for live
  Python ownership and per-execution ledger enforcement. Tensor allocator/RSS,
  retained outputs and external loss memory are not observed or sandboxed.
- Independently admitted old p**q/tan/division/unsupported-static-layout/fixed
  eager-capture queries remain available, NOT extra native import coverage.
  Identity/domain/safety/resource failures are fatal instead of blanket
  fallback. Extended floating dtypes cannot evade finite-source checks.
  Partial construction, failure recovery, live-owner changes and concurrent
  resource admission have actual atomicity/accounting tests.
- Native import excludes general variable Pow/Div, arbitrary TF ops, dynamic
  shapes/axes/control flow/functions/resources/callbacks and opaque gradients.
  Managed frozen whole-state math is the admitted static analytic statevector,
  fixed-observable, bounded operation/method/order domain, not all devices,
  shots/transforms/trainable observable coefficients/mixed precision/plugin
  APIs or order>2. Arbitrary unlowered cached-callable mixed AD and100-wire
  MPS mixed AD are not claimed by the green subset.

The evidence supports proposing M2_SUPPORTED_SUBSET_READY_FOR_REVIEW, not
M2_DONE, permission to enter M3, or full independent SDK replacement. All
original R2 final gates remain OPEN/NOT_RUN: SDK-free/Main/Alternate FULL,
independent complete four-framework regression, GLOBAL>=91.34108013033072%,
unchanged68 exclusions, original28-section matrix, ALL numerical examples,
controlled legal/five actual import origins and frozen/worktree/staged/commit
equality. The supported subset and full objective are not redefined to hide
the4 failures or missing API families. No Git/auth/TLS/install/vendor/cloud,
financial evidence, Studio/Router, tag or release change.

No staging/commit/push/fetch/PR/auth/TLS/install/vendor/cloud, financial receipt,
Studio/Router, tag or release changes. Original R2 final gates are not replaced
by these development subsets: three-environment FULL, independent full
four-framework validation, GLOBAL>=91.34108013033072%, unchanged68 exclusions,
unmodified28-section matrix, all examples, controlled legal/five actual import
origins and frozen/worktree/staged/commit equality remain open.

## TF7 Gated Native MPS Integration: K1--K5 Development Results

The complete TF6-M2J boundary review authorized gated MPS implementation;
the complete TF7 K5 checkpoint reply authorized continuation of K6. Both
instructions are archived in the existing M2J received-prompt document.
M2 remains full INCOMPLETE; M3 is IMPLEMENTATION_AUTHORIZED / NOT_ACCEPTED.
Full independent Qiskit/PennyLane replacement remains ACTIVE / INCOMPLETE.

Actual audited call chain:

```
Public QNode.__call__ -> execute_tensorflow -> NativeHostKernel frozen source
 -> existing ExecutionPlan.circuit.lowered()/occurrence parameter UUIDs
 -> TensorFlowMPSPlan (same local operator store as whole Statevector plan)
 -> existing native q0-first gather/restore routing
 -> physical (left, 2, right) TF tensors and global complex scale
 -> local Pauli/Hamiltonian contraction -> native TF AD first/second rules
 -> original external square or exponential/cubic loss
```

The previous graph callback route stops at the order2 callback output when
TF transposes its gradient rule during legitimate FoR/RoF graph construction.
Its blanket third-order rejection is not a proof of a real third quantum-point
request. The new path uses tensor evolution and the existing point-specific
order boundary; the old callback guard was not deleted or weakened.

Existing NumPy MPS/MPSTangentJet math already supplies independent primal and
mixed local-jet references. It does not supply a TF quantum output or derivative.
The new execution uses exact local index splitting M=I*M or M*I; it keeps a
complete local basis rather than differentiating QR/SVD gauges or truncation.
This is a noncanonical exact physical MPS representation with conservative bond
growth. A state can be refused even if a compressed optimal Schmidt form would
fit the device. There is no numerical rank threshold, hidden truncation,
global dense state/operator, host quantum callback, Hessian injection,
stop_gradient or private gradient registry in the admitted path.

The q0-first routing helper was extracted from the actual native MPS gather/
restore implementation and is shared by the existing MPS Device execution,
existing tangent work estimator and TF plan. The TensorFlow layer has no new
Circuit, IR, Compiler, parameter identities, private scheduler or ledger.
Native parameter evaluation, local moving-projector fractional-power matrices,
fixed/controlled primitives and global phase are shared with the prior
whole-Statevector implementation. Ordinary Statevector selection is unchanged.

Development receipts, all with terminal exit/JUnit/same-process origins and
before/after selected-source manifest in `tmp/r2o3b-tf7-*`:

| Gate | Actual result | Receipt |
| --- | --- | --- |
| K1 original four, unchanged | Main4 failed3.31s; Alternate4 failed3.37s; both exit1 | `k1-{main,alternate}` |
| K2 2/4/6-wire and two-loss AD | Main5 passed24.21s, exit0 | `k2-candidate3-main` |
| K3 real100-wire remote entanglement | Main1 passed15.69s, exit0 | `k3-v3-main` |
| K5 original TF selection, unchanged | Main10 passed39.94s; Alternate10 passed40.14s; both exit0 | `k5-{main,alternate}` |

K2 includes complete complex amplitudes against the same native compiled plan,
native dense J/H, existing MPS primal/analytic tangent, TF chain full J/H,
two observables, noncommuting parameters, phase, fractional power, JVP/VJP and
both nonlinear-loss FoR/RoF with repeated positive/negative/zero directions.
Subsequent latest-candidate K2 also compares compiled amplitudes to the original
uncompiled source circuit; the old K2 receipt is not retroactively extended.
Forbidden full-state/host entry points are patched to fail. New mixed graphs
are inspected for PyFunc/EagerPyFunc/Svd/Qr/StopGradient.

K3 contains100 actual physical tensors, maximum represented bond4 and197
two-site gather/gate/restore steps for a distant entangling operation between
physical wires0 and99. It checks full J and streamed quantum HVP against an
independent equivalent2-wire dense calculation, including zero direction and
`max_hessian_elements=1`; global complex scale is checked against native
compiled phase semantics. K5 includes the original four unmodified formal
nonlinear-loss tests. The later full36/55/63 scopes, not K5's ten-item
`-k tensorflow` selection, include the original genuine-third refusal. No original loss,
nesting, tolerance, circuit, skip/xfail or mathematical expectation changed.

Preserved earlier development failures are not reclassified as PASS:

- `k2-red-main`:3 missing-implementation failures before the module existed.
- `k2-candidate-main` and `k2-candidate2-main`: new test setup mistakes using
  InstructionSet chain calls and `*` instead of the actual Pauli `tensor` API.
- `k3-main`: new phase assertion incorrectly equated source global phase with
  compiled global scale; native basis translation legitimately moves local
  phases into the latter. Low-wire complex amplitudes independently protect
  full physical source-phase equivalence.
- `k3-v2-main`: `GradientTape.jacobian(pfor=False)` *inside an active*
  ForwardAccumulator hits TensorFlow's variant/TensorArray dtype limitation.
  This composition is NOT claimed supported. K3-v3 takes the independent full
  Jacobian after ending the accumulator; its actual quantum HVP nesting is
  unchanged. Original four tests were not rewritten.
- `k6-resource-red-main`: controlled compile_tensorflow had no MPS selector.
  The managed selector now uses the actual native Device's existing plan and
  its work planner. Resource/identity/regression verification is still pending.
- `k6-resource-candidate-main`: the new constructor test assumed no retained
  ndarray roots. Actual192 bytes are three held64-byte fixed primitive matrices
  in the immutable-math snapshot, not leaked invocation reservations. GC and
  close do not discard the snapshot object; the test now checks the exact
  retained roots separately from zero outstanding derivative-work reservations.

First admitted domain is real float64, analytic fixed Pauli/Hamiltonian expvals,
zero initial MPS, explicitly cutoff0, supported local one/two-site operators,
existing one-qubit powered bodies and static bounded physical bonds. General
initial states, truncation, multi-qubit local powered bodies, samples/noise,
trainable coefficients, every TF API and general differentiable MPS are not
claimed. K6, M1/M2 protections and original R2 final gates remain pending.

### TF7 K6 Candidate And Selector Compatibility Review

The first K6 candidate's ten positive receipts share1559 selected files and
manifest SHA256 `8bf7c71c26e62d55aa68af10c67341aba1a2a7b3e98fa47e347f20f573f6a0c7`.
This candidate is NOT the latest selector-repair candidate described below.

| Gate, `tmp/r2o3b-tf7-` prefix | Main | Alternate |
| --- | --- | --- |
| New math/resource19 plus original four-framework MPS36, `k2-k6-v2-*` |55 passed141.61s, exit0 |55 passed142.09s, exit0 |
| Prior J2/J3 source/math/atomicity union, `k6-source-protection-*` |231 passed116.85s, exit0 |231 passed116.75s, exit0 |
| Exact prior J4 protections, `k6-protection-j4-*` |483 passed996.99s, exit0 |483 passed998.00s, exit0 |
| Prior compiler/serialization/differential scope, `k6-compiler-serialization-*` |1184 passed/5 existing xfail43.93s, exit0 |1184 passed/5 existing xfail43.97s, exit0 |
| Strict native MPS twelve-file scope, `k6-native-mps-sdkfree` |229 passed46.55s, exit0 |Not an alternate gate |
| Five real numerical mains/assertions, `k6-native-examples` |5 completed, exit0 |Not an alternate gate |

Same-process origins and before/after selected-source manifests are recorded.
The strict native gate requires `python -s`, no user sites/plugins, absent
resolution of Qiskit/PennyLane/TF/JAX before execution and no imports afterwards.
The four-framework MPS gate actually imports TF2.21, Torch2.12, Autograd and
Main JAX0.7.1 / Alternate JAX0.6.2; neither upstream quantum SDK supplies MPS
math. Compiler/differential gates separately load the real upstream SDKs.
The five xfails are exactly the existing two public QPY parameter-index losses,
one public custom-gate QASM self-roundtrip defect and two unresolved public
PennyLane transformed-QWC Hessians. They are not new native passes.

The first expanded command omitted JAX_ENABLE_X64 and stopped with25 passed/
1 configuration failure; `k2-k6-latest-main` is preserved, NOT counted PASS.
The v2 gate sets the required x64 option without modifying math/tolerances.
Original four-test source, tensorflow_graph.py and tensorflow_native_derivatives.py
hashes are unchanged from the original K1 failures.

K6 deliberately continued compatibility inspection after the positive suites.
It found a real automatic-selector regression: existing cutoff0 MPS variance
and probability queries were rejected by the new expval-only specialization;
ordinary best-method expvals were unnecessarily moved from their established
parameter-shift contract. A two-qubit local fractional power also missed the
new tensor rule despite retaining a valid existing native-host first derivative.
`k6-selector-regression-red-main`, `red-v2-main`, `red-v3-main` preserve these
probes. The scratch `tmp` probe is outside the selected-source manifest; those
receipts attest to production-file stability, not a fully frozen probe artifact.
One intermediate two-qubit CX prototype exposed a separate existing scalar
recording refusal before selection; it was not misreported as a selector defect.
The final counterexample instead uses RX/RZ/RY with a valid old host path.

The selector repair retains the existing Device method choice and only chooses
the new plan for MPS-tangent, exact zero-initial noiseless expvals. Explicit
missing local tensor rules may retain independently admitted old host execution;
resource, identity and runtime mathematical-domain failures do not fall back.
Formal protection now lives in `test_native_tf_mps_legacy_selection.py`.
Old-query preservation is NOT extra native tensor coverage. New independent
fatal-resource/source-identity injections protect this distinction.

Latest selector verification is still pending. Consequently the previous483/
231/55 results must not be presented as all-gates proof for the modified source.
M3 remains NOT_ACCEPTED; no claim of M2 full completion, general MPS AD or full
SDK replacement is made. All original R2 final gates remain OPEN.

### TF7 Latest Selector Candidate Verification

Latest selected-source candidate:1560 files, aggregate SHA256
`d9cdbf065acd04af20d96d7b595e8f119437d6ca06dd3055081d0fd3bfd5ee43`.
Production and formal tests remain unchanged during these gates. Records use
`tmp/r2o3b-tf7-selector-v2-` with actual same-process origins and selected-source
before/after manifests; they do not attest to full-worktree/Git equality.

| Latest gate suffix | Main | Alternate |
| --- | --- | --- |
| `mps-*`: math6/resource13/legacy8/original frameworks36 |63 passed149.63s, exit0 |63 passed149.71s, exit0 |
| `ancillary-*`: directives, transformed HVP, JAX examples |10 passed22.18s, exit0 |10 passed22.41s, exit0 |
| `source-*`: previous J2/J3 union |231 passed119.88s, exit0 |231 passed119.22s, exit0 |
| `compiler-*`: compiler/serialization/public differentials |1184 passed/5 old xfail43.76s, exit0 |1184 passed/5 old xfail43.98s, exit0 |
| `native-sdkfree`:12 native MPS files |229 passed49.35s, exit0 |Not an alternate gate |
| `examples`: original five actual numerical mains |5 completed, exit0 |Not an alternate gate |
| `cap-boundaries-*`: supplemental exact admission probe |18 passed8.83s, exit0 |18 passed8.85s, exit0 |
| `j4-*`: complete previous483 protections |483 passed1014.58s, exit0 |483 passed1011.78s, exit0 |

The supplemental probe is `tmp/tf7_mps_exact_admission_probe.py`, explicitly
outside the selected-source roots. Each of its18 JUnit cases records its own
source SHA256 `e2acd749f85cdfd9ee5dfc0b64c133905e19513700298523a303f83901d8f37a`;
all36 Main/Alternate properties were checked against the actual probe file.
It checks value/JVP/HVP crossed with exact/one-below memory/work/tape budgets:
equal succeeds, one-below refuses before `_run_graph`, no temporary live memory
or outstanding work survives, and parent/child consumption is identical. This
is logical native accounting, not an observed TensorFlow allocator/RSS limit.

Selector-repair intermediate receipts remain versioned:
`k6-selector-repair-main` had17 passed/2 new-test metadata expectation errors
because a commuting RY fractional power had been legitimately compiled into
ordinary parameter-shift gates. The protected powered cases now genuinely
contain noncommuting moving projectors. `...repair-v2-main` had19 passed/2
misplaced new-test assertions (KeyError after correctly refused injected
errors); that assertion was restored to its proper test. `...repair-v3-main`
then passed all21 cases. No original public test/loss/tolerance was altered.

Evidence-scope correction: earlier K5 commentary and checkpoint messages
incorrectly said that its10 selected cases included the original
`test_tf_graph_true_third_point_derivative_refuses_not_fabricated_zero`.
Actual JUnit inspection proves it was deselected by `-k tensorflow`. The
latest complete63-case JUnit does include that exact original test, plus
`test_mps_full_second_order_and_first_only_boundaries_remain_real`; both PASS.
The full55-case first K6 candidate also included the original36. Thus the
current third-order evidence is real, but it must be attributed to the correct
complete-file gates, not the narrower K5 selector.

The complete latest J4 now has terminal PASS receipts in both environments.
M3 is proposed for supported-subset review, not unconditionally DONE, and full
independent replacement remains ACTIVE / INCOMPLETE. Exact low-bond/no
truncation is not general differentiable MPS; active-ForwardAccumulator
pfor=False variant-loop composition remains an explicit unsupported gap.

### TF7 K1--K6 Latest-Candidate Terminal Review Handoff

All14 latest selector-v2 receipts have exit0 and identical1560-file manifests
before/after; the complete current selected-root manifest also matches, not
merely the hashes of a possibly incomplete pre-existing list. Aggregate SHA
is the d9cdbf06 candidate above. All needed execution sessions are terminal.
Current branch is main, HEAD `b443430ec3eb7eac418c22814e08fe6d940bf099`;
the existing dirty/ahead state is preserved. No Git mutation or remote action
was performed. Ruff F821/F841 on changed native boundaries/new tests and
`git diff --check` pass.

The exact four original public tests are independently confirmed PASS in
both latest complete MPS JUnit files: square/exponential_cubic crossed with
forward_reverse/reverse_forward on TensorFlow. Their entire original source
file, tensorflow_graph.py and tensorflow_native_derivatives.py have unchanged
hashes from K1. The old third-order callback guard was not edited; the new
tensor path uses the pre-existing point-specific derivative-order rules.

Handoff distinctions:

- M2 verified support remains the prior frozen native scalar/whole-Statevector
  source, ownership, first/second-order query and shared-resource domain.
  Its full public API remains INCOMPLETE. This batch does not expand GraphDef
  import syntax, arbitrary TF ops/dtypes/dynamic shapes, general shots/noise,
  trainable observable coefficients, plugin/device coverage or SDK semantics.
- M3 now has real TF tensor-chain primal/J/H/JVP/VJP/HVP and nonlinear FoR/RoF
  evidence, including actual100 physical wires, remote entanglement, phase,
  routing, full small-wire amplitude oracles and independent native derivatives.
  Accepted math is exact low-bond uncompressed index splitting with no numerical
  truncation or gauge factorization; its conservative representation may refuse
  states that a smaller Schmidt-compressed form could store.
- Native method choice and old variance/probability/wider-power query paths
  are preserved. Those CPU-native host results are not new TF tensor coverage.
  Named missing tensor-rule capability misses are distinct from fatal identity,
  resource, source-domain or runtime math refusal; invalid branches do not
  acquire a silent fallback or a fabricated zero derivative.
- Managed explicit requests use existing DerivativeExecutionRequest/work
  planning, owner/source fingerprint guards, scope lifecycle, constructor/cache
  work and parent/child/concurrent reservations. Cached query math has real
  repeated-direction/cotangent and failure-recovery evidence. External cached
  ConcreteFunctions do not enforce live Python ownership or per-invocation
  ledgers; allocator/RSS, retained TF outputs and outside loss allocation remain
  OUT_OF_SCOPE/ESTIMATED_ONLY as documented. No private MPS scheduler or ledger
  was introduced. Conservative local jet slots are not observed global
  coherent-MPS component counts.
- Every latest development scope is listed above. None is the original SDK-free,
  Main or Alternate FULL run, independent four-framework FULL, GLOBAL coverage
  >=91.34108013033072%,68 unchanged exclusions, original28-section matrix,
  ALL numerical examples, controlled legal/five actual origins or frozen/
  worktree/staged/commit equality gate. All those original final gates remain
  OPEN and cannot be inferred from these passing subsets.

K1--K6 therefore supports proposing M3_SUPPORTED_SUBSET_READY_FOR_REVIEW.
It does not complete M2's full API, general TensorFlow/MPS AD, full Qiskit or
PennyLane parity, or the active independent replacement objective. No cloud/
hardware tasks, dependency/vendor/auth/TLS changes, financial history changes,
Studio/Router work, tag or release were performed. The existing authorized
ChatGPT conversation receives this terminal handoff for the next limited task.

## TF8 Native MPS Exact Local Matrix Coverage

The completed TF7 review accepts the verified supported subset only. TF8 now
follows N1 -> N2 -> N3 -> N4 -> N5 -> N6 -> N7. Full independent replacement
remains ACTIVE / INCOMPLETE. No Studio, Router, hardware, finance-history,
Git/authentication, dependency installation, tag or release work is performed.

### Preserved Baseline And Actual Gap

The1560 TF7 selected source files are archived in
`tmp/r2o3b-tf7-selected-source-baseline-v2.tar.gz`, archive SHA256
`aa9a7d697e40919b4b32f3705c2c2b38eaa40f60d95d10cc17ad457389fe87f3`.
Every archived content hash was checked against the TF7 selected manifest.
This is not a full-worktree/frozen/staged/commit-equality archive. The first
non-v2 tar contains AppleDouble extras; only v2 is the clean baseline above.

The original `scripts/run_local_matrix.sh` was read in full:28 sections, same
worktree/HEAD SHA256
`1d93b127aa5783541178d6c852ecec3457fac89694248dd2cd270dad989a7798`.
Core-only/dev invoke whole pytest; Aer contains native MPS compatibility tests;
PennyLane sections cover optional adapters/full-compat targets. Not all new TF
tensor tests have a separate matrix section. The original matrix is unmodified
and NOT_RUN as a final gate; these selected gates cannot replace it.

N1 first exposed a real independent category1 public API defect:
`QuantumCircuit.unitary` inherits Circuit.unitary, which calls the public
QuantumCircuit.append with unsupported metadata. The raw two-failure receipts
are `tmp/r2o3b-tf8-n1-red-{main,alternate}.json` and matching XML. This defect
is NOT fixed, NOT a typo, and NOT closed by using the lower-level native Circuit.

The v2 minimal red deliberately isolates the category2 gap using actual native
Circuit.unitary: native dense and MPS execution agree including complete complex
phase, while TF refuses `tensorflow_whole_operation`. Both one/two-wire payloads
fail in `n1-red-v2-{main,alternate}` before the repair. This is a missing TF local
rule, not a routing defect or insufficient-bond failure.

### Native Repair And Mathematical Scope

The common fixed-operation classification is now an overridable admission
predicate. Only the MPS specialization additionally accepts the existing
`unitary` name, no parameters, exactly matrix metadata and one/two wires. It
uses existing native gate_matrix/strict validate_unitary_matrix, gather/restore
routing, local power math, parameter UUID bindings and exact index splitting.
No second Circuit/IR, simulator, matrix library or derivative engine was added.
Arbitrary custom matrix names/metadata and wider local matrices remain outside
this rule. The Statevector default fixed-operation admission is unchanged.

Structural workspace now also scales with cumulative local evolution, fixed
operator storage, local power AD graph and observable contractions. This closes
a storage-estimate omission rather than claiming exact TF allocator/RSS control.
All estimates run before fixed-matrix construction/TF execution. Exact matrix
and finite/unitary validation remains mandatory, without generic host fallback.

N2 candidate passed15 tests (2 local-matrix primal/13 prior resource protections).
N3 passed10 tests in both environments before the domain probes: independent
2/4/6-wire dense/native-MPS value/J/H, full complex amplitudes and global phase,
reversed remote two-wire ordering, JVP/VJP, streamed FoR/RoF, zero/multiple
directions and square/exponential-cubic outer losses. No production finite
difference, full-Hessian injection, host callback or dense fallback is used.

N4 candidate2 Main passed2 tests46.56s, exit0. Actual20/100 physical tensor
chains match an independent two-active-wire oracle including full active
complex amplitudes and a joint inactive-vacuum projector contraction. Observed
and predicted max bond are both16; actual routing steps76/396. Runtime linear,
square and exponential-cubic losses, three directions and nontrivial/basis
cotangents match complete independent chain-rule Hessian products. Global dense
conversions and full Jacobian construction are patched to fail during streams.
The final expanded latest-candidate gates below must revalidate this result.

N5 found no missing observable implementation: existing native conversion
already handles Pauli words, fixed-real Hamiltonian sums, Hadamard combinations,
sparse operators, identity/offset and noncontiguous multi-output contractions.
New tests verify value/J/H at2/6 wires, including zero identity derivatives.
Trainable coefficients are not converted into claimed fixed-coefficient support.

N5/N6 first candidate passed23 tests34.10s. Value/JVP/HVP crossed with memory,
work and tape budgets at equal/one-below limits validate parent/child accounting,
early refusal, snapshot/source distinction, modified fixed-store identity
refusal, injected runtime failure/recovery and concurrent live memory pressure.
Additional five payload/storage probes pass2.77s, rejecting shape/NaN/Inf/
nonunitary payloads and admitting cumulative storage before fixed allocation.
These logical reservations do not measure retained TF outputs or external losses.

Physical Schmidt rank falls2 ->1 on entangle/uncompute, but observed algebraic
representation max bond stays4 ->4. This exact identity-split implementation
does not compress on disentangling, and no bond-decrease capability is claimed.
The cap-minus-one plan refuses before chain execution; no truncation occurs.

### Negative Evidence And Corrections

The new approximate-unitary test initially assumed loose Circuit construction
implied native runtime acceptance. Actual native execution already rejects
that payload strictly. `n2-unitary-domain-red-main` preserves the wrong new-test
assumption; `n3-domain-confirmation-main` preserves a subsequent wrong error-regex
expectation. Both native and TF strict guards were retained, not weakened.
`n4-candidate-main` preserves the new large test's nonexported qb.QNode alias
mistake; candidate2 uses the actual QNode import. None is an original-test edit.

The explicit diagnostic `tests/interfaces/probes/diagnose_tf_mps_pfor_variant.py`
is outside automatic test-name collection, not an added exclusion or xfail.
It tests active ForwardAccumulator around GradientTape.jacobian(pfor=False)
with real analytic second-derivative assertions for pure TF and small native
MPS. Alternate v2 records2 actual TypeError failures (`variant` incompatible
with int64), exit1. No workaround, host callback or private registry is used.
The initial Alternate diagnostic exit2 was missing tests/interfaces on PYTHONPATH,
not a mathematical result; the v2 raw failures are the actual evidence.

Latest selected-source candidate is1565 files, aggregate SHA256
`f2fd10c630e4477761576a0d7a8534cb275130bfc2f0a33580c28272a9fe099d`.
N7 complete regression sessions are in progress; no latest-candidate overall
PASS or TF8 acceptance is claimed until their terminal receipts are inspected.
M1/M2/M3 remain verified supported subsets with full APIs incomplete. Original
SDK-free/Main/Alternate FULL, independent four-framework FULL, GLOBAL coverage
>=91.34108013033072%, unchanged68 exclusions,28-section original matrix, ALL
native numerical examples, controlled legal/five actual origins and frozen/
worktree/staged/commit-equality gates remain OPEN.

### TF8 N1--N7 Latest-Candidate Terminal Handoff

Both remaining J4 sessions are now terminal. Eight latest positive/negative
receipts share the exact1565-file f2fd10c6 selected-source manifest before/
after; a new scan of every selected root matches the complete manifest too.
This is selected-source equality, not full-worktree/Git equality.

| Latest receipt under tmp/r2o3b-tf8- | Actual outcome | Exit |
| --- | --- | --- |
| `n3-n7-expanded-main` |1530 passed,5 existing xfail,453.83s |0 |
| `n3-n7-expanded-alternate` |1530 passed,5 existing xfail,453.72s |0 |
| `n7-j4-main` |483 passed,1035.31s |0 |
| `n7-j4-alternate` |483 passed,1033.66s |0 |
| `n7-sdkfree` |229 passed,46.46s, strict no-user-site runtime |0 |
| `n7-examples` |5 actual numerical mains completed |0 |
| `pfor-diagnostic-main` |2 real variant TypeErrors,6.15s |1 |
| `pfor-diagnostic-latest-alternate` |2 real variant TypeErrors,6.28s |1 |

All pytest gates have raw matching XML and actual terminal outcomes; examples
have completion/assertion receipts, not a fabricated pytest count. No positive
gate has new failures/skips/xfails. The five expanded xfails are exactly the
prior two public QPY13 annotation parameter-index losses, one public QASM2
custom-standard-name self-roundtrip loss and two public PennyLane transformed
QWC shift-Hessian failures. They remain unresolved comparison cases, not native
successes. The explicit negative diagnostic is still UNSUPPORTED/UNRESOLVED.

The expanded1530 scope is the prior63 MPS,10 ancillary,231 source/ownership,
1184 compiler/IR/QPY/public differential passes plus42 new formal cases. The
separate483 scope preserves prior M2 math, default-pfor, cached queries,
whole-Statevector, resource/owner and four-framework protections. These are
selected development scopes, not original FULL gates or API counts.

The exact original four `test_host_framework_actual_mixed_mode_graphs` cases
crossing TensorFlow/FoR/RoF and square/exponential-cubic were checked by name
in both latest expanded JUnits: all PASS. The original true-third refusal also
actually appears and passes. The full original test file, tensorflow_graph.py
and tensorflow_native_derivatives.py retain their TF7 hashes; indeed no old
selected test file changed. Selected-root changes are only the three native
production files, THIRD_PARTY_NOTICES and five newly added test/probe files.

Actual expanded-gate import origins were inspected in both processes: native
QuantumBridge from this checkout; TF2.21.0, NumPy2.4.6, SciPy1.18.1, Torch2.12.0,
Autograd and JAX0.7.1(Main)/0.6.2(Alternate). Comparison SDKs actually load as
Qiskit2.4.1/PennyLane0.44.1(Main) and2.6.0/0.42.3(Alternate). Strict SDK-free
find_spec for Qiskit/PL/TF/JAX is false, post-import list empty; NumPy1.26.4
is the actual loaded math module there. Five numerical examples do not import
Qiskit, PennyLane or a framework quantum executor. Missing imports in a receipt
are recorded absent, not inferred from package installation.

Formal large-chain properties in both latest JUnits confirm observed max
representation bond16 (predicted16),20/100 physical wires, routing76/396.
These tests prove the actual low-active circuit family, not arbitrary global
100-wire entangled states or optimal bond compression.

Proposed review status: TF8_SUPPORTED_SUBSET_READY_FOR_REVIEW, restricted to
TF_MPS_EXACT_COVERAGE_EXPANDED_SUPPORTED_SUBSET. Acceptance is not assumed.
Public QuantumCircuit.unitary ABI, active-ForwardAccumulator pfor=False,
compression/truncation, trainable coefficients, arbitrary local width/custom
metadata, initial-state/noise/shots/dynamic/transforms/device/plugin and full
SDK semantics remain outside this new rule. Existing legal native host paths
are preserved but are not extra TF tensor coverage.

All required local sessions have terminal results. Branch main and HEAD
b443430ec3eb7eac418c22814e08fe6d940bf099 remain unchanged; pre-existing dirty/
ahead state is preserved. Ruff F821/F841 and git diff --check pass. All original
R2 final gates remain OPEN as listed above. There is no Git mutation, cloud/
hardware task, auth/TLS/dependency/vendor change, financial-history rewrite,
Studio/Router modification, tag or release. Full independent Qiskit/PennyLane
replacement remains ACTIVE / INCOMPLETE, not completed by this local milestone.

TF8 terminal review was fully read and accepts only the verified exact MPS
supported subset, based on supplied receipts. It does not independently attest
to uncommitted code or remote CI. Before QC1 changes, the1565 selected TF8 files
were archived as `tmp/r2o3b-tf8-selected-source-baseline.tar.gz`; all names and
file contents match the f2fd10c6 manifest, archive SHA256
`765b6dc40367ad81b5a9b00f0a4674db31470b6eb4e19d9ee995c3a408679b7a`.
Next received bounded task is QC1: real public QuantumCircuit.unitary ABI
repair, inherited append consistency and single-store/compiler/device proof.
The full operative instructions are archived in the existing received-prompt
document; no new MPS expansion or private pfor workaround is authorized.

## QC1 Public Unitary ABI: A--C Checkpoint, Not Acceptance

QC1-A formal1/2-wire complex asymmetric matrix tests reproduce the exact public
TypeError in Main and Alternate (`tmp/r2o3b-qc1-a-red-*.json/xml`,2 failed each,
exit1). Native Circuit value equals the independent matrix first column before
the public call fails. JUnit records actual append signatures, zero operations
and unchanged source store on failure, not a hidden partial append.

The installed public-only probe (`qc1-a-public-*`) passes7 observations in each
real Qiskit2.4.1/2.6.0 process. Both unitary signatures are obj/qubits/label,
return InstructionSet, retain a UnitaryGate/label/operand frame, and reject
shape/nonunitary/duplicate/range/dtype inputs before store mutation. The
noncontiguous1/2-wire valid observations also record that caller ndarray mutation
aliases the upstream gate. Existing native UnitaryGate deliberately owns its
matrix; QC1 preserves that already-tested native contract, does not silently
claim full public aliasing parity or rewrite NumPy borrowing rules.

QC1-B minimal production change is a four-line public QuantumCircuit.unitary
adapter constructing the existing native UnitaryGate and invoking existing
public append. No private metadata keyword is added to public append; native
Circuit.unitary/fluent behavior, operation store, Gate registry and TF fixed
predicate are unchanged. The original TypeErrors now genuinely pass.

QC1-C independent NumPy q0-first local application verifies complex matrices on
wires2/(3,1)/(0,3), global phase, value, existing exact MPS, copy/decompose and
compose-inverse; the matrix snapshot survives caller mutation. Public data and
InstructionSet reference the same stored Gate with its label. Invalid input
and a63-byte matrix-construction cap reject atomically and permit recovery.
This is native wire-convention math, not an unrecorded claim that all upstream
endian/ownership semantics match transparently.

Latest `qc1-b-c-candidate-{main,alternate}` each pass128 tests, exit0,4.19/4.20s:
11 new public-unitary cases plus117 existing standard Gate contracts. Raw
initial `qc1-b-minimal-*` receipts show118 pass/1 JAX dtype configuration failure
because JAX_ENABLE_X64 was omitted. Corrected commands set the required x64
option; no old math/tolerance/test was weakened. Ruff F821/F841 passes.

These are A--C targeted receipts, not QC1-D/E/F/G or final acceptance. Bounded
inherited-append audit, actual public-entry compiler/IR/QPY/QASM, additional
matrix/resource/owner cases, TF7/TF8/20/100 public-entry regressions and strict
SDK-free/latest affected two-environment gates remain required. Other inherited
append conflicts are not closed merely by adding unitary. Public Gate/Operator
input forms and all broader ABI parity must be investigated, not inferred from
ndarray success. All original R2 final gates remain OPEN and full independent
replacement ACTIVE/INCOMPLETE. No remote/Git/UI/cloud action occurred.

QC1 A--C checkpoint review was fully read and confirms continuing original
D -> E -> F -> G, no new stage or early acceptance. Current1567-file A--C
selected-source SHA256 is
`7403ada13d16a08014d9f7051dd976ab471e684c2afed06efe68ec20719367b3`.
Additional `tmp/r2o3b-qc1-a-c-sdkfree.json/xml` passes all11 new native unitary
cases under strict no-user-site/forbidden SDK isolation, exit0,0.22s, same
candidate; no new skipped tests or foreign dependencies. This is an A--C
SDK-free spot gate, not the pending QC1-G broad gate or original FULL gate.
All needed local execution sessions at this checkpoint are terminal.

### QC1-W1 Pre-Edit Execution Audit

D added real two-environment red/green Gate/Operator input and CH/CSwap wrapper
proof. E/F added39 targeted cases, plus8 actual public-entry TF MPS cases
(including20/100 wires). A separate exact same-public-call wire probe exposed
width2 failure in both SDK versions:8/16 amplitudes wrong, max0.61543702;
width1 passes. Raw `qc1-wire-parity-*` is not a green supported-domain result.
The completed correction review requires fixing this rather than permanently
excluding the real public math error. Native owned-copy alias drift remains open.

Actual conversion table before the next production edit:

| Boundary | Current public path | Required corrected public path |
| --- | --- | --- |
| Public Gate/authoritative source | Original U/qargs/label, no unitary public frame |Same original U/qargs/label; existing frame records provenance |
| Gate definition/native lowering |Raw U interpreted native-first-high, conversion0 (wrong) |One local basis conversion in execution snapshot, source unchanged |
| Already native lowered operator |No later conversion |No second conversion |
| SV/MPS/TF |Existing native first-high math |Identical kernels, consume converted local operator |
| IR |execution_operation normalizes invocation |Serialize normalized native math, not a second source store |
| QPY writer |execution_operation, then _unitary_wire_order |Normalize public math once; existing format encoding converts native-to-QPY |
| QPY reader |Standard matrix wire-order decode |Decode once into native math; native/public origin may not survive standard wire format |
| Native Circuit.unitary |q0-first raw matrix, no public invocation |Unchanged native contract |

All39 native-convention cases alone are insufficient public parity evidence.
Other observed inherited direct append paths remain: kraus/channel/phase/u1/
u2/u3/csx/csxdg/dcx/ecr/iswap. Only existing registered CH/CSwap were repaired
in the bounded root-cause batch; an AST list is not claimed functional coverage.
The h/rx/unitary-only basis lacks an existing rz translation route, still open.
QASM first rejects a circuit name by default; after explicit metadata-loss
permission its actual arbitrary-unitary synthesis miss was mislabeled as
FormatValidationError. The corrected emitter now preserves typed unsupported
feature/format without claiming synthesis. Initial wrong new GateLimits import,
Python-is bit assertion and QASM first-refusal assumptions retain raw receipts.

### QC1-W1 Actual Wire Fix And Derived-Owner Reds

The original same-U/same-qargs complex-amplitude probe remains unchanged.
Public unitary now marks its existing owned UnitaryGate with explicit local
matrix provenance; execution_operation builds the native local-basis snapshot
once, while source U/qargs/label and the native global tensor convention remain
unchanged. Native Circuit.unitary and unmarked native matrix factories retain
their original q0-first contracts. Provenance is copied by the existing owned
copy machinery, not inferred from the string name "unitary" or stored in a
second instruction list/IR schema. This is not all public append parity.

The first all-UnitaryGate conversion attempt broke three unchanged controlled
power cases (`qc1-w1-broad-probe-main`,247 passed/3 failed, maxfail3). Explicit
provenance fixes this; `qc1-w1-provenance-v1-main` has exit0/no JUnit failures.
The new derived-owner test then exposed seven actual failures (39 passed):
fractional-power provenance loss on four transports, repeat QPY canonical-class
refusal, and two native raw-matrix QPY misses. Raw receipts are
`tmp/r2o3b-qc1-w1-derivations-red-main.json/xml`.

Repairs preserve public-origin matrix basis through the existing power engine,
resolve marked owners even inside native repeat definitions, and promote a
checked native raw matrix only to the existing standard UnitaryGate QPY record.
No private matrix-origin sidecar is emitted. New tests check resolution
idempotence, live parameter update freshness, bad raw-frame width before copy,
and QPY numeric admission before owned allocation. The unchanged native powers,
new derivations and original public wire probe pass238 cases in Main.

New installed-SDK transport probes use exactly the same U and qargs in the
actual public calls:1wire and2wire orders(0,1)/(1,0)/(3,1)/(0,3), ndarray/native
matrix Gate/Operator forms, source/compiled/native QPY/bidirectional actual SDK
QPY, complex global phase and exact SV/MPS amplitudes. Eight actual owner
modifier cases additionally compare copy/inverse/repeat/integer/fractional/
open/closed/annotated control. Main2.4.1 and Alternate2.6.0 each pass134 combined
oracle/derivation cases (`qc1-w1-oracle-fixed-*`,exit0,2.88/3.10s), not full SDK
parity. A first new compiler test incorrectly omitted cx from its declared
target basis:15 configuration failures/70 passes remain archived as
`qc1-w1-transports-main`; cx is now explicitly admitted, not silently synthesized.

The earlier new C/E NumPy oracle incorrectly interpreted public local qargs as
native high-first. Only those new QC1 expectations were corrected to reverse
local axes after the real two-SDK counterexample; input U, public qargs, original
wire probe, tolerances and pre-QC1 formal mathematical tests are not rewritten.
Owned native matrices versus upstream caller aliasing remain different. General
direct append(UnitaryGate(U)) and Operator-from-circuit provenance are not
claimed resolved by the literal-matrix unitary-wrapper comparisons.

Broad affected circuit/core/compiler/serialization/information regression is
currently RUNNING on the1574 selected-file development candidate. This is not
the final QC1 frozen D--G evidence, TF regression or acceptance. All original
R2 FULL/GLOBAL/Git-equality gates remain OPEN; full native replacement remains
ACTIVE/INCOMPLETE, with no Git/remote/cloud/hardware/UI changes.

### QC1-W1/F Later Candidates And Still-Open Admission Audit

The1574-file development candidate completed Main and Alternate broad native
circuit/core/compiler/serialization/information scope:5173 passed/3 original
xfail,exit0,356.82/361.06s (`qc1-w1-broad-v3-*`). Strict SDK-free v3 passed317.
These precede additional public append/Operator-origin and recursion repairs.

Actual2.4.1/2.6.0 same-U/qargs independent-entry probes both exposed append
max0.5301432571194317 and Operator(body) max0.5942475837860108. Shared binary
GenericGate DAG cap7 failed to refuse>=30 expanded operations;12-level analysis
read8190 definitions. Permanent `qc1-w1-independent-entries-red-main` records
4fail/2pass. Fixes use public invocation frames for literal UGate, explicit native
numerical factories, origin-preserving UGate/real literal-repeat wrappers and
memo/active-path/per-reference expanded cost. Native Core.to_gate wrappers and
copy=False native reuse are protected. Operator(circuit)/from_circuit marks
the existing object's native representation; raw Operator(U) and literal Gate
Operators are distinguished. Copy/power/adjoint/transpose/conjugate/reverse_qargs
have actual public comparisons. Unproved compound compose/tensor or controlled
origins are explicit public_operator_matrix_origin refusals, still parity gaps.

The fully read authorized review precisely permits5 old public-entry expectation
corrections only in test_native_controlled_public_powers.py:4powers and one
width2 factory case. Original matrices/exponents/tolerances remain, native
Operator/rawCircuit/SV/density math is additionally asserted. Actual SDK public
math is required, not inferred. Generic repeat/control passed into public
unitary is rejected by the upstream SDKs themselves (to_matrix undefined);
6 explicit negative ABI checks replace wrong new positive assumptions, no skips.
Native internal to_matrix remains. Wrong new qb.CircuitError top-level import
and the native inverse-before-QPY metadata miss have raw failed receipts.
Native raw QPY then inverse passes; raw inverse metadata still precisely refuses
unitary_dg/no sidecar and is not claimed supported.

First frozen1575-file candidate27d6b73da8b9be88f7a86cea20d4a596c05703bf54bf6b73c71e188399b9a53d
has archive qc1-w1-selected-source-baseline.tar.gz, SHA
a8d66edad6601712d871f341de1d9f4bd8ffcdfacf43be26a434a38bc816c2f8,
all names/content verified. Two actual expanded broad gates each6602pass/1fail/
4existingxfail,exit1,406.28/407.92s. TF-MPS each207pass,exit0,368.94/369.16s,
including actual public2/4/6/20/100, original4 mixedAD, true-third,4framework
moving MPS and fixed/resource/legacy guards. Strict SDKfree525pass, five actual
numerical examples exit0 (initial missing examples PYTHONPATH retained, corrected
.:examples). The broad failure is unchanged metadata refusal expectation,
independently reproduced from exact TF8 archive in both actual runtimes with
baseline module origin/JUnit. Baseline semantic checks in both show userdata
preserved, no executable scope/vars/captures/declared bindings across copy/
compose/IR/value and typed native scope QPY still rejected. Separately authorized
one-test metadata-vs-execution assertion correction strengthens these checks;
no production QPY reader/whitelist/sidecar change. Old exit1 is never relabelled.

Read-only fault injection found actual foreign operations property execution
inside the new family classifier. Formal qc1-f-foreign-owner-red-main has7fail/
1pass. Closed native definition/container/param/enum admission before property
or equality fixes this; latest11 trap cases assert no foreign callback, unchanged
store and ledger0. One new fixture initially retained a legitimately owned64B
Operator in its scope; fixture construction is now outside the refusal-only
ledger, not a production leak repair. Current and Alternate targeted each553
pass,exit0,7.74/7.72s after the separately authorized metadata correction.

Second1575-file candidate SHA
a2feae581b2a5aead645962116e01615ccb9f6244edc94bbad5ccef6cacb0891
is immutable while current final revalidation runs. Exact archive
qc1-f-selected-source-baseline.tar.gz SHA
d1900448fa388d548f0620acbdb5a0bf5542c93acd676ae3ee6a978f3a8c659d.
Latest strict SDK-free536pass/exit0/50.73s and five actual examples exit0.
Broad Main/Alternate sessions77054/80375 and TF-MPS56358/56426 are RUNNING;
do not edit selected roots until terminal. Receipts qc1-f-final-*.json/xml.

One more read-only trap during immutable runs proves public unitary(Gate)
must reuse the same admission before reading that Gate's provenance: forged
UnitaryGate._public_matrix_basis=str subclass logs origin.eq, returns without
refusal and appends1. Classifier/Operator paths are fixed but this front door
still reads the field after to_matrix. After current terminal receipts, add
permanent direct public Gate-origin/matrix and Operator-width traps, invoke
existing UGate family admission before to_matrix/propagation, and exact-int
Operator width admission before bitshift; then new latest-candidate proof.
This is still QC1-F, not a new feature. QC1 NOT_ACCEPTED; no source, ownership,
callback or full-parity success is inferred from passing valid-input tests.
All original R2 final gates OPEN; full replacement ACTIVE/INCOMPLETE; local-only.

### QC1-F2 Terminal And W2 Detached-Record Reuse

After the a2fe sessions became terminal,3 permanent direct unitary-owner trap
cases failed in qc1-f-public-owner-red-main. Reuse of existing managed owner
admission BEFORE Gate/Operator reads, existing UGate family checks BEFORE
to_matrix, and exact-int Operator width before bitshift fix those. Raw numeric
buffers do not acquire a new graph-admission restriction:4 C/F/strided/ndarray
subclass readonly cases preserve existing owned nonalias data,256B accounting
and full release. Fourteen total malformed-owner traps verify callbacks=[],
typed refusal, unchanged store and ledger0. Main/Alternate targeted301 each.

Frozen5c2af77d7b43aa0258985c4767ce09e91b02f4733e4f91bf61155f85663cccb2
candidate exact archive qc1-f2-selected-source-baseline.tar.gz SHA
e125d1cbf21a6ac8aef998fe003868ca6f107ee612b33c3c41d3c2481fffdecb:
Main/Alternate broad each6621passed/4originalxfail,exit0,413.40/413.84s;
TF-MPS each207pass,exit0,369.40/368.38s; strictSDKfree543pass,50.84s;
5actual numerical examples exit0. Every selected before/after manifest matches.
These sessions all finished before the next source edit. The fully read F2
reply confirms bounded review conditions, not acceptance or full SDK parity.

Post-transport valid Gate reuse then exposed another original QC1-E/W1 issue:
whole restored circuits were correct, but detaching a QPY/JSON-IR UGate and
appending it to a new public circuit converted native matrix coordinates twice.
In-memory IR retained the temporary marker and concealed actual JSON behavior.
Simple diag probe max0.19866933; permanent asymmetric QR cases seed9696, matrix
phase.17 and receiver globalphase.23 record14 failures (source/copy/inverse/
power/repeat/open/closed times QPY/JSONIR) in qc1-w2-detached-red-main.

The existing shared standard_from_record factory already receives decoded
native matrix coordinates from both native format readers/canonical checks.
It now marks that validated UGate as native; matrix values and standard wire
formats are unchanged, no private sidecar/schema/registry is added. This is a
proved construction context, not inference from an arbitrary operation name.
Native detached reuse and14 actual SDK detached-derivative comparisons pass.
The new public transport probe now exercises real JSON encode/decode. Main/
Alternate targeted698pass/2originalxfail,exit0,9.90/9.89s before final comment
freeze; do not reuse its manifest as final broad-source proof.

Latest1575-file W2 candidate SHA
e3ee8aa5663e17af096abbe78cb1ada1c9c98e9f9c83b8c84f9121f74c7e5729,
exact archive qc1-w2-selected-source-baseline.tar.gz SHA
50cf3fba5ae8c761b97d9527c50e7038c897aea5e6f0a72b436ae41d93decd70.
Latest strictSDKfree557pass,exit0,51.16s and5actual examples exit0, all source
unchanged. Latest broad45726/62154 and TF-MPS9373/41363 sessions RUNNING;
do not mutate selected roots, duplicate runs or claim terminal acceptance.
Receipts are qc1-w2-final-*. All original R2 gates OPEN/full replacement
ACTIVE/INCOMPLETE/local-only unchanged.

### QC1 Latest Terminal Evidence: Supported Subset Ready For Review

All six W2 sessions are terminal, exit0. Main/Alternate affected broad gates
each6649passed/4originalxfail/0failed/0skipped (410.49/410.73s). Main/Alternate
TF-MPS gates each207passed,0failed/skip/xfail (368.43/368.12s), including the
original four actual100-wire mixed-AD cases and true-third refusal. Strict
SDK-free557passed,0failed/skip/xfail (51.16s); five actual native numerical
example mains completed, hardware0. Receipt names: tmp/r2o3b-qc1-w2-final-*.json
and corresponding JUnit XML. Every selected before/after manifest equals the
current1575-file SHAe3ee8aa5663e17af096abbe78cb1ada1c9c98e9f9c83b8c84f9121f74c7e5729.
Exact archive SHA50cf3fba5ae8c761b97d9527c50e7038c897aea5e6f0a72b436ae41d93decd70.
Original28-section matrix script SHA remains
1d93b127aa5783541178d6c852ecec3457fac89694248dd2cd270dad989a7798.

Actual same-process Main SDKs are Qiskit2.4.1/PennyLane0.44.1, Alternate
2.6.0/0.42.3. Both use TF2.21.0; JAX/JAXlib Main0.7.1,Alternate0.6.2;
Torch2.12.0 system-site, Autograd actual origins recorded (versionNone).
Strict SDK-free has no user site and no Qiskit/PL/TF/JAX resolution/import.
Its actual NumPy is system1.26.4, not guessed from environment naming.

QC1_SUPPORTED_SUBSET_READY_FOR_REVIEW is a proposal, not acceptance or full
parity. Existing ownership-versus-upstream-alias, compound Operator origins,
arbitrary-unitary QASM synthesis/narrow basis, inverse-metadata QPY and other
inherited append conflicts remain OPEN. Original R2 FULL gates, independent
four-framework FULL, GLOBAL/68 exclusions, original28-section matrix,
ALL numerical examples, controlled legal/five origins and full Git equality
remain OPEN/NOT_RUN. No claim that selected1575-file equality is full-worktree,
staged or committed equality. Main HEAD b443430 unchanged; no staging/commit/
push/fetch/PR/install/auth/cloud/hardware/Studio/Router changes in this batch.
Full replacement remains ACTIVE/INCOMPLETE.

### QC1 Review Closed; QC2 Actual Public Operator Reds

The completed QC1 terminal reply accepts only
QC1_PUBLIC_UNITARY_VERIFIED_SUPPORTED_SUBSET from supplied local receipts,
not independent inspection/full SDK completion. Its complete next QC2 prompt
and ending were read and archived in the existing received-prompt document.

QC2-A added probe_operator_composition_public_parity.py before production
changes: Main2.4.1 and Alternate2.6.0 each56failed/5passed,0skip/xfail,exit1,
0.81/0.83s. Receipts tmp/r2o3b-qc2-a-red-{main,alternate}.json/xml, selected
1576-file manifests before==after. Independent complex QR inputs and explicit
little-bit local embedding establish upstream compose/default/front/dot/kron
semantics. Raw/circuit/from_circuit/mixed origins and qargs(2,0)/(0,2) reveal
real math differences; default raw compose maxerror1.15215995. Derived public
unitary refuses unresolved origin; direct public append refuses Operator.
Separate actual upstream checks accept all6 derived compose/tensor/expand
times unitary/append in both SDKs. Initial scratch command SyntaxError retained
as scratch failure; corrected multiline checks really executed, no test PASS
inferred from a syntax failure.

Existing native tests intentionally require default compose=A@B/front=B@A,
native qargs0-high and mixed-radix Qiskit reference front inversion. Selected
old baseline167passed/24deselected,exit0,0.87s, JUnit
tmp/r2o3b-qc2-a-native-contract-baseline.xml. No old test changed. There is one
existing Operator class; raw input has no implicit native-vs-public call
context. Universally changing defaults breaks QC2-D native-math preservation;
choosing order by matrix provenance conflates representation and API semantics.
This concrete conflict was sent for scoped direction in the authorized
conversation as QC2-A-REAL-REDS-AND-NATIVE-PUBLIC-CONTRACT-CONFLICT before
production edits. Full replacement ACTIVE/INCOMPLETE; all R2 final gates OPEN;
local-only and original matrix/source-history restrictions unchanged.

### QC2-B1 Conversion Path Before Production Edits

Explicit same-class as_qiskit_operator is authorized; native defaults and
original56-red probe stay untouched. New independent35 cases first fail
AttributeError,exit1 in qc2-b1-explicit-red-main, no fabricated supported pass.

Conversion table: raw Operator (unmarked literal) -> owned copy, no basis
permutation; proved circuit-native Operator -> one global qubit permutation
to literal public coordinates; already explicit-public -> owned copy, no
permutation. Internal dimension tuples remain high-first for existing kernels;
public dimension access reverses the descriptor order. Arithmetic convention
is a separate immutable field, never inferred from basis/source. Public
compose swaps front and maps reversed public qargs into native high-first
positions; existing contraction kernel alone performs numeric math. Tensor
keeps numeric kron(A,B), expand kron(B,A); dimension order follows actual
factor geometry, not provenance guessing. Public outputs remain literal
public-coordinate matrices. Public unitary then does its existing local-frame
execution conversion exactly once; IR/QPY continue existing native records.
No additional conversion in _new/compiler/format readers. Mixed arithmetic
conventions explicitly refuse until caller selects the same convention.

### QC2 B1--B5 Targeted Evidence And Default-Migration Impact

Earlier Main/Alternate470pass each used the first explicit candidate. Isolated
new probe really found4 imports failures; helper independence repaired and
isolated4pass/240deselected rerun completed. B5 actual7fail/35pass (qc2-b5-
resources-red-main) proves raw float tensor input/output lacked grouped
admission and derived transpose/copy/adjoint/power lacked early owner checks.
Existing numeric/admission paths now cover these; no new resource system or
MatrixFunctions change. Latest Main/Alternate each512pass/0fail/skip/xfail,
exit0,6.58/6.63s, qc2-b5-targeted-{main,alternate}.json/xml. Includes42 resource
tests: callbacks never run, no allocation on known denial, grouped dtype/
output, work/dimension bounds, typed modes, parent/child concurrent readonly
leases, escaped views, nonunitary gate refusal and legal recovery. This is
TARGETED_GREEN/NOT_ACCEPTED, not final-source B6 or R2 FULL.

Default migration impact, evidence only: native subsystem tests explicitly
assert compose A@B, qargs0-high; mixed-radix tests map opposite SDK front and
reverse dimensions/qargs, including rectangles. Production
information/channels.py:_embed_operator uses identity.compose
with the native qargs contract; a universal default switch changes channel
placement. from_circuit/native state/MatrixFunctions rely on the q0-high
representation. Other .compose users include Circuit, Pauli, sparse operators,
channels and Clifford; these are DIFFERENT types and cannot be mechanically
rewritten as Operator migration sites. Public .unitary is an execution boundary
only, after arithmetic has already occurred, so cannot infer which compose
order was intended. An explicit same-class view can select convention before
arithmetic. Bare constructor/default migration would need a separate Owner-
approved compatibility decision and impact tests, not a silent field/provenance
heuristic. Original56 default-red difference remains OPEN_DEFAULT_API_PARITY_GAP;
the original28-section matrix priority and complete native SDK goal unchanged.

### QC2 B6 Frozen Candidate In Progress

Selected1579-file SHA8b6d37db44addb9e20ae70e83aeeae2a9ff44f6f842bbb4e38760855c03c7840;
exact archive tmp/r2o3b-qc2-b6-selected-source-baseline.tar.gz SHA
cceeadd2cbc6a432f0992704c0f33af2bd3069588b7d91194c49d10557f44950,
all archive filenames/content verified. Compared with frozen QC1, only
information/operator.py and THIRD_PARTY_NOTICES.md selected old files changed;
four new tests/probes, zero removed; EVERY preexisting test unchanged.
Original matrix/workflow unchanged; Ruff F821/F841 and diff-check pass.

Latest strict SDK-free639passed,0fail/skip/xfail,exit0,51.37s;5actual numerical
examples completed,exit0; source manifests unchanged. Main original default
probe independently rerun56fail/5pass,exit1,0.73s (qc2-b6-default-gap-main),
not changed into opt-in or hidden as skip/xfail. Latest broad Main71208,
Alternate44717 and expanded TF/MPS Main93882,Alternate55540 sessions RUNNING;
do not edit selected source until terminal or count these gates PASS. Expanded
TF/MPS adds cachedRoF/defaultpfor/scalar-lowering/M2 lifecycle and managed cache
guards beyond QC1's207. All receipts qc2-b6-final-*; R2 final gates OPEN,
QC2 NOT_ACCEPTED/full replacement ACTIVE INCOMPLETE/local-only unchanged.

### QC2 B6 Latest Terminal Evidence

All six frozen8b6d37db B6 gates terminal, actual exit0. Main/Alternate broad
each6970passed/4originalxfail/0failed/0skipped (417.57/419.83s). Expanded TF/MPS
each305passed/0fail/skip/xfail (520.18/519.55s), including cachedRoF/defaultpfor/
scalar-lowering/M2 lifecycle/managedcache and original4 actual100wiremixedAD/
true-third, individually verified present and PASS in both XMLs. SDKfree639
pass/0fail/skip/xfail (51.37s), no-user-site/forbidden resolution/import empty.
Five actual native numerical example mains completed,hardware0. Each of six
source_before==source_after==current1579-file manifest; same exact archive.
Actual loaded origins/versions retained: MainQiskit2.4.1/PL0.44.1/JAX0.7.1,
Alternate2.6.0/0.42.3/JAX0.6.2, TF2.21 both, Torch2.12 system, real Autograd
origins/versionNone. JUnit broad4 skipped elements are ORIGINAL xfails, not
new skipped tests/native passes. Receipts tmp/r2o3b-qc2-b6-final-*.json/xml.

Supplementary read-only18 QPY/JSON restored Operator reentry cases for source/
fractionalpower/adjoint and compose/tensor/expand max complex error0, no source
change, not a substitute for formal244 opt-in probes. EVERY preexisting test
unchanged against QC1 archive, newdefault probe unchanged against its original
QC2-A red manifest. Native default/public56-gap remains separately OPEN.
HEAD b443430/main unchanged; all sessions terminal; diff-check/Ruff pass.

Propose QC2_EXPLICIT_PUBLIC_ARITHMETIC_SUPPORTED_SUBSET_READY_FOR_REVIEW,
not acceptance, bare-default parity or full SDK completion. Original R2
FULL/independent4framework/GLOBAL>=91.34108013033072%/68exclusions/28-section
matrix/ALLexamples/controlledlegal/fiveorigins/full frozen-worktree-staged-commit
equality remain OPEN/NOT_RUN. Selected1579 equality is not full Git equality.
Local-only/full replacement ACTIVE INCOMPLETE; no push/stage/commit/install/
cloud/hardware/financial13/Studio/Router changes.

### QC2 Accepted Bounded Scope; QC3 Handoff

The completed terminal review and ending were fully read. The reviewer accepts
QC2_EXPLICIT_PUBLIC_ARITHMETIC_SUPPORTED_SUBSET_READY_FOR_REVIEW based on
supplied local receipts, not independent source inspection. Main and Alternate
original default probes both rerun at final source56fail/5pass,exit1,0.73/0.68s;
both remain OPEN_DEFAULT_API_PARITY_GAP. Latest proof and archive untouched.

Next complete QC3 prompt archived in the existing received-prompt document:
explicit same-class native arithmetic entry and narrowly proved internal
native-callsite migration, shadow math and machine-checkable impact inventory,
resources/latest affected gates, then Owner decision materials. Actual default
convention switch remains NOT_AUTHORIZED until explicit Owner compatibility
approval. QC3 production implementation has not started at this checkpoint;
do not call it complete or reuse QC2 receipts after later edits. Full SDK goal
ACTIVE/INCOMPLETE, all R2 final gates OPEN, local-only unchanged.

### QC3 P1 Revalidated And P2 Conversion Contract

Previous goal turn made verified production/test progress (QC2), not a wait or
no-progress turn. Current main/b443430/ahead51 and selected1579-file8b6d37db
candidate revalidated unchanged. P1 actual Main/Alternate default each56fail/
5pass,exit1,0.64/0.65s; native baseline each167pass/24deselected,exit0,0.86/
0.91s. New receipts qc3-p1-*, original tests/inputs unchanged.

Before P2 production edits: explicit native selection of a legacy native raw
matrix owns the same data/dimension descriptors and DECLARES native physical
coordinates; no numerical permutation or provenance-value guessing. Explicit
public -> native uses existing reverse_qargs permutation and reversed internal
dimension descriptors (general mixed-radix/rectangular included), preserving
physical subsystem identities. Native physical -> public uses that same
existing inverse permutation/descriptors. Already-native conversion is an
owned idempotent copy. Legacy raw.as_qiskit_operator remains literal, as QC2
proved. Unresolved origins still refuse. Explicit native arithmetic operands
have a chosen physical frame, so native product/factor output origin requires
independent geometry proof before retaining native provenance; implicit legacy
compound refusal is NOT globally removed. No default convention switch.

### QC3 P2--P5 Evidence

P2 real29missing-native-entry failures preserved (qc3-p2-native-red-main),
then541pass Main/6.39s, including originalQC2 and native contracts. Native
entry/roundtrip checks cover scalar, binary, unequal mixed-radix and rectangular
dimensions; explicit native product/factor coordinates independently proved.
P3 real4fail/8pass runtime mode guard preserved (qc3-p3-callsite-red-main),
then553pass Main/6.51s after ONLY channels._embed_operator selects both
operands native. Independent high-qargs native embedding, Channel/SuperOp/Choi
front/default numerical checks pass managed/unmanaged. P4 two-branch native/
public shadow actual Main/Alternate104pass each,0.62/0.65s, including unequal
partition data/dimensions and original sameU/qargs two-version public calls.

P5 real2fail/36pass (qc3-p5-native-resources-red-main) showed conversion element
work was unchecked without a resource scope; shared existing logical work cap
now rejects before copy/permutation. No new numerical/budget system. Earlier
latest targeted Main/Alternate659pass each,exit0,7.09/7.12s, before addition of
one exact512B roundtrip lease test. New resource module now covers39scope/conversion/
forged fields/origin/width/modes/subclass/parent-child/concurrency/fault/recovery
paths, no callback, independent result ownership, no release-before-view-death.
No old test changed and no default API migration.

### QC3 P7 Default-Switch Decision Materials

Arithmetic receivers: AST enumerates83production compose/dot/tensor/expand
candidates and records complete context/source fingerprints. One confirmed
external dense Operator receiver, channels._embed_operator, is now explicit
native with runtime guard. Five Operator-internal dispatches are convention-
aware and protected by shadow/tensorpower tests. Remaining same-name APIs are
not blanket migrated. Inventory PROVEN/UNRESOLVED/NOT_APPLICABLE hints do NOT
prove Python runtime types; unresolved factory/attribute/mutable map receivers
remain visible. Valid NoiseModel APIs populate QuantumError, but externally
mutated dictionaries/subclasses are NOT certified by a lexical inventory.

Constructor/data consumers: the initial inventory records26production
constructor/factory candidates separately, NOT26approved migrations. Raw
Operator arrays retain literal numeric data; future convention changes must
not automatically permute them. Circuit-derived data and native state/operator
factories require individual representation proof. Current examples include
Gate.to_matrix/from_circuit, Gate.power, AnnotatedOperation.to_matrix,
channels._operator_data, Clifford.to_matrix/to_operator, Statevector.evolve/
to_operator, DensityMatrix.to_operator, metrics/random factories, Pauli/sparse
factories, transform gate proof and serialization validation. Existing native
Gate/power/state/channel tests prove current numbers, NOT future constructor
switch safety. All candidate constructor default migration remains UNRESOLVED.
No from_native_circuit or from_circuit default change is authorized this batch.

Risks/cost: explicit native selection owns one matrix-sized output; a live
public->native->public pair needs two distinct matrix buffers, not duplicate
representation stores. The channel migration adds short-lived owned identity
and local-matrix snapshots, plus strict existing dimension/logical-work limits;
it is not zero-allocation or zero-validation overhead. No measured end-user
latency claim is made. Before an actual default switch, validate constructor
normalization and mode initialization/_new propagation, downstream native
.data/.power consumers, raw/dynamic inputs, copies/resources, external user
code and full original matrix impact. Public direct append(Operator) remains
a separate existing ABI gap; changing compose defaults alone does not fix all
56original failures. Bare default56 tests remain unchanged and OPEN.

Decision: confirmed arithmetic receiver migration can be reviewed after latest
P6 gates; global default switch is NOT READY/NOT_AUTHORIZED because constructor
and external-code risks remain unverified and explicit Owner approval is still
required. Bounded QC3 review readiness is not full default/SDK parity. Original
R2 FULL/GLOBAL>=91.34108013033072%/68exclusions/28-sectionmatrix/ALLexamples/
controlledlegal/fiveorigins/fullGit equality stay OPEN; full goal ACTIVE
INCOMPLETE/localonly. Continue constructor proof in a later authorized step,
never permanently replace full default parity with dual-mode compatibility.

### QC3 First Frozen Candidate Interrupted For Actual Binary Red

First48edff1c1584-file archive remains exact. SDKfree724pass/51.84s and9actual
examples exit0 certify ONLY that old scope. Original default Main/Alternate
each56fail/5pass,exit1,0.72/0.75s unchanged. A separate read-only asymmetric QR
seed12401 check proves native + public and native - public both silently
accepted with native origin but physical error1.0317455788350143. This is the
existing shared binary _new/admission boundary, not a speculative feature.

Only four owned broad/TF test processes were intentionally stopped before
source edits. Main/Alternate broad each2806pass/3originalxfail,exit2, incomplete;
AlternateTF120pass,exit2,incomplete. MainTF SIGINT was handled inside TensorFlow
and produced an interrupted normalization failure rather than stopping; then
SIGTERM ended that same PID73599/session27299,actualexit143. No final MainTF
pytest JSON/XML is claimed; signal-induced F is not an algorithm verdict.
Controller receipt tmp/r2o3b-qc3-p6-interruption-controller.json records actual
exit statuses; all old handles terminal before edits. No old partial pass was
relabelled as a new candidate gate. No unrelated service/process was stopped.

Formal new binary tests qc3-p5-binary-red-main:24fail/4pass,exit1,0.13s cover
mixed modes, foreign Operator.data callbacks, forged origins and raw dtype/
output known group denial. Existing _arithmetic now qualifies mode/owners/
compatible dimensions BEFORE reads, uses existing typed refusal and shared
numeric/group allocation APIs, no implicit basis conversion or new math.
Latest Main/Alternate affected688pass each,exit0,7.38/7.41s before final4 exact
budget-success tests; same modes/scalar/current native math and old assertions
preserved. Fresh final candidate required; old48ed receipts not reusable.

### QC3 P6B Replacement Frozen Candidate

Final32binary cases pass,exit0,0.13s, including exact512B group success/256B
retained output versus511B denial before factory. Ruff F821/F841/diffcheck pass.
Latest1585-file SHAb960cf600c621001d412703a83d4255918bb5b502cfe912df9d9edbe8dc06dee,
exact tmp/r2o3b-qc3-p6b-selected-source-baseline.tar.gz SHA
b5c7245d7fdc1695e9c13f309017f0952d4a41983564e8a14c298c462bb48bea,
all filenames/content verified. QC2 old selected only Operator/channels/NOTICE
changed;6newtests/probes,0removed,EVERYpreexistingtest unchanged. New inventory
tmp/r2o3b-qc3-p6b-operator-callsite-inventory.json scans1326Pythonfiles/2373
candidates;83production arithmetic classifications and26constructor gaps
unchanged. Both original default probes unchanged, separate p6b-gap receipts.

Fresh broad Main27603/Alternate69078,TFMain12462/Alternate15770,strictSDKfree
16720,nineexamples32057 sessions RUNNING, not counted PASS. Keep selected
roots frozen until terminal; receipts qc3-p6b-final-*. No old48ed partial gate
or example result certifies latest source. Full default/global/SDK replacement
and all original R2 final gates OPEN; local-only/mainHEADb443430 unchanged.

P6B partial terminal update: strictSDKfree756passed,0fail/skip/xfail,exit0,
52.04s; all9actual numerical mains completed,exit0/hardware0. Latest original
default probes each56fail/5pass,exit1,0.71/0.75s, no expected-input changes.
These latestb960 receipts are separate from48ed/older ones. Broad/TF sessions
still RUNNING, no latest broad/TF PASS claim until actual terminal. Received
freeze review fully read/archived;32unresolved/26constructor risks remain.

### QC3 P6B Final Terminal Evidence

All6latestb960cf60 sessions terminal,actualexit0. Main/Alternate broad each
7150passed/4ORIGINALxfail/0fail/skip (422.45/422.56s). ExpandedTF/MPS each
305passed/0fail/skip/xfail (517.91/519.32s), includes original4actual100wire
mixedAD and true-third individually verified present/PASS in BOTH XMLs.
StrictSDKfree756pass/0fail/skip/xfail,52.04s; no-user-site and forbidden
Qiskit/PL/TF/JAX resolution/import empty. Nine native numerical example mains
really executed,exit0/hardware0. Every six before==after==current1585manifest,
exact b5c7245d archive unchanged. Actual gate-process origins recorded, not
inferred: MainQiskit2.4.1/PL0.44.1/JAX0.7.1; Alt2.6.0/0.42.3/JAX0.6.2,
TF2.21 both; Torch2.12system; actualAutograd paths/versionNone. SDKfree actual
NumPy1.26.4system. Records tmp/r2o3b-qc3-p6b-final-*.json/xml.

Both latest original default probes56fail/5pass,actualexit1,0.71/0.75s remain
OPEN_DEFAULT_API_PARITY_GAP; not hidden as skip/xfail or changed into opt-in.
Every preexisting test byte-identical to QC2 frozen baseline. Latest inventory
1326Python fingerprints all match current selected source; classifications
still6PROVEN/45NOT_APPLICABLEhints/32UNRESOLVED;26constructor default risks
UNRESOLVED. Original matrix SHA1d93b127 unchanged, no workflow changes. All
old48ed stopped runs and true red tests retained, never substituted as latest
proof. Ruff/diffcheck pass, mainHEADb443430 unchanged/no commit or push.

Propose QC3_NATIVE_CALLSITE_MIGRATION_READY_FOR_DEFAULT_SWITCH_REVIEW only as
bounded arithmetic-callsite and explicit-native prep review, NOT permission or
readiness for actual global default switch. All constructor/external-code/
dynamic-source risks and original56 remain. Original R2 FULL/GLOBAL>=
91.34108013033072%/68exclusions/original28matrix/ALLexamples/controlledlegal/
fiveorigins/fullfrozen-worktree-staged-commit equality OPEN/NOT_RUN; selected
1585 equality is NOT fullGit equality. Full independent native SDK replacement
ACTIVE/INCOMPLETE, local-only/no cloud/hardware/financial13/Studio/Router change.

### QC3 Bounded Review Accepted; QC4 Handoff

The complete QC3-P6B-LATEST-TERMINAL-REVIEW response and ending were read.
QC3_NATIVE_CALLSITE_MIGRATION_READY_FOR_DEFAULT_SWITCH_REVIEW accepted only
as supplied-evidence supported development checkpoint, NOT actual global
switch readiness/authorization, SDK-wide completion or independent inspection.
All latest1585-fileb960 receipts and old true-red/interruption evidence retained.

Next complete QC4 prompt archived in existing received-prompt doc: prove real
Operator raw/Circuit/Gate/state/density/Clifford construction/data origins and
consumer math, repair only actual source/provenance red in existing boundaries,
then strict ownership/resources and latest affected proof. No default switch,
secondOperator/batch26construction migration/new ctor without necessity proof.
Original56 arithmetic defaults,32dynamic receiver hints,26constructor future
risks/all R2 full gates remain OPEN. QC4 implementation not started at this
checkpoint; don't reuse QC3 proof after its future source edits. Full goal
ACTIVE/INCOMPLETE/localonly unchanged.

### QC4 State-Derived Operator Origin Repair

Current local HEAD remains b443430, main ahead51 with preexisting dirty files;
no Git mutation or remote/hardware invocation. QC4 is PARTIAL/NOT_ACCEPTED.
Raw Operator(ndarray) remains a literal matrix, not an inferred state origin.
Actual Native and Qiskit2.4.1 lack Operator.from_instruction; no API added.

Paired asymmetric H/RY/CX/RZ/RY/S circuits with global phase .13 establish
complete native-high state amplitudes versus actual public-low amplitudes
(maximum3.38e-16), but state/density .to_operator lost origin. Native projector
was correct; explicit public conversion was wrong by0.1502835076937487.
Formal Main2.4.1/Alternate2.6.0 before-repair receipts each24failed/23passed,
exit1, retained under tmp/r2o3b-qc4-h2-red-*. Two failures concern foreign
receiver properties; the other22 concern numeric origin/derivations.

Minimal repair: exact native state receiver/buffer/dimension/shape and existing
limits/graph admission at the two state->Operator boundaries; retain existing
native matrix-basis marker. Statevector keeps one owned outer-product output;
DensityMatrix keeps its borrowed source alias. No arithmetic-mode field is set.
The former general-native-origin admission requirement for an explicit-native
arithmetic field is removed: basis and arithmetic are distinct. All exact
Operator/type/dtype/dims/shape/width/graph/limit checks remain. Existing mixed-
radix reversal handles physical coordinates; no new converter/store/registry.

Latest same-source targeted Main/Alternate each108passed/no skip or xfail,
exit0: tmp/r2o3b-qc4-h4-h5-{main,alternate}.{json,xml}. Earlier information-only
Main2083passed is a narrower, earlier-source checkpoint, not latest full proof.
The first expanded targeted run107passed/1failed used random_unitary(2) but
wrongly expected a4x4 output. This new test's argument was corrected to the
actual total-dimension API(4), preserving tolerance; production was not changed.

New tests independently enumerate complete complex projector and mixed-radix
coordinates; no probability-only or global-phase masking. They cover1--4qubit
and(2,3)/(3,2) states; copy/adjoint/power; density alias mutation vs public
snapshot; exact and-minus-one output budgets; escaped views; graph/data
callbacks; readonly concurrent construction; injected numeric failure/recovery.
Escaped owned arrays remain legal after ResourceScope exits by the existing
storage lifetime contract; there is no fabricated expired-owner rule.

Nonunitary projectors are refused atomically by public unitary. Their genuine
Householder reflection I-2P traverses native/public arithmetic, public unitary,
existing Compiler, SV/MPS, actual JSON IR/QPYv13 and detached-owner reuse,
checked against actual SDK plus independent local matrix embedding. Clifford
labels/Pauli/sparse/raw-Kraus/random/metric probes keep their proved literal
output rather than assigning universal native provenance.

H1/H4 audit remains bounded: old26AST count is16Operator constructors plus
8native from_circuit plus2explicit-native selectors; internal self.from_circuit
adds a27th separate candidate. Counts are not runtime migration approvals.
Native state/evolution, channel embeddings, Gate power, serialization and
definition-proof data consumers must retain high-first numbers. Clifford
tableau synthesis maps native circuit wires before returning public-literal
matrix data; Pauli/sparse labels and random numeric matrices are literals.
Polymorphic Gate/AnnotatedOperation/channel factory inputs and raw matrices
with external caller expectations remain UNRESOLVED for a future constructor
default switch. No mechanical migration of these candidates was performed.

Latest full affected two-environment/TF-MPS/strict SDKfree/nine-example gates
are pending at this append. QC3 receipts cannot certify the changed source.
Original56 default-call arithmetic parity and all R2 final gates remain OPEN;
full independent Qiskit/PennyLane replacement remains ACTIVE/INCOMPLETE.

QC4 H4 follow-up found two additional concrete preexisting construction reds,
not repaired by the state factory change: native circuit-derived annotation
inverse -> Operator loses origin (whole-matrix error1.090089347), and native
Circuit -> Kraus -> Operator loses origin (whole-SuperOp error0.90230993).
Formal corrected Main/Alternate probes each2failed/0passed, exit1, preserved
as tmp/r2o3b-qc4-h4-open-origins-corrected-*. They remain explicitly OPEN and
are not included in any green-gate pass total or hidden with xfail.

The first channel diagnostic incorrectly required an exact matrix phase from
an SDK Kraus decomposition. Its original failed receipt is retained. The
corrected channel oracle compares the FULL complex SuperOp against independent
kron(U.conj(),U) and actual SDK SuperOp(Kraus(public)), where Kraus gauge is
not a physical channel difference. The annotation oracle still requires full
matrix/global phase equality. Native matrix math passes before each final red.

Blindly replacing AnnotatedOperation's raw matrix constructor with
Operator(resolved_gate) is NOT proved: raw UnitaryGate and circuit-derived
gates have different input origins, while resolution may discard that origin.
Channel conversion/copy paths likewise need real per-source propagation, not
blanket Kraus tagging. These H4 defects prevent QC4 acceptance irrespective of
the state-factory affected regression result. Next work remains original QC4,
not a new feature/safety stage, and global defaults remain unchanged.

#### QC4 Bounded Constructor/Data Consumer Classification

Reenumerated AST candidate inventory:
tmp/r2o3b-qc4-state-constructor-candidates.json,1330Pythonfile fingerprints,
2410candidates globally. The27rows below are individual relevant production
source callsites; status proves only the stated current source/math path, NOT
approval to change any constructor/default ABI. Dynamic inputs and all external
users remain unverified. Multiple identical expressions occur in separate
managed/unmanaged branches and are not silently deduplicated.

| Source / Callsite | Current Classification | Source / Runtime Evidence And Remaining Boundary |
| --- | --- | --- |
| AnnotatedOperation.to_matrix, raw Operator | UNRESOLVED | Native-derived inverse red; literal base differs; H4B required |
| Gate.to_matrix, from_circuit(definition) | UNRESOLVED | Native definitions tested by bridge/Gate suites, but raw literal wrappers differ |
| Gate.power, Operator(to_matrix).power | UNRESOLVED | Existing numeric integer/fractional tests pass; polymorphic origin not carried by this raw constructor |
| channels._operator_data, managed from_circuit | PROVEN_NATIVE_DEPENDENCY | Closed native Circuit -> high-first matrix, native channel tests; current output origin is then lost |
| channels._operator_data, unmanaged from_circuit | UNRESOLVED | Native input proved, duck-typed foreign operations objects not a closed origin proof |
| channels._embed_operator, identity Operator | PROVEN_NATIVE_DEPENDENCY | QC3 explicit native embedding, independent channel matrix oracle |
| channels._embed_operator, identity native selector | PROVEN_NATIVE_DEPENDENCY | Same existing selector/convention guard and owned-buffer cost |
| channels._embed_operator, local matrix Operator | PROVEN_NATIVE_DEPENDENCY | Native local coordinates; raw constructor itself does not infer origin |
| channels._embed_operator, local native selector | PROVEN_NATIVE_DEPENDENCY | Explicit high-first composition and resource tests |
| channel.tensorpower, zero-power unmanaged scalar | NOT_APPLICABLE | 1x1 identity has no subsystem permutation; no default arithmetic invoked |
| channel.tensorpower, zero-power managed scalar | NOT_APPLICABLE | Same 1x1 identity with existing ledger admission |
| channel.to_operator, raw Operator(kraus matrix) | UNRESOLVED | Raw literal path passes; Circuit-derived full-SuperOp red remains |
| Clifford.to_matrix, from_circuit(mapped circuit).data | PROVEN_NATIVE_DEPENDENCY | Tableau mapping reverses circuit wires before existing native matrix execution |
| Clifford.to_operator, raw matrix Operator | PROVEN_PUBLIC_COMPATIBILITY | HS/SX/IHS actual SDK full matrices match literally; not a universal native tag |
| DensityMatrix.to_operator | PROVEN_NATIVE_DEPENDENCY | Native data/dims/borrowed alias, mixed-radix full matrix and public snapshot proof |
| metrics._as_choi, raw Operator(channel) | UNRESOLVED | Numeric literal tested; arbitrary foreign/data factories not source-qualified |
| process_fidelity, identity target Operator | PROVEN_PUBLIC_COMPATIBILITY | Coordinate-invariant identity, independent abs(trace(U))**2/d**2 proof |
| Operator.__init__, self.from_circuit | PROVEN_NATIVE_DEPENDENCY | Actual1--4wire constructors preserve native numbers and qualified circuit provenance |
| random_unitary, raw numeric Operator | PROVEN_PUBLIC_COMPATIBILITY | Numeric literal plus unitarity/full channel metric tests, not seeded upstream distribution parity |
| random_hermitian, raw numeric Operator | PROVEN_PUBLIC_COMPATIBILITY | Numeric literal plus complete Hermitian and actual SDK raw Operator comparison |
| Statevector.evolve, from_circuit | PROVEN_NATIVE_DEPENDENCY | Existing bridge full complex nontrivial-state/local-qargs oracles require high-first data |
| Statevector.to_operator | PROVEN_NATIVE_DEPENDENCY | Native outer product, one owned buffer, mixed-radix/public conversion and derivations |
| Pauli.to_instruction, Operator(to_matrix) | PROVEN_PUBLIC_COMPATIBILITY | Literal XY/YZI/IXY matrix construction; downstream native Instruction is not full public gate parity |
| sparse.to_operator, raw matrix Operator | PROVEN_PUBLIC_COMPATIBILITY | Actual SDK string-label/coefficient full matrix equality; no wire-origin inference |
| serialization roundtrip, original from_circuit.data | PROVEN_NATIVE_DEPENDENCY | Native exhaustive complex execution proof, existing IR/QPY tests |
| serialization roundtrip, restored from_circuit.data | PROVEN_NATIVE_DEPENDENCY | Same native coordinate requirement; no public conversion/extra selector needed currently |
| transform definition proof, from_circuit.data | PROVEN_NATIVE_DEPENDENCY | Existing bounded opaque-matrix complete phase proof uses native definition coordinates |

No selector is added mechanically. For the native .data consumers, a future
constructor that returns public coordinates would require explicit approved
boundary migration, not raw-data reversal guessed at each callsite. Existing
native selectors allocate a matrix-sized owned buffer; adding them everywhere
would add snapshots/work/cap pressure. Raw numeric power is coordinate-agnostic
but derived provenance/public reuse is not; passing power tests do not close
Gate/annotation construction origins. H4B's two reds remain blocking QC4.

#### State-Factory Frozen Regression Terminal Results

All six owned gate sessions are now terminal; no test process is intentionally
left running. Selected1589-file manifest SHA256:
dd37347697b787596e02379765688482200d810bef11fac19e68bf983ad6fbc8.
Verified exact selected-source archive:
tmp/r2o3b-qc4-state-source-baseline-clean.tar.gz,
SHA256 f92dd1e7036a84d4d2b81f0e8457a9dfee8d3177d7b077ccbcd05893b6cfb029.
The initial archive also includes macOS AppleDouble metadata entries; every
selected source file hash matches, but its total member set is not the exact
manifest. It is retained and superseded for exact-set proof by the clean one.

Receipts tmp/r2o3b-qc4-state-final-*.json/xml:
- broad-main:7258passed/4ORIGINALxfail/0fail/skip,422.49s,exit0.
- broad-alternate:same7258/4,423.36s,exit0.
- tf-mps-main:305passed/0fail/skip/xfail,520.85s,exit0.
- tf-mps-alternate:same305,520.18s,exit0.
- sdkfree:805passed/0fail/skip/xfail,52.24s,exit0.
- examples:9actualnumericalmainscompleted,exit0,hardwaretasks0.

All six before==after==current manifests independently checked; same-process
versions/import paths retained. Main Qiskit2.4.1/PL0.44.1, Alternate2.6.0/
PL0.42.3; TF2.21/NP2.4.6/SciPy1.18.1; actual JAX/JAXlib0.7.1/0.6.2 and
Torch2.12. SDKfree/examples import actual NumPy1.26.4 with SDK/TF/JAX resolution
absent and forbidden imports empty. Four original TF100wire actual mixedAD
IDs and true-third refusal individually verified PASS in each305-case XML.
All preexisting tests remain byte-identical to QC3 frozen source. Four broad
xfails are the unchanged original2symbolicQPY,1QASMstandard-name and1public
genericGate-mutation cases; no new xfail. RuffF821/F841 anddiffcheck pass.

Latest default-gap Main/Alternate still56failed/5passed,exit1, records
tmp/r2o3b-qc4-state-default-gap-*. H4 annotation/channel source reds remain
separate2failed receipts, not folded into these7258passed totals or declared
outside requirements. The state-only broad freeze started before the complete
H4B priority reply arrived; these terminal runs certify ONLY this state-factory
candidate, not completed H6 or QC4/H4B acceptance. Next source edits require
fresh targeted and later frozen proof. No defaultABI switch/Git/cloud/hardware/
financial13/Studio/Router/install/auth/tag/release mutation. Fullgoal/R2 remain
ACTIVEINCOMPLETE/OPEN as before.

The complete state-factory terminal review and ending were read and archived.
It confirms the supplied bounded regression evidence, not independent source
inspection or QC4/H4B acceptance. Next originalH4B order: annotation source
repair first, Circuit-derived Kraus source second, separately proved against
raw literal inputs and resource/owner boundaries, then fresh final gates.
No remaining actual math failure is redefined outside the full SDK goal.

### QC4 H4B Annotation And Channel Source Repair

Previous goal turn was verified progress (state-factory repair and actual
terminal gates). Local HEAD remains b443430/main ahead51/preexisting dirty;
no Git/remote/hardware/UI/auth/install changes. New work stays original QC4.

Original H4B two-red probe is unchanged. Reproduced Main2failed before edits;
prior same-source Alternate2failed retained. Annotation repaired first by
sharing the existing finite matrix-owner origin classifier with its resolved
matrix factory, without replacing numeric data or adding a second execution.
Raw unitary None/little remains literal, Circuit-derived output native.
Annotation-first Main89passed/1failed: only channel red remained. Then channel
source propagation closed that red; Main Information+probes2095passed. All
records are under tmp/r2o3b-qc4-h4b-* and are earlier-source checkpoints.

Existing Channel classes/factories carry the existing native/unresolved origin
enum, readonly once published. Sources are qualified native Circuit/Operator/
Channel objects; raw arrays/lists remain literals. Copies and six existing
representations retain source basis; no global array registry/second store or
numeric channel algorithm. Native .data and column vectorization unchanged.
Binary mixed origins are unresolved rather than inferred. Native receiver,
matrix/factor shape, dtype, dimensions, canonical aliases and managed graph
are admitted before source fields can invoke foreign callbacks/copies.
General multi-Kraus maps still refuse to_operator when not a unitary map.

The first new annotation lifetime test used a nonexistent receipt key,
peak_live_memory_bytes:3passed/1KeyError, retained. Corrected only that new
test to the actual peak_memory_bytes API;4passed. Source repair/tolerances
were not changed for this test setup error.

### QC4 H4C Source-Proved Hybrid Matrix Coordinates

After H4B closed its original two reds, raw-controlled annotations exposed a
real adjacent source gap. Proposal and full review approval archived in the
existing received-prompt document. This is original QC4-H4B continuation, not
a new SDK stage/default-arithmetic switch. Exact raw UnitaryGate(origin=None)
and a bounded validated ordered modifier chain are the only new source domain.
Unknown wrappers/foreign/dynamic bases are not inferred into that domain.

Independent functions enumerate all control/target basis bits and define:
hybrid h=Cbig*2**k+Tlittle; public p=Tlittle*2**c+Clittle;
native n=Cbig*2**k+Tbig. Both row and column maps are proved bijective. Public
conversion MOVES registers as well as reversing control significance; it is
not just a control-bit reversal. Main/Alternate original56-case evidence each
44failed/12passed before production changes:32typedrefusals and12wrong public
matrices. Every native hybrid matrix and independent actual-SDK oracle passed
before the final public-conversion assertion. Receipts
tmp/r2o3b-qc4-h4c-hybrid-before-* retained, with identical inputs/tolerances.

Same Operator now carries finite hybrid basis + readonly literal-target width;
control width follows checked qubit dimensions. Existing owned qubit permutation
path is shared, not a new numerical executor or dense permutation matrix.
Legacy .data/default arithmetic remain unchanged. Explicit native/public views
own one converted matrix, drop hybrid metadata and are value-idempotent.
copy/adjoint/power preserve proved coordinates; unsupported repartitions and
unproved mixed arithmetic refuse rather than laundering the descriptor.
Direct Channel(hybrid) requires existing native/public selection, not a guessed
channel coordinate basis. The goal still requires eventual no-opt-in SDK parity.

Constructor Operator(annotation) and bare public unitary normalize this finite
representation exactly once. Full phase-sensitive tests cover1/2controls,
1/2targets, open/closed states, seven modifier orders, nested annotations,
integer/fractional powers, immutable/forged descriptors, equal/minus-one memory,
readonly concurrent views, parent-child ledgers and injected copy/permutation
fault recovery. Raw gate payloads are qualified before .definition callbacks.
This structural/source validation is NOT authentication against arbitrary
Python private-field mutation/object.__setattr__ privilege.

Public execution keeps U/qargs/label as supplied: Operator(annotation) ->
unitary or legitimate append(UnitaryGate), Compiler, complete SV/MPS complex
amplitudes and standard JSON IR/QPY13 matrix transport/detached reuse pass
targeted probes. No private descriptor appears in serialized payloads. These
matrix transports do NOT prove arbitrary modifier serialization/full annotation
interoperability. The earlier two refusal assertions in this turn's new eight-
case probe were replaced by actual public parity after the new formal red/repair;
no preexisting state-baseline test is changed, no xfail/tolerance weakening.

Targeted Main/Alternate each229passed before two final fault tests; previous
Core+Information+probes each3345passed91.69/92.57s before final raw-root guard.
Latest final fault/resource Main70passed. These are development checkpoints,
not later-source/full-gate claims. Six latest frozen gates are RUNNING at this
append and must reach terminal before review. Selected1595-file SHA256:
852b9cdf3ea1837e728780cc7f9ed26eba1943b3c2d90a7ae9047476bb8a6960.
Exact-set source archive tmp/r2o3b-qc4-h4c-source-baseline.tar.gz,
SHA256 a5f16ea8bba027c1142ad6ad1f2b2d415d1a4fb6121edf8fbf0e171d5cd76166.
Old preexisting tests byte-identical to state-factory baseline; production delta
only operator.py/channels.py/core annotated_operation.py/public_circuit.py and
notices. No default ABI switch. QC4 NOT_ACCEPTED/fullreplacementACTIVEINCOMPLETE;
default56/alloriginalR2 final gates remain OPEN.

#### QC4 H7 Remaining Source And Default Boundaries

No no-opt-in global default migration is authorized or claimed. Current fresh
default-gap probes Main/Alternate still56failed/5passed exit1, unchanged test
inputs/expectations. Records tmp/r2o3b-qc4-h4c-default-gap-* share the latest
1595 source. Explicit view success is not those default public API successes.

Read-only current-runtime diagnostic confirms another precise open path:
Kraus(Operator(raw-controlled-annotation)) currently raises channel_matrix_origin,
where actual Qiskit Kraus(public annotation Operator) accepts dimensions(8,8).
Existing .as_native_operator()/.as_qiskit_operator() selections permit(8,8)
construction, but this explicit-selection requirement is an OPEN full-parity
gap, not the requested final SDK endpoint. No new code change was made during
the freeze to hide or prematurely repair it. Direct Gate/Generic wrapper
source origins, arbitrary modifier serialization, dynamic aliases/external
users and broader native/public constructor migration still need proof.

The complete latest freeze review was read/archived. Keep1595source unchanged;
all six gates need terminal manifests/JUnit/import evidence. Strict SDKfree
has already completed932passed exit0 with SDK/TF/JAX resolution/imports absent;
nine actual numerical examples completed exit0 without hardware. Main/Alt
broad and TF-MPS remain running at this append. No QC4 acceptance proposal yet.
All original R2 FULL/independent4frameworkFULL/GLOBAL>=91.34108013033072%/
68exclusions/original28matrix/ALLexamples/controlledlegal/fiveorigins/full
worktree-staged-commit equality remain OPEN/NOT_RUN. Selected1595 equality is
not full Git equality. Full native replacement remains ACTIVE/INCOMPLETE.

#### QC4 H4C Final Frozen Terminal Proof

All six owned sessions reached terminal exit0, no needed execution left running.
Same1595 source before==after==current verified independently for all receipts:
tmp/r2o3b-qc4-h4c-final-*.json/xml. Selected SHA852b9cdf3ea1837e728780cc7f9ed26
eba1943b3c2d90a7ae9047476bb8a6960 (line-wrapped here only).
- Main broad7489passed/4unchangedoriginalxfail/0fail/skip,428.96s.
- Alternate broad same7489/4,427.86s.
- MainTF-MPS305passed/0fail/skip/xfail,520.13s.
- AlternateTF-MPS305passed/0fail/skip/xfail,519.21s.
- StrictSDKfree932passed/0fail/skip/xfail,52.11s.
- Nineactualnumericalexamplescompleted exit0, hardwaretasks0.

Actual in-process Main Qiskit2.4.1/PennyLane0.44.1 and Alternate2.6.0/0.42.3
origins retained, native repo path correct; NP2.4.6/SciPy1.18.1/TF2.21.0/
Torch2.12/JAX+JAXlib0.7.1/0.6.2. Strict SDKfree/examples actualNP1.26.4,
SDK/TF/JAX resolution false and forbidden imports empty. Each TF XML confirms
originalfour actual100wiremixedAD and true-third refusal individually PASS.
Broad XML individually verifies originalH4Btwo,56hybridmatrixparity cases,
2nestedhybridcases and36publicexecution/standardtransport cases PASS. Four
xfail nodeIDs/type exactly match the state-factory baseline; no new xfail.
RuffF821/F841 anddiffcheck pass; matrixworkflow/HEADunchanged. Reenumerated
AST inventory1336Pythonfiles/2442candidates retains dynamic/default migration
gaps; no AST total is claimed as runtime type proof or approved migration count.

Maximum proposed result is QC4_OPERATOR_CONSTRUCTION_ORIGIN_SUPPORTED_SUBSET_
READY_FOR_REVIEW, bounded to the actual tested factories/representations. It is
NOT no-opt-in default parity, full annotation serialization, all constructors,
external-user compatibility, global default-switch readiness or full SDK goal
completion. Current default56failed/5passed persists on both actual SDKs.
Direct bare-hybrid Channel construction remains the concrete H7 gap above.
All original R2 final gates OPEN/fullgoalACTIVEINCOMPLETE/localonly unchanged.

Complete H4B/H4C terminal review and ending read/archived. Bounded
QC4_OPERATOR_CONSTRUCTION_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW accepted
from supplied evidence, NOT independent inspection/QC4done/defaultparity.
Original QC4-H4D next: actual bare hybridOperator->Kraus public red, then one
owned hybrid->native snapshot at existing admitted Channel boundary, native
source propagation without user opt-in. Require actualdualSDK/fullSuperOp/
Choi/evolution/owner/budget proof and freshfrozen regressions. No H4D production
change yet; current1595 candidate remains the terminal-tested baseline.

#### QC4 H4D Bare Hybrid Channel Construction

Original D1 permanent public-call probes saved at
tmp/r2o3b-qc4-h4d-d1-red-{main,alternate}.json/xml: 57 failed each, exit1,
all the original channel_matrix_origin explicit-selection refusal. Actual
Qiskit2.4.1/2.6.0 accept the same raw U/modifiers/controlstates. No input
pre-permutation, opt-in substitution, skipped/xfail or tolerance relaxation.
The original two H4B source probes are unchanged.

Existing channels._operator_data now admits the exact bounded hybrid owner,
then consumes one owned as_native_operator snapshot without a second copy.
Finite new-domain coefficients are checked before allocation. Construction
publishes native origin only after numeric success; original Operator/data/
descriptor stay hybrid/unchanged. Raw literals and native Circuit-derived
operators keep prior paths. Unknown nested generalized Stinespring factors
remain refused, not silently relabeled. Existing kernels/vectorization and
default Operator arithmetic are unchanged; no new executor/origin registry.

D2 actual main/alternate each57passed exit0. D3/D4 latestfocused each337passed
exit0, including six representations/derivations, exactly-once conversion
chains, full SuperOp/Choi, independent rho evolution/noncontiguousphysicalwires,
legal multi-Kraus maps and trace preservation. First D3 test-oracle red
207passed/1failed preserved in tmp/r2o3b-qc4-h4d-d3d4-first-main.json/xml:
test-side wire labels were incorrectly reversed along with numeric storage.
Independent tensor/native agreed; actual Qiskit same physicalqargs(3,1) gives
7.1e-17 maxerror versus erroneous(2,0)0.0413. Corrected oracle, not production
math or tolerances. Source/channel copies, adjoint/conjugate/transpose/power
checked on both actual Qiskit versions; no gauge-dependent Kraus identity.

Resource proof: original hybridbuffer and normalizedsnapshot are distinct
allocations, parent/child account each actual owner once, Kraus/Stinespring
snapshot exact-nbytes success/minus1preallocation refusal, retained-view lease,
readonly3-thread construction, 54badfield/nonfinite cases, six foreignowner/
cap paths, fault-after-snapshot sixrepresentations and fault-insidepermutation
release/recovery. No private-attribute cryptographic authentication claim,
whole-API finite coverage or hidden Python allocator/RSS accounting claim.

Latest1598selected candidate frozen: SHA
b66ef07695eb4198fd1b8ba8fa7780ac9878ab9f122b4247a519a92e822cd8c5.
Archive tmp/r2o3b-qc4-h4d-source-baseline.tar.gz exactset/filehash verified;
archiveSHA4abdd69c5d49e592e6a1e634f93c535c9184b4f28dccf67163f33ec22a8cf3fb.
Sixlatestgates launched. StrictSDKfree terminal1053passed exit0 and nineactual
examples terminalexit0/hardware0. Broad2env/TF-MPS2env still RUNNING; no latest
broad acceptance claimed. Defaultprobes both terminal56failed/5passed exit1,
retained in tmp/r2o3b-qc4-h4d-default-gap-*.json/xml, same open contract gap.
RuffF821/F841/diffcheck pass. FullgoalACTIVEINCOMPLETE/R2OPEN/localonly.

#### QC4 H4D Final Frozen Terminal Proof

All six owned sessions terminal exit0; no required test process left running.
Receipts tmp/r2o3b-qc4-h4d-final-*.json/xml record same1598source before==after
==current, SHA b66ef07695eb4198fd1b8ba8fa7780ac9878ab9f122b4247a519a92e822cd8c5.
- Mainbroad7703passed/4originalxfail/0fail/skip,431.75s.
- Alternatebroad7703passed/4originalxfail/0fail/skip,432.28s.
- MainTF-MPS305passed/0fail/skip/xfail,520.11s.
- AlternateTF-MPS305passed/0fail/skip/xfail,520.47s.
- StrictSDKfree1053passed/0fail/skip/xfail,53.18s.
- Nineactualnumericalexamplescompleted exit0; hardwaretasks0.

Both broad JUnits individually verify all93newactualSDK channel probes PASS,
and all original cases retained. Four expectedfailure nodeIDs/type exactly
match H4C baseline: symbolicQPY native/public parameterindex, public-to-native
QASM standardname2, publicGenericGate directindexmutation. No oldtest modified,
newxfail introduced or missing test relabeled as implemented. New native math50
and resource71 cases all actual PASS, including in strict SDKfree environment.
Each TF XML individually verifies originalfour100wireactualmixedAD cases
(square/exponentialcubic,forward_reverse/reverse_forward) plus true-third
typed-refusal PASS; no substitute graph or fabricated zero.

Actual in-process MainQiskit2.4.1/PL0.44.1, AlternateQiskit2.6.0/PL0.42.3;
native import path remains this repo. Both NP2.4.6/SciPy1.18.1/TF2.21.0/
Torch2.12.0, JAX+JAXlib0.7.1main/0.6.2alternate. StrictSDKfree/examples
python-s/no_user_site, actualNP1.26.4, SDK/TF/JAX find_specFalse and forbidden
imports empty verified. Originaldefault probes still56failed/5passed exit1
each; exactfailure nodeIDs unchanged fromH4C. Fulldefaultmigration NOT_READY/
NOT_AUTHORIZED. Native raw .data/high-first ABI is not claimed to be default
public matrix identity, even when complete physical maps agree after output
coordinate comparison. Sourcepermute-once is not a silent global ABI switch.

Only channels.py + THIRD_PARTY_NOTICES changed among1595oldselected files;
three new tests/probe files added. Matrixworkflow/HEAD unchanged at b443430ec3
eb7eac418c22814e08fe6d940bf099 (linewrap only), no stage/commit/push/fetch.
No Studio/Router/install/vendor/auth/TLS/cloud/hardware/financialhistory edits.
Maximum proposal QC4_HYBRID_CHANNEL_CONSTRUCTION_SUPPORTED_SUBSET_READY_FOR_
REVIEW; not QC4done/fullSDK/no-opt-in publicarithmetic parity/allconstructors.
General unknown wrappers, channels/devices/noise/transforms/plugins/pfor/fullMPS
and real fullSDK gaps remain open. Original R2 SDKfree/Main/AltFULL,
independentfourframeworkFULL, GLOBAL>=91.34108013033072%,68exclusions,
original28matrix,ALLexamples,controlledlegal/fiveorigins/fullworktree-staged-
committedruntimeequality all OPEN/NOT_RUN. Selectedsourceequality is not full
Git equality. Full independent native replacement remains ACTIVE/INCOMPLETE.

Complete H4D latestterminal review and ending read and archived in existing
receivedprompt document. Peer accepts bounded QC4_HYBRID_CHANNEL_CONSTRUCTION_
SUPPORTED_SUBSET_READY_FOR_REVIEW from supplied development evidence, not an
independent code audit, wholeQC4/defaultparity/fullSDK acceptance. Next original
QC4-H5 requirements received: actual Gate/Clifford->Operator source/math reds,
independent2/3/4qubit Clifford phase convention, minimal admitted owner-origin
repair only if actualfailure, publicexecution/Compiler/SV/MPS/JSON/QPY/detached
reuse, resources and latest affecteddualSDK/strictSDKfree/nineexample/default56.
No new stage/defaultABI migration/Channel numerical reimplementation authorized.
CurrentH4D1598selected frozen baseline remains terminal-tested and unchanged.

#### QC4 H5 Gate And Clifford Source Audit

H4D1598/sourceb66ef076... baseline equality verified before H5. New permanent
probe_gate_clifford_operator_origins.py actualMain2.4.1/Alternate2.6.0 initially
each45failed/35passed exit1:30constructor cases coerced Clifford.__array__
tableau to rectangular complexdata,15nativeCircuitClifford.to_operator lost
origin. Rawtableau to_operator15 alreadycorrect. Gate20 fullphase cases
(raw/native,2/3qubits,base/inverse/power2/.37/repeat) alreadygreen and mathnot
modified. Originalred evidence tmp/r2o3b-qc4-h5-initial-red-*.json/xml retained.

ExistingClifford now has finite readonlynative/unresolved/None origin, with
exacttableau/type/booldtype/width/shape/symplectic/densecap/graph admission.
Existing Operator constructor dispatches qualified Clifford to actual dense
matrix, not tableau coercion. KnownCircuit/Operator origin retained only with
proved representation; rawmatrix/tableau remainliteral. copy/adjoint/conj/
power and homogeneouscompose/tensor checked; mixedsourcejoin unresolved.
No secondclass/executor/ndarrayregistry or synthesis/tableau numericalrewrite.
Clifford.to_matrix exactsynthesisphase unchanged, separate independent index
embedding oracle from H/S/Sdg/CX/CZ/SWAP. ProjectiveClifford equivalence uses
eachmatrix's own intrinsic phaseanchor, never fittedphase. This is NOT exact
QiskitClifford synthesisphaseidentity; after Operator construction complete
complexmatrix phases are checked throughout. Tableau cannot retain explicit
inputCircuitglobalphase; tests document that loss, not fabricate recovery.

Secondaryrealreds retained: nativeOperator->Clifford lostframe, explicitpublic
Operator->Instruction->Operator doublebasis, foreignGate.definition read before
owneradmission. Fixed using existingqualifiers/normalizers only. Publicpipeline
then showed18opaqueInstruction failures (191pass18fail, firsttransportreceipt).
Only explicitpublic/provedhybrid to_instruction now uses existing owned native
UnitaryGate, not opaqueMatrixmetadata-onlyInstruction; defaultlegacycustom
Instruction behavior untouched. Standardtransport requires no newQPY/IRformat
or sidecar, native.data/defaultarithmetic untouched. ExtraGate copies and unitary
validation workspace are real costs, not a one-total-buffer/no-copy claim.

Latestpre-R1 focused345pass each, after original45/secondary7/transport18 reds.
One3failure forgedGate fixture triggered np.full->__array__ in testsetup before
production; receipt342pass3fail retained. Fixed objectslot fixture construction
only, no tolerance/math changes. Owned source/output, foreignfields/callbacks,
malformeddims/dtype/definition, work/memory exact andminus1, peakworkspace,
parentchildleases, readonlyconcurrency, sourceMutation/faultrelease/recovery
all targetedpass. Initialfinite source5ba5edee...1601 archive exactset verified.

#### QC4 H5 Mixed-Radix R1 Correction

Readonly frozenaudit found actual newsource propagation error: nativeOperator
with mixed/quditpartition was incorrectly carried as binary-native Clifford.
Diagnostic(4,)projectiveerror1.4142, then formal(4,),(2,4),(4,2) actual9failed
eachSDK saved tmp/r2o3b-qc4-h5-mixedradix-red-*.json/xml. These are real numeric
errors, NOT globalphase freedom. ActualQiskit.from_operator accepts partitions;
directQClifford(QOperator) raisesTypeError (nativector extension not claimed as
Qiskitpublicctorparity). Independent radixindex enumeration proves each source
as_qiskit_operator map; these partitions are NOT one generic totalbitreverse.

Before edits, exactfourowned runners identified viaPID+fullcmd+evidence paths
83024/83043/83045/83047; sentSIGINT onlythese. Re-polled originalhandles until
terminalexit2, no survivingownedprocess before sourcechange. Oldbroads1984pass
each/TF92pass each are INTERRUPTED/INCOMPLETE, retainedoriginalJSON/XML source
before==after5ba, not fullpass/not latestR1proof. EarlierSDKfree1197pass4optional
skips andnineexamples belongoldcandidateonly. Interruption was dueactualmath
defect, never observationtimeout. No restart of unconfirmedlive process.

R1 only adds a guarded existing Operator-input branch: qualifiednativeorigin+
num_qubitsNone requires finite matching2^n-square partitions BEFORE normalize;
existing mixedradix as_qiskit_operator snapshot thenexistingfrom_matrix in
literal/publicframeNone. Purequbitnative/raw/public paths unchanged. Shared
preexisting constructor extension also tested, not newAPI. Rectangular/non2^n/
mismatchedpartitions/nonfinite refusebeforecopy; nonCliffordunitary accurately
refused with temporaryframe released. No generalreshape/data/tableau/math change.
Nativeinputdata/dims untouched. Resourceproof separately counts normalizedtemp
and finaltableau, actualpeak exact/-1, childsource/output leases, concurrent
readonly; originalnative fullsynthesisphase andprojectivecontract distinguished.

LatestR1 focused363PASS each actualSDK exit0. New1601sourceSHA
0924e2500f694ce023c8cdeabed5408318d6b586af6458e7246de22687fab87e;
archive tmp/r2o3b-qc4-h5-r1-source-baseline.tar.gz SHA
ad69b61c25f04cef6ac999f4618cdbcdb7f24c20edc2a28456dfb15f8ba3087e,
exactselectedmanifest verified. Original1601candidate5ba archive remains kept.
Oldsource numeric counterexample replay from exact own-native archive (NOT
thirdparty/vendor) saved fullcomplexsource/public/synthesis/wrongoutput matrices
in tmp/r2o3b-qc4-h5-pre-r1-full-matrices.json with actual archived importorigin
and filehashes verified. Explicitly oldsource reproduction, not currentpass.

LatestR1 sixgates launched. StrictSDKfree terminal1212pass/4optionalupstream
oracleSKIPs exit0; four precise optionalQiskit tableauoracle IDs H/S/HS/SHY are
absentSDK skips, not nativepasses. Allfour actualPASS in both363focused SDK
environments. Nineexamples terminalexit0/hardware0; broad2env/TFMPS2env RUNNING.
Latestdefault56fail/5pass each exit1 retained, not xfailed/hidden. BilateralQPY13
actualMain2.4.1/Alternate2.6.0 load+dump/3sources6directions+fullamplitudes rerun
onR1source, receipts tmp/r2o3b-qc4-h5-r1-qpy-bilateral-*.json. No privateorigin
sidecar in output. Native origin paths/SDKversions/manifests retained.

Gate20alreadycorrect, no newGate matrixengine. NativeClifford/privateorigin is
structural, not authentication against arbitrary Python fieldwrites. Default
arithmetic, rawlegacy/customInstruction migration, generic/dynamic owners,
generalQPYobject/AnnotatedOperationinterop and fullSDK remain open. Newtest
counts are NOT API completionpercent. Maximum laterproposal boundedH5source
readiness only, not QC4full/default/fullreplacement done. All originalR2FULL/
coverage>=91.34108013033072%/68exclusions/original28matrix/ALLexamples/legal/
fiveorigins/fullGit3state equality OPEN. FullgoalACTIVEINCOMPLETE/localonly,
no Gitstage/commit/push/fetch/install/vendor/auth/TLS/cloud/hardware/financial13/
Studio/Router/tag/release changes. Selectedsourceequality is not fullworktree.

#### QC4 H5 R1 Final Frozen Terminal Proof

All six freshR1 sessions terminalexit0, no required gateprocess remains live.
Latest1601source before==after==current verified for everygate and extraQPY/
mixedradixtransport audit: SHA0924e2500f694ce023c8cdeabed5408318d6b586af6458e
7246de22687fab87e (linewrapped only). Receipts tmp/r2o3b-qc4-h5-r1-final-*:
- Mainbroad8043passed/4unchangedoriginalxfail/0fail/skip,442.88s.
- Alternatebroad8043passed/4unchangedoriginalxfail/0fail/skip,443.91s.
- MainTF-MPS305passed/0fail/skip/xfail,523.58s.
- AlternateTF-MPS305passed/0fail/skip/xfail,522.03s.
- StrictSDKfree1212passed/4optionalupstreamoracleSKIPs/0fail,54.09s.
- Nineactualnumericalexamplescompletedexit0/hardware0.

Both broad JUnits retain every originalH4Dcase and exactfourxfail nodeIDs/type
(symbolicQPYnative/publicparameterindex,QASMstandardname2publictonative,
publicGenericGatedirectindexmutation). New144actualSDKsource/math/transport
probe cases individualPASS, including3newmixedradixactualfrom_operator cases;
six nativefactory mixedradix cases also PASS. EachTF XML individually confirms
originalfouractual100wiremixedAD square/exponentialcubic forward_reverse/
reverse_forward plus true-thirdrefusal PASS, no replacement/skip/fabricatedzero.
Strict four skips are ONLY old optionalactualQiskit tableauoracles H/S/HS/SHY
with absentSDK importreason. Each is actualPASS in bothSDKfocused environments
andlatestbroads. They are NOT nativeimplementationpasses or missingwork hidden
as skips. Strictpython-s/no_user_site/NP1.26.4, forbiddenSDK/TF/JAX resolution
False/imports empty verified. ActualinprocessMainQiskit2.4.1/PL0.44.1,
Alternate2.6.0/0.42.3, nativeimportthisrepo; NP2.4.6/SciPy1.18.1/TF2.21.0/
Torch2.12/JAX+lib0.7.1main/0.6.2alt retained in latestJSONorigins.

Additional R1 mixedradixtransport eachactualSDK independently checks allthree
partitions through source/Compiler/JSONIR/QPY13, nativeSV/MPS fullamplitudes,
and both directions of actualSDKQPY13 parsing: receipts
tmp/r2o3b-qc4-h5-r1-mixedradix-transport-{main,alternate}.json, samecurrentsource.
The ad-hoc audit initially had shellnewlinequoting errors (no math executed),
then an inappropriate bitwise equality between independentfloating reduction
orders (2.30e-17 residual). Final audit retains bitwiseequality against actual
native synthesis and uses the EXISTING permanentindependent-oracle3e-13/rtol0
for independentmatrix reduction; no permanenttest/source/tolerance changed.
State tolerances remain4e-12/rtol0. Both actualaudits now exit0; no phasefit.
Originalpre-R1 complexnumeric archive replay stays labelledoldsourcefailure.

Originaldefault56fail/5pass each SDK remainsactualexit1 andexactfailureIDs
unchanged fromH4D. No defaultarithmetic switch or claimedno-opt-infullparity.
Only operator.py/clifford.py/THIRD_PARTY_NOTICES among1598oldselectedfiles
changed; three newtest/probefiles, allpreexistingtestsbyteunchanged. Workflow/
HEADb443430ec3eb7eac418c22814e08fe6d940bf099 unchanged, lintF821/F841/diffcheckPASS.
No stage/commit/push/fetch/auth/install/vendor/cloud/hardware/UI/history changes.
Selectedsourceequality is NOT fullworktree/staged/committed equality.

Maximum proposedresult QC4_GATE_CLIFFORD_OPERATOR_ORIGIN_SUPPORTED_SUBSET_READY_
FOR_REVIEW. Known-notclaimed: exactQiskitClifford synthesizerphaseidentity,
upstreamClifford(Operator) directctor support (actualTypeError; nativeextension),
unprovedgeneric/dynamicowners, arbitraryClifford/annotationformatrecords,
legacydefaultInstruction/frame/arithmetic migration. GeneralSDK/API/plugin/
device/noise/transforms/pfor/fullMPS andfullgoalremainopen. All originalR2final
gates FULLSDKfree/Main/Alt/independentfourframework/GLOBALcoverage>=
91.34108013033072%/68exclusions/original28matrix/ALLexamples/controlledlegal/
fiveactualorigins/fullGit3state equality OPEN/NOT_RUN. Full native replacement
ACTIVE/INCOMPLETE; no API completionpercentage inferred from testcount.

Complete H5-R1 terminalreview/ending read and archived. Peer accepts bounded
QC4_GATE_CLIFFORD_OPERATOR_ORIGIN_SUPPORTED_SUBSET_READY_FOR_REVIEW from
suppliedlocalreceipts only, not independent source/remoteCI inspection or
QC4/default/fullSDK completion. New prioritized originalR2/P4 coretask received:
QPY1 v13 Parameter/Vector UUID/index/expression interoperability. First locate
the two originalQPYxfails and actualbothSDK selfroundtrips/fourdirections,
classifyupstreamvsnative, publicformatspec/independentbinaryfixture/identity
math+AD/resources proofs, minimalactualrootfix and freshfrozengates. No second
codec/newSDKstage/default56/MPS/Clifford/UI expansion. All originalfullgoals
andR2conditions remainOPEN; current0924e250... candidate remains untouched.

#### QPY1 Reader Roots: Actual Red, Fix And Frozen Candidate

Continuation classified PROGRESS: authoritative originalred andnewtwo-version
fixtures changed nextactions, three actual native readerroots repaired. Original
two annotationtests rununmodified with--runxfail: eachSDK2failed/exit1; actual
qiskit.qpy.load atline202 loses circuitindex for nativeANDpublicwriterbytes.
Native->Native/Public->Native alreadyindex+UUID+bind/mathcorrect; noCircuit
owner/store/parameters displaypatch. PeerinitialD4misclassification corrected
fromexactfour-directionevidence, completeinitialreview+correction archived.

Newinitialreplaytests Main13fail/32pass,Alt11fail/34pass exit1,1603sourcebefore
andafterequal: tmp/r2o3b-qpy1-replay-red-*. Native op255 recursive s/e andop13
gradient wereUnsupported, sameUUID/differentname acceptedassplitidentities,
malformedframe/depth paths unsupported. BothactualSDK readers accept independent
completepublished-v13fixture r**2+(p+q)/2 andgradient q*cos(p). Main's additional
two failures are public2.4.1 partiallyboundwriter malformedstack, notnativebug.
Initialred receiptsretained. Newdiagnosis assertsactualQ2.4/native refusal,
no newxfail/skip; notclaimedas nativeimplementation/mathpass. Nativewriter
partialbound andall2.6directions retainactualmathsuccess.

Onlyexisting qpy.Reader andqpy_expressions changed, no writerrewrite/newcodec.
Boundediterativeframes, strictmarkers/zero/delimiters/onechildresult, depth+
aggregateexpressionrecord+Gatework admission, resultASTnodepreflight; native
symbolicgradientunderclampedexistingSymbolicExpressionLimits, nofinitediff.
Sharedscalar/expression/vector/baseReader UUIDadmission name/kind/root/size/
index; legalrepeatreturnsownedcanonicalparameter; sameUUIDdifferentname and
conflictingvectorsize refusedbeforesecondvectorallocation. Existingdifferent
UUID/samename boundary stayspreciseUnsupported; noUUID/name/indexregeneration.

Newnativeproofs include full12elementroot reconstruction fromsparse2/10, shared
occurrenceidentity, samepointdifferentUUIDdistinction, malformedunknownUUID,
duplicate/missingsymbolmap,truncation,badopcode,padding,hugecount/record/depth,
aggregateboundbeforemath,resultASTboundbeforebinaryconstruction, middecode
fault/ownerunchanged/recovery/no livenumericallease. PythonobjectRSS/allocator
peak is NOT claimedfrom numericalledgerzero; preflight covers logicalrecords
andASTwork. Fixed16UUIDbytes are all validUUIDbitpatterns; invalidreferences/
conflictingidentity/truncation tested, not an inventedonly-v4 restriction.

Fournativeanalytic E proofs Statevector/MPS xfull/partial bind preserveUUID/
AST throughcopy/compose/decompose/unboundCompiler; actualexpectation/Jacobian/
JVP/VJP/Hessian/HVP andfullcomplexRXmatrix. Independent f=r*r+(p+q)/2,
df=(.5,.5,2r),Hf=diag(0,0,2),cos(f) calculus; originaltolerancesunchanged.
Existingannotationcompiler/AD and100wire tests retained. Latestfocused230pass/
2originalxfail each exit0, no nativefailure/skip (noticeonlyupdatedafterthese
focusedreceipts; latestfinalgates below usefinalmanifest).

Frozen1603selectedfiles SHA4adfe5c8a0fb6a9dcbb16eee6b2c63e71126a179a7608a0c830d
2dad7d692e47 (linewrappedonly); tmp/r2o3b-qpy1-source-baseline.tar.gz SHA
e851261b67266a2236f9979433c09a132cb6b62482c952cf5e39819a137171e6. Exacttar
selectedfilehash equalityverified. RelativeH5R11601 onlyqpy.py,expressions.py,
THIRD_PARTY plus2newtest/probes; allpreexistingtestsbyteunchanged. No fullGit
staged/committed equality inferred. mainHEADunchanged, noGitmutation.

Actualrawv13 blackboxbytes savedforpublic/nativepartialbinding,originalscalar
annotation andsparsevector, plusindependentrecursivefixture: sixqpyfiles each
SDK under tmp/r2o3b-qpy1-record-{main,alternate}-*.qpy. Completeauditsorigins/
versions/selectedbeforeafter/fullmatrices/phaseoprecords in corresponding
*-diagnostics.json. Main2.4 publicpartialbind has4replayrecords finalstack2:
sin(.21)push thenq**2push, explicitnumeric sin(.21)+pop(q**2) leavesfirst
sinvalue, dividepop leaves2. BOTHpublic2.4ownreader/native reject. Nativewriter
stack1,bothreadersmathpass;actual2.6writer stack1,bothreadersmathpass. Public
2.4unusedsparsevectorUUIDsdiffer/warningskept;used2/10UUID/index/sizecorrect.
Nativeentire12rootrestored;actual2.6entirerootcorrect. Publicannotationcircuit
index0vsoperationUUIDpresent, nativeindex1 persists. No unsupportedstream
acceptedtofollowupstreambug. Additionalreadonlyboundgradient-symbolfloat
fixture is rejectedbyBOTHactualQ2.4andnative, not an establishedsupportgap.

Sixlatestfrozengates tmp/r2o3b-qpy1-final-* launched. StrictSDKfree1240pass/
4oldoptionalupstreamtableauoracleSKIPs exit0 (absentqiskit reason, notnative
passes);nineactualnumericalexamplesexit0/hardware0. Broads2env/TFMPS2env
confirmedliveoriginalhandles, awaitterminalswithoutsourceedits. RuffF821/F841
anddiffcheckPASS; runtimepython-mruffmissing, usedalreadyinstalledruffCLI,
noinstall. u/substitution variablelength/mapping semantic support remains
UNSUPPORTED/NOT_CLOSED; sourcehas no newu branch. QPY1 ACTIVE/NOT_ACCEPTED,
notnewstageorfullQPYparity. Originaldefault56/fullR2gates/SDKreplacementOPEN.

#### QPY1 Frozen Three-Root Final Terminals

Allsixoriginalsessions nowconfirmedterminalexit0, no requiredrunner/PIDlive.
Mainbroad8106pass/4unchangedoriginalxfail/0fail/skip,441.33s;
Alternatebroad8106pass/4samexfail/0fail/skip,442.85s;
MainTFMPS305pass/0fail/skip/xfail,519.69s;
AlternateTFMPS305pass/0fail/skip/xfail,518.06s;
StrictSDKfree1240pass/4oldoptionaloracleSKIPs/0fail,54.88s;
Nineactualnumericalexamplescompletedexit0/hardwaretasks0.

Everylatestgate JSON selectedbefore==after==current1603 manifest SHA4adfe5c8
a0fb6a9dcbb16eee6b2c63e71126a179a7608a0c830d2dad7d692e47 independentlychecked.
RelativeH5R1all8047oldbroadnodeIDsretained,exact4xfailIDs/typeunchanged,
63newcases individuallypassed. These includeactualmath, malformedrefusal and
explicitupstreamdefectdiagnosis tests; testcountsarenotAPIcompletionrates.
No addedxfail/skip. Latestoriginaltwo--runxfail extraeach2fail/exit1 saved
tmp/r2o3b-qpy1-final-original-xfail-{main,alternate}.{json,xml}; original
publicindexproblem remainsactualredwithlatestsource, not silentlyclosed.
Latestdefaultgap each56fail/5pass/exit1, exact56failureIDsetunchangedH5R1,
tmp/r2o3b-qpy1-default-gap-*. No defaultarithmeticchange.

EachTF JUnit independentlyconfirms EXACT originalfourhostmixedmodecases
square/exponential_cubic xforward_reverse/reverse_forward xtensorflow and
true-thirdrefusal actualPASS, no surrogate/replacement/skip. Sameprocess
nativeoriginthisrepo,TF2.21.0,Torch2.12,NP2.4.6/SciPy1.18.1,JAX/lib0.7.1Main/
0.6.2Alt; actualbroadSDKorigins Qiskit2.4.1/PL0.44.1 and2.6.0/0.42.3. Strict
python-s/no_user_site,forbiddenSDK/TF/JAXresolutionFalse/imports empty. Four
skipsONLYexistingoptionalupstreamH/S/HS/SHYtableauoracles, notnativepasses or
anSDKfreeFULLclaim. Originaltestsunchanged andfouroraclespassinactualSDKbroad.

Readonlyindependentvectorgradient audit additionallytestsop13on12element
vector sparseindex2/10, reversedmaporder, sameUUID/freeparameters/canonical
nativeowner/fullunusedroot, actualbothSDKreaders andbilateralrewrites with
fullcomplexRXmath. Actualexit0both; tmp/r2o3b-qpy1-vector-gradient-*.json/.qpy
samefrozensource. Existing2.4unusedvectorwarningkept,2.6fullrootmatches.
ActualfullrootcomparisoncheckedfromrawdiagnosticJSON: native12/12matchesboth,
public2.4unused10indicesdiffer; public2.6all12match. No lower-tolerancechange.

Only3oldselectedfileschanged(qpy.py,qpy_expressions.py,THIRD_PARTY),2newtests;
allpreexistingtestsbyteunchanged. HEADb443430ec3eb7eac418c22814e08fe6d940bf099,
workflowuntouched. NoGit/auth/TLS/install/vendor/cloud/hardware/financial13/
UI/Router/tag/release actions. LintF821/F841/diffcheckPASS. Internalprogress/
receivedpromptrecordsoutside selectedmanifest, notfullGitstateequalityproof.

QPY1threeconfirmedreaderrootsprovedinthisscope, NOTQPY1acceptance. Current
read_expression stillfixed-recordpreflight; actualu/substitution variable
length/name-keyedMAPPING semantics remainUNSUPPORTED/NOT_CLOSED. No writer
operation-history/substitutionrecord supportclaimed; nativeASTwriteremits
currentexpressionmathematics, not publicAPIcallhistory. Completedpeerfrozen
review/ending read+archivedwithfullH0-H7prompt. H0sixterminalconditionnowmet;
nextwork QPY1-H genuineu/subs binaryred+name->validatedUUIDcontext+existing
simultaneousASTsubstitution/resource/transportproofs, notnativeCircuitindexfix.
FullreplacementACTIVE/INCOMPLETE,alloriginalR2finalgatesOPEN/NOT_RUN.

CompleteQPY1-THREE-ROOTS-LATEST-SIX-TERMINALSpeerreviewandendingread+archived:
boundedQPY1_THREE_READER_ROOTS_VERIFIED_SUPPORTED_SUBSETacceptedfromlocal
receipts,noindependentsource/CIaudit/noQPY1fullacceptance. NextH1-H7unchanged,
actualu/substitutionmappingclosure;alllimitsandopenoriginalgatespreserved.

#### QPY1-H4R2 Frozen Implementation And Initial Terminal Evidence

The existing v13 reader now parses variable-length opcode 15/u substitution
mappings with !Q count and !HcH entries, exact boundaries and preflight
budgets. Keys resolve within the current expression's validated UUID/owner
context; substitutions are simultaneous. Reader support does not claim that
the writer preserves public API operation history. Modern public SDK writers
in the independent evidence serialize the resulting AST instead.

The same native ParameterExpression now owns bounded retained formal
identities separately from mathematical dependencies. Binding, substitution,
calculus, simplification and native IR preserve the finite demonstrated
contract. The AST has no artificial zero terms. Only actual retained context
is projected to standard QPY zero arithmetic on the wire; repeated rewrites
do not grow the native AST. Constant native gradient return-type parity is
still OPEN, not silently equated with public SDK float return types.

Frozen selected source: 1606 files, SHA256
32d0f44a72794f8034c84ec816167760e3059730cced2f21a8590c7a88b064ff.
Archive tmp/r2o3b-qpy1h-formal-source-baseline.tar.gz, SHA256
c3e44ecd1cc27a09b51a7dbea86d4bff9199446f16b54228c58d3b7e64b2fe0f.
Relative to the prior 1603-file checkpoint only parameters.py, qb_ir.py,
qpy.py, qpy_expressions.py and THIRD_PARTY_NOTICES.md changed, plus three new
test/probe files. All preexisting tests remain byte unchanged. One NEW test
oracle was corrected from mathematical r-only to public formal q/r identity;
the native/public UUID comparison and numerical tolerances were not weakened.

Initial final receipts tmp/r2o3b-qpy1h-formal-final-*:
Main broad: 8110 PASS, 46 missing-framework SKIP, 4 original XFAIL, exit 0.
Strict SDK-free: 1278 PASS, 1 FAIL, 4 old optional SDK oracle SKIP, exit 1.
Nine actual numerical examples completed, exit 0, hardware tasks 0.
All three selected manifests before/after equal the frozen candidate. The 50
new substitution/formal-context cases individually PASS in the Main XML.
Five no-context writer samples exactly match the earlier native QPY bytes:
single, simultaneous, nested, same-name/new-UUID and partial-numeric. Evidence
is tmp/r2o3b-qpy1h-no-context-byte-audit.json, with the same frozen manifest.
These five samples are not a claim of exhaustive byte canonicality.

The apparent 319-PASS alternate targeted receipt is INVALID as dual-version
proof: external /tmp cleanup removed pyvenv.cfg and Python package sources,
so both nominal runners actually loaded user Qiskit 2.4.1. Actual import
origins identified this. Older genuine 2.6.0 receipts remain old-source proof
only. TensorFlow/JAX were absent, causing the 46 Main skips; no skip markers
or tests were added. Fresh Alternate/TF results were NOT_RUN at this point.

The strict failure is the unchanged exact np.outer vs Statevector.to_operator
assertion for a complex projector, maximum difference about 3.10317e-17. Own
old-source extraction reproduced the same difference. A fixed 32-trial
read-only Fraction.from_float diagnostic records C/F output, strides,
offsets, alignments, exact rounding errors and all differing components:
tmp/r2o3b-qpy1h-projector-exact-current.json and *-old.json. Current source
differs in 10/32 trials, old source 12/32, both at max 3.1031676915590914e-17.
Both paths have max exact component error 2.591347828842737e-17; neither is
universally nearer the exact rational result. Near-zero ULP distances are
not relative accuracy measures. The current kernel is closer in 780 differing
components vs outer 550; old kernel 936 vs outer 660. These are predetermined
layout diagnostics, not reruns to obtain a passing gate. NumPy-version root
cause is NOT_PROVEN. No old test, tolerance or production kernel was changed.

Human permission to rebuild external test environments has now arrived.
Stable Main/Alternate venvs are being restored under the owner's cache. The
initial bundled pip certificate check failed; existing system pip 26.2 with
--python target performs verified HTTPS successfully. No trusted-host,
certificate-store edit, verification disable, Git/auth/TLS configuration,
project dependency edit, vendor, cloud/hardware, financial-history, Studio,
Router, tag or release action. main HEAD remains b443430ec3eb7eac418c22814e08fe6d940bf099.
QPY1 PARTIAL/NOT_ACCEPTED; strict FAILED/OPEN; full replacement INCOMPLETE.

#### QPY1-H4R3-E Environment Recovery In Progress

Both external pinned environments installed with verified HTTPS. Genuine
Main and Alternate focused receipts each show 332 PASS, zero fail/skip/xfail,
exit 0, source before/after equal the frozen 1606-file candidate:
tmp/r2o3b-qpy1h-rebuilt-focused-{main,alternate}.{json,xml}.
Same-process Qiskit origins/versions are actually 2.4.1 and 2.6.0. These are
new-source dual-version evidence, unlike the discarded nominal 319 receipts.

The Main all-framework sanity completed with correct TF derivative/JAX sine
and process exit 0. Alternate computed the same correct numbers but the
process exited 139 during interpreter finalization; a fixed full-import
diagnostic also exited 139. Do not treat the JSON written before shutdown as
an exit-0 receipt. The crash trace points to _mi_arenas_page_free in the
public Qiskit _accelerate binary while dropping EquivalenceLibrary.

Independent three-case diagnosis imports NO QuantumBridge or TensorFlow:
Qiskit 2.6.0 alone exits 0; Qiskit then PyArrow 24.0.0 exits -11; reverse
import order also exits -11. Receipt:
tmp/r2o3b-qpy1h-alternate-import-crash-matrix.json. This establishes an
external public-SDK/global-library interaction, not the deeper allocator root
cause or a native QPY regression. Alternate broad likewise died by SIGSEGV
in a public Qiskit collision test. No final runner JSON/JUnit was published;
its wrapper exit 245 represents child return -11, NOT partial test success.

The initial venvs reused system-site packages, just as the old test paths did.
pip check reports inherited pyquafu/NumPy and weasyprint/tinycss2 conflicts;
dependency cleanliness is NOT claimed. Those unrelated global packages must
not be uninstalled or changed. Main broad and both TF/MPS regression original
handles are still live. The proposed bounded correction is to finish live
Alternate TF first, then regenerate that SAME authorized venv without system
inheritance and install its test stack locally, excluding unrelated PyArrow
by ordinary dependency isolation, not by sys.modules masking or SDK patches.

The exact rounding diagnostic v2 adds separate nonzero-reference ULP and
exact-zero residual counts; original v1 receipts remain unchanged. The fixed
32 layout trials can change allocation-dependent counts between executions:
v2 current 8/32, old 11/32, same max difference 3.1031676915590914e-17. This
does not supersede the strict FAIL or establish a NumPy-version root cause.
No selected production/test source or project dependency file has changed.

#### QPY1-H4R3-E New Isolated Runtime And Main Terminal Results

The in-place Alternate rebuild proposal above was NOT executed. Following the
complete peer isolation review, created a fresh sibling venv at
/Users/avalok/.cache/quantumbridge/test-envs/qpy1h-alternate-isolated-20261026.
Old environments and crash evidence remain untouched. Its pyvenv.cfg has
include-system-site-packages=false; actual sys.path has neither global nor
user site-packages. NumPy/SciPy/Qiskit/PennyLane/TF/JAX/JAXlib/Torch/Autograd
origins are all inside the new prefix. PyArrow does not resolve. No packages
are hidden by import hooks or manually assembled from residual binaries.
pip check: exit 0, no broken requirements. Core versions are the requested
ones; resolved transitive dependency versions are recorded in the external
pip installation report, not silently equated with the inherited environment.

Parent-captured fixed six-process sanity: Qiskit, TF, JAX, PennyLane single
imports, then two joint checks, all actual exit 0 including interpreter
shutdown. Joint checks use real v13 QPY dump/load and RX matrix, SciPy expm,
public PennyLane default.qubit execution, TF gradient and JAX sine. Evidence
tmp/r2o3b-qpy1h-isolated-runtime-sanity.json includes complete paths and values.
This validates the new runtime only, NOT repair of the old binary combination.

Isolated Alternate focused: 332 PASS, 0 fail/skip/xfail, exit 0, with same
frozen source before/after. Genuine Qiskit 2.6.0 origin is local to that venv.
Main broad: 8156 PASS, 4 original XFAIL, 0 fail/skip, exit 0, 440.77s.
Main TF/MPS: 305 PASS, 0 fail/skip/xfail, exit 0, 503.73s.
Old inherited Alternate TF/MPS: 305 PASS, exit 0, 502.75s. It does not import
Qiskit in that gate, so this cannot repair/close its Qiskit/PyArrow crash.
Every original broad node ID remains; exactly 50 new cases individually pass.
All four original 100-wire TF host mixed-mode cases and true-third refusal
individually PASS in each completed TF XML. New isolated Alternate broad and
TF/MPS original handles are running, source unchanged.

Current Main default-gap rerun: 56 FAIL/5 PASS, exit 1, exact old 56 failure
ID set unchanged. Current Main original two annotation-index --runxfail:
2 FAIL, exit 1. Both are genuine retained red evidence, not new xfail edits.
The four original constant-gradient cases show native ParameterExpression vs
public float with equal 1/0 values; return-type parity is still OPEN. Latest
receipt tmp/r2o3b-qpy1h-rebuilt-constant-gradient-main.json.

Strict SDK-free was NOT rerun for a green result. Its NumPy 1.26.4 and absent
Qiskit/PennyLane/TF/JAX resolution were independently rechecked unchanged.
Its original 1278 PASS/1 FAIL/4 optional SKIP remains OPEN. An asynchronous
HUMAN question requests permission for only the projector test's strict
rounding-error comparison while preserving exact coordinate/ownership/
roundtrip assertions. No answer yet and no test/production change made.
No final R2 or full QPY/replacement acceptance follows from this checkpoint.

#### QPY1-H4R3-E Complete 32d0 Terminals And Authorized Test-Only Candidate

All original 32d0 sessions reached real terminal exits. Isolated Alternate
broad: 8156 PASS/4 original XFAIL/zero fail or skip, exit 0, 468.92s.
Isolated Alternate TF/MPS: 305 PASS/zero fail/skip/xfail, exit 0, 486.86s.
Final independent audit tmp/r2o3b-qpy1h-final-evidence-audit.json confirms all
six gate manifests before/after/current equal the 1606-file 32d0 candidate,
including strict's exit-1 receipt and nine completed numerical examples.
Both full original broad node-ID sets remain; exactly 50 new cases PASS.
Both original four TF 100-wire mixed AD cases and true-third refusal PASS.
Default probes in BOTH environments remain 56 FAIL/5 PASS, with the old exact
56-ID set; both original annotation-index --runxfail probes remain 2 FAIL.
Both actual public SDK versions return float in the four constant-gradient
controls; native PE return-type parity remains OPEN despite equal values.

The HUMAN then explicitly approved only correcting the old projector test's
numeric comparison contract. No production file changed. For the computed
state projector, compare each real/imaginary component with independent exact
Fraction.from_float input arithmetic, using gamma_2 = 2u/(1-2u), u=2^-53.
The fixture's products are normal binary64 values. For two exact terms,
rounding each product and the sum yields coefficient error at most
(1+u)^2-1 <= gamma_2; fused evaluation uses no more rounding. No tolerance is
derived from measured errors or array size. Density's no-arithmetic alias
still compares exactly with raw. Coordinate conversion and roundtrip compare
exactly against a separate snapshot of the computed native matrix; an exact
nonmutation assertion is added. Ownership/dimensions/convention assertions
remain unchanged. Statevector/Operator kernels are untouched.

Strict SDK-free focused file: 23 PASS, exit 0, no fail/skip/xfail. Fixed
negative controls reject 1e-14 perturbation, row permutation, missing
conjugation, phase reversal and complex64 downgrade; both legitimate native
and np.outer rounding paths satisfy the independent bound. Evidence:
tmp/r2o3b-qpy1h-approved-contract-sdkfree-focused.{json,xml} and
tmp/r2o3b-qpy1h-approved-contract-negative-controls.json.

New frozen candidate: 1606 selected files, SHA256
05b347c5939a0e2d6aa0dc16887497cd0808a20227e3b4712a7e540e8bf41679.
Archive tmp/r2o3b-qpy1h-approved-contract-source-baseline.tar.gz, SHA256
037692efc0c3e52e05567491ade1b5b799b15bc986ff28ab527e0bfb2ea0ef37.
Archive member hashes equal the candidate. Relative to 32d0 exactly ONE old
test file differs; all production files byte unchanged. Scope receipt:
tmp/r2o3b-qpy1h-approved-contract-scope.json. All earlier 32d0 receipts remain
old-selected-source evidence, not silently transferred to 05b3.

Fresh Main/Alternate broad, both TF/MPS, strict SDK-free and nine examples
were launched on 05b3; await their original terminal exits without source
edits. The first examples launcher omitted the examples module search path
and stopped with ModuleNotFoundError before numerical execution. That exit-1
receipt is retained as *-approved-contract-examples.json. Corrected only the
launcher's PYTHONPATH=.:examples, using a distinct *-examples-correct-path.json
receipt; no example/production code edit or silent overwrite.
All original full R2 gates and full SDK replacement remain OPEN/INCOMPLETE.

#### QPY1-H4R3 Approved Contract Strict Terminal And Sensitivity Checks

On the new 05b3 candidate, complete affected strict SDK-free gate actually
terminates exit 0: 1279 PASS, 4 old optional SDK oracle SKIP, zero fail/xfail,
56.34s. Actual python -s/no_user_site is true, NumPy remains system 1.26.4,
all forbidden Qiskit/PennyLane/TF/JAX resolutions are false and imports after
the gate are empty. Four skips are ONLY the unchanged optional public
H/S/HS/SHY tableau oracles absent in this environment. They are not native
passes or an SDK-free FULL claim. The prior 32d0 exit-1 gate is preserved.
Receipt tmp/r2o3b-qpy1h-approved-contract-sdkfree.{json,xml}.

Reproducible diagnostic pytest file tmp/test_qpy1h_projector_contract.py adds
six positive controls (random, real-only, imaginary-only, exact cancellation,
near-zero cancellation, tiny normal products) and five negative sensitivity
controls (1e-14 perturbation, row permutation, missing conjugation, phase
reversal, complex64). Native and np.outer paths both satisfy the independent
bound; all five wrong cases are rejected. Actual strict/Main/Alternate each
11 PASS/zero fail/skip/xfail, exit 0. Receipts
tmp/r2o3b-qpy1h-contract-bound-sensitivity-{sdkfree,main,alternate}.{json,xml}.
This diagnostic file is OUTSIDE the selected manifest roots; its own hash
must be recorded separately. No added original-suite node IDs or SDK
capability counts are inferred from these 11 checks.

Corrected examples launcher now completes all nine real numerical examples,
exit 0, hardware tasks 0, same 05b3 before/after manifest, in
tmp/r2o3b-qpy1h-approved-contract-examples-correct-path.json. First erroneous
launcher receipt remains retained, not overwritten. Latest Main/Alternate
broad and TF/MPS original handles are still running. No source edits during
those gates. No production file, other old test or old numerical tolerance
was changed by the authorized correction.

#### QPY1-H4R3 Approved Contract Latest Six Terminal Proofs

All six original 05b3 sessions have now reached real terminal exit 0, including
interpreter shutdown; no required runner remains live. Latest selected-source
SHA256 05b347c5939a0e2d6aa0dc16887497cd0808a20227e3b4712a7e540e8bf41679,
1606 files, unchanged from the authorized test-only freeze.

Main broad: 8156 PASS, 4 unchanged original XFAIL, zero fail/skip, 457.48s.
Isolated Alternate broad: 8156 PASS, same 4 XFAIL, zero fail/skip, 502.85s.
Main TF/MPS: 305 PASS, zero fail/skip/xfail, 531.98s.
Isolated Alternate TF/MPS: 305 PASS, zero fail/skip/xfail, 533.16s.
Strict SDK-free complete affected set: 1279 PASS, 4 unchanged optional public
tableau oracle SKIP only, zero fail/xfail, 56.34s.
Nine actual numerical examples: all completed, hardware tasks 0.

Independent final audit:
tmp/r2o3b-qpy1h-approved-contract-final-audit.json. All six selected manifests
before/after/current equal the 05b3 candidate. All original broad node IDs
remain and exactly the four original xfail IDs/type remain. Both TF XMLs
individually show the original four 100-wire mixed-mode cases and true-third
refusal PASS. Actual same-process origins establish Qiskit 2.4.1/PennyLane
0.44.1/JAX 0.7.1 in Main versus Qiskit 2.6.0/PennyLane 0.42.3/JAX 0.6.2 in
isolated Alternate, TF 2.21.0/Torch 2.12/NumPy 2.4.6/SciPy 1.18.1 in those
numerical gates. Strict uses its unchanged NumPy 1.26.4, python -s, no user
site and no forbidden SDK/TF/JAX resolution or import. Optional skips are not
native passes; this is not an original R2 SDK-free FULL claim.

Latest new-source default probes still each genuinely FAIL 56/5 PASS, exit 1,
same exact 56 failure-ID sets. Latest original annotation-index --runxfail
each 2 FAIL, exit 1. Those red receipts have the same 05b3 source. Public
2.4.1 malformed partial-bind streams remain rejected by both readers; this
diagnosis is not a successful interchange claim. Constant native gradient
return types remain PE versus actual public float in both versions. Writer
operation history is not supported merely because reader opcode 15 is.

The one HUMAN-approved projector test-contract blocker is locally resolved
for the complete affected strict set, with rigorous componentwise bounds,
exact ownership/coordinate/roundtrip contracts and the separately hashed
11-case zero/near-zero/negative sensitivity tests. Production kernel unchanged;
old strict failure and old-source reproduction retained. This closes neither
the default 56 nor any original R2 final obligation. Full independent SDK
replacement ACTIVE/INCOMPLETE; QPY1 PARTIAL/NOT_ACCEPTED pending bounded peer
review. Test counts are not function/API completion percentages.

Final report sent to the authorized existing ChatGPT conversation under
QPY1-H4R3-APPROVED-CONTRACT-LATEST-SIX-TERMINALS, requesting bounded review and
the next precise prompt. No independent remote CI or full code/legal audit
is inferred. main HEAD unchanged b443430ec3eb7eac418c22814e08fe6d940bf099.
No Git mutation, repo dependency edit, vendor, credentials/TLS configuration,
cloud/hardware, financial-history, Studio/Router, tag or release actions.

#### QPY1-H4R3 Final Bounded Peer Review

Complete latest-six-terminal peer reply and ending actually read and next
QPY1-I prompt archived in the existing received-prompt record. Peer accepts
QPY1_READER_AND_RETAINED_FORMAL_SUPPORTED_SUBSET_READY_FOR_REVIEW from the
same 05b3 local receipts. The precisely authorized projector test blocker is
resolved for the affected strict set; no production mathematics was changed.
This is bounded local development review, not remote CI/code/legal audit,
whole QPY completion, full original R2 acceptance or full SDK replacement.

Next bounded work is QPY1-I constant gradient public return ABI: real dual-SDK
type/identity/math reds, actual internal caller audit, minimum existing-engine
public/internal boundary repair, QPY/Compiler/SV-MPS/AD/resource protections,
then fresh frozen gates. Do not implement by test-side coercion, erase
retained formal identities or create another symbolic engine. Default 56 and
public reader defects stay separate and OPEN. All original final gates and
full independent Qiskit/PennyLane replacement remain ACTIVE/INCOMPLETE.

#### QPY1-I3-F2 a381d80b Terminal Regression And Prefix Repair

All a381d80b processes reached real terminals. Main broad8218PASS/4originalXFAIL
exit0 (453.70s), isolatedAlternate same exit0 (497.34s). Strict1478PASS/37optional
SKIP and nineexamples exit0. Both expanded TF-MPS406PASS/2FAIL exit1 (565.89s/
569.40s). The two failures are the unchanged old cached-RoF mixed_native square
and exponential_cubic losses, refused by the new exact capture identity guard.
No math/tolerance/old node ID was changed. The native builder's capture is a
correct prefix, not the whole recorder after a subsequent RX(.2*point[0]).

This genuine production regression invalidates a381 for bounded acceptance.
Audit tmp/r2o3b-qpy1i-final-r3-audit.json retains its same-source outcomes, all old
IDs/four xfails, all36 original100wire/third cases PASS and all real separate red
probes. An initial audit incorrectly used XML child-count as the PASS condition
and treated harmless JUnit properties as failures; corrected derived audit uses
absence of failure/error/skipped. No original test result was rewritten.

Approved minimum repair readmits exact native prefix identities/order/AST/owner/
budget but does not use that prefix as the full executable mapping. Full actual
pack GraphDef enters the existing bounded normal lowerer, producing all native
expressions directly from the real source. Prefix-only capability misses now
typed-refuse rather than use legacy/unproved projection. Complete native capture
still requires the new readonly proof. Final output count and native plan recorder
UUID order are checked against kernel slots. Both original losses plus proof/
forgery/retained suites first52PASS each environment; added partial unsupported/
nonfinite no-fallback guards and repeated-gate/noncontiguous-wire slot checks are
in the current final focused set. New all-gates freeze/validation remains pending
at this checkpoint; do not transfer the previous candidate's passes.

#### QPY1-I Constant Scalar ABI And Retained Frozen Transport

Local-only development, main HEAD still b443430. Actual Qiskit2.4.1 and2.6.0
black-box calls established 25 exact builtin scalar type/value cases and five
symbolic context/math cases. Original native ABI gates genuinely failed25 each;
Main additionally exposed public2.4.1 sin(p)^2+cos(p)^2 derivative =
2.514784412658314 at .31 versus analytic/native/public2.6 zero. That original
comparison remains FAIL, not skip/xfail or a changed expected value.

Public gradient now returns observed int/float/complex constants from the same
bounded native calculus. Internal MatrixJet and QPY op13 retain the existing AST
through _gradient_expression/validated constant coercion, preserving order and
formal identity. No second differentiation engine. New source-domain/work/order
tests and scalar op13 repeated replay protect rejection and resource semantics.

Unchanged old PE-extension gate was first saved as383PASS/11FAIL. Only true
gradient-always-PE assumptions in two old test files/helpers were updated after
production ABI fix. Independent math points/tolerances, UUID/context and resource
guards remain; exact raw builtin types and internal AST second derivatives are
separately asserted. The earlier human-approved projector comparison correction
is unchanged from05b3; no additional projector production or tolerance changes.

FrozenBinding real initial12FAIL/5PASS: context-only q disappeared from cos(r),
missing formal input wrongly accepted, foreign owner property accessed. Existing
freeze now readmits native owners before inspection, retains validated context/
order, and accounts unique formal-only mapping identities without fake0*q.
Existing compiled scalar evaluator carries mapped symbolic context only; actual
numeric/framework evaluation retains zero mathematical q-dependence.

Two genuine further admission counterexamples were retained: manually constructed
constant2/node_count0 gave wrong finite expectation; complete create fixed this,
but valid p*2 could still be substituted for actual captured p. Candidate b5f1
was invalidated. Exactly own runner PIDs50035/50040/50042/50044 received SIGINT;
all four original sessions terminal exit2, broad745PASS each and TF45PASS each
are INTERRUPTED/INCOMPLETE history, not successful full gates. Old completed
strict1477/37SKIP/examples9/affected498 do not transfer to later candidates.

Full captured binding is now validated before projection, with exact native
owner/root identities, occurrence count and complete conservative node envelope.
The same actual captured scalar snapshot is then read-only verified by the
existing bounded GraphDef scanner before quantum tensor plan construction.
Input positions, admitted static layouts, ordered operations and exact float64
literal bits are compared per output occurrence against native AST structure.
No algebraic equivalence/sampling, AST emission, graph execution/import, newUUID,
private gradient or normal-lowering whitelist expansion. Unsupported proofs
typed-refuse, never fall back to unproved projection.

Before final freeze: source-proof46PASS, earlier proof/admission/atomicity211PASS,
latest affected Core/QPY/MatrixJet/old-contract/resources499PASS; previous actual
four-framework targeted Main/isolatedAlt34PASS each before final added negatives.
Fresh frozen TF-MPS runs include all latest framework/proof/refusal tests.

Latest candidate selected SHA256
a381d80b427e220b117e4d0fdece58c709431e7b28e4d6c991d5cb2375264566,1612files.
Archive tmp/r2o3b-qpy1i-final-r3-source.tar.gz SHA256
106bddad151a9cfbd9134258ddb3953a2fae9619bdb2be26b351163e6220d41b.
Archive members exactly match selected manifest. Fresh gate receipts use
tmp/r2o3b-qpy1i-final-r3-*.json/xml. Four expensive broad/TF-MPS sessions RUNNING
at this checkpoint, no final acceptance inferred. Same-candidate strict affected
1478PASS/37 pre-existing optional SDK skips, nine actual numerical examples0
hardware tasks, affected499PASS already complete in receipts. The37 skips are
the prior4 optional tableau controls plus33 optional public elementary oracles
newly included in this affected selection, not new test exclusions/native passes.

Latest raw public ABI comparison Main29PASS/1genuine trigFAIL, Alt30PASS. Original
default Operator probes each56FAIL/5PASS with exact unchanged failure IDs; the
original annotation-index --runxfail each2FAIL. No default arithmetic switch.
These remain distinct from native mathematics and bounded local regression.
Ruff F821/F841 passes. No Git mutation, auth/TLS/dependency/vendor/hardware/cloud/
financial-history/Studio/Router/tag/release changes. Original R2 final gates and
full independent Qiskit/PennyLane replacement remain ACTIVE/INCOMPLETE.

#### QPY1-I3-F2 Final 51a96b21 Terminal Proofs

All latest required processes, including interpreter shutdown, reached actual
terminals. No required validation session is still live. Selected source SHA256
51a96b21a23d7757669f0d45952352ff0663e4e9a786b9ebc4434138e8de9a09,1612files;
archive tmp/r2o3b-qpy1i-final-r4-source.tar.gz SHA256
d4358e67ac327e1c0e20acce25460ea10ca387dced5dc7b6009d1f78fed12b96.

Latest same-source results, all real terminal exits:
- Main broad8218PASS/4unchanged originalXFAIL,0fail/skip,exit0,454.87s.
- Isolated Alternate broad8218PASS/same4XFAIL,0fail/skip,exit0,496.84s.
- Main expandedTF-MPS411PASS,0fail/skip/xfail,exit0,571.24s.
- Isolated Alternate expandedTF-MPS411PASS,0fail/skip/xfail,exit0,573.73s.
- StrictSDKfree affected1478PASS/37original optionalSKIP,0fail,exit0,57.22s.
- Nine numerical examples completed,exit0,hardware0.
- Core/QPY/MatrixJet/old-contract/resource affected499PASS,exit0,53.72s.
- Separate projector sensitivity diagnostic11PASS in strict runtime,exit0.

Audit tmp/r2o3b-qpy1i-final-r4-audit.json verifies every actual gate's selected
before/after/current manifest, all archive member hashes and archive digest.
All old broad/TF node IDs remain, exactly four original xfail IDs/type remain,
all36 protected original100wire/third-refusal cases pass, both original mixed-
native RoF regressions pass, and all9 forged-binding refusal cases pass per TF
environment. Full/proper-prefix dispatch, readonly proof, repeated/noncontiguous
wire slot mapping, partial/retained/empty-output AD and unsafe-prefix no-fallback
guards are included. Source proof emits no AST or numerical graph; complete
partial sources use the existing normal lowerer only, with no whitelist expansion.

Actual same-process Main origins: Qiskit2.4.1/PL0.44.1/JAX0.7.1; isolatedAlternate:
Qiskit2.6.0/PL0.42.3/JAX0.6.2. Both numerical stacks actually imported TF2.21.0,
Torch2.12,Autograd,NumPy2.4.6,SciPy1.18.1. Strict used python-s,NumPy1.26.4,
no user site, no forbidden SDK/TF/JAX resolution/import, and no framework import.
Its37 skips are4old optional tableau +33old optional public elementary oracles
included in this wider affected selection; they are not new exclusions or native
passes. This is not an original R2 FULL or all-framework FULL claim.

The human-approved projector comparison test is bit-for-bit unchanged from05b3
and its rigorous Fraction/gamma2 bound still detects all deliberate negative
perturbations. No Statevector/DensityMatrix projector production math changed.
The25 native constant-gradient raw ABI reds are repaired on the existing engine;
internal AST repeated calculus/QPY resource context and formal transport remain.

Explicit latest red evidence remains: Main actual public gradient oracle29PASS/
1FAIL (Qiskit2.4.1 wrong trig derivative), isolatedAlt30PASS; defaultOperator each
56FAIL/5PASS with identical original failure IDs; original public annotation-index
--runxfail each2FAIL. Public2.4.1 malformed streams/history-writer coverage remain
open. Old interrupted b5f1 and failed a381 receipts are retained, not relabeled.

Bounded local development review only. All original R2 FULL/GLOBAL>=
91.34108013033072%/68exclusions/28section/ALLexamples/controlledlegal/5origins/
fullworktree-staged-committed equality gates remain OPEN. NoGit mutation,
dependency/auth/TLS/vendor/cloud/hardware/financial-history/Studio/Router/tag/
release actions; main HEAD b443430 unchanged. Full independent native Qiskit/
PennyLane replacement remains ACTIVE/INCOMPLETE; no default arithmetic switch.

#### QPY1-I3-F2 Bounded Final Peer Acceptance

Latest complete final review and next prompt read in default Chrome. Peer accepts
QPY1_CONSTANT_GRADIENT_PUBLIC_ABI_SUPPORTED_SUBSET_READY_FOR_REVIEW only for
51a96b21/1612 selected sources and reported local terminal receipts. This is not
an independent source/remoteCI/legal audit, fullQPY, defaultAPI parity, original
R2 acceptance or complete SDK replacement. All explicit old red probes and final
obligations remain OPEN. Next exact QASM1 prompt archived in the existing received
prompt document: investigate the long-standing custom Gate/standard-name QASM2
xfail via real four-direction dual-SDK/math evidence before any repair. Do not
switch Operator defaults, edit old mathematical expectations or weaken source
admission. No new QASM1 implementation is included in this checkpoint.

### QASM1-B Native Declaration Scope And Definition Admission

Continue full independent SDK replacement, local-only. Actual original QASM2
xfail investigated first on unchanged51a96b21/1612 selected sources. Original
`test_bilateral_public_qasm_declarations[public_to_native-standard_name-2]`
still produces a real --runxfail failure on installed Qiskit2.4.1 and2.6.0:
custom Gate named h with X body is exported as bare h, body lost. Both readers
then implement H, not the original X. No reader can recover the absent body;
original source/test/math/tolerance/xfail remain unchanged and OPEN.

Black-box four-direction evidence in tmp/r2o3b-qasm1-initial-diagnostics-*.json
also preserves public x/H definition loss, parameterized/two-wire h invalid
export, and p export without a valid standard definition. Native writer->both
readers retains correct full matrices for all six diagnostic cases. Existing
native exporter did not require a change. Publication references, paraphrased:
https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2 and
https://arxiv.org/pdf/1707.03429 distinguish source includes, visible previous
gate declarations, local formal scope and fixed call signatures. No upstream
implementation/source was read or copied into the production repair.

Initial formal new Native suite: each Main/strict/isolatedAlternate16FAIL/2PASS,
exit1, actual same-source receipts preserved. Independent Native defects were
literal declaration alias priority, include-at-point duplicate/namespace
conflicts, unused self/forward/unknown/local-formal/indexed-qubit validation.
First repair yielded78PASS with original QASM2/QASM3 suites. Expanded test then
found four genuine unused depth/work budget failures. A fifth failure was test
harness-only: inverse generates a circuit name not representable in QASM2;
test now explicitly exercises existing allow_metadata_loss and expected warning,
without changing mathematical expectations/tolerance or production exporter.

Minimal production changes only in existing text_lowering.py: shared existing
OPS signature lookup gives visible literal declarations priority over aliases;
QASM2 includes reject duplicates/earlier name conflicts; each definition gets
direct-call signature/local formal/qarg/previous-declaration validation before
publication. Body admission never constructs an executable Gate or expands
nested templates. Local memoized footprint charges repeated DAG references at
full logical expansion cost, with existing serialization/GateCircuit limits;
actual analysis traversal is also bounded. No extra persistent registry, parser,
math engine or global standard-gate renaming. Existing QASM3 path protected.

New57 native tests include full complex independent Operator/SV/MPS oracle,
noncommuting nested gates, reversed noncontiguous wires, copy/inverse/compiler,
QASM2/QPY13/JSON IR, parameter identity before numeric binding, source AST
immutability, invalid definition not published and no Gate constructed on bad
admission. New35 real public observations include28 invalid declaration inputs,
six legal literal names and full complex nested QPY13 bilateral execution.
Two actual SDK versions accept unused rx missing a parameter AND an unused
custom inner(t) called with no parameter. Native refuses both without inventing
default values. They are PUBLIC_QASM2_SIGNATURE_ACCEPTANCE_DIFFERENCE / OPEN,
not successful parser parity. No attempt to execute those malformed public
bodies was made.

Pre-freeze public-specific Main228PASS/1oldXFAIL and isolatedAlternate same,
both exit0. Existing old tests including approved projector contract were not
modified. Production text_lowering changed; two new test files added.
Frozen selected1614-source candidate:
3aa2f50b63c4369c4b9fdfd6ada83dbf1b607fabfa2b3e8debee23111bd5cb55.
Archive tmp/r2o3b-qasm1-final-r1-source.tar.gz SHA256:
c0e3c8bee7a1a8ebef629880b86008ca16302bc6515f8187ca01e7272d825579.
No selected source edits during gates. Latest frozen receipts so far:
public-specific228PASS/1oldXFAIL each SDK; affected616PASS; strict1595PASS/
37old optional SDK skips, no failures; nine numerical examples exit0/hardware0.
Main oracle29PASS/1old trig FAIL, Alternate30PASS; default each56FAIL/5PASS;
old public annotation-index each2 realFAIL; original QASM writer each1 realFAIL.
Their original failure IDs remain unchanged. Main+isolatedAlternate broad and
each411TF/MPS are RUNNING, not yet final accepted at this intermediate entry.

All original fullSDK/R2/GLOBAL/coverage/exclusion/legal/Git-three-state final
gates remain OPEN. Full replacement ACTIVE/INCOMPLETE. No git/auth/TLS/repository
dependency/vendor/cloud/hardware/finance-history/Studio/Router/tag/release action.

#### QASM1-B Frozen Final Terminals And Audit

All required sessions, including both TF interpreter shutdowns, actually exited
zero for the bounded positive gates. No provenance runner remains live. Same
3aa2f50b63c4369c4b9fdfd6ada83dbf1b607fabfa2b3e8debee23111bd5cb55 /
1614 selected files and c0e3c8bee7a1a8ebef629880b86008ca16302bc6515f8187ca01e7272d825579 archive:

- Main broad8310PASS/4exactoldXFAIL,0fail/skip,exit0,455.55s.
- Isolated Alternate broad8310PASS/4exactoldXFAIL,0fail/skip,exit0,499.97s.
- Main TF/MPS411PASS,0fail/skip/xfail,exit0,573.70s.
- Isolated Alternate TF/MPS411PASS,0fail/skip/xfail,exit0,577.19s.
- Strict affected1595PASS/37exactoldoptionalSDKskip,0fail,exit0,58.75s.
- Affected Core/QPY/MatrixJet/resources/QASM616PASS,exit0,55.75s.
- Public QASM-specific228PASS/1oldXFAIL per SDK,exit0.
- Nine numerical examples complete,exit0,hardware0.

tmp/r2o3b-qasm1-final-r1-audit.json verifies all17 actual receipts' source before/
after/current equality with every archived member and archive digest. All prior
broad/TF nodeIDs retained, exactly four old xfails unchanged, original05b3 36
protected100wire/third-refusal cases pass and latest45 protected cases pass in
each environment. Both original mixed-native cachedRoF cases and all9 forged-
binding refusals pass per TF environment. All57 new Native cases and35 actual
public observations pass; the two malformed unused-parameter public acceptance
differences are explicitly classified OPEN, not interop-match evidence.
Original strict37 skips/type/reasons/IDs unchanged; approved projector test hash
unchanged. Only three selected changed files relative51a9, no old test weakened.

Actual same-process MainQiskit2.4.1/PL0.44.1/JAX0.7.1 versus isolatedAlternate
Qiskit2.6.0/PL0.42.3/JAX0.6.2; both actually imported TF2.21.0,Torch2.12.0,
Autograd,NumPy2.4.6,SciPy1.18.1. Strict python-s/no user site usesNumPy1.26.4,
with no SDK/TF/JAX resolution or import. This is not all-framework FULL.

Explicit original red probes retained: public QASM writer original1FAIL each;
defaultOperator56FAIL/5PASS each; annotation-index2FAIL each; Main actualpublic
gradient29PASS/1oldtrigFAIL, isolatedAlternate30PASS. Their failureIDs are exactly
unchanged, no skip/xfail relabeling. Public writer x/H and invalid h/p exports,
special signature acceptance and remaining QASM/QPY/default SDK gaps stay OPEN.
Original human-approved floating comparison still leaves production projector
math unchanged. No git/dependency/cloud/hardware/UI/auth/history changes. main
HEAD b443430ec3eb7eac418c22814e08fe6d940bf099 remains unchanged.

All terminal receipts and scope sent to the authorized existing ChatGPT
conversation using prefix QASM1-B ALL_ACTUAL_TERMINALS_AND_FROZEN_AUDIT, asking
bounded review and next exact prompt. Proposed only
QASM1_NATIVE_DECLARATION_SCOPE_SUPPORTED_SUBSET_READY_FOR_REVIEW. Full independent
native replacement ACTIVE/INCOMPLETE and all original final R2 gates OPEN.

#### QASM1-B Accepted Subset And QPY2 Initial Diagnosis

Complete final peer review actually read in default Chrome and exact body saved
in tmp/r2o3b-qasm1-final-peer-reply.json. Accepted only
QASM1_NATIVE_DECLARATION_SCOPE_SUPPORTED_SUBSET_READY_FOR_REVIEW for reported
local3aa2/1614 receipts, not independent source/legal/remoteCI/fullSDK audit.
QASM full and all original final obligations remain OPEN. Next QPY2 exact scope
archived in existing received-prompt journal: derivedUnitary standardQPY13 with
independent math/provenance/owner/Exactly-once conversion/resource atomicity.

Initial QPY2 read-only black-box diagnosis on unchanged3aa2 selected sources:
tmp/r2o3b-qpy2-initial-main.json / -alternate.json, both actualexit0/sourceunchanged.
24factory/operation/writer records per environment, asymmetriccomplex128QR U,
nonzeroH/RY/RXprep,globalphase.23,originalqargs[1,0]. Current raw class
UnitaryGate(U).inverse() returns exactUnitaryGate/nameunitary/emptymetadata and
all four native/public QPY directions preserve source matrix/state to~7e-16.
The historical raw-class description is therefore not presumed current red.

Old unitary_dg refusal actually reproduces on base Native Circuit.unitary
primitive->to_gate()->inverse(), also repeat/inverse. Existing _inverse_operation
stores adjoint matrix plus inverse_of in primitive unitary_dg; existing standard
writer refuses. QuantumCircuit-derived retained-owner inverse itself encodes.
Additional Native QuantumCircuit-derived Gate.repeat(2) false-cycle candidate
fails during _validate_definition before QPY writer; actual trace retained and
needs independent acyclic-owner proof, not a cycle-refusal relaxation. Actual
both public SDKs reject raw/public-methodUnitary repeat(2).inverse() construction
with ndarray-parameterCircuitError, also before writer, separate upstream issue.

Initial diagnostic harness first failed to catch public construction errors,
then erroneously inspected restored baseCircuit.data after Native parse/math
had already succeeded. Both harness artifacts preserved separately, not called
reader defects. Corrected metadata inspection uses sole Native operation store.
Corrected representable records have no reader errors. Base Circuit.unitary
does not accept label keyword; diagnostic uses its real signature, no production
API rewrite. This is initial encoding/source-preservation diagnosis ONLY, not
independent NumPy math proof, repaired Native code, or QPY2 acceptance. No QPY2
production/selected-test edit yet; QASM frozen manifest still matches archive.
Root-cause split reported to peer with QPY2-A_INITIAL_ROOT_CAUSE_SPLIT prefix,
asking to confirm focused next execution, not scope expansion. All original R2
gates OPEN and full replacement ACTIVE/INCOMPLETE. Strict local-only unchanged.

Complete peer root-cause reply now read and archived in
tmp/r2o3b-qpy2-initial-peer-reply.json. Classification confirmed from actual
receipts only. Next QPY2-B/C must establish TWO independent formal reds: trusted
baseCircuit primitive inverse QPY standardrecord, and a separately proven
acyclicrepeat(2) DAG before correcting any false-cycle check. No RawUnitary
inverse rewrite, automaticdensefallback, upstreambadmathcopy or weakened real
cycle protection. Full current prompt archived in existing received journal.
QPY2 implementation/formal mathematical proof and regression remain NOT_DONE;
this checkpoint closes only the accepted QASM1-B subset and initial diagnosis.

### QPY2-B/C Formal Reds And Native Repair In Progress

Previous goal turn was genuine progress: QASM1-B production repair and frozen
dual-runtime gates accepted only as local supported subset. Current QPY2 starts
from actual3aa2/1614 source baseline, mainHEAD unchangedb443430. Strictlocalonly.

New tests/serialization/test_qpy_derived_unitary.py independently builds NumPy
complex128 QR matrices, global phases, ordered noncontiguous embeddings and
adjoints/repetition. Before production edits actual Main/strict/isolatedAlternate
each10FAIL/2PASS,exit1,1615-sourceunchanged. Eight failures were true primitive
inverse/doubleinverse/copyinverse/repeatinverse standardQPY refusals. Two were
repeat() false-cycle on independently inspected acyclic owned definitions, with
24 repeat/inverse iterations to expose transient snapshot identity reuse. Raw
UnitaryGate.inverse standardQPY already passes; not changed or claimed newfix.

Both existing definition validators now hold actual active ancestors strongly,
use is-only identity and read child.definition once. No visited-set relaxation,
cycle guard removal or per-reference work exemption. New sharedDAG work exact6,
definitions5/depth2 and eachonebelow refuse; real direct/indirectGate/Instruction
cycles refuse beforecopy; collection stress protects ephemeral execution owners.
First strictcycle/resources214PASS/75 existingoptionalSKIP,exit0. No claimthose
SDK skips nativepasses or originalR2FULL.

New core/unitary_inverse.py qualifies only actual trusted native primitive
inverse construction using existing exact owned Native UnitaryGate. Private
qualification binds owned metadata/operand/parameter/owner object identities,
names,label,native local basis,width/type and immutable exact-contentdigest.
Constructor uses admitted adjoint outbuffer and existing unitary validation;
source stored operation/name/matrix/inverse_of are not mutated. Explicit standard
QPY/IR/remap/binding boundaries request canonical existing UnitaryGate record.
Default execution validates but does not force an extra canonical-copy graph.
Unknown *_dg/loose inverse_of receives no dense writer fallback. No new format,
sidecar, registry, symbolic engine or copied SDK implementation.

Identical matrixpointer/width/inverse_of in a plain forged Operation refuses.
Foreign witness/subclass/array/comparison callbacks refuse without callback;
wrongsourcebinding/matrix/width/name/inverse_of and changed buffers refuse.
Structural constructor/field qualification is NOT cryptographic authenticity
against arbitrary private-field rewriting. Creation buffer is read-only;
existing trusted copies may produce writable private buffers, but contentdigest
and identity revalidation refuse numerical changes. This physical-flag versus
readonly-consumer nuance explicitly reported for peer review, not hidden.
Actual one-wire constructor peak258bytes, escapedownedarray64bytes, bothparent/
child release0; exact258 passes and257 refuses for eitherlimiter. EarlyQPYnumeric
limits precede canonicalcopy; injectedconstructor/copy errors preserve source
and stream, legaldump recovers; concurrent12dumps deterministic/readonly.

Expandedcontrolorder tests preserved an initial48 harness-only failures from an
invalid StatevectorDevice(initial_state) assumption, corrected to existing
Statevector.evolve, leaving8 real control-before-inverse standardQPY failures.
Both actual Qiskitversions retainControlledGate(base.inverse) andcontrolstate.
Exact Native ControlledGate.inverse now does so only after validating canonical
definition signature; changed live definitions keep prior actual-definition
inverse behavior. RawUnitaryGate.inverse/specializedgateoverrides unchanged.
New complex math coversopen/closed/multiplecontrols,numericfractional/integer
power,annotatedmodifierorder,repeat/inverse,globalphase,sourceidentity andfull
amplitudes,detachedQPYpublicreuse exactlyonce,IR/compiler/SV/MPS.

Earlier new immutability test compared two recomputed matrices bit-for-bit and
saw5.6e-17 operation-order/alignment rounding. That harness artifact is retained;
new test instead checks exact stored sourcearray/IR immutability, while original
independent fullmatrix3e-14 math expectation stays unchanged. No old test touched.
Before latest additionalsource/concurrent-admission cases, actual Main2.4.1 and
isolatedAlternate2.6.0 each199PASS,0fail/skip/xfail,exit0,1619sourceunchanged;
114Native+85actualpublic observations. One publicrepeat-inverse construction
error explicitly OPEN, not interopmatch. Affected old+new815PASS exit0,65.97s.
Fullfrozenbroad/TF/strict/nineexample validation NOT_RUN on QPY2 yet; no acceptance
claim. FullreplacementACTIVE/INCOMPLETE, all originalR2/oldredgates OPEN. NoGit/
auth/TLS/dependency/vendor/cloud/hardware/financehistory/StudioRouter/tag/release.

#### QPY2 Readonly Copy Hardening And New Frozen Candidate

The next goal turn rechecked the latest HUMAN-approved projector comparison
only: existing23 tests plus independent11 sensitivity cases each34PASS in
strict/Main/isolatedAlternate, no source edit. That was evidence/revalidation,
not an additional production feature or full replacement completion.

Complete peer targeted review actually read in the default Chrome existing
conversation. It requires physical flags.writeable=False on every retained
inverse witness copy as well as content/identity checks. New focused cases
first genuinely10FAIL/5PASS/25deselected,exit1 on unchanged1619 selected sources:
Operation/Circuit/Gate/Instruction copies in unmanaged and managed execution
lost readonly; canonical compose/remap/bind/QPY/IR already passed. Original
red receipt tmp/r2o3b-qpy2-readonly-copy-red-strict.{json,xml} preserved.

Minimal repair uses the existing native object copy protocol for qualified
Operation deepcopy. Audited strict graph copying admits original qualification
before allocation, reconstructs through the same alias memo, then seals only
copied inverse witness arrays readonly and revalidates them before publication.
Ordinary matrix/Gate buffers are not made globally readonly. No extra matrix
snapshot is added: parent/child64byte exact copy passes and63byte refusal is
proved before retained_array destination construction. Existing unknown/forged
metadata has no writer fallback. Content-digest/owner checks remain in addition
to physical readonly protection. Changing ndarray flags back and mutating the
buffer is explicitly adversarial private-object tampering, still refused.

Latest targeted Main2.4.1 and isolatedAlternate2.6.0 each220PASS,zero fail/skip/
xfail,actualexit0,9.06s/8.82s. Includes135Native +85actualpublic observations;
one upstream repeat/inverse construction difference remains explicitly OPEN.
Source-bound receipts *-final-r2-qpy2-specific-{main,alternate}-final.{json,xml}.
Latest affected gate836PASS,zero fail/skip/xfail,exit0,69.92s. New approved
projector test and all other original tests remain unchanged from QASM baseline.

Frozen candidate1619files, selectedSHA256
71e951fcbbde2ea274cb4654a18c30fa39f59434c17fe212c67d2c9bc56b8a8d,
archiveSHA2567abbef683713251916b695185e043f8ac3a3814208ea543d6bb79f5d0955f538,
tmp/r2o3b-qpy2-final-r2-source.tar.gz. Current manifest equals every archive
member and all received latest targeted/affected manifests. Exactly11 selected
changed paths versus3aa2:7production paths and4new test/probe paths. Existing
array_ownership narrow witness sealing is the seventh production path; no old
test is among changed paths. Fresh Mainbroad running; Altbroad, both411TF/MPS,
strictSDKfree,nineexamples and oldred probes still pending. Audit explicitly
lists pending gates and does NOT claim final green. No selected edits during
these runs. Full QPY2 NOT_ACCEPTED, originalR2 gatesOPEN, full replacement
ACTIVE/INCOMPLETE; noGit/cloud/hardware/UI/dependency/auth/history mutation.

#### QPY2-C2 Qualified Contract And All Final Actual Terminals

Previous goal turn answered the owner's overall progress/time question using
current README/ledger/remaining-work evidence. That was a scope/status audit,
not another delivered feature or measured completion percentage. Full goal
remains unchanged; no full-API denominator or reliable completion date exists.

The71e951fc frozen Mainbroad actually completed8529PASS/1FAIL/4originalXFAIL,
exit1,439.73s. Failure was the old blanket native unitary_dg QPY refusal in
test_native_inverse_matrix_metadata_keeps_precise_qpy_refusal_without_sidecar.
Its archive and failure receipt remain unchanged, not called accepted. Complete
peer C2 reply approves only that exact old semantic contract update, retaining
same nodeID/originaldiaginput/precise unqualified refusal. The updated old test
adds exact independent adjoint, readonly witness, standardQPY13/no sidecar,
native fullmatrix/nonzero-state/phase and detachedcopyinversepublicreuse checks.
An ordinary Operation with IDENTICAL public matrixpointer,targets,inverse_of and
metadata but no private qualification still refuses precisely unitary_dg;
source/store unchanged, stream untouched and ledger releases0. One new actual
public SDK diagonal case verifies reading/rewriting/copyinverse/publicappend.
No C2 production writer/Gate math/resource-setting/other old-test/tolerance
changes. Strict complete provenance-boundary file46PASS,exit0,0.68s.

New final selectedSHA256
5a47a0ecc6a119a15c8471e98c64fbbfa9ded57474f1ff3c7efbd5fa585d2c1f,
1619files. Archive tmp/r2o3b-qpy2-final-r3-source.tar.gz, SHA256
e3a8a6c54a41c1f73719bf9b02e9ee58120be3cf552c6033b7f23806178c7152.
Audit tmp/r2o3b-qpy2-final-r3-audit.json confirms all19 final receipt source
before/after/current match every archive member and actual process terminals.
C2 changed exactly2testpaths versus71e9, ALLproduction bytes unchanged. Total
QPY2 versus3aa2 changes12selectedpaths:7production,4newtest/probe files and only
the explicitly reviewed originalsemantic test. Approved projector test hash
unchanged. No selected edits occurred while final gates ran.

| Latest final actual gate | Outcome including terminal exit |
| --- | --- |
| Main broad | 8531PASS/4exactoldXFAIL,0fail/skip,exit0,459.93s |
| Isolated Alternate broad | 8531PASS/4exactoldXFAIL,0fail/skip,exit0,501.01s |
| Main TF/MPS | 411PASS,0fail/skip/xfail,actualexit0,552.29s |
| Isolated Alternate TF/MPS | 411PASS,0fail/skip/xfail,actualexit0,553.94s |
| Main targeted | 222PASS,0fail/skip/xfail,exit0,9.64s |
| Isolated Alternate targeted | 222PASS,0fail/skip/xfail,exit0,9.38s |
| Main affected | 838PASS,0fail/skip/xfail,exit0,70.44s |
| Strict SDK-free affected | 1730PASS/37exactoldoptionalSKIP,0fail/xfail,exit0,60.35s |
| Nine actual native numerical examples | All completed,exit0,hardware tasks0 |
| QASM/public regression each environment | 228PASS/1oldXFAIL,exit0 |

All original broad/TF node IDs and nonpass types/reasons are retained. Both
original05b3 protected36 and latest45 100wire/true-third cases PASS, as do the
2mixed-native cachedRoF and9forged-binding refusal cases in each TF runtime.
135newNative +86actualpublic observations +1retained originalcontract comprise
222targeted cases, not222completed APIs. One actualpublic repeat/inverse
construction difference is explicitly OPEN, not an interoperability match.
Strict uses systemNumPy1.26.4, python-s/no user site, noSDK/PL/TF/JAXresolution
or import; its37optional skips are not Native passes or originalR2FULL proof.

Broad same-process origins: MainQiskit2.4.1/PL0.44.1/JAX0.7.1 versus isolated
AlternateQiskit2.6.0/PL0.42.3/JAX0.6.2. Both broad and TF actually import
TF2.21.0,Torch2.12.0,Autograd,NumPy2.4.6,SciPy1.18.1. The separate411TF gates
themselves import NOQiskit/PL; broad is the actual SDK-origin evidence. No
four-framework FULL claim follows. Terminal proof, including TF interpreter
shutdown, is *-process-terminals.json; authoritative process scan finds no
remaining QPY2 gate runners. git diff --check exits0, mainHEAD remainsb443430.

Original real red diagnostics independently retained on this exact source:
defaultOperator each56FAIL/5PASS; originalannotation-index --runxfail each2FAIL;
originalpublicQASM h/X writer each1FAIL; Mainactualpublictrig29PASS/1FAIL while
Alternate30PASS. Every failure-ID set matches priorQASM1 evidence. No changed
mathematical oracle, newskip/xfail, genericmatrixfallback or privateformat.

Report sent to the authorized existing ChatGPT conversation under QPY2-C2
ALL_ACTUAL_TERMINALS_AND_FROZEN_AUDIT. Proposed ONLY
QPY2_DERIVED_UNITARY_STANDARD_RECORD_SUPPORTED_SUBSET_READY_FOR_REVIEW, pending
complete peer response. FullQPY/SDK and full independent replacement remain
ACTIVE/INCOMPLETE; all originalR2FULL/GLOBAL>=91.34108013033072%/68exclusions/
28section/ALLexamples/legal/5origins/Git3state gates OPEN. No git/auth/TLS/
dependency/vendor/cloud/hardware/financehistory/StudioRouter/tag/release action.
Next requested work is function-level gap accounting from the original
unmodified28-section matrix, not testcount-based feature percentages.

#### QPY2-C2 Accepted Bounded Review; R2-GAP1 Baseline Started

Complete peer review and next G1-G10 prompt read in existing default Chrome.
An initially interrupted partial stream was not treated as complete. After
actual API turncompleted, existing-tab reload restored the full prompt and a
native upward scroll exposed the earlier hidden review items0-12; together
with the previously read items13-113 this is the complete response. It accepts
ONLY QPY2_DERIVED_UNITARY_STANDARD_RECORD_SUPPORTED_SUBSET_READY_FOR_REVIEW
based on the reported local5a47a0ec evidence, not independent remote repository,
legal/CI/Git3state verification or fullSDK acceptance. No source rollback is
requested. The complete next executable requirements are archived as a faithful
semantic transcription in the existing received-prompt journal.

All12 selected changed production/test files pass ruff F821/F841. A repeated
git diff --check passes. No required QPY2 runner remains. No selected source
changed after final acceptance audit; the candidate remains5a47a0ec/1619.

R2-GAP1 G1 requirement lock begins with actual complete reads of the original
script, workflow and earlierR2executionprompt. Current original script is
/Users/avalok/work/QuantumBridge/scripts/run_local_matrix.sh, SHA256
1d93b127aa5783541178d6c852ecec3457fac89694248dd2cd270dad989a7798,
matching historical recorded1d93b127 and HEAD's exact script bytes. Workflow
/Users/avalok/work/QuantumBridge/.github/workflows/test-matrix.yml has SHA256
e6cbbc6c580df678375e437db9859e441c19b3a136bfde125fcb6b27244dac81.
Neither file was modified or executed for this audit. Read-only collector
tmp/r2_gap1_baseline.py actually exits0 and saves
tmp/r2-gap1-original-matrix-baseline.json: all28 original namedsectionIDs,
sourceorder,lines and FULLoriginalshellblocks, workflowhash,currentcandidate,
HEAD and historicalinventorycaveats. Sourceorder is position, not invented
numberedrequirements. Fulluncommittedcandidate must not be confused withHEAD.

Important early finding: the28sections are real CI/test lanes, not an exhaustive
enumeration of all SDK APIs/behaviors. core-only/dev run broad pytest; optional
lanes depend on module availability; ecosystem-inventory executes public-name
inventory scripts. Preserving this baseline does NOT create a complete
functional denominator. Existing Qiskit public inventory has311records at
Level0; PL inventory has1180public-name records. These historical snapshots
are not current native-function completion counts or full public-method and
behavior inventories. Their recordcounts must not become a paritypercentage.

G1 source-implementation survey and G2-G10 persection API->Nativecallchain->
actualexecutedevidence mapping, statusclassification, highvalue realgap probes,
dependencies/priorities/conditionaleffort and ONE nextimplementationprompt are
still REQUIRED. Do not call this initial lock the completedfunctional audit.
No largeproductionrewrite, Operator-default switch, matrix changes, newdeps,
git/cloud/hardware/Studio/financehistory actions. Whole independent native
replacement ACTIVE/INCOMPLETE; all originalR2finalgates remainOPEN.

#### R2-GAP1 Functional Accounting And Actual Public Contract Reds

Date: 2026-10-26. The intervening owner-facing progress/time answer is not a
delivered feature or a measured completion percentage. This continuation makes
new audit progress: all28 original named lane purposes now have source-to-test
traceability, fresh executable evidence and explicit limitations. It does NOT
claim an exhaustive API/behavior inventory of either SDK or final acceptance.

Authoritative machine-readable accounting:
`tmp/r2-gap1-functional-accounting.json`, generated by the diagnostic
`tmp/r2_gap1_accounting.py`. It contains the unchanged original shell blocks,
original section IDs/order/lines, upstream requirements, native entry symbols,
AST-verified source lines and SHA256s, actual callchains, supported inputs,
oracle strength, dependencies, remaining behaviors, exact executed node IDs,
JUnit paths, actual process exits and same-process import origins. Every chosen
proof selector must match an actual JUnit testcase; mere source presence cannot
satisfy that check. An initially unexecuted gradient selector genuinely stopped
the accounting generator. The existing gradient/transform suites were then
actually executed and their source-bound receipt added; no fabricated proof.

Original matrix: `scripts/run_local_matrix.sh`, SHA256
`1d93b127aa5783541178d6c852ecec3457fac89694248dd2cd270dad989a7798`.
Workflow SHA256 remains
`e6cbbc6c580df678375e437db9859e441c19b3a136bfde125fcb6b27244dac81`.
Current selected source still matches5a47a0ec/1619files and the final QPY2
archive, including every new GAP receipt before/after. Matrix/workflow are
unmodified. This audit did NOT rerun the original whole28-section script:
inventory sections mutate docs, optional references are missing, and a selected
pytest suite is not a whole-matrix run. HEADb443430/main/ahead51 is not the
uncommitted implementation candidate; no stage/commit/fetch/push occurred.

Fresh actual terminals, all using the same1619 selected source bytes:

| Receipt stem under tmp/ | Actual result | What it proves |
| --- | --- | --- |
| r2-gap1-curated-main | 105PASS,0fail/skip/xfail,exit0 | Selected native/provider/primitive/Aer/industry tests plus actual public Qiskit/PL/qchem comparisons |
| r2-gap1-curated-alternate | 105PASS,0fail/skip/xfail,exit0 | Same selected cases in isolated Qiskit2.6.0/PL0.42.3, not all SDK APIs |
| r2-gap1-curated-strict | 99PASS,0fail/skip/xfail,exit0 | Same native subset with no Qiskit/PL/TF/JAX resolution/import, python-s/no user site |
| r2-gap1-lane-samples-main | 16PASS,0fail/skip/xfail,exit0 | Original chemistry-core files, small optional wrapper/conversion, temp inventory writer and existing local Studio execution smoke |
| r2-gap1-structural-ad-main | 104PASS,0fail/skip/xfail,exit0 | Actual native QNode derivative and basic structural transform suites |
| r2-gap1-core-contracts-main-v2 | 3PASS/9FAIL,0skip/xfail,exit1 | Real unresolved public ABI/behavior gaps in Qiskit2.4.1/PL0.44.1 |
| r2-gap1-core-contracts-alternate-v2 | 3PASS/9FAIL,0skip/xfail,exit1 | Same9 failure IDs in Qiskit2.6.0/PL0.42.3 |

These are overlapping scopes, not additive function counts. Main selected
curated executes Qiskit2.4.1 and PL0.44.1; Alternate executes2.6.0/0.42.3.
Only actual imported origins in each JSON prove a reference execution. The
separate dependency-resolution snapshot is explicitly resolution-only: it finds
Main Nature0.8.0, Algorithms0.4.0, OpenFermion1.7.1, PySCF2.13.1, Aer0.17.2,
Runtime0.46.1 and pyquafu0.4.5; it does NOT prove their imports or functioning.
Finance, Optimization, ML, Dynamics, Metal, Experiments, all4addons,
TorchQuantum and quark are unresolved in that Main environment. No dependency
was installed. Main known pip conflicts remain; no globally-clean-env claim.

The retained initial public-probe receipt
`tmp/r2-gap1-core-contracts-main.{json,xml}` has11FAIL/1PASS. Eight were harness
errors: the diagnostic assumed public `PrimitiveJob.result(timeout=30)`, while
the installed public signature is `result()`. Only the tmp diagnostic invocation
was corrected; no production or original test changed. The corrected v2
receipts, not that initial harness count, establish the9 actual native gaps.
Public precision was also observed rather than guessed: on the seeded test
public EV=-0.8898737546494153, stds=0.0 and target_precision=.1; no assertion that
public stds must equal .1 was introduced.

##### Original28 Lanes, In Their Unmodified Order

The status below applies to the lane's full functional intent, NOT its CI job
conclusion. KNOWN_FAILING means demonstrated public parity failure, not that
the original lane was freshly run and failed. Each full upstream behavior
denominator remains UNKNOWN. Positive subset execution, API implementation and
complete behavioral parity are separate facts; the JSON retains all three
through source entries, exact observations and explicit scope/limitations.

| Original section ID | Functional status | Actual native behavior and principal remaining gap |
| --- | --- | --- |
| core-only | KNOWN_FAILING | Real native Circuit/Operator/compiler/device/AD subsets; default Operator56, annotation-index2 and public execution gaps remain. The original label alone does not isolate SDK imports |
| qiskit-extra | KNOWN_FAILING | Actual basic Circuit/IR/counts bridge in both versions; four old adapter tests are not full Circuit/Target/quantum_info/Primitives parity |
| pennylane-extra | KNOWN_FAILING | Actual scalar QNode and tape/observable bridge; native parameter broadcasting fails, outbound PL callable is upstream execution |
| qiskit-aer-extra | PARTIALLY_SUPPORTED | Native CPU double state/density/tableau/MPS/unitary/superop/save/set/noisy feedback subsets; GPU/non-double/options and full method/protocol/performance scope remain |
| qiskit-finance-extra | PARTIALLY_SUPPORTED | Synthetic four-asset budget2 exact classical enumeration,1001 and objective-.0278; not complete Finance or tutorial quantum optimizer flow; reference package missing |
| qiskit-optimization-extra | PARTIALLY_SUPPORTED | Binary quadratic objective/linear constraints/bruteforce, optimum-1.35 and infeasible case; not full mixed integer/continuous/converter/solver family |
| qiskit-machine-learning-extra | PARTIALLY_SUPPORTED | Tiny native QNN forward and separate native kernels exist; fresh forward oracle only finite/bounded, full QNN training/derivatives/public protocol unproved |
| qiskit-nature-extra | PARTIALLY_SUPPORTED | Fixed educational H2 example distinguished from real geometry-generated s-Gaussian/RHF/JW H2 path; full bases/elements/properties/open shells/differentiable HF/UCCSD incomplete |
| qiskit-algorithms-extra | PARTIALLY_SUPPORTED | Actual marked-state Grover, exact eigensolver/gradient descent helpers; exact probability sum/classical phase eigendecomposition are not full quantum AE/PE algorithms |
| qiskit-dynamics-extra | PARTIALLY_SUPPORTED | Offline2x2 Z/Rabi evolution; dephasing is metadata damping, not a full Lindblad solver. Fresh shape/tag smoke is not a numerical parity proof |
| qiskit-metal-extra | NOT_IMPLEMENTED | Advisory/schema wrapper only; no native CAD/EM/fabrication capability demonstrated; missing upstream also blocks external comparison |
| qiskit-runtime-extra | NOT_IMPLEMENTED | Offline inventory/passthrough/schema, no token read; no native IBM service/session/batch/cloud primitive implementation shown by these wrappers |
| qiskit-experiments-extra | PARTIALLY_SUPPORTED | Synthetic Rabi data/local fit; not real calibration, complete analysis/service/database or experiment framework |
| qiskit-addons-extra | NOT_IMPLEMENTED | SQD/MPF/AQC/OBP advisory wrappers; lookup/schema tests do not implement addon algorithms |
| pennylane-full-extra | KNOWN_FAILING | Native measurements/shadows/selected transforms/real AD/qchem; operation broadcasting fails, public UCCSD template entry absent, full devices/plugins/capture/qcut unfinished |
| mqt-compat | PARTIALLY_SUPPORTED | Greedy topology/SWAP routing and decoded3wire probability equivalence; same-engine comparison is not complete DD simulation or optimal QMAP |
| torchquantum-compat | PARTIALLY_SUPPORTED | Native tiny RY/RZ/CX layer forward/IR; NumPy wrapper not full TorchQuantum trainable device/module protocol |
| qos-uqci-compat | PARTIALLY_SUPPORTED | Native offline Bell128shot mock/job/spec, hardware=False; no actual authenticated service/backend evidence in this audit |
| quafu-compat | PARTIALLY_SUPPORTED | Offline mock Bell128shot checked; separate real QuarkStudio transport source exists, but no fresh real transport call/hardware evidence, quark unavailable |
| benchpress-compat | PARTIALLY_SUPPORTED | Local runner/timing/status aggregation with fake deterministic callables; not workload parity or validated performance comparisons |
| studio-backend-api | PARTIALLY_SUPPORTED | Existing local request/registry/in-memory execution smoke only; no UI/server expansion; status success is not science validation and old Router issue stays open |
| ecosystem-inventory | PARTIALLY_SUPPORTED | Temp-dir inventory writer/missing-dependency/schema contracts; original generators not rerun; capped import-name inventory does not establish native behavior |
| dev | IMPLEMENTED_UNVERIFIED | Selected source-bound regression is green within its scope; original whole-worktree pytest/coverage/new-SHA CI/finalR2 gates not newly verified |
| chemistry-core | PARTIALLY_SUPPORTED | Actual native FermionicOp/JW/QubitHamiltonian and general-complex JW comparison; ParityMapper and BravyiKitaevMapper explicitly raise NotImplementedError |
| chemistry-extra | PARTIALLY_SUPPORTED | Optional Nature provenance wrapper and one actual OpenFermion conversion; upstream driver execution/conversion is not native electronic structure parity |
| qiskit-nature-p2-extra | IMPLEMENTED_UNVERIFIED | Optional wrapper and existing inventory-heading test run; installed driver/H2 lane not rerun, no generator mutation or full driver parity claim |
| algorithms-extra | IMPLEMENTED_UNVERIFIED | Optional vqe() adapter returns only status; installed VQE test runs upstream VQE and wraps it, not Native VQE parity |
| openfermion-extra | PARTIALLY_SUPPORTED | One actual creation-annihilation term0.5 converts exactly; not full OpenFermion molecular/API capability |

Reference validation for unresolved optional packages is ENVIRONMENT_BLOCKED,
separate from whether a native subset executes. Deliberately refused GPU,
unsupported format/AD paths are UNSUPPORTED, not positive implementation proof.
Native functions with only shape/finite smoke are IMPLEMENTED_UNVERIFIED for
their wider mathematics. These distinctions must not be merged into PASS.

##### Core Function Families Beyond The Adapter Lane Names

| Requirement family | Current actual evidence | Remaining final contract |
| --- | --- | --- |
| QuantumCircuit/Instruction/Bits/Parameters | Existing native mutable/owned bit graphs, symbolic parameter/calculus, composites/control/inverse/power, dynamic nodes, qualified QPY2 records | All signatures/classes/scopes/classical expressions/calibrations/schedule and public error/alias contracts not closed; annotation-index2 remains |
| circuit.library/operations/templates | Actual native standard/composite gates, bounded embeddings/entanglers/IQP/QFT/Trotter and real derivatives | Complete catalog/synthesis/arithmetic/state preparation/public object protocols not enumerated or accepted; public UCCSD entry absent |
| transpile/PassManager/Target | Actual layout/basis/routing/levels0-3, DAG invariants, ASAP/ALAP schedules and full-complex-operator tests in source-identical broad receipt | Complete pass/plugin/synthesis/backend properties/options/public signatures and general dynamic timing remain incomplete |
| quantum_info | Native mixed-radix Operator/state/density/channel/Clifford/Pauli/MPS subsets, matrix and resource evidence | Default Operator arithmetic still56 failures/version; full class/public container/dimension/synthesis/random/channel families not closed |
| Primitives V2 | Existing scalar physics works; legacy native PUB helpers execute | Actual7 public Sampler/Estimator constructor/input/shape/metadata/job-identity gaps below; full containers/precision/shots/session protocol incomplete |
| Provider/Backend/Job | Existing local discovery/config/options/state/counts/batches and unique provider Job IDs execute | Local Job calls submit synchronously; full asynchronous lifecycle/cancellation/BackendV2 Target/service contracts not established |
| QPY/QASM2/3 | Actual supported QPY13 standard records, UUID/parameter/control/composite/qualified unitary exchange; bounded text language/scope | Other versions/full instruction families/languages/types/includes unresolved; original public loss and partial-binding/trig differences remain OPEN |
| Aer/devices/noise | Real CPU vector/density/stabilizer/MPS/linear-map kernels and save/set/noise/dynamic subsets | Full options/GPU/performance/channel/noise families and general truncating MPS differentiation not established |
| QNode/measurements/devices | Real scalar/multiple measurements, counts/state/probs/density, shot partitions and classical shadows | Broadcasting red; full public constructor/executor/capture/device_vjp/plugin/remote contract incomplete |
| transforms/gradients/interfaces | Native decompose/cancel/compile/split/QWC/deferred subsets, shift/adjoint/JVP/VJP/Hessian/HVP, actual bounded four-framework graphs | General dynamic transforms/MCM/capture/stochastic/device gradient protocols and higher orders outside admitted subsets remain; full interfaces not accepted |
| metric/QNG/SPSA | Existing metric_tensor, qng_step and spsa_gradient are real callable native numerical helpers, not absent | Their finite-difference state-function interface is not complete PL tape transform/optimizer/AD parity; broad public-equivalence verification not claimed |
| qchem/Nature | Actual geometry H2/STO3G s-shell integrals/RHF/fermion/JW, number conservation, independent quadrature/public overlap/Hamiltonian tests | General elements/angular momenta/basis/open-shell/active-space/tapering/properties/differentiable HF/UCCSD and material workflows unfinished |
| algorithms/optimizers | Native VQE/QAOA/Grover/linear algebra/gradient-descent subsets exist | Full algorithm/result/optimizer families plus real PUB/backend glue and true quantum AE/PE not supplied by exact classical helpers |
| resource/kernels/QNN/qcut/plugins | Actual compiler gate/depth analysis, native small overlap kernels/QNN and native shadows distinguished from passthrough wrappers | Resource family completeness and full derivative/training/device plugin contracts unverified; surveyed qcut path is upstream scaffold, not native cutting/reconstruction |
| industry/remote | Small real native industry workflows; real QuarkStudio transport source and preserved prior cloud receipts | Four-category19direction taxonomy is not completed industry functionality; new actual backend-capability/lifecycle evidence absent; no hardware jobs in this audit |

The dated Stage11O ledger's statement that JAX/TF are entirely unimplemented
is superseded by the actual Stage12 bounded graph evidence. Conversely, actual
TF/MPS100wire exact-low-bond support must not become a general truncating-MPS,
all-orders or full PennyLane claim. Native shadows/fermionic excitation/metric
helpers must not be called absent merely because similarly named ecosystem
adapters are scaffolds.

##### Exact New Public Failures And Working Controls

All node IDs below are in `tmp/test_r2_gap1_core_contracts.py`. Both actual
version pairs execute the same physical circuits/angles and have identical9
failure IDs. Unsupported exceptions count as failures, not skipped successes.

| Test suffix after test_ | Actual observation |
| --- | --- |
| sampler_public_default_shots_constructor_is_callable | Public default_shots=16 accepted; native alias rejects keyword |
| sampler_result_retains_the_actual_classical_register_name | Public default register c; native result always meas, data.c missing |
| sampler_parameter_batch_shape_is_not_flattened | Public BitArray shape(2,2); native returns flat list4, physical basis counts themselves agree |
| sampler_independent_runs_have_distinct_job_identity | Public distinct IDs; native constant quantumbridge-primitive-result |
| estimator_public_pauli_label_input_executes | Same Z string input works publicly; native malformed-complex-string ValueError |
| estimator_pub_broadcast_preserves_shape_and_axis_semantics | Public2x2 [[cos(.23),cos(.91)],[sin(.23),sin(.91)]]; equivalent native Pauli objects produce(2,2,1) with parameter-outer orientation |
| estimator_precision_metadata_retains_the_public_target_precision | Public target_precision=.1; native precision-only metadata, exact-mean behavior; no accepted full precision distribution proof |
| qnode_public_operation_broadcast_reaches_native | Public RY([.23,.91]) gives cosine vector; native scalar-angle admission explicitly rejects broadcasting |
| public_uccsd_template_has_a_callable_native_entry | Public4wire/2electron UCCSD actually normalizes and conserves particles; native template namespace has no UCCSD entry, separate excitation kernel exists |

The3 controls actually pass in both: same X/measure16shot counts, scalar RY/Z
Estimator cosine and scalar native/public QNode cosine. This shows working
physics underneath missing execution contracts, NOT a25% overall completion.
The UCCSD test only proves absent template entry, not absent chemistry kernels.

Formal old reds remain unchanged: default Operator56FAIL/5PASS each version;
annotation-index2FAIL each; public QASM h/X definition-loss1FAIL each;
public2.4trig29PASS/1FAIL versus2.6all30PASS; malformed public2.4partial-bindQPY,
repeat/inverse public construction differences, matrix alias and constant-gradient
ABI beyond proved subsets remain OPEN. None is deleted, loosened, or relabeled
as native full parity. There is no new xfail/skip or Operator-default switch.

##### Priority And Dependency Decision

Priority is based on public-core importance, blocked user workflows, real oracle
availability, existing engine reuse, regression cost and uncertainty, not test
count or easiest wrappers. One implementation candidate is proposed below.

| Rank | Work family | Reason, dependencies and risk |
| --- | --- | --- |
| 1 | Public Primitives V2 execution contract |7actual public failures, central sampling/observable execution API, local analytic and2version oracle, reuse existing parameters/registers/devices. Legacy alias/result ABI conflict requires explicit reviewed decision |
| 2 | QNode operation/batch broadcasting end-to-end | Actual basic RY vector fails; affects many PL programs, measurements and AD. Must preserve batch/shot/measurement/parameter axes across devices and framework graphs; high regression risk |
| 3 | Circuit/quantum_info public ABI plus compiler integration | High fanout and56actual default arithmetic mismatches; require separate contract review, not an audit-time default switch. Protect native ordering/dimensions/math and current compilation |
| 4 | Full template/qchem pipelines | UCCSD entry plus general geometry/SCF/excitation/basis/active-space gaps; dependent on correct devices/AD/PUB contracts. Independent integral/fermion math required |
| 5 | Full device/transform/noise/plugin protocols | Existing bounded kernels valuable but not complete dynamic/gradient/capture/truncation/plugin support; high mathematical and engineering uncertainty |
| 6 | Complete algorithm/industry families and remote evidence | Must compose real implementations through corrected core APIs; no status-only adapters. Remote proof depends on actual authorized service and hardware capabilities |

Import fanout check is explicit: current `rg quantumbridge.primitives quantumbridge`
finds only primitive modules and root exports. Existing native VQE/finance code
mostly calls devices/enumerators directly. Therefore priority1 has high PUBLIC
workflow importance, but claiming that current Native VQE/finance already depend
on Primitives would be false. Integrating those workflows is additional work.

##### Exactly One Next Implementation Prompt, Not Yet Executed

Stage12-B R2-PV2: Implement the public Primitives V2 PUB execution contract in
the existing NativeCore, without creating a second Circuit, parameter store,
compiler or simulator. Original sections: core-only, qiskit-extra, dev; algorithm
and industry lanes are future consumers, not assumed current callchains.

Start by confirming the same candidate source and preserving both actual v2
9red/3control receipts. The specific task is the seven demonstrated public
Sampler/Estimator failures, with true shape-aware PUB/result semantics rather
than a hardcoded fix for their one-qubit samples. Read actual installed public
signatures and behavior in both SDK versions. Use only public oracle execution,
not copied/private SDK implementation. Reuse Circuit parameters/UUID/register
graphs, ShotSampler/StatevectorDevice and existing provider execution contracts.

First resolve and show the owner the legacy/public contract collision BEFORE
production changes: tests/primitives/test_primitives_v2.py explicitly requires
StatevectorSampler(shots=...).run(...).result() is the immediate result and a
constant job ID; another alias test requires the old parameter-outer nested
Estimator shape. Those assertions are incompatible with public V2 semantics.
Keep legacy Sampler/Estimator native calls and run_pubs contracts explicitly
available. Propose a clear public-facade migration; do not silently switch modes,
rename failures, weaken math, or update old tests without explicit approval.
No concrete ABI migration has been approved by this gap audit.

Implement/coerce PUB inputs with retained parameter batch shape and UUID order,
shape-aware observable normalization/broadcasting and true public register-named
BitArray/DataBin/PubResult outputs. Preserve each register's classical bit order,
partial/unmeasured bits and shot order, not a counts-expanded fake memory stream.
Default/public/run/PUB shots precedence and invalid shots/precision/shape/width
admission must match actual contracts. Sampler constructor accepts public
default_shots/seed behavior. Estimator accepts Pauli labels and appropriate
observable families; evs axes and values obey broadcasting, not unconditional
Cartesian nesting. Target precision metadata/behavior must be observed in both
public versions and verified, not implemented as metadata-only pretend sampling.
Each real execution has a distinct job identity. Preserve truthful terminal/error
states and result containers; do not claim an asynchronous service from an
immediate local object or implement IBM Runtime sessions as offline wrappers.

Expected ownership: existing quantumbridge/primitives/{sampler,estimator,
containers,backend,__init__}.py; a narrowly scoped shared PUB normalization module
only if it removes actual duplicate logic; existing provider Job/Result or core
register/parameter helpers only when an observed contract requires it. No broad
compiler/device arithmetic rewrite, no second simulator, no new dependency.

Required red->green proof: preserve original mathematical inputs and seven IDs;
scalar/multi-PUB and zero-parameter inputs, nontrivial2qubit entangled states,
multiple/unequal-width/classical-register and unused-bit mappings, arbitrary
leading parameter dimensions, scalar/broadcast-compatible/incompatible observable
shapes, same-name/different-UUID parameters, bound/unbound admission, per-PUB shots,
seed reproducibility versus independent jobs, actual measurement memory/packed
bits, deterministic expectations plus justified precision statistics, genuine
errors before publication. Compare both public SDKs and independent analytic/full
matrix/count oracles; one example does not establish the whole protocol. Keep
all legacy numerical tests, native Parameter/Compiler/Operator/QPY2/TF-MPS and
resource/readonly/atomicity contracts. Add cumulative work/shot/storage admission
through existing limits; no unbounded batch expansion or private sidecar.

Freeze unique source only after actual focused success. Rerun affected legacy
native tests, both public differential environments, strict SDK-free native
execution, selected broad/TF and original known-red probes; record actual imports,
node IDs, source-before/after, JUnit and terminal exits. Original fullR2/FULL/
GLOBAL/legal/Git3state and the two unrelated PL probe failures remain OPEN.
No git/auth/cloud/hardware/Studio/vendor/tag/release changes. At most accept a
demonstrated public V2 contract milestone, never full SDK replacement. Owner
direction/ABI approval is required before executing this proposal.

##### Conditional Effort Envelopes, Not A Completion Forecast

These planning intervals are low-confidence engineering effort for a dedicated
experienced implementer plus review, AFTER scope/contract decisions and assuming
working local oracles. They are not measured velocity, deadlines or additive
remaining-time totals. Regression/novel math/dependency changes can exceed them.
The full original objective remains unchanged and its total completion percentage
and credible finish date are UNKNOWN.

| Capability domain | Approximate planning envelope | Main dependencies and uncertainty |
| --- | --- | --- |
| Public V2 PUB execution contract |2-6 engineer-weeks for the specified contract, not full Runtime | Legacy/public ABI decision, bit/shape/shot/precision oracles, resource accounting |
| QNode broadcasting and its measurement/AD axes |3-8 engineer-weeks for a validated end-to-end family | Four-framework graphs, device/shot partitions, stochastic/transform interactions |
| Remaining Circuit/Operator/compiler public families |3-9 engineer-months as a group, low confidence | Exhaustive behavior list, default ordering migration, synthesis/pass/Target/dynamic timing |
| General device/transforms/AD/plugin families |3-12 engineer-months, possibly more | Full device protocols, capture/remote plugins, higher orders, MPS truncation/degeneracy math |
| Full interchange languages/object families |2-6 engineer-months, possibly more | Chosen format versions, public version differences, includes/types/expressions/opaque records |
| Broad Aer methods/noise/options/performance |6-18 engineer-months, possibly more | CPU/GPU/parallel infrastructure, independent noise/performance oracles, full result methods |
| General qchem/Nature/templates |6-18 engineer-months, possibly more | Basis data/provenance, angular integrals/SCF/open shells, differentiable HF, properties/mappers |
| Full algorithms and named industry ecosystem |6-18+ engineer-months; all-project total UNKNOWN | Correct core protocols, real algorithm math and workflows; many package APIs still not enumerated |
| One authorized real cloud backend integration/validation |4-12 engineer-weeks after access/capabilities known | Transport/backend service version, quota/cost limits, mapping/gates/shots, actual hardware receipts |

Parallel engineering can overlap some domains, but shared-core decisions and
hardware queues prevent simply dividing by agent count. A bounded useful core
can improve in months; full independent native replacement at this breadth is a
year-scale or multi-year planning problem, not a promise. IBM/Quafu hardware
cannot return simulator-only state APIs merely because a software facade exists.

No new owner-facing page/report/server was created; this updates the existing
implementation journal, keeping raw diagnostics in tmp/. Existing finance and
hardware receipts were preserved. New cloud/hardware tasks0, production edits0,
original test edits0, dependency installations0, git/auth mutations0. Proposed
ONLY R2_FULL_PARITY_FUNCTIONAL_GAP_AUDIT_READY_FOR_REVIEW for representative
lane accounting; exhaustive all-API inventory, original finalR2 gates and full
independent replacement remain ACTIVE / INCOMPLETE. Peer review and owner
implementation-direction approval are still pending.

#### R2-PV2-A Public Contract Oracle And Legacy Migration Decision

Complete peer review now accepts ONLY the preceding representative functional
audit, not independent repository/remote verification or finalR2/fullSDK. Its
first answer actually stopped midsection3. A precise follow-up plus existing
Chrome refresh exposed complete P0-P8 preparation requirements, archived in
the existing received-prompt journal. Owner has not yet answered the async
direction question. No default/API/old-test migration is authorized or performed.

Actual public-only diagnostic `tmp/r2_pv2_public_contract_probe.py` imports
Qiskit/NumPy but never QuantumBridge. Both direct runs exit0 and preserve full
typed numerical/packed-bit/metadata/exception observations in
`tmp/r2-pv2-a-public-{main,alternate}.json`. A separate pytest wrapper actually
executes the9 cases again, records full observations and probe/wrapper SHA256s
in JUnit, and asserts no QuantumBridge module was imported. Source-bound
`tmp/r2-pv2-a-public-gate-{main,alternate}.{json,xml}` each9PASS,0fail/skip/xfail,
exit0, actual Qiskit2.4.1/2.6.0 origins. Direct and pytest runs have distinct
real Job IDs; they are separate executions, not claimed identical processes.
Selected source-before/after stays5a47a0ec/1619. Nine green reference cases
are NOT nine Native V2 fixes, and negative-input ValueError verification is
explicitly a public error contract, not Unsupported-as-numerical-success.

Strict SDK-free current-Native baseline actually5PASS,0fail/skip/xfail,exit0:
`tmp/r2-pv2-a-native-baseline-strict.{json,xml}`. It proves exact scalar physics,
16shots, legacy alias/result identity/constantjobID, old(2,2,1) axis behavior,
existing qubit/memory denial and native reset ensemble expectation. It does
NOT prove a global Primitive PUB quota or publicV2 correctness. The original7
unmodified public Primitive probes are freshly rerun as
`tmp/r2-pv2-a-original-contracts-{main,alternate}.{json,xml}`; actual7FAIL and
5deselected each,exit1. The5 are deliberately unselected3controls+2otherPLgaps,
not skips/xfails. No original inputs, tolerances or failure IDs changed.

##### Actual Dual-Version Public Behavior

| Contract | Actual Qiskit2.4.1 and2.6.0 observation | Current Native implication |
| --- | --- | --- |
| Constructor/signature | StatevectorSampler(*,default_shots=1024,seed=None); Estimator(*,default_precision=0.0,seed=None); run takes keyword-only shots/precision and Iterable PUBs | Native Statevector names are exact aliases of older Sampler/Estimator; constructor and return ABI are not publicV2 |
| Job/result | PrimitiveJob.result() returns PrimitiveResult; job is not result; repeated result() is same result; separate runs have distinct real IDs | Legacy PrimitiveResult.result() returns itself and has a constant fallback ID |
| Actual PUB classes | Sampler gives SamplerPubResult; Estimator gives PubResult, NOT an assumed class named EstimatorPubResult; both DataBin shapes are explicit | Existing generic PubResult/DataBin wrappers have no equivalent complete shape contract |
| Parameter batch | RY values shape(2,2,1) produces BitArray.shape(2,2), packed uint8 shape(2,2,3,1) for3shots, exact0/pi per-point counts | Current native flattening erases leading shape; current BitArray is tuple strings, no packed multidimensional backing |
| Register output | Separate a2bit and b9bit registers, partial measurements/unmeasured bits, a=11 and b=000000000 in selected deterministic circuit | Current native meas field loses public register identity; this selected b case checks padding/width only, not every nonzero9bit byte-order case |
| Shots precedence | default5, run override7, per-PUB override13; per-PUB overrides run | Need preserve precedence and enforce total actual workload, not just set a metadata field |
| Integer seed | Repeated runs with int11 on selected H circuit repeat the same16-shot sequence while Job IDs differ | Reproducibility and identity are separate; only this actual RNG observation is proved |
| Generator seed | Same Generator instance advances: second16-shot sequence differs | Must not reconstruct or copy Generator as if it were an integer seed; concurrency ownership needs design |
| Nontrivial broadcast math |3wire RY(theta)/RZ(phi) on wire2, params batch(2,2), observables(3,1,1), evs(3,2,2), full independent cos(theta),sin(theta)cos(phi),sin(theta)sin(phi) | Public Pauli string rightmost character means wire0; normalize at boundary without changing native q0-first conventions |
| Incompatible broadcast | Observables(3,) and params(2,) reject with ValueError and explicit shape message | Do not execute a Cartesian product or reshape into a plausible wrong result |
| Precision | With seed17 and X/Z: run precision.1 -> EV-.8898737546494153; PUB precision.05 -> EV-.9449368773247077; stds both0, target_precision metadata matches overrides | Native exact-mean + precision metadata does not implement observed public finite-precision behavior; stds must not be invented as precision |
| Reset | Bell preparation then reset(wire0), Z(wire1), public seeds2/3/4/5 give+1,+1,-1,-1; native exact branch ensemble gives0 | Both can be valid mathematics but different execution contracts. Do not globally replace Native ensemble math; future public facade must implement verified public trajectory semantics |

The mathematical oracle constructs the full3x2x2 Bloch values independently
and uses np.broadcast_shapes, not SDK-generated expected values. Deterministic
basis counts alone are asserted exactly. Stochastic H counts are recorded as
samples and are not equated to analytic probabilities. Seeded precision/reset
numbers are observed finite examples, not proof of a whole random distribution,
all nonunitary circuits or cross-version RNG equivalence beyond this sample.
Packed nonzero multi-byte bit order, register aliases/colliding field names,
zero-size dimensions, all observable families and all error variants remain
required implementation tests, not claims inferred from9 observations.

##### Seven Reds By Behavior And Actual Root Cause

All IDs are under `tmp/test_r2_gap1_core_contracts.py`, unchanged from GAP1.

| Exact test suffix | Behavior class | Source root cause |
| --- | --- | --- |
| test_sampler_public_default_shots_constructor_is_callable | CONSTRUCTOR_ABI | sampler.py::Sampler.__init__ takes shots; StatevectorSampler aliases it |
| test_sampler_result_retains_the_actual_classical_register_name | RESULT_CONTAINER | run_pubs hardcodes DataBin.meas instead of projecting native cregs |
| test_sampler_parameter_batch_shape_is_not_flattened | PUB_NORMALIZATION / RESULT_CONTAINER | _parameter_array_to_mappings reshape(-1,nparams); BitArray has no batch shape |
| test_sampler_independent_runs_have_distinct_job_identity | JOB_LIFECYCLE | PrimitiveResult itself acts as job; default job_id constant |
| test_estimator_public_pauli_label_input_executes | PUB_NORMALIZATION / NUMERICAL_EXECUTION | Plain string reaches generic observable_matrix conversion rather than Pauli normalization |
| test_estimator_pub_broadcast_preserves_shape_and_axis_semantics | PUB_NORMALIZATION / NUMERICAL_EXECUTION | Parameter-outer Cartesian loop plus nested _restore_shape, not NumPy broadcasting |
| test_estimator_precision_metadata_retains_the_public_target_precision | METADATA / NUMERICAL_EXECUTION | Precision-only key; current exact evaluation has no public seed/precision stochastic execution |

##### Reusable Native Architecture, Not A Second Runtime

Existing native path is Sampler.run[_pubs] -> parse -> parameter mapping ->
ShotSampler -> StatevectorDevice.run_shots/probabilities -> Result -> BitArray/
DataBin/PubResult. Current Sampler._run_legacy does NOT request memory=True,
so static results can fall back to sorted counts expansion: that is not true
shot order and must not serve as public packed memory. ShotSampler already
supports memory=True and StatevectorDevice already routes static/dynamic shot
execution; reuse these paths rather than re-sampling from reported counts.

Estimator -> existing StatevectorDevice.expectation -> bound/lowered Circuit
and existing observable kernels. It currently averages dynamic branches;
that exact native ensemble remains protected. Public statevector reset behavior
needs explicit facade-level trajectory selection through existing dynamic/shot
kernels, with observable/RNG semantics verified, not an alteration of generic
device expectation. Existing backend facade delegates to Backend.run/Job,
which is synchronous, catches errors and stores results. Its module-global
itertools counter is current provider behavior, not a freshly proved portable
concurrent public Job factory; no new unverified global counter is proposed.

Circuit bit identity/register membership already lives in core/bits.py:
initialize_bits/add_register/find_bit preserve native Clbit keys and aliases.
Project each public register by those identities from genuine classical memory;
native display order and public packed/display order are a boundary conversion,
not permission to reverse the whole simulator or discard UUID/alias information.
Existing Parameter bindings/owned copies/compiler traversal must be reused.

##### Explicit A/B Migration Alternatives

Neither alternative is implemented or selected on the owner's behalf.

| Item | A: Explicit transitional PublicV2 entry | B: Owner-approved target public defaults |
| --- | --- | --- |
| Proposed entry, not existing API | A clearly named/module-scoped publicV2 facade; current Sampler/Estimator/Statevector aliases unchanged | Current target StatevectorSampler/StatevectorEstimator names become real publicV2 facades; native Sampler/Estimator and clearly named Legacy aliases retain exact old behavior |
| Return policy | Entry name selects contract, never shape/kwargs guessing | Same: public names always public contract; legacy names always legacy contract |
| Existing tests | Original old alias/identity/nesting tests untouched; add independent public-facade tests | Exact conflicting old alias tests require reviewed migration to explicit Legacy entry or approved semantic split; preserve old math/inputs and add public tests, never erase the distinction |
| Known in-repo callers | Root/primitives exports and tests/primitives alias users; Backend classes inherit native Sampler/Estimator and should stay native at this stage | Same exports plus alias users migrate; MPS/density/stabilizer/control-flow BackendSampler/Estimator callers must not silently change to new public result nesting |
| Existing examples | Native stabilizer example uses BackendSampler/Estimator, not the Statevector aliases | Keep its current API; public backend V2 migration is a separate future reviewed contract |
| Shared implementation | Same existing binding/compiler/device/shot kernels; small shared input normalization only where genuinely useful | Same; change facade/default policy, not numerical engine |
| Resource cost | New V2 arrays/job/result ownership plus validation; no duplicate state engine | Same numerical/array costs plus compatibility migration/review; extra names do not remove ABI risk |
| Principal risk | Transitional opt-in must not be called final default/public parity | Breaking public alias signatures/result identities/shapes, import/pickle paths and unknown external-user usage; external callers have NOT been audited |
| Full-goal consequence | Useful migration step only; no-opt-in target parity still OPEN | Moves target default contract toward full parity after explicit approval; still not full primitives/SDK closure |

Exact known collision node IDs in tests/primitives/test_primitives_v2.py:
test_sampler_v2_accepts_qiskit_style_numpy_parameter_values_and_alias;
test_sampler_v2_result_is_job_like_for_qiskit_style_result_call;
test_estimator_v2_accepts_numpy_parameter_values_nested_observables_and_alias.
In particular the second asserts identity and constant ID; the third asserts
old parameter-outer3D nesting. Original11 existing primitive tests actually
passed in GAP curated baselines; these3 are not silently reinterpreted.

Actual callsite search across quantumbridge/tests/examples/scripts distinguishes
Native exports/internal subclasses from optional upstream Finance/Algorithms
imports of qiskit.primitives. Those upstream imports are not current Native V2
integration and do not justify a claim that native industry workflows are
already corrected by a facade change. External package-user usage is UNKNOWN.

##### Future Resource/Atomicity Contract, Design Only

For PUB i let P_i be the product of parameter batch dimensions, S_i actual
shots and w_ir the width of classical register r. Sampler packed retained
bytes are sum_i[P_i*S_i*sum_r ceil(w_ir/8)]. Also reserve input/shape/UUID maps,
true shot memory and packing temporaries, result metadata and actual state
workspace; packed output alone is not peak memory. Aliased registers still
produce separate result fields unless validated view sharing is explicitly
designed. Native string/NumPy intermediates need their own admitted payload.
Python object headers/allocator peak/RSS remain explicitly unavailable, not0.

Estimator E_i is the product of np.broadcast_shapes(observable_shape,
parameter_shape), not unconditional P_i*O_i. Retained float64 evs/stds need at
least16*sum(E_i) bytes plus metadata and owned observable/binding arrays. Reuse
actual parameter-point state work where allowed by public semantics; count
every observable action and any random precision/trajectory work. Do not map
precision to1/precision^2 imaginary hardware shots: these public statevector
observations use a different contract. Native max_memory_mb checks are not a
whole-PUB budget or OS memory sandbox.

Before any device call/result publication, boundedly normalize the whole job's
PUBs, validate all UUIDs/dimensions/shapes/observables/shots/options, calculate
integer-safe cumulative work/storage and acquire aggregate reservations. A
later invalid/oversized PUB must not leave already published earlier results.
For a runtime numerical failure, keep actual completed shots/work consumed,
release outstanding reservations, publish ERROR with no partial success result;
do not refund performed work or claim physical execution was rolled back.

Reuse UnifiedResourceLedger.preflight/reserve and parent-child accounts,
ResourceScope, existing array ownership/resident/retained lifetimes. Its actual
fields are memory/tapes/shots/derivative_work. PUB counts, broadcast/observable
points and concurrent jobs are NOT magically covered as existing named fields:
a narrowly scoped public-facade limits design and explicit mapping/extra caps
must be reviewed. Do not overload tape/shots counters with unrelated units.
Reserve retained result arrays until final result/view ownership ends, not only
until ResourceScope exit; use existing lifetime machinery, not leaked tickets.
All failure/one-below/concurrency paths need executable tests before acceptance.

Proposed Job identity mechanism is standard-library per-job UUID4 without an
ad hoc global incrementing counter. This supplies practical probabilistic
uniqueness, NOT a mathematical guarantee of zero collisions. If strict
per-service uniqueness is required, add a bounded synchronized live-job
registry/collision check with explicit lifecycle and concurrency proof; do not
claim that UUID4 or a finite stress test proves absolute uniqueness. Preserve
existing native Job status/result/error behavior behind Legacy; public pending,
result and error timing must be independently matched before public acceptance.

##### Decision Boundary And Next Production Scope

Preparation covers the demonstrated7 failure contracts, small independent
public oracles and concrete A/B impact, not exhaustive publicV2 validation.
Future smallest coherent production area remains existing primitives/sampler,
estimator,containers,backend,exports plus a genuinely shared normalization
helper if needed. Protect current legacy calls, quantum physics, full complex
operators, bit/UUID identity, existing compiler/QPY2/TF-MPS and resource safety.
Tests must extend beyond these selected cases: nonzero multi-byte memory,
multiple/aliased registers, actual shot order, general shapes/observables,
errors, RNG/precision/nonunitary semantics and cumulative atomic resources.

Awaiting specific human decisions: A versus B migration policy; exact target
default namespace; and, only for B, approval for the precisely listed old
alias-contract test migration. The prior async asks only whether to prioritize
this direction and prepare a plan; it does not by itself authorize old test or
default ABI changes. No implicit approval is inferred from the peer's review.
At most propose R2_PV2_PUBLIC_ABI_MIGRATION_DECISION_READY for review. The7
Primitive reds,2otherPLgaps,all formal old reds and all originalR2finalgates
remain OPEN. Full independent replacement ACTIVE/INCOMPLETE. No production,
old-test,dependency,Git/auth/cloud/hardware/UI change in this preparation.

Final preparation audit `tmp/r2_pv2_audit.py` actually exits0 and writes
`tmp/r2-pv2-a-preparation-audit.json`: both public-only9case ID sets match,
Qiskit versions/origins are actual, no QuantumBridge import in those gates,
both exact7failure ID sets equal the original GAP1 Primitive subset, strict5
native cases and SDK absence hold, every source-before/after equals current
5a47a0ec/1619, original probe SHA unchanged. No V2 implementation acceptance
follows. All required local runners have actual terminal exits.

#### R2-PV2-B Native PUB Input Containers: First Production Increment

The actual human reply selected option B: "方案 B：迁移目标默认接口并保留
Legacy（推荐）". The prior PENDING_OWNER decision above is historical and no
longer blocks the two target defaults or the three specifically listed alias
tests. It is not authorization to change other old semantics. The complete
production prompt was read in the existing default Chrome conversation;
its B0-B12 semantic record is in the existing received-prompt journal.

Concrete production progress, not a V2-completion claim:

- Added native `BindingsArray` and `SamplerPub`, exported through primitives
  and its existing containers module. Scalar, grouped, named, UUID/vector and
  ND parameter sets retain their parameter axis and batch shape. `as_array`
  reorders columns; `bind`/`bind_all` call the existing `Circuit.bind`, and
  independently derived complex RY/RZ states are executed by the existing
  StatevectorDevice. Basic slicing, reshape/ravel, zero axes, parameterless
  sets, PUB coercion and per-PUB/default shots are executable.
- Reused checked `array_layout`, the existing ledger/scope, whole conversion
  group reservations and retained ndarray-root leases. Noncontiguous reshape
  copies reserve the complete known group before their first allocation.
  Tests exercise exact/one-below bytes, parent/child denial, escaped ndarray
  and memoryview lifetimes, bounded eager bind_all, hostile foreign conversion
  rejection and huge zero-stride input rejection before value traversal.
  Accounting is owned numerical/object-pointer payload, not Python heap/RSS.
- No second simulator, parameter store, math engine or ledger. Legacy
  sampler/estimator/backend code and ALL existing test files remain unchanged.
  The Statevector defaults still point to Legacy at this intermediate state;
  the approved switch and three-test migration are NOT implemented yet.

Actual red: `tmp/r2-pv2-b-bindings-red-strict.{json,xml}` has 5FAIL/33ERROR/
1PASS, exit1, due to the two missing input classes. The old1619 source entries
are exactly equal to the prior5a47 freeze in this preproduction receipt;
only the new test file was added. The original receipt remains intact.

Current directed candidate: selected SHA
`74b56a1eb6a4efc5eb8e4bd8ebf73ecf824dc4938951e354a6cead40a4dcfed6`,
1623 files. Relative to5a47, four added files (two production/two tests), two
changed primitives export modules, and no changed original test. This is not
the former 5a47 candidate and not committed HEAD. Archive/manifest:
`tmp/r2-pv2-b-bindings-source.tar.gz` and
`tmp/r2-pv2-b-bindings-freeze.json`. Actual audit
`tmp/r2_pv2_b_bindings_audit.py` exits0 and writes
`tmp/r2-pv2-b-bindings-audit.json`, checking current/before/after hashes, old
test preservation, exact node sets, real origins, terminal exits and unchanged
original matrix-script SHA.

Actual terminal evidence on this candidate:

| Scope | Actual result |
| --- | --- |
| Strict SDK-free primitives, `r2-pv2-b-bindings-strict` | 62PASS, exit0, zero skip/xfail/error; prohibited SDK/TF/JAX resolution/import absent |
| Actual public input differential, Main/isolatedAlternate | 21PASS each, real Qiskit2.4.1/2.6.0 |
| Affected parameters/circuits/IR/QPY/four-framework/primitive set, Main/isolatedAlternate `*-affected-*-x64` | 496PASS each, exit0, same496 node IDs, zero skip/xfail/error/deselect |
| Unmodified complete GAP1 diagnostics `r2-pv2-b-original-contracts-*` | 3PASS/9FAIL each, exit1, same original9 failures, zero skip/xfail/deselect |

Initial affected runs omitted JAX_ENABLE_X64 and actually returned491PASS/
5FAIL in each environment, with explicit float64-to-float32 warnings. Those
exit1 receipts remain `r2-pv2-b-bindings-affected-{main,alternate}`. Rerunning
the identical496 tests with the prior established x64 configuration gave the
green receipts above; no production calculation, math expectation or tolerance
was changed. The initial five failure IDs and both actual configurations are
checked by the audit. This is a runner-configuration correction, not a claimed
production fix for those gradients.

Public-semantic boundaries remain OPEN: the installed public containers accept
duplicate/overlapping names and NaN at construction, bind same-name foreign
UUIDs by name, and SamplerPub may delay wrong-name detection. The new native
containers currently reject these earlier. The21 supported-domain matches do
NOT settle this difference or prove full BindingsArray/SamplerPub parity.
Next: separate public representability from whole-job pre-execution safety,
then complete Estimator PUB/observable normalization, genuine shot memory and
packed results, public Job, precision/reset trajectories, whole-PUB admission
and the approved default/three-old-test migration. The original7 Primitive
reds and2 PL gaps are not closed by this input-container increment.

Results were sent to the authorized ChatGPT peer for review/next execution
prompt. No broad/old411TF/full28matrix or originalR2 final acceptance is claimed
from these directed gates. Full replacement stays ACTIVE / INCOMPLETE. No Git
mutation, auth/TLS/dependency install/vendor/cloud/hardware/finance/UI changes.

Peer follow-up actually read: accepts only the reported binding/PUB supported
domain, explicitly not an independent local-code audit or public execution
acceptance. Complete R2-PV2-B2 now directs public container representability
versus safe execution admission, then the genuine Native Sampler shot-memory/
packed-result/Job path, approved Sampler-only default/two-test migration when
ready, followed by Estimator. Its complete semantic record is appended to the
existing received-prompt journal. This new prompt does not close any remaining
gap or turn the62/496 directed counts into SDK completion percentages.

#### R2-PV2-B2 Public Representation And Native Sampling Foundation

Previous goal turn was concrete progress (the74b56a1e input-container increment),
not a wait or completion of the overall SDK goal. Its archive/receipts remain
unchanged. This turn re-read actual source/worktree and continued B2 production.

Representation versus execution is now explicit. BindingsArray can preserve
duplicate/overlapping descriptions and nonfinite values, including through
basic views and reshape/ravel/default as_array. Original descriptor groups
retain UUID ownership after public-name normalization/collision handling.
SamplerPub construction checks cardinality, not circuit-name/finite execution
validity. Concrete Circuit binding and Job admission retain duplicate/owner/
finite rejection. No Native Parameter equality or binding engine was changed.
The first formal boundary gate had9FAIL and is retained in
`tmp/r2-pv2-b2-container-red.{json,xml}`.

One new oracle expectation was corrected: explicit duplicate-name reordering
in upstream BindingsArray.as_array can leave columns of np.empty uninitialized.
An observed zero or previous allocator value in an unwritten column is NOT a
reproducible mathematical value. Read-only inspection of that public method
confirmed placement can leave holes; no SDK source was copied into production.
Native explicitly rejects ambiguous requested reordering, while default
as_array preserves all duplicate columns. This precise difference remains
OPEN; undefined allocator bytes are not copied or hardcoded as an oracle.
Two duplicate safety cases and nonfinite guards introduced in the previous
increment retain their IDs/inputs and reject at execution rather than container
construction. All original pre-B test files remain byte-identical.

Added `quantumbridge.primitives.v2.StatevectorSampler`: real Native unitary/
terminal-measurement sampling, not an upstream proxy or a final opt-in product
decision. It uses Circuit.bind/lowered, existing gate validation, and
StatevectorDevice.sample -> existing Statevector.sample_memory and completion
metering. The same actual per-shot memory projects into named-register packed
uint8 data, bitstrings and counts. Native q0-first physics remains unchanged;
only the explicit selected-wire/register packing boundary changes display order.
Tests include2/9-bit nonzero registers (111000000 -> bytes[1,192]), both byte
boundaries, unused zeros, partial/noncontiguous/repeated measurements, ND
parameters, exact integer/Generator RNG progression, multi-PUB and shots
precedence. New sampler tests initially had10ERROR due to the absent module;
`tmp/r2-pv2-b2-sampler-red.{json,xml}` retains that actual terminal failure.

Public-style local containers/Job in this v2 module are isolated from unchanged
Legacy containers and provider code. Job differs from result, caches repeat
reads, preserves runtime exception type and clears failed executor tracebacks
so workspaces do not stay retained. Per-instance live/pending UUID4 collision
checks have bounded retries, with injected repeats and concurrent calls tested;
this is probabilistic identity plus scoped detection, not an absolute globally
collision-free registry or a remote/asynchronous service.

Whole-job admission checks every PUB before any quantum sampling: identity,
finite snapshots, shape/points/shots, register graph, parameter-specific lowered
gate legality and total packed output/work/conservative workspace. The existing
account lock preserves synchronous headroom while allocation still uses the
same ledger; no second resource accounting implementation. Result buffers are
reserved as one group before sampling. Exact/one-below and parent/child caps,
later bad/over-budget PUB before first execution, concurrent shared-parent
results, escaped ndarray/memoryview, real completed shots after second-PUB
failure, huge state rejection and zero-point huge-state nonmaterialization
are executable tests. A20001-point sweep is denied before snapshot copying.
Owned array/pointer/text-payload estimates are not a Python heap/RSS sandbox;
unknown partial work in a failed call is unavailable, not zero or refunded.

Actual current candidate:
`5fffca7053cf43dd54c3c5a8fa04010420f9916e3a3c7af2048e8a554804a85a`,
1626 selected files. Relative to74b, changed bindings_array/pubs, added v2.py,
refined the prior new binding tests' admission phase and added two formal test
modules. No Device/math/compiler/Provider production file, original pre-B test,
matrix script, dependency, Git, cloud/hardware/finance/UI state was changed.
Archive/manifest: `tmp/r2-pv2-b2-source.tar.gz`,
`tmp/r2-pv2-b2-freeze.json`. `tmp/r2_pv2_b2_audit.py` actually exits0 and writes
`tmp/r2-pv2-b2-audit.json`, checking identical before/after/current source,
actual exits/origins/JUnit, prior496 IDs retained and original pre-B tests.

| Actual terminal gate on this candidate | Result |
| --- | --- |
| `r2-pv2-b2-strict`, no prohibited SDK/TF/JAX resolution/import | 87PASS, exit0, zero skip/xfail/error |
| Main2.4.1 / isolatedAlternate2.6.0 `r2-pv2-b2-affected-*` | 539PASS each, identical539 IDs, zero skip/xfail/error/deselect, exit0 |
| Included actual public differential | 39 cases each: previous21 plus11 shot/packing and7 new representation cases |
| Complete unmodified original GAP1 `r2-pv2-b2-original-*` | 3PASS/9FAIL each, same9 failures, zero skip/xfail/deselect, exit1 |

The first Main public sampling gate was17PASS/1FAIL while Alternate had18PASS:
the harness submitted two asynchronous upstream Jobs sharing a Generator before
waiting for either. Its preserved baseline, initial JUnit and24 actual public
runs (`tmp/r2-pv2-b2-public-rng-race.json`) show two different complete outputs
under the same seed due to competing job order. The harness now waits for the
first result before submitting the second, so serial Generator advancement is
defined. Both installed public versions then give18PASS, included in current539.
No Native math/RNG/shot assertion was weakened. An initial standalone race
script invocation without PYTHONPATH imported a different old editable checkout
and failed; it is a runner error, not a Native runtime failure. The corrected
record asserts and includes this repository's actual QuantumBridge origin.

Still OPEN: reset/nonunitary public trajectories (the new path currently
rejects dynamic operations), complete public result helpers/types and export
relationships, all public container error/owner contracts, default Statevector
Sampler switch and two approved old-test migrations, then Estimator and its
third migration. Current root StatevectorSampler/Estimator are STILL Legacy
aliases; no old alias test was migrated and the original seven default-API
reds are NOT closed by testing the explicit in-progress v2 module. That module
is a construction step toward B, not a smaller replacement objective.

No Sampler-wide/B9/B10 acceptance: final migrated-candidate broad/old411TF/
nine-example and original R2 FULL/28matrix/coverage/exclusions/legal/origins/
Git-equality gates have not been executed here. All other prior formal reds,
QNode broadcasting and UCCSD remain independent OPEN. Results were sent to the
authorized peer for concrete next production instructions, not an independent
repo audit. Full independent Qiskit/PennyLane replacement ACTIVE/INCOMPLETE.

The actual next B3 prompt was read completely in condensed eight-point form
in the existing default Chrome conversation. It directs reset/trajectory and
full result/helper contracts, then the already-approved default Sampler/two
old-test migration and frozen regression. It explicitly does not independently
audit local code or accept the final goal. The received-prompt journal records
the complete execution instructions and remaining permissions.

B3 has begun with an actual public-only reset probe, not production changes
to the5fff candidate: `tmp/r2_pv2_b3_reset_probe.py` actually exits0 in both
installed SDKs and writes `tmp/r2-pv2-b3-reset-public-{main,alternate}.json`.
It imports no QuantumBridge and covers6 scenarios x4 integer seeds x4 serial
runs (96 observations/environment), preserving packed bytes, per-point counts,
dtype/shape, metadata and errors/phases. Entangled H/CX/reset(q0)/measure(q1)
gives sixteen identical outcomes within each observed run (all00 or all10),
but repeated calls with the SAME integer sampler seed can select different
reset branches. Therefore a seeded sampler is NOT yet evidence of deterministic
reset preparation; do not demand exact seeded branch sequences or substitute
per-shot ensemble sampling for the observed one-state trajectory behavior.
The analytic remaining-qubit ensemble is half/half, distinct from an individual
pure-state trajectory's conditional shots. Both versions reject the MCM case
at job.result with QiskitError 'StatevectorSampler cannot handle mid-circuit
measurements'. These observations change the next implementation/oracle design;
they are not a Native reset implementation or comprehensive dynamic acceptance.

### R2-PV2-B3: Actual Native Default Sampler And Frozen Protection

This supersedes the historical B2 status that the default Sampler was still
a Legacy alias. The Estimator default is STILL Legacy and is not completed.
The frozen selected candidate is
`0145747fbcfd4f2f73497cdaba8c3b51469311de5b81314ed12a206c1d3fd6f9`,
1631files, with archive `tmp/r2-pv2-b3-source.tar.gz` SHA
`0f5554f5f0103d45419fc8f8ab3426901ce975b73e26681b77908349cad5f9c2`.
The complete selected manifest is `tmp/r2-pv2-b3-freeze.json`; this is not
whole-worktree/index/commit equality. Main HEAD remainsb443430ec3eb7eac418c22814e08fe6d940bf099.

Native public Sampler now supports unconditional reset plus supported unitary
operations and terminal measurements. It reuses DynamicExecutionEngine's
single trajectory preparation per bound parameter point and existing
Statevector.sample_memory for terminal shots. No Device/kernel/math or Legacy
ensemble was changed. Sampler seed controls terminal sampling; actual public
reset preparation was not seeded reproducibly by that integer, so no false
exact reset-sequence oracle is imposed. Static MCM is a cached Native
QiskitError at result(), and all pending MCM plans are checked before any
earlier PUB quantum work. General classical control and simulator directives
are explicitly refused, not ignored or called full dynamic support.

The public packed BitArray implementation now resides in packed_bits.py,
separate from the unchanged Legacy container. Added sampled/count/bool
construction, bitcount, endian conversion, basic batch indexing, bit/shot
selection, reshape/transpose, batch/shot/bit concatenation, postselection and
diagonal I/Z expectation helpers. These operate on the same packed shot
memory, with independent9bit[1,192]/16bit/ND/count/boolean references, owned
copy/view leases and first-allocation denial. PubResult, SamplerPubResult
and join_data use the shared resource ledger. This is not a claim that fancy
indexing, all observable object forms, public type/export/error contracts or
every helper method is complete. Python heap/RSS and failed-call unknown work
remain outside the numerical ownership guarantee.

Root/primitives/sampler.StatevectorSampler now point to the real Native V2
class with public default_shots/run/Job/named-register results. Sampler,
LegacySampler, BackendSampler and named Legacy run_pubs retain the old ABI.
Exactly the two approved old Sampler test functions were migrated, with their
original physical inputs and tolerances retained; the old bodies execute in
new explicit Legacy tests, AST-identical except for the class entry name.
The third approved Estimator test and every other B2-baseline test source
remain unchanged. Freeze/audit scripts check those actual deltas.

Initial formal new reset tests had7FAIL/1PASS; helpers6FAIL; default export
tests2FAIL. Their original receipts remain in tmp/r2-pv2-b3-*-red.{json,xml}.
After implementation, actual Main/isolatedAlternate affected gates each give
592PASS, zero fail/skip/xfail/error/deselect and exit0. They include73 actual
public cases, prior539 IDs plus reset/helper/export/Legacy checks. Directed
strict106PASS has no SDK/TF/JAX resolution or imports.

The original GAP1 source remains SHA
`d10721b2056929e71006896299ac122c6256400b110adf6e96d599571f93f242`.
Its full12 cases actually give3PASS/9FAIL in each environment after migration:
four failures are exactly TypeError at StatevectorSampler(shots=16), classified
LEGACY_HARNESS_ABI_MISMATCH, not production regressions. The other five remain
real Native Estimator3/QNode1/UCCSD1 gaps. The public-corrected complete12
(`tmp/test_r2_pv2_b3_default_contracts.py`, distinct new IDs, SHA
`bd6ec53ab5feb43c61b143963b79b49c1ad9a0c5652b96b3acd7561caa67b4c8`)
give7PASS/5FAIL: public Sampler behavior green, real other gaps retained.
Both files execute together:10PASS/14FAIL, exit1, no deselection. No new green
replaces an old node ID or receipt. The peer's actual harness clarification
is recorded in the existing received-prompt journal.

Frozen gate launcher: tmp/r2_pv2_b3_run_frozen.py. Actual terminal results:

| Gate on0145747f | Actual result |
| --- | --- |
| Main broad | 8710PASS/4oldXFAIL, zero skip/fail/error/deselect, exit0 |
| Alternate broad | 8710PASS/4oldXFAIL, zero skip/fail/error/deselect, exit0 |
| Strict protected SDK-free | 1836PASS/37oldoptionalSKIP, no new skip/fail/xfail/error, exit0; no forbidden SDK/TF/JAX resolution/import |
| Original nine native examples | All nine completed, exit0 |
| Main/Alternate original411 TF/MPS protection | 411PASS each, zero skip/fail/xfail/error/deselect, exit0 |
| Supplemental full16bit packed-memory checks | Main/Alternate7PASS each, strict3PASS, all exit0 |

Receipts have r2-pv2-b3-final-* names and before/after manifests equal to
the freeze. The first examples launch lacked PYTHONPATH=.:examples and exited1
on the original sibling-module import before a numeric example completed.
Its receipt is preserved as r2-pv2-b3-examples-launcher-missing-path-main.json.
The corrected environment, with no example/production edits, actually runs all
nine and retains the original numerical outputs including H2 optimization
error1.24e-14 and100-wire MPS. This is a launch-path correction, not a hidden
native failure. Both TF/MPS handles subsequently actually terminated with exit0,
560.60s/567.42s, and their original411IDs remain equal. The final
tmp/r2_pv2_b3_audit.py actually exits0 and writes tmp/r2-pv2-b3-audit.json:
archive/current/before/after match, original8535 broad IDs and exact old4xfails,
original411TF IDs and37strict optional skips are retained, imports originate
in this repository/the actual two public SDK environments, and only the two
approved old tests changed. Original28matrix/workflow hashes are unchanged.
Audit consistency is not full functional acceptance; it also preserves and
classifies the actual remaining red receipts below.

Additional canonical type closure is genuinely RED. Actual public/native
tmp/test_r2_pv2_b3_canonical_types_red.py gives4FAIL/2PASS, exit1 in both SDK
environments, on the same frozen source. Public BitArray/DataBin/PrimitiveResult/
PubResult imports in primitives still refer to the Legacy containers while
the default Sampler returns the new packed/v2 classes. SamplerPubResult and
PrimitiveJob canonical identities do pass. These are real Native export/type
contract failures, not old-harness ABI issues. Existing old tests also depend
on the canonical Legacy to_dict/tolist/isinstance contracts, so no additional
old assertion was silently migrated beyond the two explicitly authorized.
No fake ABC registration, instanceof spoofing or automatic shape-based Legacy
mode was introduced. Complete canonical export/Legacy isolation remains OPEN
for the next production increment; these four reds prevent claiming complete
B3 public-container/default-contract closure.

Separate public-only Estimator observations (20cases/version) were actually
run in2.4.1 and2.6.0 with no Native import, saved to
tmp/r2-pv2-estimator-public-{main,alternate}.json. Pauli labels/mappings/native
analogues require real shape broadcasts, target_precision and0-dimensional
evs/stds. Nonzero precision produces seed-controlled Gaussian perturbations
while reported stds remain zero. Entangled reset yields independently prepared
trajectories across observable/output cells, which can produce individually
valid but mutually inconsistent expectations if mistaken for a single state.
Therefore Estimator must not inherit Sampler's per-parameter-point trajectory
organization without proving its actual public contract. These observations
are preparation evidence, not an Estimator implementation or acceptance.

No B3/fullSampler/Primitives/R2 acceptance. The complete actual results,
including the four new canonical-type failures and the old-contract conflict,
were sent to the authorized ChatGPT conversation with a request for the next
concrete production prompt; peer communication is not independent repository
verification or permission to change a fourth old assertion. FULL/GLOBAL coverage/exclusions/
original28matrix/ALLexamples/legal/fiveorigins/Git3state remain OPEN, as do all
other formal reds and the unknown full-SDK denominator. No Git/auth/TLS/deps/
vendor/cloud/hardware/finance/Studio/Router changes in this increment. Full
independent native Qiskit/PennyLane replacement remains ACTIVE/INCOMPLETE.

### R2-PV2-B4: Canonical Public Containers, Legacy Isolation In Progress

The next complete eight-point prompt was actually read in default Chrome and
recorded in the existing received-prompt journal. It directs the canonical
type fix first, then actual Estimator V2. It explicitly forbids silently
migrating a fourth old assertion; additional conflicts need human approval.
No acceptance of full B3/B4 or the full replacement was given.

Current selected candidate is
`dcddd6e22238361f1a88d001d0d9769afac328035428aefe0b4488d91998cf74`,
1633files. `tmp/r2-pv2-b4-canonical-source.tar.gz` is a snapshot of an
IN_PROGRESS/NOT_ACCEPTED candidate, not a green freeze. Its actual SHA is
`928498f251a15069c282a335768926a205cb849b47348a3ac35be2d661ac07a7`.
The manifest and checks are in tmp/r2-pv2-b4-canonical-audit.json; its script
actually exits0, proving evidence consistency rather than full feature parity.
The old0145747f source/archive/all receipts remain intact.

Moved the unchanged Legacy container implementation to
quantumbridge/primitives/legacy_containers.py. Original class/function ASTs
are identical to the B3 archived containers.py. Legacy Sampler/Estimator
internal imports now explicitly use those classes; Backend facades inherit
the same unchanged Legacy path. New containers.py is a public reexport facade,
not a second container runtime. primitives/root now expose actual Native
BitArray/DataBin/PrimitiveResult/PubResult/SamplerPubResult/PrimitiveJob with
one class identity; explicit LegacyBitArray/LegacyDataBin/LegacyPrimitiveResult/
LegacyPubResult aliases retain old access. No virtual ABC, isinstance proxy,
input-shape mode or Native numerical/kernel changes were introduced.

The same six canonical public probe IDs that previously gave4FAIL/2PASS now
give6PASS in each actual SDK environment. New formal tests prove root/module/
class identity, public constructor signatures and unchanged Legacy dictionary,
list, fixedJobID/result-identity, backend and scalar-physics behavior.
Whole B3 affected selection plus new tests actually runs without deselection:
Main611PASS/4FAIL, Alternate611PASS/4FAIL, exit1 each; same original592 IDs
retained, no skip/xfail/error. Strict SDK-free primitives give112PASS/4FAIL,
exit1, no SDK/TF/JAX resolution/import. Those four failures are precisely the
additional old canonical-container contracts below, not the now-fixed six
public type probes. Every pre-existing B3 test file remains byte-identical;
no assertion was changed to hide these failures.

ADDITIONAL_OWNER_AUTHORIZATION_REQUIRED, exact existing nodes:

- tests/primitives/test_primitives_v2.py::test_primitive_result_container_protocol_and_dict_round_trip
  constructs canonical classes but requires old to_dict/tolist extensions.
- tests/primitives/test_primitives_v2.py::test_sampler_v2_accepts_pub_sequence_shots_and_parameter_batches
  calls explicit Legacy Sampler but expects the canonical Public PrimitiveResult type.
- tests/primitives/test_primitives_v2.py::test_estimator_v2_accepts_observable_batches_parameter_batches_and_precision
  calls explicit Legacy Estimator but expects the canonical Public PrimitiveResult type.
- tests/primitives/test_public_sampler_exports.py::test_public_export_executes_and_legacy_container_export_remains_unchanged
  expects LegacySampler results to have the now-Public canonical result class.

A specific async human question requests permission only to change these four
tests' container/type references to explicit Legacy entries, retaining all
original mathematical, dictionary/list and result assertions; separate new
tests verify Public V2. No human response has yet been applied. These are
recorded old-contract migration conflicts, not a reason to restore wrong
public exports, fake type relationships or pause the whole project. Estimator
production work remains available while this answer is pending.

Both complete24-case diagnostic runs are retained on this current candidate:
original12 still3PASS/9FAIL, corrected12 still7PASS/5FAIL, together10PASS/14FAIL,
exit1 in both environments. Sampler's four old constructor failures retain
their proven harness classification; Estimator3/QNode1/UCCSD1 remain real
functional gaps. The current change is canonical type closure, NOT Estimator
V2. No third authorized alias-test migration or actual new Estimator execution
has happened yet. Do not transfer the old B3 broad8710/TF411 passes to this
edited candidate; its eventual frozen broad/TF protection is still OPEN.
Original R2/full-SDK completion gates and all unrelated formal reds remain
OPEN. No Git/auth/TLS/dependencies/vendor/cloud/hardware/finance/UI changes.
Full independent native Qiskit/PennyLane replacement remains ACTIVE/INCOMPLETE.

### R2-PV2-B4-E1: Actual Native Default Estimator Execution

This supersedes dcddd6e2's historical "Estimator remains Legacy" status.
Current selected-source SHA is
`d687577e21497dae7e4b30778e9b2b45acc9dcded231361e1037b1d4fed01c9d`,
1637files. The directed checkpoint archive tmp/r2-pv2-b4-e1-source.tar.gz has
actual SHA9be09d164d79372cf3cfd8f391a2a92f54d228ca25a694de3e0848faf8fee687.
It is NOT a full-green freeze: four additional old-contract assertions still
await an actual Human response, and final broad/TF/protected SDKfree/examples
gates have not run on this source. No Git state was changed.

Implemented ObservablesArray with actual shaped scalar/ND native Pauli sums,
native wire-addressed Hamiltonian/PauliString and existing SparsePauliOperator
normalization, owned numeric shape-index storage and conservative term payload
leases. Native q0-first SparsePauliOperator is NOT renamed public SparsePauliOp:
its physical wire interpretation is explicitly converted at this boundary.
Public string labels instead use rightmostq0; actual Pauli objects retain
their explicit phase. Existing bindings are reused, not reinterpreted by a
second parameter engine. EstimatorPub normalizes circuit/observables/bindings/
precision, retains shapes and derives standard broadcast axes. Representation
can retain nonfinite coefficients, but whole-Job execution refuses them.

Actual public probes exposed an important string contract: "-Z" is a two-wire
projector label, NOT the one-wire phased Pauli object Pauli("-Z"). Native
representation now preserves IXYZ+-rl01 labels and the public1e-8 simplification
threshold. Both actual installed StatevectorEstimator versions nevertheless
reject projector execution at result() with QiskitError; the Native public
path matches that observed refusal. Independent native factorized-projector
math is tested separately, without claiming the upstream reference executes
it or expanding n projector factors into2**n Pauli terms.

The actual StatevectorEstimator in primitives.v2 reuses native Circuit bind/
lowering, StatevectorDevice, DynamicExecutionEngine and shared observable/math
kernels. Each output cell prepares its actual state/trajectory and evaluates
the requested observable. The independent three-wire RY(theta)RZ(phi) onwire2
has parameter(2,2), observable(3,1,1), evs/stds(3,2,2) and agrees with cos(theta),
sin(theta)cos(phi), sin(theta)sin(phi), atol3e-14/rtol0. Asymmetric multi-wire
weighted observables, multiple PUBs, zero axes and bad broadcasts are covered.

Precision uses the actual public Gaussian perturbation contract with zero
reported stds, target_precision and circuit_metadata. Per-PUB integer seeds
restart while Generator instances advance. Critically, reset trajectory draws
and Gaussian draws interleave PER OUTPUT CELL, not all resets followed by one
noise batch. The first new dual-public test found that real RNG mismatch;
both versioned receipts at46PASS/5FAIL are retained. Two other failures were
the public reference's own projector execution refusal, and one was a new
independent memory-fixture label using XI(q1) while its X-prepared wire wasq0;
that new fixture now explicitly uses IX, without changing production wire
order, mathematical tolerances or any original test.

Whole-Job preflight validates all PUB ownership/UUID, finite values/coefficients,
dimensions, broadcast shape, precision, checked output/state/gate/work costs
and parameter-specific lowered gates before the first quantum evolution.
Outputs reserve as a group; evs/stds and escaped ndarray/memoryview leases use
the existing ledger/scope. Equal/one-below memory including parent/child,
late-invalid/late-overbudget no earlier execution, concurrency, cached original
errors and partial runtime failure are actual tests. A failed second cell
retains first-cell work, releases result storage, and marks unobserved partial
failed-call work unavailable. No physical rollback or Python heap/RSS bound.

The first shared-instance concurrency test revealed a real ledger/RNG lock
inversion. Actual live processes23750/54720 were confirmed blocked, then
deliberately aborted to obtain all-thread faulthandler dumps (actual exits134).
A waiting thread held its ledger lock while waiting for the primitive RNG
lock; the executing thread's GC finalizer needed that waiting ledger lock.
The local primitive lock now precedes any ledger lock during planning AND
execution. This reuses the existing per-instance synchronous execution policy,
not a second scheduler/ledger. Same-instance Jobs and distinct Estimator
instances with forced GC inside state execution now pass in both installed
SDK environments and strict mode. The aborted attempts have actual terminal
tool stderr, NOT completed JUnit/provenance receipts; no successful gate is
claimed from them. A non-absolute sample command resolved to an unrelated
broken Python entry point and failed; it was not evidence of a sampled stack.

Only after actual directed math/resource/public passes did the default
root/primitives/estimator.StatevectorEstimator switch to this Native V2 class.
Estimator, explicit LegacyEstimator and BackendEstimator keep original
ensemble/nesting/return semantics. The third and LAST already-approved old
alias test migrated: original math inputs/tolerance remain, a precision0 run
verifies exact public broadcast math and a seeded0.02 run verifies perturbation
metadata. Its entire original body, including original precision0.02/exact
Legacy math/nesting assertions, is independently executed under LegacyEstimator;
AST equals the original after only the explicit entry-name substitution.
No fourth old assertion was migrated. All other previous test files are
byte-identical, and the total old-function delta sinceB2 is EXACTLY the three
owner-approved aliases. Initial new modules had2 actual collectionERROR before
their missing production symbols existed; that original receipt is retained.

| Actual current-source terminal gate | Result |
| --- | --- |
| Main2.4.1 / isolatedAlternate2.6.0 affected set | 665PASS/4existing-old-contractFAIL each, exit1; zero skip/xfail/error/deselect; prior615 IDs retained |
| Current Estimator directed math + real public comparisons | 53PASS each, exit0; includes25 actual public cases |
| Strict SDK-free complete primitives | 141PASS/4same-old-contractFAIL, exit1; no SDK/TF/JAX resolution/import |
| Original unchanged GAP1 complete12 | 6PASS/6FAIL each:4 proven old Sampler constructor ABI failures + QNode/UCCSD2 |
| Distinct public-corrected complete12 | 10PASS/2FAIL each; all three original Estimator reds now PASS; QNode/UCCSD remain real FAIL |

All original/current diagnostic nodes execute without deselection; corrected
greens do not overwrite old IDs. tmp/r2_pv2_b4_e1_audit.py actually exits0 and
writes tmp/r2-pv2-b4-e1-audit.json, checking current/before/after manifests,
exact allowed test AST changes/Legacy body, prior615IDs, failure classes,
actual origins and current archive. Audit consistency is not acceptance.
Ruff and git diff --check pass. The four extra old canonical container-test
conflicts remain ADDITIONAL_OWNER_AUTHORIZATION_REQUIRED; no Human response
has been applied, and this is not a reason to pause other production work.

Still OPEN: complete SparseObservable native type/return relationships,
ObservablesArray sparse_observables_array/apply_layout and full helper/error/
owner contracts, general dynamics/classical controls/directives, every other
formal SDK gap and the original R2 full gates. The old B3 broad8710/TF411/
SDKfree1836/nine-example evidence is HISTORICAL, not this new source's final
protection. B4 IN_PROGRESS/NOT_ACCEPTED; full independent native replacement
ACTIVE/INCOMPLETE, denominator/completion percentage UNKNOWN. Local only;
no Git/auth/TLS/dependencies/vendor/cloud/hardware/finance/Studio/Router changes.

The complete E1 results were sent to the authorized peer, and its complete
six-point E2 SparseObservable/container/layout/ownership/concurrency production
prompt was actually read in the same default Chrome conversation. The existing
received-prompt journal records it. The peer explicitly has no independent
local source/test audit and does not accept B4; no extra old-test authorization
was granted. Continue E2 production while the separate Human question remains
pending; do not restate an old test-migration request as a whole-project blocker.

### R2-PV2-B4-E2: Real Sparse Observables, Layout Execution And Reentry

2026-10-26 local directed checkpoint: selected SHA256
`a59bab8da0ffa0c9b041ecdad04ad05dd3871b5d99bc46e24973c6cfe4706d1f`,
1642 selected files, NOT committed HEAD `b443430`. Source archive
`tmp/r2-pv2-e2-source.tar.gz` SHA256
`37940ccc861c97c2b968894f676f193f31723fd45108809c014708b9ee8eb179`.
The actual audit is `tmp/r2_pv2_e2_audit.py`, receipt
`tmp/r2-pv2-e2-audit.json`, exit0. This is a reproducible directed checkpoint
with explicit failures, NOT a full-green/final acceptance freeze.

Actual Qiskit2.4.1 and2.6.0 observations confirm SparseObservable's CSR arrays,
BitTerm values, copied immutable Term objects, live mutable raw-field handles,
and owned raw-field slices. ObservablesArray.coerce_observable and slice return
real SparseObservable objects; ordinary scalar [] returns a dictionary. A
slice aliases its parent, copy=True raw exports deeply copy sparse objects,
and copy=False raw object-array replacement affects the parent. The initial
22-observation probe receipts are retained in tmp/r2-pv2-e2-public-*.json;
the formal current differential suite executes128 cases per SDK environment.

New native quantumbridge.operators.SparseObservable is exported through the
root and information namespaces. It owns complex128 coefficients, uint8 bit
terms, uint32 physical indices and uint64 boundaries; the existing shared
ledger reserves the complete four-buffer group before allocation. Construction,
raw/Term round trips, simplification, complex arithmetic, adjoint/transpose/
conjugation, tensor/expand, composition/qargs, Pauli evolution, layout, Pauli
bases and explicit projector expansion reuse existing native algebra/matrix
helpers. The old native SparsePauliOperator's q0-first dense labels are
explicitly converted, NOT renamed to pretend it is public SparsePauliOp.

Composition now multiplies sparse single-qubit Pauli/projector factors directly.
Disjoint and idempotent projectors stay sparse; a40-factor projector on a
million-qubit declared space composes with itself in one term, and a mapped
orthogonal projector produces zero terms. The old expansion path really failed
its memory preflight at246290604622064 requested bytes; that7PASS/1FAIL receipt
is retained. The100 possible single-factor pairs, both multiplication orders,
multiqubit complex sums and noncontiguous qargs match the actual public SDK
and independent explicit matrices. Genuine exponential expansions remain
bounded/refused before their numeric allocation, not mislabeled supported.

ObservablesArray now stores actual owned/borrowed sparse objects, preserving
slice/reshape/raw-export aliasing and deep-copy behavior. Its pointer slots
and each sparse object's numeric storage have leases. A strided external
object-array view originally admitted80bytes while retaining an800byte root;
the actual9PASS/1FAIL receipt is retained, and the entire retained root is now
admitted. Streamed from_terms stops at its first denied record rather than
materializing an unbounded iterator. Term rejects lossy floating indices and
invalid bit terms; an empty Pauli basis keeps its declared width. Escaped Term
memoryviews and raw object arrays retain their real buffers until deletion.
These are numeric-storage accounting proofs, NOT Python heap/RSS guarantees.

Actual native transpile runs reversed and noncontiguous layouts on real
circuits, then uses the compiler's actual logical_final_layout report to remap
the observable. Original and compiled Estimator results match explicit basis
embedding and independent complex matrix math at atol3e-14/rtol0. Existing
native Layout and explicit lists are supported here; the absent full public
TranspileLayout type is NOT claimed. The first layout fixture used an empty
Target instruction set and correctly failed; the new test now declares its
actual x/h/ry/rz/cx basis, without changing any previous test or production
Target policy.

Typed sparse Estimator inputs preserve weighted(3,1,1) observable and(2,2)
parameter broadcasting to(3,2,2), public Gaussian precision and reset behavior.
Mutated raw entries, nonfinite/imaginary coefficients and width errors in a
later PUB refuse before any earlier evolution. A64-wire projector PUB with
zero parameter points returns an empty result without a state allocation or
eager dense-label validation. Public projector execution refusal for nonempty
PUBs remains distinct from the independently tested native projector math.

A genuine new concurrency red demonstrated two different primitive instances
holding their own locks while recursively waiting for each other in separate
threads. The subprocess emitted both blocked stacks and was killed/reaped by
its bounded parent test; the original12PASS/2FAIL receipt is retained (the
other failure was the new fixture's wrong classical register name). A shared
reentrant local admission lock now precedes instance and ledger locks. Actual
same/cross-instance nesting, nested cached exceptions, recovery, mixed Sampler/
Estimator nesting and GC pass. This deliberately serializes synchronous local
primitive admissions; it is NOT parallel performance parity, a new scheduler,
or a proof that arbitrary external lock/reentry cycles cannot deadlock.

| Actual current-source terminal gate | Result |
| --- | --- |
| Main2.4.1 / isolatedAlternate2.6.0 complete affected selection | 817PASS/4same-old-contractFAIL each, exit1; all669 E1 IDs retained, total821 IDs equal across environments |
| New actual public differential subset within that selection | 128PASS each, no skip/xfail/deselection |
| Strict SDK-free complete primitives plus new sparse math | 165PASS/4same-old-contractFAIL, exit1; no SDK/TF/JAX resolution/import |
| Original unchanged GAP1 complete12 | 6PASS/6FAIL each, including4 old shots= constructor diagnostic failures and actual QNode/UCCSD gaps |
| Distinct public-corrected complete12 | 10PASS/2FAIL each; QNode broadcasting and UCCSD remain real failures |

All source-before/source-after manifests match the audited current candidate;
real executable/import origins, node IDs, failures and terminal exit codes are
recorded. Every test file present in E1 remains byte-identical; exactly the
three already-authorized old alias migrations remain the total delta sinceB2.
The four additional old canonical-container migration assertions are untouched,
still pending Human authorization, not silently xfailed/deselected. No repeat
authorization question was sent. Ruff and git diff --check actually pass.

Still OPEN: full SparseObservable helper/error/repr/canonical-order and mutable
raw intermediate contracts; full public TranspileLayout; cross-ledger mutable
external object borrowing; general dynamic/control/directive primitives and
asynchronous/remote Provider/Backend/Job; full SDK function-family coverage.
No new-source broad/411TF/protectedSDKfree/nine-example final gate or original
R2 FULL/GLOBAL/68exclusion/28matrix/legal/Git acceptance is claimed. Prior broad
results remain historical. B4 IN_PROGRESS/NOT_ACCEPTED; full independent native
replacement ACTIVE/INCOMPLETE, denominator/completion percentage UNKNOWN.
All work stayed local: no stage/commit/push/fetch/auth/TLS/dependency/vendor/
cloud/hardware/finance/Studio/Router/tag/release changes.

The E2 actual report was sent to the authorized peer; the complete response
766764c4-d499-406a-8815-8108d77a1e31 was actually read in the existing default
Chrome tab. It grants only the limited sparse-subdomain review label, not B4
acceptance or any extra old-test permission. Its next eight-section R2-DYN1
dynamic/classical-control prompt is in the existing received-prompt journal.

### R2-DYN1 Initial Inspection And Actual Remaining Reds

No new dynamic production edit is claimed yet; the selected production source
remains a59bab8d/1642files. Inspection confirms the existing DynamicExecutionEngine
already interprets native per-shot classical state, if/else, switch, bounded
for/while, break/continue, reset/measurement and mapped nested bodies. It must
be extended and reused, not described as wholly absent or replaced.

Fresh unchanged existing tests on that source: strict native/classical/
compose/QPY dynamic baseline89PASS/36existingSKIP; the36 are existing optional
public-Qiskit checks, unavailable in strict SDK-free. Main public dynamics
gives6PASS; isolatedAlternate2PASS/4existingSKIP because qiskit_aer is absent.
No dependency installation or new skip/deselection was introduced. The absent
Alternate Aer execution comparisons remain unverified, not four passes.
Receipts: tmp/r2-dyn1-existing-native-baseline-strict.{json,xml} and
tmp/r2-dyn1-existing-public-baseline-{main,alternate}.{json,xml}.

The new unchanged tmp/test_r2_dyn1_public_and_runtime_red.py (SHA256
774acdaa12f69e29ae1826c1623d5a351f5050fb7c1387e0fb6bc76638174641) actually executes
three full diagnostics in both installed Qiskit versions:0PASS/3FAIL each,
exit1, no skip/xfail/error/deselection. Actual public Circuit if_test/for_loop
context construction succeeds first; the corresponding native public methods
fail because if_test requires a body and for_loop(None body) composes None.
The public StatevectorSampler correctly refuses the valid measured dynamic
Circuit, separately from its construction validity; this is not a reason to
claim that reference sampler supports general dynamic execution.

The third actual red demonstrates a shared-resource gap: an active ledger with
max_derivative_work=2 does not meter dynamic interpreter control steps; an
infinite empty-body while instead reaches its separate max_loop_iterations=5
ClassicalExecutionError. Thus existing loop termination is bounded, but unified
runtime-work admission is not fulfilled. The same diagnostic is0PASS/1FAIL in
strict SDK-free. Receipts: tmp/r2-dyn1-initial-red-{main,alternate}.{json,xml}
and tmp/r2-dyn1-runtime-work-red-strict.{json,xml}. These are retained real
remaining gaps, not E2 regressions, not acceptance and not a project blocker.
Next production must connect public builder scopes and the existing unified
work account to the existing interpreter while preserving all legacy scopes,
bindings, shots/trajectories and QPY/Compiler contracts.

### R2-DYN1: Executable Public Builders And Shared Runtime Control Work

2026-10-26 directed development snapshot:
`85acd94c89d25f05670c5b9e5cb2079041a29ff114ac28d9056b79c3f78bcfa5`,
1645 selected files, NOT committed HEAD b443430. Source archive
tmp/r2-dyn1-source.tar.gz SHA256
`1cb8cf9225b21f6efeac3a619b2139604e1e5fbad90ed119dce4fc5bc66f5648`.
tmp/r2_dyn1_audit.py actually exits0 and writes tmp/r2-dyn1-audit.json.
This proves evidence consistency for this increment, not DYN1/B4 acceptance.

The prior turn was real production/evidence progress, not a verified wait or
an impasse. Fresh worktree inspection retained main HEAD and all dirty user/
previous work. No active execution process from the previous increment remained.
The original three DYN1 diagnostics were preserved byte-identical (SHA774acdaa)
and actually ran red in both SDK versions before implementation. All three
now execute PASS inside both current full directed selections.

New core/control_builders.py supplies lexical if/else, for/while and switch
contexts; public QuantumCircuit also accepts explicit mapped control bodies
and contextual break/continue. They emit existing ControlBlock values into
the authoritative native operation store, not a parallel gate list/interpreter.
Legacy fluent Circuit methods and their original return/execution semantics
are unchanged. Parameter UUIDs and loop-local substitution use existing native
parameter and binding code. An unused automatically generated loop parameter
is dropped; explicitly supplied parameters keep their identity.

Context exit restores the outer operation/measurement/execution-metadata
stores and emits one block only after successful construction. Python errors
discard the block without altering the outer store. Else must immediately
follow its matching if. A retained gate InstructionSet points at the actual
captured body, not the later outer control-node index. Foreign bits/registers,
invalid loop jumps, omitted explicit qarg/carg lists, duplicate switch cases
and register mutation inside builders refuse without partial parent edits.
Existing gate-graph/depth/work admission bounds body construction.

Nested builder identifier validation initially revealed a real environment
bug: a captured outer Var was validated without its enclosing lexical map.
The existing execution_environment now receives the active builder's captured
environment. Tests verify captured outer identity, nested local declaration/
store/condition, local variables absent from outer lookup and final runtime
store, and proper rejection after leaving scope. No second identifier system.

Real H->measure->feedforward and else execution pass on Statevector,
DensityMatrix, MatrixProductState and Stabilizer devices; both exact ensembles
and actual per-shot correlated outputs are tested. Native reset/while feedback,
switch/default, nested conditional break/continue, register equality, explicit
noncontiguous body mapping, bound loop rotations and captured parameters run
through the existing DynamicExecutionEngine. A bound source travels through
native IR JSON restore, noncontiguous q/c remap, optimization-level2 compilation
and actual analytic classical-branch probabilities, with independently derived
cos/sin results. Numerical near-zero compiler branches are included in the
full output-vector comparison at the original1e-13 absolute tolerance, not
silently dropped or described as exact zero.

Dynamic interpreter classical dispatch and loop-condition tests now consume
one existing shared-ledger derivative_work unit before that control step.
Quantum tapes and measurement shots are not incremented by this control meter.
The existing max_loop_iterations/max_instruction_executions limits remain.
An empty infinite while with a shared cap2 now stops at the unified work limit,
retaining2 units consumed, rather than reaching only the separate loop bound5.
A two-iteration loop consumes4 control units including its final termination
check: cap4 completes one shot; cap3 through a parent/child account retains3
actual units and zero completed shots on failure. No new RNG or ledger is
created. Ordinary reset-only primitive trajectories do not become control-flow
charges; all prior reset/precision/concurrency/Legacy tests still execute.
Python classical-store/branch headers and allocator RSS are explicitly marked
unavailable. This is control-step accounting, NOT a complete quantum-work or
whole dynamic multi-PUB maximum-work reservation proof.

Actual public construction/error comparisons run11 cases under each installed
Qiskit version. Valid public dynamic Circuit construction is separate from
public StatevectorSampler/Estimator execution: those reference primitives
reject the measured/controlled circuit with QiskitError, and the native public
reference entries preserve that refusal. Actual dynamic execution here uses
the native device/engine path, not an invented claim that those references
support every dynamic program.

| Current-source terminal selection | Actual result |
| --- | --- |
| Main Qiskit2.4.1 and isolatedAlternate2.6.0 directed affected gates | 1130PASS/4same-pending-old-contractFAIL each, exit1; all821 E2 IDs retained; total1134 IDs identical across versions |
| New builder/device/IR/resource native cases within affected | 15PASS each |
| New actual public builder/error comparisons within affected | 11PASS each |
| Original unchanged three DYN1 construction/runtime diagnostics | 3PASS each, not removed or weakened |
| Strict SDK-free primitives/sparse/control/Compiler/IR/QASM/QPY selection | 465PASS/4same-old-contractFAIL, exit1; all169 E2 strict IDs retained; no SDK/TF/JAX resolution/import |
| Original complete12 GAP1 / corrected complete12 | 6PASS/6FAIL and10PASS/2FAIL respectively in BOTH environments; original QNode/UCCSD actual reds retained |
| New complete public control-object/transport diagnostic | 0PASS/4FAIL each, exit1; same actual IDs in both versions |

All directed gates have zero skip/xfail/error/deselection. Separate old dynamic
optional-Aer comparison baselines remain Main6PASS/Alternate2PASS+4oldSKIP as
recorded earlier; those skipped comparisons are not counted as new passes.
Every E2 test source remains byte-identical, including the four Human-pending
canonical-container assertions. Exactly the three already-approved old alias
migrations remain; no new old-test authorization was inferred or requested.

The new four full-contract failures are explicit and unresolved:
1. QuantumCircuit.data for a native ControlBlock has no real public IfElseOp/
   ControlFlowOp owner, minimal public block qarg/carg or full live ABI yet.
2. Native dynamic standard QPY13 output is still refused.
3. Actual public QPY13 conditional input is still refused by the native reader.
4. Direct public-reference Circuit OpenQASM export still refuses Instruction
   owner records. An explicitly lowered executable path DOES roundtrip through
   standard QASM3 after explicit allow_metadata_loss=True for the nonsemantic
   Circuit name, preserving the warning. This is not direct-entry parity.

The initial QASM fixture did not lower public references, then omitted the
existing explicit metadata-loss opt-in; both actual failing receipts remain.
Only the new fixture was qualified to test the already-supported lowered
semantic path. No old serialization assertion, tolerance or format policy
was changed to hide the remaining direct-entry/QPY failures.

Focused Ruff checks for new code/tests/internal audit and git diff --check
pass. An initial whole-file Ruff check also reports pre-existing compact-style
E701/E702 and unused-import issues in public_circuit.py; no global Ruff-green
claim or unrelated formatting rewrite follows from the focused check.

DYN1 IN_PROGRESS/NOT_ACCEPTED. Still required: actual typed public control
operations and live owner/block ABI, full standard control transport, whole
dynamic Job static/max-work/classical-memory admission, typed packed dynamic
BackendSamplerV2 and full devices/control/error contracts. All original full
SDK families and R2 FULL/GLOBAL/exclusions/28matrix/legal/origins/Git gates
remain OPEN; no new-source broad/411TF/protectedSDKfree/nine-example final gate
has run. Full independent native replacement ACTIVE/INCOMPLETE, denominator
UNKNOWN. Local only; no Git/auth/TLS/dependencies/vendor/cloud/hardware/finance/
Studio/Router/tag/release changes. The complete current-source report will be
sent to the authorized peer for the next production instructions.

That report has now been sent, and the complete reply27f0b67a-7808-44f1-b565-
38a6e83560e1 was actually read in the same default Chrome tab. Its eight-point
DYN1-B prompt prioritizes live public ControlFlowOp/owner ABI, Compiler/IR/four
devices, standard QPY, direct QASM and whole-Job admission in that order. It
does not accept DYN1, grant old-test permission or independently audit the local
source. The complete requirements are recorded in the existing received-prompt
journal. Next production continues the same full goal, not a reduced target.

### R2-DYN1-B Live Public Control Owners And Actual Execution

2026-10-26: continued the same full independent replacement goal, not a
production-only subset. Branch main and HEADb443430ec3eb7eac418c22814e08fe6d940bf099
remain unchanged. The pre-existing dirty worktree is preserved. This increment
is local only: no Git/index/commit/push/fetch, authentication/TLS/dependency,
vendor/cloud/hardware/finance-history/Studio/Router/tag/release changes.

Current selected source: e45d079fbdb229667256de9fa49a25b2ecacc2ca30209927c6bafcc1b4638e4e,
1648files. Archive tmp/r2-dyn1b-source.tar.gz SHA256
acf375a751017403d973befe94873af095cb3293bf8066cd5f53a29a900afb61.
Actual audit tmp/r2_dyn1b_audit.py exits0 and emits tmp/r2-dyn1b-audit.json.
All1134 DYN1 affected IDs, all469 strict IDs, every prior test source, original
diagnostic source, original28 matrix script and workflow hash are preserved.
The baseline85acd94c archive and receipts remain historical, not overwritten.

Implemented within existing Instruction/Circuit/Operation/ControlBlock paths:
- Real ControlFlowOp, IfElseOp, ForLoopOp, WhileLoopOp and SwitchCaseOp classes;
  BreakLoopOp/ContinueLoopOp are Instructions, not fake ControlFlowOps and do
  not invent a blocks property. Public exports use these real native types.
- Public blocks and live params lists remain canonical executable owners.
  Existing full-width ControlBlocks are derived execution materializations,
  invalidated against actual block/parameter/resource signatures; there is no
  new interpreter or second canonical Circuit store. Actual block/condition/
  indexset replacement changes native results, not just introspection.
- Builders infer minimal q/c operands. If/for preserve measured first-use
  order; if/else unify both sides while retaining the actual true-body object
  and escaped handles. Loop jumps are finalized to the enclosing loop's actual
  resources, including resources first encountered after a nested jump.
- Native/public append and direct compose, parameter UUIDs and lexical loop
  binding, independent copied blocks, explicit q/c maps, captured Var identity
  remapping, managed construction bounds and cyclic owner refusal are wired
  into existing storage/validation. Work admission occurs before IR signature
  encoding and failed append leaves the parent unchanged with zero shots.
- Existing Compiler/IR/four-device dynamic physics tests remain actual passes.
  Lowering resolves executable snapshots without detaching exposed source
  owners. Earlier public reference primitive dynamic refusals are retained.

Actual SDK black-box probes under2.4.1 and2.6.0 record7 owner families and13
constructor/mutation observations in tmp/r2-dyn1b-public-owners-*.json. Official
IBM API descriptions and those installed versions informed implementation;
latest documentation's additional Var-loop form is not claimed by this work.
No upstream source was copied. The first native owner collection failed for a
missing module; the intermediate1/4 and3/2 owner receipts remain. New differential
fixtures initially revealed both real native gaps and incorrect fixture
assumptions. Those original failing receipts are kept, not retroactively green.

Fixture qualifications apply ONLY to these newly written tests:
1. Qiskit standard singleton private class names are not the control-owner
   ABI. Nested non-control instructions compare their operation names/maps;
   real control-owner named types are compared exactly.
2. Switch resource-union ordering is not treated as a stable public contract.
   Its2q/1c widths, resource set and EVERY case's physical parent-wire action
   are compared. If/for/while/jump operand ordering remains exact.
3. Actual SwitchCaseOp.params assignment permits a width-inconsistent body,
   unlike conditional/loop setters. Native assignment preserves that observed
   behavior; executable admission still rejects inconsistent widths before
   the first shot. No old assertion, numeric tolerance, skip or xfail changed.

| Current-source terminal selection | Actual result |
| --- | --- |
| Main Qiskit2.4.1 / isolatedAlternate2.6.0 full retained directed selections | 1157PASS/4same-pending-old-contractFAIL each, exit1;1161 identical IDs |
| New permanent native public owner tests | 11PASS each, inside the directed selection |
| New actual public owner/resource/error comparisons | 16PASS each, inside the directed selection |
| Earlier builder/device/Compiler/IR cases and original3 DYN1 reds | retained and passing, not removed |
| Strict SDK-free retained selection | 476PASS/4sameFAIL, exit1;480 IDs, no SDK/TF/JAX resolution/import |
| Focused strict owners/builders/additional admission diagnostics | 30PASS, exit0; overlapping counts, not additional API coverage |
| Original unchanged public owner/QPY-out/QPY-in/direct-QASM4 diagnostics | 1PASS/3FAIL each, exit1; owner/width/map case now PASS |
| Original complete12 GAP1 / corrected complete12 | 6PASS/6FAIL and10PASS/2FAIL each; combined16/8, all IDs retained |

All named final directed gates have zero skip/xfail/error/deselection and exact
before/after/current selected-source equality. Four old canonical-container
assertions still fail unchanged and await Human permission; the prior three
approved alias migrations have not expanded. The final affected runs are
tmp/r2-dyn1b-final-affected-{main,alternate,strict}.{json,xml}; oracles and remaining
diagnostics use the same final prefix. Focused new-code Ruff and git diff
--check pass; no unrelated compact-style whole-repository lint claim follows.

R2-DYN1-B IN_PROGRESS/NOT_ACCEPTED. Standard dynamic QPY13 writer/reader and
direct public-reference QASM still have the same actual3 unresolved diagnostic
failures. Full helper/error/raw-mutation ABI, whole dynamic multi-PUB maximum
work/while bounds/classical storage/packed backend results remain unclosed.
No new-source broad/411TF/protectedSDKfree/nine-example/full original R2 final
acceptance run has occurred. Original full Circuit/library/info/compiler/Aer/
algorithms/providers/ecosystems and PennyLane/QNode/interfaces/templates/qchem
requirements remain OPEN, including actual operation broadcast and UCCSD reds.
Full independent replacement ACTIVE/INCOMPLETE, denominator UNKNOWN.

The owner-increment report was sent to the same authorized ChatGPT conversation.
The complete reply09b7069e-0fae-417f-972a-3369a07f0cb1 was actually read in the
existing default Chrome tab. It provides the eight-point R2-DYN1-C standard-QPY
production prompt, recorded in the existing received-prompt journal, and
explicitly does not independently audit or accept full parity.

R2-DYN1-C C1 preparation has started without changing the e45d079f production
source. The internal oracle-only script tmp/r2_dyn1c_qpy_public_fixtures.py
actually generated6 standard QPY13 fixtures in EACH SDK environment: if/else,
parameterized for, measured while/reset, register switch/default, nested loop
jumps and standalone/captured/local Vars. Binary samples, SHA256, public source
and restored object trees, root binary-header observations and exact initial
native failures are in tmp/r2-dyn1c-public-{main,alternate}/observations.json.
This is not a new native parser or QPY implementation, and the observation
tree is public object reconstruction plus root-header inspection, not a claim
of complete binary control-record parsing.

Actual both-SDK native-reader failures are retained: conditional if at byte314,
while at279, unknown ForLoopOp at190, SwitchCaseOp at197, jump's enclosing for
at198, standalone Vars at57. All6 public->public executable structures match
after excluding only Circuit-name fields, but every RAW tree differs: actual
public v13 restores nested builder Circuit names as unnamed. Both raw trees
and EVERY difference are saved. The initial exact-name assertions genuinely
failed before this public behavior was identified; no native success, raw-tree
equality or complete format fidelity is claimed. Parameter/condition/case/
operation names, maps, captures and other fields are not filtered. The next
production step is C2 standard typed records and bounded recursive scopes,
not another inventory. Existing native QPY tests and Unauthorized old
Unsupported expectations are untouched; full goal remains ACTIVE/INCOMPLETE.
