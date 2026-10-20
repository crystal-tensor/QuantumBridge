# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Execute documented examples, rather than accepting their printed claims."""

from importlib import import_module

import numpy as np
import pytest


def test_native_device_and_unified_failure_examples_execute():
    result = import_module("examples.native_device_derivatives").main()
    assert result["status"] == 0 and result["shots"] == 0 and result["tapes"] == 2
    np.testing.assert_allclose(result["hvp"], [-.4*np.cos(.3)], atol=1e-12)
    failed = import_module("examples.native_unified_resource_budget").main()
    assert failed["status"] == 3 and failed["live_bytes_after_failure"] == 0


def test_mps_budget_example_executes_without_dense_expansion(monkeypatch):
    from quantumbridge import StatevectorDevice, DensityMatrixDevice
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*a, **k): pytest.fail("MPS example used dense expansion")
    for cls, name in ((StatevectorDevice, "statevector"), (DensityMatrixDevice, "density_matrix"),
            (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix")):
        monkeypatch.setattr(cls, name, forbidden)
    result = import_module("examples.native_mps_hvp_budget").main()
    np.testing.assert_allclose([result["energy"], result["hvp"]], [np.cos(.3), -np.cos(.3)], atol=1e-10)
    assert result["status"] == 0 and result["shots"] == 0 and result["tapes"] == 8
    assert "mps_svd_allocator_peak" in result["unavailable"]


@pytest.mark.parametrize("framework,module", [("jax", "native_jax_hvp_status"), ("tensorflow", "native_tensorflow_hvp_status")])
def test_actual_framework_example_success_invalid_success(framework, module):
    pytest.importorskip(framework)
    result = import_module("examples."+module).main()
    assert [row["status"] for row in result] == [0, 1, 0]
