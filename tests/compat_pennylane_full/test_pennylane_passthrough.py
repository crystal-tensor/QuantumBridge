# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.contracts import UnsupportedCapability
from quantumbridge.compat.pennylane_full.dependency import dependency_available
from quantumbridge.compat.pennylane_full.passthrough import get_public_object, passthrough_class, safe_describe_object


def test_pennylane_passthrough_gets_object_or_unsupported():
    obj = get_public_object("pennylane", "QNode")
    if dependency_available():
        assert obj is not None
    else:
        assert isinstance(obj, UnsupportedCapability)


def test_pennylane_passthrough_class_and_description():
    obj = passthrough_class("pennylane", "QNode")
    description = safe_describe_object("pennylane", "QNode")
    if dependency_available():
        assert isinstance(description["callable"], bool)
        assert obj is not None
    else:
        assert isinstance(obj, UnsupportedCapability)
        assert description["supported"] is False
