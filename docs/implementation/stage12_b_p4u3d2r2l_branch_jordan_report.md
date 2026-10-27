# Native Operator Branch and Jordan Correctness Checkpoint

2026-10-23. This is an incomplete development checkpoint inside the original
R2 task, not complete Qiskit/PennyLane replacement or a frozen acceptance run.
No new hardware tasks, financial evidence changes, dependencies, Studio/Router,
Git history operations, commits or pushes were performed.

## Real Reds and Oracle Correction

The original 45-case exploration was re-executed before the repair:
18 numerical matches to its reference, 24 explicit numerical refusals,
3 wrong finite outputs. The captured 2x2 Fourier-similarity input was frozen
element by element with float.hex, not replaced by a real Hadamard fixture.
New independent tests initially produced **27 failed / 84 passed**: the original
three and 24 failures in a strictly exact-binary dense Jordan family.

The earlier ideal Jordan reference is not authoritative for the rounded
Fourier input on a branch cut. For the *actual binary input*, a 100-digit
characteristic-polynomial interpolation oracle gives eigenvalues near
`-0.9999999958344471 + 2.20495369e-9j` and
`-1.0000000041655527 - 2.20495371e-9j`, on opposite sides of the default cut.
The theoretical exact Jordan input is a different matrix.

The original native errors against this correct actual-input oracle were:

| Power | Pre-repair max complex error | Relative error | Post-repair outcome |
| --- | ---: | ---: | --- |
| 0.5 | 13469634.579791859 | 0.4232281284 | Quantified LinAlgError, no finite output |
| 0.3 | 10897163.283072066 | 0.4232281240 | Quantified LinAlgError, no finite output |
| -0.3 | 10897163.283072070 | 0.4232281240 | Quantified LinAlgError, no finite output |

The true 100-digit square-root residual is about `1.185e-86`; rounding that
correct answer to complex128 yields a NumPy multiplication residual of
`0.1267783059`. The old native residual was `0.1333319062`. Therefore an
absolute square-root residual alone cannot decide correctness on this
extremely ill-conditioned input. The original oracle and post-repair outcome
are separate immutable/generated files; a refusal is not recorded as zero
forward error or as numerical support.

The collaborator's original R2L ideal-Jordan requirement was explicitly
corrected after receiving this evidence. The actual full replies are retained
in `stage12_b_p4u3d2r2l_received_prompt.md` and
`stage12_b_p4u3d2r2l_oracle_correction.md`. No xfail, skip, wider tolerance or
fake coalescing is used to hide the original failure.

## Native Repair

`matrix_functions.py` retains the existing owned-array/resource/Schur/binomial
matrix-function engine and adds three operations:

1. For a 2x2 matrix, certify the discriminant identity exactly using its binary
   scalar values and standard-library Fraction arithmetic. Only an exactly
   zero discriminant admits the repeated-eigenvalue derivative formula.
   A merely small discriminant never merges distinct branches. This is a
   constant-size scalar certificate, not another matrix execution backend.
2. For a coupled Schur pair straddling the logarithm branch, compare its
   eigenvalue separation with a conservative sensitivity screen derived from
   the admitted Schur backward resolution and coupling. Refuse before an
   unresolved branch produces a plausible but unreliable matrix. The error
   reports gap, coupling, resolution and screen, not just output magnitude.
   This is a conservative numerical screen, not a rigorous all-matrix
   condition-number certification.
3. Detect exact disconnected matrix components and apply the same native
   function to each. This preserves strict repeated 2x2 blocks inside a 4x4
   matrix, including interleaved component indices, without a global unstable
   eigensolver or a new executor.

For exact repeated spectra, the implementation uses
`f(A) = f(lambda) I + p f(lambda)/lambda (A-lambda I)`, preserving the full
complex derivative and nonnormal term. Matrix input, winding of the selected
cut, ownership and existing array/workspace limits remain intact. Python
scalar-certificate allocator/RSS is explicitly unobserved; the fixed-size
binary scalar work is charged and no resource ceilings are raised.

The mathematical references are the scalar branch, matrix-function and
binomial identities, not source implementations.
[Higham on fractional matrix powers](https://nhigham.com/2020/12/08/what-is-a-fractional-matrix-power/)

## Numerical Evidence

- **108/108 strict binary Jordan cases compute numerically**, not by refusal:
  lambda in `-.25,-1,-2`, coupling `.125,.25,.5`, three exponents and four cuts.
  The measured maximum error in the dual-version probe is about `3.14e-16`.
- **32 separated cross-cut nonnormal cases compute**, including fixed-unitary
  dense similarities. There is no blanket negative-axis or cross-cut refusal.
- Exact 4x4 block diagonals and interleaved disconnected components compute.
- Managed output leases release, input remains unchanged, false normality is
  rejected, and the exact-pair certificate follows memory preflight and avoids
  the unstable eigensolver. Existing malicious/dtype/dimension/work guards run.
- The original 45-case probe now has **18 numerical results / 27 refusals /
  0 wrong finite results**. The refusals are not counted as numeric passes.
- Two actual public versions, Qiskit **2.4.1 and 2.6.0**, each execute 153
  recorded comparisons: original 45 plus strict 108. Against valid independent
  references, the native wrong-result count is 0. Forty-two strict Jordan
  observations per public version disagree numerically with the exact analytic
  reference; these are scoped observed UPSTREAM_DEFECT classifications, not a
  claim about all public matrix powers. The original three actual-input
  differences are separately classified as intentional numerical safety.
- For larger rounded near-cut cases without a trusted actual-input oracle,
  the ideal Jordan limit is reference-only; certification is marked unsupported
  and is not counted as correct numerical parity.

The focused old/new power modules execute **420 passed** in each installed SDK
environment; SDK-free executes **364 passed / 56 unavailable-public skips**.
All 151 new branch/Jordan tests run SDK-free without new skips or xfails.

## Shared Regression Evidence

Completed during this checkpoint:

| Scope | Actual result |
| --- | --- |
| Information/core/circuit/compiler, JAX x64 enabled | 3997 passed, 2 warnings, 304.03s, exit 0 |
| Serialization | 776 passed, 3 existing xfailed, 6 warnings |
| Gradients/QML/devices/noise/H2 selected workflows | 357 passed, 2 warnings |
| Finance and all compat_quafu after repair | 183 passed, SDK-free |
| SDK-free native public frames example | Actual matrix/IR/QPY/first/second/HVP/100-wire MPS checks executed |
| SDK-free bit/register QPY gradient example | Executed gradient and HVP, 100 wires |
| SDK-free Aer density/MPS example | Executed counts and native MPS receipt |
| New SDK-free Operator/state/density example | 6 numerical cases, max matrix error about 1.57e-16 |
| compileall, F821, diff check | Passed for changed numerical sources |

An initial broad information/core/circuit/compiler run completed with
**3974 passed / 23 failed**. All 23 were JAX tests explicitly requesting float64
while the process had JAX x64 disabled, with warnings proving truncation to
float32 and errors around 1e-7. No tolerances or library global configuration
were changed. With `JAX_ENABLE_X64=True`, those exact 23 rerun **23 passed**.
The complete same-group x64 rerun then terminated **3997 passed**, 2 warnings,
304.03 seconds, exit 0. This is a four-directory development regression, not
the whole SDK FULL gate.

## Remaining Work

Original R2 is not frozen or accepted. The three-environment SDK FULL runs,
independent final JAX/TF/Torch/Autograd gates, explicit GLOBAL coverage baseline
`91.34108013033072%`, unchanged 68 exclusions, original 28-section matrix,
all SDK-free examples, controlled legal/import origins and frozen/worktree/
stage/commit equality remain unproven in this checkpoint. ParameterView,
factory/error/resource and other original R2 ABI gaps are not erased by the
matrix repair. Reliable larger near-cut nonnormal ranges also remain partial.

All 13 finance hardware task receipts remain unchanged and 7 task slots remain
unused. Financial accuracy stays INCONCLUSIVE. No scoped commit is made before
the required final gates. The full independent native Qiskit/PennyLane
functional-parity/full-replacement goal remains ACTIVE/INCOMPLETE.

## Reproduction Artifacts

`output/operator-branch-jordan/pre_repair_exact_input.json` retains the original
wrong finite results and exact-input high-precision references.
`tests/information/data/operator_branch_actual_input.json` is the frozen
SDK-free regression fixture. `public-main.json` and `public-alternate.json`
contain all 153 actual public/native observations and reference-validity flags.

```bash
PYTHONPATH=. python -m pytest -q tests/information/test_native_operator_power_branch_jordan.py
PYTHONPATH=. python examples/native_operator_branch_powers.py
PYTHONPATH=. python scripts/probe_operator_branch_jordan.py --public --output output/operator-branch-jordan/public-main.json
```

The last command needs the already installed development oracle/public SDK;
runtime and SDK-free tests do not import mpmath or a public SDK executor.
