# Stage 12-B P4-U3B Execution Prompt

Status: ACTUALLY RECEIVED TASK / NOT IMPLEMENTATION OR FINAL ACCEPTANCE.
This normalized English transcription preserves the complete owner-authorized
U3B continuation and the subsequently confirmed correction. The correction
supersedes the original confusion between Instruction.repeat and Circuit.repeat.

## Reading Evidence And Checkpoint Review

Conversation: "Claude 代码泄漏与应对",
6a20d458-a76c-83ea-9b49-f8f0caedb3cf. The actual local result and implementation
commit a23c40e9030eb685c2f41fd5b4d1021db1ca9343 were sent using the authorized
connector. The complete rendered review and sections0-11 were read in Chrome:
the latest reply container first showed28-128/128 items, then0-100/128 after
scrolling upward. Completed-answer controls were visible. read_thread timed
out; no source-message ID or independent source review is fabricated.

The report-based review accepts only the supported standard-gate checkpoint:
23 real native classes, SDK-free/main/alternate FULL4473/5728/5726 passed,
all27 R2 child receipts and driver/audit0, GLOBAL91.20221639305609%,
original28-section matrix NOT_RUN, new-SHA remote CI NOT_VERIFIED,
U3/P4/full SDK ACTIVE / INCOMPLETE. The collaborator did not inspect unpushed
source or remote CI. Controlled legal and unowned Router dirty-worktree legal
remain separate facts. Next priority is Instruction/public Circuit semantics,
not adding more standard classes or entering U4.

The original task mislabeled three Instruction.repeat error cases as Circuit
cases. An independent public-only separate-repeat241/260 probe each produced
seven actual observations/exit0. The correction was sent and its complete
rendered answer, four replacement clauses/table and completed-answer state
were actually read at Chrome AX515-699. It confirms seven Instruction plus
three Circuit red cases, with distinct repeat contracts as below.

## 0. Scope

Start from local main a23c40e9030eb685c2f41fd5b4d1021db1ca9343 and continue
U3B: real native Instruction constructor/fifth positional label, inverse
returns and deferred annotation, repeat; Circuit compose/assign_parameters
inplace None return, inverse naming; independently measured Circuit repeat
boundaries; internal fluent/compiler/serialization safety; parameter,
dynamic-control, phase, derivative and resource regressions. Full independent
Qiskit/PennyLane functional parity/replacement stays ACTIVE / INCOMPLETE.
No U4, Studio or extra ecosystem feature implementation.

## 1. Migrate The Ten Real Red Cases First

Move the external positive requirements into controlled tests and run them
before implementation. They are seven Instruction and three Circuit cases,
not ten different missing functions:

| ID | Actual requirement |
| --- | --- |
| I1 | Fifth positional Instruction argument is label. |
| I2 | A supported unitary defined Instruction inverse defaults to actual Gate. |
| I3 | Instruction.inverse(annotated=True) returns actual AnnotatedOperation. |
| I4 | Instruction.repeat(n) is an actual public method. |
| I5-I7 | Instruction.repeat(0/-1/1.5) raises CircuitError. |
| C1 | Circuit.compose(inplace=True) returns None and actually modifies owner. |
| C2 | Circuit.assign_parameters(inplace=True) returns None and binds owner. |
| C3 | Circuit.inverse() uses the observed _dg output-name policy. |

Source requirements: /tmp/test_qb_stage12b_p4u3_instruction_initial_reds.py
and /tmp/test_qb_stage12b_p4u3_instruction_boundaries.py. The former is
reconfirmed on final R2 as4failed/2passed/exit1; the latter is6failed/exit1.
Repeat-invalid cases extend the same missing repeat method, not three APIs.
Run the existing44-record Instruction and43-record boundary public probes
against actual Qiskit2.4.1 and2.6.0. Preserve literal outcomes, exception
class, return type, signature and necessary independent math. Public
Instruction.control/power are ABSENT in both versions: native extensions,
not compatibility gaps or invented red tests.

## 2. Instruction Construction

Implement the public form:

```python
Instruction(name, num_qubits, num_clbits, params, label=None)
```

Protect native definition, metadata and resource extensions. Test five
positional arguments, keyword label/num_clbits, existing safe aliases,
positional/keyword conflicts, label types, nonnegative integer arity, params
intake and owner-backed storage, copy, mutable, base_class and exception
categories. Audit all production constructors before changing signatures.
Distinguish public construction from internal controlled construction. Do not
guess whether an ambiguous old positional value is label or definition;
use an explicit internal construction route where needed. Do not break
existing internal calls merely by reordering __init__ arguments.

## 3. Inverse: Construction, Resolution And Execution

Supported unitary definitions return actual Gate for omitted/False/None;
annotated=True returns AnnotatedOperation. Some opaque or nonunitary public
Instructions permit deferred inverse construction even when ordinary inverse
rejects. Keep construction admissibility, existence of a legal unitary
resolution, and device execution support as separate stages. Do not reject
every deferred measurement/reset construction solely because it has no Gate
inverse; never silently execute a nonunitary instruction as a unitary Gate.

Exercise unitary Instruction -> inverse -> Gate -> append -> Operator ->
independent conjugate-transpose matrix, and Instruction -> annotated inverse
-> representable IR/QPY v13 roundtrip -> real resolution or explicit Unsupported.
Compare full complex matrices, global phase, binding, noncontiguous wires
and copy lifetimes, not just names/types or equality up to phase.

## 4. Real Instruction.repeat(n)

Build an executable repeated definition, not a repeat_count-only wrapper.
Follow actual dual-version Instruction acceptance of positive integers,
positive integral floats, bool and NumPy integers. Test nonpositive and
nonintegral reals, NaN/Inf, string, complex, huge integer, parameterized,
classical-bit and empty definitions, source mutation after repetition, nested
definitions and aggregate work budgets. Admit resources before expansion.
Check full complex equivalence to independently constructed U**n for the
unitary subset. Preserve legitimate nonunitary/dynamic repetition without
forcing every Instruction into Gate. These parameter rules are NOT the
Circuit.repeat rules.

## 5. Circuit Inplace Returns And Fluent Safety

Audit real production call sites for consumed or chained results of compose
and assign_parameters with inplace=True, including equivalent/dynamic keyword
calls. An untyped AST method-name inventory is not proof of receiver identity
or a complete call graph. Write both public ABI tests and genuine internal
execution protections before implementation.

```python
qc = make_test_circuit()
result = qc.compose(other, inplace=True)
assert result is None
assert_circuit_was_modified_correctly(qc)
```

Apply the same contract to assign_parameters. Convert any real internal fluent
dependency to explicit two-step mutation/use; do not keep the wrong public
return just to satisfy internal legacy chaining. Execute real compiler,
QNode, source/binary serialization, standard recipes and SDK-free examples.
Test inplace=False isolation, defaults, valid state after failure, UUID/vector
set updates, ParameterList/Circuit cache invalidation, ControlBlock binding,
transformed QNode parameter dependencies and re-binding after QPY roundtrip.
Returning None without performing the real circuit mutation is prohibited.

## 6. Circuit Inverse Names And Math

Measure and implement _dg naming, including unnamed/empty and named Circuits,
successive inverses, custom definitions, symbolic global phase, dynamic and
nonunitary operations, double inverse, copying and serialization. Do not only
rename objects. Check U_inverse @ U == identity with full complex matrices.
Observe special public naming policies instead of guessing their behavior.

## 7. Keep The Two Repeat Protocols Separate

The corrected actual dual-version observations are:

| Input | Instruction.repeat | QuantumCircuit.repeat |
| --- | --- | --- |
| 0 | CircuitError | Empty operation list, source**0. |
| -1 | CircuitError | Empty operation list, source**-1. |
| 1.5 | CircuitError | TypeError. |
| 2.0 | Accepted as two repeats. | TypeError. |
| True | Accepted as one repeat. | One repeat, source**True. |
| np.int64(2) | Accepted as two repeats. | Two repeats, source**2. |

Circuit zero/negative results and names need independent compatibility
regressions. Do not change them to satisfy Instruction's error tests. Share
underlying resource checks only, not incompatible public argument policies.
Separate API input errors from huge-but-valid-work budget rejections; reject
before allocation/expansion and never swallow true resource exceptions to
imitate a public exception name. Preserve separate Gate integer/negative/zero
power semantics. Distinct repeat results must not be merged into one parity
result or mislabeled as the original three Circuit red cases.

## 8. Nonunitary, Dynamic And Resource Protection

This is not U4, but guard against cross-stage regressions: measurement/reset
Instructions, classical-bit objects, conditional Circuits, nested ControlBlock,
deferred unsupported inverse construction and explicit rejection at actual
resolution, QPY annotations, QASM lossless-or-reject, aggregate definition
budgets, QPY cross-record/circuit numeric limits and100-wire no-dense MPS.
Do not bypass the newly repaired shared max_numeric_elements budget through
repeat, inverse or compose.

## 9. Public Differential And Mathematical Acceptance

Run both versions'44-record Instruction and43-record boundary probes plus
the independently measured Circuit repeat observations, ten initial red cases,
new constructor/inverse/repeat scenarios, inplace/error recovery, native
Operator/Statevector/DensityMatrix math, symbolic gradient/Hessian/HVP,
actual Torch/Autograd/JAX/TF paths, QPY v13 annotation/custom/standard records,
H2, Aer noise and100-wire MPS. Distinguish callability, literal returns,
return-object types, exception classes, post-mutation state and mathematics.
Generic mathematical equivalence is not concrete return-ABI equivalence.
Successful public construction does not establish executable validity.

## 10. Tests, Gates And Commit Conditions

Prefer existing test organization. Suggested modules:

```text
tests/circuit/test_native_instruction_public_abi.py
tests/circuit/test_native_instruction_inverse_repeat.py
tests/circuit/test_native_circuit_inplace_contracts.py
tests/circuit/test_native_circuit_inverse_repeat_errors.py
tests/compat/test_qiskit_instruction_circuit_abi_differential.py
```

First observe migrated reds, then change real production behavior. On the
same final frozen code run SDK-free FULL; main Qiskit2.4.1/PennyLane0.44.1
FULL; alternate Qiskit2.6.0/PennyLane0.42.3 FULL; independent JAX/TF FOCUS;
Torch/Autograd FOCUS; dual-version public differential; explicit GLOBAL
coverage; compileall; controlled legal; affected real SDK-free numeric
examples; actual frozen/staged/commit runtime equality audit. New GLOBAL
baseline91.20221639305609%, exclusions68. No increased exclusions, weakened
tolerances or deleted tests to obtain green. Original28-section matrix stays
NOT_RUN until actual P4-U5 joint acceptance. Preserve protected Studio/Router
dirt. No unauthorized push, authentication/TLS changes, history rewriting,
vendor, hardware/cloud calls. Normal scoped local commit after actual gates:

```text
feat: align native instruction and circuit public contracts
```

If only part is finished, name the supported checkpoint accurately and do
not mark U3 DONE.

## 11. Required Final Report

State whether all ten initial cases are fixed; actual callable constructor/
inverse/repeat; absent public control/power still labeled native extensions;
internal fluent safety after None returns; correct naming/repeat exceptions
and math; QPY/IR/compiler/derivative/MPS status; actual dual-version outcomes;
complete local gate/coverage/independent exits; remaining U3 signatures/error
gaps; original P4/full SDK still incomplete. Reassess substantive U3 public
ABI gaps after this batch; continue U3 if any remain, do not approve U4.
Full independent Qiskit/PennyLane functional parity/replacement remains
ACTIVE / INCOMPLETE.
