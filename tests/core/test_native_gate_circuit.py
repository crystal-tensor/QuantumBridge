# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native gate structure and independent complex-matrix execution checks."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator


def test_to_gate_preserves_a_real_definition_and_parameter_identity():
    p = qb.Parameter("p")
    source = qb.Circuit(2, name="composite").h(0).cx(0, 1).rz(p, 1)
    gate = source.to_gate(label="block")
    assert isinstance(gate, qb.Gate) and isinstance(gate, qb.Instruction)
    assert gate.num_clbits == 0 and gate.num_qubits == 2
    assert gate.label == "block" and gate.is_parameterized()
    assert gate.definition.parameters == (p,)
    outer = qb.Circuit(2).append(gate, [0, 1])
    assert len(outer.operations) == 1
    actual = Operator(outer.bind({p: .4})).data
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    cx = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    rz = np.diag(np.exp(np.array([-.2j, .2j])))
    np.testing.assert_allclose(actual, np.kron(np.eye(2), rz) @ cx @ np.kron(h, np.eye(2)), atol=1e-12)


@pytest.mark.parametrize("kind", ["measure", "reset", "kraus", "classical", "condition"])
def test_to_gate_rejects_nonunitary_or_classical_circuits(kind):
    circuit = qb.Circuit(1, 1 if kind in {"measure", "classical", "condition"} else 0).h(0)
    if kind == "measure": circuit.measure(0, 0)
    elif kind == "reset": circuit.reset(0)
    elif kind == "kraus": circuit.kraus([np.eye(2)], [0])
    elif kind == "condition": circuit.c_if(0, 1)
    with pytest.raises(ValueError): circuit.to_gate()


def test_unbound_controlled_gate_keeps_relative_global_phase():
    p = qb.Parameter("phase")
    source = qb.Circuit(1).rz(p, 0)
    source.global_phase = p / 3
    controlled = source.to_gate().control(1)
    actual = Operator(qb.Circuit(2).append(controlled, [0, 1]).bind({p: .4})).data
    expected = np.eye(4, dtype=complex)
    expected[2:, 2:] = np.exp(.4j / 3) * np.diag(np.exp(np.array([-.2j, .2j])))
    np.testing.assert_allclose(actual, expected, atol=1e-12)


def test_decompose_reps_is_one_level_not_recursive_flattening():
    leaf = qb.Circuit(1, name="leaf").rx(.31, 0).to_gate()
    middle = qb.Circuit(1, name="middle").append(leaf, [0]).to_gate()
    outer = qb.Circuit(1).append(middle, [0])
    assert [op.name for op in outer.operations] == ["middle"]
    assert [op.name for op in outer.decompose(reps=1).operations] == ["leaf"]
    assert [op.name for op in outer.decompose(reps=2).operations] == ["rx"]
    assert [op.name for op in outer.operations] == ["middle"]


@pytest.mark.parametrize("reps", [0, 1, 2, 3, -1])
def test_circuit_repeat_is_structural_and_preserves_full_phase(reps):
    source = qb.Circuit(1, name="unit").ry(.37, 0)
    source.global_phase = .19
    repeated = source.repeat(reps)
    assert len(repeated.operations) == max(0, reps)
    np.testing.assert_allclose(Operator(repeated).data, np.linalg.matrix_power(Operator(source).data, max(0, reps)), atol=1e-12)


@pytest.mark.parametrize("widths", [(1, 1), (1, 2), (2, 1), (2, 2)])
def test_tensor_public_qubit_order_with_native_wire_major_matrices(widths):
    a, b = (qb.Circuit(n) for n in widths)
    a.x(0).rz(.23, widths[0]-1)
    b.h(widths[1]-1).ry(-.17, 0)
    a.global_phase, b.global_phase = .19, -.07
    tensor = a.tensor(b)
    expected = np.kron(Operator(b).data, Operator(a).data)
    np.testing.assert_allclose(Operator(tensor).data, expected, atol=1e-12)
    assert tensor.num_qubits == sum(widths)
    assert a.num_qubits == widths[0]
    assert a.copy().tensor(b, inplace=True) is None


def test_gate_copy_definition_assignment_and_atomic_failed_replacement():
    p = qb.Parameter("p")
    gate = qb.Circuit(1, name="g").rx(p, 0).to_gate()
    copied = gate.copy(name="copy")
    copied.definition.ry(.3, 0)
    assert len(gate.definition.operations) == 1
    assert len(copied.definition.operations) == 2
    assert copied.params[0] == p
    with pytest.raises(ValueError): copied.definition = qb.Circuit(2)
    assert copied.definition.num_qubits == 1
    outer = qb.Circuit(1).append(gate, [0])
    gate.definition.rz(.7, 0)
    assert len(outer.decompose().operations) == 1


def test_gate_parameter_reassignment_and_append_overrides_are_owned():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    gate.params = (q.sin(),)
    assert gate.definition.parameters == (q,)
    first = qb.Circuit(1).append(gate, [0])
    bound = first.bind({q: .4})
    np.testing.assert_allclose(Operator(bound).data, Operator(qb.Circuit(1).rx(np.sin(.4), 0)).data, atol=1e-12)
    assert first.parameters == (q,)
    direct = qb.Circuit(1).ry(p, 0).to_gate()
    second = qb.Circuit(1).append(direct, [0], params=[q])
    assert second.parameters == (q,) and direct.definition.parameters == (p,)


@pytest.mark.parametrize("controls,state", [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (2, 3), (3, 5)])
def test_open_multi_controls_against_basis_enumeration(controls, state):
    p = qb.Parameter("p")
    source = qb.Circuit(1).ry(p, 0).rz(2*p, 0)
    source.global_phase = p.sin()/3
    gate = source.to_gate().control(controls, ctrl_state=state)
    actual = Operator(qb.Circuit(controls+1).append(gate, range(controls+1)).bind({p: .31})).data
    reference = Operator(source.bind({p: .31})).data
    expected = np.eye(1 << (controls+1), dtype=complex)
    # Public integer bits enumerate controls least-significant first. Convert
    # explicitly to native wire-major control basis rather than reusing codec.
    native_index = sum(((state >> wire) & 1) << (controls-1-wire) for wire in range(controls))
    selected = slice(2*native_index, 2*native_index+2)
    expected[selected, selected] = reference
    np.testing.assert_allclose(actual, expected, atol=1e-12)


def test_inverse_power_and_numerical_principal_fractional_power():
    source = qb.Circuit(1).ry(.37, 0).rz(-.81, 0)
    source.global_phase = .23
    gate = source.to_gate()
    matrix = Operator(source).data
    np.testing.assert_allclose(Operator(gate.inverse()).data @ matrix, np.eye(2), atol=1e-12)
    for exponent in (-3, -1, 0, 1, 2, 3):
        np.testing.assert_allclose(Operator(gate.power(exponent)).data, np.linalg.matrix_power(matrix, exponent), atol=1e-12)
    root = Operator(gate.power(.5)).data
    np.testing.assert_allclose(root @ root, matrix, atol=1e-12)
    np.testing.assert_allclose(root.conj().T @ root, np.eye(2), atol=1e-12)


def test_noncontiguous_mapping_and_selected_layer_labels():
    a = qb.Circuit(2, name="a").h(0).cx(0, 1).to_gate(label="choose")
    b = qb.Circuit(1, name="b").ry(.31, 0).to_gate()
    source = qb.Circuit(3).append(a, [2, 0]).append(b, [1])
    selected = source.decompose("choose")
    assert [op.name for op in selected.operations] == ["h", "cx", "b"]
    assert selected.operations[0].wires == (2,)
    assert selected.operations[1].wires == (2, 0)
    np.testing.assert_allclose(Operator(source).data, Operator(selected).data, atol=1e-12)
    assert source.operations[0].name == "a"


def test_invalid_mutated_definition_rejected_before_append():
    gate = qb.Circuit(1).h(0).to_gate()
    gate.definition.num_qubits = 2
    target = qb.Circuit(1)
    with pytest.raises(ValueError): target.append(gate, [0])
    assert not target.operations


def test_cycle_rejected_without_recursive_deepcopy():
    gate = qb.Circuit(1).h(0).to_gate()
    gate.definition.operations.append(qb.Operation("cyclic", (0,), metadata={"gate": gate}))
    with pytest.raises(ValueError, match="Cyclic"):
        qb.Circuit(1).append(gate, [0])


def test_definition_and_repeat_limits_are_admitted_before_mutation():
    from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
    gate = qb.Circuit(1).rx(.2, 0).ry(.3, 0).to_gate()
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=3, max_repeat_count=2)):
        with pytest.raises(MemoryError): gate.repeat(2)
        with pytest.raises(MemoryError): gate.repeat(3)
        with pytest.raises(MemoryError): qb.Circuit(1).x(0).x(0).x(0).to_gate().repeat(2)
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)):
        with pytest.raises(MemoryError): qb.Circuit(2).h(0).to_gate().to_matrix()


@pytest.mark.parametrize("kind", ["barrier", "delay", "unknown"])
def test_directives_and_unknown_opaque_operations_are_not_gates(kind):
    circuit = qb.Circuit(1)
    if kind == "barrier": circuit.barrier()
    elif kind == "delay": circuit.delay(10, 0)
    else: circuit.append("unknown", [0])
    with pytest.raises(ValueError): circuit.to_gate()


def test_measured_repeat_and_tensor_keep_measurement_positions_and_bits():
    source = qb.Circuit(1, 1).h(0).measure(0, 0).x(0)
    repeated = source.repeat(2)
    assert [m.metadata["operation_index"] for m in repeated.measurements] == [1, 3]
    tensor = source.tensor(qb.Circuit(1, 1).x(0).measure(0, 0))
    assert sorted((m.wire, m.bit) for m in tensor.measurements) == [(0, 0), (1, 1)]


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("point", [(.4, -.2), (-.7, .5), (.8, 1.1)])
def test_controlled_symbolic_phase_reaches_real_quantum_hessian_and_hvp(method, point):
    from quantumbridge.qml import QNode
    p, q = qb.Parameter("p"), qb.Parameter("q")
    angle = p.sin()+q*p**2
    sub = qb.Circuit(1).rz(angle, 0)
    sub.global_phase = angle/3
    circuit = qb.Circuit(3).h(2).append(sub.to_gate().control(), [2, 0])
    node = QNode.from_circuit(circuit, qb.PauliX(2), diff_method=method, max_diff=2)
    p, q = point
    f = np.sin(p)+q*p*p
    df = np.array([np.cos(p)+2*p*q, p*p])
    hf = np.array([[-np.sin(p)+2*q, 2*p], [2*p, 0]])
    expected_gradient = -np.sin(f/6)*df/6
    expected_hessian = -np.cos(f/6)*np.outer(df, df)/36-np.sin(f/6)*hf/6
    assert node(np.array(point)) == pytest.approx(np.cos(f/6), abs=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(np.array(point)), expected_gradient, atol=1e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(np.array(point)), expected_hessian, atol=2e-10, rtol=0)
    direction = np.array([.4, -.2])
    np.testing.assert_allclose(node.compute_hvp(direction, np.array(point)), expected_hessian@direction, atol=2e-10, rtol=0)


def test_large_composite_definition_executes_on_mps_without_dense_expansion(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): raise AssertionError("Dense state expansion is forbidden.")
    monkeypatch.setattr(qb.StatevectorDevice, "statevector", forbidden)
    monkeypatch.setattr(qb.DensityMatrixDevice, "density_matrix", forbidden)
    monkeypatch.setattr(MatrixProductState, "statevector", forbidden)
    monkeypatch.setattr(qb.Gate, "to_matrix", forbidden)
    p = qb.Parameter("p")
    sub = qb.Circuit(1).ry(p.sin()+2*p, 0).to_gate()
    source = qb.Circuit(100).h(0)
    for wire in range(99): source.cx(wire, wire+1)
    source.append(sub, [99])
    # A 100-wire Gate must lower structurally, never materialize its operator.
    wrapped = qb.Circuit(100).append(source.to_gate(), range(100))
    node = QNode.from_circuit(wrapped, qb.PauliZ(0).tensor(qb.PauliZ(99)),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0),
        diff_method="parameter-shift")
    x = .3
    angle = np.sin(x)+2*x
    assert node(x) == pytest.approx(np.cos(angle), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(angle)*(np.cos(x)+2), abs=3e-11)


def test_native_gate_execution_enters_existing_compiler_and_mixed_states():
    from quantumbridge.compiler import native_transpile
    from quantumbridge.information import Statevector, DensityMatrix
    p = qb.Parameter("p")
    definition = qb.Circuit(2).h(0).ry(p, 1).cx(0, 1)
    definition.global_phase = p/3
    gate = definition.to_gate()
    circuit = qb.Circuit(2).append(gate, [1, 0])
    compiled = native_transpile(circuit, basis_gates=["h", "ry", "cx"], optimization_level=0)
    bound = circuit.bind({p: .4})
    matrix = Operator(bound).data
    np.testing.assert_allclose(Operator(compiled.bind({p: .4})).data, matrix, atol=1e-12)
    vector = np.array([1, 2j, -1j, .3], complex)
    vector /= np.linalg.norm(vector)
    rho = .7*np.outer(vector, vector.conj())+.3*np.eye(4)/4
    np.testing.assert_allclose(Statevector(vector).evolve(bound).data, matrix@vector, atol=1e-12)
    np.testing.assert_allclose(DensityMatrix(rho).evolve(bound).data, matrix@rho@matrix.conj().T, atol=1e-12)


@pytest.mark.parametrize("name,params", [("rx", ()), ("rx", (.2, .3)), ("x", (.4,)), ("u2", (.3,)), ("u", (.1, .2))])
def test_to_gate_does_not_accept_wrong_primitive_parameter_arity(name, params):
    with pytest.raises(ValueError): qb.Circuit(1).append(name, [0], params=params).to_gate()


@pytest.mark.parametrize("bad", ["angle", float("inf"), float("nan"), [1, 2]])
def test_gate_constructor_rejects_non_scalar_or_nonfinite_parameters(bad):
    with pytest.raises((TypeError, ValueError)): qb.Gate("g", 1, [bad])


def test_controlled_metadata_cycles_and_excessive_width_reject_before_identity_allocation(monkeypatch):
    from quantumbridge.utils import math as native_math
    metadata = {}
    metadata["controlled_base"] = {"name": "native_controlled", "metadata": metadata, "controls": 1}
    def forbidden(*args, **kwargs): raise AssertionError("No matrix may be allocated before rejecting this description.")
    monkeypatch.setattr(native_math, "_gate_identity", forbidden)
    with pytest.raises(ValueError, match="Cyclic"): native_math.gate_matrix("native_controlled", (), metadata)
    metadata = {"controlled_base": {"name": "x", "metadata": {}, "controls": 16}}
    with pytest.raises(MemoryError): native_math.gate_matrix("native_controlled", (), metadata)


def test_live_gate_nodes_are_not_discardable_source_metadata():
    from quantumbridge.serialization import qasm3_dumps
    from quantumbridge.serialization.errors import UnsupportedFeature
    gate = qb.Circuit(1, name="h").x(0).to_gate()
    circuit = qb.Circuit(1).append(gate, [0])
    from quantumbridge.serialization import qasm3_loads
    np.testing.assert_allclose(Operator(qasm3_loads(qasm3_dumps(circuit))).data, [[0, 1], [1, 0]], atol=1e-13)
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir import IRProgram
    restored = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    np.testing.assert_allclose(Operator(restored).data, [[0, 1], [1, 0]], atol=1e-13)


def test_controlled_binding_retains_type_and_base_gate_namespace():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    controlled = qb.Circuit(1).rx(p, 0).to_gate().control(2, ctrl_state="10")
    copied = controlled.copy()
    copied.params = (q,)
    assert copied.definition.parameters == copied.base_gate.definition.parameters == (q,)
    assert controlled.definition.parameters == (p,)
    bound = copied.assign_parameters({q: .3})
    assert isinstance(bound, qb.ControlledGate)
    assert bound.ctrl_state == 2 and bound.num_ctrl_qubits == 2
    assert not bound.definition.parameters and not bound.base_gate.definition.parameters


@pytest.mark.parametrize("kind", ["barrier", "delay"])
def test_nonunitary_directives_remain_repeatable_circuit_structure(kind):
    source = qb.Circuit(1)
    if kind == "barrier": source.barrier()
    else: source.delay(10, 0)
    repeated = source.repeat(3)
    assert [op.name for op in repeated.operations] == [kind]*3


def test_control_flow_body_gate_is_structurally_lowered():
    gate = qb.Circuit(1).x(0).to_gate()
    body = qb.Circuit(1).append(gate, [0])
    source = qb.Circuit(1).if_else(True, body)
    lowered = source.lowered()
    node = lowered.operations[0].metadata["control_node"]
    assert node.bodies[0].operations[0].name == "x"
    assert "gate" not in node.bodies[0].operations[0].metadata
    assert "gate" in source.operations[0].metadata["control_node"].bodies[0].operations[0].metadata
    assert qb.StatevectorDevice().expectation(lowered, qb.PauliZ(0)) == pytest.approx(-1.)


@pytest.mark.parametrize("controlled", [False, True])
def test_native_gate_state_constructors_and_storage_release_in_managed_scope(controlled):
    import gc
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.information import Statevector, DensityMatrix
    gate = qb.Circuit(1).ry(.31, 0).to_gate()
    if controlled: gate = gate.control()
    reference = Operator(gate).data[:, 0]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1000000))
    with ResourceScope(ledger):
        vector = Statevector.from_instruction(gate)
        density = DensityMatrix.from_instruction(gate)
        np.testing.assert_allclose(vector.data, reference, atol=1e-12)
        np.testing.assert_allclose(density.data, np.outer(reference, reference.conj()), atol=1e-12)
        copied = gate.copy()
        assert copied.definition is not gate.definition
    del vector, density, copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_gate_matrix_copy_rejects_storage_before_numpy_factory(monkeypatch):
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    gate = qb.Circuit(1).unitary(np.array([[0, 1], [1, 0]], complex), [0]).to_gate()
    def forbidden(*args, **kwargs): raise AssertionError("Copy preceded storage admission.")
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))):
        with pytest.raises(MemoryError): gate.copy()


@pytest.mark.parametrize("widths", [(1, 1), (1, 2), (2, 1), (2, 2)])
def test_actual_public_tensor_wire_order_and_native_matrix_convention(widths):
    public = pytest.importorskip("qiskit")
    public_info = pytest.importorskip("qiskit.quantum_info")
    a, b = [qb.Circuit(n) for n in widths]
    pa, pb = [public.QuantumCircuit(n) for n in widths]
    for native, upstream in ((a, pa), (b, pb)):
        native.h(0).ry(.31, native.num_qubits-1)
        upstream.h(0)
        upstream.ry(.31, upstream.num_qubits-1)
        native.global_phase = upstream.global_phase = .17
    result = a.tensor(b)
    expected = public_info.Operator(pa.tensor(pb)).data
    width = sum(widths)
    order = [int(format(index, "0"+str(width)+"b")[::-1], 2) for index in range(1 << width)]
    np.testing.assert_allclose(Operator(result).data, expected[np.ix_(order, order)], atol=1e-12)


@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_actual_public_controlled_gate_with_symbolic_phase_and_binding(state):
    public = pytest.importorskip("qiskit")
    public_info = pytest.importorskip("qiskit.quantum_info")
    public_circuit = public.QuantumCircuit(1, name="g")
    public_circuit.ry(.37, 0)
    public_circuit.global_phase = .17
    public_outer = public.QuantumCircuit(3)
    public_outer.append(public_circuit.to_gate().control(2, ctrl_state=state, annotated=False), [0, 1, 2])
    native = qb.Circuit(1, name="g").ry(.37, 0)
    native.global_phase = .17
    native_outer = qb.Circuit(3).append(native.to_gate().control(2, ctrl_state=state), [0, 1, 2])
    order = [int(format(index, "03b")[::-1], 2) for index in range(8)]
    matrix = public_info.Operator(public_outer).data
    np.testing.assert_allclose(Operator(native_outer).data, matrix[np.ix_(order, order)], atol=2e-12)


@pytest.mark.parametrize("framework", ["torch", "autograd", "jax", "tensorflow"])
@pytest.mark.parametrize("controlled", [False, True])
@pytest.mark.parametrize("value", [.3, -.4])
def test_real_framework_second_graph_survives_native_gate_lowering(framework, controlled, value):
    module = pytest.importorskip(framework)
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    angle = p.sin()+2*p
    sub = qb.Circuit(1).rz(angle, 0)
    sub.global_phase = angle/3
    gate = sub.to_gate()
    circuit = qb.Circuit(2 if controlled else 1).h(0)
    circuit.append(gate.control() if controlled else gate, [0, 1] if controlled else [0])
    node = QNode.from_circuit(circuit, qb.PauliX(0), interface=framework, max_diff=2)
    if framework == "torch":
        x = module.tensor(value, dtype=module.float64, requires_grad=True)
        actual = node(x)
        first, = module.autograd.grad(actual, x, create_graph=True)
        second, = module.autograd.grad(first, x)
        result = [v.detach().numpy() for v in (actual, first, second)]
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
    k = 1/6 if controlled else 1.
    f, df = np.sin(value)+2*value, np.cos(value)+2
    reference = [np.cos(k*f), -k*np.sin(k*f)*df,
                 -k*k*np.cos(k*f)*df*df+k*np.sin(k*f)*np.sin(value)]
    np.testing.assert_allclose(result, reference, atol=2e-9 if framework == "jax" else 2e-10, rtol=0)


def test_gate_parameter_iterable_is_bounded_before_materialization():
    from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
    consumed = []
    def parameters():
        for value in range(20):
            consumed.append(value)
            yield value
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)):
        with pytest.raises(MemoryError): qb.Gate("g", 1, parameters())
    assert consumed == [0, 1, 2], "Gate consumed beyond the preallocation admission probe."


def test_managed_gate_append_rejects_foreign_subclass_before_definition_callback():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class ForeignGate(qb.Gate):
        @property
        def definition(self): raise AssertionError("Foreign definition callback was executed.")
    value = object.__new__(ForeignGate)
    with ResourceScope(UnifiedResourceLedger()):
        with pytest.raises(UnsupportedFeature): qb.Circuit(1).append(value, [0])


def test_managed_definition_rejects_foreign_circuit_before_width_callback():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class ForeignCircuit(qb.Circuit):
        def __getattribute__(self, name):
            if name == "num_qubits": raise AssertionError("Foreign width callback was executed.")
            return object.__getattribute__(self, name)
    value = object.__new__(ForeignCircuit)
    gate = qb.Circuit(1).h(0).to_gate()
    with ResourceScope(UnifiedResourceLedger()):
        with pytest.raises(UnsupportedFeature): gate.definition = value


def test_known_primitive_name_never_overrides_a_custom_gate_definition_in_tableau():
    from quantumbridge.information import Clifford
    gate = qb.Circuit(1, name="h").x(0).to_gate()
    circuit = qb.Circuit(1).append(gate, [0])
    assert qb.StabilizerDevice().expectation(circuit, qb.PauliZ(0)) == pytest.approx(-1.)
    np.testing.assert_array_equal(Clifford(circuit).tableau, Clifford(qb.Circuit(1).x(0)).tableau)
    np.testing.assert_array_equal(Clifford(gate).tableau, Clifford(qb.Circuit(1).x(0)).tableau)


def test_known_primitive_name_never_overrides_custom_gate_definition_in_public_adapters():
    pytest.importorskip("qiskit")
    qml = pytest.importorskip("pennylane")
    from qiskit.quantum_info import Operator as PublicOperator
    from quantumbridge.compat.qiskit_adapter import circuit_to_qiskit
    from quantumbridge.compat.pennylane_adapter import circuit_to_pennylane_callable
    circuit = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    np.testing.assert_allclose(PublicOperator(circuit_to_qiskit(circuit)).data, np.array([[0, 1], [1, 0]]), atol=1e-12)
    np.testing.assert_allclose(circuit_to_pennylane_callable(circuit)(), [0, 1], atol=1e-12)


@pytest.mark.parametrize("method", ["statevector", "density_matrix", "matrix_product_state", "stabilizer"])
def test_native_aer_methods_use_gate_definition_before_name_dispatch(method):
    from quantumbridge.simulator import NativeAerSimulator
    circuit = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    circuit.save_probabilities(label="p")
    data = NativeAerSimulator(method=method, shots=None).run(circuit).result().data()
    np.testing.assert_allclose(data["p"], [0, 1], atol=1e-12)


@pytest.mark.parametrize("method", ["unitary", "superop"])
def test_native_aer_linear_maps_keep_custom_gate_math(method):
    from quantumbridge.simulator import NativeAerSimulator
    circuit = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    if method == "unitary": circuit.save_unitary(label="matrix")
    else: circuit.save_superop(label="matrix")
    actual = NativeAerSimulator(method=method, shots=None).run(circuit).result().data()["matrix"]
    x = np.array([[0, 1], [1, 0]], complex)
    np.testing.assert_allclose(actual, x if method == "unitary" else np.kron(x, x), atol=1e-12)


def test_named_composite_noise_is_rejected_instead_of_silently_lost():
    from quantumbridge.simulator import NativeAerSimulator
    from quantumbridge.noise import NoiseModel, pauli_error
    from quantumbridge.providers import JobError
    model = NoiseModel()
    model.add_all_qubit_quantum_error(pauli_error([("X", .1), ("I", .9)]), ["h"])
    circuit = qb.Circuit(1).append(qb.Circuit(1, name="h").x(0).to_gate(), [0])
    with pytest.raises(JobError): NativeAerSimulator(noise_model=model, shots=None).run(circuit).result()
