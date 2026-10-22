# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Exact coherent phase and native derivatives after real composition."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def rz(x):return np.diag(np.exp([-.5j*x,.5j*x]))
def ry(x):return np.array([[np.cos(x/2),-np.sin(x/2)],[np.sin(x/2),np.cos(x/2)]])


def pair():
    p,q=qb.Parameter("p"),qb.Parameter("q")
    a=qb.Circuit(1).rz(p,0);a.global_phase=p/3
    b=qb.Circuit(1).ry(q,0);b.global_phase=q.sin()/5
    return a,b,p,q


def test_normal_compose_retains_noncommuting_order_and_complex_phase():
    a,b,p,q=pair();out=a.compose(b).bind({p:.3,q:.4})
    np.testing.assert_allclose(Operator(out).data,np.exp(1j*(.1+np.sin(.4)/5))*ry(.4)@rz(.3),atol=5e-13,rtol=0)


def test_front_compose_reverses_multiplication_not_phase_sign():
    a,b,p,q=pair();out=a.compose(b,front=True).bind({p:.3,q:.4})
    np.testing.assert_allclose(Operator(out).data,np.exp(1j*(.1+np.sin(.4)/5))*rz(.3)@ry(.4),atol=5e-13,rtol=0)


def test_wrap_keeps_phase_inside_definition_and_never_counts_it_twice():
    a,b,p,q=pair();out=a.compose(b,wrap=True).bind({p:.3,q:.4})
    np.testing.assert_allclose(Operator(out).data,np.exp(1j*(.1+np.sin(.4)/5))*ry(.4)@rz(.3),atol=5e-13,rtol=0)


def test_inverse_of_composed_symbolic_circuit_is_full_complex_adjoint():
    a,b,p,q=pair();source=a.compose(b,wrap=True).bind({p:.3,q:.4})
    np.testing.assert_allclose(Operator(source.inverse()).data,Operator(source).data.conj().T,atol=5e-13,rtol=0)


def test_controlled_conversion_keeps_original_global_phase_observable():
    p=qb.Parameter("p");source=qb.Circuit(1).ry(p,0);source.global_phase=p/3
    composed=qb.Circuit(1).compose(source,wrap=True)
    circuit=qb.Circuit(2).h(0).append(composed.to_gate().control(),[0,1])
    node=QNode.from_circuit(circuit,qb.PauliX(0),diff_method="parameter-shift",max_diff=2)
    x=.4;expected=np.cos(x/3)*np.cos(x/2)
    gradient=-np.sin(x/3)*np.cos(x/2)/3-np.cos(x/3)*np.sin(x/2)/2
    assert node(x)==pytest.approx(expected,abs=3e-12)
    assert np.asarray(node.compute_jacobian(x)).item()==pytest.approx(gradient,abs=4e-11)


def test_composed_nonlinear_qnode_has_actual_analytic_hessian_and_hvp():
    p=qb.Parameter("p");inner=qb.Circuit(1).ry(2*p+p.sin(),0)
    circuit=qb.Circuit(1).compose(inner,wrap=True).compose(inner,wrap=True)
    node=QNode.from_circuit(circuit,qb.PauliZ(0),diff_method="parameter-shift",max_diff=2)
    x=.3;angle=4*x+2*np.sin(x);first=4+2*np.cos(x);second=-2*np.sin(x)
    expected=-np.cos(angle)*first**2-np.sin(angle)*second
    assert float(node.compute_hessian(x))==pytest.approx(expected,abs=5e-10)
    assert float(node.compute_hvp(.7,x))==pytest.approx(.7*expected,abs=5e-10)


def test_wrapped_vector_ir_roundtrip_keeps_one_live_container_and_key_binding():
    vector=qb.ParameterVector("v",3)
    source=qb.Circuit(1).ry(vector[0],0)
    peer=qb.Circuit(1).rz(vector[1]+vector[2],0)
    out=qb.Circuit(1).compose(source,wrap=True).compose(peer,wrap=True)
    restored=circuit_from_ir(IRProgram.from_json(out.to_ir().to_json()))
    assert all(p.vector is restored.parameters[0].vector for p in restored.parameters)
    np.testing.assert_allclose(Operator(restored.bind({vector:[.2,.3,.4]})).data,rz(.7)@ry(.2),atol=5e-13,rtol=0)


def test_hundred_wire_wrapped_composition_runs_mps_without_dense_conversion(monkeypatch):
    source=qb.Circuit(100).ry(.4,99)
    wrapped=qb.Circuit(100).compose(source,wrap=True)
    monkeypatch.setattr(qb.MatrixProductState,"statevector",lambda *a,**k:pytest.fail("wide dense conversion"))
    device=qb.MatrixProductStateDevice()
    assert device.expectation(wrapped,qb.PauliZ(99))==pytest.approx(np.cos(.4),abs=3e-12)


def test_open_control_of_a_wrapped_composition_preserves_the_entire_phase_block():
    a,b,p,q=pair();composed=a.compose(b,wrap=True).bind({p:.3,q:.4})
    controlled=composed.to_gate().control(1,ctrl_state=0)
    expected=np.eye(4,dtype=complex)
    expected[:2,:2]=np.exp(1j*(.1+np.sin(.4)/5))*ry(.4)@rz(.3)
    np.testing.assert_allclose(Operator(controlled).data,expected,atol=7e-13,rtol=0)


def test_inplace_composition_phase_matches_independent_full_matrix():
    a,b,p,q=pair()
    assert a.compose(b,inplace=True,wrap=True) is None
    np.testing.assert_allclose(Operator(a.bind({p:.3,q:.4})).data,
        np.exp(1j*(.1+np.sin(.4)/5))*ry(.4)@rz(.3),atol=5e-13,rtol=0)


def test_copy_of_composed_symbolic_phase_has_independent_rebinding():
    a,b,p,q=pair();source=a.compose(b,wrap=True);peer=source.copy()
    peer.assign_parameters({p:.3,q:.4},inplace=True)
    assert source.parameters==(p,q) and not peer.parameters
    np.testing.assert_allclose(Operator(peer).data,np.exp(1j*(.1+np.sin(.4)/5))*ry(.4)@rz(.3),atol=5e-13,rtol=0)


@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
def test_wrapped_composition_has_real_framework_gradient(framework):
    p=qb.Parameter("p");circuit=qb.Circuit(1).compose(qb.Circuit(1).ry(2*p+p.sin(),0),wrap=True)
    node=QNode.from_circuit(circuit,qb.PauliZ(0),interface=framework,diff_method="parameter-shift")
    x=.3;expected=-np.sin(2*x+np.sin(x))*(2+np.cos(x))
    module=pytest.importorskip(framework)
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True);node(value).backward();actual=float(value.grad)
    elif framework=="autograd":actual=float(module.grad(node)(x))
    elif framework=="jax":actual=float(module.grad(node)(module.numpy.asarray(x,dtype=module.numpy.float64)))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as tape:result=node(value)
        actual=float(tape.gradient(result,value))
    assert actual==pytest.approx(expected,abs=2e-10)
