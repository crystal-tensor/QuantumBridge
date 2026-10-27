# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Offline protocol numerics and actual local cryptography checks."""

import copy
import json
import shutil
import subprocess

import numpy as np
import pytest

from quantumbridge.applications.common import run_local_case
from quantumbridge.applications.security import (
    audit_record,
    bb84_circuit,
    bb84_transcript,
    grover_circuit,
    hamming_correct,
    hamming_encode,
    pqc_case,
    privacy_case,
    qrng_case,
    stream_health,
    threat_case,
    von_neumann_extract,
    qkd_case,
    verify_audit,
)
from quantumbridge.devices import StatevectorDevice


@pytest.mark.parametrize("bit", [0, 1])
@pytest.mark.parametrize("basis", [0, 1])
def test_bb84_matched_and_mismatched_basis(bit, basis):
    device = StatevectorDevice()
    assert device.probabilities(bb84_circuit(bit, basis, basis)).get(
        str(bit)
    ) == pytest.approx(1)
    assert device.probabilities(bb84_circuit(bit, basis, 1 - basis)).get(
        "1"
    ) == pytest.approx(0.5)


def test_protocol_qber_and_no_production_keys():
    clean, eve = bb84_transcript(), bb84_transcript(eve=True)
    assert clean["qber"] == 0
    assert 0.20 < eve["qber"] < 0.30
    assert clean["sifted_count"] == eve["sifted_count"]
    assert qkd_case().outputs["production_key_emitted"] is False


@pytest.mark.parametrize("position", range(7))
def test_hamming_single_bit_errors(position):
    data = [1, 0, 1, 1]
    word = hamming_encode(data)
    word[position] ^= 1
    decoded, syndrome = hamming_correct(word)
    assert decoded == data
    assert syndrome == position + 1


@pytest.mark.parametrize("marked", ["0000", "1011", "1111"])
def test_grover_analytic_amplification_and_clean_work_wire(marked):
    theta = np.arcsin(1 / 4)
    device = StatevectorDevice()
    for r in range(6):
        p = device.probabilities(grover_circuit(r, marked))
        assert p.get(marked + "0", 0) == pytest.approx(
            np.sin((2 * r + 1) * theta) ** 2, abs=1e-12
        )
        assert sum(value for key, value in p.items() if key[-1] == "1") < 1e-12
    evidence = run_local_case(threat_case())
    assert evidence["estimates"]["grover3"]["estimate"] > 0.90


def test_extraction_health_and_no_physical_entropy_claim():
    assert von_neumann_extract([0, 0, 0, 1, 1, 0, 1, 1, 1]) == [0, 1]
    assert stream_health([0] * 256)["diagnostics_pass"] is False
    case = qrng_case()
    assert case.outputs["physical_entropy_claim"] is False
    assert case.outputs["production_random_bytes_emitted"] is False
    assert 0.45 < case.outputs["extracted_ones_fraction"] < 0.55
    raw = [int(bit) for bit in case.intermediate["ordered_raw_stream"]]
    assert case.intermediate["extracted_stream"] == "".join(
        map(str, von_neumann_extract(raw))
    )


def test_actual_pqc_library_no_secret_export():
    executable = shutil.which("openssl")
    if not executable:
        pytest.skip("Optional actual-library check requires OpenSSL ML-KEM / ML-DSA.")
    algorithms = subprocess.run(
        [executable, "list", "-public-key-algorithms"],
        capture_output=True,
        text=True,
        timeout=20,
    ).stdout
    if not all(name in algorithms for name in ("ML-KEM-768", "ML-DSA-65")):
        pytest.skip(
            "Installed OpenSSL provider lacks optional ML-KEM-768 or ML-DSA-65."
        )
    case = pqc_case()
    for key in (
        "shared_secrets_equal",
        "tampered_kem_implicit_rejection",
        "valid_signature_accepted",
        "altered_message_rejected",
        "temporary_directory_removed",
    ):
        assert case.outputs[key] is True
    for key, expected in case.reference.items():
        assert case.outputs[key] == expected
    assert case.outputs["private_keys_exported"] is False
    assert not case.experiments
    serialized = json.dumps(case.intermediate)
    assert "BEGIN PRIVATE KEY" not in serialized
    assert not any(
        "test-entropy" in row["arguments"] or "hexikme" in row["arguments"]
        for row in case.intermediate["operation_log"]
    )


def test_classical_aead_access_and_anchored_audit():
    pytest.importorskip("cryptography")
    case = privacy_case()
    for key in (
        "roundtrip_ok",
        "altered_ciphertext_rejected",
        "altered_aad_rejected",
        "valid_audit_accepted",
        "audit_tamper_rejected",
        "truncation_rejected_with_anchor",
    ):
        assert case.outputs[key] is True
    assert case.outputs["ciphertext_bytes"] - case.outputs["plaintext_bytes"] == 16
    assert case.intermediate["access_decisions"][-1]["allowed"] is False
    assert not case.experiments


def test_audit_wrong_key_reorder_tamper_and_truncation():
    key = b"public test key only"
    first = audit_record({"action": "read"}, 0, "0" * 64, key)
    second = audit_record({"action": "local"}, 1, first["tag"], key)
    records = [first, second]
    assert verify_audit(records, key, 2, second["tag"])
    assert not verify_audit(records, b"wrong", 2, second["tag"])
    assert not verify_audit(records[::-1], key, 2, second["tag"])
    assert not verify_audit(records[:-1], key, 2, second["tag"])
    changed = copy.deepcopy(records)
    changed[0]["payload"]["action"] = "altered"
    assert not verify_audit(changed, key, 2, second["tag"])


@pytest.mark.parametrize("bits", [[0, 2], [], ["0", "1"]])
def test_invalid_health_input(bits):
    with pytest.raises(ValueError):
        stream_health(bits)
