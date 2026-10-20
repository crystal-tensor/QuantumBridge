"""Template inputs retain native quantum derivatives and framework graphs."""
import numpy as np
import pytest
from quantumbridge import Circuit, StatevectorDevice, DensityMatrixDevice, MatrixProductState, MatrixProductStateDevice, templates as t, qchem
from quantumbridge.qml import QNode
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.utils.math import PauliX, PauliZ


def test_angle_shared_nonlinear_input_chain_rule_is_analytic():
    def program(tape,x):
        t.AngleEmbedding([np.sin(x),2*x],[0,1],rotation='Y').apply(tape)
        tape.cx(0,1)
        return tape.expval(PauliZ(1))
    node=QNode(program,2);x=.37
    expected=-np.sin(np.sin(x))*np.cos(x)*np.cos(2*x)-2*np.cos(np.sin(x))*np.sin(2*x)
    for method in ('adjoint','parameter-shift'):
        assert node.gradient(x,method=method)==pytest.approx(expected,abs=1e-11)
    assert node.last_metadata['classical_chain_rule']


def test_basic_tensor_weights_jacobian_matches_sum_rotation_formula():
    def program(tape,w):
        t.BasicEntanglerLayers(w,[0],rotation='Y').apply(tape)
        return tape.expval(PauliZ(0))
    weights=np.array([[.2],[.4]])
    node=QNode(program,1)
    for method in ('adjoint','parameter-shift'):
        np.testing.assert_allclose(node.gradient(weights,method=method),np.full((2,1),-np.sin(.6)),atol=1e-12)


def test_strong_shared_nonlinear_rot_parameters_preserve_chain_rule():
    def program(tape,x):
        t.StronglyEntanglingLayers([[[x*x,np.sin(x),2*x]]],[0]).apply(tape)
        return tape.expval(PauliX(0))
    node=QNode(program,1);x=.31
    expected=np.cos(np.sin(x))*np.cos(x)*np.cos(2*x)-2*np.sin(np.sin(x))*np.sin(2*x)
    for method in ('adjoint','parameter-shift'):
        assert node.gradient(x,method=method)==pytest.approx(expected,abs=1e-11)


def test_keyword_tensor_weights_and_nontrainable_static_features():
    def program(tape,features,*,weights):
        t.AngleEmbedding(features,[0],rotation='Y').apply(tape)
        t.BasicEntanglerLayers(weights,[0],rotation='Y').apply(tape)
        return tape.expval(PauliZ(0))
    node=QNode(program,1)
    result=node.gradient([.2],weights=np.array([[.3]]),argnums=(),argnames='weights')
    np.testing.assert_allclose(result,[[-np.sin(.5)]],atol=1e-12)


def test_template_multioutput_nested_jacobian_and_jvp_vjp():
    def program(tape,w):
        t.BasicEntanglerLayers(w,[0],rotation='Y').apply(tape)
        return {'z':tape.expval(PauliZ(0)),'probabilities':tape.probs([0])}
    node=QNode(program,1);w=np.array([[.2],[.4]])
    jac=node.jacobian(w)
    np.testing.assert_allclose(jac['z'],np.full((2,1),-np.sin(.6)))
    np.testing.assert_allclose(jac['probabilities']['0'],np.full((2,1),-.5*np.sin(.6)))
    jvp=node.compute_jvp(np.ones_like(w),w)
    assert jvp['z']==pytest.approx(-2*np.sin(.6))
    cotangent={'z':1.,'probabilities':{'0':0.,'1':0.}}
    np.testing.assert_allclose(node.compute_vjp(cotangent,w),jac['z'])


def test_iqp_feature_product_gradients_match_central_difference():
    def program(tape,x):
        t.IQPEmbedding([x,2*x],[0,1],n_repeats=2).apply(tape)
        return tape.expval(PauliX(1))
    node=QNode(program,2);x=.37
    expected=(node(x+1e-6)-node(x-1e-6))/2e-6
    for method in ('adjoint','parameter-shift'):
        assert node.gradient(x,method=method)==pytest.approx(expected,abs=1e-8)


def test_trotter_time_gradient_includes_identity_phase_without_spurious_signal():
    from quantumbridge.utils.math import Hamiltonian,PauliString
    h=Hamiltonian([(.2,PauliString([])),(.4,PauliX(0))])
    def program(tape,time):
        t.TrotterProduct(h,time,[0],n=2,order=2).apply(tape)
        return tape.expval(PauliZ(0))
    node=QNode(program,1)
    for method in ('adjoint','parameter-shift'):
        assert node.gradient(.3,method=method)==pytest.approx(-.8*np.sin(.24),abs=1e-11)


def test_amplitude_and_basis_trainable_input_are_explicitly_unsupported():
    def program(tape,x):
        t.AmplitudeEmbedding(x,[0],normalize=True).apply(tape)
        return tape.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature,match='static'):
        QNode(program,1).gradient(np.array([.3,.4]))
    def basis(tape,x):
        t.BasisEmbedding(x,[0]).apply(tape)
        return tape.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature): QNode(basis,1).gradient(np.array([1.]))


def test_native_basic_template_optimization_is_deterministic_and_updates_weights():
    def program(tape,w):
        t.BasicEntanglerLayers(w,[0],rotation='Y').apply(tape)
        return tape.expval(PauliZ(0))
    node=QNode(program,1);weights=np.array([[.3],[.4]])
    initial=(node(weights)+1)**2
    for _ in range(60):
        value=node(weights)
        weights-=.12*2*(value+1)*node.gradient(weights)
    assert (node(weights)+1)**2<initial/1000
    assert np.linalg.norm(weights-np.array([[.3],[.4]]))>.5


def test_torch_template_backward_and_sgd_retain_nonleaf_parameter_graph():
    torch=pytest.importorskip('torch')
    def program(tape,x):
        t.StronglyEntanglingLayers([[[x*x,torch.sin(x),2*x]]],[0]).apply(tape)
        return tape.expval(PauliX(0))
    node=QNode(program,1,interface='torch');x=torch.tensor(.31,dtype=torch.float64,requires_grad=True)
    value=node(x);value.backward()
    expected=np.cos(np.sin(.31))*np.cos(.31)*np.cos(.62)-2*np.sin(np.sin(.31))*np.sin(.62)
    assert x.grad.item()==pytest.approx(expected,abs=1e-11)
    optimizer=torch.optim.SGD([x],lr=.15)
    initial=(node(x)-.1).item()**2
    for _ in range(35):
        optimizer.zero_grad();loss=(node(x)-.1)**2;loss.backward();optimizer.step()
    assert (node(x)-.1).item()**2<initial/10


def test_autograd_template_tensor_gradient_uses_native_quantum_engine():
    ag=pytest.importorskip('autograd')
    import autograd.numpy as anp
    def program(tape,w):
        t.BasicEntanglerLayers(anp.sin(w),[0],rotation='Y').apply(tape)
        return tape.expval(PauliZ(0))
    node=QNode(program,1,interface='autograd');w=np.array([[.2],[.4]])
    expected=-np.sin(np.sin(w).sum())*np.cos(w)
    np.testing.assert_allclose(ag.grad(node)(w),expected,atol=1e-11)


def test_generated_qchem_hamiltonian_template_ansatz_energy_and_gradient():
    problem=qchem.molecular_hamiltonian_native(qchem.Molecule(['H','H'],[(0,0,0),(0,0,1.4)],unit='bohr'))
    h=problem.hamiltonian.to_quantumbridge()
    def program(tape,x):
        t.BasisEmbedding(qchem.hf_state(2,4),range(4)).apply(tape)
        t.StronglyEntanglingLayers([[[0.,x,0.]]],[0]).apply(tape)
        qchem.apply_fermionic_excitation(tape,-.2,[0,1,2,3])
        return tape.expval(h)
    node=QNode(program,4);x=.4
    expected=(node(x+1e-6)-node(x-1e-6))/2e-6
    assert abs(expected)>.01
    assert node.gradient(x)==pytest.approx(expected,abs=1e-8)
    initial=node(x)
    for _ in range(20): x-=.3*node.gradient(x)
    assert node(x)<initial and node(x)>=problem.exact_ground_energy()-1e-10


def test_hundred_wire_mps_template_shift_never_uses_dense_expansion(monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('Dense expansion forbidden')
    monkeypatch.setattr(StatevectorDevice,'statevector',forbidden)
    monkeypatch.setattr(DensityMatrixDevice,'density_matrix',forbidden)
    monkeypatch.setattr(MatrixProductState,'statevector',forbidden)
    def program(tape,x):
        tape.h(0)
        for q in range(99): tape.cx(q,q+1)
        t.AngleEmbedding([x],[99],rotation='Y').apply(tape)
        return tape.expval(PauliZ(0).tensor(PauliZ(99)))
    device=MatrixProductStateDevice(max_memory_mb=2,max_bond_dim=4,cutoff=0)
    node=QNode(program,100,device=device)
    assert node(.3)==pytest.approx(np.cos(.3),abs=1e-11)
    assert node.gradient(.3,method='parameter-shift')==pytest.approx(-np.sin(.3),abs=1e-10)
    resources=node.last_metadata['partitions'][0]['resources']
    assert max(resources['bond_dimensions'])<=2
    assert node.last_metadata['shifted_evaluation_count']==2
