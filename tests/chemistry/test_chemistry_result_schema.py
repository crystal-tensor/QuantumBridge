from quantumbridge.chemistry import ChemistryResult


def test_chemistry_result_json():
    text = ChemistryResult(total_energy=-1.0, provenance={"mode": "Native Core"}).to_json()
    assert "total_energy" in text
    assert "Native Core" in text
