# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Pure TF model gates. Passing these does not imply native QNode acceptance."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("tensorflow")
_spec = importlib.util.spec_from_file_location("tf_vjp_probe", Path(__file__).parent / "probes/probe_tf_differentiable_vjp.py")
_probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_probe)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("point", [(0.37, 0.82), (0.17, -0.42)])
@pytest.mark.parametrize("seed", ["point", "cotangent", "both"])
def test_explicit_vjp_parameter_cotangent_and_joint_variations(point, seed, traced):
    _probe.check_semantics(point=point, seed=seed, traced=traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("cotangent", [(1., 0.), (0., 1.), (0.7, -0.2), (-0.4, 0.8)])
def test_multioutput_cotangent_both_rows_contribute(cotangent, traced):
    _probe.check_semantics(cotangent=cotangent, traced=traced)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("kind", ["scalar", "vector", "multioutput"])
@pytest.mark.parametrize("mode", ["for", "rof", "tape_tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_pure_model_actual_mixed_modes(kind, mode, loss_kind, traced):
    _probe.check_loss(kind=kind, mode=mode, loss_kind=loss_kind, traced=traced)
