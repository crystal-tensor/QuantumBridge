# Independent QuantumBridge mathematical oracles; no SDK implementation copied.

import numpy as np
import pytest

from quantumbridge import Circuit, DensityMatrixDevice, MatrixProductStateDevice, StatevectorDevice, StabilizerDevice
from quantumbridge import Hamiltonian, PauliX, PauliY, PauliZ, PauliString, parameter_shift, ExecutionLimits, UnsupportedFeature
from quantumbridge.information import MatrixProductState
from quantumbridge.qml import QNode, ShotSpec
from quantumbridge.diff.trace import flatten_tree


def rotation(axis="ry", observable=None, **options):
    def program(tape, theta):
        getattr(tape, axis)(theta, 0)
        return tape.expval(PauliZ(0) if observable is None else observable)
    return QNode(program, 1, **options)


@pytest.mark.parametrize("method", ["adjoint", "parameter-shift", "finite-diff"])
def test_rx_ry_and_rz_noncommuting_derivatives(method):
    for axis in ("rx", "ry"):
        assert rotation(axis).gradient(.4, method=method) == pytest.approx(-np.sin(.4), abs=1e-8)
    def rz(tape, theta):
        tape.h(0); tape.rz(theta, 0)
        return tape.expval(PauliY(0))
    assert QNode(rz, 1).gradient(.4, method=method) == pytest.approx(np.cos(.4), abs=1e-8)


def test_shared_parameter_is_summed_by_gate_occurrence():
    def program(tape, theta):
        tape.ry(theta, 0); tape.ry(theta, 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1)
    for method in ("adjoint", "parameter-shift", "finite-diff"):
        assert node.gradient(.4, method=method) == pytest.approx(-2 * np.sin(.8), abs=1e-8)
    assert parameter_shift(node, .4) == pytest.approx(-2 * np.sin(.8))
    assert node.last_metadata["shifted_evaluation_count"] == 4


def test_nonlinear_classical_chain_rule_and_constant_scaling():
    def program(tape, theta):
        tape.ry(2 * theta + np.sin(theta), 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1)
    expected = -np.sin(.8 + np.sin(.4)) * (2 + np.cos(.4))
    for method in ("adjoint", "parameter-shift", "finite-diff"):
        assert node.gradient(.4, method=method) == pytest.approx(expected, abs=1e-8)


def test_phase_and_controlled_rotation_generalized_shift_rules():
    phase = QNode(lambda t, x: (t.h(0), t.phase(x, 0), t.expval(PauliX(0)))[-1], 1)
    assert phase.gradient(.6, method="parameter-shift") == pytest.approx(-np.sin(.6))
    for gate in ("crx", "cry", "crz"):
        def program(tape, theta):
            tape.h(0); tape.h(1); getattr(tape, gate)(theta, 0, 1)
            return tape.expval(PauliX(0))
        node = QNode(program, 2)
        assert node.gradient(.4, method="parameter-shift") == pytest.approx(node.gradient(.4, method="adjoint"), abs=1e-10)


def test_entangled_hamiltonian_multi_parameter_adjoint():
    observable = Hamiltonian([(1., PauliZ(0)), (.7, PauliZ(1))])
    def program(tape, angles):
        tape.ry(angles[0], 0); tape.ry(angles[1], 1); tape.cx(0, 1)
        return tape.expval(observable)
    node = QNode(program, 2)
    angles = np.array([.4, -.3])
    expected = [-np.sin(.4) * (1 + .7 * np.cos(-.3)), -.7 * np.cos(.4) * np.sin(-.3)]
    np.testing.assert_allclose(node.gradient(angles), expected, atol=1e-10)
    np.testing.assert_allclose(node.gradient(angles, method="parameter-shift"), expected, atol=1e-10)


def test_probability_and_nested_multiple_output_jacobians():
    def program(tape, theta):
        tape.ry(theta, 0)
        return {"z": tape.expval(PauliZ(0)), "more": [tape.probs([0]), (tape.var(PauliZ(0)),)]}
    node = QNode(program, 1)
    for method in ("adjoint", "parameter-shift", "finite-diff"):
        result = node.jacobian(.4, method=method)
        assert result["z"] == pytest.approx(-np.sin(.4), abs=1e-8)
        assert result["more"][0] == pytest.approx({"0": -.5 * np.sin(.4), "1": .5 * np.sin(.4)}, abs=1e-8)
        assert result["more"][1][0] == pytest.approx(np.sin(.8), abs=1e-8)
    with pytest.raises(ValueError): node.gradient(.4)


def test_jacobian_products_and_execute_derivative_contracts():
    def program(tape, angles):
        tape.ry(angles[0], 0); tape.ry(angles[1], 1)
        return (tape.expval(PauliZ(0)), tape.expval(PauliZ(1)))
    node = QNode(program, 2)
    angles = np.array([.3, .7])
    expected = np.diag(-np.sin(angles))
    value, jacobian = node.execute_and_compute_derivatives(angles)
    np.testing.assert_allclose(jacobian, expected, atol=1e-12)
    np.testing.assert_allclose(value, np.cos(angles))
    np.testing.assert_allclose(node.compute_vjp((2., -3.), angles), np.array([2., -3.]) @ expected)
    np.testing.assert_allclose(node.compute_jvp(np.array([2., -3.]), angles), expected @ [2., -3.])
    with pytest.raises(ValueError): node.compute_vjp(np.ones(2), angles)
    with pytest.raises(ValueError): node.compute_jvp(np.ones(3), angles)
    with pytest.raises(TypeError): node.compute_jvp(np.ones(2, dtype=complex), angles)


def test_keyword_nontrainable_and_multiple_trainable_arguments():
    def program(tape, theta, feature=.2, *, scale=.3):
        tape.ry(theta * feature + scale, 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1)
    assert node.gradient(theta=.4) == pytest.approx(-.2 * np.sin(.38))
    derivatives = node.gradient(.4, .2, scale=.3, argnums=(0,), argnames=("scale",))
    np.testing.assert_allclose(derivatives, [-.2 * np.sin(.38), -np.sin(.38)])
    assert node.gradient(.4, .2, scale=.3, argnums="scale") == pytest.approx(-np.sin(.38))


def test_unused_and_array_inputs_have_mathematically_correct_shapes():
    node = QNode(lambda t, a: (t.ry(a[0, 1], 0), t.expval(PauliZ(0)))[-1], 1)
    expected = np.zeros((2, 2)); expected[0, 1] = -np.sin(.2)
    np.testing.assert_allclose(node.gradient(np.array([[.1, .2], [.3, .4]])), expected)
    constant = QNode(lambda t, x: t.expval(PauliZ(0)), 1)
    assert constant.gradient(.3) == pytest.approx(0)


def test_fixed_noise_mixed_state_gradient_is_not_pure_substitution():
    def program(tape, theta):
        tape.ry(theta, 0); tape.amplitude_damping(.3, 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1, device=DensityMatrixDevice())
    for method in ("parameter-shift", "finite-diff"):
        assert node.gradient(.4, method=method) == pytest.approx(-.7 * np.sin(.4), abs=1e-8)
    with pytest.raises(UnsupportedFeature): node.gradient(.4, method="adjoint")


def test_dynamic_branch_probability_and_conditional_gate_gradients():
    def program(tape, angles):
        tape.ry(angles[0], 0)
        outcome = tape.measure(0, reset=True)
        tape.cond(outcome, lambda branch: branch.ry(angles[1], 1))
        return tape.expval(PauliZ(1))
    angles = np.array([.7, .3])
    expected = [.5 * np.sin(.7) * (np.cos(.3) - 1), -np.sin(.7 / 2) ** 2 * np.sin(.3)]
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
        node = QNode(program, 2, device=device)
        np.testing.assert_allclose(node.gradient(angles), expected, atol=1e-10)
        with pytest.raises(UnsupportedFeature): node.gradient(angles, method="adjoint")


def test_mps_hundred_qubit_gradient_never_expands_dense_state(monkeypatch):
    def forbidden(*args, **kwargs): pytest.fail("Dense state expansion used for MPS gradient")
    monkeypatch.setattr(MatrixProductState, "statevector", forbidden)
    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    monkeypatch.setattr(DensityMatrixDevice, "density_matrix", forbidden)
    def program(tape, theta):
        tape.ry(theta, 0)
        for wire in range(99): tape.cx(wire, wire + 1)
        return tape.expval(PauliZ(99))
    node = QNode(program, 100, device=MatrixProductStateDevice(max_memory_mb=2))
    assert node.gradient(.4) == pytest.approx(-np.sin(.4), abs=1e-10)
    resources = node.last_metadata["gradient_resource_evaluations"]
    assert all(item["resources"]["max_bond_observed"] == 2 for item in resources)
    assert all(max(item["resources"]["bond_dimensions"]) == 2 for item in resources)
    assert all("approximation_warning" in item for item in resources)
    with pytest.raises(UnsupportedFeature): node.gradient(.4, method="adjoint")


def test_real_finite_shot_vectors_are_independent_ordered_and_seeded():
    def program(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0)), tape.counts([0]), tape.probs([0])
    node = QNode(program, 1, shots=[100, (200, 2)], seed=51)
    result = node(.8)
    assert result == node(.8)
    assert len(result) == 3
    assert [sum(part[1].values()) for part in result] == [100, 200, 200]
    assert len(set(item["seed"] for item in node.last_metadata["partitions"])) == 3
    assert all(abs(part[0] - np.cos(.8)) < .25 for part in result)
    with pytest.raises(UnsupportedFeature): node.jacobian(.8)


def test_finite_shot_shift_estimates_are_not_analytic_results():
    node = rotation(shots=[5000, 6000], seed=12)
    derivative = node.jacobian(.8, method="parameter-shift")
    np.testing.assert_allclose(derivative, [-np.sin(.8)] * 2, atol=.04)
    assert node.last_metadata["gradient_semantics"] == "finite-shot estimate"
    with pytest.raises(UnsupportedFeature): node.jacobian(.8, method="adjoint")


def test_shot_validation_and_resource_limits():
    for value in (0, True, [], [None], [(100, 0)], [(1, 10001)], [1.2]):
        with pytest.raises(ValueError): ShotSpec.parse(value)
    assert ShotSpec.parse(None).partitions == (None,)
    assert ShotSpec.parse(12).partitions == (12,)
    with pytest.raises(ValueError, match="max_shots"):
        rotation(shots=20, device=StatevectorDevice(execution_limits=ExecutionLimits(max_shots=10)))(.2)


def test_capability_rejections_never_fallback_silently():
    for method in ("backprop", "unknown"):
        with pytest.raises(UnsupportedFeature): rotation().gradient(.4, method=method)
    with pytest.raises(UnsupportedFeature): rotation(device=StabilizerDevice()).gradient(.4)
    assert rotation(max_diff=2).gradient(.4) == pytest.approx(-np.sin(.4), abs=1e-12)
    with pytest.raises(UnsupportedFeature): rotation(max_diff=3).gradient(.4)
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: (t.ry(x, 0), t.state())[-1], 1).jacobian(.4)
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: (t.ry(x if x > 0 else -x, 0), t.expval(PauliZ(0)))[-1], 1).gradient(.4)
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: (t.ry(float(x), 0), t.expval(PauliZ(0)))[-1], 1).gradient(.4)
    with pytest.raises(TypeError): rotation().gradient(1)


def test_finite_difference_convergence_and_nondefault_shift_coefficient():
    node = rotation()
    errors = []
    for step in (.1, .01, .001):
        node.gradient_kwargs = {"step": step}
        errors.append(abs(node.gradient(.7, method="finite-diff") + np.sin(.7)))
    assert errors[2] < errors[1] < errors[0]
    assert parameter_shift(lambda x: np.cos(x[0]), .4, shift=.7) == pytest.approx(-np.sin(.4))
    with pytest.raises(ValueError): parameter_shift(lambda x: x[0], .4, shift=0)


def test_native_training_reduces_loss_with_reproducible_gradients():
    def program(tape, angles):
        tape.ry(angles[0], 0); tape.ry(angles[1], 1); tape.cx(0, 1)
        return tape.expval(Hamiltonian([(1, PauliZ(0)), (1, PauliZ(1))]))
    node = QNode(program, 2)
    angles = np.array([.8, .5]); initial = node(angles)
    trace = []
    for _ in range(50):
        gradient = node.gradient(angles)
        trace.append(gradient)
        angles -= .1 * gradient
    assert node(angles) < initial - 2
    assert node(angles) < -1.9
    np.testing.assert_allclose(trace[0], [-np.sin(.8) * (1 + np.cos(.5)), -np.cos(.8) * np.sin(.5)])


def test_two_qubit_generators_and_dense_observable_adjoint_are_real_derivatives():
    for gate in ("rxx", "ryy", "rzz", "cp"):
        def program(tape, theta):
            if gate in {"rzz", "cp"}: tape.h(0)
            if gate == "cp": tape.h(1)
            getattr(tape, gate)(theta, 0, 1)
            return tape.expval(PauliX(0) if gate in {"rzz", "cp"} else PauliZ(0))
        node = QNode(program, 2)
        actual = node.gradient(.4, method="adjoint")
        assert actual == pytest.approx((- .5 if gate == "cp" else -1.) * np.sin(.4), abs=1e-10)
        assert actual == pytest.approx(node.gradient(.4, method="parameter-shift"), abs=1e-10)
        assert actual == pytest.approx(node.gradient(.4, method="finite-diff"), abs=1e-8)
    matrix = np.array([[.4, .2 - .3j], [.2 + .3j, -.4]])
    node = rotation(observable=matrix)
    assert node.gradient(.4) == pytest.approx(.2 * np.cos(.4) - .4 * np.sin(.4), abs=1e-10)


def test_classical_arithmetic_trace_does_not_drop_derivatives():
    def program(tape, x):
        value = np.cos(x) + np.tan(x / 3) + np.exp(x) - np.log(x + 2) + np.sqrt(x + 3)
        value += x ** 2 + 2 ** x + np.absolute(-x) + 2 / x + x * x - x / 2
        tape.ry(value, 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1)
    x, step = .4, 1e-6
    expected = (node(x + step) - node(x - step)) / (2 * step)
    assert node.gradient(x) == pytest.approx(expected, abs=1e-8)
    def array_program(tape, values):
        tape.ry(np.sin(values).sum(), 0)
        return tape.expval(PauliZ(0))
    values = np.array([.2, .4])
    np.testing.assert_allclose(QNode(array_program, 1).gradient(values), -np.sin(np.sin(values).sum()) * np.cos(values))


def test_trace_and_output_resource_errors_are_explicit():
    with pytest.raises(MemoryError): rotation().gradient(np.zeros(1025))
    with pytest.raises(ValueError): rotation()(np.ones(2))
    with pytest.raises(ValueError): rotation()(float("nan"))
    with pytest.raises(ValueError): rotation().gradient(.3, argnums=(0, 0))
    with pytest.raises(ValueError): rotation().gradient(.3, argnums=())
    with pytest.raises(ValueError): rotation().gradient(float("inf"))
    with pytest.raises(UnsupportedFeature): QNode(lambda t: t.probs(), 17)()
    with pytest.raises(UnsupportedFeature): QNode(lambda t: {"x": t.expval(PauliZ(0)), "constant": 1}, 1)()
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: (t.ry(np.floor(x), 0), t.expval(PauliZ(0)))[-1], 1).gradient(.3)
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: (t.ry(abs(x), 0), t.expval(PauliZ(0)))[-1], 1).gradient(0.)


def test_finite_shot_hamiltonian_and_dense_measurements_sample_actual_states():
    def program(tape, theta):
        tape.ry(theta, 0)
        return (tape.expval(Hamiltonian([(.2, PauliX(0)), (.4, PauliZ(0))])),
                tape.expval(np.array([[1, 0], [0, -1]])), tape.var(PauliZ(0)))
    output = QNode(program, 1, shots=5000, seed=29)(.4)
    np.testing.assert_allclose(output, [.2 * np.sin(.4) + .4 * np.cos(.4), np.cos(.4), np.sin(.4) ** 2], atol=.04)


def test_dynamic_finite_shot_gradient_uses_all_branch_probabilities():
    def program(tape, theta):
        tape.ry(theta, 0); outcome = tape.measure(0)
        tape.cond(outcome, lambda branch: branch.x(1))
        return tape.expval(PauliZ(1))
    node = QNode(program, 2, shots=2000, seed=18)
    assert node.gradient(.7) == pytest.approx(-np.sin(.7), abs=.06)


def test_adjoint_reverse_sweep_never_uses_shift_or_finite_difference(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    def forbidden(*args, **kwargs): pytest.fail("Shift/finite-difference path used by adjoint")
    monkeypatch.setattr(ExecutionPlan, "_occurrences", forbidden)
    node = rotation(diff_method="adjoint")
    assert node.gradient(.4) == pytest.approx(-np.sin(.4), abs=1e-10)
    assert node.last_metadata["gradient_method"] == "adjoint"
    assert node.last_metadata["shifted_evaluation_count"] == 0
    assert node.last_metadata["derivative_evaluation_count"] == 1
