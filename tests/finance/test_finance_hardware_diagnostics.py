"""Offline diagnostic contracts: no credentials, network, or real submissions."""

import json

import pytest

from quantumbridge.compat.quafu import QuafuCloudBackend
from quantumbridge.finance.execution import FinanceCloudSession, _journal_digest
from quantumbridge.finance.hardware_diagnostics import FinanceDiagnosticSession, audit_task, diagnostic_circuits, zero_one_metrics
from quantumbridge.providers import JobTimeoutError
from tests.finance.test_finance_hardware_guards import Transport


def session_at(tmp_path, transport=None):
    original = FinanceCloudSession(QuafuCloudBackend(transport=Transport()), journal=tmp_path / "session.json")
    original.calibrate_bit_order(poll_interval=0)
    backend = QuafuCloudBackend(transport=transport or Transport({"status": "finished", "counts": {"000": 1024}}))
    # Keep injected IDs distinct from the original calibration ID.
    backend._transport.submissions.append("original-placeholder")
    return FinanceDiagnosticSession(backend, original_journal=original.journal,
                                    journal=tmp_path / "diagnostics/diagnostic_task_ledger.json")


def test_four_deterministic_gate_minimal_probes():
    circuits = diagnostic_circuits()
    assert len(circuits) == 4
    for key, circuit in circuits.items():
        assert all(op.name == "x" for op in circuit.operations)
        assert len(circuit.operations) == (circuit.num_qubits if key.endswith("one") else 0)


def test_restart_preserves_original_and_submits_no_duplicate(tmp_path):
    session = session_at(tmp_path)
    before = session.original.journal.read_bytes()
    first = session.run_one("diagnostic/3q-zero", poll_interval=0)
    second = session.run_one("diagnostic/3q-zero", poll_interval=0)
    assert first == second
    assert len(session.backend._transport.submissions) == 2
    assert session.original.journal.read_bytes() == before
    with pytest.raises(RuntimeError, match="frozen"):
        with session.original._journal_lock():
            session.original._raw_job("new/task", diagnostic_circuits()["diagnostic/3q-zero"], timeout=1, poll_interval=0)


def test_ambiguous_submission_is_not_retried(tmp_path):
    transport = Transport()
    session = session_at(tmp_path, transport)

    def interrupted(*args, **kwargs):
        raise ConnectionError("accepted status unknown")

    transport.submit = interrupted
    with pytest.raises(ConnectionError):
        session.run_one("diagnostic/3q-zero")
    with pytest.raises(RuntimeError, match="intent"):
        session.run_one("diagnostic/3q-zero")
    assert "pending_submission" in json.loads(session.journal.read_text())


def test_pending_task_timeout_reuses_id(tmp_path):
    transport = Transport({"status": "running"})
    session = session_at(tmp_path, transport)
    with pytest.raises(JobTimeoutError):
        session.run_one("diagnostic/3q-zero", timeout=0, poll_interval=0)
    transport.payload = {"status": "finished", "counts": {"000": 1024}}
    assert session.run_one("diagnostic/3q-zero", poll_interval=0)["job"]["job_id"] == "task-2"
    assert len(transport.submissions) == 2


@pytest.mark.parametrize("problem", ["original-change", "duplicate-id", "wrong-plan", "shot-count"])
def test_resealed_conflicting_ledger_cannot_resume(tmp_path, problem):
    session = session_at(tmp_path)
    session.run_one("diagnostic/3q-zero", poll_interval=0)
    data = json.loads(session.journal.read_text())
    saved = data["jobs"]["diagnostic/3q-zero"]
    if problem == "original-change":
        session.original.journal.write_text(session.original.journal.read_text() + "\n")
    elif problem == "duplicate-id":
        saved["job"]["job_id"] = "task-1"
    elif problem == "wrong-plan":
        saved["artifact"]["gates"] = 99
    else:
        saved["raw_counts"] = {"000": 1023}
    data["integrity_sha256"] = _journal_digest(data)
    session.journal.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        FinanceDiagnosticSession(session.backend, original_journal=session.original.journal, journal=session.journal)


def test_combined_budget_checked_before_submission(tmp_path):
    from copy import deepcopy

    session = session_at(tmp_path)
    job = next(iter(session.original.data["jobs"].values()))
    for i in range(19):
        saved = deepcopy(job)
        saved["job"].update(job_id=f"old-{i}", name=f"qb-finance-old/{i}")
        session.original.data["jobs"][f"old/{i}"] = saved
    session.original._save()
    session = FinanceDiagnosticSession(session.backend, original_journal=session.original.journal, journal=session.journal)
    with pytest.raises(ValueError, match="budget"):
        session.run_one("diagnostic/3q-zero")


def test_mapping_is_ambiguous_even_for_perfect_zero_and_one():
    for width in (3, 4):
        for value in (0, 1):
            result = zero_one_metrics({str(value) * width: 1024}, width, value)
            assert result["success_probability"] == 1
            assert result["mapping_status"] == "AMBIGUOUS"
            assert not result["mitigation_applied"]


def test_noisy_marginals_and_joint_errors_are_not_independent_by_assumption():
    result = zero_one_metrics({"000": 512, "110": 512}, 3, 0)
    assert result["multiple_bit_error_probability"] == .5
    assert result["pair_errors"][0]["error_covariance"] == .25
    assert result["mapping_status"] == "AMBIGUOUS"


@pytest.mark.parametrize("counts", [{"000": 1023}, {"00": 1024}, {"000": 1024.0}, {"000": True}])
def test_invalid_shots_labels_counts_rejected(counts):
    with pytest.raises(ValueError):
        zero_one_metrics(counts, 3, 0)


@pytest.mark.parametrize("field", ["tid", "chip", "count", "circuit", "transpiled", "status"])
def test_readonly_audit_refuses_inconsistent_or_missing_metadata(tmp_path, field):
    session = session_at(tmp_path)
    saved = session.run_one("diagnostic/3q-zero", poll_interval=0)
    source = saved["artifact"]["openqasm"]
    payload = {"tid": saved["job"]["job_id"], "chip": session.backend.name, "count": saved["raw_counts"],
               "circuit": source, "transpiled": source, "status": "Finished", "error": ""}
    valid = audit_task(saved, payload)
    assert valid["compiled_vs_submitted_tvd"] == 0
    assert valid["fields"]["calibration_id"]["status"] == "ABSENT"
    payload.pop(field)
    with pytest.raises(ValueError):
        audit_task(saved, payload)
