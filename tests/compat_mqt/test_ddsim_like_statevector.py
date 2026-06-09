from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import run_ddsim_like_statevector_native
import pytest


def test_ddsim_like_statevector_executes_bell_circuit():
    circuit = Circuit(2).h(0).cx(0, 1)

    result = run_ddsim_like_statevector_native(circuit)

    assert result.num_qubits == 2
    assert result.probabilities["00"] == pytest.approx(0.5)
    assert result.probabilities["11"] == pytest.approx(0.5)
    assert result.decision_diagram_metadata["decision_diagram_parity_claim"] is False
