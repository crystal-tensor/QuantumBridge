# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Closed channel origins survive existing copies and representation paths."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Kraus, SuperOp, Choi, PTM, Chi, Stinespring, DensityMatrix


REPRESENTATIONS = (Kraus, SuperOp, Choi, PTM, Chi, Stinespring)


def source(width=2):
    rng = np.random.default_rng(12421 + width)
    size = 1 << width
    matrix, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))
    circuit = qb.Circuit(width)
    circuit.unitary(matrix, range(width))
    circuit.global_phase = .13
    return circuit, np.exp(.13j) * matrix


def public_matrix(matrix):
    width = matrix.shape[0].bit_length() - 1
    order = [int(format(i, f"0{width}b")[::-1], 2) for i in range(len(matrix))]
    return matrix[np.ix_(order, order)]


@pytest.mark.parametrize("representation", REPRESENTATIONS)
@pytest.mark.parametrize("raw", [False, True])
def test_channel_literal_and_circuit_origins_have_distinct_public_conversions(representation, raw):
    circuit, matrix = source()
    channel = representation(Kraus([matrix]) if raw else circuit)
    expected = np.kron(matrix.conj(), matrix)
    np.testing.assert_allclose(channel.to_superop().data, expected, atol=3e-13, rtol=0)
    operator = channel.to_operator()
    converted = operator.as_qiskit_operator().data
    target = matrix if raw else public_matrix(matrix)
    np.testing.assert_allclose(np.kron(converted.conj(), converted),
        np.kron(target.conj(), target), atol=3e-13, rtol=0)
    assert operator.__dict__.get("_public_matrix_basis") == (None if raw else "native")
    assert "_arithmetic_convention" not in operator.__dict__


@pytest.mark.parametrize("method", ["to_superop", "to_choi", "to_ptm", "to_chi", "to_stinespring", "to_kraus"])
def test_channel_cross_representation_roundtrips_preserve_known_native_origin(method):
    circuit, matrix = source()
    channel = Kraus(circuit)
    for conversion in ("to_choi", "to_ptm", "to_stinespring", method, "to_chi", "to_superop", "to_kraus"):
        channel = getattr(channel, conversion)()
        assert channel.__dict__["_public_matrix_basis"] == "native"
    operator = channel.to_operator().as_qiskit_operator()
    target = public_matrix(matrix)
    np.testing.assert_allclose(np.kron(operator.data.conj(), operator.data),
        np.kron(target.conj(), target), atol=6e-13, rtol=0)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
@pytest.mark.parametrize("method", ["copy", "adjoint", "conjugate", "transpose", "power"])
def test_channel_derivation_origin_and_full_complex_map(representation, method):
    circuit, matrix = source()
    channel = representation(circuit)
    result = channel.power(2) if method == "power" else getattr(channel, method)()
    target = matrix @ matrix if method == "power" else matrix.conj().T if method == "adjoint" \
        else matrix.conj() if method == "conjugate" else matrix.T if method == "transpose" else matrix
    assert result.__dict__["_public_matrix_basis"] == "native"
    np.testing.assert_allclose(result.to_superop().data,
        np.kron(target.conj(), target), atol=4e-13, rtol=0)
    converted = result.to_operator().as_qiskit_operator().data
    target = public_matrix(target)
    np.testing.assert_allclose(np.kron(converted.conj(), converted),
        np.kron(target.conj(), target), atol=5e-13, rtol=0)


def test_native_channel_snapshot_is_independent_of_mutated_source_and_later_copies():
    circuit, matrix = source()
    channel = Kraus(circuit)
    operator = channel.to_operator()
    public = operator.as_qiskit_operator()
    circuit.global_phase = .8
    circuit.x(0)
    np.testing.assert_allclose(channel.data[0], matrix, atol=2e-14, rtol=0)
    np.testing.assert_array_equal(operator.data, channel.data[0])
    assert not np.shares_memory(operator.data, channel.data[0])
    channel.data[0][:] = np.eye(4)
    np.testing.assert_allclose(operator.data, matrix, atol=2e-14, rtol=0)
    np.testing.assert_allclose(public.data, public_matrix(matrix), atol=2e-14, rtol=0)


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_multi_kraus_nonunitary_channel_retains_domain_refusal(representation):
    raw = Kraus([np.diag([1., np.sqrt(.7)]), np.array([[0, np.sqrt(.3)], [0, 0]])])
    channel = representation(raw)
    np.testing.assert_allclose(channel.to_superop().data,
        sum(np.kron(k.conj(), k) for k in raw.data), atol=2e-14, rtol=0)
    with pytest.raises(ValueError):channel.to_operator()
    assert channel.__dict__.get("_public_matrix_basis") is None


def test_mixed_channel_sources_cannot_launder_a_native_origin():
    from quantumbridge.core.classical import UnsupportedFeature
    circuit, matrix = source()
    result = Kraus(circuit).compose(Kraus([matrix]))
    assert result.__dict__["_public_matrix_basis"] == "unresolved"
    with pytest.raises(UnsupportedFeature):result.to_operator().as_qiskit_operator()


def test_noncontiguous_native_channel_evolution_has_independent_tensor_oracle():
    circuit, matrix = source()
    vector = np.arange(1, 17) + 1j * np.arange(16, 0, -1)
    vector /= np.linalg.norm(vector)
    wires = (3, 1)
    axes = wires + tuple(i for i in range(4) if i not in wires)
    transformed = matrix @ vector.reshape((2,) * 4).transpose(axes).reshape(4, -1)
    expected = transformed.reshape((2,) * 4).transpose(np.argsort(axes)).reshape(-1)
    result = Kraus(circuit).evolve(DensityMatrix(np.outer(vector, vector.conj())), qargs=wires)
    np.testing.assert_allclose(result.data, np.outer(expected, expected.conj()), atol=3e-14, rtol=0)
