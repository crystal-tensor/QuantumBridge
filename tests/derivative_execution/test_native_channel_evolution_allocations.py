# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public native channel/evolution calls obey their allocation contract."""

import gc

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Statevector, DensityMatrix, Operator, Kraus, Choi, SuperOp, PTM, Chi, Stinespring


@pytest.mark.parametrize("cls", [Kraus, Choi, SuperOp, PTM, Chi, Stinespring])
@pytest.mark.parametrize("method", ["to_choi", "to_superop"])
def test_public_channel_conversion_denied_before_matrix_factories(cls, method, monkeypatch):
    channel = cls(Kraus([np.eye(2, dtype=complex)]))
    def forbidden(*a, **k):pytest.fail("Channel conversion allocated before admission")
    for name in ("array", "kron", "outer", "column_stack", "empty"):
        monkeypatch.setattr(np, name, forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):
        getattr(channel, method)()


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_public_state_evolution_denied_before_dtype_factory(cls, monkeypatch):
    state = cls([1., 0.]) if cls is Statevector else cls(np.eye(2)/2)
    matrix = np.eye(2, dtype=np.float32)
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("Evolution dtype copy preceded admission"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Evolution output preceded admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):state.evolve(matrix)


def test_public_density_reset_denied_before_kraus_or_copy_factory(monkeypatch):
    state = DensityMatrix(np.eye(2, dtype=complex)/2)
    monkeypatch.setattr(np, "array", lambda *a, **k: pytest.fail("Reset operators preceded admission"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Reset buffers preceded admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):state.reset()


def test_dense_initial_state_denied_before_zero_factory(monkeypatch):
    from quantumbridge import DensityMatrixDevice
    monkeypatch.setattr(np, "zeros", lambda *a, **k: pytest.fail("Initial density preceded admission"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Initial density preceded admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):DensityMatrixDevice()._initial(1)


def test_superop_evolution_denied_before_expansion_factory(monkeypatch):
    from quantumbridge.simulator.aer import LinearMapDevice
    from quantumbridge.simulator.limits import AerExecutionLimits
    device = LinearMapDevice("superop", AerExecutionLimits())
    state, matrix = np.eye(4, dtype=complex), np.eye(2, dtype=complex)
    for name in ("zeros", "kron", "empty"):
        monkeypatch.setattr(np, name, lambda *a, **k: pytest.fail("Linear map evolution preceded admission"))
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))), pytest.raises(MemoryError):device.map_gate(state, matrix, (0,), 1)


@pytest.mark.parametrize("cls", [Kraus, Choi, SuperOp, PTM, Chi, Stinespring])
@pytest.mark.parametrize("generalized", [False, True])
def test_managed_channel_construction_conversion_evolution_and_algebra(cls, generalized):
    left = (np.array([[1, .2j], [.1, .7]], complex), np.array([[0, .3], [.2j, 0]], complex))
    right = (np.array([[.7j, .1], [.2, 1]], complex), np.array([[.1, 0], [0, .4j]], complex)) if generalized else left
    raw = (left, right) if generalized else left
    source = cls(Kraus(raw))
    expected = sum(np.kron(b.conj(), a) for a, b in zip(left, right))
    rho = np.array([[.4, .1j], [-.1j, .6]], complex)
    expected_rho = sum(a@rho@b.conj().T for a, b in zip(left, right))
    expected_algebra = [source.compose(source), source.compose(source, front=True), source.tensor(source),
        source.adjoint(), source.conjugate(), source.transpose(), source*.3, source+source, source-source]
    expected_algebra = [value.to_superop().data for value in expected_algebra]
    ledger = Ledger()
    with ResourceScope(ledger):
        result = cls(Kraus(raw))
        superop, choi = result.to_superop(), result.to_choi()
        roundtrip = cls(choi).to_superop()
        state = result.evolve(rho)
        algebra = [result.compose(result), result.compose(result, front=True), result.tensor(result),
            result.adjoint(), result.conjugate(), result.transpose(), result*.3, result+result, result-result]
        actual_algebra = [value.to_superop().data for value in algebra]
    np.testing.assert_allclose(superop.data, expected, atol=2e-14, rtol=1e-13)
    np.testing.assert_allclose(roundtrip.data, expected, atol=2e-14, rtol=1e-13)
    np.testing.assert_allclose(state.data, expected_rho, atol=2e-14, rtol=1e-13)
    for actual, wanted in zip(actual_algebra, expected_algebra):
        np.testing.assert_allclose(actual, wanted, atol=3e-14, rtol=1e-13)
    del result, superop, choi, roundtrip, state, algebra, actual_algebra, actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Kraus, Choi, SuperOp, Stinespring])
def test_rectangular_generalized_map_has_correct_output_and_root_lifetime(cls):
    left = np.array([[1, .1j], [0, .7], [.2, 0], [0, .3j]], complex)
    right = left*.9j
    source = cls(Kraus(([left], [right])))
    rho = np.diag([.4, .6]).astype(complex)
    expected = left@rho@right.conj().T
    ledger = Ledger()
    with ResourceScope(ledger):result = cls(source).evolve(rho)
    np.testing.assert_allclose(result.data, expected, atol=2e-15)
    view = result.data[:1, :1]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 4*4*16
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("imag", [0., 1e-16, 2e-14, 3e-14, np.nan, np.inf])
def test_managed_real_if_close_matches_numpy_threshold_and_view_semantics(imag):
    from quantumbridge.information.channels import _real_if_close
    source = np.array([complex(1, imag), complex(2, imag)], complex)[::-1]
    expected = np.real_if_close(source)
    ledger = Ledger()
    with ResourceScope(ledger):actual = _real_if_close(source)
    np.testing.assert_array_equal(actual, expected)
    assert actual.dtype == expected.dtype and np.shares_memory(actual, source)
    assert ledger.receipt()["total_reserved_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_state_evolution_preserves_complex_phase_and_nonconsecutive_wire_order(cls):
    from quantumbridge.information.operator import _expand_subsystem_operator
    rng = np.random.default_rng(32)
    vector = rng.normal(size=8)+1j*rng.normal(size=8);vector /= np.linalg.norm(vector)
    operator, _ = np.linalg.qr(rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)))
    full = _expand_subsystem_operator(operator, (2,0), 3)
    state = cls(vector) if cls is Statevector else cls(np.outer(vector, vector.conj()))
    expected = full@vector if cls is Statevector else full@state.data@full.conj().T
    ledger = Ledger()
    with ResourceScope(ledger):result = state.evolve(operator, qargs=[2,0])
    np.testing.assert_allclose(result.data, expected, atol=3e-16, rtol=1e-14)
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_density_reset_and_project_match_bell_state_without_mutating_input():
    from quantumbridge import DensityMatrixDevice
    vector = np.array([1,0,0,1], complex)/np.sqrt(2)
    source = np.outer(vector, vector.conj())
    state, device = DensityMatrix(source), DensityMatrixDevice()
    ledger = Ledger()
    with ResourceScope(ledger):
        result = state.reset([0])
        projected, probability = device._project(source, 0, 1, 2)
    np.testing.assert_allclose(result.data, np.diag([.5,.5,0,0]), atol=2e-16)
    np.testing.assert_allclose(projected, np.diag([0,0,0,1]), atol=2e-16)
    assert probability == pytest.approx(.5)
    np.testing.assert_array_equal(source, np.outer(vector, vector.conj()))
    del result, projected
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [SuperOp, Operator])
def test_power_does_not_delegate_unowned_array_intermediates_to_matrix_power(cls, monkeypatch):
    from quantumbridge.information import Operator
    matrix = np.array([[1, .2j], [0, .8]], complex)
    source = cls(Operator(matrix)) if cls is SuperOp else cls(matrix)
    expected = [source.power(n).data for n in (0, 1, 2, 5, -2)]
    monkeypatch.setattr(np.linalg, "matrix_power", lambda *a, **k: pytest.fail("Matrix power intermediates lack ownership"))
    ledger = Ledger()
    with ResourceScope(ledger):actual = [source.power(n).data for n in (0, 1, 2, 5, -2)]
    for result, target in zip(actual, expected):np.testing.assert_allclose(result, target, atol=2e-14)
    del actual, result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("method", ["statevector", "density_matrix"])
def test_aer_analytic_ensemble_keeps_owned_density_after_job_and_scope_die(method, monkeypatch):
    from quantumbridge.simulator import NativeAerSimulator
    circuit = Circuit(2).h(0).cx(0,1).reset(0)
    ledger = Ledger()
    monkeypatch.setattr(np,"outer",lambda *a, **k: pytest.fail("Analytic ensemble used an unowned outer product"))
    with ResourceScope(ledger):
        job = NativeAerSimulator(method,shots=None).run(circuit)
        result = job.result()
    density = result.results[0].density
    np.testing.assert_allclose(density,np.diag([.5,.5,0,0]),atol=2e-16)
    view = density[:1,:1]
    del job, result, density
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 256
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("exponent", [0, 2, -1])
@pytest.mark.parametrize("cls", [Operator, SuperOp])
def test_integer_power_denies_before_identity_product_or_inverse(exponent, cls, monkeypatch):
    source = Operator(np.eye(2,dtype=complex))
    if cls is SuperOp:source=SuperOp(source)
    def forbidden(*a, **k):pytest.fail("Power allocated before prior admission")
    monkeypatch.setattr(np,"empty",forbidden)
    monkeypatch.setattr(np.linalg,"inv",forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=source.data.nbytes-1))
    with ResourceScope(ledger), pytest.raises(MemoryError):source.power(exponent)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_eigh_group_admission_failure_recovery_and_eigenvector_view_lifetime(monkeypatch):
    from quantumbridge.execution import mps_arrays as arrays
    source = np.diag([1.,2.,3.,4.]).astype(complex)
    ledger = Ledger(Limits(max_total_memory_bytes=287))
    with monkeypatch.context() as patch:
        patch.setattr(np.linalg,"eigh",lambda *a, **k: pytest.fail("Partial eigendecomposition output admission"))
        with ResourceScope(ledger), pytest.raises(MemoryError):arrays.decomposed(source,"eigh")
    assert ledger.receipt()["live_memory_bytes"] == 0
    ledger = Ledger()
    with monkeypatch.context() as patch:
        def failure(*a, **k):raise np.linalg.LinAlgError("injected eigendecomposition failure")
        patch.setattr(np.linalg,"eigh",failure)
        with ResourceScope(ledger), pytest.raises(np.linalg.LinAlgError):arrays.decomposed(source,"eigh")
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):values,vectors=arrays.decomposed(source,"eigh")
    np.testing.assert_array_equal(values,[1,2,3,4])
    view = vectors[:,2]
    del values,vectors
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 256
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind", ["stack", "generalized", "copy"])
def test_kraus_conversion_group_admission_precedes_first_dtype_or_defensive_copy(kind, monkeypatch):
    source = np.stack([np.eye(2),np.eye(2)])
    if kind == "generalized":source=(source,source)
    elif kind == "copy":source=Kraus(source.astype(complex))
    amount = 256 if kind == "generalized" else 128
    ledger = Ledger(Limits(max_total_memory_bytes=amount-1))
    monkeypatch.setattr(np,"empty",lambda *a, **k: pytest.fail("Partial Kraus conversion group allocated"))
    with ResourceScope(ledger), pytest.raises(MemoryError):Kraus(source)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_generalized_kraus_numeric_stacks_do_not_dispatch_subclass_iteration():
    class NoDispatch(np.ndarray):
        def __iter__(self):pytest.fail("Foreign generalized Kraus iteration dispatched")
        def __getitem__(self, key):pytest.fail("Foreign generalized Kraus indexing dispatched")
        def __array_ufunc__(self, *a, **k):pytest.fail("Foreign generalized Kraus arithmetic dispatched")
    raw = np.stack([np.eye(2,dtype=complex),np.diag([1,1j])])
    left,right=raw.view(NoDispatch),(raw*.7j).view(NoDispatch)
    ledger=Ledger()
    with ResourceScope(ledger):result=Kraus((left,right))
    assert ledger.receipt()["total_reserved_memory_bytes"] == 0
    for a,b in zip(result._left,raw):np.testing.assert_array_equal(a,b)


def test_managed_operator_public_algebra_exports_and_circuit_phase():
    first = np.array([[1,1], [1,-1]],complex)/np.sqrt(2)
    second = np.diag([1,np.exp(.31j)])
    operator,other=Operator(first),Operator(second)
    circuit=Circuit(1).h(0).barrier().phase(.31,0)
    circuit.global_phase=.23
    expected={"adjoint":first.conj().T,"conjugate":first.conj(),"transpose":first.T,
        "copy":first,"export":first,"compose":first@second,"front":second@first,
        "dot":first@second,"tensor":np.kron(first,second),"expand":np.kron(second,first),
        "circuit":np.exp(.23j)*second@first}
    ledger=Ledger()
    with ResourceScope(ledger):
        assert operator.is_unitary()
        results={"adjoint":operator.adjoint().data,"conjugate":operator.conjugate().data,
            "transpose":operator.transpose().data,"copy":operator.copy().data,"export":operator.to_matrix(),
            "compose":operator.compose(other).data,"front":operator.compose(other,front=True).data,
            "dot":operator.dot(other).data,"tensor":operator.tensor(other).data,
            "expand":operator.expand(other).data,"circuit":Operator.from_circuit(circuit).data}
    for name,result in results.items():np.testing.assert_allclose(result,expected[name],atol=3e-16)
    assert not np.shares_memory(results["copy"],first)
    assert not np.shares_memory(results["export"],first)
    del results,result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Kraus, Choi, SuperOp, PTM, Chi, Stinespring])
def test_channel_native_operator_and_circuit_constructors_produce_actual_map(cls):
    circuit=Circuit(1).h(0).phase(.31,0)
    matrix=np.diag([1,np.exp(.31j)])@np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    expected=np.kron(matrix.conj(),matrix)
    operator=Operator(matrix)
    ledger=Ledger()
    with ResourceScope(ledger):
        by_operator=cls(operator)
        by_circuit=cls(circuit)
        copied=by_operator.copy()
        maps=[value.to_superop().data for value in (by_operator,by_circuit,copied)]
    for actual in maps:np.testing.assert_allclose(actual,expected,atol=1e-14)
    del by_operator,by_circuit,copied,maps,actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("generalized", [False,True])
def test_raw_stinespring_constructor_retains_generalized_map_and_dimensions(generalized):
    left=np.array([[1,0],[0,.8],[0,.6],[0,0]],complex)
    right=left*.7j if generalized else left
    source=(left,right) if generalized else left
    a,b=left.reshape(2,2,2),right.reshape(2,2,2)
    expected=sum(np.kron(b[:,index,:].conj(),a[:,index,:]) for index in range(2))
    ledger=Ledger()
    with ResourceScope(ledger):
        channel=Stinespring(source)
        result=channel.to_superop()
    assert channel.dim == (2,2)
    np.testing.assert_allclose(result.data,expected,atol=2e-16)
    del channel,result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("diagonal,valid", [([1,0],True),([.4,.6],True),([1.1,-.1],False),([.4,.4],False)])
def test_managed_density_validity_and_pure_state_reconstruction(diagonal,valid):
    state=DensityMatrix(np.diag(diagonal).astype(complex))
    ledger=Ledger()
    with ResourceScope(ledger):
        assert state.is_valid() is valid
        if diagonal==[1,0]:
            vector=state.to_statevector()
            np.testing.assert_allclose(np.outer(vector.data,vector.data.conj()),state.data,atol=1e-15)
            view=vector.data[:1]
            del vector
            gc.collect()
            assert ledger.receipt()["live_memory_bytes"] == 64
            del view
        else:
            with pytest.raises(ValueError,match="pure state"):state.to_statevector()
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
