#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Offline export of actual retrieved counts; never sends a cloud request."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantumbridge.finance import build_finance_cases  # noqa: E402
from quantumbridge.finance.acceptance import analyze_case_evidence, restore_submitted_circuits  # noqa: E402


def write_immutable(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != data:
            raise ValueError(f"refusing to overwrite changed raw evidence: {path.name}")
        return
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def main():
    folder = ROOT / "output/finance-hardware"
    journal = json.loads((folder / "session.json").read_text(encoding="utf-8"))
    reports, metrics, task_ids = {}, {}, set()
    notebooks = ROOT / "output/jupyter-notebook/finance"
    for key, original in build_finance_cases().items():
        case = restore_submitted_circuits(original, folder / "session.json")
        evidence = json.loads((notebooks / f"{key}_hardware_evidence.json").read_text(encoding="utf-8"))
        results = evidence["hardware_results"]
        reports[key] = analyze_case_evidence(case, results)
        metrics[key] = reports[key]["measured_analysis"]
        for name, result in results.items():
            task_id = result["task_id"]
            if task_id in task_ids:
                raise ValueError("task ID reused across finance cases")
            task_ids.add(task_id)
            common = {"task_id": task_id, "backend": result["backend"], "case": key,
                      "experiment": name, "shots": result["shots"], "sha256": result["artifact"]["sha256"]}
            write_immutable(folder / "raw_counts" / f"{task_id}.json", {**common, "counts": result["raw_counts"],
                                                                     "bit_order": result["provider_bit_order"]})
            write_immutable(folder / "normalized_counts" / f"{task_id}.json", {**common, "counts": result["counts"],
                                                                            "bit_order": "q0-first"})
    write_immutable(folder / "task_ledger.json", journal)
    for filename, data in (("finance_metrics.json", metrics), ("hardware_vs_ideal.json", reports)):
        (folder / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    rows = "\n".join(f"| {key} | {saved['job']['job_id']} | {sum(saved['raw_counts'].values())} | DONE |"
                     for key, saved in journal["jobs"].items())
    tvd = "\n".join(f"| {key}/{name} | {row['total_variation_distance']:.6f} | INCONCLUSIVE |"
                    for key, report in reports.items() for name, row in report["experiment_diagnostics"].items())
    document = f"""# Finance–Quafu Hardware Acceptance

Date: 2026-10-23. Backend: **{journal['backend']}**.

## Actual Execution

The original 9 tasks completed: 8 business circuits and 1 bit-order calibration,
1024 shots each, **9216 actual shots**, maximum4 business qubits. The owner
approved at most20 tasks,1024 shots each, at most6 qubits;11 tasks remain unused.
No additional retry, mitigation or tuning job is submitted by this export.

| Experiment | Actual Task ID | Actual shots | Execution |
| --- | --- | --- | --- |
{rows}

Calibration raw counts: `{json.dumps(journal['jobs']['calibration/bit-order']['raw_counts'], sort_keys=True)}`.
Dominant `01` identifies q0-last under the provider's consistent bit-order
convention. This is not full per-wire tomography or readout-error mitigation.

## Numerical Acceptance Is Not Execution Success

No owner-approved business-error tolerances exist. Overall numerical acceptance
remains **INCONCLUSIVE**, not PASS. There are substantial observed discrepancies:

- Allocation: feasible probability {metrics['allocation']['feasible_probability']:.6f},
  unconditional optimal-hit probability {metrics['allocation']['optimal_probability']:.6f}.
- Constrained optimization: feasible probability {metrics['constraints']['feasible_probability']:.6f},
  unconditional optimal-hit probability {metrics['constraints']['optimal_probability']:.6f}.
- Base risk: EL {metrics['risk']['base']['expected_loss']:.6f},
  VaR95 {metrics['risk']['base']['VaR']}, ES95 {metrics['risk']['base']['CVaR_expected_shortfall']};
  exact input-model references are1.54,6,11.6.
- Call price {metrics['derivatives']['call_price']:.8f}, compared with exact3-step
  reference10.05471821; Delta {metrics['derivatives']['delta']:.8f}.
- Positive-correlation measurement {metrics['correlation']['positive_correlation']['correlation']:.8f}
  contradicts the intended positive reference0.96617392. Negative-correlation
  measurement {metrics['correlation']['negative_correlation']['correlation']:.8f}
  also differs substantially from reference-0.97266612.

Finding a single optimal bitstring is not stable solver success. Per-case
reports separately show feasible, conditional optimum and unconditional optimum
probabilities, Wilson intervals and conditional mean objective. Risk reports
show empirical multinomial bootstrap intervals and DKW VaR ranges, including
discrete boundary probability mass. An empirical bootstrap can miss unseen
tails and is not a hardware-bias confidence interval.

| Business circuit | TVD vs actual submitted ideal circuit | Numerical status |
| --- | --- | --- |
{tvd}

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
"""
    (ROOT / "docs/implementation/finance_quafu_hardware_acceptance.md").write_text(document, encoding="utf-8")
    print(json.dumps({"business_tasks": len(task_ids), "total_tasks": len(journal["jobs"]),
                      "execution": "COMPLETED", "numerical_acceptance": "INCONCLUSIVE"}))


if __name__ == "__main__":
    main()
