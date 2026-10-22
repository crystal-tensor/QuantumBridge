# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Instruction execution, staged failures and pre-allocation resource guards."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps, qpy_loads, SerializationLimits, ResourceLimitError


@pytest.mark.parametrize("device_type", [qb.StatevectorDevice, qb.DensityMatrixDevice, qb.MatrixProductStateDevice, qb.StabilizerDevice])
@pytest.mark.parametrize("condition", [None, (0, 1), True])
def test_repeated_nonunitary_instruction_uses_real_measurement_mapping_and_control(device_type, condition):
    body = qb.Circuit(1, 1).reset(0).x(0).measure(0, 0)
    if condition is not None: body = body.if_else(condition, qb.Circuit(1, 1).x(0))
    repeated = body.to_instruction().repeat(2)
    parent = qb.Circuit(3, 4).append(repeated, [2], clbits=[1])
    result = device_type().run_shots(parent, shots=8, seed=7)
    assert result.counts() == {"0100": 8}


@pytest.mark.parametrize("opaque", [True, False])
@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_deferred_unsupported_inverse_is_transported_but_never_executed_as_unitary(opaque, format):
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    source = qb.Instruction("opaque", 1, 0, [.3]) if opaque else qb.Circuit(1).reset(0).to_instruction()
    deferred = source.inverse(annotated=True)
    circuit = qb.Circuit(1).append(deferred, [0])
    restored = circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json())) if format == "ir" else qpy_loads(qpy_dumps(circuit))[0]
    assert type(restored.operations[0].metadata["annotated_operation"]) is qb.AnnotatedOperation
    with pytest.raises((ValueError, qb.UnsupportedFeature)): restored.lowered()
    with pytest.raises((ValueError, qb.UnsupportedFeature)): Operator(restored)


def test_instruction_repeat_admits_aggregate_work_before_any_owned_snapshot(monkeypatch):
    owner = qb.Circuit(1).x(0).h(0).to_instruction()
    def forbidden(*args, **kwargs): pytest.fail("Instruction copied before aggregate work admission.")
    monkeypatch.setattr(qb.Instruction, "copy", forbidden)
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=5)), pytest.raises(MemoryError, match="max_total_operations"):
        owner.repeat(2)


def test_instruction_repeat_rejects_cycle_before_copy(monkeypatch):
    owner = qb.Circuit(1).x(0).to_instruction()
    owner.definition.operations.append(qb.Operation("cycle", (0,), metadata={"instruction_object": owner}))
    def forbidden(*args, **kwargs): pytest.fail("Cyclic definition copied.")
    monkeypatch.setattr(qb.Instruction, "copy", forbidden)
    with pytest.raises(ValueError, match="Cyclic"): owner.repeat(2)


def test_managed_instruction_work_rejects_foreign_metadata_before_callbacks():
    class Foreign(dict):
        def get(self, *args): pytest.fail("Foreign metadata callback ran during managed work admission.")
    owner = qb.Circuit(1).x(0).to_instruction()
    object.__setattr__(owner.definition.operations[0], "metadata", Foreign())
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(qb.UnsupportedFeature): owner.repeat(2)


@pytest.mark.parametrize("direction", ["write", "read"])
def test_repeated_instruction_qpy_keeps_shared_numeric_admission(direction):
    from quantumbridge.circuit_library import UnitaryGate
    owner = qb.Circuit(1).append(UnitaryGate(np.eye(2)), [0]).to_instruction()
    source = qb.Circuit.from_instruction(owner.repeat(2))
    if direction == "write":
        with pytest.raises(ResourceLimitError): qpy_dumps(source, limits=SerializationLimits(max_numeric_elements=5))
    else:
        payload = qpy_dumps(source)
        with pytest.raises(ResourceLimitError): qpy_loads(payload, limits=SerializationLimits(max_numeric_elements=5))


def test_repeated_instruction_symbolic_gradient_hessian_hvp_has_no_dense_hundred_wire_fallback(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): pytest.fail("Instruction repeat used a dense hundred-wire fallback.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p = qb.Parameter("p")
    owner = qb.Circuit(100).ry(2*p+p.sin(), 99).to_instruction()
    node = QNode.from_circuit(qb.Circuit.from_instruction(owner.repeat(2)), qb.PauliZ(99),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0),
        diff_method="parameter-shift", max_diff=2)
    x = .3
    f, df, ddf = 4*x+2*np.sin(x), 4+2*np.cos(x), -2*np.sin(x)
    expected = -np.cos(f)*df*df-np.sin(f)*ddf
    assert node(x) == pytest.approx(np.cos(f), abs=3e-12)
    assert node.compute_jacobian(x) == pytest.approx(-np.sin(f)*df, abs=3e-10)
    assert node.compute_hessian(x) == pytest.approx(expected, abs=5e-10)
    assert node.compute_hvp(.3, x) == pytest.approx(.3*expected, abs=5e-10)


def test_probability_sampler_preserves_repeated_terminal_measurement_bits():
    from types import SimpleNamespace
    from quantumbridge.devices import ShotSampler
    body = qb.Instruction("measure", 1, 1, []).repeat(2)
    source = qb.Circuit(3, 4).x(2).append(body, [2], clbits=[1])
    device = SimpleNamespace(probabilities=qb.StatevectorDevice().probabilities)
    assert ShotSampler(shots=8, seed=7, base_device=device).run(source).counts() == {"0100": 8}


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tensorflow"])
def test_repeated_instruction_native_execution_reaches_real_framework_gradient(interface):
    from quantumbridge.qml import QNode
    p = qb.Parameter("p")
    body = qb.Circuit(1).ry(2*p+p.sin(), 0).to_instruction().repeat(2)
    node = QNode.from_circuit(qb.Circuit.from_instruction(body), qb.PauliZ(0), interface=interface,
        diff_method="parameter-shift", max_diff=2)
    x = .3
    expected = -np.sin(4*x+2*np.sin(x))*(4+2*np.cos(x))
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
    assert actual == pytest.approx(expected, abs=3e-10)


@pytest.mark.parametrize("format", ["qasm2", "qasm3"])
@pytest.mark.parametrize("allow_metadata_loss", [False, True])
def test_qasm_never_discards_an_instruction_reference_as_ordinary_metadata(format, allow_metadata_loss):
    from quantumbridge import serialization
    from quantumbridge.serialization import UnsupportedFeature
    source = qb.Circuit.from_instruction(qb.Circuit(1).rx(.3, 0).to_instruction().repeat(2))
    with pytest.raises(UnsupportedFeature):
        getattr(serialization, format+"_dumps")(source, allow_metadata_loss=allow_metadata_loss)


@pytest.mark.parametrize("corruption", ["label", "width", "clbits", "extra_binding", "non_parameter", "changed_template"])
def test_instruction_ir_rejects_malformed_fields_and_stale_binding_templates(corruption):
    from quantumbridge.ir.qb_ir import IRProgram
    p = qb.Parameter("p")
    owner = qb.Circuit(1).rx(p, 0).to_instruction()
    owner.params[0] = .2
    payload = qb.Circuit.from_instruction(owner.repeat(2)).to_ir().to_dict()
    record = payload["instructions"][0]["metadata"]["instruction_object"]
    if corruption == "label": record["label"] = 3
    elif corruption == "width": record["num_qubits"] = 2
    elif corruption == "clbits": record["num_clbits"] = 1
    elif corruption == "extra_binding": record["parameter_binding"]["foreign"] = True
    elif corruption == "non_parameter": record["parameter_binding"]["formals"] = [.2]
    else: record["parameter_binding"]["definition"]["instructions"][0]["params"] = [.8]
    with pytest.raises((TypeError, ValueError)): IRProgram.from_dict(payload)


def test_instruction_ir_parameter_count_is_checked_before_owner_materialization(monkeypatch):
    from quantumbridge.ir.qb_ir import IRProgram
    source = qb.Circuit.from_instruction(qb.Instruction("opaque", 1, 0, [.3]).repeat(2)).to_ir().to_dict()
    source["instructions"][0]["metadata"]["instruction_object"]["params"] = [.3, .4]
    def forbidden(*args, **kwargs): pytest.fail("Instruction materialized before its declared parameter budget.")
    monkeypatch.setattr(qb.Instruction, "__init__", forbidden)
    with pytest.raises(ResourceLimitError):
        IRProgram.from_dict(source, serialization_limits=SerializationLimits(max_parameter_nodes=1))


def test_repeated_instruction_control_reuses_structural_engine_for_hundred_wire_mps(monkeypatch):
    from quantumbridge.qml import QNode
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args, **kwargs): pytest.fail("Coherent repeat control used a dense hundred-wire fallback.")
    for kind, method in [(qb.Gate, "to_matrix"), (qb.StatevectorDevice, "statevector"),
            (qb.DensityMatrixDevice, "density_matrix"), (MatrixProductState, "statevector")]:
        monkeypatch.setattr(kind, method, forbidden)
    p = qb.Parameter("p")
    body = qb.Circuit(100).ry(p, 99).to_instruction().repeat(2)
    controlled = body.control(1)
    source = qb.Circuit(101).x(0).append(controlled, range(101))
    node = QNode.from_circuit(source, qb.PauliZ(100),
        device=qb.MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0),
        diff_method="parameter-shift", max_diff=2)
    assert node(.3) == pytest.approx(np.cos(.6), abs=3e-12)
    assert node.compute_jacobian(.3) == pytest.approx(-2*np.sin(.6), abs=3e-10)
