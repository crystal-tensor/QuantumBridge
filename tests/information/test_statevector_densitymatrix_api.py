# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.information import DensityMatrix, Operator, Statevector


def test_statevector_from_int_tensor_expand_and_equivalence():
    zero = Statevector.from_int(0, 2)
    one = Statevector.from_label("1")

    assert zero.dim == 2
    assert zero.dims() == (2,)
    assert zero.tensor(one).equiv(Statevector.from_label("01"))
    assert zero.expand(one).equiv(Statevector.from_label("10"))
    assert Statevector([0, 1j]).equiv(1j * Statevector.from_label("1"))
    assert Statevector.from_label("01").reverse_qargs().equiv(Statevector.from_label("10"))


def test_statevector_subsystem_evolve_and_expectation_match_circuit():
    state = Statevector.from_label("00").evolve(Operator.from_label("X"), qargs=[1])
    expected = Statevector.from_circuit(Circuit(2).x(1))

    assert state.equiv(expected)
    assert state.probabilities_dict() == {"00": 0.0, "01": 1.0, "10": 0.0, "11": 0.0}
    assert abs(state.expectation_value(Operator.from_label("Z"), qargs=[0]) - 1.0) < 1e-12
    assert abs(state.expectation_value(Operator.from_label("Z"), qargs=[1]) + 1.0) < 1e-12


def test_statevector_measure_and_sample_memory_on_subset():
    bell = Statevector.from_circuit(Circuit(2).h(0).cx(0, 1))
    outcome, collapsed = bell.measure(qargs=[0], seed=5)

    assert outcome in {"0", "1"}
    assert collapsed.is_valid()
    assert abs(collapsed.probabilities([0])[outcome] - 1.0) < 1e-12
    assert Statevector.from_label("10").sample_memory(4, qargs=[0], seed=2) == ["1", "1", "1", "1"]


def test_density_matrix_subsystem_evolve_expectation_and_sampling():
    rho = DensityMatrix.from_statevector(Statevector.from_label("00")).evolve(Operator.from_label("X"), qargs=[0])

    assert rho.dim == (4, 4)
    assert rho.dims() == (2, 2)
    assert rho.probabilities_dict() == {"00": 0.0, "01": 0.0, "10": 1.0, "11": 0.0}
    assert abs(rho.expectation_value(Operator.from_label("Z"), qargs=[0]) + 1.0) < 1e-12
    assert rho.sample_counts(3, qargs=[0], seed=9) == {"1": 3}
    assert rho.sample_memory(3, qargs=[1], seed=9) == ["0", "0", "0"]


def test_density_matrix_tensor_expand_reverse_and_to_statevector():
    zero = DensityMatrix.from_statevector(Statevector.from_label("0"))
    one = DensityMatrix.from_statevector(Statevector.from_label("1"))

    np.testing.assert_allclose(zero.tensor(one).data, DensityMatrix.from_statevector(Statevector.from_label("01")).data)
    np.testing.assert_allclose(zero.expand(one).data, DensityMatrix.from_statevector(Statevector.from_label("10")).data)
    assert zero.tensor(one).reverse_qargs().probabilities_dict() == {"00": 0.0, "01": 0.0, "10": 1.0, "11": 0.0}
    assert one.to_statevector().equiv(Statevector.from_label("1"))
