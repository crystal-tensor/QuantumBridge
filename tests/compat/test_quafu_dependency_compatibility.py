# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from importlib.metadata import PackageNotFoundError, version

import pytest


def test_quafu_dependency_compatibility_smoke():
    pytest.importorskip("quafu", reason="optional dependency unavailable: pyquafu")

    import numpy as np

    try:
        pyquafu_version = version("pyquafu")
    except PackageNotFoundError:
        pytest.skip("optional dependency unavailable: pyquafu distribution metadata")

    if int(np.__version__.split(".", 1)[0]) >= 2:
        pytest.skip("pyquafu 0.4.5 requires numpy<2; current environment is not quafu-compatible")

    assert pyquafu_version == "0.4.5"
