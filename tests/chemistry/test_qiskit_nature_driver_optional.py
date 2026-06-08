import pytest

from quantumbridge.chemistry.adapters import QiskitNatureDriverAdapter


def test_qiskit_nature_driver_optional():
    pytest.importorskip("qiskit_nature", reason="optional dependency unavailable: qiskit-nature")
    result = QiskitNatureDriverAdapter().run()
    assert result.provenance["dependency"] == "qiskit-nature"
