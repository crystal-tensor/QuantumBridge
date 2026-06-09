from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import MQT_COMPAT_WARNING, run_ddsim_like_statevector_native


def test_mqt_warnings_and_provenance_avoid_parity_claims():
    result = run_ddsim_like_statevector_native(Circuit(1).h(0))

    assert MQT_COMPAT_WARNING in result.warnings
    assert result.provenance["copied_upstream_source"] is False
    assert result.provenance["official_endorsement_claim"] is False
    assert result.provenance["full_replacement_claim"] is False
    assert result.provenance["production_parity_claim"] is False
