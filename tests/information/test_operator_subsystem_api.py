# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.information import Operator


def test_operator_dimensions_copy_and_global_phase_equivalence():
    x = Operator.from_label("X")

    assert x.dim == (2, 2)
    assert x.input_dims() == (2,)
    assert x.output_dims() == (2,)
    assert x.input_dims([0]) == (2,)
    assert x.copy() is not x
    assert x.copy().equiv(x)
    assert x.equiv((-1j) * x)
    assert x.reshape(num_qubits=1).equiv(x)


def test_operator_subsystem_compose_matches_circuit_wire_order():
    identity = Operator(np.eye(4, dtype=complex))
    x = Operator.from_label("X")

    on_wire_0 = identity.compose(x, qargs=[0])
    on_wire_1 = identity.compose(x, qargs=[1])

    assert on_wire_0.equiv(Operator.from_circuit(Circuit(2).x(0)))
    assert on_wire_1.equiv(Operator.from_circuit(Circuit(2).x(1)))
    assert on_wire_0.equiv(Operator.from_label("XI"))
    assert on_wire_1.equiv(Operator.from_label("IX"))


def test_operator_subsystem_front_compose_orders_multiplication():
    x = Operator.from_label("X")
    z = Operator.from_label("Z")

    x_after_z = z.compose(x)
    z_after_x = z.compose(x, front=True)

    np.testing.assert_allclose(x_after_z.to_matrix(), z.to_matrix() @ x.to_matrix())
    np.testing.assert_allclose(z_after_x.to_matrix(), x.to_matrix() @ z.to_matrix())


def test_operator_tensorpower_reverse_qargs_and_arithmetic():
    x = Operator.from_label("X")
    z = Operator.from_label("Z")

    assert x.tensorpower(2).equiv(Operator.from_label("XX"))
    assert (x ^ 2).equiv(Operator.from_label("XX"))
    assert Operator.from_label("XZ").reverse_qargs().equiv(Operator.from_label("ZX"))
    np.testing.assert_allclose((x + z - z).to_matrix(), x.to_matrix())
    np.testing.assert_allclose((2 * x / 2).to_matrix(), x.to_matrix())


def test_operator_to_instruction_executes_as_custom_unitary():
    x = Operator.from_label("X")
    instruction = x.to_instruction(name="native_x_matrix")
    circuit = Circuit(1).append(instruction, [0])

    assert instruction.name == "native_x_matrix"
    assert instruction.num_qubits == 1
    assert Operator.from_circuit(circuit).equiv(x)
