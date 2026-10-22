# Stage 12-B P4-U3 Execution Prompt

Status: ACTUALLY RECEIVED TASK / NOT IMPLEMENTATION OR FINAL ACCEPTANCE.
This is the complete normalized English transcription of the10-section
owner-authorized ChatGPT continuation, preserving every execution requirement.

## Reading Evidence And Review

Conversation: "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. U2 final result was sent after the local
implementation commit. The complete rendered reply, review table and task
were actually read in Chrome AX2022-2622, with completed-answer state visible.
Backend read_thread timed out; a content-reference/source-message ID is not
fabricated. The final reply was read, not inferred from a loading placeholder.

Report-based U2 checkpoint acceptance: e2e60554abff49a54600ed1c8fda385bec293e83,
mutable/validation supported subset and atomic state tests accepted; SDK-free/
main/alternate FULL4263/5291/5289 passed; global91.1484%; original28-section
matrix NOT_RUN; push/new-SHA remote CI unverified; P4-U/P4/full SDK PARTIAL.
No established new blocker in the report. The collaborator has not independently
inspected unpushed source or remote CI. Do not reimplement accepted U2 parameter
machinery; advance specialized types, annotated defaults and error contracts.

## 1. Objective

Start from local main e2e60554abff49a54600ed1c8fda385bec293e83. On the existing
Gate/ControlledGate/AnnotatedOperation/ParameterList architecture, add real
standard public Gate objects and behavior. Prioritize RX/RY/RZ dedicated types;
control/inverse/power return types and public semantics; annotated=None/True/
False; standard parameter validation; returned objects' bind/copy/definition;
exception classes and timing; native Operator/Gradient/Hessian/HVP; actual
IR/QASM/QPY interchange. No second Gate or quantum execution engine; preserve
U2 atomic parameter updates.

## 2. First Red: Dedicated Standard Return Types

Using only actual public Qiskit2.4.1 and2.6.0 APIs, construct RXGate(.37),
RYGate and RZGate, and call inverse(annotated=True), power(2,annotated=True),
control(1,annotated=True). Record actual type, base_class, name, params,
definition, whether AnnotatedOperation and the full complex matrix.
Do not assume all methods return the same type. Then write real native reds:
RX/RY/RZ methods must not always degrade to generic Gate. Implement actual
specialized objects sharing the existing Operation/Gate execution path.

## 3. Second Red: Measure Annotated Defaults

For generic Gate and RX/RY/RZ, separately call control(1),
control(1,annotated=None), control(1,annotated=False), control(1,annotated=True).
Test corresponding available inverse/power signatures too. Distinguish
omitted arguments from explicit None/False/True. Do not infer actual behavior
from deprecation warnings. If versions differ, record both literal outcomes
and explicitly select the native target contract.

## 4. Actual Standard Classes

Prioritize RXGate, RYGate, RZGate, PhaseGate, UGate, HGate, XGate, YGate,
ZGate, CXGate, CZGate and SwapGate; extend other standards when real dependencies
require them. Each must actually support construction, parameter checks, copy,
inverse, control, its supported power subset, definition, to_matrix or existing
Operator, native Circuit.append and native serialization. Empty subclasses
whose names are counted as completed functions are not sufficient. Handle
base_class and applicable singleton semantics without sacrificing safe native
object ownership merely to imitate Python internals.

## 5. Gate/Instruction/Annotation ABI

Focus on name, label, params, num_qubits, num_clbits, definition, base_class,
mutable, copy, inverse, control, power and validate_parameter. Measure actual
public versions for Circuit inplace return values. Four independent acceptance
dimensions: correct mathematics; correct return type; correct parameter and
definition lifetimes; correct exception class and timing. Matrix equality
alone does not establish full API parity.

## 6. Parameter And Exception Semantics

Keep U2 strong atomicity: invalid g.params=[.2,1j] cannot leave a partially
changed Gate. Record observed public partial mutation as ABI difference; never
copy that unsafe behavior. At least test wrong parameter counts; complex angles;
nonfinite parameters; equal names/distinct UUIDs; ParameterVectorElement;
mutable/frozen objects; invalid control counts; invalid ctrl_state; unsupported
symbolic fractional powers; incompatible definitions; nested annotation;
unsupported nonunitary control. Use clear exception categories without hiding
native causes merely to reproduce upstream exception names.

## 7. Mathematical, Derivative And Format Regression

Real execution chain: specialized standard Gate -> annotated control/inverse/
power -> binding -> native Circuit/compiler -> Operator/Statevector/DensityMatrix
-> Jacobian/Hessian/streamed HVP. Compare complete complex matrices to independent
math, not phase-discarding comparisons. Protect controlled global phase, open
controls, UUID/vector, P3 symbolic functions, P4-S custom definitions, U1 bilateral
QPY annotations, U2 ParameterList, Aer composite-noise guard and100-wire MPS
no-dense execution. For new standard types in QPY v13, restore specialized types
where actual standard fields permit; never fabricate identity merely from a
gate name for objects that cannot be preserved. Actual public bilateral QPY
loading remains required.

## 8. Required New Tests

- At least12 standard construction/return-type scenarios.
- At least12 annotated omitted/explicit-argument scenarios.
- At least10 parameter/mutable lifetime scenarios.
- At least10 exception/resource scenarios.
- At least8 math/gradient/HVP scenarios.
- At least10 QPY/IR/compiler scenarios.
- At least20 actual dual-version public differential scenarios.

First produce two real return-type/default-behavior reds, then implement.
Use public2.4.1/2.6.0 APIs only; do not inspect/copy upstream source or tests.

## 9. Gates

First focused checks:

```sh
python3 -m compileall -q quantumbridge
pytest -q -rs tests/circuit
pytest -q -rs tests/serialization
pytest -q -rs tests/compiler
pytest -q -rs tests/qml
pytest -q -rs tests/devices
git diff --check
```

Then on final U3 frozen code: SDK-free FULL, main FULL, alternate FULL,
independent JAX FOCUS, independent TF FOCUS, Torch/Autograd FOCUS, dual-version
public differential, explicit global coverage, legal/privacy/no-vendor/no-token,
scoped-file audit. Effective GLOBAL baseline91.14835394634642%; no increased
exclusions, deleted failing tests or weakened mathematical tolerances. Original
28-section matrix is still U5 joint acceptance; U3 must not claim it passed
unless actually run with a real independent exit receipt.

## 10. Git And Final Report

Only normal scoped local commits. No git add ., Studio/Router changes,
reset/rebase/amend/force, authentication/TLS changes, token reads or bypassing
GitHub workflow permissions. Suggested commit:
feat: implement native standard gate return and error contracts.

Report starting/ending HEAD; actual specialized types; literal dual-version
four-way annotated behavior; returned types/base_class; validation/lifetimes;
math/native derivatives; QPY/IR/compiler; native/public differential; three FULL
environments; JAX/TF/Torch/Autograd FOCUS; coverage; real Git/CI state; U4/U5 gaps.
Only after real U3 code, math and complete local gates pass, proceed to U4
dynamic/empty/resource contracts and then U5 original28-section/P4 acceptance.
Full Qiskit/PennyLane functional parity remains ACTIVE / INCOMPLETE.

## Initial Evidence, Not Completed U3

Public probe /tmp/qb-stage12b-p4u3-public-probe.py produced60 actual observations
per version; /tmp/qb-stage12b-p4u3-public241 and public260 both terminate0.
All observations include actual matrices/definitions/types.48 method cases
separate omitted/None/False/True;12 standard constructors are also observed.
The versions' recorded outcomes agree excluding version/warnings.

Actual generic control returns ControlledGate for omitted/None/False and
AnnotatedOperation for True; generic numeric power returns UnitaryGate for
omitted/None/False and AnnotatedOperation for True. RX/RY/RZ retain specialized
types under all four modes: control gives CRX/CRY/CRZ, inverse/power retain
their rotation class. Singleton standard classes have distinct type/base_class;
these observations are not claims that native matching already exists.

Outside-suite positive tests /tmp/test_qb_stage12b_p4u3_initial_reds.py ran on
the unchanged accepted U2 frozen source. /tmp/qb-stage12b-p4u3-initial-reds
terminates1 with6failed/5passed:3 missing dedicated exports,3 generic numeric
power return mismatches. Generic control's four annotation choices and generic
power(True) pass. Move/extend these reds into controlled U3 tests during actual
implementation; do not count them as completed support or hide them in U2 gates.
No U3 production code has changed at this documentary continuation checkpoint.
