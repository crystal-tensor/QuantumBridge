# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Principal controlled powers, public return objects and real execution chains."""

import cmath
import gc

import numpy as np
import pytest

import quantumbridge as qb
import quantumbridge.circuit_library as library
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps, qpy_loads


AXES = {"CRXGate": np.array([[0, 1], [1, 0]], complex),
        "CRYGate": np.array([[0, -1j], [1j, 0]], complex),
        "CRZGate": np.diag([1., -1.])}


def principal_rotation(name, angle, power):
    pauli = AXES[name]
    result = np.zeros((2, 2), complex)
    for sign in (-1, 1):
        value = cmath.exp(-.5j * sign * angle)
        scalar = value ** int(power) if float(power).is_integer() else cmath.exp(power * (np.log(abs(value)) + 1j * cmath.phase(value)))
        result += scalar * (np.eye(2) + sign * pauli) / 2
    return result


def controlled(matrix, state):
    result = np.eye(4, dtype=complex)
    result[2*state:2*state+2, 2*state:2*state+2] = matrix
    return result


@pytest.mark.parametrize("name", AXES)
@pytest.mark.parametrize("angle", [.31, 7.3, -9.1])
@pytest.mark.parametrize("state", [0, 1])
@pytest.mark.parametrize("power", [-1, .5, -.3, 2])
@pytest.mark.parametrize("annotated", [False, True])
def test_controlled_rotation_power_matches_independent_projector_oracle(name, angle, state, power, annotated):
    source = getattr(library, name)(angle, ctrl_state=state, label="source")
    before = Operator(source).data.copy()
    result = source.power(power, annotated=annotated)
    assert type(result) is (qb.AnnotatedOperation if annotated else library.UnitaryGate)
    expected = controlled(principal_rotation(name, angle, power), state)
    np.testing.assert_allclose(Operator(result).data, expected, atol=2e-12, rtol=0)
    np.testing.assert_array_equal(Operator(source).data, before)
    assert source.ctrl_state == state and source.params == [angle] and source.label == "source"


@pytest.mark.parametrize("name", AXES)
@pytest.mark.parametrize("power", [2, .5])
def test_symbolic_controlled_power_requires_deferred_mode_then_binds_to_the_correct_branch(name, power):
    parameter = qb.ParameterVector("angle", 2)[1]
    source = getattr(library, name)(parameter, ctrl_state=0)
    with pytest.raises(TypeError):
        source.power(power)
    result = source.power(power, annotated=True)
    assert type(result) is qb.AnnotatedOperation
    circuit = qb.QuantumCircuit(2)
    circuit.append(result, [0, 1])
    assert tuple(circuit.parameters) == (parameter,)
    bound = circuit.assign_parameters({parameter: 7.3})
    np.testing.assert_allclose(Operator(bound).data, controlled(principal_rotation(name, 7.3, power), 0), atol=2e-12, rtol=0)


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("name", AXES)
@pytest.mark.parametrize("annotated", [False, True])
def test_fractional_power_copy_inverse_decompose_roundtrip_reaches_state_and_density(name, format, annotated):
    powered = getattr(library, name)(7.3, ctrl_state=0).power(.5, annotated=annotated)
    parameter = qb.Parameter("phase")
    register = qb.QuantumRegister(2, "register")
    alias = qb.QuantumRegister(name="alias", bits=[register[0]])
    source = qb.QuantumCircuit(register, alias, global_phase=parameter)
    source.append(powered, register)
    source.metadata = {"user": ["untouched"], "global_phase": "not execution phase"}
    stages = [source.copy()]
    stages.append(stages[-1].inverse())
    stages.append(stages[-1].decompose(reps=1))
    stages.append(stages[-1].assign_parameters({parameter: .19}))
    assert all(type(stage) is qb.QuantumCircuit for stage in stages)
    result = stages[-1]
    expected = np.exp(-.19j) * controlled(principal_rotation(name, 7.3, .5), 0).conj().T
    restored = qpy_loads(qpy_dumps(result))[0] if format == "qpy" else circuit_from_ir(IRProgram.from_json(result.to_ir().to_json()))
    np.testing.assert_allclose(Operator(restored).data, expected, atol=3e-12, rtol=0)
    assert len(restored.find_bit(restored.qubits[0]).registers) == 2
    assert restored.metadata == result.metadata == {}
    assert source.metadata == {"user": ["untouched"], "global_phase": "not execution phase"}
    assert tuple(source.parameters) == (parameter,) and not result.parameters
    vector = np.array([1, 2j, -.3, .7j], complex)
    vector /= np.linalg.norm(vector)
    density = np.outer(vector, vector.conj())
    np.testing.assert_allclose(Statevector(vector).evolve(restored).data, expected @ vector, atol=3e-12, rtol=0)
    np.testing.assert_allclose(DensityMatrix(density).evolve(restored).data, expected @ density @ expected.conj().T, atol=3e-12, rtol=0)


@pytest.mark.parametrize("state", [0, 1])
@pytest.mark.parametrize("power", [-1, .5, 2])
def test_specialized_controlled_phase_scaling_retains_its_open_control(state, power):
    gate = library.CPhaseGate(7.3, ctrl_state=state).power(power)
    assert type(gate) is library.CPhaseGate and gate.ctrl_state == state
    expected = controlled(np.diag([1., cmath.exp(7.3j * power)]), state)
    np.testing.assert_allclose(Operator(gate).data, expected, atol=2e-12, rtol=0)


def test_generic_fractional_gate_power_reuses_the_guarded_operator_engine_in_managed_scope():
    source = library.CRYGate(7.3, ctrl_state=0)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        result = source.power(.5)
    np.testing.assert_allclose(Operator(result).data, controlled(principal_rotation("CRYGate", 7.3, .5), 0), atol=2e-12, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == result.params[0].nbytes
    view = result.params[0][0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 256
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("budget", ["memory", "dimension", "work"])
def test_fractional_power_preflight_rejects_before_operator_workspace_and_leaves_owner_unchanged(budget, monkeypatch):
    source = library.CRXGate(7.3, ctrl_state=0)
    before = tuple(source.params), source.ctrl_state, source.definition
    def forbidden(*args, **kwargs):
        pytest.fail("spectral allocation preceded resource admission")
    monkeypatch.setattr(np.linalg, "eig", forbidden)
    monkeypatch.setattr(np.linalg, "qr", forbidden)
    limits = GateCircuitLimits(max_matrix_dimension=2) if budget == "dimension" else GateCircuitLimits(max_decomposition_work=1) if budget == "work" else GateCircuitLimits()
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0 if budget == "memory" else 10**7))
    with gate_circuit_scope(limits), ResourceScope(ledger), pytest.raises(MemoryError):
        source.power(.5)
    assert (tuple(source.params), source.ctrl_state, source.definition) == before
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_managed_fractional_power_rejects_foreign_exponent_before_any_callback():
    class Foreign(float):
        def __float__(self): pytest.fail("foreign float callback")
        def __eq__(self, other): pytest.fail("foreign equality callback")
        def __mul__(self, other): pytest.fail("foreign multiplication callback")
    source = library.CRXGate(.3)
    with ResourceScope(UnifiedResourceLedger()), pytest.raises(UnsupportedFeature):
        source.power(Foreign(.5))


@pytest.mark.parametrize("name", ["XGate", "YGate", "ZGate", "HGate", "IGate", "SwapGate"])
def test_self_inverse_fixed_gate_returns_its_unlabelled_immutable_public_class(name):
    source = getattr(library, name)(label="source")
    result = source.inverse(annotated=True)
    assert type(result) is type(source) and result.label is None and result.mutable is False
    assert source.label == "source" and source.mutable is True


def test_unitary_inverse_annotation_flag_keeps_the_specialized_public_object():
    source = library.UnitaryGate(np.diag([1, 1j]), label="source")
    result = source.inverse(annotated=True)
    assert type(result) is library.UnitaryGate
    np.testing.assert_array_equal(result.to_matrix(), np.diag([1, -1j]))
    assert not np.shares_memory(result.params[0], source.params[0])


@pytest.mark.parametrize("power", [-1, .5, -.3, 2])
def test_operator_power_legal_unitary_subset_reaches_public_circuit_and_native_states(power, record_property):
    phases = np.array([.2, -.7, 1.3, -2.1])
    fourier = np.exp(2j*np.pi*np.outer(np.arange(4), np.arange(4))/4)/2
    matrix = fourier @ np.diag(np.exp(1j*phases)) @ fourier.conj().T
    expected = fourier @ np.diag(np.exp(1j*power*phases)) @ fourier.conj().T
    powered = Operator(matrix).power(power, branch_cut_rotation=0)
    np.testing.assert_allclose(powered.data, expected, atol=3e-12, rtol=0)
    native = qb.Circuit(2)
    assert native.unitary(powered.data, [0, 1]) is native
    np.testing.assert_allclose(Operator(native).data, expected, atol=3e-12, rtol=0)
    circuit = qb.QuantumCircuit(2)
    circuit.append(library.UnitaryGate(powered.data), [0, 1])
    # PUBLIC_ENTRY_EXPECTATION_CORRECTION: a bare matrix passed to a public
    # UnitaryGate loses its earlier Operator provenance; qargs are little-first.
    public_expected = expected.reshape(2, 2, 2, 2).transpose(1, 0, 3, 2).reshape(4, 4)
    record_property("expectation_correction", "PUBLIC_ENTRY_EXPECTATION_CORRECTION")
    np.testing.assert_allclose(Operator(circuit).data, public_expected, atol=3e-12, rtol=0)
    vector = np.array([1., 1j, .2, -.3j]); vector /= np.linalg.norm(vector)
    density = np.outer(vector, vector.conj())
    np.testing.assert_allclose(Statevector(vector).evolve(native).data, expected@vector, atol=3e-12, rtol=0)
    np.testing.assert_allclose(DensityMatrix(density).evolve(native).data, expected@density@expected.conj().T, atol=3e-12, rtol=0)
    np.testing.assert_allclose(Statevector(vector).evolve(circuit).data, public_expected@vector, atol=3e-12, rtol=0)
    np.testing.assert_allclose(DensityMatrix(density).evolve(circuit).data, public_expected@density@public_expected.conj().T, atol=3e-12, rtol=0)


@pytest.mark.parametrize("power", [1, .5, 2])
def test_a_computable_nonunitary_operator_power_cannot_be_promoted_to_a_unitary_gate(power):
    matrix = Operator(np.diag([2., 3.])).power(power).data
    np.testing.assert_allclose(matrix, np.diag([2.**power, 3.**power]), atol=3e-12, rtol=0)
    with pytest.raises(ValueError, match="unitary"):
        library.UnitaryGate(matrix)


@pytest.mark.parametrize("width", [0, 1, 2])
def test_public_factory_promotes_numeric_matrix_to_an_owned_unitary_not_an_opaque_generic_definition(width):
    matrix = np.diag(np.exp(1j*np.linspace(.1, .7, 1<<width)))
    source = qb.QuantumCircuit(width)
    source.append(library.UnitaryGate(matrix), range(width))
    out = source.copy().inverse().decompose(reps=1)
    assert type(out.data[0].operation) is library.UnitaryGate
    restored = qpy_loads(qpy_dumps(out))[0]
    expected = matrix.conj().T
    native = qb.Circuit(width).unitary(matrix, range(width))
    np.testing.assert_allclose(Operator(native.inverse()).data, expected, atol=2e-12, rtol=0)
    native_restored = qpy_loads(qpy_dumps(native))[0].inverse()
    np.testing.assert_allclose(Operator(native_restored).data, expected, atol=2e-12, rtol=0)
    if width == 2:
        # PUBLIC_ENTRY_EXPECTATION_CORRECTION: width=2 only, actual public qargs.
        expected = expected.reshape(2, 2, 2, 2).transpose(1, 0, 3, 2).reshape(4, 4)
    np.testing.assert_allclose(Operator(restored).data, expected, atol=2e-12, rtol=0)
