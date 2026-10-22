# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real standard objects, independently checked quantum math and return ABI."""

import numpy as np
import pytest

import quantumbridge as qb
import quantumbridge.circuit_library as library
from quantumbridge.information import Operator


CONSTRUCTORS = [
    ("RXGate", (.37,)), ("RYGate", (.37,)), ("RZGate", (.37,)),
    ("PhaseGate", (.37,)), ("UGate", (.37, .19, -.23)), ("HGate", ()),
    ("XGate", ()), ("YGate", ()), ("ZGate", ()), ("CXGate", ()),
    ("CZGate", ()), ("SwapGate", ()),
]


def standard(name, *args, **kwargs):
    kind = getattr(library, name, None)
    assert kind is not None, "Missing a real dedicated native standard Gate constructor"
    return kind(*args, **kwargs)


def rotation(axis, angle):
    if axis == "RZGate": return np.diag([np.exp(-.5j*angle), np.exp(.5j*angle)])
    c, s = np.cos(angle/2), np.sin(angle/2)
    return np.array([[c, -1j*s], [-1j*s, c]]) if axis == "RXGate" else np.array([[c, -s], [s, c]])


def independent(name, params):
    if name in {"RXGate", "RYGate", "RZGate"}: return rotation(name, params[0])
    if name == "PhaseGate": return np.diag([1, np.exp(1j*params[0])])
    if name == "UGate":
        theta, phi, lam = params
        c, s = np.cos(theta/2), np.sin(theta/2)
        return np.array([[c, -np.exp(1j*lam)*s], [np.exp(1j*phi)*s, np.exp(1j*(phi+lam))*c]])
    if name == "HGate": return np.array([[1, 1], [1, -1]])/np.sqrt(2)
    if name == "XGate": return np.array([[0, 1], [1, 0]])
    if name == "YGate": return np.array([[0, -1j], [1j, 0]])
    if name == "ZGate": return np.diag([1, -1])
    if name == "CXGate": return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    if name == "CZGate": return np.diag([1, 1, 1, -1])
    return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])


@pytest.mark.parametrize("name,args", CONSTRUCTORS)
def test_twelve_real_standard_objects_execute_independent_full_complex_matrices(name, args):
    gate = standard(name, *args)
    assert gate.base_class is getattr(library, name)
    assert gate.num_clbits == 0
    np.testing.assert_allclose(Operator(gate).data, independent(name, args), atol=2e-13, rtol=0)
    circuit = qb.Circuit(gate.num_qubits).append(gate, range(gate.num_qubits))
    np.testing.assert_allclose(Operator(circuit).data, independent(name, args), atol=2e-13, rtol=0)


@pytest.mark.parametrize("name", ["RXGate", "RYGate", "RZGate"])
@pytest.mark.parametrize("method", ["inverse", "power", "control"])
@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_rotation_return_types_and_all_four_annotated_argument_choices(name, method, mode):
    source = standard(name, .37)
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    args = () if method == "inverse" else (2,) if method == "power" else (1,)
    result = getattr(source, method)(*args, **kwargs)
    expected_name = "C"+name if method == "control" else name
    assert type(result).__name__ == expected_name
    assert result.base_class is getattr(library, expected_name)
    if method == "control":
        expected = np.eye(4, dtype=complex)
        expected[2:, 2:] = rotation(name, .37)
    else: expected = rotation(name, -.37 if method == "inverse" else .74)
    np.testing.assert_allclose(Operator(result).data, expected, atol=2e-13, rtol=0)


@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_numeric_generic_power_has_a_real_unitary_return_object(mode):
    source = qb.Circuit(1).rx(.37, 0).to_gate()
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    result = source.power(2, **kwargs)
    assert isinstance(result, qb.AnnotatedOperation) is (mode is True)
    if mode is not True:
        assert type(result).__name__ == "UnitaryGate"
        assert result.base_class is library.UnitaryGate
    np.testing.assert_allclose(Operator(result).data, rotation("RXGate", .74), atol=2e-13, rtol=0)


@pytest.mark.parametrize("mode", ["omitted", None, False, True])
def test_generic_control_defaults_remain_correct_without_a_fake_compatibility_fix(mode):
    gate = qb.Circuit(1).rx(.37, 0).to_gate()
    kwargs = {} if mode == "omitted" else {"annotated": mode}
    result = gate.control(1, **kwargs)
    assert isinstance(result, qb.AnnotatedOperation) is (mode is True)


@pytest.mark.parametrize("name", ["RXGate", "RYGate", "RZGate", "PhaseGate"])
def test_parameter_views_copies_uuid_and_repeated_binding_have_independent_lifetimes(name):
    p, q = qb.ParameterVector("v", 2)[1], qb.Parameter("q")
    gate = standard(name, p)
    copied = gate.copy()
    view = copied.params
    view[0] = 2*q+q.sin()
    bound = copied.assign_parameters({q: .3})
    bound.params[0] = .8
    assert gate.params == [p] and copied.params[0].parameters == {q}
    assert type(bound) is type(gate) and type(copied) is type(gate)
    np.testing.assert_allclose(Operator(bound).data, independent(name, [.8]), atol=2e-13, rtol=0)
    assert view == copied.params


@pytest.mark.parametrize("name", ["HGate", "XGate", "YGate", "ZGate", "CXGate", "CZGate", "SwapGate"])
def test_frozen_defaults_expose_mutability_but_only_owned_mutable_copy_can_change(name):
    gate = standard(name)
    assert gate.mutable is False
    with pytest.raises(TypeError): gate.label = "changed"
    with pytest.raises(TypeError): gate.params = []
    copied = gate.to_mutable()
    copied.label = "owned"
    assert copied.mutable and gate.label is None
    assert not standard(name).mutable
    np.testing.assert_allclose(Operator(copied).data, Operator(gate).data, atol=2e-13, rtol=0)


@pytest.mark.parametrize("name", ["RXGate", "RYGate", "RZGate"])
def test_controlled_standard_parameters_update_base_phase_and_open_control(name):
    gate = standard(name, qb.Parameter("p")).control(1, ctrl_state=0)
    gate.params[0] = .7
    assert gate.base_gate.params == [.7]
    expected = np.eye(4, dtype=complex)
    expected[:2, :2] = rotation(name, .7)
    np.testing.assert_allclose(Operator(gate).data, expected, atol=3e-13, rtol=0)
    restored = gate.assign_parameters({})
    assert type(restored) is type(gate) and restored.ctrl_state == 0


@pytest.mark.parametrize("value", [1j, np.complex128(.2), float("inf"), float("nan"), "bad", None])
def test_standard_invalid_parameter_changes_are_atomic(value):
    gate = standard("RYGate", .3)
    before = Operator(gate).data.copy()
    with pytest.raises((TypeError, ValueError)): gate.params[0] = value
    assert gate.params == [.3]
    np.testing.assert_array_equal(Operator(gate).data, before)


def test_unitary_matrix_parameters_are_owned_live_validated_and_copy_isolated():
    matrix = rotation("RXGate", .3)
    gate = standard("UnitaryGate", matrix)
    matrix[:] = 0
    copied = gate.copy()
    copied.params[0] = rotation("RYGate", .8)
    np.testing.assert_allclose(Operator(gate).data, rotation("RXGate", .3), atol=2e-13, rtol=0)
    np.testing.assert_allclose(Operator(copied).data, rotation("RYGate", .8), atol=2e-13, rtol=0)
    with pytest.raises(ValueError): copied.params[0] = np.zeros((2, 2))
    np.testing.assert_allclose(Operator(copied).data, rotation("RYGate", .8), atol=2e-13, rtol=0)


@pytest.mark.parametrize("name,args", [("RXGate", (.3,)), ("UGate", (.3, .2, .1)), ("HGate", ()), ("CRXGate", (.3,))])
def test_managed_constructors_reject_foreign_subclass_before_its_hooks(name, args):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    kind = getattr(library, name)
    calls = []
    class Foreign(kind):
        def _initialize(self, *args, **kwargs): calls.append("initialize")
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature): Foreign(*args)
    assert not calls


@pytest.mark.parametrize("name,args", CONSTRUCTORS)
def test_registered_standard_objects_work_in_managed_operator_state_and_density(name, args):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.information import Statevector, DensityMatrix
    with ResourceScope(UnifiedResourceLedger()):
        gate = standard(name, *args)
        expected = independent(name, args)
        np.testing.assert_allclose(Operator(gate).data, expected, atol=3e-13, rtol=0)
        np.testing.assert_allclose(Statevector.from_instruction(gate).data, expected[:, 0], atol=3e-13, rtol=0)
        np.testing.assert_allclose(DensityMatrix.from_instruction(gate).data,
            np.outer(expected[:, 0], expected[:, 0].conj()), atol=3e-13, rtol=0)


def test_matrix_parameter_copy_has_real_quota_and_retained_view_lifetimes():
    import gc
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=63))
    with ResourceScope(ledger), pytest.raises(MemoryError): standard("UnitaryGate", np.eye(2))
    assert ledger.receipt()["live_memory_bytes"] == 0
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=4096))
    with ResourceScope(ledger):
        gate = standard("UnitaryGate", np.eye(2))
        copied = gate.copy()
    assert ledger.receipt()["live_memory_bytes"] == 128
    view = copied.params[0][:]
    del gate, copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 64
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_specialized_hundred_wire_mps_uses_no_dense_matrix_entrypoint(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): pytest.fail("Dense fallback was called.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p = qb.Parameter("p")
    circuit = qb.Circuit(100).h(0)
    for wire in range(99): circuit.cx(wire, wire+1)
    circuit.append(standard("RYGate", 2*p+p.sin()), [99])
    node = QNode.from_circuit(circuit, qb.PauliZ(0).tensor(qb.PauliZ(99)),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0),
        diff_method="parameter-shift", max_diff=2)
    x = .3
    f, df = 2*x+np.sin(x), 2+np.cos(x)
    assert node(x) == pytest.approx(np.cos(f), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(f)*df, abs=3e-11)


@pytest.mark.parametrize("state", [0, 1])
def test_cu_controlled_phase_and_four_parameter_mutation_bind_copy_are_coherent(state):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    gate = standard("CUGate", p, .2, -.1, q, ctrl_state=state)
    copied = gate.assign_parameters({p: .3, q: .17})
    copied.params[0] = .4
    copied.params[3] = -.23
    assert type(copied) is library.CUGate
    assert gate.is_parameterized()
    expected = np.eye(4, dtype=complex)
    offset = 0 if state == 0 else 2
    expected[offset:offset+2, offset:offset+2] = np.exp(-.23j)*independent("UGate", [.4, .2, -.1])
    np.testing.assert_allclose(Operator(copied).data, expected, atol=4e-13, rtol=0)
    np.testing.assert_allclose(Operator(copied.inverse()).data, expected.conj().T, atol=4e-13, rtol=0)


@pytest.mark.parametrize("name", ["CXGate", "CZGate"])
@pytest.mark.parametrize("inner,outer", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_nested_specialized_control_states_preserve_integer_bit_order(name, inner, outer):
    gate = standard(name, ctrl_state=inner).control(1, ctrl_state=outer)
    assert gate.ctrl_state == outer+2*inner
    expected = np.eye(8, dtype=complex)
    offset = 4*outer+2*inner
    expected[offset:offset+2, offset:offset+2] = independent("XGate" if name == "CXGate" else "ZGate", [])
    np.testing.assert_allclose(Operator(gate).data, expected, atol=4e-13, rtol=0)


@pytest.mark.parametrize("name", ["XGate", "ZGate"])
def test_direct_two_control_standard_objects_are_real_and_execute(name):
    gate = standard(name).control(2, ctrl_state=1)
    assert type(gate).__name__ == ("CCXGate" if name == "XGate" else "CCZGate")
    expected = np.eye(8, dtype=complex)
    expected[4:6, 4:6] = independent(name, [])
    np.testing.assert_allclose(Operator(gate).data, expected, atol=4e-13, rtol=0)


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tensorflow"])
def test_standard_gate_native_circuit_has_real_framework_gradient(interface):
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    source = qb.Circuit(1).append(standard("RYGate", 2*p+p.sin()), [0])
    node = QNode.from_circuit(source, qb.PauliZ(0), interface=interface, diff_method="parameter-shift", max_diff=2)
    x = .3
    expected = -np.sin(2*x+np.sin(x))*(2+np.cos(x))
    if interface == "torch":
        torch = pytest.importorskip("torch")
        value = torch.tensor(x, dtype=torch.float64, requires_grad=True)
        actual = torch.autograd.grad(node(value), value)[0].item()
    elif interface == "autograd":
        autograd = pytest.importorskip("autograd")
        actual = autograd.grad(node)(x)
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        actual = float(jax.grad(node)(jax.numpy.asarray(x, dtype=jax.numpy.float64)))
    else:
        tf = pytest.importorskip("tensorflow")
        value = tf.Variable(x, dtype=tf.float64)
        with tf.GradientTape() as tape: result = node(value)
        actual = tape.gradient(result, value).numpy()
    assert actual == pytest.approx(expected, abs=2e-10)


@pytest.mark.parametrize("matrix", [np.ones(2), np.eye(3), np.ones((2, 3)), np.empty((0, 0))])
def test_unitary_shape_rejection_precedes_owned_matrix_construction(matrix):
    with pytest.raises(ValueError): standard("UnitaryGate", matrix)


def test_unitary_empty_binding_and_deferred_inverse_keep_owned_executable_math():
    gate = standard("UnitaryGate", np.diag([1, 1j]))
    copied = gate.assign_parameters({})
    assert copied is not gate and not np.shares_memory(copied.params[0], gate.params[0])
    inverse = gate.inverse(annotated=True)
    np.testing.assert_allclose(Operator(inverse).data, np.diag([1, -1j]), atol=2e-13, rtol=0)


def test_controlled_rotation_power_and_nested_control_reuse_the_existing_engine():
    gate = standard("CRYGate", .3).power(2).control(1, ctrl_state=0)
    expected = np.eye(8, dtype=complex)
    expected[2:4, 2:4] = rotation("RYGate", .6)
    np.testing.assert_allclose(Operator(gate).data, expected, atol=4e-13, rtol=0)
