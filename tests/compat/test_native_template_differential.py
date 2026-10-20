"""Public SDK black-box comparisons; no upstream implementation/test source."""
import numpy as np
import pytest
qml=pytest.importorskip('pennylane')
from quantumbridge import Circuit, templates as t
from quantumbridge.qml import QNode
from quantumbridge.information import Operator
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def compare(native, public, width):
    np.testing.assert_allclose(Operator.from_circuit(native.to_circuit()).data,qml.matrix(public,wire_order=range(width)),atol=2e-12,rtol=0)


def test_public_angle_three_rotation_axes_complex_matrices():
    for axis in ('X','Y','Z'):
        compare(t.AngleEmbedding([.2,-.4],[0,1],rotation=axis),qml.AngleEmbedding([.2,-.4],wires=[0,1],rotation=axis),2)


def test_public_partial_angle_features_and_wire_order():
    native=t.AngleEmbedding([.2],[1,0],rotation='Y').apply(Circuit(2))
    expected=qml.matrix(qml.AngleEmbedding([.2],wires=[1,0],rotation='Y'),wire_order=range(2))
    np.testing.assert_allclose(Operator.from_circuit(native).data,expected,atol=1e-12,rtol=0)


def test_public_basis_integer_prepares_identical_occupation():
    from quantumbridge import StatevectorDevice
    state=StatevectorDevice().statevector(t.BasisEmbedding(5,range(3)).to_circuit())
    device=qml.device('default.qubit',wires=3)
    @qml.qnode(device)
    def oracle():
        qml.BasisEmbedding(5,wires=range(3));return qml.state()
    np.testing.assert_allclose(state,oracle(),atol=1e-12,rtol=0)


def test_public_complex_amplitude_preparation_state():
    from quantumbridge import StatevectorDevice
    data=np.array([1j,.2,-.4j,.7]);data/=np.linalg.norm(data)
    state=StatevectorDevice().statevector(t.AmplitudeEmbedding(data,[0,1]).to_circuit())
    device=qml.device('default.qubit',wires=2)
    @qml.qnode(device)
    def oracle():
        qml.AmplitudeEmbedding(data,wires=[0,1]);return qml.state()
    np.testing.assert_allclose(state,oracle(),atol=1e-12,rtol=0)


def test_public_padding_normalization_order():
    from quantumbridge import StatevectorDevice
    state=StatevectorDevice().statevector(t.AmplitudeEmbedding([2,1j],[0,1],pad_with=2j,normalize=True).to_circuit())
    device=qml.device('default.qubit',wires=2)
    @qml.qnode(device)
    def oracle():
        qml.AmplitudeEmbedding([2,1j],wires=[0,1],pad_with=2j,normalize=True);return qml.state()
    np.testing.assert_allclose(state,oracle(),atol=1e-12,rtol=0)


def test_public_basic_two_wire_does_not_add_reversed_entangler():
    data=np.array([[.2,.3],[-.1,.4]])
    compare(t.BasicEntanglerLayers(data,[0,1]),qml.BasicEntanglerLayers(data,wires=[0,1]),2)


def test_public_basic_multilayer_ring_with_rotation_choice():
    data=np.arange(12).reshape(3,4)/13
    compare(t.BasicEntanglerLayers(data,range(4),rotation='Y'),qml.BasicEntanglerLayers(data,wires=range(4),rotation=qml.RY),4)


def test_public_strong_single_wire_euler_semantics():
    data=np.array([[[.2,-.3,.4]],[[.5,.1,-.2]]])
    compare(t.StronglyEntanglingLayers(data,[0]),qml.StronglyEntanglingLayers(data,wires=[0]),1)


def test_public_strong_range_two_cz_imprimitive():
    data=np.arange(18).reshape(2,3,3)/19
    compare(t.StronglyEntanglingLayers(data,range(3),ranges=[2,1],imprimitive='cz'),
            qml.StronglyEntanglingLayers(data,wires=range(3),ranges=[2,1],imprimitive=qml.CZ),3)


def test_public_iqp_repeated_custom_pattern_full_operator():
    data=[.2,.4,-.3];pattern=[(0,2),(2,1)]
    compare(t.IQPEmbedding(data,range(3),n_repeats=2,pattern=pattern),
            qml.IQPEmbedding(data,wires=range(3),n_repeats=2,pattern=pattern),3)


def test_public_qft_inverse_full_complex_operator():
    compare(t.QFT(range(4),inverse=True),qml.adjoint(qml.QFT(wires=range(4))),4)


def test_public_trotter_first_and_second_order_operand_conventions():
    native=Hamiltonian([(.4,PauliX(0)),(.7,PauliZ(0))])
    public=qml.Hamiltonian([.4,.7],[qml.X(0),qml.Z(0)])
    for order in (1,2):
        compare(t.TrotterProduct(native,.7,[0],n=3,order=order),qml.TrotterProduct(public,.7,n=3,order=order),1)


def test_public_angle_nonlinear_shared_input_gradient():
    from pennylane import numpy as pnp
    from quantumbridge.utils.math import PauliZ
    def native(tape,x):
        t.AngleEmbedding([np.sin(x),2*x],[0,1],rotation='Y').apply(tape);tape.cx(0,1)
        return tape.expval(PauliZ(1))
    device=qml.device('default.qubit',wires=2)
    @qml.qnode(device)
    def oracle(x):
        qml.AngleEmbedding(pnp.array([pnp.sin(x),2*x]),wires=[0,1],rotation='Y');qml.CNOT([0,1])
        return qml.expval(qml.Z(1))
    x=pnp.array(.3,requires_grad=True)
    assert QNode(native,2).gradient(.3)==pytest.approx(qml.grad(oracle)(x),abs=1e-10)


def test_public_strong_tensor_jacobian():
    from pennylane import numpy as pnp
    def native(tape,x):
        t.StronglyEntanglingLayers(x,[0,1]).apply(tape)
        return tape.expval(PauliZ(1))
    device=qml.device('default.qubit',wires=2)
    @qml.qnode(device)
    def oracle(x):
        qml.StronglyEntanglingLayers(x,wires=[0,1]);return qml.expval(qml.Z(1))
    data=np.arange(6).reshape(1,2,3)/7+.1
    np.testing.assert_allclose(QNode(native,2).gradient(data),qml.grad(oracle)(pnp.array(data,requires_grad=True)),atol=1e-10,rtol=0)


def test_public_invalid_basic_shape_rejects_not_truncates():
    with pytest.raises(ValueError): t.BasicEntanglerLayers([[.2]],[0,1])
    with pytest.raises(ValueError): qml.BasicEntanglerLayers([[.2]],wires=[0,1])
