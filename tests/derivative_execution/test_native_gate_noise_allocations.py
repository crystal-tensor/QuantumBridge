# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native gate/noise/evolution factories admit storage before execution."""

import gc
from types import SimpleNamespace

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.core.classical import ClassicalStore
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.control_flow_engine import Branch, DynamicExecutionEngine
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.noise.quantum_error import QuantumError, kraus_error
from quantumbridge.utils.math import gate_matrix, validate_kraus_operators, apply_unitary, apply_density_operator


@pytest.mark.parametrize("name,params", [
    ("global_phase", (.31,)), ("h", ()), ("sx", ()), ("sxdg", ()),
    ("s", ()), ("sdg", ()), ("t", ()), ("tdg", ()),
    ("rx", (.31,)), ("ry", (.31,)), ("rz", (.31,)), ("phase", (.31,)),
    ("u2", (.2, -.4)), ("u3", (.3, .2, -.4)),
    ("cx", ()), ("cy", ()), ("cz", ()), ("ch", ()), ("csx", ()),
    ("csxdg", ()), ("crx", (.31,)), ("cry", (.31,)), ("crz", (.31,)),
    ("cp", (.31,)), ("rxx", (.31,)), ("ryy", (.31,)), ("rzz", (.31,)),
    ("swap", ()), ("dcx", ()), ("ecr", ()), ("iswap", ()), ("ccx", ()), ("cswap", ()),
])
def test_gate_factory_denied_before_array_or_kron(name, params, monkeypatch):
    def forbidden(*a, **k):pytest.fail("Native gate allocated before reservation")
    for factory in ("array", "empty", "eye", "diag", "kron"):
        monkeypatch.setattr(np, factory, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        gate_matrix(name, params)


@pytest.mark.parametrize("dtype", [float, complex])
def test_custom_unitary_admission_precedes_dtype_or_gram_copy(dtype, monkeypatch):
    circuit, matrix = Circuit(1), np.eye(2, dtype=dtype)
    def forbidden(*a, **k):pytest.fail("Custom unitary allocated before reservation")
    for factory in ("asarray", "empty", "eye"):
        monkeypatch.setattr(np, factory, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        circuit.unitary(matrix, [0])
    assert circuit.operations == []


def test_stacked_numeric_kraus_input_is_not_an_opaque_container():
    p = .27
    operators = np.array([[[1, 0], [0, np.sqrt(1-p)]], [[0, np.sqrt(p)], [0, 0]]], complex)
    with ResourceScope(Ledger()):actual = validate_kraus_operators(operators)
    for matrix, expected in zip(actual, operators):
        np.testing.assert_array_equal(matrix, expected)
        assert not np.shares_memory(matrix, operators)


@pytest.mark.parametrize("kind", ["compose", "tensor"])
def test_quantum_error_algebra_denied_before_products_and_copies(kind, monkeypatch):
    first, second = QuantumError([np.eye(2)]), QuantumError([np.diag([1, 1j])])
    if kind == "compose":
        class ProductSpy(np.ndarray):
            def __matmul__(self, other):pytest.fail("QuantumError product preceded admission")
        first._operators = (first._operators[0].view(ProductSpy),)
        second._operators = (second._operators[0].view(ProductSpy),)
    def forbidden(*a, **k):pytest.fail("QuantumError algebra allocated before reservation")
    for factory in ("kron", "matmul", "array", "empty"):
        monkeypatch.setattr(np, factory, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        getattr(first, kind)(second)


def test_canonical_kraus_denied_before_choi_or_eigen_factory(monkeypatch):
    operators = [np.eye(2, dtype=complex)]
    def forbidden(*a, **k):pytest.fail("Canonical Choi/eigen allocation preceded admission")
    monkeypatch.setattr(np, "outer", forbidden)
    monkeypatch.setattr(np.linalg, "eigh", forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=200))), pytest.raises(MemoryError):
        kraus_error(operators, canonical_kraus=True)


def test_dense_apply_denied_before_output_factory(monkeypatch):
    state, matrix = np.array([1., 0.], complex), np.eye(2, dtype=complex)
    monkeypatch.setattr(np, "zeros_like", lambda *a, **k: pytest.fail("Evolution allocated before admission"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Evolution allocated before admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=31))), pytest.raises(MemoryError):
        apply_unitary(state, matrix, (0,), 1)


def test_density_apply_denied_before_product_or_conjugate(monkeypatch):
    state, matrix = np.eye(2, dtype=complex)/2, np.eye(2, dtype=complex)
    def forbidden(*a, **k):pytest.fail("Density contraction preceded admission")
    monkeypatch.setattr(np, "conjugate", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    monkeypatch.setattr(np, "matmul", forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=63))), pytest.raises(MemoryError):
        apply_density_operator(state, matrix, (0,), 1)


def test_superop_reset_denied_before_operator_factory(monkeypatch):
    circuit = Circuit(1).reset(0)
    engine = object.__new__(DynamicExecutionEngine)
    engine.adapter = SimpleNamespace(kind="superop")
    branch = Branch(None, ClassicalStore(0))
    monkeypatch.setattr(np, "array", lambda *a, **k: pytest.fail("Reset allocated before admission"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Reset allocated before admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        engine._leaf(circuit.operations[0], branch, None, {})


def test_tableau_expansion_denies_dense_request_before_synthesis(monkeypatch):
    from quantumbridge.information import StabilizerState
    state = StabilizerState.from_stabilizer_list(["+Z"])
    monkeypatch.setattr(type(state.clifford), "to_circuit", lambda *a, **k: pytest.fail("Dense tableau request entered synthesis before admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=31))), pytest.raises(MemoryError):state.to_statevector()


def _golden_gates():
    eye = np.eye(2, dtype=complex)
    x, y, z = (np.array(value, complex) for value in (
        [[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]))
    theta, phi, lam = .31, .2, -.4
    rotate = lambda p, angle: np.cos(angle/2)*eye-1j*np.sin(angle/2)*p
    u = np.exp(.5j*(phi+lam))*rotate(z, phi)@rotate(y, theta)@rotate(z, lam)
    u2 = np.exp(.5j*(phi+lam))*rotate(z, phi)@rotate(y, np.pi/2)@rotate(z, lam)
    sx = .5*((1+1j)*eye+(1-1j)*x)
    phase = np.diag([1, np.exp(1j*theta)])
    gates = {
        "i": ((), eye), "id": ((), eye), "x": ((), x), "y": ((), y), "z": ((), z),
        "global_phase": ((theta,), np.exp(1j*theta)*eye), "h": ((), (x+z)/np.sqrt(2)),
        "sx": ((), sx), "sxdg": ((), sx.conj().T),
        "s": ((), np.diag([1, 1j])), "sdg": ((), np.diag([1, -1j])),
        "t": ((), np.diag([1, np.exp(1j*np.pi/4)])), "tdg": ((), np.diag([1, np.exp(-1j*np.pi/4)])),
        "rx": ((theta,), rotate(x, theta)), "ry": ((theta,), rotate(y, theta)), "rz": ((theta,), rotate(z, theta)),
        "phase": ((theta,), phase), "p": ((theta,), phase), "u1": ((theta,), phase),
        "u": ((theta, phi, lam), u), "u3": ((theta, phi, lam), u), "u2": ((phi, lam), u2),
    }
    p0, p1 = np.diag([1, 0]), np.diag([0, 1])
    for name, target in (("cx", "x"), ("cy", "y"), ("cz", "z"), ("ch", "h"),
                         ("csx", "sx"), ("csxdg", "sxdg"), ("crx", "rx"), ("cry", "ry"),
                         ("crz", "rz"), ("cp", "p"), ("cphase", "p")):
        params, matrix = gates[target]
        gates[name] = params, np.kron(p0, eye)+np.kron(p1, matrix)
    swap = np.eye(4, dtype=complex)[[0, 2, 1, 3]]
    gates["swap"] = (), swap
    gates["dcx"] = (), swap@gates["cx"][1]@swap@gates["cx"][1]
    gates["iswap"] = (), np.diag([1, 1j, 1j, 1])@swap
    gates["ecr"] = (), (np.kron(x, eye)-np.kron(y, x))/np.sqrt(2)
    for name, pauli in (("rxx", x), ("ryy", y), ("rzz", z)):
        gates[name] = (theta,), np.cos(theta/2)*np.eye(4)-1j*np.sin(theta/2)*np.kron(pauli, pauli)
    for name, swapped in (("ccx", (6, 7)), ("cswap", (5, 6))):
        order = list(range(8));a, b = swapped;order[a], order[b] = b, a
        gates[name] = (), np.eye(8, dtype=complex)[order]
    return gates


@pytest.mark.parametrize("name,case", list(_golden_gates().items()))
def test_managed_gate_matches_independent_analytic_matrix_and_retains_root(name, case, monkeypatch):
    params, expected = case
    ledger = Ledger()
    monkeypatch.setattr(np, "kron", lambda *a, **k: pytest.fail("Managed gate used an unowned Kronecker temporary"))
    with ResourceScope(ledger):actual = gate_matrix(name, params)
    np.testing.assert_allclose(actual, expected, atol=3e-16, rtol=1e-15)
    assert ledger.receipt()["live_memory_bytes"] == actual.nbytes
    view, amount = actual[:1, :1], actual.nbytes
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == amount
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("dtype", [float, complex])
def test_direct_gate_helpers_and_metadata_do_not_invent_borrowed_allocations(dtype):
    from quantumbridge.utils.math import _u_matrix, _controlled_one_qubit_matrix
    source = np.eye(2, dtype=dtype)
    expected = _u_matrix(.3, .2, -.4)
    ledger = Ledger()
    with ResourceScope(ledger):
        u = _u_matrix(.3, .2, -.4)
        controlled = _controlled_one_qubit_matrix([[1j, 0], [0, -1j]])
        metadata = gate_matrix("custom", metadata={"matrix": source})
    np.testing.assert_array_equal(u, expected)
    np.testing.assert_array_equal(controlled, np.diag([1, 1, 1j, -1j]))
    assert np.shares_memory(metadata, source) == (dtype is complex)
    assert ledger.receipt()["live_memory_bytes"] == 320+(64 if dtype is float else 0)
    del u, controlled, metadata
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_strided_stacked_kraus_subclass_aliases_and_recovery():
    class NoDispatch(np.ndarray):
        def __iter__(self):pytest.fail("Foreign stack iteration dispatched")
        def __getitem__(self, key):pytest.fail("Foreign stack indexing dispatched")
        def __array_ufunc__(self, *a, **k):pytest.fail("Foreign numeric dispatch executed")
    source = np.zeros((4, 2, 2), complex)
    source[0] = np.eye(2)/np.sqrt(2);source[2] = source[0]
    stack = source[::2].view(NoDispatch)
    ledger = Ledger(Limits(max_total_memory_bytes=260))
    with ResourceScope(ledger):
        outputs = validate_kraus_operators(stack)
        assert not np.shares_memory(*outputs)
        with pytest.raises(MemoryError):validate_kraus_operators(stack)
        view = outputs[0][0:1]
        del outputs
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 64
        del view
        gc.collect()
        outputs = validate_kraus_operators([source[0], source[0]])
        np.testing.assert_array_equal(outputs[0], source[0])
        del outputs
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind,front", [("compose", False), ("compose", True), ("tensor", False)])
def test_managed_quantum_error_algebra_and_canonical_choi_preserve_channel(kind, front):
    from quantumbridge.noise.quantum_error import amplitude_damping_error, coherent_unitary_error
    first = amplitude_damping_error(.23)
    second = coherent_unitary_error(_golden_gates()["u"][1])
    expected = getattr(first, kind)(second, **({"front": front} if kind == "compose" else {})).to_quantumchannel().to_choi().data
    ledger = Ledger()
    with ResourceScope(ledger):
        result = getattr(first, kind)(second, **({"front": front} if kind == "compose" else {}))
        canonical = kraus_error(result._operators, canonical_kraus=True)
        actual = canonical.to_quantumchannel().to_choi().data
    np.testing.assert_allclose(actual, expected, atol=2e-15, rtol=1e-14)
    del result, canonical, actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("name,args", [
    ("reset_error", (.2,.3)), ("phase_amplitude_damping_error", (.2,.1,.3)),
    ("amplitude_damping_error", (.2,.3)), ("phase_damping_error", (.3,)),
    ("thermal_relaxation_error", (50.,40.,10.,.2)), ("depolarizing_error", (.3,2)),
])
def test_noise_error_factories_preserve_choi_and_release_outputs(name, args):
    from quantumbridge.noise import quantum_error as module
    factory = getattr(module, name)
    expected = factory(*args).to_quantumchannel().to_choi().data
    ledger = Ledger()
    with ResourceScope(ledger):
        error = factory(*args)
        actual = error.to_quantumchannel().to_choi().data
        exports = error.kraus()
    np.testing.assert_allclose(actual, expected, atol=2e-15, rtol=1e-14)
    assert all(not np.shares_memory(a,b) for a,b in zip(error._operators,exports))
    del error, actual, exports
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_stabilizer_noise_weights_are_admitted_before_scaling(monkeypatch):
    matrix = np.eye(2, dtype=complex)
    device = SimpleNamespace(simulation="exact_stabilizer", noise_model=SimpleNamespace(),
        _noise_instructions=lambda width: [("pauli",[(.5,matrix),(.5,matrix)],(0,),{})])
    ledger = Ledger(Limits(max_total_memory_bytes=127))
    monkeypatch.setattr(np,"empty",lambda *a, **k: pytest.fail("Noise scaling preceded whole-group admission"))
    with ResourceScope(ledger), pytest.raises(MemoryError):DynamicExecutionEngine(device,Circuit(1))
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("name", ["BitFlipChannel", "PhaseFlipChannel", "DepolarizingChannel", "AmplitudeDampingChannel", "PhaseDampingChannel"])
def test_builtin_noise_channel_copies_match_legacy_and_have_independent_owners(name):
    from quantumbridge.noise import channels
    channel = getattr(channels,name)(.31)
    expected = channel.kraus()
    ledger = Ledger()
    with ResourceScope(ledger):
        actual = channel.kraus()
        assert channel.is_trace_preserving()
        exported = channels.KrausChannel(actual).kraus()
    for result, target in zip(actual, expected):np.testing.assert_array_equal(result,target)
    assert not np.shares_memory(actual[0],exported[0])
    assert ledger.receipt()["live_memory_bytes"] == 2*len(actual)*64
    del actual, exported, result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_malformed_managed_gate_descriptions_reject_before_factories(monkeypatch):
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.utils.math import _u_matrix
    monkeypatch.setattr(np,"empty",lambda *a, **k: pytest.fail("Malformed gate reached allocation"))
    with ResourceScope(Ledger()):
        with pytest.raises(UnsupportedFeature):gate_matrix(object())
        with pytest.raises(UnsupportedFeature):gate_matrix("custom",metadata=object())
        with pytest.raises(ValueError):gate_matrix("rx",[[.3]])
        with pytest.raises(ValueError):_u_matrix([.3],.2,.1)


def test_native_kron_guards_reject_bad_shapes_aliases_and_strides_before_einsum(monkeypatch):
    from quantumbridge.execution.array_reservations import kron_into
    first,second=np.eye(2,dtype=complex),np.eye(2,dtype=complex)
    backing=np.zeros((4,8),complex)
    cases=[(first,second,np.empty((2,2),complex)),
        (first,np.ones((1,1),complex),first),(first,second,backing[:,::2])]
    monkeypatch.setattr(np,"einsum",lambda *a, **k: pytest.fail("Invalid Kronecker output dispatched"))
    for a,b,out in cases:
        with ResourceScope(Ledger()),pytest.raises(ValueError):kron_into(a,b,out)
