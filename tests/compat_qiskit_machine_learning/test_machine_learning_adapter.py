import pytest

from quantumbridge.compat.qiskit_machine_learning.kernel_adapter import ADAPTER as KERNEL
from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER as QNN
from quantumbridge.compat.qiskit_machine_learning.classifier_adapter import ADAPTER as CLASSIFIER
from quantumbridge.compat.qiskit_machine_learning.torch_connector_adapter import ADAPTER as TORCH_CONNECTOR


def test_qiskit_machine_learning_dependency_and_inventory_contract():
    assert isinstance(QNN.dependency_available(), bool)
    assert QNN.list_public_api_inventory()


def test_qiskit_machine_learning_passthrough_or_clear_import_error():
    if QNN.dependency_available():
        inventory_names = {record.public_api for record in QNN.list_public_api_inventory()}
        assert inventory_names
    else:
        with pytest.raises(ImportError, match="qiskit-machine-learning"):
            QNN.passthrough_class("EstimatorQNN")


def test_qiskit_machine_learning_result_wrapper():
    wrapped = KERNEL.wrap_result({"kernel": "smoke"})
    assert wrapped["provenance"]["adapter_package"] == "qiskit-machine-learning"
    assert wrapped["provenance"]["dependency_extra"] == "qiskit-machine-learning"


def test_qiskit_machine_learning_named_availability_or_clear_import_error():
    if QNN.dependency_available():
        assert QNN.passthrough_class("EstimatorQNN") is not None
        assert QNN.passthrough_class("SamplerQNN") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-machine-learning"):
            QNN.passthrough_class("EstimatorQNN")

    if KERNEL.dependency_available():
        assert KERNEL.list_public_api_inventory()
    else:
        with pytest.raises(ImportError, match="qiskit-machine-learning"):
            KERNEL.passthrough_class("FidelityQuantumKernel")

    if CLASSIFIER.dependency_available():
        assert CLASSIFIER.list_public_api_inventory()
    else:
        with pytest.raises(ImportError, match="qiskit-machine-learning"):
            CLASSIFIER.passthrough_class("VQC")


def test_qiskit_machine_learning_torch_connector_lane():
    if TORCH_CONNECTOR.dependency_available():
        assert TORCH_CONNECTOR.list_public_api_inventory()
    else:
        with pytest.raises(ImportError, match="qiskit-machine-learning"):
            TORCH_CONNECTOR.passthrough_class("TorchConnector")


def test_qiskit_machine_learning_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        QNN.warn_unsupported("production ML training")
