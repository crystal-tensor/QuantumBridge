from __future__ import annotations

from quantumbridge.compat.contracts import (
    AdapterProvenance,
    AdapterWarning,
    CapabilityLevel,
    UnsupportedCapability,
)
from quantumbridge.compat.qiskit_common import normalize_qiskit_inventory_record


def test_capability_levels_are_stable_integers():
    assert int(CapabilityLevel.INVENTORY) == 0
    assert int(CapabilityLevel.PASSTHROUGH) == 1
    assert int(CapabilityLevel.SCHEMA_ADAPTER) == 2
    assert int(CapabilityLevel.NATIVE_SUBSET) == 3
    assert int(CapabilityLevel.PRODUCTION_EQUIVALENT) == 4


def test_provenance_defaults_do_not_claim_cloud_or_endorsement():
    provenance = AdapterProvenance(
        ecosystem="pennylane",
        upstream_package="pennylane",
        adapter="quantumbridge.compat.pennylane_full",
        dependency_extra="pennylane-full",
    )

    payload = provenance.to_dict()

    assert payload["capability_level"] == 0
    assert payload["official_endorsement"] is False
    assert payload["cloud_access"] is False
    assert payload["token_storage"] is False
    assert payload["source_code_copied"] is False


def test_unsupported_capability_has_structured_reason_warning_and_provenance():
    warning = AdapterWarning(
        code="offline-only",
        message="Runtime support is offline-only in this stage.",
    )
    provenance = AdapterProvenance(
        ecosystem="qiskit-runtime",
        upstream_package="qiskit-ibm-runtime",
        capability_level=CapabilityLevel.INVENTORY,
        mode="offline-only",
    )
    unsupported = UnsupportedCapability(
        reason="No cloud access is allowed in Stage 8A.",
        warnings=(warning,),
        provenance=provenance,
    )

    payload = unsupported.to_dict()

    assert payload["supported"] is False
    assert payload["reason"] == "No cloud access is allowed in Stage 8A."
    assert payload["warnings"][0]["code"] == "offline-only"
    assert payload["provenance"]["ecosystem"] == "qiskit-runtime"


def test_qiskit_module_imported_inventory_row_is_not_passthrough_supported():
    class Facade:
        ecosystem = "qiskit_experiments"
        advisory = True

    class Adapter:
        package_key = "qiskit_experiments"

    row = normalize_qiskit_inventory_record(
        Facade(),
        Adapter(),
        {
            "module": "qiskit_experiments",
            "public_api": "module-imported",
            "api_type": "module-status",
            "notes": "module imported; no class/function exported",
        },
    )

    assert row["supported"] is False
    assert row["importable"] is False
    assert row["unsupported_reason"] == "module imported; no class/function exported"
