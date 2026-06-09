# This file is independently implemented for QuantumBridge SDK.
# No source code or website content from IBM, Qiskit, PennyLane, or third-party projects was copied.

import pytest

from quantumbridge.ecosystem.catalog import EcosystemProject, make_catalog


def test_ecosystem_catalog_schema_roundtrip_and_search():
    project = EcosystemProject(
        project_id="qiskit-algorithms",
        display_name="QuantumBridge Algorithms Slice",
        upstream_name="Qiskit Algorithms",
        category="algorithms",
        tags=("algorithms", "vqe", "qaoa", "grover"),
        adapter_module="quantumbridge.compat.qiskit_algorithms",
        capability_level=3,
        executable_workflows=("native_vqe", "native_qaoa", "native_grover"),
        clean_room_status="executable",
        official_endorsement=False,
    )
    catalog = make_catalog([project])
    payload = catalog.to_dict()
    restored = catalog.from_dict(payload)
    assert restored.to_dict() == payload
    assert restored.search("grover")[0].project_id == "qiskit-algorithms"
    assert restored.filter_by_category("algorithms")[0].capability_level == 3


def test_ecosystem_catalog_rejects_official_endorsement_claim():
    with pytest.raises(ValueError):
        EcosystemProject(
            project_id="bad",
            display_name="Bad",
            upstream_name="Bad",
            category="bad",
            official_endorsement=True,
        )
