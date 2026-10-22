# Stage 12-B P4-U3C Execution Prompt

Native QuantumCircuit Composition, Typed Classical Scope And Remaining Circuit ABI

Status: ACTUALLY RECEIVED TASK / NOT IMPLEMENTATION OR ACCEPTANCE.
This normalized English transcription preserves all17 sections of the actual
owner-authorized continuation. It is not a claim that the APIs below are
missing, implemented, or validated. Observe actual public behavior first.

## Reading Evidence And Checkpoint Review

Conversation: "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. The actual local implementation commit
af66875b13593706282dac1ace0481911a2bbb27 and complete R2 results were sent.
Chrome AX656-1158 covered the review/sections0-6; subsequent AX1234-1759
covered the rest of section6 and sections7-16. Completed-answer controls and
AX1761 confirmed answer completion. The intermediate interrupted stream was
not treated as complete. No independent collaborator source/remote-CI review
or source-message identifier is fabricated.

The report-based review accepts only the supported U3B checkpoint: all29 R2
children, driver and audit0; SDK-free/main/alternate FULL4544/5900/5898 passed;
GLOBAL91.28961589017088%, exclusions68; actual committed runtime equals the
tested runtime. R1 was correctly invalidated for the actual control defect
and not reused. No new confirmed unresolved blocker was identified from the
report. The collaborator did not inspect unpushed source or verify remote CI.
Original28-section matrix NOT_RUN; new-SHA CI NOT_VERIFIED; U3/P4/full SDK
ACTIVE / INCOMPLETE. The next priority is compose wrap/copy/var_remap and
classical capture, not additional standard gate names or U4.

## 0. Objective And Boundaries

Start from af66875b13593706282dac1ace0481911a2bbb27, allowing a normal
documentation-only follow-up with identical runtime. GLOBAL baseline
91.28961589017088%, exclusions68. Continue P4-U3, not U4/U5 or Studio.
Implement genuine public Circuit capabilities affecting composition, binding,
execution and typed classical scope: full quantum/classical wire mapping;
front/inplace/wrap/copy; var_remap; inline_captures; Var/Stretch scope and
lifetimes; integration with ControlBlock, Compiler, Devices, QNode and
IR/QASM/QPY. Continue substantive Instruction/Circuit boundaries, not only
return types. The ultimate independent native Qiskit/PennyLane full
functional parity/full replacement goal stays ACTIVE / INCOMPLETE.
No upstream wrapper execution, implementation source or test copying.

## 1. Observe Public Behavior Before Genuine Reds

Run actual public APIs independently in Qiskit2.4.1 and2.6.0. At minimum:

| Call | Actual observation required |
| --- | --- |
| compose(other), omitted inplace | Return and original mutation. |
| compose(other,inplace=True) | None return and actual owner mutation. |
| compose(other,inplace=False) | New Circuit and unchanged owner. |
| compose(other,front=True) | Actual operation ordering. |
| compose(other,wrap=True) | Gate/Instruction type and definition hierarchy. |
| compose(other,copy=True) | Mutation isolation. |
| compose(other,copy=False) | Actual sharing/ownership reuse or transfer. |
| compose(other,qubits=...) | Quantum wire mapping. |
| compose(other,clbits=...) | Classical wire mapping. |
| compose(other,var_remap=...) | Typed identifier rewriting. |
| compose(other,inline_captures=True) | Capture association with target variables. |
| compose plus ControlBlock | Dynamic execution. |
| compose plus global phase | Full complex matrix. |
| compose plus ParameterVector | Parameter identity. |

The received task references IBM's public Qiskit2.4 Circuit documentation
for inline composition, wrapping, variable remapping and capture merging.
Consult actual public documentation/API, not upstream implementation source.
These contracts are more than concatenating operations. First run native
tests and audit existing implementation; create reds only for true observed
differences, never invent failures for already-correct APIs.

## 2. wrap=True Must Retain Hierarchy

Public scenario:

```python
inner = QuantumCircuit(1)
inner.h(0)
inner.rz(0.37, 0)
outer = QuantumCircuit(2)
outer.compose(inner, qubits=[1], wrap=True, inplace=True)
```

Check one outer wrapped operation, ordered H/RZ definition, actual public
wrapper type, independent embedded Operator matrix, real one-layer
decompose(reps=1) and progressive reps=2, parameter binding, copy definition
retention and supported IR/QPY wrapped-object restoration.
The received task also proposes adding inner.measure(0,0) to determine the
public nonunitary wrapper type and classical mapping. That illustrative
one-qubit/no-clbit Circuit needs valid classical storage before measurement;
observe the public argument error separately and construct a legal measured
Circuit for the intended semantic test. Never force nonunitary Instruction
into Gate or mistake invalid setup for an implementation gap.

## 3. front And Wire Mapping

Public setup:

```python
left = QuantumCircuit(3)
left.cx(0, 2)
right = QuantumCircuit(2)
right.rx(0.31, 0)
right.cx(0, 1)
out = left.compose(right, qubits=[2, 0], front=True, inplace=False)
```

Verify actual front order, noncontiguous mapping, control/target orientation,
global phase, original isolation, exact full complex Operator and equivalent
decomposition. The oracle must be independently constructed matrices, not
two Circuits using the same compose code. Also cover crossed/noncontiguous
classical bit mapping.

## 4. copy Lifetimes

Compose a parameterized source with copy=True, mutate source parameters and
verify the output retains its original definition/math. Independently observe
copy=False. Distinguish public permitted ownership reuse, unintended
cross-Circuit contamination, parameter owner, copied Gate, mutable
ParameterList, definition caches, hash identity and validity after source
lifetime ends. Public copy=False does not mean unrestricted sharing of all
Python references. Resolve native safe-ownership/public observable differences
through controlled transfer or demonstrably safe sharing, never bypassing
existing atomic update mechanisms.

## 5. Typed Classical var_remap

Reuse Stage11J ClassicalType/Var/Expr/ControlBlock. Exercise a real Bool a,
Uint[4] b, measurement-derived a, incremented b and an X branch on a, using
legal public/native APIs. Map those identifiers into a target Circuit.
Cover string name to new name; variable object to variable object; compatible
types; incompatible types; same names in separate scopes; illegal Var/Stretch
mapping; undeclared variables; target conflicts; expression references inside
ControlBlock; nested blocks; independent parameter/variable namespaces.
Rewrite all actual expression references, not just declaration names while
leaving conditions attached to stale Var objects.

## 6. inline_captures

Target owns Uint[8] counter and Bool enabled. Source captures both and
conditionally increments counter. Test:

```python
target.compose(source, inline_captures=True, inplace=True)
```

Associate source captures with existing target variables and correct scope,
not mistaken fresh locals. Cover type consistency, nested capture, missing
capture rejection, input/capture conflicts, var_remap before capture binding
and no replacement of parameter identities by classical identifiers.
Execute on native Statevector, Density and supported dynamic executor paths.
Use independent classical state trajectories, not only final probabilities.

## 7. front=True And Dynamic Structures

Compose circuits containing measure/reset, if/else, for, while, switch and
legally scoped break/continue. Verify front compose -> ControlBlock remap ->
runtime interpretation -> measurement/classical state -> observable result.
Do not statically execute dynamic conditions or delete actual measurements.
Observe public builder-context front=True restrictions and reject matching
unsupported combinations rather than silently reorder operations.

## 8. Phase, Parameters And Derivatives

Use CircuitA with phase p/3 and RZ(p), CircuitB with phase sin(q)/5 and RY(q).
Exercise normal/front compose, wrap/copy, noncontiguous wires, binding,
inverse and coherent controlled conversion. Independently compute the full
complex matrix exp(i*(phaseA+phaseB)) times the ordered operation matrices;
adjust multiplication order to actual compose semantics.
Protect P2 UUID/vector, P3 symbolic AST, Gate formal maps, live ParameterList,
parameter-shift/adjoint, Hessian, streamed HVP, Torch/Autograd/JAX/TF and
100-wire non-dense MPS. Phase cannot be discarded as irrelevant, especially
when converted to coherent control later.

## 9. Resource Safety Before Composition

Protect shared QPY cross-record/circuit max_numeric_elements, definition
depth, aggregate work, expression nodes, ControlBlock depth, repeat work,
foreign-type admission, managed copying and dense allocation preflight.
New costs include source operation count, wrap definition nesting, variable
remap count, capture count, nested block remap work, copy amplification and
front whole-list reorder work. Budget before large copying/expansion/matrix
materialization. Incrementally metered traversal must leave inplace targets
unmodified on failure, not partially remapped.

## 10. IR/QASM/QPY And Compiler Integration

Reuse existing engines, not second compilers/codecs. Execute typed dynamic
composition(var_remap/inline_captures) -> native IR roundtrip -> native
execution; also parameterized unitary compose(wrap=True) -> QPYv13 -> bind ->
native Operator/QNode. Distinguish public-to-native, native-to-public and
native-to-native QPY. Unsupported Var/Stretch/capture format fields require
explicit Unsupported and exact format ranges. Do not pre-execute dynamic
circuits, drop variables or emit unconditional gates to fake interoperability.
QASM2/3 must likewise losslessly represent or explicitly reject; an explicitly
chosen mathematically justified lowering may be supported, not mislabeled
lossless transport.

## 11. Remaining Public ABI Audit

Actually observe copy_empty_like(), copy(name=...), from_instructions(),
to_instruction(), to_gate(), append bit mapping, compose(singleInstruction),
zero-width Instruction/Circuit, empty Circuit name, invalid arbitrary name,
compose after mutable parameter updates and positional/keyword-only rules.
Implement genuinely suitable U3C contracts; explicitly preserve larger
remaining U3 work, never hide it. Observe public copy_empty_like(vars_mode=...)
and capture-only subcircuits as critical typed-scope cases.

## 12. Test Design

Prefer extending existing organization or these modules:

```text
tests/circuit/test_native_compose_contracts.py
tests/circuit/test_native_compose_wrap_copy.py
tests/circuit/test_native_compose_classical_remap.py
tests/circuit/test_native_compose_inline_captures.py
tests/circuit/test_native_compose_dynamic.py
tests/circuit/test_native_compose_resources.py
tests/serialization/test_native_composed_circuit_roundtrip.py
tests/compat/test_qiskit_compose_public_differential.py
```

Minimum independent scenario targets:12 front/inplace/wrap;10 copy/lifetime;
15 typed Var/Stretch remap;12 capture/dynamic execution;10 phase/parameter;
10 IR/QPY/Compiler;15 resource/error counterexamples;30 dual-version public
differential. These are scenario coverage targets, not inflated parameter
grids or duplicated tests. Observe reds before production changes. Separate
broken claimed-supported behavior from explicit Unsupported; Unsupported is
not successful compatibility.

## 13. Preserve Existing Regressions

Protect P2/P3 parameters/symbolic AD; P4/P4-S Gate definitions/custom QPY;
P4-T Annotation; P4-U1 annotation QPY; P4-U2 ParameterList; P4-U3 standard
objects; U3B real Instruction references; coherent phase; CSX/csxdg QPY;
Aer composite-noise boundaries; H2;100-wire MPS; dynamic ControlBlock runtime;
SDK-free examples and four-framework AD. Never substitute public SDK
execution for native results.

## 14. Development And Final Gates

Start with affected focused red/green tests, then frozen final gates:

```bash
python3 -m compileall -q quantumbridge
pytest -q -rs tests/circuit
pytest -q -rs tests/serialization
pytest -q -rs tests/compiler
pytest -q -rs tests/qml
pytest -q -rs tests/devices
pytest -q -rs
pytest --cov=quantumbridge
bash scripts/run_local_matrix.sh
git diff --check
```

Use project/resource conventions, no competing FULL/coverage processes in
the same controlled environment. Require SDK-free FULL; Qiskit2.4.1/PL0.44.1
FULL; Qiskit2.6.0/PL0.42.3 FULL; independent JAX/TF FOCUS; Torch/Autograd
FOCUS; both public differentials; GLOBAL coverage; every new SDK-free numeric
example; actual import origins; controlled legal; no-vendor/no-token and
actual frozen/stage/commit runtime equality.
Original28-section matrix is separate and previously NOT_RUN. It may be run
with bounded resources this batch, but report completion only from actual
exit receipts; even passing it does not establish full P4 completion. Never
reuse invalidated snapshots or old coverage. Baseline91.28961589017088%;
exclusions68 cannot increase.

## 15. Scoped Commit, Protection And Continuation

Only normal local commits of explicitly owned paths. No git add dot,
reset/rebase/amend/force, Studio/Router edits or invented Router provenance,
auth/TLS changes, token access/transmission, cloud/hardware calls, vendored
third-party sources, unauthorized push, PR/tag/release or cached-origin
claims about live remote CI. If all supported-scope gates pass, suggested:

```text
feat: implement native circuit composition and classical scope contracts
```

If partial, name the supported checkpoint precisely and keep U3 PARTIAL.

## 16. Final Report

Report start/end HEAD; actual new/fixed native APIs; first reds/final greens;
front/inplace/wrap/copy behavior; actual var_remap/inline_captures execution;
Var/Stretch types/scope/reference fidelity; classical traces/quantum results;
full-phase Operator/gradient/Hessian/HVP; format support/rejection boundaries;
actual dual-version differential; three FULLs; four AD frameworks; GLOBAL/
exclusions; original28-section matrix status; source/frozen/stage/commit
identity; remaining Instruction/Circuit ABI gaps; actual push/CI state; whether
full SDK parity is complete.
Do not automatically enter U4 after U3C. Reassess zero widths, arbitrary
names, classical QPY headers, Instruction/Circuit storage and other public
contracts. Continue U3 while substantive core protocol gaps remain. The full
independent native Qiskit/PennyLane replacement goal remains ACTIVE/INCOMPLETE.
