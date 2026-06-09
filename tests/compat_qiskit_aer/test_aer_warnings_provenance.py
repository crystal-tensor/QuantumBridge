# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

from quantumbridge.compat.qiskit_aer import (
    create_bitflip_noise_model,
    run_noisy_qasm_simulator_native,
    run_statevector_simulator_native,
)
from quantumbridge.core import Circuit


def test_native_simulator_warnings_and_provenance_are_explicit():
    circuit = Circuit(1)
    circuit.h(0)

    result = run_statevector_simulator_native(circuit)

    assert any("not a full Qiskit Aer replacement" in item for item in result.warnings)
    assert result.provenance["official_endorsement"] is False
    assert result.provenance["source_code_copied"] is False
    assert result.provenance["upstream_source_copied"] is False
    assert result.metadata["qiskit_aer_parity_claim"] is False


def test_noise_warning_does_not_claim_aer_noise_parity():
    circuit = Circuit(1, 1)
    circuit.h(0).measure(0, 0)
    result = run_noisy_qasm_simulator_native(
        circuit, shots=16, seed=4, noise_model=create_bitflip_noise_model(0.25)
    )

    assert result.noise_model["qiskit_aer_noise_model_parity"] is False
    assert any("does not provide Qiskit Aer noise-model parity" in item for item in result.warnings)
