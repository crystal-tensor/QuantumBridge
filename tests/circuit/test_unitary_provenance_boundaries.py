# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Fault injection for finite matrix-origin classification before copying."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gates import Gate
from quantumbridge.core.operations import Operation, _matrix_owner_family
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope


def shared_dag(depth):
    source = qb.QuantumCircuit(2)
    source.unitary(np.eye(4), [0, 1])
    owner = source.data[0].operation
    for index in range(depth):
        body = qb.Circuit(2)
        body.operations = [Operation(owner.name, (0, 1), metadata={"gate": owner}) for _ in range(2)]
        wrapper = Gate("layer" + str(index), 2)
        # Inject shared/cyclic graphs without constructor cloning or expansion.
        object.__setattr__(wrapper, "_definition", body)
        owner = wrapper
    return owner


def test_shared_matrix_dag_is_charged_per_expanded_reference_before_work():
    owner = shared_dag(4)
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=7, max_decomposition_work=7)):
        with pytest.raises(MemoryError, match="max_(total_operations|decomposition_work)"):
            _matrix_owner_family(owner)


def test_shared_matrix_dag_analysis_is_memoized_without_exponential_visits(monkeypatch):
    owner = shared_dag(12)
    getter = Gate.definition.fget
    visits = []
    def observed(self):
        visits.append(id(self))
        return getter(self)
    monkeypatch.setattr(Gate, "definition", property(observed, Gate.definition.fset))
    assert _matrix_owner_family(owner)
    assert len(visits) <= 30


def test_matrix_family_cycle_refuses_without_mutating_graph():
    owner = shared_dag(1)
    original = owner.definition.operations[0]
    owner.definition.operations[0] = Operation(owner.name, (0, 1), metadata={"gate": owner})
    with pytest.raises(ValueError, match="[Cc]yclic"):
        _matrix_owner_family(owner)
    assert owner.definition.operations[1] is not original


def test_matrix_family_depth_refuses_before_copy_or_expansion():
    owner = shared_dag(4)
    with gate_circuit_scope(GateCircuitLimits(max_definition_depth=2)):
        with pytest.raises(MemoryError, match="max_definition_depth"):
            _matrix_owner_family(owner)


@pytest.mark.parametrize("payload", ["primitive", "gate"])
def test_native_to_gate_matrix_wrapper_retains_native_q0_first_math(payload):
    from quantumbridge.core.standard_gates import UnitaryGate

    rng = np.random.default_rng(9292)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    body = qb.Circuit(2)
    if payload == "primitive": body.unitary(matrix, [0, 1])
    else: body.append(UnitaryGate(matrix), [0, 1])
    wrapped = body.to_gate()
    assert not _matrix_owner_family(wrapped, public_unmarked=True)
    source = qb.QuantumCircuit(2)
    source.append(wrapped, [0, 1])
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source), matrix[:, 0], atol=3e-12, rtol=0)


def test_public_append_copy_false_retains_owner_without_changing_native_use():
    from quantumbridge.core.standard_gates import UnitaryGate

    matrix = np.array([[1, 1, 1, 1], [1, 1j, -1, -1j],
        [1, -1, 1, -1], [1, -1j, -1, 1j]], complex) / 2
    owner = UnitaryGate(matrix)
    source = qb.QuantumCircuit(2)
    source.ry(.31, 0)
    source.append(owner, [0, 1], copy=False)
    assert source.data[1].operation is owner
    expected = matrix.reshape(2, 2, 2, 2).transpose(1, 0, 3, 2).reshape(4, 4)
    initial = np.array([np.cos(.31 / 2), 0, np.sin(.31 / 2), 0])
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source), expected @ initial, atol=3e-12, rtol=0)
    native = qb.Circuit(2).ry(.31, 0).append(owner, [0, 1])
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(native), matrix @ initial, atol=3e-12, rtol=0)
    assert getattr(owner, "_public_matrix_basis", None) is None
    np.testing.assert_array_equal(owner.to_matrix(), matrix)


@pytest.mark.parametrize("kind", ["copy", "inverse", "integer", "fractional", "repeat", "open", "closed"])
def test_derivation_before_or_after_public_matrix_lowering_has_same_physics(kind):
    from quantumbridge.core.standard_gates import UnitaryGate
    from quantumbridge.core.operations import execution_operation
    from quantumbridge.serialization import qpy_dumps, qpy_loads

    rng = np.random.default_rng(9393)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    raw = UnitaryGate(matrix)
    source = qb.QuantumCircuit(2)
    source.append(raw, [0, 1])
    normalized = execution_operation(source.operations[0]).metadata["gate"]
    def derive(owner):
        if kind == "copy": return owner.copy()
        if kind == "inverse": return owner.inverse()
        if kind == "integer": return owner.power(2)
        if kind == "fractional": return owner.power(.37)
        if kind == "repeat": return owner.repeat(2)
        return owner.control(1, ctrl_state=int(kind == "closed"))
    states = []
    for owner in (raw, normalized):
        gate = derive(owner)
        body = qb.QuantumCircuit(gate.num_qubits, global_phase=.17)
        body.ry(.31, 0)
        body.append(gate, range(gate.num_qubits))
        values = [qb.StatevectorDevice().statevector(body), qb.StatevectorDevice()
            .statevector(qpy_loads(qpy_dumps(body))[0])]
        np.testing.assert_allclose(values[0], values[1], atol=3e-12, rtol=0)
        states.append(values[0])
    np.testing.assert_allclose(states[0], states[1], atol=3e-12, rtol=0)


def test_mixed_literal_and_marked_native_definition_keeps_both_origins():
    from quantumbridge.core.standard_gates import UnitaryGate
    from quantumbridge.core.operations import execution_operation

    matrix = np.diag(np.exp(1j * np.array([.1, .3, .7, -.2])))
    source = qb.QuantumCircuit(2)
    source.unitary(matrix, [0, 1])
    marked = source.data[0].operation
    native_matrix = execution_operation(source.operations[0]).metadata["gate"].to_matrix()
    body = qb.Circuit(2).append(UnitaryGate(matrix), [0, 1]).append(marked, [0, 1])
    public = qb.QuantumCircuit(2)
    public.h(0)
    public.h(1)
    public.append(body.to_gate(), [0, 1])
    expected = native_matrix @ matrix @ (np.ones(4) / 2)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(public), expected, atol=3e-12, rtol=0)


@pytest.mark.parametrize("kind", ["compose", "tensor"])
def test_unproved_compound_operator_origin_is_explicit_and_does_not_mutate_native_math(kind):
    from quantumbridge.information import Operator
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope

    body = qb.QuantumCircuit(2)
    body.ry(.41, 0)
    body.cx(0, 1)
    owner = Operator(body)
    other = Operator(np.diag(np.exp(1j * np.array([.1, .3, .7, -.2]))) if kind == "compose"
        else np.diag([1., 1j]))
    compound = getattr(owner, kind)(other)
    expected = owner.data @ other.data if kind == "compose" else np.kron(owner.data, other.data)
    np.testing.assert_allclose(compound.data, expected, atol=2e-12, rtol=0)
    source = qb.QuantumCircuit(compound.num_qubits)
    source.h(0)
    before = source.to_ir().to_json()
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature) as error:
        source.unitary(compound, range(compound.num_qubits))
    assert error.value.feature == "public_operator_matrix_origin"
    assert source.to_ir().to_json() == before and ledger.receipt()["live_memory_bytes"] == 0


def test_native_inverse_matrix_metadata_keeps_precise_qpy_refusal_without_sidecar():
    import gc
    import io
    from quantumbridge.information import Operator, Statevector
    from quantumbridge.serialization import qpy_dump, qpy_dumps, qpy_loads, UnsupportedFeature
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope

    source = qb.Circuit(2).unitary(np.diag([1., 1j, -1., -1j]), [0, 1]).inverse()
    operation = source.operations[0]
    expected = np.diag([1., 1j, -1., -1j]).conj().T
    assert operation.metadata["matrix"].flags.writeable is False
    np.testing.assert_array_equal(operation.metadata["matrix"], expected)
    payload = qpy_dumps(source, version=13)
    assert payload.startswith(b"QISKIT\r") and b"UnitaryGate" in payload
    assert b"inverse_of" not in payload and b"_native_inverse" not in payload
    restored = qpy_loads(payload)[0]
    assert restored.global_phase == source.global_phase
    np.testing.assert_array_equal(Operator(restored).data, expected)
    vector = np.array([1., 2j, -3., 4j]) / np.sqrt(30)
    np.testing.assert_array_equal(Statevector(vector).evolve(restored).data, expected @ vector)
    reused = qb.QuantumCircuit(2)
    reused.append(restored.copy().inverse().to_gate(), [0, 1])
    np.testing.assert_array_equal(Operator(reused).data, expected.conj().T)

    # Equal public metadata alone is not an inverse-construction witness.
    fake = Operation(operation.name, operation.targets, operation.controls,
        operation.params, dict(operation.metadata))
    assert fake.metadata["matrix"] is operation.metadata["matrix"]
    assert fake.metadata["inverse_of"] == operation.metadata["inverse_of"]
    unqualified = qb.Circuit(2)
    unqualified.operations = [fake]
    before = dict(fake.__dict__)
    stream = io.BytesIO(b"untouched")
    stream.seek(0, 2)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="unitary_dg"):
        qpy_dump(unqualified, stream)
    gc.collect()
    assert stream.getvalue() == b"untouched"
    assert unqualified.operations[0] is fake and source.operations[0] is operation
    assert fake.__dict__.keys() == before.keys()
    assert all(fake.__dict__[key] is value for key, value in before.items())
    np.testing.assert_array_equal(operation.metadata["matrix"], expected)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind", ["definition", "subclass", "container", "measurements", "params", "matrix_parameter", "entry", "owner_origin", "wrapper_origin", "operation_origin", "operator_origin", "public_gate_origin", "public_gate_matrix", "operator_width"])
def test_invalid_matrix_owner_graph_refuses_before_foreign_callbacks_and_has_no_partial_effect(kind):
    from quantumbridge.core.circuit import Circuit
    from quantumbridge.core.standard_gates import UnitaryGate
    from quantumbridge.core.operations import capture_public_frame, execution_operation
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.information import Operator

    calls = []
    class Foreign:
        def touched(self, name):
            calls.append(name)
            raise AssertionError("Foreign callback ran before admission")
        @property
        def operations(self): return self.touched("operations")
        def __iter__(self): return self.touched("iter")
        def __len__(self): return self.touched("len")
        def __getattr__(self, name): return self.touched("getattr:" + name)
    class ForeignCircuit(Circuit):
        @property
        def operations(self):
            calls.append("subclass.operations")
            raise AssertionError("A foreign subclass property ran")
    class ForeignOrigin(str):
        def __eq__(self, other):
            calls.append("origin.eq")
            raise AssertionError("Foreign provenance equality ran")
    class ForeignWidth:
        def __rlshift__(self, other):
            calls.append("width.shift")
            raise AssertionError("Foreign width arithmetic ran")

    body = Circuit(1).h(0)
    owner = Gate("owned", 1, definition=body)
    if kind == "definition": object.__setattr__(owner, "_definition", Foreign())
    elif kind == "subclass": object.__setattr__(owner, "_definition", object.__new__(ForeignCircuit))
    elif kind == "container": owner.definition.operations = Foreign()
    elif kind == "measurements": owner.definition.measurements = Foreign()
    elif kind == "params": object.__setattr__(owner, "_params", Foreign())
    elif kind == "entry": owner.definition.operations = [Foreign()]
    elif kind == "wrapper_origin": object.__setattr__(owner, "_public_matrix_basis", ForeignOrigin("literal_wrapper"))
    elif kind in ("owner_origin", "operation_origin", "matrix_parameter", "public_gate_origin", "public_gate_matrix"):
        owner = UnitaryGate(np.eye(2))
        if kind in ("owner_origin", "public_gate_origin"): object.__setattr__(owner, "_public_matrix_basis", ForeignOrigin("little"))
        if kind in ("matrix_parameter", "public_gate_matrix"): object.__setattr__(owner, "_params", (Foreign(),))
    source = qb.QuantumCircuit(1)
    source.h(0)
    before = source.to_ir().to_json()
    operation = capture_public_frame(Operation(owner.name, (0,), metadata={"gate": owner}), owner.name, ()) if kind != "params" else None
    if kind == "operation_origin": object.__setattr__(operation, "_public_matrix_basis", ForeignOrigin("little"))
    if kind in ("operator_origin", "operator_width"):
        value = Operator(np.eye(2))
        value._public_matrix_basis = ForeignOrigin("native") if kind == "operator_origin" else "native"
        if kind == "operator_width": value.num_qubits = ForeignWidth()
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises((TypeError, ValueError)):
        if kind in ("operator_origin", "operator_width"):
            source.unitary(value, [0])
        elif kind in ("public_gate_origin", "public_gate_matrix"): source.unitary(owner, [0])
        elif kind == "params": _matrix_owner_family(owner)
        else: execution_operation(operation)
    assert not calls
    assert source.to_ir().to_json() == before and len(source.operations) == 1
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("path", ["qpy", "ir_json"])
@pytest.mark.parametrize("modifier", ["source", "copy", "inverse", "power", "repeat", "open", "closed"])
def test_detached_restored_matrix_owner_can_be_reused_without_second_conversion(path, modifier):
    from quantumbridge.serialization import qpy_dumps, qpy_loads
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir

    rng = np.random.default_rng(9696)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    original = qb.QuantumCircuit(2)
    original.unitary(matrix * np.exp(.17j), [0, 1], label="detached-origin")
    restored = qpy_loads(qpy_dumps(original))[0] if path == "qpy" else circuit_from_ir(
        IRProgram.from_json(original.to_ir().to_json()))
    detached = restored.operations[0].metadata["gate"]

    def derive(owner):
        if modifier == "copy": return owner.copy()
        if modifier == "inverse": return owner.inverse()
        if modifier == "power": return owner.power(.37)
        if modifier == "repeat": return owner.repeat(2)
        if modifier in ("open", "closed"): return owner.control(1, ctrl_state=int(modifier == "closed"))
        return owner

    values = []
    for owner in (original.data[0].operation, detached):
        gate = derive(owner)
        body = qb.QuantumCircuit(4, global_phase=.23)
        body.h(1)
        body.ry(.31, 0)
        body.h(3)
        body.append(gate, [0, 3, 1] if gate.num_qubits == 3 else [3, 1])
        value = qb.StatevectorDevice().statevector(body)
        np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=16)
            .matrix_product_state(body).statevector(), value, atol=3e-12, rtol=0)
        values.append(value)
    np.testing.assert_allclose(values[0], values[1], atol=3e-12, rtol=0)
