# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Live parameter mutation must change native computation, not a list copy."""

import gc
from collections.abc import MutableSequence

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator


def rx(angle):
    return np.array([[np.cos(angle/2), -1j*np.sin(angle/2)], [-1j*np.sin(angle/2), np.cos(angle/2)]])


def test_copied_custom_gate_index_mutation_changes_only_its_actual_matrix():
    p = qb.Parameter("p")
    first = qb.Circuit(1).rx(p, 0).to_gate()
    second = first.copy()
    second.params[0] = .5
    assert first.params[0] == p and second.params[0] == .5
    np.testing.assert_allclose(Operator(qb.Circuit(1).append(second, [0])).data, rx(.5), atol=1e-13)
    assert first.is_parameterized() and not second.is_parameterized()


def test_gate_validate_parameter_is_real_and_does_not_mutate():
    gate = qb.Gate("rx", 1, [.3])
    assert gate.validate_parameter(.5) == .5
    with pytest.raises((TypeError, ValueError)): gate.validate_parameter(1j)
    assert gate.params[0] == .3


def test_annotation_validation_and_index_mutation_delegate_to_base():
    base = qb.Gate("rx", 1, [.3])
    annotation = qb.AnnotatedOperation(base, [])
    assert annotation.validate_parameter(.5) == .5
    annotation.params[0] = .5
    assert base.params[0] == .5
    np.testing.assert_allclose(Operator(annotation).data, rx(.5), atol=1e-13)


@pytest.mark.parametrize("value", [.5, 1j, "payload", [1, 2], np.array([1., 2.])])
def test_generic_instruction_validation_preserves_arbitrary_parameter_payload(value):
    instruction = qb.Instruction("instruction", 1, params=[.3])
    assert instruction.validate_parameter(value) is value
    instruction.params[0] = value
    assert instruction.params[0] is value


def test_failed_assignment_keeps_parameters_and_owned_definition():
    p = qb.Parameter("p")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    definition = gate.definition
    with pytest.raises((TypeError, ValueError)): gate.params = [.2, 1j]
    assert gate.params == (p,) and gate.definition is definition


@pytest.mark.parametrize("value", [1j, complex(.2, 0), np.complex128(.2), float("inf"), float("nan"), object()])
def test_invalid_gate_index_update_is_atomic(value):
    gate = qb.Gate("rx", 1, [.3])
    view = gate.params
    before = gate.to_matrix()
    with pytest.raises((TypeError, ValueError)): view[0] = value
    assert gate.params == (.3,) and view == [.3]
    np.testing.assert_array_equal(gate.to_matrix(), before)


def test_live_proxy_and_repeated_numeric_symbolic_updates():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    view = gate.params
    assert isinstance(view, MutableSequence)
    for value in [.2, .5, q.sin()+2*q, -.4]:
        view[0] = value
        assert gate.params[0] == value
        if isinstance(value, qb.ParameterExpression):
            actual = gate.assign_parameters({q: .3}).to_matrix()
            expected = rx(np.sin(.3)+.6)
        else: actual, expected = gate.to_matrix(), rx(value)
        np.testing.assert_allclose(actual, expected, atol=1e-13)
    gate.params = [.7]
    assert view == [.7], "The proxy must observe current owner data, not retain a detached tuple."


def test_mutation_changes_uuid_dependencies_without_changing_appended_snapshot():
    p, q = qb.Parameter("p"), qb.ParameterVector("angles", 2)[1]
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    original_circuit = qb.Circuit(1).append(gate, [0])
    gate.params[0] = q.sin()
    new_circuit = qb.Circuit(1).append(gate, [0])
    assert original_circuit.parameters == (p,) and new_circuit.parameters == (q,)
    assert new_circuit.parameters[0].uuid == q.uuid
    np.testing.assert_allclose(Operator(original_circuit.bind({p: .2})).data, rx(.2), atol=1e-13)
    np.testing.assert_allclose(Operator(new_circuit.bind({q: .3})).data, rx(np.sin(.3)), atol=1e-13)


def test_custom_multi_parameter_rebinding_keeps_phase_and_independent_constants():
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).rx(p.sin()+q*p*p, 0).rz(.5, 0)
    body.global_phase = p/3
    gate = body.to_gate()
    for values in [[.5, -.2], [.7, .4], [.2, -.3]]:
        gate.params[:] = values
        x, y = values
        expected = np.exp(1j*x/3)*np.diag(np.exp(1j*np.array([-1, 1])*.25))@rx(np.sin(x)+y*x*x)
        np.testing.assert_allclose(gate.to_matrix(), expected, atol=2e-13)


def test_already_bound_gate_can_be_mutated_again():
    p = qb.Parameter("p")
    original = qb.Circuit(1).rx(p, 0).to_gate()
    bound = original.assign_parameters({p: .2})
    bound.params[0] = .7
    np.testing.assert_allclose(bound.to_matrix(), rx(.7), atol=1e-13)
    assert original.params == (p,)


@pytest.mark.parametrize("base_kind", ["custom", "primitive"])
def test_controlled_gate_mutation_updates_base_and_actual_open_control(base_kind):
    p = qb.Parameter("p")
    base = qb.Circuit(1).rx(p, 0).to_gate() if base_kind == "custom" else qb.Gate("rx", 1, [.3])
    gate = base.control(2, ctrl_state=1)
    for value in [.2, .7]:
        gate.params[0] = value
        assert gate.base_gate.params == (value,)
        expected = np.eye(8, dtype=complex)
        expected[4:6, 4:6] = rx(value)
        np.testing.assert_allclose(gate.to_matrix(), expected, atol=1e-13)


def test_instruction_definition_mutation_updates_real_execution_and_copy():
    p = qb.Parameter("p")
    instruction = qb.Circuit(1).rx(p, 0).to_instruction()
    copied = instruction.copy("copy")
    for value in [.2, .7]:
        copied.params[0] = value
        actual = Operator(qb.Circuit.from_instruction(copied)).data
        np.testing.assert_allclose(actual, rx(value), atol=1e-13)
    assert instruction.params == (p,) and instruction.definition.parameters == (p,)


def test_instruction_mutation_preserves_nonunitary_classical_definition():
    p = qb.Parameter("p")
    instruction = qb.Circuit(1, 1).rx(p, 0).measure(0, 0).to_instruction()
    instruction.params[0] = .3
    circuit = qb.Circuit(2, 2).append(instruction, [1], clbits=[0])
    assert circuit.measurements[0].wire == 1 and circuit.measurements[0].bit == 0
    assert circuit.operations[0].params == (.3,)


def test_free_parameter_list_has_real_list_mutators():
    gate = qb.Gate("opaque", 1, [.1, .2])
    view = gate.params
    view.append(.3)
    view.extend([.4, .5])
    view.insert(0, .0)
    assert view.pop() == .5
    del view[1:3]
    view.reverse()
    view.sort()
    view += [.7]
    view *= 2
    assert gate.params == [0., .3, .4, .7]*2
    view.clear()
    assert not gate.params


@pytest.mark.parametrize("change", [lambda p: p.clear(), lambda p: p.append(.5), lambda p: p.__delitem__(0)])
def test_known_primitive_invalid_arity_mutation_rolls_back(change):
    gate = qb.Gate("rx", 1, [.3])
    with pytest.raises(ValueError): change(gate.params)
    assert gate.params == (.3,)


def test_bounded_parameter_extend_does_not_consume_an_unbounded_generator():
    from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
    gate = qb.Gate("opaque", 1, [.1])
    consumed = []
    def values():
        for value in range(20):
            consumed.append(value)
            yield value
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=3)):
        with pytest.raises(MemoryError): gate.params.extend(values())
    assert consumed == [0, 1, 2] and gate.params == (.1,)


def test_live_definition_edits_are_not_silently_dropped_by_parameter_update():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    gate.params[0] = q
    gate.definition.rz(.5, 0)
    gate.params[0] = .7
    expected = np.diag(np.exp(1j*np.array([-1, 1])*.25))@rx(.7)
    np.testing.assert_allclose(gate.to_matrix(), expected, atol=1e-13)


@pytest.mark.parametrize("kind", ["gate", "instruction"])
def test_managed_parameter_update_rejects_foreign_value_before_callbacks(kind):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class Foreign:
        def __getattribute__(self, name):
            if name == "__class__": pytest.fail("Foreign parameter class callback executed.")
            return object.__getattribute__(self, name)
    owner = qb.Gate("rx", 1, [.3]) if kind == "gate" else qb.Instruction("payload", 1, params=[.3])
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature): owner.params[0] = Foreign()
    assert owner.params == (.3,)


def test_managed_foreign_instruction_constructor_does_not_call_post_init():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class ForeignInstruction(qb.Instruction):
        def __post_init__(self): pytest.fail("Foreign post-init callback executed.")
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature):
        ForeignInstruction("foreign", 1, params=[.3])


def test_managed_copy_failure_during_mutation_rolls_back_then_recovers():
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    p = qb.Parameter("p")
    matrix = np.eye(2, dtype=complex)
    owner = qb.Circuit(1).rx(p, 0).unitary(matrix, [0]).to_gate()
    before = owner.definition
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=matrix.nbytes-1))
    with ResourceScope(ledger), pytest.raises(MemoryError): owner.params[0] = .2
    assert owner.params == (p,) and owner.definition is before
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    owner.params[0] = .2
    np.testing.assert_allclose(owner.to_matrix(), rx(.2), atol=1e-13)


def test_managed_view_copy_and_owner_lifetimes_keep_storage_until_last_reference():
    from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
    from quantumbridge.execution.resource_context import ResourceScope
    p = qb.Parameter("p")
    source = qb.Circuit(1).rx(p, 0).unitary(np.eye(2, dtype=complex), [0]).to_gate()
    source.params[0] = .2
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=100000))
    with ResourceScope(ledger):
        copied = source.copy()
        view = copied.params
        copied.params[0] = .7
    np.testing.assert_allclose(copied.to_matrix(), rx(.7), atol=1e-13)
    np.testing.assert_allclose(source.to_matrix(), rx(.2), atol=1e-13)
    assert ledger.receipt()["live_memory_bytes"] > 0
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] > 0
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("name", ["rx", "ry", "rz", "phase", "crx", "cry", "crz", "cp", "rxx", "ryy", "rzz"])
def test_standard_definition_factory_numeric_parameter_mutation_uses_its_recipe(name):
    from quantumbridge.circuit_library import standard_gate_object, standard_gate
    gate = standard_gate_object(name, .3)
    for value in [.5, -.2]:
        gate.params[0] = value
        np.testing.assert_allclose(gate.to_matrix(), Operator(standard_gate(name, value)).data, atol=2e-13)


def test_managed_foreign_metaclass_equality_is_never_used_for_parameter_admission():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class Meta(type):
        def __eq__(self, other): pytest.fail("Foreign metaclass equality executed.")
        __hash__ = type.__hash__
    class Foreign(metaclass=Meta): pass
    gate = qb.Gate("rx", 1, [.3])
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature): gate.params[0] = Foreign()
    assert gate.params == (.3,)


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_mutated_parameter_graph_survives_qpy_and_native_second_derivatives(method):
    from quantumbridge.circuit_library import standard_gate_object
    from quantumbridge.serialization import qpy_dumps, qpy_loads
    from quantumbridge.qml import QNode
    p = qb.ParameterVector("angles", 2)[1]
    gate = standard_gate_object("ry", .3)
    gate.params[0] = 2*p+p.sin()
    source = qb.Circuit(1).append(gate, [0])
    restored = qpy_loads(qpy_dumps(source))[0]
    assert restored.parameters == (p,) and restored.parameters[0].uuid == p.uuid
    node = QNode.from_circuit(restored, qb.PauliZ(0), diff_method=method, max_diff=2)
    x = .4
    f, df, ddf = 2*x+np.sin(x), 2+np.cos(x), -np.sin(x)
    assert node(x) == pytest.approx(np.cos(f), abs=2e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(f)*df, abs=2e-10)
    hessian = -np.cos(f)*df*df-np.sin(f)*ddf
    assert node.compute_hessian(x) == pytest.approx(hessian, abs=4e-10)
    assert node.compute_hvp(.3, x) == pytest.approx(.3*hessian, abs=4e-10)


@pytest.mark.parametrize("kind", ["gate", "instruction"])
def test_expression_parameter_map_preserves_original_formal_slots_for_mutation(kind):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p, 0)
    body.global_phase = p/3
    owner = body.to_gate({p: q.sin()}) if kind == "gate" else body.to_instruction(parameter_map={p: q.sin()})
    owner.params[0] = .5
    for value in [.5, .7]:
        owner.params[0] = value
        actual = Operator(owner if kind == "gate" else qb.Circuit.from_instruction(owner)).data
        np.testing.assert_allclose(actual, np.exp(1j*value/3)*rx(value), atol=1e-13)
    assert body.parameters == (p,)


def test_parameter_view_read_list_operations_return_detached_bounded_lists():
    gate = qb.Gate("opaque", 1, [.1, .2])
    view = gate.params
    assert view[:] == [.1, .2] and view[::-1] == [.2, .1]
    assert view+[.3] == [.1, .2, .3]
    assert [.0]+view == [.0, .1, .2]
    assert view*2 == 2*view == [.1, .2, .1, .2]
    detached = view.copy()
    detached[0] = .9
    assert view == [.1, .2]
    view.remove(.1)
    assert gate.params == (.2,)
    assert repr(view) == "[0.2]"


@pytest.mark.parametrize("operation", ["index", "slice", "sort", "container"])
def test_managed_parameter_mutators_reject_foreign_callbacks_without_mutation(operation):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    class Foreign:
        def __index__(self): pytest.fail("Foreign index callback executed.")
        def __iter__(self): pytest.fail("Foreign iterator callback executed.")
    def key(value): pytest.fail("Foreign sort callback executed.")
    gate = qb.Gate("opaque", 1, [.2, .1])
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature):
        if operation == "index": gate.params[Foreign()] = .7
        elif operation == "slice": gate.params[slice(Foreign(), None)] = []
        elif operation == "sort": gate.params.sort(key=key)
        else: gate.params = Foreign()
    assert gate.params == (.2, .1)


def test_mutated_hundred_wire_gate_runs_mps_derivatives_without_dense_fallback(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): pytest.fail("Dense fallback was called.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(100).h(0)
    for wire in range(99): body.cx(wire, wire+1)
    gate = body.ry(p, 99).to_gate()
    gate.params[0] = q.sin()
    source = qb.Circuit(100).append(gate, range(100))
    node = QNode.from_circuit(source, qb.PauliZ(0).tensor(qb.PauliZ(99)),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0),
        diff_method="parameter-shift", max_diff=2)
    x = .3
    assert node(x) == pytest.approx(np.cos(np.sin(x)), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(np.sin(x))*np.cos(x), abs=3e-11)


def test_repeated_formal_slots_reject_conflicting_updates_atomically():
    p = qb.Parameter("p")
    gate = qb.Gate("shared", 1, [p, p], definition=qb.Circuit(1).rx(p, 0))
    before = gate.definition
    with pytest.raises(ValueError, match="Repeated formal"): gate.params[:] = [.3, .4]
    assert gate.params == (p, p) and gate.definition is before
    gate.params[:] = [.3, .3]
    np.testing.assert_allclose(gate.to_matrix(), rx(.3), atol=1e-13)


def test_bound_definition_edits_are_not_inferred_from_equal_numeric_constants():
    p = qb.Parameter("p")
    gate = qb.Circuit(1).rx(p, 0).to_gate()
    gate.params[0] = .5
    gate.definition.rz(.5, 0)
    before = gate.definition
    with pytest.raises(ValueError, match="explicit symbolic formals"): gate.params[0] = .7
    assert gate.params == (.5,) and gate.definition is before
    np.testing.assert_allclose(gate.to_matrix(), np.diag(np.exp(1j*np.array([-1, 1])*.25))@rx(.5), atol=1e-13)


def test_managed_object_array_parameter_payload_is_rejected_before_retention():
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.core.classical import UnsupportedFeature
    instruction = qb.Instruction("opaque", 1, params=[.3])
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature):
        instruction.params[0] = np.array([object()], dtype=object)
    assert instruction.params == (.3,)
