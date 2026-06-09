from quantumbridge.compat.torchquantum.quantum_layer_native import quantum_layer_forward_native
from quantumbridge.compat.torchquantum.warnings import HIGH_RISK_ML_WARNING, TORCHQUANTUM_COMPAT_WARNING


def test_warnings_and_provenance_disclaim_full_replacement_and_production():
    result = quantum_layer_forward_native([0.1, 0.2], [0.0, 0.0, 0.0, 0.0])
    assert TORCHQUANTUM_COMPAT_WARNING in result.warnings
    assert HIGH_RISK_ML_WARNING in result.warnings
    assert result.provenance["copied_upstream_source"] is False
    assert result.provenance["full_replacement_claim"] is False
    assert result.provenance["production_parity_claim"] is False
    assert result.provenance["high_risk_decision_claim"] is False
