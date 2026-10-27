# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Framework-free admission for an optional native local TF specialization."""

import builtins

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.interfaces.tensorflow_native_execution import TensorFlowLocalOperator
from quantumbridge.qml import QNode


def plan(width=1):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(width).rx(p, 0).rz(q, 0) if width == 1 else qb.Circuit(width).rxx(p, 0, 1).rz(q, 0)
    source = qb.QuantumCircuit(width)
    source.append(body.to_gate().power(0.5, annotated=True), range(width))
    return QNode.from_circuit(source, qb.PauliZ(0), max_diff=2)._construct((np.array([0.37, 0.82]),), {})


@pytest.fixture
def forbid_framework_import(monkeypatch):
    original = builtins.__import__
    def check(name, *args, **kwargs):
        if name.split(".")[0] in {"tensorflow", "qiskit", "pennylane"}:
            pytest.fail("Structural native admission imported an optional framework/SDK")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", check)


def test_structural_admission_needs_no_framework_or_numeric_matrix_evaluation(forbid_framework_import, monkeypatch):
    from quantumbridge.core.gates import Gate
    from quantumbridge.diff import matrix_power_jet
    current = plan()
    before = current.circuit.to_ir().to_json()
    def forbidden(*args, **kwargs):
        pytest.fail("Structural local admission evaluated a quantum matrix")
    monkeypatch.setattr(Gate, "to_matrix", forbidden)
    monkeypatch.setattr(matrix_power_jet, "matrix_power_value", forbidden)
    monkeypatch.setattr(matrix_power_jet, "_body_directions", forbidden)
    kernel = TensorFlowLocalOperator(current, 0)
    assert kernel.input_size == 2 and kernel.wires == (0,)
    assert len(kernel.source_parameter_uuids) == 2
    assert current.circuit.to_ir().to_json() == before


@pytest.mark.parametrize("index", [True, -1, 1, 0.5])
def test_malformed_compiled_occurrence_index_is_rejected(index, forbid_framework_import):
    with pytest.raises(ValueError, match="index"):
        TensorFlowLocalOperator(plan(), index)


def test_foreign_parameter_identity_does_not_bind_by_name(forbid_framework_import):
    current = plan()
    current.recorder.parameters = [qb.Parameter(parameter.name) for parameter in current.recorder.parameters]
    with pytest.raises(ValueError, match="identity"):
        TensorFlowLocalOperator(current, 0)


def test_unvalidated_multiqubit_source_refuses_without_tensorflow(forbid_framework_import):
    with pytest.raises(UnsupportedFeature, match="multi-qubit"):
        TensorFlowLocalOperator(plan(2), 0)


def test_local_dimension_limit_is_checked_before_optional_import(forbid_framework_import):
    current = plan()
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=4)), pytest.raises(MemoryError, match="max_matrix_dimension"):
        TensorFlowLocalOperator(current, 0)


def test_kernel_does_not_accept_a_second_circuit_or_ir_store(forbid_framework_import):
    with pytest.raises(TypeError, match="existing native ExecutionPlan"):
        TensorFlowLocalOperator(qb.Circuit(1), 0)


def test_malformed_operand_frame_is_rejected_before_optional_import(forbid_framework_import):
    from dataclasses import replace
    current = plan()
    current.circuit = current.circuit.lowered()
    current.circuit.operations = [replace(current.circuit.operations[0], targets=())]
    with pytest.raises(ValueError, match="operand frame"):
        TensorFlowLocalOperator(current, 0)


def test_duplicate_recorder_identities_are_not_silently_collapsed(forbid_framework_import):
    current = plan()
    current.recorder.parameters = [current.recorder.parameters[0]]*2
    with pytest.raises(ValueError, match="duplicate parameter identities"):
        TensorFlowLocalOperator(current, 0)
