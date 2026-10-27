# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Whole-map and ownership checks for the existing hybrid channel boundary."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.information import Operator, Kraus, SuperOp, Choi, PTM, Chi, Stinespring, DensityMatrix


REPRESENTATIONS = (Kraus, SuperOp, Choi, PTM, Chi, Stinespring)


def source():
    rng = np.random.default_rng(1774)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    matrix *= np.exp(.23j)
    owner = Operator(qb.AnnotatedOperation(UnitaryGate(matrix), [qb.InverseModifier(), qb.ControlModifier(1, 0)]))
    # Control prefix is native; reverse only the two literal target bits.
    order = [control * 4 + int(format(target, "02b")[::-1], 2) for control in range(2) for target in range(4)]
    high = np.eye(8, dtype=complex)
    high[:4, :4] = matrix.conj().T
    high = high[np.ix_(order, order)]
    return owner, high


def full_map(matrices):
    return sum(np.kron(matrix.conj(), matrix) for matrix in matrices)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
@pytest.mark.parametrize("derivation", ["copy", "adjoint", "conjugate", "transpose", "power"])
def test_hybrid_constructor_and_derivations_preserve_entire_channel(representation, derivation):
    owner, high = source()
    before = owner.data.copy()
    channel = representation(owner)
    result = channel.power(2) if derivation == "power" else getattr(channel, derivation)()
    expected = high @ high if derivation == "power" else high.conj().T if derivation == "adjoint" \
        else high.conj() if derivation == "conjugate" else high.T if derivation == "transpose" else high
    np.testing.assert_allclose(result.to_superop().data, full_map([expected]), atol=3e-12, rtol=0)
    vector = expected.reshape(-1, order="F")
    np.testing.assert_allclose(result.to_choi().data, np.outer(vector, vector.conj()), atol=3e-12, rtol=0)
    for item in (channel, result):assert item.__dict__["_public_matrix_basis"] == "native"
    assert owner.__dict__["_public_matrix_basis"] == "hybrid"
    np.testing.assert_array_equal(owner.data, before)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_hybrid_channel_conversion_chain_normalizes_once(representation):
    owner, high = source()
    channel = representation(owner)
    for method in ("to_choi", "to_ptm", "to_chi", "to_stinespring", "to_superop", "to_kraus"):
        channel = getattr(channel, method)()
        assert channel.__dict__["_public_matrix_basis"] == "native"
        np.testing.assert_allclose(channel.to_superop().data, full_map([high]), atol=4e-12, rtol=0)
    reverse = [int(format(i, "03b")[::-1], 2) for i in range(8)]
    public = channel.to_operator().as_qiskit_operator().data
    np.testing.assert_allclose(full_map([public]), full_map([high[np.ix_(reverse, reverse)]]), atol=4e-12, rtol=0)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_hybrid_channel_noncontiguous_evolution_has_tensor_oracle(representation):
    owner, matrix = source()
    vector = np.arange(1, 33) + 1j * np.arange(32, 0, -1)
    vector /= np.linalg.norm(vector)
    wires = (4, 1, 3)
    axes = wires + (0, 2)
    expected = matrix @ vector.reshape((2,) * 5).transpose(axes).reshape(8, -1)
    expected = expected.reshape((2,) * 5).transpose(np.argsort(axes)).reshape(-1)
    evolved = representation(owner).evolve(DensityMatrix(np.outer(vector, vector.conj())), qargs=wires)
    np.testing.assert_allclose(evolved.data, np.outer(expected, expected.conj()), atol=3e-12, rtol=0)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_legal_nonunitary_map_composed_with_hybrid_channel_preserves_full_map(representation):
    owner, high = source()
    factors = [np.kron(np.diag([1, np.sqrt(.63)]), np.eye(4)),
        np.kron(np.array([[0, np.sqrt(.37)], [0, 0]]), np.eye(4))]
    noise = Kraus(factors)
    result = representation(owner).compose(representation(noise))
    expected = full_map(factors) @ full_map([high])
    np.testing.assert_allclose(result.to_superop().data, expected, atol=4e-12, rtol=0)
    vectors = [(factor @ high).reshape(-1, order="F") for factor in factors]
    np.testing.assert_allclose(result.to_choi().data,
        sum(np.outer(vector, vector.conj()) for vector in vectors), atol=4e-12, rtol=0)
    np.testing.assert_allclose(sum(factor.conj().T @ factor for factor in factors), np.eye(8), atol=4e-12, rtol=0)
    assert result.__dict__["_public_matrix_basis"] == "unresolved"
    with pytest.raises(ValueError):result.to_operator()
    vector = np.arange(1, 9) + 1j * np.arange(8, 0, -1)
    vector /= np.linalg.norm(vector)
    rho = np.outer(vector, vector.conj())
    target = sum(factor @ high @ rho @ high.conj().T @ factor.conj().T for factor in factors)
    np.testing.assert_allclose(result.evolve(DensityMatrix(rho)).data, target, atol=4e-12, rtol=0)
    np.testing.assert_allclose(np.trace(target), np.trace(rho), atol=4e-12, rtol=0)


def test_literal_native_and_hybrid_channels_keep_distinct_source_meanings():
    owner, high = source()
    raw = Operator(owner.data.copy())
    native = Operator(qb.Circuit(3).unitary(high, range(3)))
    for value, expected, origin in ((raw, raw.data, None), (native, high, "native"), (owner, high, "native")):
        channel = Kraus(value)
        np.testing.assert_array_equal(channel.data[0], expected)
        assert channel.__dict__.get("_public_matrix_basis") == origin
        assert not np.shares_memory(channel.data[0], value.data)
    channel = Kraus(owner)
    owner.data[:] = np.eye(8)
    np.testing.assert_array_equal(channel.data[0], high)


def test_nested_generalized_hybrid_factors_do_not_invent_a_common_origin():
    from quantumbridge.core.classical import UnsupportedFeature
    owner, _ = source()
    with pytest.raises(UnsupportedFeature):Stinespring((owner, owner))
