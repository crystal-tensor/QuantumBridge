# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or IBM ecosystem packages was copied.

from pathlib import Path


def test_qiskit_stage8d_no_vendor_artifacts_staged_in_repo():
    forbidden = {
        "site-packages",
        ".venv",
        "venv",
    }
    repo = Path(__file__).resolve().parents[2]
    offenders = []
    for path in repo.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name in forbidden or path.suffix == ".whl" or path.name.endswith((".dist-info", ".egg-info")):
            if path.name == "quantumbridge_sdk.egg-info":
                continue
            offenders.append(path.relative_to(repo).as_posix())
    assert offenders == []


def test_qiskit_docs_do_not_claim_full_replacement_or_production_parity():
    repo = Path(__file__).resolve().parents[2]
    docs = [
        repo / "README.md",
        repo / "docs" / "architecture" / "qiskit_ecosystem_fusion_architecture_v0.1.md",
        repo / "docs" / "review" / "qiskit_ecosystem_fusion_risk_review_v0.1.md",
    ]
    for path in docs:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        assert "full qiskit replacement" not in text.replace("not a full qiskit replacement", "")
        assert "production parity" not in text.replace("no production parity", "").replace("not production parity", "")
