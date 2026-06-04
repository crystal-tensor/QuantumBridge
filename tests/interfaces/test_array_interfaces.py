# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import importlib.util

import numpy as np
import pytest

from quantumbridge.interfaces import to_jax, to_numpy, to_torch


def test_numpy_interface():
    arr = to_numpy([1, 2, 3])
    assert isinstance(arr, np.ndarray)
    assert arr.tolist() == [1.0, 2.0, 3.0]


def test_torch_interface_if_available():
    torch = pytest.importorskip("torch")
    tensor = to_torch([1.0, 2.0], dtype=torch.float64)
    assert tensor.dtype == torch.float64
    assert tensor.tolist() == [1.0, 2.0]


def test_jax_interface_optional_behavior():
    if importlib.util.find_spec("jax") is None:
        with pytest.raises(ImportError):
            to_jax([1.0])
    else:
        assert list(to_jax([1.0, 2.0])) == [1.0, 2.0]

