# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.compat.qiskit_core.quantum_info_adapter import get_native_quantum_info_symbols, native_class
from quantumbridge.information import DensityMatrix, Operator, Statevector
from quantumbridge.operators import PauliList, SparsePauliOp, SparsePauliOperator


def test_native_quantum_info_symbols_are_callable():
    symbols = get_native_quantum_info_symbols()
    assert symbols["Statevector"] is Statevector
    assert symbols["DensityMatrix"] is DensityMatrix
    assert symbols["Operator"] is Operator
    assert symbols["SparsePauliOp"] is SparsePauliOperator
    assert native_class("PauliList") is PauliList


def test_statevector_density_matrix_operator_core_methods():
    plus = Statevector.from_label("0").evolve(Operator.from_label("X")).evolve(Circuit(1).h(0))
    assert plus.num_qubits == 1
    assert plus.is_valid()
    assert set(plus.probabilities()) == {"0", "1"}
    assert abs(plus.expectation_value(Operator.from_label("Z"))) < 1e-12

    rho = DensityMatrix.from_statevector(plus)
    assert rho.is_valid()
    assert abs(rho.purity() - 1.0) < 1e-12
    assert abs(rho.evolve(Operator.from_label("X")).expectation_value(Operator.from_label("X")) + 1.0) < 1e-12

    h = Operator.from_circuit(Circuit(1).h(0))
    assert h.is_unitary()
    np.testing.assert_allclose(h.power(2).to_matrix(), np.eye(2), atol=1e-12)
    np.testing.assert_allclose(h.adjoint().compose(h).to_matrix(), np.eye(2), atol=1e-12)


def test_pauli_list_sparse_pauli_op_core_methods():
    paulis = PauliList(["XI", "ZZ"])
    assert paulis.size == 2
    assert paulis.num_qubits == 2
    assert paulis.to_labels() == ["XI", "ZZ"]
    assert len(paulis.to_matrix()) == 2
    assert paulis.compose(PauliList(["XI"])).to_labels() == ["II", "YZ"]

    op = SparsePauliOp.from_list([("Z", 1), ("Z", -1), ("X", 0.5)]).simplify()
    assert op.to_list() == [("X", 0.5 + 0j)]
    np.testing.assert_allclose(op.matrix(), np.array([[0, 0.5], [0.5, 0]], dtype=complex))

    dense = SparsePauliOperator.from_operator(Operator.from_label("Z"))
    assert dense.simplify().to_list() == [("Z", 1 + 0j)]
