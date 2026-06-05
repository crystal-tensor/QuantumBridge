import pytest

from quantumbridge.compat.pennylane_full.operations_adapter import ADAPTER as OPERATIONS
from quantumbridge.compat.pennylane_full.qnode_adapter import ADAPTER as QNODE
from quantumbridge.compat.pennylane_full.templates_adapter import ADAPTER as TEMPLATES
from quantumbridge.compat.pennylane_full.device_adapter import ADAPTER as DEVICES
from quantumbridge.compat.pennylane_full.gradients_adapter import ADAPTER as GRADIENTS
from quantumbridge.compat.pennylane_full.measurement_adapter import ADAPTER as MEASUREMENTS
from quantumbridge.compat.pennylane_full.qchem_adapter import ADAPTER as QCHEM
from quantumbridge.compat.pennylane_full.transforms_adapter import ADAPTER as TRANSFORMS


def test_pennylane_full_dependency_and_inventory_contract():
    assert isinstance(OPERATIONS.dependency_available(), bool)
    assert OPERATIONS.list_public_api_inventory()


def test_pennylane_qnode_passthrough_or_clear_import_error():
    if QNODE.dependency_available():
        assert QNODE.passthrough_class("QNode") is not None
    else:
        with pytest.raises(ImportError, match="pennylane-full"):
            QNODE.passthrough_class("QNode")


def test_pennylane_template_schema_contract():
    schema = TEMPLATES.to_quantumbridge_schema({"template": "smoke"})
    assert schema["schema"] == "quantumbridge.ecosystem.object.v0.1"
    assert schema["provenance"]["adapter_package"] == "pennylane"


def test_pennylane_full_inventory_categories():
    for adapter in (OPERATIONS, MEASUREMENTS, QCHEM, TEMPLATES, GRADIENTS, DEVICES, TRANSFORMS):
        assert isinstance(adapter.dependency_available(), bool)
        assert adapter.list_public_api_inventory()


def test_pennylane_full_smoke_when_installed():
    if not QNODE.dependency_available():
        pytest.skip("pennylane unavailable")
    qml = pytest.importorskip("pennylane")
    dev = qml.device("default.qubit", wires=1)

    @qml.qnode(dev)
    def circuit():
        qml.PauliX(wires=0)
        return qml.probs(wires=0)

    probs = circuit()
    assert probs.shape[0] == 2


def test_pennylane_full_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        QNODE.warn_unsupported("full plugin ecosystem parity")
