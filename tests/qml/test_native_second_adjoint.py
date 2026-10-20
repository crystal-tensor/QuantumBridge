# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent tangent-over-reverse mathematics, not SDK derivative helpers.

import numpy as np
import pytest

from quantumbridge import PauliX, PauliZ, Hamiltonian
from quantumbridge.qml import QNode
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.transforms import split_non_commuting


def test_second_adjoint_ry_hessian_and_streamed_direction_are_actual_reverse_sweeps(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a, **k: pytest.fail("adjoint must not substitute shifted circuits"))
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint")
    np.testing.assert_allclose(node.compute_hessian(.37), -np.cos(.37), atol=1e-12)
    np.testing.assert_allclose(node.compute_hvp(.4, .37), -.4*np.cos(.37), atol=1e-12)
    assert node.last_metadata["gradient_method"] == "adjoint"
    assert node.last_metadata["shifted_evaluation_count"] == 0
    assert node.last_metadata["hvp_streamed"]
    assert node.last_metadata["adjoint_second_sweeps"] == 1


def test_second_adjoint_nonlinear_classical_map_variance_and_probability_curvature():
    def circuit(t, x):
        t.ry(x[0]*x[1], 0)
        return {"z": t.expval(PauliZ(0)), "p": t.probs([0]), "v": t.var(PauliZ(0))}
    point, direction = np.array([.7, .2]), np.array([.4, -.3])
    seed = np.array([.2, .7])
    mixed = np.array([[0., 1.], [1., 0.]])
    hz = -np.cos(.14)*np.outer(seed, seed)-np.sin(.14)*mixed
    hv = 2*np.cos(.28)*np.outer(seed, seed)+np.sin(.28)*mixed
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint",
                 higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    result = node.compute_hvp(direction, point)
    np.testing.assert_allclose(result["z"], hz @ direction, atol=1e-11)
    np.testing.assert_allclose(result["p"]["0"], .5*(hz @ direction), atol=1e-11)
    np.testing.assert_allclose(result["p"]["1"], -.5*(hz @ direction), atol=1e-11)
    np.testing.assert_allclose(result["v"], hv @ direction, atol=1e-11)


def test_transformed_second_adjoint_retains_coefficient_and_cross_child_terms():
    def circuit(t, x):
        t.ry(np.sin(x)+2*x, 0)
        return t.expval(Hamiltonian([(.7+.1*x, PauliX(0)), (.2, PauliZ(1).tensor(PauliX(0)))]))
    point, a, angle, first = .37, .937, np.sin(.37)+.74, np.cos(.37)+2
    expected = .2*np.cos(angle)*first-a*np.sin(angle)*first**2-a*np.cos(angle)*np.sin(point)
    node = split_non_commuting(QNode(circuit, 2, max_diff=2, diff_method="adjoint"))
    np.testing.assert_allclose(node.compute_hessian(point), expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(.4, point), .4*expected, atol=1e-11)
    assert node.last_metadata["gradient_method"] == "adjoint"
    assert node.last_metadata["shifted_evaluation_count"] == 0
    assert node.last_metadata["postprocessing_second_chain_rule"]
    assert node.last_metadata["derivative_evaluation_count"] > 0


@pytest.mark.parametrize("gate", ["rx", "ry", "rz", "phase", "cp", "crx", "cry", "crz", "rxx", "ryy", "rzz"])
def test_second_adjoint_gate_rules_include_controlled_mixed_frequencies(gate):
    def circuit(t, x):
        if gate in {"rz", "phase", "rzz", "cp", "crx", "cry", "crz"}: t.h(0)
        if gate in {"cp", "crz"}: t.h(1)
        if gate in {"rx", "ry", "rz", "phase"}: getattr(t, gate)(x, 0)
        else: getattr(t, gate)(x, 0, 1)
        if gate in {"crx", "cry", "crz"}:
            target = PauliX(1) if gate == "crz" else PauliZ(1)
            return t.expval(Hamiltonian([(1., PauliX(0)), (.3, target)]))
        return t.expval(PauliX(0) if gate in {"rz", "phase", "rzz", "cp"} else PauliZ(0))
    x = .37
    expected = -.25*np.cos(x/2)-.15*np.cos(x) if gate in {"crx", "cry", "crz"} else -.5*np.cos(x) if gate == "cp" else -np.cos(x)
    node = QNode(circuit, 2, max_diff=2)
    np.testing.assert_allclose(node.compute_hessian(x, method="adjoint"), expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(-.3, x, method="adjoint"), -.3*expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hessian(x, method="parameter-shift"), expected, atol=1e-11)


def test_complex_hermitian_observable_global_phase_and_full_mixed_hessian():
    observable = np.array([[.4, .2-.3j], [.2+.3j, -.4]])
    def circuit(t, x):
        t.circuit.global_phase = .27
        t.ry(x[0], 0); t.rz(x[1], 0)
        return t.expval(observable)
    point = np.array([.37, -.2])
    x, y = point
    value = np.sin(x)*(.2*np.cos(y)+.3*np.sin(y))+.4*np.cos(x)
    mixed = np.cos(x)*(-.2*np.sin(y)+.3*np.cos(y))
    expected = np.array([[-value, mixed], [mixed, -np.sin(x)*(.2*np.cos(y)+.3*np.sin(y))]])
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint")
    actual = node.compute_hessian(point)
    np.testing.assert_allclose(actual, expected, atol=1e-11)
    np.testing.assert_allclose(actual, actual.T, atol=1e-12)
    np.testing.assert_allclose(node.compute_hvp(np.array([.4, -.3]), point), expected @ [.4, -.3], atol=1e-11)
    assert node.last_metadata["total_physical_shots"] == 0


def test_stationary_classical_map_keeps_first_quantum_gradient_times_map_hessian():
    node = QNode(lambda t, x: (t.ry(x*x, 0), t.expval(PauliX(0)))[-1], 1, max_diff=2, diff_method="adjoint")
    np.testing.assert_allclose(node.compute_hessian(0.), 2., atol=1e-12)
    np.testing.assert_allclose(node.compute_hvp(.4, 0.), .8, atol=1e-12)


@pytest.mark.parametrize("options", [
    {"higher_order_limits": HigherOrderLimits(max_adjoint_operations=1)},
    {"higher_order_limits": HigherOrderLimits(max_memory_bytes=128)},
    {"higher_order_limits": HigherOrderLimits(max_total_tapes=1)},
])
def test_second_adjoint_resource_rejections_precede_all_quantum_execution(options, monkeypatch):
    from quantumbridge import StatevectorDevice
    node = QNode(lambda t, x: (t.ry(x, 0), t.expval(PauliZ(0)))[-1], 1, max_diff=2, diff_method="adjoint", **options)
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("preflight must precede native forward execution"))
    with pytest.raises(MemoryError): node.compute_hvp(.4, .3)


def test_combined_device_buffer_budget_and_parent_adjoint_work_reject_before_execution(monkeypatch):
    from quantumbridge import StatevectorDevice
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    baseline = QNode(circuit, 1, max_diff=2, diff_method="adjoint")
    baseline.compute_hvp(.4, .3)
    work = baseline.last_metadata["second_order_work"]["adjoint_operations"]
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint", higher_order_limits=HigherOrderLimits(max_adjoint_operations=work))
    doubled = node.with_transform(lambda tape: ((tape.copy(), tape.copy()), lambda results: results[0]*results[1]))
    small = QNode(circuit, 1, device=StatevectorDevice(max_memory_mb=.0005), max_diff=2, diff_method="adjoint")
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("combined preflight must precede every child"))
    with pytest.raises(MemoryError, match="max_adjoint_operations"): doubled.compute_hvp(.4, .3)
    with pytest.raises(MemoryError, match="max_memory_mb"): small.compute_hvp(.4, .3)


@pytest.mark.parametrize("kind", ["mixed", "mps", "sampled", "record", "nonhermitian"])
def test_unsupported_second_adjoint_paths_never_substitute_shift_or_other_devices(kind, monkeypatch):
    from quantumbridge import StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, UnsupportedFeature
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    def circuit(t, x):
        t.ry(x, 0)
        if kind == "record":
            t.measure(0)
            t.x(0)
        return t.expval(np.array([[0., 1.], [0., 0.]])) if kind == "nonhermitian" else t.expval(PauliZ(0))
    options = {"device": DensityMatrixDevice()} if kind == "mixed" else {"device": MatrixProductStateDevice()} if kind == "mps" else {"shots": 100, "seed": 7} if kind == "sampled" else {}
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint", **options)
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("unsupported path must reject before native state allocation"))
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a, **k: pytest.fail("unsupported adjoint must not fall back"))
    with pytest.raises((UnsupportedFeature, ValueError)): node.compute_hvp(.4, .3)


def test_unused_terminal_measurement_keeps_existing_analytic_expectation_contract():
    def circuit(t, x):
        t.ry(x, 0)
        t.measure(0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint")
    np.testing.assert_allclose(node.compute_hessian(.37), -np.cos(.37), atol=1e-12)


def test_long_shared_parameter_adjoint_has_no_shift_pair_expansion(monkeypatch):
    from quantumbridge import StatevectorDevice
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    calls, original = [], StatevectorDevice.statevector
    def statevector(self, *args, **kwargs):
        calls.append(args[0].num_qubits)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(StatevectorDevice, "statevector", statevector)
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a, **k: pytest.fail("long adjoint must not enumerate shifted pairs"))
    def circuit(t, x):
        for _ in range(64): t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint",
        higher_order_limits=HigherOrderLimits(max_shifted_circuits=1, max_hessian_elements=1))
    np.testing.assert_allclose(node.compute_hvp(.4, .003), -.4*64**2*np.cos(64*.003), atol=2e-10)
    assert calls == [1, 1], "one actual base measurement and one authoritative adjoint primal"
    assert node.last_metadata["adjoint_second_sweeps"] == 1
    assert node.last_metadata["second_order_work"]["shift_count"] == 0


def test_classical_identity_processing_reports_no_quantum_second_engine(monkeypatch):
    from quantumbridge import PauliString, StatevectorDevice
    def circuit(t, x):
        return t.expval(Hamiltonian([(x*x, PauliString([(0, "I")]))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, diff_method="adjoint"))
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("identity-only source derivative needs no quantum work"))
    np.testing.assert_allclose(node.compute_hvp(.4, .3), .8, atol=1e-12)
    assert node.last_metadata["gradient_method"] == "classical-only"
    assert node.last_metadata["derivative_evaluation_count"] == 0
