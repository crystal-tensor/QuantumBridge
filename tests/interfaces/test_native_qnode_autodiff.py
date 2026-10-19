# Independent interface graph tests, not upstream SDK wrappers.

import numpy as np
import pytest

from quantumbridge import PauliZ, UnsupportedFeature
from quantumbridge.qml import QNode


def test_torch_backward_nonlinear_preprocessing_and_classical_loss():
    torch = pytest.importorskip("torch")
    def program(tape, theta):
        tape.ry(torch.sin(theta) + theta, 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1, interface="torch")
    theta = torch.tensor(.4, dtype=torch.float64, requires_grad=True)
    output = node(theta); (output ** 2).backward()
    angle = .4 + np.sin(.4)
    assert theta.grad.item() == pytest.approx(-np.sin(2 * angle) * (1 + np.cos(.4)), abs=1e-10)
    assert output.dtype == theta.dtype and output.device == theta.device
    assert node.last_metadata["native_vjp"] is True


def test_torch_gradcheck_repeated_parameters_and_vector_cotangents():
    torch = pytest.importorskip("torch")
    def program(tape, angles, feature):
        tape.ry(angles[0] * feature, 0); tape.ry(angles[0], 0); tape.rx(angles[1], 0)
        return tape.expval(PauliZ(0)), tape.probs([0])
    node = QNode(program, 1)
    angles = torch.tensor([.3, .2], dtype=torch.float64, requires_grad=True)
    feature = torch.tensor(.4, dtype=torch.float64)
    def scalar(values):
        ev, probs = node(values, feature)
        return 2 * ev - 3 * probs["1"]
    assert torch.autograd.gradcheck(scalar, (angles,), eps=1e-6, atol=1e-6)
    gradient, = torch.autograd.grad(scalar(angles), angles)
    expected = [-3.5 * 1.4 * np.sin(.42) * np.cos(.2), -3.5 * np.cos(.42) * np.sin(.2)]
    np.testing.assert_allclose(gradient, expected, atol=1e-10)


def test_torch_optimizer_closes_a_real_two_parameter_training_loop():
    torch = pytest.importorskip("torch")
    def program(tape, values):
        tape.ry(values[0], 0); tape.ry(values[1], 1); tape.cx(0, 1)
        return tape.expval(PauliZ(1))
    node = QNode(program, 2, diff_method="parameter-shift")
    values = torch.tensor([1., .7], dtype=torch.float64, requires_grad=True)
    initial = float(node(values).detach())
    optimizer = torch.optim.SGD([values], lr=.15)
    for _ in range(30):
        optimizer.zero_grad(); loss = node(values); loss.backward(); optimizer.step()
    assert float(node(values).detach()) < initial - 1
    assert not torch.allclose(values, torch.tensor([1., .7], dtype=torch.float64))


def test_torch_unused_inputs_float32_and_explicit_higher_order_rejection():
    torch = pytest.importorskip("torch")
    node = QNode(lambda t, x: t.expval(PauliZ(0)), 1)
    x = torch.tensor(.3, dtype=torch.float32, requires_grad=True)
    assert torch.autograd.grad(node(x), x)[0].item() == 0
    node = QNode(lambda t, x: (t.ry(x, 0), t.expval(PauliZ(0)))[-1], 1)
    assert node(x).dtype == x.dtype
    with pytest.raises(UnsupportedFeature): torch.autograd.grad(node(x), x, create_graph=True)
    with pytest.raises(UnsupportedFeature): node(torch.empty((), device="meta"))


def test_autograd_real_grad_jacobian_and_nonlinear_chain_rule():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    def program(tape, angles):
        tape.ry(anp.sin(angles[0]) + angles[1], 0)
        return tape.expval(PauliZ(0))
    node = QNode(program, 1, interface="autograd")
    values = anp.array([.3, .2]); angle = np.sin(.3) + .2
    expected = -2 * np.cos(angle) * np.sin(angle) * np.array([np.cos(.3), 1.])
    np.testing.assert_allclose(autograd.grad(lambda x: node(x) ** 2)(values), expected, atol=1e-10)
    np.testing.assert_allclose(autograd.jacobian(node)(values), -np.sin(angle) * np.array([np.cos(.3), 1]), atol=1e-10)
    with pytest.raises(UnsupportedFeature): autograd.hessian(node)(values)


def test_autograd_unused_input_and_native_training_loss():
    autograd = pytest.importorskip("autograd")
    node = QNode(lambda t, x: t.expval(PauliZ(0)), 1, interface="autograd")
    assert autograd.grad(node)(.2) == pytest.approx(0)
    node = QNode(lambda t, x: (t.ry(x, 0), t.expval(PauliZ(0)))[-1], 1, interface="autograd")
    x = .7; initial = node(x)
    for _ in range(25): x -= .2 * autograd.grad(node)(x)
    assert node(x) < initial - 1


def test_unimplemented_frameworks_and_unknown_interfaces_are_explicit():
    for interface in ("jax", "tf", "tensorflow"):
        node = QNode(lambda t, x: (t.ry(x, 0), t.expval(PauliZ(0)))[-1], 1, interface=interface)
        with pytest.raises(UnsupportedFeature): node(.3)
    with pytest.raises(ValueError): QNode(lambda t: t.expval(PauliZ(0)), 1, interface="unknown")
