# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual sparse return types, aliases and shaped Observable ownership."""
import gc
import numpy as np
import pytest

from quantumbridge import Circuit, SparseObservable, StatevectorEstimator
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.primitives import ObservablesArray


def test_scalar_coerce_slice_and_raw_array_have_real_native_sparse_types():
    sparse = ObservablesArray.coerce_observable("-Z")
    assert isinstance(sparse, SparseObservable) and sparse.num_qubits == 2
    array = ObservablesArray([["Z"], ["X"]])
    scalar = array.slice((0, 0))
    assert isinstance(scalar, SparseObservable)
    assert scalar is array.slice((0, 0))
    scalar.coeffs[0] = 3
    assert array.tolist() == [[{"Z": 3.0}], [{"X": 1.0}]]
    raw = array.sparse_observables_array(copy=False)
    assert raw.shape == (2, 1) and raw.dtype == object
    raw[1, 0] = SparseObservable("Y")
    assert array[1, 0] == {"Y": 1.0}
    assert all(isinstance(item, ObservablesArray) for item in array)
    assert array.reshape(-1).shape == (2,)


def test_object_export_copy_and_reshape_share_only_the_expected_owners():
    array = ObservablesArray([["Z"], ["X"]])
    copied = array.sparse_observables_array(copy=True)
    copied[0, 0].coeffs[0] = 8
    assert array[0, 0] == {"Z": 1.0}
    view = array.reshape(2)
    view.slice(0).coeffs[0] = 2
    assert array[0, 0] == {"Z": 2.0}
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        array = ObservablesArray(["Z", "X"])
        raw = array.sparse_observables_array(copy=False)
    before = ledger.receipt()["live_memory_bytes"]
    del array
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == before and before > 0
    assert isinstance(raw[0], SparseObservable)
    del raw
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_real_sparse_input_runs_estimator_and_layout_preserves_expected_wires():
    sparse = SparseObservable.from_list([("XIZ", 0.5), ("ZII", -0.3)])
    observable = ObservablesArray([sparse]).apply_layout([4, 0, 2], num_qubits=5)
    circuit = Circuit(5).x(4).h(2)
    result = StatevectorEstimator().run([(circuit, observable)]).result()[0]
    np.testing.assert_allclose(result.data.evs, [-0.5], atol=3e-14, rtol=0)
    with pytest.raises(ValueError, match="Hermitian"):
        ObservablesArray(SparseObservable.from_list([("Z", 1j)]))


@pytest.mark.parametrize("mapping", [[2, 1, 0], [4, 0, 2]])
def test_real_compiler_layout_and_estimator_agree_with_independent_state_math(mapping):
    from quantumbridge.compiler import Layout, Target, transpile
    from quantumbridge.core.circuit_metadata import execution_metadata

    circuit = Circuit(3).x(0).h(1).ry(0.4, 2).rz(0.7, 2).cx(0, 2)
    observable = ObservablesArray([SparseObservable.from_list([("IIZ", 0.7), ("IXI", -0.2), ("YII", 0.3)])])
    width = max(mapping) + 1
    compiled, _ = transpile(circuit, target=Target(width, ("x", "h", "ry", "rz", "cx")), initial_layout=Layout(mapping),
                            optimization_level=0, return_report=True)
    final = execution_metadata(compiled)["transpile"]["analyses"]["logical_final_layout"]
    mapped = observable.apply_layout(Layout(final), compiled.num_qubits)
    estimator = StatevectorEstimator()
    original, actual = estimator.run([(circuit, observable), (compiled, mapped)]).result()
    expected = -0.7-0.2-0.3*np.sin(0.4)*np.sin(0.7)
    np.testing.assert_allclose(original.data.evs, [expected], atol=3e-14, rtol=0)
    np.testing.assert_allclose(actual.data.evs, [expected], atol=3e-14, rtol=0)
    # An explicit basis-vector embedding checks wire order independently of
    # observable label remapping and the compiler's statevector implementation.
    logical = np.zeros(8, complex)
    for middle in (0, 1):
        logical[1 + 2*middle + 4] = np.cos(0.4/2)*np.exp(-0.7j/2)/np.sqrt(2)
        logical[1 + 2*middle] = np.sin(0.4/2)*np.exp(0.7j/2)/np.sqrt(2)
    physical = np.zeros(1 << width, complex)
    for basis, amplitude in enumerate(logical):
        destination = sum(((basis >> wire) & 1) << final[wire] for wire in range(3))
        physical[destination] = amplitude
    dense = mapped.slice(0).to_matrix()
    np.testing.assert_allclose(np.vdot(physical, dense @ physical).real, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("mutation", ["nan", "imaginary", "width", "raw"])
def test_late_mutated_sparse_observable_refuses_before_first_evolution(mutation, monkeypatch):
    from quantumbridge.devices import StatevectorDevice

    array = ObservablesArray(["Z"])
    if mutation == "nan":
        array.slice(0).coeffs[0] = float("nan")
    elif mutation == "imaginary":
        array.slice(0).coeffs[0] = 1j
    elif mutation == "width":
        array.sparse_observables_array()[0] = SparseObservable("ZZ")
    else:
        array.sparse_observables_array()[0] = object()
    calls = []
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *args, **kwargs: calls.append(1))
    with pytest.raises((ValueError, TypeError)):
        StatevectorEstimator().run([(Circuit(1), "Z"), (Circuit(1), array)])
    assert calls == []


def test_borrowed_strided_object_array_admits_entire_retained_storage_root():
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits

    raw = np.empty(100, object)
    raw.fill(None)
    view = raw[::10]
    exact = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=raw.nbytes))
    with ResourceScope(exact):
        array = ObservablesArray(view, num_qubits=1, copy=False, validate=False)
    assert exact.receipt()["live_memory_bytes"] == raw.nbytes
    del array, view
    gc.collect()
    assert exact.receipt()["live_memory_bytes"] == raw.nbytes
    del raw
    gc.collect()
    assert exact.receipt()["live_memory_bytes"] == 0
    raw = np.empty(100, object)
    raw.fill(None)
    below = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=raw.nbytes-1))
    with ResourceScope(below), pytest.raises(MemoryError):
        ObservablesArray(raw[::10], num_qubits=1, copy=False, validate=False)
    assert below.receipt()["live_memory_bytes"] == 0
