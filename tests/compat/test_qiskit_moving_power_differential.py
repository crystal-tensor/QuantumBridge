# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Installed public Qiskit is a test-only numeric oracle, never the runtime."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode

qiskit = pytest.importorskip("qiskit")
PublicParameter = pytest.importorskip("qiskit.circuit").Parameter
PublicOperator = pytest.importorskip("qiskit.quantum_info").Operator


@pytest.mark.parametrize("point", [0.37, 1.3, 2.8])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
@pytest.mark.parametrize("control", [None, 0, 1])
def test_moving_eigenbasis_complete_complex_matrix_matches_public_power(
    point, power, control
):
    p, native = qb.Parameter("p"), qb.Circuit(1)
    native.ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0)
    q, public = PublicParameter("p"), qiskit.QuantumCircuit(1)
    public.ry(-q, 0)
    public.rz(q * q + 0.4, 0)
    public.ry(q, 0)
    ng, pg = native.to_gate(), public.to_gate()
    if control is not None:
        ng, pg = ng.control(ctrl_state=control), pg.control(ctrl_state=control)
    ns, ps = qb.QuantumCircuit(ng.num_qubits), qiskit.QuantumCircuit(pg.num_qubits)
    ns.append(ng.power(power, annotated=True), range(ng.num_qubits))
    ps.append(pg.power(power, annotated=True), range(pg.num_qubits))
    node = QNode.from_circuit(
        ns, qb.PauliZ(ng.num_qubits - 1), diff_method="adjoint", max_diff=2
    )
    plan = node._construct((point,), {})
    actual = Operator(
        plan.circuit.bind(
            dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
        )
    ).data
    expected = PublicOperator(ps.assign_parameters({q: point})).data
    if control is not None:
        order = [0, 2, 1, 3]
        expected = expected[np.ix_(order, order)]
    np.testing.assert_allclose(actual, expected, atol=8e-12, rtol=0)


@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
@pytest.mark.parametrize("control", [None, 0, 1])
def test_two_parameter_entangling_power_and_controlled_phase_match_installed_public_sdk(
    power, control
):
    p, q = qb.ParameterVector("angles", 2)
    pp, pq = qiskit.circuit.ParameterVector("angles", 2)
    native = qb.Circuit(2).rx(p, 0).rz(q, 1).rxx(p * q, 0, 1)
    native.global_phase = 0.13 * p * q
    public = qiskit.QuantumCircuit(2)
    public.rx(pp, 0)
    public.rz(pq, 1)
    public.rxx(pp * pq, 0, 1)
    public.global_phase = 0.13 * pp * pq
    ng, pg = (
        native.to_gate().power(power, annotated=True),
        public.to_gate().power(power, annotated=True),
    )
    if control is not None:
        ng, pg = ng.control(ctrl_state=control), pg.control(ctrl_state=control)
    ns, ps = qb.QuantumCircuit(ng.num_qubits), qiskit.QuantumCircuit(pg.num_qubits)
    if control is not None:
        ns.h(0)
        ps.h(0)
    ns.append(ng, range(ng.num_qubits))
    ps.append(pg, range(pg.num_qubits))
    node = QNode.from_circuit(
        ns, qb.PauliZ(ng.num_qubits - 1), max_diff=2, diff_method="adjoint"
    )
    plan = node._construct((np.array([0.37, 0.82]),), {})
    actual = Operator(
        plan.circuit.bind(
            dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
        )
    ).data
    expected = PublicOperator(ps.assign_parameters({pp: 0.37, pq: 0.82})).data
    order = [
        int(f"{index:0{ng.num_qubits}b}"[::-1], 2) for index in range(len(expected))
    ]
    np.testing.assert_allclose(
        actual, expected[np.ix_(order, order)], atol=2e-11, rtol=0
    )
