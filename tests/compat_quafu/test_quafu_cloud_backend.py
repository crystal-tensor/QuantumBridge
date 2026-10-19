import json

import pytest

from quantumbridge.compat.quafu import QuafuCloudBackend, QuarkStudioTransport
from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.providers import JobStatus
from quantumbridge.schema.backend_results import QuafuBackendResult


class FakeTransport:
    transport_name = "fake-quarkstudio"

    def __init__(self, responses=None):
        self.responses = list(responses or [{"status": "finished", "count": {"00": 520, "11": 504}}])
        self.submissions = []

    def submit(self, openqasm, *, backend_name, shots, name, compile):
        self.submissions.append(
            {
                "openqasm": openqasm,
                "backend_name": backend_name,
                "shots": shots,
                "name": name,
                "compile": compile,
            }
        )
        return "task-123"

    def retrieve(self, task_id):
        assert task_id == "task-123"
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]

    def status(self, task_id=None):
        return {"Dongling": 2}

    def cancel(self, task_id):
        return {"status": "Cancelled", "task_id": task_id}


def test_quafu_cloud_backend_submits_and_wraps_real_transport_contract():
    transport = FakeTransport([{"status": "running"}, {"status": "finished", "count": {"00": 520, "11": 504}}])
    backend = QuafuCloudBackend("Baihua", transport=transport)
    job = backend.submit(quafu_bell_circuit(), shots=1024, name="bell-cloud")

    assert job.job_id() == "task-123"
    assert job.status() == JobStatus.QUEUED
    result = job.result(timeout=1, poll_interval=0)

    assert isinstance(result, QuafuBackendResult)
    assert result.mode == "cloud_hardware"
    assert result.counts == {"00": 520, "11": 504}
    assert sum(result.probabilities.values()) == pytest.approx(1.0)
    assert result.metadata["backend_name"] == "Baihua"
    assert result.metadata["cloud_access"] is True
    assert result.provenance["hardware_access"] is True
    assert transport.submissions[0]["openqasm"].startswith("OPENQASM 2.0;")


def test_cloud_backend_auto_measures_and_enforces_quark_shot_unit():
    circuit = quafu_bell_circuit().remove_final_measurements()
    transport = FakeTransport()
    backend = QuafuCloudBackend(transport=transport)
    backend.submit(circuit, shots=1024)
    assert "measure q[0] -> c[0];" in transport.submissions[0]["openqasm"]
    with pytest.raises(ValueError, match="multiple of 1024"):
        backend.submit(circuit, shots=1000)


def test_cloud_backend_exposes_queue_status_and_remote_cancel():
    transport = FakeTransport([{"status": "pending"}])
    backend = QuafuCloudBackend("Dongling", transport=transport)
    job = backend.submit(quafu_bell_circuit())
    assert backend.status() == {"Dongling": 2}
    assert job.cancel() is True
    assert job.status() == JobStatus.CANCELLED
    assert job.cancel() is False


def test_cloud_backend_rejects_unbound_parameters():
    from quantumbridge import Circuit, Parameter

    circuit = Circuit(1, 1).rx(Parameter("theta"), 0).measure(0, 0)
    with pytest.raises(ValueError, match="parameters to be bound"):
        QuafuCloudBackend(transport=FakeTransport()).submit(circuit)


def test_quark_transport_requires_explicit_credential(monkeypatch):
    monkeypatch.delenv("QUAFU_TOKEN", raising=False)
    monkeypatch.delenv("QUAFU_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="requires an explicit token"):
        QuarkStudioTransport(task_factory=lambda token: object())


def test_quark_transport_uses_repeat_contract_without_serializing_token():
    secret = "test-only-secret"

    class FakeTaskManager:
        def __init__(self, token):
            assert token == secret
            self.calls = []

        def run(self, task, repeat):
            self.calls.append((task, repeat))
            return "task-123"

        def result(self, task_id):
            return {"count": {"0": 1024}}

    transport = QuarkStudioTransport(secret, task_factory=FakeTaskManager)
    backend = QuafuCloudBackend(transport=transport)
    result = backend.run(quafu_bell_circuit(), shots=1024, poll_interval=0)
    serialized = json.dumps(result.to_dict(), sort_keys=True)

    submitted_task, submitted_repeat = transport._task_manager.calls[0]
    assert submitted_task["shots"] == 1024
    assert submitted_repeat == 1
    assert secret not in serialized
    assert secret not in repr(transport)
    assert result.job_spec["openqasm_sha256"]
    assert "circuit" not in result.job_spec
