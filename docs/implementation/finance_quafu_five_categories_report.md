# Five Finance Categories: Implementation And Verification

Date: 2026-10-23

## Follow-Up: Actual Hardware Results Retrieved

The initial local snapshot below is retained as history. The owner subsequently
provided the credential and authorized local storage. All original9 Dongling
tasks have now finished with1024 measured shots each. Real counts, task IDs,
exact QASM and hash-checked notebook replay are present. Numerical acceptance
is INCONCLUSIVE with substantial measured discrepancies; see
`docs/implementation/finance_quafu_hardware_acceptance.md`. Execution completion
must not be confused with financial accuracy or full SDK parity.

## Initial Local Snapshot

Local implementation, Chinese tutorials and local executed outputs are present.
**Hardware acceptance is NOT complete.** No finance cloud task was submitted in
this batch because the process has no configured Quafu credential. A secure
local credential location was requested, not another website login. No secret
from the earlier reference script was copied into these files or notebooks.

This is one representative executable workflow per finance category, not every
function in the financial industry, full Qiskit Finance parity, or production
finance. The original native full-SDK goal remains incomplete.

## Deliverables

- `quantumbridge/finance/kernels.py`: bounded real/signed probability-state
  loading with elementary RY/CX gates, quadratic-cost QAOA, local training,
  expectation statistics and discrete VaR/expected shortfall.
- `quantumbridge/finance/cases.py`: five synthetic input models, explicit
  intermediate tables, independent classical references and measured-result
  financial analysis.
- `quantumbridge/finance/execution.py`: existing native simulation and Quafu
  cloud transport reuse, strict counts decoding, explicit shot/task/qubit
  limits, asymmetric bit-order calibration, persistent task receipts,
  timeout retrieval and POSIX concurrent-kernel locking.
- `scripts/build_finance_notebooks.py`: five Chinese tutorials, actual notebook
  execution, embedded plots and HTML reading editions.
- `output/jupyter-notebook/finance/index.html`: browser entry with five reading
  editions and five downloadable `.ipynb` files. Static HTML needs no server.
- `docs/tutorials/finance_quafu_five_categories.md`: execution and scope guide.

The five notebooks each contain principles, input data, formulas, implementation
steps, full generated QASM, intermediate results, ideal-vs-shot plots, final
analysis, real cloud opt-in code, evidence export, an exercise and references.
All 45 code cells executed to completion locally with zero error outputs and
15 embedded PNG plots. No result is fabricated or relabeled as hardware.

## Actual 1024-Shot Local Results

Seed: 20261023, incremented within each case. These are **local simulator
measurements**, not Quafu hardware counts.

| Category | Exact reference | Observed local result |
| --- | --- | --- |
| Allocation | `1001`, objective -0.13 | `1001` found, gap 0; feasible probability 0.7109375, optimal probability 0.1181640625 |
| Risk: base | EL 1.54, VaR95 6, ES95 11.6 | EL 1.7314453125, VaR95 8, ES95 13.078125 |
| Risk: stress | EL 2.6, VaR95 12, ES95 16 | EL 2.73828125, VaR95 12, ES95 17.3125 |
| Derivatives | three-step call 10.05471821, Delta 0.60699697 | call 10.60408203, Delta 0.61116530; price sampling SE 0.43225007 |
| Constraints | `1010`, objective -0.124 | `1010` found, gap 0; feasible probability 0.478515625, optimal probability 0.115234375 |
| Correlation: positive | 0.96617392 | 0.951171875 |
| Correlation: negative | -0.97266612 | -0.966796875 |
| Annual historical volatility | 0.23289281 | 0.23031605 |

The unhedged vs static-delta-hedged terminal P&L standard deviations in the
derivatives example are 14.24628826 vs 5.10551403. This is not a dynamic hedge
or a guarantee for other scenarios. Three-step binomial vs Black-Scholes call
pricing differs by about 0.64131483 before sampling; model and sampling errors
are reported separately. Finite-shot put-call parity residual is not hidden.

The base VaR jump is intentionally retained. A finite sample near a discrete
CDF atom can change the selected quantile. A 95% DKW empirical-CDF bound has
epsilon approximately 0.0424 at 1024 IID shots; it does not cover hardware bias,
model misspecification or certify exact tail risk.

## Cloud Budget And Evidence Rules

Owner approved option 1: at most 20 total tasks, exactly 1024 shots per task,
at most 6 qubits, stop on any charging prompt. Planned execution: 8 business
circuits plus 1 bit-order calibration = 9 tasks and 9216 shots. Business circuits
use at most 4 qubits. No invoice/quote API or free-execution guarantee is assumed.

The installed QuarkStudio `QuantumCircuit.from_openqasm2` accepted all 8 actual
business-circuit artifacts. This is a genuine local parser check, **not remote
compilation, backend availability, authenticated submission or hardware proof**.

The shared `output/finance-hardware/session.json` records each accepted task ID
before waiting for counts. A timeout does not authorize a second submission.
Reruns retrieve the original task; changed circuits and different backend/shot
contracts refuse journal reuse. An OS lock prevents concurrent kernels from
double-submitting from the same ledger. The remote-accept/local-durable-write
crash window remains explicit because there is no provider idempotency key.
Non-production injected test transports are labeled `injected_transport`, not
hardware. Protocol test fixtures are never notebook hardware outputs.

Cloud analysis requires actual counts, correct width/bit order and exact shot
count. Calibration failure or inconsistent shots stops before interpreting
business results. Native and hardware evidence are stored separately so a local
rerun does not overwrite existing hardware evidence. No actual hardware evidence
file exists for this batch at report time.

## Verification

- SDK-free NumPy environment, finance + existing Quafu + existing Qiskit Finance
  compatibility regression: 87 passed, one existing scaffold warning.
- Finance-only independent tests: 57 passed.
- Finance line coverage: 410/425 statements, **96.470588%**. This is local test
  coverage, not hardware or full project acceptance.
- Ruff: passed on new finance modules, tests and generator.
- Notebook validation/execution: 5 notebooks, 45/45 code cells, zero errors,
  15 plots; actual current Python interpreter, fresh IPC kernels.
- Browser checks: desktop1440 and mobile390 across the index and all five
  reading editions; zero document overflow or broken images, no page errors.
  Index also checked at320. A plotted derivatives result was visually inspected.
- Generated artifacts contain no copied provider token.
- New source paths are added to the source migration ledger and notices.

A broader legal check additionally failed at the pre-existing untracked
`quantumbridge/router/core.py` missing from the migration ledger. This same
issue was recorded in the earlier Stage10G report. It is not repaired or hidden
by this finance change; no full-repository-green claim is made. The initial
coverage invocation encountered a local mixed-install NumPy loading issue;
preloading the selected environment's NumPy before pytest produced the final
successful coverage receipt without changing dependencies. HTML export was
fixed to locate the installed Jupyter templates under the base interpreter.

No commit, push, PR, tag, release, OAuth change, vendoring or dependency install
was performed. Existing dirty workspace changes are preserved. The outstanding
next action is real cloud submission/retrieval with a safely supplied valid
credential, within the already approved task budget, followed by separate
hardware-result/error reporting. This report does not mark that action done.
