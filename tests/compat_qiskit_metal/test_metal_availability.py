# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_metal.component_adapter import ADAPTER as COMPONENT
from quantumbridge.compat.qiskit_metal.design_adapter import ADAPTER as DESIGN
from quantumbridge.compat.qiskit_metal.renderer_adapter import ADAPTER as RENDERER
from quantumbridge.compat.qiskit_metal.simulation_adapter import ADAPTER as SIMULATION


def test_metal_modules_or_clear_missing_dependency():
    if not DESIGN.dependency_available():
        with pytest.raises(ImportError, match="qiskit-metal"):
            DESIGN.passthrough_class("DesignPlanar")
        return
    assert DESIGN.list_public_api_inventory()
    assert COMPONENT.list_public_api_inventory()
    assert RENDERER.list_public_api_inventory()
    assert SIMULATION.list_public_api_inventory()