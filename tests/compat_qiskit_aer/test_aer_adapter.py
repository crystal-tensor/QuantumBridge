# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.


import numpy as np
import pytest

from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER as AER
from quantumbridge.compat.qiskit_aer.noise_adapter import ADAPTER as NOISE


def test_qiskit_aer_dependency_and_inventory_contract():
    assert isinstance(AER.dependency_available(), bool)
    assert AER.list_public_api_inventory()


def test_qiskit_aer_passthrough_or_clear_import_error():
    if AER.dependency_available():
        assert AER.passthrough_class("AerSimulator") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-aer"):
            AER.passthrough_class("AerSimulator")


def test_qiskit_aer_noise_schema_and_provenance():
    wrapped = NOISE.wrap_result({"noise_model": "smoke"})
    assert wrapped["schema"] == "quantumbridge.ecosystem.result.v0.1"
    assert wrapped["provenance"]["dependency_extra"] == "qiskit-aer"


def test_qiskit_aer_statevector_and_density_matrix_smoke_when_installed():
    if not AER.dependency_available():
        pytest.skip("qiskit-aer unavailable")
    qiskit = pytest.importorskip("qiskit")
    AerSimulator = AER.passthrough_class("AerSimulator")

    state_circuit = qiskit.QuantumCircuit(1)
    state_circuit.h(0)
    state_circuit.save_statevector()
    state_result = AerSimulator(method="statevector").run(state_circuit).result()
    assert np.asarray(state_result.get_statevector()).shape == (2,)

    density_circuit = qiskit.QuantumCircuit(1)
    density_circuit.x(0)
    density_circuit.save_density_matrix()
    density_result = AerSimulator(method="density_matrix").run(density_circuit).result()
    assert np.asarray(density_result.data(0)["density_matrix"]).shape == (2, 2)


def test_qiskit_aer_noise_model_availability_or_clear_import_error():
    if NOISE.dependency_available():
        assert NOISE.passthrough_class("NoiseModel") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-aer"):
            NOISE.passthrough_class("NoiseModel")


def test_qiskit_aer_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        AER.warn_unsupported("production noise parity")
