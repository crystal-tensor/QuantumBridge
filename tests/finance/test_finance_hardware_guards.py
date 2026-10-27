"""Cloud protocol red tests: no credentials, network or hardware used."""

import json

import pytest

from quantumbridge.compat.quafu import QuafuCloudBackend
from quantumbridge.core import Circuit
from quantumbridge.finance import FinanceCloudSession
from quantumbridge.providers import JobError


class Transport:
    transport_name = "protocol-test-only"

    def __init__(self, payload=None):
        self.submissions = []
        self.payload = payload

    def submit(self, source, **kwargs):
        self.submissions.append(source)
        return f"task-{len(self.submissions)}"

    def retrieve(self, task_id):
        return self.payload or {"status": "finished", "counts": {"10": 1024}}


@pytest.mark.parametrize("status", ["failed", "cancelled", "error"])
def test_remote_failure_with_stale_counts_is_never_success(status):
    backend = QuafuCloudBackend(transport=Transport({"status": status, "counts": {"0": 1024}}))
    with pytest.raises(JobError):
        backend.run(Circuit(1, 1), poll_interval=0)


@pytest.mark.parametrize("value", [1024.0, 1024.9, True, "1024", -1])
def test_gateway_does_not_coerce_invalid_counts_into_finance_samples(value):
    backend = QuafuCloudBackend(transport=Transport({"status": "finished", "counts": {"0": value}}))
    with pytest.raises(JobError):
        backend.run(Circuit(1, 1), poll_interval=0)


@pytest.mark.parametrize("field", ["bit_order", "shots", "job_id", "qasm", "raw_counts"])
def test_modified_journal_is_rejected_before_remote_calls(tmp_path, field):
    path = tmp_path / "journal.json"
    transport = Transport()
    session = FinanceCloudSession(QuafuCloudBackend(transport=transport), journal=path)
    session.calibrate_bit_order(poll_interval=0)
    data = json.loads(path.read_text())
    saved = data["jobs"]["calibration/bit-order"]
    if field == "bit_order":
        data["bit_order"] = "q0-last"
    elif field == "shots":
        saved["job"]["shots"] = 2048
    elif field == "job_id":
        saved["job"]["job_id"] = "different-task"
    elif field == "qasm":
        saved["artifact"]["openqasm"] += "x q[1];"
    else:
        saved["raw_counts"] = {"01": 1024}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        FinanceCloudSession(session.backend, journal=path)
    assert len(transport.submissions) == 1


@pytest.mark.parametrize("corruption", ["duplicate-task", "shots", "qasm", "failed-counts", "bit-order"])
def test_recomputed_checksum_does_not_bypass_structural_checks(tmp_path, corruption):
    from copy import deepcopy
    from quantumbridge.finance.execution import _journal_digest

    path = tmp_path / "journal.json"
    session = FinanceCloudSession(QuafuCloudBackend(transport=Transport()), journal=path)
    session.calibrate_bit_order(poll_interval=0)
    data = json.loads(path.read_text())
    saved = data["jobs"]["calibration/bit-order"]
    if corruption == "duplicate-task":
        extra = deepcopy(saved)
        extra["job"]["name"] = "qb-finance-other/job"
        data["jobs"]["other/job"] = extra
    elif corruption == "shots":
        saved["job"]["shots"] = 2048
    elif corruption == "qasm":
        saved["artifact"]["openqasm"] += "x q[0];"
    elif corruption == "failed-counts":
        saved["job"]["status"] = "ERROR"
    else:
        data["bit_order"] = "q0-last"
    data["integrity_sha256"] = _journal_digest(data)
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        FinanceCloudSession(session.backend, journal=path)


def test_absent_credential_does_not_construct_the_cloud_client(monkeypatch, tmp_path):
    monkeypatch.delenv("QUAFU_TOKEN", raising=False)
    monkeypatch.delenv("QUAFU_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="credential|explicit token"):
        FinanceCloudSession.from_environment(journal=tmp_path / "absent.json")
    assert not (tmp_path / "absent.json").exists()
