# Finance–Quafu Hardware Acceptance

Date: 2026-10-23. Backend: **Dongling**.

## Actual Execution

The original 9 tasks completed: 8 business circuits and 1 bit-order calibration,
1024 shots each, **9216 actual shots**, maximum4 business qubits. The owner
approved at most20 tasks,1024 shots each, at most6 qubits;11 tasks remain unused.
No additional retry, mitigation or tuning job is submitted by this export.

| Experiment | Actual Task ID | Actual shots | Execution |
| --- | --- | --- | --- |
| calibration/bit-order | 2610231235264038840 | 1024 | DONE |
| allocation/qaoa | 2610231235383826369 | 1024 | DONE |
| risk/base | 2610231235440801552 | 1024 | DONE |
| risk/stress | 2610231235484838251 | 1024 | DONE |
| derivatives/risk_neutral_paths | 2610231235566974565 | 1024 | DONE |
| constraints/qaoa | 2610231236018836200 | 1024 | DONE |
| correlation/positive_correlation | 2610231236118773106 | 1024 | DONE |
| correlation/negative_correlation | 2610231236189351427 | 1024 | DONE |
| correlation/time_sampling | 2610231236333069511 | 1024 | DONE |

Calibration raw counts: `{"00": 38, "01": 828, "10": 11, "11": 147}`.
Dominant `01` identifies q0-last under the provider's consistent bit-order
convention. This is not full per-wire tomography or readout-error mitigation.

## Numerical Acceptance Is Not Execution Success

No owner-approved business-error tolerances exist. Overall numerical acceptance
remains **INCONCLUSIVE**, not PASS. There are substantial observed discrepancies:

- Allocation: feasible probability 0.378906,
  unconditional optimal-hit probability 0.073242.
- Constrained optimization: feasible probability 0.245117,
  unconditional optimal-hit probability 0.047852.
- Base risk: EL 3.423828,
  VaR95 20.0, ES95 20.0;
  exact input-model references are1.54,6,11.6.
- Call price 8.25075993, compared with exact3-step
  reference10.05471821; Delta 0.51276372.
- Positive-correlation measurement -0.11914062
  contradicts the intended positive reference0.96617392. Negative-correlation
  measurement -0.11523438
  also differs substantially from reference-0.97266612.

Finding a single optimal bitstring is not stable solver success. Per-case
reports separately show feasible, conditional optimum and unconditional optimum
probabilities, Wilson intervals and conditional mean objective. Risk reports
show empirical multinomial bootstrap intervals and DKW VaR ranges, including
discrete boundary probability mass. An empirical bootstrap can miss unseen
tails and is not a hardware-bias confidence interval.

| Business circuit | TVD vs actual submitted ideal circuit | Numerical status |
| --- | --- | --- |
| allocation/qaoa | 0.366456 | INCONCLUSIVE |
| risk/base | 0.253281 | INCONCLUSIVE |
| risk/stress | 0.232070 | INCONCLUSIVE |
| derivatives/risk_neutral_paths | 0.164001 | INCONCLUSIVE |
| constraints/qaoa | 0.337881 | INCONCLUSIVE |
| correlation/positive_correlation | 0.634355 | INCONCLUSIVE |
| correlation/negative_correlation | 0.604038 | INCONCLUSIVE |
| correlation/time_sampling | 0.138672 | INCONCLUSIVE |

## Evidence And Error Attribution

`output/finance-hardware/session.json` retains all task IDs, original submitted
QASM, exact hashes and raw counts. Separate immutable JSON exports are in
`raw_counts/` and `normalized_counts/`; `finance_metrics.json` and
`hardware_vs_ideal.json` contain measured business metrics and uncertainty.
These are actual authenticated-service results, not simulated or injected
transport fixtures. They are not a cryptographic attestation of hardware.

The cloud runtime and notebook runtime differ by one floating-point ULP in one
RY angle. The exact submitted QASM is therefore reloaded for replay and ideal
probabilities; its SHA must match both the original plan and receipt. Its full
complex state must also match the unchanged financial reference at the existing
2e-14 preparation-test tolerance. Hash checks are not weakened and no task is
resubmitted. Same frozen decoding is used for ideal, local and real counts.

Three-step tree-vs-Black–Scholes model error, finite-shot sampling error and
hardware distribution discrepancy are separate. Compiled physical mapping,
current device calibration and a physical noise model are not available in the
saved provider receipt; the specific cause of the large discrepancies is
**not determined**. No arbitrary TVD cutoff, noise explanation or quantum
advantage claim is added after seeing results.

## Safety And Verification

The received credential was saved outside the repository in macOS Keychain.
Cloud calls used hidden in-memory input; no credential is included here or in
notebooks. The platform's old128-byte interactive `security -w` prompt truncated
the supplied longer credential; it was replaced via native Security APIs and
the complete credential then authenticated successfully. No token or password
value is printed. Background CLI keychain reads require macOS authorization;
no website login or authentication bypass was requested.

Real red tests found stale counts masking failed/cancelled jobs and coercion
of noninteger counts. The shared cloud gateway is repaired, with regression
tests. Sealed journals additionally validate hashes, task IDs, shot contracts,
states and calibration evidence. A local SHA checksum detects inconsistent
edits but is not an authenticated defense against coherent local forgery.

Five notebooks now replay original hardware receipts without a network request
using `QB_FINANCE_REPLAY_HARDWARE=1`; graphs explicitly compare real counts with
the same submitted circuit's ideal distribution. No source vendoring, dependency
installation, push, PR, tag or release occurred. Full Qiskit/PennyLane parity
and the original R2 full-regression requirements remain **ACTIVE / INCOMPLETE**.
