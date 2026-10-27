# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Native scalar bindings retain UUID semantics without owning a circuit."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

import quantumbridge as qb


@pytest.mark.parametrize("expression,expected", [
    (lambda p, q: p, 0.3), (lambda p, q: -p, -0.3),
    (lambda p, q: p+q, 1.1), (lambda p, q: p-q, -0.5),
    (lambda p, q: p*q, 0.24), (lambda p, q: p/q, 0.375),
    (lambda p, q: p**2, 0.09), (lambda p, q: p.sin(), np.sin(0.3)),
    (lambda p, q: p.cos(), np.cos(0.3)), (lambda p, q: q.exp(), np.exp(0.8)),
    (lambda p, q: q*q+0.4, 1.04), (lambda p, q: 0.17*p*q, 0.0408),
])
def test_native_frozen_binding_uses_existing_ast(expression, expected):
    from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
    p, q = qb.ParameterVector("angles", 2)
    binding = FrozenParameterBinding.create((p, q), (expression(p, q), p+q))
    result = binding.evaluate((0.3, 0.8))
    np.testing.assert_allclose(result, [expected, 1.1], atol=1e-14, rtol=0)
    assert binding.parameter_uuids == (str(p.uuid), str(q.uuid))
    with pytest.raises(FrozenInstanceError):
        binding.expressions = ()


def test_same_name_different_uuid_is_never_coalesced():
    from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
    p, other = qb.Parameter("p"), qb.Parameter("p")
    with pytest.raises(ValueError, match="identit"):
        FrozenParameterBinding.create((p, other), (p, other))


def test_frozen_binding_rejects_missing_duplicate_or_unbounded_inputs():
    from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
    p, q = qb.ParameterVector("angles", 2)
    for parameters, expressions in (((p,), (q,)), ((p, p), (p,)), ((p, q), (p,))):
        with pytest.raises(ValueError):
            FrozenParameterBinding.create(parameters, expressions)
    with pytest.raises(TypeError):
        FrozenParameterBinding.create(iter((p, q)), (p+q,))
