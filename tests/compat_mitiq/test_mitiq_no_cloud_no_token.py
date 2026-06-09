from quantumbridge.compat.mitiq import (
    bell_circuit,
    run_readout_mitigation_native,
    run_zne_native,
)


def test_native_mitiq_workflows_do_not_access_cloud_tokens_or_hardware():
    for result in [
        run_zne_native(bell_circuit(), observable="ZZ", shots=64, seed=2),
        run_readout_mitigation_native(bell_circuit(), shots=64, seed=2),
    ]:
        assert result.metadata["cloud_access"] is False
        assert result.metadata["token_read"] is False
        assert result.metadata["hardware_access"] is False
        assert result.provenance["cloud_access"] is False
        assert result.provenance["token_read"] is False
        assert result.provenance["hardware_access"] is False
