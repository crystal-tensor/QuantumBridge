from quantumbridge.compat.qiskit_nature import (
    MATERIAL_WARNING,
    NATIVE_CHEMISTRY_WARNING,
    QISKIT_NATURE_WARNING,
    run_h2_native,
)


def test_chemistry_warnings_and_provenance_boundaries():
    result = run_h2_native()

    assert QISKIT_NATURE_WARNING in result.warnings
    assert NATIVE_CHEMISTRY_WARNING in result.warnings
    assert MATERIAL_WARNING in result.warnings
    assert result.production_ready is False
    assert result.provenance["official_endorsement"] is False
    assert result.provenance["source_code_copied"] is False
    assert result.provenance["upstream_source_copied"] is False
    assert result.provenance["ibm_branding_copied"] is False
    assert result.metadata["materials_band_gap"] is False
