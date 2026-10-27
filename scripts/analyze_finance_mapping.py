#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""D2 exclusively offline audit; no network, credential or submit path."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantumbridge.compat.quafu import QuafuCloudBackend  # noqa: E402
from quantumbridge.finance.execution import FinanceCloudSession  # noqa: E402
from quantumbridge.finance.hardware_diagnostics import FinanceDiagnosticSession, audit_task, zero_one_metrics  # noqa: E402
from quantumbridge.finance.mapping_diagnostics import (  # noqa: E402
    compare_tasks, count_order_hypotheses, experiment_identifiability, gate_profile, joint_error_bootstrap, ordered_mapping,
)
from run_finance_diagnostics import BASE, fingerprint_original, write_json  # noqa: E402


def main():
    dest = BASE / "diagnostics/d2"
    watched = list(BASE.glob("*.json")) + list((BASE / "raw_counts").glob("*.json")) + list((BASE / "normalized_counts").glob("*.json"))
    watched += list((BASE / "provider_metadata").glob("*.json"))
    for name in ("provider_metadata", "zero_one_raw_counts"):
        watched += list((BASE / "diagnostics" / name).glob("*.json"))
    watched.append(BASE / "diagnostics/diagnostic_task_ledger.json")
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    original_finance = fingerprint_original()
    provider = SimpleNamespace(name="Dongling")
    original = FinanceCloudSession(provider, journal=BASE / "session.json")
    diagnostics = FinanceDiagnosticSession(provider, original_journal=original.journal,
                                           journal=BASE / "diagnostics/diagnostic_task_ledger.json")
    audits, records, hypothesis, joints = {}, {}, {}, {}
    for parent, folder in ((original, BASE), (diagnostics, BASE / "diagnostics")):
        for key, saved in parent.data["jobs"].items():
            payload = json.loads((folder / "provider_metadata" / f'{saved["job"]["job_id"]}.json').read_text())
            audit = audit_task(saved, payload)
            audit["gate_profile"] = gate_profile(payload["transpiled"])
            audit["ordered_measurement_mapping"] = ordered_mapping(audit)
            audits[key], records[key] = audit, saved
            hypothesis[key] = count_order_hypotheses(saved["raw_counts"], audit["native_compiled"]["probabilities"], ordered_mapping(audit))
            if key.startswith("diagnostic/"):
                prepared = str(int(key.endswith("one"))) * saved["artifact"]["num_qubits"]
                joints[key] = {**joint_error_bootstrap(saved["raw_counts"], prepared),
                               "metrics": zero_one_metrics(saved["raw_counts"], len(prepared), int(prepared[0]))}
                assert len({candidate["noiseless_multinomial_log_likelihood_up_to_constant"] for candidate in hypothesis[key]["candidates"]}) == 1
    ids = [item["task_id"] for item in audits.values()]
    if len(ids) != 13 or len(set(ids)) != 13 or len(ids) > 20:
        raise ValueError("D2 requires the same thirteen unique tasks within total budget")
    pairings = {f"{old} :: {probe}": compare_tasks(audit, audits[probe]) for old, audit in audits.items()
                if not old.startswith("diagnostic/") for probe in diagnostics.data["jobs"]}
    plans = {
        "3q_single_one_hot": experiment_identifiability(["001"]),
        "3q_two_distinct_patterns": experiment_identifiability(["001", "010"]),
        "4q_single_one_hot": experiment_identifiability(["0001"]),
        "4q_three_one_hot": experiment_identifiability(["0001", "0010", "0100"]),
        "4q_two_asymmetric_patterns": experiment_identifiability(["0011", "0101"]),
    }
    for plan in plans.values():
        plan.update(target_physical_set=[3, 4, 10] if len(plan["patterns_q0_first"][0]) == 3 else [3, 4, 10, 11],
                    provider_fixed_layout_capability="UNVERIFIED; current adapter exposes chip/compile only",
                    precharge_compile_or_dry_run="UNVERIFIED; no live API requests in D2",
                    decision="NO_NEW_SUBMISSION_RECOMMENDED",
                    stop_conditions=["owner approval absent", "target mapping not verified before charge", "mapping changes", "unexpected billing or shots", "combined budget risk"],
                    marginal_value="potential count-order evidence only for the explicitly verified layout; no automatic historical transfer")
    write_json(dest / "physical_layout_matrix.json", audits)
    write_json(dest / "historical_task_pairing.json", pairings)
    write_json(dest / "count_order_hypotheses.json", hypothesis)
    write_json(dest / "joint_error_patterns.json", joints)
    asymmetry = {}
    for width in (3, 4):
        zero, one = (joints[f"diagnostic/{width}q-{state}"]["metrics"] for state in ("zero", "one"))
        asymmetry[str(width)] = {
            "raw_label_position_one_minus_zero_error": [b["probability"] - a["probability"] for a, b in zip(
                zero["marginal_errors_by_raw_label_position"], one["marginal_errors_by_raw_label_position"])],
            "one_minus_zero_success": one["success_probability"] - zero["success_probability"],
            "qualification": "state preparation plus measurement; cannot isolate pure readout or assign a physical wire without count order"}
    write_json(dest / "zero_one_asymmetry.json", asymmetry)
    write_json(dest / "mapping_identifiability.json", {"status": "AMBIGUOUS", "reason": "unknown count serialization and preparation/hardware noise; symmetric probes carry no permutation information",
                                                     "selected_permutation": None, "readout_mitigation_applied": False})
    write_json(dest / "candidate_experiment_plan.json", plans)
    after = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    if before != after or original_finance != fingerprint_original():
        raise ValueError("immutable original or diagnostic evidence changed")
    write_json(dest / "d2_readonly_audit.json", {"file_hashes": before, "all_unchanged": True, "task_ids": ids,
               "total_tasks": 13, "new_submissions": 0, "remaining_tasks": 7,
               "network_connections_disabled": True, "submit_gateway_disabled": True,
               "financial_acceptance": "INCONCLUSIVE", "decision": "NO_NEW_SUBMISSION_RECOMMENDED"})
    print(json.dumps({"tasks_audited": 13, "historical_probe_pairs": len(pairings), "new_submissions": 0,
                      "unchanged": True, "decision": "NO_NEW_SUBMISSION_RECOMMENDED"}))


if __name__ == "__main__":
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("D2 forbids network connections")), \
            patch.object(socket.socket, "connect_ex", side_effect=RuntimeError("D2 forbids network connections")), \
            patch.object(QuafuCloudBackend, "submit", side_effect=RuntimeError("D2 forbids new hardware tasks")):
        main()
