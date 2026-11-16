# Quafu SDK Case Refresh: 2026-11-16

## Scope and preservation

All 29 home-registered cases in four domains and 19 directions have a separate
quafu-sdk update section. Original notebook cells, mathematical outputs,
accuracy caveats, historical receipts and frozen historical stock data remain.
The update is not an acceptance claim for the complete QuantumBridge goal.

The existing domain indexes link each case update. Every case links its JSON,
CSV, PNG and a reproducibility bundle under `downloads/quafu-cases-20261116`.
No separate web port, orphan HTML page or Studio feature was introduced.

## Official SDK and backend contract

The owner-supplied `/docs/sdk/instal` URL returns 404. The actual official
[installation page](https://quafu.com.cn/docs/sdk/install) specifies `quafu-sdk`,
not the older pyquafu or QuarkStudio clients. PyPI reported **0.2.7** at this
check. It was installed in a separate repository-external environment; existing
Qiskit/PennyLane reference profiles and the legacy cloud adapter were not changed.

- [Submission and compilation](https://quafu.com.cn/docs/sdk/submit)
- [Results, bit order and quota](https://quafu.com.cn/docs/sdk/results)
- [Live device limits and calibration](https://quafu.com.cn/docs/sdk/devices)
- [Credential formats](https://quafu.com.cn/docs/sdk/login)
- [Distribution metadata](https://pypi.org/project/quafu-sdk/0.2.7/)

The public device/calibration query genuinely exited 0. Its UTC timestamp,
imported SDK identity, entry hash and unmodified public limits are in
`backend.json`. Baihua was online at that observation. That snapshot is not a
promise that queue, calibration or availability will remain unchanged.
The runner re-reads live limits before submission.

The Mac Python trust store initially rejected the server certificate. Passing
the existing `/etc/ssl/cert.pem` CA bundle to this Client succeeded; certificate
verification was never disabled and no global TLS configuration was changed.

## Frozen work plan

- 27 cases have quantum kernels; the PQC and privacy cases are classical.
- There are **111 distinct source circuits** after exact QASM SHA-256 deduplication.
- This includes 14 chemistry measurements, both four-power call/put MLAE sets,
  both four-power risk MLAE sets, and **all 63 held-out hybrid validation dates**.
- All quantum circuits use at most six logical qubits and request 1024 shots.
- Identical D-Wave portfolio/constraint aliases share a task, not invented runs.
- The D-Wave CQM solver, classical optimization/training, pricing/risk model and
  postprocessing remain classical. The 9-wire PennyLane QPE references remain
  original local references; they are not claimed to run within this hardware cap.
- Cirq exports are checked against the full independent Cirq ideal distribution.
  Missing standard-QASM2 sx definitions are explicit H-S-H definitions. The
  controlled four-wire walk matrix uses installed Qiskit public synthesis; its
  complete terminal distribution is checked, not labelled Native-only synthesis.
- Native local sampling is genuinely rerun at 1024 shots with seed 20261116.
  Fresh PQC/cryptographic checks are also rerun without exporting private keys.

This is a logical plan, not verified physical backend compilation. The provider
must return actual compiler identity, executed QASM, mapping and calibration.
Seven-byte headers, ideal probabilities or a submission acknowledgement are not
substitutes for real execution evidence.

## Receipt and restart rules

`job.id` is the task-group identifier; `result.task_id` identifies the individual
task. The receipt preserves both, compiler settings, executed and submitted
QASM hashes, calibration ID, raw counts, `c0_rightmost`, measurement mapping,
requested/returned shots and actual-shot-normalized probabilities.
The logical q0-first view is separately decoded after checking the mapping.
Hardware noise is not deterministically reproducible with a local seed.

A locked, sealed journal is outside the repository. A durable intent is written
before each submission. Unknown acceptance is never automatically resubmitted;
timeouts keep the remote job alive. Normal quota exhaustion stops further
submissions, without switching backend, consuming degraded quota or silently
starting a new daily batch. SDK-side idempotency does not eliminate the need to
reconcile a lost local job ID.

Each verified result can invoke `--refresh-pages` to rebuild the corresponding
case documentation, tables, data and figures while preserving the original
case. Receipt refreshes reuse the frozen local evidence and original source
identity even if core development has moved on; they do not rerun newer code
and silently refresh old verification dates. Report regeneration cannot change
the frozen execution-plan identity.

Example, after configuring the new SDK identity locally:

```sh
python quafu_case_runtime.py --manifest execution-plan.json \
  --journal /PRIVATE/OUTSIDE-REPOSITORY/journal.json --max-tasks 111 \
  --execute --timeout 5 --ca-bundle /etc/ssl/cert.pem \
  --refresh-pages /PATH/TO/QuantumBridge
```

Use the separate quafu-sdk Python for this runner; `--documentation-python`
selects the existing notebook environment for page rebuilding. For query-only
resumption, omit `--execute`. Keep original journal/configuration unchanged.

## Actual execution and blockers

**New SDK cloud tasks submitted: 0. New hardware results: 0.**

An actual submission command stopped before any cloud submission because neither
`QUAFU_API_KEY` nor the new SDK saved login exists on this machine. The legacy
QuarkStudio token is not silently repurposed as the new credential format. No
browser login, new personal token or paid task was created. Configure the new
SDK identity locally; do not paste a credential into chat, notebooks or Git.

Remote main/gh-pages inspection through the existing `127.0.0.1:7890` Git proxy
exited 128 because that proxy is unavailable. No authorization/global settings
were changed and no dirty core was pushed. This was the initial local-preparation
observation, not a permanent statement about website publication. A later
per-command HTTP/1.1 connection successfully revalidated both remote branch
heads without changing global Git, proxy or authentication settings. Actual
publication must still be established by the resulting branch commits and
deployed-byte checks; local page generation alone never proves deployment.

The local shared preview remains at `http://127.0.0.1:8765/framework.html`.
Each domain's existing case index contains the new update directory.
The full project scope and deadline are unchanged; library parity and hardware
business acceptance are separate from this documentation/runtime slice.

## Focused verification

- Case runner/artifact Python tests: **33 passed**, actual process exit 0.
- Existing Node artifact, public-build and README tests: **14 passed**, exit 0.
- Existing framework check: four domains / 19 bilingual directions passed.
- Existing protected mathematical tests were not edited for this update.
- 29 desktop and 29 phone home-to-case-to-home journeys were exercised in a
  browser. Figures loaded and no document-level horizontal overflow was found.
  Screenshot review additionally found and repaired a clipped long status label.
- The installed quafu-sdk 0.2.7 Result object was exercised with an explicitly
  synthetic local fixture; bit order and shots reconciled, process exit 0. This
  fixture is not a cloud result, actual task ID or hardware acceptance test.
- Original notebooks were not all rerun from scratch. The new offline-default
  cloud code cells were each executed in real Python subprocesses with exit 0;
  original cells retain their original evidence and hashes. The 111 frozen
  circuits were independently replayed locally; this does not validate remote
  compilation, calibration, queue completion or current core-library parity.
