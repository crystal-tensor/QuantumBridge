# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public-shaped native conversions with independent dense/tensor oracles."""

from contextlib import nullcontext
import gc
from itertools import product

import numpy as np
import pytest

from quantumbridge import Circuit, Instruction, Parameter
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


CUSTOM = np.array([[1,0,0,0],[0,0,1j,0],[0,1,0,0],[0,0,0,-1j]],complex)
CX = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)


def fixture(angle=.43):
    parameter = Parameter("bridge_angle")
    block = Circuit(2).h(0).ry(parameter,1).cx(0,1).rz(-.29,0)
    block.global_phase = .37 + parameter/3
    circuit = Circuit(3).rx(-.2,1)
    circuit.append(block.to_instruction(),(2,0))
    circuit.unitary(CUSTOM,(0,2))
    circuit.rz(.13,1)
    return circuit.assign_parameters({parameter:angle})


def gate_sequence(angle=.43):
    h = np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    ry = np.array([[np.cos(angle/2),-np.sin(angle/2)],[np.sin(angle/2),np.cos(angle/2)]],complex)
    rx = np.array([[np.cos(-.1),-1j*np.sin(-.1)],[-1j*np.sin(-.1),np.cos(-.1)]],complex)
    rz = lambda value:np.diag([np.exp(-.5j*value),np.exp(.5j*value)])
    return [(rx,(1,)),(h,(2,)),(ry,(0,)),(CX,(2,0)),(rz(-.29),(2,)),(CUSTOM,(0,2)),(rz(.13),(1,))]


def embedded_product(sequence, width, phase):
    """Basis enumeration and dense products, independent of native kernels."""
    total = np.eye(2**width,dtype=complex)
    for matrix,wires in sequence:
        embedded = np.zeros_like(total)
        for column,bits in enumerate(product((0,1),repeat=width)):
            local_column = sum(bits[wire]*2**(len(wires)-1-position) for position,wire in enumerate(wires))
            for local_row,replacement in enumerate(product((0,1),repeat=len(wires))):
                output = list(bits)
                for wire,bit in zip(wires,replacement):output[wire]=bit
                row = sum(bit*2**(width-1-position) for position,bit in enumerate(output))
                embedded[row,column] = matrix[local_row,local_column]
        total = embedded @ total
    return np.exp(1j*phase)*total


def tensor_action(state, sequence, width, phase):
    """Per-gate tensor contraction; no embedded matrix or production helper."""
    tensor = state.reshape((2,)*width)
    for matrix,wires in sequence:
        gate = matrix.reshape((2,)*(2*len(wires)))
        tensor = np.tensordot(gate,tensor,axes=(tuple(range(len(wires),2*len(wires))),wires))
        order = wires+tuple(wire for wire in range(width) if wire not in wires)
        tensor = tensor.transpose(tuple(order.index(wire) for wire in range(width)))
    return np.exp(1j*phase)*tensor.reshape(-1)


def vector(width):
    values = np.arange(1,2**width+1)
    state = np.cos(values)+1j*np.sin(2*values)
    return state/np.linalg.norm(state)


@pytest.mark.parametrize("angle", [.43,-1.2])
@pytest.mark.parametrize("managed", [False,True])
@pytest.mark.parametrize("kind", ["circuit","instruction","matrix_instruction"])
def test_full_complex_operator_and_states_match_two_independent_oracles(angle,managed,kind):
    circuit = fixture(angle)
    reference = embedded_product(gate_sequence(angle),3,.37+angle/3)
    for column in range(8):
        np.testing.assert_allclose(reference[:,column],tensor_action(np.eye(8,dtype=complex)[:,column],gate_sequence(angle),3,.37+angle/3),atol=5e-15,rtol=0)
    value = circuit if kind=="circuit" else circuit.to_instruction() if kind=="instruction" else Instruction("custom",3,metadata={"matrix":reference})
    with ResourceScope(Ledger()) if managed else nullcontext():
        operator = Operator(value)
        state = Statevector.from_instruction(value)
        density = DensityMatrix.from_instruction(value)
        constructed_state = Statevector(value)
        constructed_density = DensityMatrix(value)
    np.testing.assert_allclose(operator.data,reference,atol=5e-15,rtol=0)
    expected = reference[:,0]
    for result in (state,constructed_state):
        np.testing.assert_allclose(result.data,expected,atol=5e-15,rtol=0)
        assert result.dims()==(2,2,2)
    for result in (density,constructed_density):
        np.testing.assert_allclose(result.data,np.outer(expected,expected.conj()),atol=6e-15,rtol=0)
        assert result.dims()==(2,2,2)
    assert operator.input_dims()==operator.output_dims()==(2,2,2)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("managed", [False,True])
@pytest.mark.parametrize("targets", [(0,1,2),(3,0,2),(2,1,0)])
def test_instruction_evolution_preserves_input_complex_amplitudes_and_target_order(cls,managed,targets):
    source = vector(4)
    before = source.copy()
    sequence = [(matrix,tuple(targets[wire] for wire in wires)) for matrix,wires in gate_sequence()]
    expected = tensor_action(source,sequence,4,.37+.43/3)
    dense = embedded_product(sequence,4,.37+.43/3)
    np.testing.assert_allclose(expected,dense@source,atol=6e-15,rtol=0)
    value = Statevector(source) if cls is Statevector else DensityMatrix.from_statevector(source)
    with ResourceScope(Ledger()) if managed else nullcontext():
        direct = value.evolve(fixture(),qargs=targets)
        result = value.evolve(fixture().to_instruction(),qargs=targets)
    expected = expected if cls is Statevector else np.outer(expected,expected.conj())
    np.testing.assert_allclose(result.data,expected,atol=7e-15,rtol=0)
    np.testing.assert_allclose(direct.data,expected,atol=7e-15,rtol=0)
    np.testing.assert_array_equal(source,before)
    assert result.dims()==(2,)*4


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
@pytest.mark.parametrize("dims", [(3,2),(2,4),(2,3,2)])
@pytest.mark.parametrize("managed", [False,True])
def test_typed_mixed_radix_state_to_operator_is_actual_numeric_conversion(cls,dims,managed):
    size = int(np.prod(dims))
    data = np.arange(1,size+1)+1j*np.arange(size,0,-1)
    data /= np.linalg.norm(data)
    state = Statevector(data,dims=dims)
    value = state if cls is Statevector else DensityMatrix.from_statevector(state)
    with ResourceScope(Ledger()) if managed else nullcontext():result=value.to_operator()
    np.testing.assert_allclose(result.data,np.outer(data,data.conj()),atol=1e-15,rtol=0)
    assert result.input_dims()==result.output_dims()==dims
    assert result.num_qubits is None


def test_two_actual_function_chains_end_in_independent_expectations_and_purity():
    circuit = fixture()
    sequence = gate_sequence()
    source = vector(3)
    expected = tensor_action(source,sequence,3,.37+.43/3)
    matrix = embedded_product(sequence,3,.37+.43/3)
    observable = np.diag(np.arange(8))+1j*np.eye(8,k=1)
    # Chain A: bound Circuit -> Operator -> Statevector.evolve -> expectation.
    with ResourceScope(Ledger()):
        evolved = Statevector(source).evolve(Operator(circuit))
        expectation = evolved.expectation_value(Operator(observable))
    assert expectation==pytest.approx(expected.conj()@observable@expected,abs=1e-14)
    np.testing.assert_allclose(evolved.data,matrix@source,atol=5e-15,rtol=0)
    # Chain B: Circuit -> composite Instruction -> density -> reduction -> purity.
    with ResourceScope(Ledger()):
        density = DensityMatrix.from_statevector(source).evolve(circuit.to_instruction())
        reduced = density.partial_trace([2,0])
        purity = reduced.purity()
        expectation_b = reduced.expectation_value(Operator(np.diag([1.,-2.,3.,-.5])))
    # Existing native keep semantics retain original subsystem order, not keep-list order.
    tensor = expected.reshape(2,2,2).transpose(0,2,1).reshape(4,2)
    reference = tensor@tensor.conj().T
    np.testing.assert_allclose(reduced.data,reference,atol=6e-15,rtol=0)
    assert purity==pytest.approx(np.trace(reference@reference),abs=1e-14)
    assert expectation_b==pytest.approx(np.trace(reference@np.diag([1.,-2.,3.,-.5])),abs=1e-14)


@pytest.mark.parametrize("kind", ["measurement","reset","unbound"])
def test_dynamic_and_unbound_instruction_never_become_a_unitary(kind):
    circuit = Circuit(1,1)
    if kind=="measurement":circuit.h(0).measure(0,0)
    elif kind=="reset":circuit.h(0).reset(0)
    else:circuit.ry(Parameter("unbound"),0)
    instruction = circuit.to_instruction()
    with pytest.raises((TypeError,ValueError,UnsupportedFeature)):Operator(instruction)
    if kind=="unbound":
        for cls in (Statevector,DensityMatrix):
            with pytest.raises((TypeError,ValueError,UnsupportedFeature)):cls.from_instruction(instruction)
    elif kind=="reset":
        with pytest.raises((ValueError,UnsupportedFeature)):Statevector.from_instruction(instruction)
        np.testing.assert_allclose(DensityMatrix.from_instruction(instruction).data,[[1,0],[0,0]],atol=1e-15,rtol=0)
    else:
        # Native terminal-measurement pure-state convention is retained.
        np.testing.assert_allclose(DensityMatrix.from_instruction(instruction).data,np.eye(2)/2,atol=1e-15,rtol=0)


def test_existing_operator_from_circuit_cannot_silently_discard_terminal_measurement():
    with pytest.raises(ValueError):Operator.from_circuit(Circuit(1,1).h(0).measure(0,0))


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_qudit_circuit_ir_guard_remains_even_for_power_of_two_total_dimension(cls,monkeypatch):
    value = Statevector(np.ones(8)/np.sqrt(8),dims=(2,4))
    if cls is DensityMatrix:value=DensityMatrix.from_statevector(value)
    instruction = Circuit(3).h(0).to_instruction()
    monkeypatch.setattr(Operator,"from_circuit",lambda *a,**k:pytest.fail("Qudit state reached binary operator conversion"))
    with pytest.raises(UnsupportedFeature):value.evolve(instruction)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_invalid_instruction_targets_reject_without_mutating_input(cls):
    source = Statevector(vector(3))
    value = source if cls is Statevector else DensityMatrix.from_statevector(source)
    before = value.data.copy()
    instruction = Circuit(2).cx(0,1).to_instruction()
    for selected in ((0,),(0,0),(0,3),(-1,0),(True,0)):
        with pytest.raises((ValueError,TypeError,UnsupportedFeature)):
            value.evolve(instruction,qargs=selected)
    np.testing.assert_array_equal(value.data,before)


def test_conversion_output_admission_and_escaped_view_ownership(monkeypatch):
    value = Statevector(vector(3),dims=(2,4))
    amount = 8*8*16
    ledger = Ledger(Limits(max_total_memory_bytes=amount-1))
    with ResourceScope(ledger),monkeypatch.context() as patch:
        patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Projector output allocated before admission"))
        with pytest.raises(MemoryError):value.to_operator()
    assert ledger.receipt()["live_memory_bytes"]==0
    ledger = Ledger()
    with ResourceScope(ledger):result=value.to_operator()
    view = result.data[:,0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(ledger):recovered=value.to_operator()
    assert recovered.input_dims()==(2,4)


def test_numeric_instruction_normalization_admits_metadata_copy_before_factory(monkeypatch):
    instruction = Instruction("custom",2,metadata={"matrix":CUSTOM})
    ledger = Ledger(Limits(max_total_memory_bytes=CUSTOM.nbytes-1))
    with ResourceScope(ledger),pytest.raises(MemoryError):
        Circuit.from_instruction(instruction)
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(Ledger()):circuit=Circuit.from_instruction(instruction)
    np.testing.assert_array_equal(circuit.operations[0].metadata["matrix"],CUSTOM)
    assert not np.shares_memory(circuit.operations[0].metadata["matrix"],CUSTOM)


@pytest.mark.parametrize("cls", [Operator,Statevector,DensityMatrix])
def test_circuit_constructor_output_lease_survives_views_and_failure_recovers(cls,monkeypatch):
    circuit = Circuit(3).h(0).cx(0,1)
    amount = 128 if cls is Statevector else 1024
    failed = Ledger(Limits(max_total_memory_bytes=amount-1))
    with ResourceScope(failed),monkeypatch.context() as patch:
        patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Constructor output allocated before admission"))
        with pytest.raises(MemoryError):cls(circuit)
    gc.collect()
    assert failed.receipt()["live_memory_bytes"]==0
    ledger = Ledger()
    with ResourceScope(ledger):result=cls(circuit)
    view = result.data.reshape(-1)[::2]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(failed):
        # The same ledger remains usable for an actual smaller circuit result.
        recovered = cls(Circuit(1))
    assert recovered.num_qubits==1


@pytest.mark.parametrize("dtype", [complex,np.complex64,float])
def test_projector_strided_unnormalized_input_is_not_repaired(dtype):
    backing = np.arange(1,25).astype(dtype)
    if dtype is not float:backing+=1j*np.arange(24,0,-1)
    raw = backing[::3]
    state = Statevector(np.ones(8),dims=(2,4))
    state.data = raw
    before = raw.copy()
    with ResourceScope(Ledger()):result=state.to_operator()
    np.testing.assert_array_equal(result.data,np.outer(raw.astype(complex),raw.astype(complex).conj()))
    np.testing.assert_array_equal(raw,before)
    assert result.input_dims()==result.output_dims()==(2,4)


def test_owned_source_projector_outside_scope_retains_source_ledger():
    from quantumbridge.execution.array_ownership import storage_ledger
    ledger = Ledger()
    with ResourceScope(ledger):state=Statevector.from_label("r+-")
    result = state.to_operator()
    assert storage_ledger(result.data) is ledger
    del state
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==8*8*16
    view = result.data[:,0]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==8*8*16
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_invalid_mapped_instruction_rejects_before_metadata_copy(cls,monkeypatch):
    value = Statevector(vector(3))
    if cls is DensityMatrix:value=DensityMatrix.from_statevector(value)
    instruction = Instruction("custom",2,metadata={"matrix":CUSTOM})
    with ResourceScope(Ledger()),monkeypatch.context() as patch:
        patch.setattr(np,"empty",lambda *a,**k:pytest.fail("Bad targets reached metadata/output copy"))
        for selected in ((0,),(0,0),(0,4),(True,0)):
            with pytest.raises(ValueError):value.evolve(instruction,qargs=selected)


@pytest.mark.parametrize("cls", [Operator,Statevector,DensityMatrix])
def test_managed_constructors_do_not_execute_opaque_array_or_instruction_protocols(cls):
    class Foreign:
        def __array__(self,*a,**k):pytest.fail("Opaque array protocol executed")
        def to_matrix(self):pytest.fail("Opaque matrix protocol executed")
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):cls(Foreign())
    if cls is not Operator:
        with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):cls.from_instruction(Foreign())


@pytest.mark.parametrize("angle", [.43,-1.2])
def test_existing_static_circuit_paths_already_match_independent_oracles(angle):
    circuit = fixture(angle)
    expected = embedded_product(gate_sequence(angle),3,.37+angle/3)
    np.testing.assert_allclose(Operator.from_circuit(circuit).data,expected,atol=5e-15,rtol=0)
    np.testing.assert_allclose(Statevector.from_circuit(circuit).data,expected[:,0],atol=5e-15,rtol=0)
    np.testing.assert_allclose(DensityMatrix.from_circuit(circuit).data,np.outer(expected[:,0],expected[:,0].conj()),atol=6e-15,rtol=0)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_optional_public_instruction_conversions_have_explicit_endian_mapping(cls):
    qiskit = pytest.importorskip("qiskit")
    info = pytest.importorskip("qiskit.quantum_info")
    public = qiskit.QuantumCircuit(3)
    # Public wire 0 is low-order; reverse local unitary wires as well.
    public.rx(-.2,1)
    public.h(0)
    public.ry(.43,2)
    public.cx(0,2)
    public.rz(-.29,0)
    public.unitary(CUSTOM,[0,2])
    public.rz(.13,1)
    public.global_phase = .37+.43/3
    public_cls = info.Statevector if cls is Statevector else info.DensityMatrix
    native = cls.from_instruction(fixture().to_instruction())
    reference = public_cls.from_instruction(public.to_instruction())
    np.testing.assert_allclose(native.data,reference.data,atol=6e-15,rtol=0)
    np.testing.assert_allclose(Operator(fixture()).data,info.Operator(public).data,atol=6e-15,rtol=0)
    source = Statevector(vector(4))
    if cls is DensityMatrix:source=DensityMatrix.from_statevector(source)
    value = source.evolve(fixture().to_instruction(),qargs=[3,0,2])
    expected = public_cls(source.data).evolve(public.to_instruction(),qargs=[1,3,0])
    np.testing.assert_allclose(value.data,expected.data,atol=8e-15,rtol=0)


@pytest.mark.parametrize("cls", [Statevector,DensityMatrix])
def test_optional_public_typed_operator_conversion_retains_subsystem_partition(cls):
    info = pytest.importorskip("qiskit.quantum_info")
    state = Statevector(vector(3),dims=(2,4))
    public_cls = info.Statevector if cls is Statevector else info.DensityMatrix
    value = state if cls is Statevector else DensityMatrix.from_statevector(state)
    public = info.Statevector(state.data,dims=(4,2))
    if cls is DensityMatrix:public=public_cls(public)
    result = value.to_operator()
    expected = public.to_operator()
    np.testing.assert_allclose(result.data,expected.data,atol=1e-15,rtol=0)
    assert result.input_dims()==expected.input_dims()[::-1]
