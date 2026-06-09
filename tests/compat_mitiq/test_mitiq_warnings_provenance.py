from quantumbridge.compat.mitiq import (
    MITIQ_WARNING,
    NATIVE_READOUT_WARNING,
    NATIVE_ZNE_WARNING,
    bell_circuit,
    run_readout_mitigation_native,
    run_zne_native,
)


def test_mitiq_warnings_and_provenance_mark_stage9g_boundaries():
    zne = run_zne_native(bell_circuit(), observable="ZZ", shots=64, seed=4)
    readout = run_readout_mitigation_native(bell_circuit(), shots=64, seed=4)

    assert MITIQ_WARNING in zne.warnings
    assert NATIVE_ZNE_WARNING in zne.warnings
    assert NATIVE_READOUT_WARNING in readout.warnings
    for result in [zne, readout]:
        assert result.provenance["stage"] == "9G"
        assert result.provenance["official_endorsement"] is False
        assert result.provenance["source_code_copied"] is False
        assert result.provenance["upstream_source_copied"] is False
        assert result.production_ready is False
