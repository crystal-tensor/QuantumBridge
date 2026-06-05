import json

import pytest

from quantumbridge.ecosystem import EcosystemAdapter
from quantumbridge.ecosystem.registry import write_inventory


def test_missing_dependency_inventory_is_recorded(tmp_path):
    adapter = EcosystemAdapter(
        package_name="example-missing",
        distribution_name="example-missing",
        root_modules=("quantumbridge_missing_dependency_for_test",),
        dependency_extra="example-extra",
        package_key="example_missing",
    )

    records = adapter.list_public_api_inventory()

    assert len(records) == 1
    assert records[0].public_api == "dependency-not-installed"
    assert records[0].quantumbridge_level == 0


def test_inventory_writer_emits_json_and_markdown(tmp_path):
    adapter = EcosystemAdapter(
        package_name="json",
        distribution_name="json",
        root_modules=("json",),
        dependency_extra="stdlib",
        package_key="json_stdlib",
    )

    inventory_path, matrix_path = write_inventory(
        adapter,
        inventory_dir=tmp_path / "inventory",
        matrix_dir=tmp_path / "matrix",
    )

    rows = json.loads(inventory_path.read_text(encoding="utf-8"))
    matrix = matrix_path.read_text(encoding="utf-8")
    assert rows
    assert "Coverage Matrix" in matrix
    assert "| Upstream Package | Module | Public API | Type | QuantumBridge Level | Mode | Dependency Extra | Test | Risk | Notes |" in matrix


def test_missing_passthrough_has_clear_import_error():
    adapter = EcosystemAdapter(
        package_name="example-missing",
        distribution_name="example-missing",
        root_modules=("quantumbridge_missing_dependency_for_test",),
        dependency_extra="example-extra",
        package_key="example_missing",
    )

    with pytest.raises(ImportError, match="example-extra"):
        adapter.passthrough_class("MissingClass")


def test_result_schema_contains_provenance():
    adapter = EcosystemAdapter("json", "json", ("json",), "stdlib", "json_stdlib")

    wrapped = adapter.wrap_result({"ok": True})

    assert wrapped["schema"] == "quantumbridge.ecosystem.result.v0.1"
    assert wrapped["provenance"]["adapter_package"] == "json"
    assert wrapped["provenance"]["official_endorsement"] is False
