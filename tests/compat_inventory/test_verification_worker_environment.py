"""Worker metadata must not be inferred from the recorder's interpreter."""
from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).parents[2] / "scripts/record_engineering_verification.py"
PACKAGES = ("numpy", "scipy", "tensorflow", "jax", "torch", "qiskit", "pennylane")
spec = importlib.util.spec_from_file_location("worker_environment_recorder", SCRIPT)
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture(tmp_path):
    checkpoint = tmp_path / "checkpoint"
    source = checkpoint / "source"
    (source / "scripts").mkdir(parents=True)
    (source / "tests").mkdir()
    (source / "quantumbridge").mkdir()
    (source / "scripts/record_engineering_verification.py").write_bytes(SCRIPT.read_bytes())
    (source / "tests/fixture.py").write_text("def test_fixture(): assert True\n")
    (source / "quantumbridge/fixture.py").write_text("VALUE = 1\n")
    manifest = {str(path.relative_to(source)): recorder.sha(path.read_bytes()) for path in source.rglob("*.py")}
    write(checkpoint / "source-manifest.json", manifest)
    write(checkpoint / "protected-tests.json", {"tests/fixture.py": manifest["tests/fixture.py"]})
    args = SimpleNamespace(name="fixture", profile="alternate", checkpoint=checkpoint,
        xml=tmp_path / "result.xml", origin=tmp_path / "origin.json", terminal=tmp_path / "terminal.json",
        environment_receipt=tmp_path / "environment.json", protected_tests=checkpoint / "protected-tests.json",
        approved_migrations=None, output=tmp_path / "recorded.json")
    args.xml.write_text('<testsuites><testsuite><testcase classname="tests.fixture" name="test_fixture"/></testsuite></testsuites>')
    origin = dict(root=str(source), test_exit=0, matching_modules=1, modules={"quantumbridge.fixture": "quantumbridge/fixture.py"})
    environment = {name: "fixture" for name in PACKAGES}
    environment.update(python="3.12.6", qiskit="2.6.0", pennylane="0.42.3")
    snapshot = dict(environment=environment, runtime=dict(executable="/fixture/python", prefix="/fixture",
        base_prefix="/base", implementation="cpython"))
    receipt = dict(schema=1, profile=args.profile, run_id="unique-fixture-run", pid=1234, root=str(source),
        complete=True, test_exit=0, source_manifest_sha256=recorder.sha((checkpoint / "source-manifest.json").read_bytes()),
        capture_script_sha256=manifest["scripts/record_engineering_verification.py"],
        junit_sha256=recorder.sha(args.xml.read_bytes()), start=copy.deepcopy(snapshot), end=copy.deepcopy(snapshot))
    write(args.origin, origin)
    write(args.environment_receipt, receipt)
    terminal = dict(terminal=True, exit=0, pid=1234, environment_run_id=receipt["run_id"],
        environment_receipt_sha256=recorder.sha(args.environment_receipt.read_bytes()))
    write(args.terminal, terminal)
    return args, receipt, terminal


def collect(args):
    with redirect_stdout(io.StringIO()):
        recorder.collect(args)
    return json.loads(args.output.read_text())["runs"][0]


def test_alternate_worker_environment_is_used_even_when_recorder_metadata_is_unavailable(tmp_path, monkeypatch):
    args, receipt, _ = fixture(tmp_path)
    def forbidden(*unused):
        pytest.fail("Recorder interpreter was mistaken for the test worker")
    monkeypatch.setattr(recorder.importlib.metadata, "version", forbidden)
    monkeypatch.setattr(recorder.platform, "python_version", forbidden)
    row = collect(args)
    assert row["environment"] == receipt["start"]["environment"]
    assert row["environment_validation"]["verified"] and row["environment_validation"]["worker_pid"] == 1234
    assert "/fixture/python" not in json.dumps(row)
    assert not {"executable", "prefix", "base_prefix"}.intersection(row["environment_validation"])
    assert row["total"] == row["passed"] == 1 and row["protected_tests_unchanged"]


def test_missing_receipt_is_unknown_not_current_interpreter_metadata(tmp_path, monkeypatch):
    args, *_ = fixture(tmp_path)
    args.environment_receipt = None
    def forbidden(*unused):
        pytest.fail("Missing worker evidence used recorder metadata")
    monkeypatch.setattr(recorder.importlib.metadata, "version", forbidden)
    row = collect(args)
    assert row["environment"] == {}
    assert row["environment_validation"] == dict(provided=False, verified=False, source="missing_test_worker_receipt")


@pytest.mark.parametrize("fault", ["schema_bool", "schema_version", "incomplete", "profile", "run_id",
    "pid_bool", "pid", "root", "manifest", "capture", "junit", "exit_bool", "exit", "end",
    "package_missing", "package_extra", "package_type", "python_missing", "runtime", "runtime_type",
    "terminal_pid", "terminal_pid_bool", "terminal_run", "terminal_hash", "terminal_missing", "start_type",
    "capture_missing_in_manifest", "receipt_type", "terminal_timeout"])
def test_mismatched_worker_receipts_cannot_publish_a_verification_row(tmp_path, fault):
    args, receipt, terminal = fixture(tmp_path)
    if fault == "schema_bool": receipt["schema"] = True
    elif fault == "schema_version": receipt["schema"] = 99
    elif fault == "incomplete": receipt["complete"] = False
    elif fault == "profile": receipt["profile"] = "main"
    elif fault == "run_id": receipt["run_id"] = []
    elif fault == "pid_bool": receipt["pid"] = True
    elif fault == "pid": receipt["pid"] = -1
    elif fault == "root": receipt["root"] = str(tmp_path)
    elif fault == "manifest": receipt["source_manifest_sha256"] = "wrong"
    elif fault == "capture": receipt["capture_script_sha256"] = "wrong"
    elif fault == "junit": receipt["junit_sha256"] = "wrong"
    elif fault == "exit_bool": receipt["test_exit"] = False
    elif fault == "exit": receipt["test_exit"] = 1
    elif fault == "end": receipt["end"]["environment"]["qiskit"] = "changed"
    elif fault == "package_missing":
        for key in ("start", "end"): del receipt[key]["environment"]["numpy"]
    elif fault == "package_extra":
        for key in ("start", "end"): receipt[key]["environment"]["unrequested"] = "extra"
    elif fault == "package_type":
        for key in ("start", "end"): receipt[key]["environment"]["qiskit"] = ["2.6.0"]
    elif fault == "python_missing":
        for key in ("start", "end"): receipt[key]["environment"]["python"] = None
    elif fault == "runtime":
        for key in ("start", "end"): del receipt[key]["runtime"]["prefix"]
    elif fault == "runtime_type":
        for key in ("start", "end"): receipt[key]["runtime"]["prefix"] = 42
    elif fault == "terminal_pid": terminal["pid"] = 2345
    elif fault == "terminal_pid_bool": terminal["pid"] = True
    elif fault == "terminal_run": terminal["environment_run_id"] = "different"
    elif fault == "terminal_timeout": terminal["timed_out"] = True
    elif fault == "start_type": receipt["start"] = None
    elif fault == "terminal_missing": args.terminal = None
    elif fault == "receipt_type": receipt = []
    elif fault == "capture_missing_in_manifest":
        path = args.checkpoint / "source-manifest.json"
        manifest = json.loads(path.read_text())
        del manifest["scripts/record_engineering_verification.py"]
        write(path, manifest)
        receipt["source_manifest_sha256"] = recorder.sha(path.read_bytes())
        receipt["capture_script_sha256"] = None
    write(args.environment_receipt, receipt)
    terminal["environment_receipt_sha256"] = "wrong" if fault == "terminal_hash" else recorder.sha(args.environment_receipt.read_bytes())
    if args.terminal is not None: write(args.terminal, terminal)
    with pytest.raises(ValueError, match="environment|terminal"):
        collect(args)
    assert not args.output.exists()


def test_capturing_distribution_metadata_does_not_import_the_sdks(monkeypatch):
    before = {name for name in sys.modules if name.split(".", 1)[0] in {"qiskit", "pennylane", "tensorflow", "torch", "jax"}}
    def version(name):
        if name == "qiskit":
            raise recorder.importlib.metadata.PackageNotFoundError(name)
        return "fixture"
    monkeypatch.setattr(recorder.importlib.metadata, "version", version)
    value = recorder._capture_environment()
    after = {name for name in sys.modules if name.split(".", 1)[0] in {"qiskit", "pennylane", "tensorflow", "torch", "jax"}}
    assert value["environment"]["qiskit"] is None and value["environment"]["pennylane"] == "fixture"
    assert after == before and value["runtime"]["executable"] == sys.executable


def test_plugin_binds_its_snapshot_pid_manifest_and_completed_junit(tmp_path, monkeypatch):
    args, _, _ = fixture(tmp_path)
    args.environment_receipt.unlink()
    for key, value in dict(QB_ENVIRONMENT_RECEIPT=str(args.environment_receipt),
        QB_ENVIRONMENT_RUN_ID="real-worker-fixture", QB_ENGINEERING_PROFILE=args.profile,
        QB_EXPECTED_NATIVE_ROOT=str(args.checkpoint / "source"),
        QB_EXPECTED_NATIVE_MANIFEST=str(args.checkpoint / "source-manifest.json")).items():
        monkeypatch.setenv(key, value)
    session = SimpleNamespace(config=SimpleNamespace(option=SimpleNamespace(xmlpath=str(args.xml))))
    recorder.pytest_sessionstart(session)
    recorder.pytest_sessionfinish(session, 0)
    recorder.pytest_unconfigure(session.config)
    receipt = json.loads(args.environment_receipt.read_text())
    assert receipt["complete"] and receipt["pid"] == recorder.os.getpid()
    assert receipt["start"] == receipt["end"] == recorder._capture_environment()
    write(args.terminal, dict(terminal=True, exit=0, pid=receipt["pid"], environment_run_id=receipt["run_id"],
        environment_receipt_sha256=recorder.sha(args.environment_receipt.read_bytes())))
    row = collect(args)
    assert row["environment_validation"]["verified"] and row["environment"] == receipt["start"]["environment"]


def test_plugin_does_not_overwrite_an_existing_receipt(tmp_path, monkeypatch):
    args, _, _ = fixture(tmp_path)
    before = args.environment_receipt.read_bytes()
    monkeypatch.setenv("QB_ENVIRONMENT_RECEIPT", str(args.environment_receipt))
    monkeypatch.setenv("QB_ENVIRONMENT_RUN_ID", "duplicate")
    monkeypatch.setenv("QB_ENGINEERING_PROFILE", "fixture")
    session = SimpleNamespace(config=SimpleNamespace(option=SimpleNamespace(xmlpath=str(args.xml))))
    with pytest.raises(ValueError, match="already exists"):
        recorder.pytest_sessionstart(session)
    assert args.environment_receipt.read_bytes() == before


def test_plugin_does_nothing_without_explicit_capture_configuration(monkeypatch):
    monkeypatch.delenv("QB_ENVIRONMENT_RECEIPT", raising=False)
    config = SimpleNamespace()
    session = SimpleNamespace(config=config)
    recorder.pytest_sessionstart(session)
    recorder.pytest_sessionfinish(session, 0)
    recorder.pytest_unconfigure(config)
    assert vars(config) == {}
