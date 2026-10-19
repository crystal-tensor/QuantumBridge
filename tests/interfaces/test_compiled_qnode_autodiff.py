# Framework classical graphs with independently compiled native quantum execution.
import numpy as np
import pytest
from quantumbridge import PauliZ
from quantumbridge.qml import QNode


def program(t,x):
    t.ry(2*x,0); t.rx(x,1); t.cx(0,1)
    return t.expval(PauliZ(1))


def test_compiled_torch_preserves_classical_graph():
    torch = pytest.importorskip("torch")
    node = QNode(program,2,interface="torch").compile(basis_gates=("rz","sx","x","cx"),optimization_level=2)
    x = torch.tensor(.31,dtype=torch.float64,requires_grad=True)
    result = node(x); result.backward()
    expected = -2*np.sin(.62)*np.cos(.31)-np.cos(.62)*np.sin(.31)
    assert x.grad.item() == pytest.approx(expected,abs=2e-12)


def test_compiled_autograd_preserves_classical_graph():
    autograd = pytest.importorskip("autograd")
    node = QNode(program,2,interface="autograd").compile(basis_gates=("rz","sx","x","cx"),optimization_level=2)
    expected = -2*np.sin(.62)*np.cos(.31)-np.cos(.62)*np.sin(.31)
    assert autograd.grad(node)(.31) == pytest.approx(expected,abs=2e-12)
