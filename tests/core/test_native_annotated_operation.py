# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Deferred modifier structure and independent phase-sensitive operators."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator, Statevector, DensityMatrix


def independent_rx(angle):
    return np.array([[np.cos(angle/2), -1j*np.sin(angle/2)], [-1j*np.sin(angle/2), np.cos(angle/2)]])


def independent_modifiers(matrix, modifiers):
    result = matrix.copy()
    for item in modifiers:
        if type(item) is qb.InverseModifier: result = result.conj().T
        elif type(item) is qb.ControlModifier:
            old = len(result)
            output = np.eye(old*(1 << item.num_ctrl_qubits), dtype=complex)
            index = sum(((item.ctrl_state >> bit) & 1) << (item.num_ctrl_qubits-bit-1) for bit in range(item.num_ctrl_qubits))
            output[index*old:(index+1)*old, index*old:(index+1)*old] = result
            result = output
        elif float(item.power).is_integer(): result = np.linalg.matrix_power(result, int(item.power))
        else:
            values, vectors = np.linalg.eig(result)
            result = vectors @ np.diag(np.exp(1j*np.angle(values)*item.power)) @ np.linalg.inv(vectors)
    return result


def test_annotation_is_not_a_gate_or_instruction_and_keeps_ordered_structure():
    base = qb.Gate("rx", 1, [.37])
    control, power = qb.ControlModifier(1), qb.PowerModifier(2)
    a = qb.AnnotatedOperation(base, [control, power])
    b = qb.AnnotatedOperation(base, [power, control])
    assert not isinstance(a, (qb.Gate, qb.Instruction))
    assert a.name == "annotated" and a.num_clbits == 0 and a.num_qubits == 2
    assert tuple(a.modifiers) == (control, power) and a != b
    # These ideal unitary matrices are equal despite different structures.
    np.testing.assert_allclose(a.to_matrix().data, b.to_matrix().data, atol=1e-13)


@pytest.mark.parametrize("state", [0, 1])
def test_deferred_controlled_symbolic_phase_binds_before_resolution(state):
    p = qb.Parameter("p")
    body = qb.Circuit(1).rz(p, 0)
    body.global_phase = p/3
    annotated = qb.AnnotatedOperation(body.to_gate(), [qb.ControlModifier(1, state)])
    assert annotated.parameters == (p,)
    bound = annotated.assign_parameters({p: .4})
    resolved = qb.resolve_annotated_operation(bound)
    expected = np.eye(4, dtype=complex)
    expected[state*2:state*2+2, state*2:state*2+2] = np.exp(.4j/3)*np.diag(np.exp(1j*np.array([-1, 1])*.4/2))
    np.testing.assert_allclose(resolved.to_matrix(), expected, atol=1e-13)
    source = qb.Circuit(2).append(annotated, [0, 1])
    assert "annotated_operation" in source.operations[0].metadata
    np.testing.assert_allclose(Operator(source.bind({p: .4})).data, expected, atol=1e-13)


def test_nested_open_controls_are_not_reordered():
    base = qb.Gate("x", 1)
    a = qb.AnnotatedOperation(base, [qb.ControlModifier(1, 0), qb.ControlModifier(1, 1)])
    b = qb.AnnotatedOperation(base, [qb.ControlModifier(1, 1), qb.ControlModifier(1, 0)])
    expected_a, expected_b = np.eye(8), np.eye(8)
    expected_a[4:6, 4:6] = [[0, 1], [1, 0]]
    expected_b[2:4, 2:4] = [[0, 1], [1, 0]]
    np.testing.assert_allclose(a.to_matrix().data, expected_a, atol=1e-13)
    np.testing.assert_allclose(b.to_matrix().data, expected_b, atol=1e-13)
    assert not np.array_equal(expected_a, expected_b)


def test_existing_gate_annotation_methods_return_deferred_operations():
    gate = qb.Gate("rx", 1, [.3])
    assert isinstance(gate.inverse(annotated=True), qb.AnnotatedOperation)
    assert isinstance(gate.control(annotated=True), qb.AnnotatedOperation)
    assert isinstance(gate.power(2, annotated=True), qb.AnnotatedOperation)


CHAINS = [[], [qb.InverseModifier()], [qb.PowerModifier(-3)], [qb.PowerModifier(0)],
    [qb.PowerModifier(2)], [qb.PowerModifier(.5)], [qb.ControlModifier(1, 0)],
    [qb.ControlModifier(2, "01")], [qb.ControlModifier(2, "10")],
    [qb.InverseModifier(), qb.ControlModifier(1)], [qb.ControlModifier(1), qb.InverseModifier()],
    [qb.ControlModifier(1, 0), qb.PowerModifier(-2)], [qb.PowerModifier(3), qb.ControlModifier(1, 0)],
    [qb.ControlModifier(1, 0), qb.ControlModifier(1, 1)],
    [qb.ControlModifier(1, 1), qb.ControlModifier(1, 0)],
    [qb.InverseModifier(), qb.PowerModifier(2), qb.ControlModifier(1, 0), qb.InverseModifier()]]


@pytest.mark.parametrize("modifiers", CHAINS)
def test_real_resolution_against_independent_dense_algebra(modifiers):
    body = qb.Circuit(1).rx(.37, 0)
    body.global_phase = .17
    operation = qb.AnnotatedOperation(body.to_gate(), modifiers)
    expected = independent_modifiers(np.exp(.17j)*independent_rx(.37), modifiers)
    np.testing.assert_allclose(Operator(operation).data, expected, atol=3e-13)
    np.testing.assert_allclose(Statevector(operation).data, expected[:, 0], atol=3e-13)
    np.testing.assert_allclose(DensityMatrix(operation).data, np.outer(expected[:, 0], expected[:, 0].conj()), atol=3e-13)
    np.testing.assert_allclose(Operator(qb.Circuit.from_instruction(operation).inverse()).data, expected.conj().T, atol=3e-13)


def test_constructor_aliases_but_append_copy_and_binding_own_snapshots():
    p = qb.Parameter("p")
    base, modifiers = qb.Gate("rx", 1, [p]), [qb.InverseModifier()]
    operation = qb.AnnotatedOperation(base, modifiers)
    assert operation.base_op is base and operation.modifiers is modifiers
    copied = operation.copy()
    source = qb.Circuit(1).append(operation, [0])
    operation.params = [.41]
    modifiers.append(qb.PowerModifier(2))
    assert base.params == (.41,) and copied.parameters == (p,)
    assert source.parameters == (p,) and len(source.operations[0].metadata["annotated_operation"].modifiers) == 1
    assert copied.base_op is not base and copied.modifiers is not modifiers
    np.testing.assert_allclose(Operator(source.bind({p: .2})).data, independent_rx(-.2), atol=2e-13)
    np.testing.assert_allclose(operation.to_matrix().data, independent_rx(-.82), atol=2e-13)


@pytest.mark.parametrize("base_type", ["gate", "instruction", "nested"])
@pytest.mark.parametrize("chain", [[], [qb.InverseModifier()], [qb.ControlModifier(1)], [qb.PowerModifier(2)],
    [qb.InverseModifier(), qb.ControlModifier(1)]])
def test_native_construction_and_structural_equality(base_type, chain):
    base = qb.Gate("rx", 1, [.2]) if base_type != "instruction" else qb.Instruction("rx", 1, params=(.2,))
    if base_type == "nested": base = qb.AnnotatedOperation(base, [])
    op = qb.AnnotatedOperation(base, chain)
    assert op == op.copy() and op != base and op.name == "annotated"
    assert op.num_qubits == 1+sum(item.num_ctrl_qubits for item in chain if isinstance(item, qb.ControlModifier))
    assert op.params == (.2,)
    assert isinstance(op.to_matrix(), Operator)


@pytest.mark.parametrize("annotated", [True, False, None])
def test_annotation_chain_methods_ignore_annotation_and_label_flags(annotated):
    operation = qb.AnnotatedOperation(qb.Gate("x", 1), qb.InverseModifier())
    assert isinstance(operation.inverse(annotated=annotated), qb.AnnotatedOperation)
    assert isinstance(operation.power(2, annotated=annotated), qb.AnnotatedOperation)
    controlled = operation.control(1, label="ignored", ctrl_state="0", annotated=annotated)
    assert controlled.base_op is operation.base_op
    assert controlled.modifiers == [qb.InverseModifier(), qb.ControlModifier(1, 0)]


def test_symbolic_power_dependency_is_explicit_and_resolves_only_after_binding():
    p, k = qb.Parameter("p"), qb.Parameter("k")
    operation = qb.AnnotatedOperation(qb.Gate("rz", 1, [p]), qb.PowerModifier(k))
    assert set(operation.parameters) == {p, k} and operation.params == (p,)
    circuit = qb.Circuit(1).append(operation, [0])
    assert set(circuit.parameters) == {p, k}
    with pytest.raises(qb.UnsupportedFeature, match="Bind a symbolic power"):
        circuit.assign_parameters({p: .4}).lowered()
    np.testing.assert_allclose(Operator(circuit.bind({p: .4, k: 2})).data,
        np.diag(np.exp(1j*np.array([-.4, .4]))), atol=2e-13)
    assert len(operation.parameters) == 2


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("state,power", [(0, 2), (1, 2), (0, -3), (1, -3)])
def test_annotation_native_jacobian_hessian_and_streamed_hvp(method, state, power):
    from quantumbridge.qml import QNode
    p, q = qb.Parameter("p"), qb.Parameter("q")
    angle = p.sin()+q*p*p
    body = qb.Circuit(1).rz(angle, 0)
    body.global_phase = angle/3
    op = qb.AnnotatedOperation(body.to_gate(), [qb.ControlModifier(1, state), qb.PowerModifier(power)])
    circuit = qb.Circuit(2).h(0).append(op, [0, 1])
    node = QNode.from_circuit(circuit, qb.PauliX(0), diff_method=method, max_diff=2)
    point = np.array([.4, -.2])
    p, q = point
    f = np.sin(p)+q*p*p
    df = np.array([np.cos(p)+2*q*p, p*p])
    hf = np.array([[-np.sin(p)+2*q, 2*p], [2*p, 0]])
    a = power/6
    gradient = -a*np.sin(a*f)*df
    hessian = -a*a*np.cos(a*f)*np.outer(df, df)-a*np.sin(a*f)*hf
    assert node(point) == pytest.approx(np.cos(a*f), abs=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=4e-10, rtol=0)
    v = np.array([.3, -.2])
    np.testing.assert_allclose(node.compute_hvp(v, point), hessian@v, atol=4e-10, rtol=0)


def test_100_wire_annotation_keeps_tensor_network_without_dense_fallback(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p = qb.Parameter("p")
    leaf = qb.AnnotatedOperation(qb.Gate("ry", 1, [p.sin()+2*p]), [qb.InverseModifier(), qb.PowerModifier(2)])
    sub = qb.Circuit(100).h(0)
    for wire in range(99): sub.cx(wire, wire+1)
    sub.append(leaf, [99])
    op = qb.AnnotatedOperation(sub.to_gate(), [])
    source = qb.Circuit(100).append(op, range(100))
    node = QNode.from_circuit(source, qb.PauliZ(0).tensor(qb.PauliZ(99)),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0), diff_method="parameter-shift")
    x = .3
    angle = -2*(np.sin(x)+2*x)
    assert node(x) == pytest.approx(np.cos(angle), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(2*np.sin(angle)*(np.cos(x)+2), abs=3e-11)


@pytest.mark.parametrize("count,state", [(0, None), (-1, None), (True, 1), (1, 2), (2, -1), (2, "1"), (1, "x")])
def test_control_modifier_rejects_invalid_values(count, state):
    with pytest.raises((TypeError, ValueError)): qb.ControlModifier(count, state)


@pytest.mark.parametrize("power", [True, 1j, np.nan, np.inf, object()])
def test_power_modifier_rejects_invalid_scalar(power):
    with pytest.raises((TypeError, ValueError)): qb.PowerModifier(power)


def test_invalid_live_base_modifiers_headers_cycles_and_atomic_append():
    base = qb.Circuit(1).rx(.2, 0).to_gate()
    operation = qb.AnnotatedOperation(base, [])
    target = qb.Circuit(1)
    operation.modifiers.append("inverse")
    with pytest.raises(TypeError): target.append(operation, [0])
    assert not target.operations
    operation.modifiers.clear()
    operation.base_op = operation
    with pytest.raises(ValueError, match="Cyclic"): target.append(operation, [0])
    operation.base_op = base
    base.definition.operations.append(qb.Operation("annotated", (0,), metadata={"annotated_operation": operation}))
    with pytest.raises(ValueError, match="Cyclic"): qb.resolve_annotated_operation(operation)
    for source in (qb.Instruction("bad", 1, num_bits=1), qb.Instruction("bad", 1, definition=qb.Circuit(1).reset(0))):
        staged = qb.AnnotatedOperation(source, [])
        with pytest.raises(ValueError): qb.resolve_annotated_operation(staged)
        if source.num_clbits:
            with pytest.raises(ValueError): qb.Circuit(1).append(staged, [0])
        else:
            stored = qb.Circuit(1).append(staged, [0])
            with pytest.raises(ValueError): stored.lowered()


def test_resource_admission_covers_nested_definition_aggregate_and_resolution():
    from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
    base = qb.Circuit(1).rx(.2, 0).rz(.3, 0).to_gate()
    operation = qb.AnnotatedOperation(base, [qb.PowerModifier(1000)])
    with pytest.raises(MemoryError, match="max_total_operations"):
        qb.resolve_annotated_operation(operation, limits=GateCircuitLimits(max_total_operations=20))
    controlled = qb.AnnotatedOperation(base, qb.ControlModifier(3))
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=8)):
        with pytest.raises(MemoryError): controlled.to_matrix()
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=2)):
        with pytest.raises(MemoryError): qb.AnnotatedOperation(qb.Gate("x", 1), [qb.InverseModifier()]*3)
    leaves = qb.Circuit(1)
    for _ in range(3): leaves.append(qb.AnnotatedOperation(base, []), [0])
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=8)):
        with pytest.raises(MemoryError, match="max_total_operations"): leaves.to_gate()


def test_selected_decompose_does_not_resolve_unselected_symbolic_power():
    p = qb.Parameter("p")
    op = qb.AnnotatedOperation(qb.Gate("x", 1), qb.PowerModifier(p))
    circuit = qb.Circuit(1).append(op, [0])
    assert circuit.decompose("other").operations[0].metadata["annotated_operation"] == op
    with pytest.raises(qb.UnsupportedFeature): circuit.decompose("annotated")


@pytest.mark.parametrize("framework", ["torch", "autograd", "jax", "tensorflow"])
def test_annotation_actual_framework_first_and_second_derivatives(framework):
    module = pytest.importorskip(framework)
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    angle = p.sin()+2*p
    body = qb.Circuit(1).rz(angle, 0)
    body.global_phase = angle/3
    op = qb.AnnotatedOperation(body.to_gate(), [qb.ControlModifier(1, 0), qb.PowerModifier(-2)])
    node = QNode.from_circuit(qb.Circuit(2).h(0).append(op, [0, 1]), qb.PauliX(0), interface=framework, max_diff=2)
    value = .31
    if framework == "torch":
        x = module.tensor(value, dtype=module.float64, requires_grad=True)
        actual = node(x)
        first, = module.autograd.grad(actual, x, create_graph=True)
        second, = module.autograd.grad(first, x)
        result = [item.detach().numpy() for item in (actual, first, second)]
    elif framework == "autograd":
        result = [node(value), module.grad(node)(value), module.grad(module.grad(node))(value)]
    elif framework == "jax":
        jnp = pytest.importorskip("jax.numpy")
        x = jnp.asarray(value, dtype=jnp.float64)
        result = [node(x), module.grad(node)(x), module.grad(module.grad(node))(x)]
    else:
        x = module.Variable(value, dtype=module.float64)
        with module.GradientTape() as outer:
            with module.GradientTape() as inner: actual = node(x)
            first = inner.gradient(actual, x)
        result = [actual.numpy(), first.numpy(), outer.gradient(first, x).numpy()]
    f, df, k = np.sin(value)+2*value, np.cos(value)+2, -1/3
    expected = [np.cos(k*f), -k*np.sin(k*f)*df,
        -k*k*np.cos(k*f)*df*df+k*np.sin(k*f)*np.sin(value)]
    np.testing.assert_allclose(result, expected, atol=3e-10, rtol=0)


def test_managed_annotation_copy_state_execution_and_lifetime():
    import gc
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    op = qb.AnnotatedOperation(qb.Gate("ry", 1, [.31]), [qb.InverseModifier(), qb.ControlModifier(1, 0)])
    reference = Operator(op).data[:, 0]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1000000))
    with ResourceScope(ledger):
        vector, density = Statevector(op), DensityMatrix(op)
        copied = op.copy()
        np.testing.assert_allclose(vector.data, reference, atol=2e-13)
        np.testing.assert_allclose(density.data, np.outer(reference, reference.conj()), atol=2e-13)
        assert copied.base_op is not op.base_op
    del vector, density, copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_managed_annotation_rejects_foreign_intake_without_callbacks():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    visited = []
    class Foreign:
        def __iter__(self):
            visited.append("iter")
            return iter([])
    with ResourceScope(UnifiedResourceLedger()):
        with pytest.raises(TypeError): qb.AnnotatedOperation(qb.Gate("x", 1), Foreign())
        with pytest.raises(TypeError): qb.AnnotatedOperation(Foreign(), [])
    assert not visited


def test_annotation_fractional_symbolic_and_unknown_generator_remain_explicit():
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    op = qb.AnnotatedOperation(qb.Gate("ry", 1, [p]), qb.PowerModifier(.5))
    with pytest.raises(qb.UnsupportedFeature): qb.resolve_annotated_operation(op)
    unknown = qb.AnnotatedOperation(qb.Gate("ry", 1, [p]), qb.ControlModifier(2))
    circuit = qb.Circuit(3).h(0).h(1).append(unknown, [0, 1, 2])
    with pytest.raises(qb.UnsupportedFeature):
        node = QNode.from_circuit(circuit, qb.PauliZ(2), diff_method="parameter-shift")
        node.compute_jacobian(.3)


def test_named_annotation_noise_boundary_rejects_instead_of_silently_lowering():
    from quantumbridge.simulator import NativeAerSimulator
    from quantumbridge.noise import NoiseModel, pauli_error
    from quantumbridge.providers import JobError
    model = NoiseModel()
    model.add_all_qubit_quantum_error(pauli_error([("X", .1), ("I", .9)]), ["annotated"])
    op = qb.AnnotatedOperation(qb.Gate("x", 1), qb.InverseModifier())
    circuit = qb.Circuit(1).append(op, [0])
    with pytest.raises(JobError): NativeAerSimulator(noise_model=model, shots=None).run(circuit).result()


@pytest.mark.parametrize("scalar", [np.float32, np.float64, np.int64, float, int])
def test_numpy_and_python_integer_power_admits_work_before_repeat(monkeypatch, scalar):
    from quantumbridge.core import GateCircuitLimits
    body = qb.Circuit(1).rx(.2, 0).rz(.3, 0).to_gate()
    op = qb.AnnotatedOperation(body, qb.PowerModifier(scalar(1000)))
    def forbidden(*args, **kwargs): raise AssertionError("Repeat entered before work admission.")
    monkeypatch.setattr(qb.Gate, "repeat", forbidden)
    with pytest.raises(MemoryError, match="max_decomposition_work"):
        qb.resolve_annotated_operation(op, limits=GateCircuitLimits(max_decomposition_work=10))
