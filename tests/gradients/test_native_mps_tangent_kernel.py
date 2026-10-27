# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual 100-wire MPS jets; only bounded local matrices may be materialized."""

import json
from pathlib import Path

import numpy as np
import pytest

from quantumbridge import DensityMatrixDevice, StatevectorDevice
from quantumbridge.diff.mps_tangent import MPSTangentJet
from quantumbridge.information import MatrixProductState
from quantumbridge.information.matrix_functions import unitary_power_mixed_jet
from quantumbridge.utils.math import gate_matrix

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


def forbid_dense(monkeypatch):
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import Operator

    def forbidden(*a, **k):
        pytest.fail("MPS jet tried to materialize a full state/density matrix")
    monkeypatch.setattr(MatrixProductState, "statevector", forbidden)
    monkeypatch.setattr(MatrixProductState, "reduced_density_matrix", forbidden)
    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    monkeypatch.setattr(DensityMatrixDevice, "density_matrix", forbidden)
    monkeypatch.setattr(Gate, "to_matrix", forbidden)
    monkeypatch.setattr(Operator, "__init__", forbidden)


def local_power_jet(point, power, left, right):
    p, q = point
    rx, rz = gate_matrix("rx", (p,)), gate_matrix("rz", (q,))
    drx = -0.5j * np.array([[0, 1], [1, 0]]) @ rx
    drz = -0.5j * np.diag([1, -1]) @ rz
    u = rz @ rx
    first = left[0] * rz @ drx + left[1] * drz @ rx
    other = right[0] * rz @ drx + right[1] * drz @ rx
    second = -0.25 * (left[0] * right[0] + left[1] * right[1]) * u
    second += (left[0] * right[1] + left[1] * right[0]) * drz @ drx
    return unitary_power_mixed_jet(u, first, other, second, power)


@pytest.mark.parametrize("active,target", [(0, 1), (0, 99), (99, 0), (98, 99)])
@pytest.mark.parametrize("column", [0, 1])
def test_100_wire_moving_projector_first_and_mixed_derivatives_without_dense_state(
    active, target, column, monkeypatch
):
    forbid_dense(monkeypatch)
    case = ORACLE["su2"][0]
    source = MatrixProductState.zero(100, max_bond_dim=4, max_memory_mb=2, cutoff=0.4)
    label = "I" * target + "Z" + "I" * (99 - target)
    observed = []
    for row in range(2):
        matrices = local_power_jet(ORACLE["point"], case["power"], np.eye(2)[row], np.eye(2)[column])
        jet = MPSTangentJet.from_state(source).applied(
            matrices[0], (active,), left=matrices[1], right=matrices[2], mixed=matrices[3]
        ).applied(gate_matrix("cx"), (active, target))
        observed.append(jet.moment(label))
        assert sum(part.tensor_bytes for part in (jet.primal, jet.left, jet.right, jet.mixed)) < 100_000
    observed = np.array(observed)
    np.testing.assert_allclose(observed[:, 0], case["value"], atol=8e-12, rtol=0)
    np.testing.assert_allclose(observed[:, 1], case["gradient"], atol=8e-11, rtol=0)
    np.testing.assert_allclose(observed[:, 2], case["gradient"][column], atol=8e-11, rtol=0)
    np.testing.assert_allclose(observed[:, 3], np.array(case["hessian"])[:, column], atol=2e-9, rtol=0)


@pytest.mark.parametrize("direction", [(0.4, -0.3), (0, 1), (1, 0), (-0.2, 0.7)])
@pytest.mark.parametrize("power_index", [1, 2])
def test_100_wire_streamed_directional_kernel_uses_no_parameter_hessian(direction, power_index, monkeypatch):
    forbid_dense(monkeypatch)
    # No parameter-Hessian method may be used to obtain this directional result.
    from quantumbridge.qml import QNode
    monkeypatch.setattr(QNode, "compute_hessian", lambda *a, **k: pytest.fail("HVP called full Hessian"))
    case, direction = ORACLE["su2"][power_index], np.array(direction)
    source = MatrixProductState.zero(100, max_bond_dim=4, max_memory_mb=2, cutoff=0)
    observed = []
    for row in range(2):
        matrices = local_power_jet(ORACLE["point"], case["power"], np.eye(2)[row], direction)
        jet = MPSTangentJet.from_state(source).applied(
            matrices[0], (99,), left=matrices[1], right=matrices[2], mixed=matrices[3]
        )
        observed.append(jet.moment("I" * 99 + "Z")[3])
    np.testing.assert_allclose(observed, np.array(case["hessian"]) @ direction, atol=2e-9, rtol=0)


@pytest.mark.parametrize("left,right", [((1, 0), (0, 1)), ((1, 0), (1, 0)), ((0, 1), (0, 1)), ((0.3, -0.2), (-0.4, 0.7))])
def test_multilayer_mixed_product_rule_includes_incoming_state_tangents(left, right, monkeypatch):
    forbid_dense(monkeypatch)
    p, q = 0.37, 0.82
    jet = MPSTangentJet.from_state(MatrixProductState.zero(100, max_bond_dim=4, cutoff=0))
    for index, (name, angle, generator) in enumerate([
        ("rx", p, np.array([[0, 1], [1, 0]])), ("ry", q, np.array([[0, -1j], [1j, 0]]))
    ]):
        u = gate_matrix(name, (angle,))
        derivative = -0.5j * generator @ u
        jet = jet.applied(u, (99,), left=left[index] * derivative,
                          right=right[index] * derivative,
                          mixed=-0.25 * left[index] * right[index] * u)
    value = np.cos(p) * np.cos(q)
    gradient = np.array([-np.sin(p) * np.cos(q), -np.cos(p) * np.sin(q)])
    hessian = np.array([[-value, np.sin(p) * np.sin(q)], [np.sin(p) * np.sin(q), -value]])
    np.testing.assert_allclose(jet.moment("I" * 99 + "Z"),
        [value, gradient @ left, gradient @ right, np.array(left) @ hessian @ right], atol=3e-12, rtol=0)


def test_global_phase_derivatives_cancel_between_bra_and_ket(monkeypatch):
    forbid_dense(monkeypatch)
    phase = np.exp(0.37j) * np.eye(2)
    jet = MPSTangentJet.from_state(MatrixProductState.zero(100)).applied(
        phase, (99,), left=1j * phase, right=1j * phase, mixed=-phase
    )
    np.testing.assert_allclose(jet.moment("I" * 99 + "Z"), [1, 0, 0, 0], atol=2e-14, rtol=0)


def test_jet_component_limit_precedes_every_chain_copy(monkeypatch):
    jet = MPSTangentJet.from_state(MatrixProductState.zero(100), max_components=1)
    jet = jet.applied(np.eye(2), (99,), left=np.eye(2), right=np.eye(2))
    monkeypatch.setattr(MatrixProductState, "copy", lambda *a, **k: pytest.fail("Expansion was not preflighted"))
    with pytest.raises(MemoryError, match="before expansion"):
        jet.applied(np.eye(2), (99,), left=np.eye(2), right=np.eye(2))
