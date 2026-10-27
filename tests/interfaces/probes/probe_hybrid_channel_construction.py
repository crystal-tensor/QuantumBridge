# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Same public construction inputs; native channel buffers remain high-first."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.information import Operator, Kraus, SuperOp, Choi, DensityMatrix
from probe_annotated_hybrid_public_parity import raw_matrix, independent_modifiers, convert, native_index, public_index


def operators(targets, controls, state, order, matrix=None):
    from qiskit.circuit.library import UnitaryGate as QU
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI, PowerModifier as QP, ControlModifier as QC
    from qiskit.quantum_info import Operator as QO
    matrix = raw_matrix(targets) if matrix is None else matrix
    control = ("control", controls, state)
    extra = ("inverse", None, None) if "inverse" in order else ("power", .37 if "fractional" in order else 2, None)
    modifiers = [control] if order == "control" else [control, extra] if order.startswith("control_") else [extra, control]
    native_mods = [qb.InverseModifier() if kind == "inverse" else qb.PowerModifier(value) if kind == "power"
        else qb.ControlModifier(value, selected) for kind, value, selected in modifiers]
    public_mods = [QI() if kind == "inverse" else QP(value) if kind == "power"
        else QC(value, selected) for kind, value, selected in modifiers]
    native = Operator(qb.AnnotatedOperation(UnitaryGate(matrix), native_mods))
    public = QO(QA(QU(matrix), public_mods))
    hybrid = independent_modifiers(matrix, modifiers)
    np.testing.assert_allclose(native.data, hybrid, atol=8e-13, rtol=0)
    low = convert(hybrid, controls, targets, public_index)
    high = convert(hybrid, controls, targets, native_index)
    np.testing.assert_allclose(public.data, low, atol=8e-13, rtol=0)
    return native, public, high, low


def assert_channel_math(native, public, high, low):
    from qiskit.quantum_info import Kraus as QK, SuperOp as QS, Choi as QC, DensityMatrix as QD
    reference = QK(public)
    # The bare source call is the regression. No explicit selector prepares it.
    channel = Kraus(native)
    superop, choi = SuperOp(channel), Choi(channel)
    expected = np.kron(high.conj(), high)
    vector = high.reshape(-1, order="F")
    np.testing.assert_allclose(superop.data, expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(choi.data, np.outer(vector, vector.conj()), atol=2e-12, rtol=0)
    np.testing.assert_allclose(QS(reference).data, np.kron(low.conj(), low), atol=2e-12, rtol=0)
    public_vector = low.reshape(-1, order="F")
    np.testing.assert_allclose(QC(reference).data, np.outer(public_vector, public_vector.conj()), atol=2e-12, rtol=0)
    width, size = native.num_qubits, len(high)
    reverse = [int(format(i, f"0{width}b")[::-1], 2) for i in range(size)]
    density_order = [reverse[row] + size * reverse[column] for column in range(size) for row in range(size)]
    # Frame comparison is on outputs, not a pre-permutation of user inputs.
    np.testing.assert_allclose(superop.data, QS(reference).data[np.ix_(density_order, density_order)], atol=2e-12, rtol=0)
    np.testing.assert_allclose(choi.data, QC(reference).data[np.ix_(density_order, density_order)], atol=2e-12, rtol=0)
    state = np.arange(1, size + 1) + 1j * np.arange(size, 0, -1)
    state /= np.linalg.norm(state)
    rho = np.outer(state, state.conj())
    expected_rho = high @ rho @ high.conj().T
    np.testing.assert_allclose(channel.evolve(DensityMatrix(rho)).data, expected_rho, atol=2e-12, rtol=0)
    public_rho = rho[np.ix_(reverse, reverse)]
    evolved = QD(public_rho).evolve(reference).data
    np.testing.assert_allclose(expected_rho, evolved[np.ix_(reverse, reverse)], atol=2e-12, rtol=0)
    assert channel.__dict__["_public_matrix_basis"] == "native"
    assert native.__dict__["_public_matrix_basis"] == "hybrid"
    assert not np.shares_memory(channel.data[0], native.data)


@pytest.mark.parametrize("targets", [1, 2])
@pytest.mark.parametrize("controls", [1, 2])
@pytest.mark.parametrize("opened", [False, True])
@pytest.mark.parametrize("order", ["control", "inverse_control", "control_inverse",
    "fractional_control", "control_fractional", "integer_control", "control_integer"])
def test_public_hybrid_operator_channel_construction_has_complete_physical_map(targets, controls, opened, order):
    state = 0 if opened else (1 << controls) - 1
    native, public, high, low = operators(targets, controls, state, order)
    before = native.data.copy()
    assert_channel_math(native, public, high, low)
    np.testing.assert_array_equal(native.data, before)


def test_original_bare_hybrid_channel_diagnostic_is_a_public_construction():
    matrix = np.diag(np.exp(1j * np.array([.1, .3, .5, .7])))
    assert_channel_math(*operators(2, 1, 1, "control", matrix))


@pytest.mark.parametrize("method", ["copy", "adjoint", "conjugate", "transpose", "power"])
def test_derived_hybrid_operator_enters_bare_channel_without_double_conversion(method):
    owner, public, high, low = operators(2, 1, 0, "fractional_control")
    native = owner.power(2) if method == "power" else getattr(owner, method)()
    actual = public.power(2) if method == "power" else getattr(public, method)()
    def transform(matrix):
        return matrix @ matrix if method == "power" else matrix.conj().T if method == "adjoint" \
            else matrix.conj() if method == "conjugate" else matrix.T if method == "transpose" else matrix
    np.testing.assert_allclose(native.data, transform(owner.data), atol=3e-12, rtol=0)
    assert_channel_math(native, actual, transform(high), transform(low))


@pytest.mark.parametrize("representation", ["Kraus", "SuperOp", "Choi", "PTM", "Chi", "Stinespring"])
@pytest.mark.parametrize("method", ["copy", "adjoint", "conjugate", "transpose", "power"])
def test_actual_sdk_channel_representations_and_derivations(representation, method):
    import qiskit.quantum_info as qi
    import quantumbridge.information as native_info
    owner, public, high, _ = operators(2, 1, 0, "inverse_control")
    channel = getattr(native_info, representation)(owner)
    reference = getattr(qi, representation)(public)
    result = channel.power(2) if method == "power" else getattr(channel, method)()
    expected = reference.power(2) if method == "power" else getattr(reference, method)()
    reverse = [int(format(i, "03b")[::-1], 2) for i in range(8)]
    order = [reverse[row] + 8 * reverse[column] for column in range(8) for row in range(8)]
    np.testing.assert_allclose(SuperOp(result).data, qi.SuperOp(expected).data[np.ix_(order, order)], atol=4e-12, rtol=0)
    np.testing.assert_allclose(Choi(result).data, qi.Choi(expected).data[np.ix_(order, order)], atol=4e-12, rtol=0)
    matrix = high @ high if method == "power" else high.conj().T if method == "adjoint" \
        else high.conj() if method == "conjugate" else high.T if method == "transpose" else high
    np.testing.assert_allclose(SuperOp(result).data, np.kron(matrix.conj(), matrix), atol=4e-12, rtol=0)
    assert result.__dict__["_public_matrix_basis"] == "native"


def test_actual_sdk_legal_multi_kraus_composition_and_noncontiguous_evolution():
    from qiskit.quantum_info import Kraus as QK, SuperOp as QS, DensityMatrix as QD
    owner, public, high, _ = operators(1, 1, 0, "fractional_control")
    native, reference = Kraus(owner), QK(public)
    reverse = [0, 2, 1, 3]
    factors = [np.kron(np.diag([1, np.sqrt(.73)]), np.eye(2)),
        np.kron(np.array([[0, np.sqrt(.27)], [0, 0]]), np.eye(2))]
    public_factors = [factor[np.ix_(reverse, reverse)] for factor in factors]
    noise, public_noise = Kraus(factors), QK(public_factors)
    result, expected = native.compose(noise), reference.compose(public_noise)
    order = [reverse[row] + 4 * reverse[column] for column in range(4) for row in range(4)]
    full = sum(np.kron(factor.conj(), factor) for factor in factors) @ np.kron(high.conj(), high)
    np.testing.assert_allclose(SuperOp(result).data, full, atol=4e-12, rtol=0)
    np.testing.assert_allclose(full, QS(expected).data[np.ix_(order, order)], atol=4e-12, rtol=0)
    vectors = [(factor @ high).reshape(-1, order="F") for factor in factors]
    choi = sum(np.outer(vector, vector.conj()) for vector in vectors)
    np.testing.assert_allclose(Choi(result).data, choi, atol=4e-12, rtol=0)
    np.testing.assert_allclose(sum(factor.conj().T @ factor for factor in factors), np.eye(4), atol=4e-12, rtol=0)
    vector = np.arange(1, 17) + 1j * np.arange(16, 0, -1)
    vector /= np.linalg.norm(vector)
    rho = np.outer(vector, vector.conj())
    output = native.evolve(DensityMatrix(rho), qargs=(3, 1)).data
    axes = (3, 1, 0, 2)
    target = high @ vector.reshape((2,) * 4).transpose(axes).reshape(4, -1)
    target = target.reshape((2,) * 4).transpose(np.argsort(axes)).reshape(-1)
    np.testing.assert_allclose(output, np.outer(target, target.conj()), atol=4e-12, rtol=0)
    global_reverse = [int(format(i, "04b")[::-1], 2) for i in range(16)]
    # Bit reversal changes storage positions, not the physical wire labels.
    actual = QD(rho[np.ix_(global_reverse, global_reverse)]).evolve(reference, qargs=(3, 1)).data
    np.testing.assert_allclose(output, actual[np.ix_(global_reverse, global_reverse)], atol=4e-12, rtol=0)
