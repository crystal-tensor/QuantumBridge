# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ
from quantumbridge.utils.math import PauliString
from quantumbridge import StatevectorDevice, Circuit, templates, qchem
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import (TransformProgram,TransformLimits,TransformError,transform,
                                     merge_rotations,cancel_inverses,compile,decompose,split_to_single_terms,split_hamiltonian)


class SampleSpy(StatevectorDevice):
    def __init__(self):
        super().__init__()
        self.samples = []

    def sample(self,circuit,wires=None,shots=1,seed=None,parameters=None):
        memory = super().sample(circuit,wires,shots,seed,parameters)
        self.samples.append({"shots":shots,"seed":seed,"memory":tuple(memory)})
        return memory


def fixed_node(**options):
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(.7,PauliX(0)),(.2,PauliX(0).tensor(PauliZ(1)))]))
    return split_non_commuting(QNode(fn,2,**options))


def gradient_runs(metadata):
    return [run for child in metadata["gradient_executions"] for run in child["gradient_evaluations"]]


def joint_receipts(metadata):
    return [receipt for run in gradient_runs(metadata) for partition in run.get("partitions",())
            for receipt in partition.get("joint_measurements",())]


def test_torch_loss_backward_reaches_qwc_child_means_and_original_theta():
    torch = pytest.importorskip("torch")
    hamiltonian = Hamiltonian([(.7,PauliX(0)),(.2,PauliX(0).tensor(PauliZ(1)))])
    def circuit(tape,theta):
        tape.ry(theta,0)
        return tape.expval(hamiltonian)
    node = split_non_commuting(QNode(circuit,2,diff_method="parameter-shift"))
    theta = torch.tensor(.37,dtype=torch.float64,requires_grad=True)
    energy = node(theta)
    assert isinstance(energy,torch.Tensor) and energy.grad_fn is not None
    loss = energy ** 2
    loss.backward()
    expected = .9*np.sin(.37)
    assert energy.item() == pytest.approx(expected,abs=1e-12)
    assert theta.grad.item() == pytest.approx(2*expected*.9*np.cos(.37),abs=1e-12)
    assert node.last_metadata["native_vjp"]
    assert node.last_metadata["postprocessing_chain_rule"]
    assert node.last_metadata["executed_tape_count"] == 1
    assert node.last_metadata["shifted_evaluation_count"] == 2


@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_native_qwc_gradient_uses_the_requested_quantum_algorithm(method):
    node = fixed_node(diff_method=method)
    for x in [.2,.7,-.3]:
        assert node.gradient(x) == pytest.approx(.9*np.cos(x),abs=1e-12)
        assert node.last_metadata["gradient_method"] == method
        assert node.last_metadata["postprocessing_chain_rule"]
        assert node.last_metadata["transform_count"] == 1


def test_shared_nonlinear_angles_survive_merge_decompose_compile_and_grouping():
    def fn(tape,x):
        tape.ry(np.sin(x),0)
        tape.ry(2*x,0)
        return tape.expval(Hamiltonian([(.7,PauliZ(0)),(.2,PauliX(0))]))
    node = TransformProgram([merge_rotations,decompose(gate_set={"RY","RZ","CNOT"}),
                             compile(basis_set={"RY","RZ","CX"}),split_non_commuting])(QNode(fn,1))
    x = .37
    angle = np.sin(x)+2*x
    expected = (-.7*np.sin(angle)+.2*np.cos(angle))*(np.cos(x)+2)
    assert node.gradient(x) == pytest.approx(expected,abs=1e-12)
    assert node.last_metadata["source_gate_parameter_count"] == 2
    assert node.last_metadata["gate_parameter_count"] == 2


def test_nested_jacobian_reconstruction_preserves_each_result_leaf_shape():
    def fn(tape,x):
        tape.ry(x[0],0)
        tape.rz(x[1],0)
        return {"a":tape.expval(PauliZ(0)),"b":[tape.expval(PauliX(0)),(tape.expval(PauliZ(1)),)]}
    node = split_non_commuting(QNode(fn,2))
    x = np.array([.2,.4])
    jac = node.jacobian(x)
    np.testing.assert_allclose(jac["a"],[-np.sin(.2),0],atol=1e-12)
    np.testing.assert_allclose(jac["b"][0],[np.cos(.2)*np.cos(.4),-np.sin(.2)*np.sin(.4)],atol=1e-12)
    np.testing.assert_allclose(jac["b"][1][0],[0,0],atol=1e-12)


def test_nested_vector_cotangents_match_the_actual_return_tree_order():
    def fn(tape,x):
        tape.ry(x,0)
        return {"z":tape.expval(PauliZ(0)),"other":[tape.expval(PauliX(0)),(tape.expval(PauliZ(1)),)]}
    node = split_non_commuting(QNode(fn,2))
    cotangent = {"z":2.,"other":[3.,(4.,)]}
    value,vjp = node.execute_and_compute_vjp(cotangent,.3)
    assert value["z"] == pytest.approx(np.cos(.3),abs=1e-12)
    assert vjp == pytest.approx(-2*np.sin(.3)+3*np.cos(.3),abs=1e-12)
    with pytest.raises(ValueError,match="Cotangent"):
        node.compute_vjp({"other":[3.,(4.,)],"z":2.},.3)


def test_native_jvp_with_multiple_inputs_and_parameter_selection():
    def fn(tape,x,y):
        tape.ry(x+2*y,0)
        return (tape.expval(PauliZ(0)),tape.expval(PauliX(0)))
    node = split_non_commuting(QNode(fn,1))
    value,jvp = node.execute_and_compute_jvp((2.,3.),.2,.1,argnums=(0,1))
    np.testing.assert_allclose(value,[np.cos(.4),np.sin(.4)],atol=1e-12)
    np.testing.assert_allclose(jvp,[-8*np.sin(.4),8*np.cos(.4)],atol=1e-12)


def test_postprocessing_chain_rule_follows_reverse_stage_order_not_source_order():
    @transform
    def squared(tape): return (tape,),lambda results:results[0]**2
    @transform
    def shifted(tape): return (tape,),lambda results:results[0]+3
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(PauliZ(0))
    node = TransformProgram([squared,shifted])(QNode(fn,1))
    assert node(.4) == pytest.approx((np.cos(.4)+3)**2,abs=1e-12)
    assert node.gradient(.4) == pytest.approx(-2*(np.cos(.4)+3)*np.sin(.4),abs=1e-12)
    assert node.last_metadata["postprocessing_order"] == [1,0]


def test_multitape_child_jacobians_use_each_childs_own_angle_slice():
    @transform
    def doubled(tape):
        first,second = tape.copy(),tape.copy()
        second.circuit.ry(.3,0)
        return (first,second),lambda results:.2*results[0]+.8*results[1]
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(PauliZ(0))
    node = doubled(QNode(fn,1))
    assert node.gradient(.4) == pytest.approx(-.2*np.sin(.4)-.8*np.sin(.7),abs=1e-12)
    assert node.last_metadata["executed_tape_count"] == 2
    assert [row["gate_angle_slice"] for row in node.last_metadata["executions"]] == [(0,1),(1,2)]


def test_native_plan_jacobian_derivative_and_vjp_entrypoints_share_the_same_engine():
    plan = fixed_node()._construct((.3,),{})
    values = plan.recorder.native_values()
    energy,matrix,spec = plan.compute_jacobian(values)
    assert energy == pytest.approx(.9*np.sin(.3),abs=1e-12)
    np.testing.assert_allclose(matrix,[[.9*np.cos(.3)]],atol=1e-12)
    assert plan.compute_vjp(2.,values) == pytest.approx([1.8*np.cos(.3)],abs=1e-12)
    assert plan.execute_and_compute_derivatives(values)[2] == spec


def test_identity_zero_and_duplicate_terms_have_the_correct_gradient():
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(2.,PauliString([])),(0.,PauliX(1)),(1.,PauliZ(0)),(2.,PauliZ(0))]))
    node = split_non_commuting(QNode(fn,2))
    assert node.gradient(.4) == pytest.approx(-3*np.sin(.4),abs=1e-12)


def test_identity_only_and_custom_empty_batches_have_true_zero_quantum_work():
    @transform
    def constant(tape): return (),lambda results:2.
    fn = lambda tape,x:tape.expval(Hamiltonian([(2.,PauliString([]))]))
    for node in [split_non_commuting(QNode(fn,1)),constant(QNode(fn,1))]:
        assert node.gradient(.4) == 0.
        assert node.last_metadata["executed_tape_count"] == 0
        assert node.last_metadata["gradient_physical_shots"] == 0


def test_coefficient_only_native_gradient_is_not_silently_zero():
    def fn(tape,x):
        tape.ry(.4,0)
        return tape.expval(Hamiltonian([(x,PauliZ(0))]))
    node = split_non_commuting(QNode(fn,1))
    assert node.gradient(.3) == pytest.approx(np.cos(.4),abs=1e-12)
    assert node.last_metadata["processing_parameter_count"] == 1
    assert node.last_metadata["trainable_coefficient_slots"] == [0]
    assert node.last_metadata["trainable_gate_occurrences"] == []


def test_same_theta_in_angles_and_coefficients_includes_both_product_rule_terms():
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(x,PauliX(0)),(x*x,PauliZ(0))]))
    x = .3
    expected = np.sin(x)+x*np.cos(x)+2*x*np.cos(x)-x*x*np.sin(x)
    native = split_non_commuting(QNode(fn,1))
    assert native.gradient(x) == pytest.approx(expected,abs=1e-12)
    # The same unified preprocessing also handles ordinary live coefficients.
    assert QNode(fn,1).gradient(x) == pytest.approx(expected,abs=1e-12)


def test_trainable_identity_offset_and_zero_valued_coefficient_keep_their_graphs():
    def identity(tape,x): return tape.expval(Hamiltonian([(x*x,PauliString([]))]))
    node = split_non_commuting(QNode(identity,1))
    assert node.gradient(.3) == pytest.approx(.6,abs=1e-12)
    assert node.last_metadata["executed_tape_count"] == 0
    def zero(tape,x):
        tape.h(0)
        return tape.expval(Hamiltonian([(x,PauliX(0))]))
    assert split_non_commuting(QNode(zero,1)).gradient(0.) == pytest.approx(1.,abs=1e-12)


def test_trainable_single_terms_and_internal_split_prototype_fixed_gradients():
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(x,PauliX(0)),(x*x,PauliString([]))]))
    node = split_to_single_terms(QNode(fn,1))
    assert node.gradient(.3) == pytest.approx(np.sin(.3)+.3*np.cos(.3)+.6,abs=1e-12)
    original = QNode(lambda tape,x:(tape.ry(x,0),tape.expval(Hamiltonian([(2.,PauliZ(0)),(.3,PauliX(0))])))[1],1)
    assert split_hamiltonian(original).gradient(.3) == pytest.approx(original.gradient(.3),abs=1e-12)


def test_analytic_grouped_variance_has_the_nonlinear_mean_chain_rule():
    def fn(tape,x):
        tape.ry(x,0)
        return {"var":tape.var(PauliZ(0)),"mean":tape.expval(PauliZ(0))}
    jac = split_non_commuting(QNode(fn,1)).jacobian(.4)
    assert jac == {"var":pytest.approx(2*np.sin(.4)*np.cos(.4),abs=1e-12),"mean":pytest.approx(-np.sin(.4),abs=1e-12)}


def test_probability_output_gradients_are_numeric_leaves_not_passive_metadata():
    def fn(tape,x):
        tape.ry(x,0)
        return tape.probs([0])
    jac = merge_rotations(QNode(fn,1)).jacobian(.4)
    assert jac == {"0":pytest.approx(-np.sin(.4)/2,abs=1e-12),"1":pytest.approx(np.sin(.4)/2,abs=1e-12)}


def test_shared_keyword_argument_and_unselected_constants_have_correct_derivatives():
    def fn(tape,*,theta,scale=2.):
        tape.ry(np.sin(theta)+scale*theta,0)
        return tape.expval(PauliZ(0))
    node = split_non_commuting(QNode(fn,1))
    expected = -np.sin(np.sin(.3)+2*.3)*(np.cos(.3)+2)
    assert node.gradient(theta=.3) == pytest.approx(expected,abs=1e-12)


def test_controlled_rotation_uses_its_four_shift_generator_recipe():
    def fn(tape,x):
        tape.h(0)
        tape.crx(x,0,1)
        return tape.expval(PauliZ(1))
    node = split_non_commuting(QNode(fn,2,diff_method="parameter-shift"))
    assert node.gradient(.4) == pytest.approx(-.5*np.sin(.4),abs=1e-12)
    assert node.last_metadata["shifted_evaluation_count"] == 4


def test_casting_postprocessor_rejects_native_tracing_instead_of_faking_zero():
    @transform
    def detached(tape): return (tape,),lambda results:float(results[0])
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(PauliZ(0))
    with pytest.raises(TransformError,match="derivative"):
        detached(QNode(fn,1)).gradient(.3)


def test_coefficient_rebinding_requires_a_fresh_plan_for_grouping_and_receipts():
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(x,PauliZ(0))]))
    torch = pytest.importorskip("torch")
    node = split_non_commuting(QNode(fn,1))
    plan = node._construct((torch.tensor(.3,dtype=torch.float64,requires_grad=True),),{})
    values = np.array([.3,.3])
    plan.evaluate(values)
    values[-1] = .4
    with pytest.raises(UnsupportedFeature,match="fresh"): plan.evaluate(values)


def test_postselection_and_discrete_sample_gradients_remain_explicitly_unsupported():
    def fn(tape,x):
        tape.ry(x,0)
        tape.circuit.operations[0].metadata["postselect"] = 1
        return tape.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature,match="postselected"):
        split_non_commuting(QNode(fn,1)).gradient(.3)
    sampled = merge_rotations(QNode(lambda tape,x:(tape.ry(x,0),tape.sample())[1],1,shots=11))
    with pytest.raises(UnsupportedFeature): sampled.gradient(.3)


def test_reused_parameterized_loop_derivative_rejects_before_child_execution():
    def fn(tape,x):
        body = Tape(1,tape.parameter_transform)
        body.ry(x,0)
        tape.circuit = tape.circuit.for_loop(range(3),body.circuit)
        return tape.expval(PauliZ(0))
    node = split_non_commuting(QNode(fn,1,diff_method="parameter-shift"))
    assert node(.3) == pytest.approx(np.cos(.9),abs=1e-12)
    with pytest.raises(UnsupportedFeature,match="loop-aware"):
        node.gradient(.3)


def test_copy_coefficient_scan_is_cycle_safe_without_claiming_cyclic_execution():
    tape = Tape(1)
    tree = {}
    tree["self"] = tree
    tape.output_tree = tree
    copied = tape.copy()
    assert copied.output_tree["self"] is copied.output_tree


def test_unsupported_methods_do_not_fall_back_to_finite_difference():
    for method in ["backprop","spsa","unknown"]:
        with pytest.raises(UnsupportedFeature): fixed_node(diff_method=method).gradient(.3)


def test_native_forward_before_backward_receipt_counts_only_real_executions():
    node = fixed_node()
    plan = node._construct((.3,),{})
    values = plan.recorder.native_values()
    plan.evaluate(values)
    plan.jacobian(values)
    assert plan.metadata["preceding_forward_evaluation_count"] == 1
    assert plan.metadata["preceding_forward_executions"][0]["tape_index"] == 0


def test_torch_gradcheck_checks_the_native_adjoint_not_a_finite_diff_implementation():
    torch = pytest.importorskip("torch")
    node = fixed_node(diff_method="adjoint")
    x = torch.tensor(.3,dtype=torch.float64,requires_grad=True)
    assert torch.autograd.gradcheck(node,(x,),eps=1e-6,atol=1e-5,rtol=1e-3)
    assert node.last_metadata["gradient_method"] == "adjoint"


def test_torch_autograd_grad_with_nonlinear_shared_angles_and_coefficients():
    torch = pytest.importorskip("torch")
    def fn(tape,x):
        tape.ry(torch.sin(x)+2*x,0)
        return tape.expval(Hamiltonian([(x*x,PauliZ(0))]))
    x = torch.tensor(.3,dtype=torch.float64,requires_grad=True)
    node = split_non_commuting(merge_rotations(QNode(fn,1)))
    gradient, = torch.autograd.grad(node(x),x)
    angle = np.sin(.3)+.6
    assert gradient.item() == pytest.approx(.6*np.cos(angle)-.09*np.sin(angle)*(np.cos(.3)+2),abs=1e-12)


def test_torch_nested_vector_cotangent_order_and_multiple_inputs():
    torch = pytest.importorskip("torch")
    def fn(tape,x,y):
        tape.ry(x+2*y,0)
        return {"first":tape.expval(PauliZ(0)),"rest":[tape.expval(PauliX(0))]}
    node = split_non_commuting(QNode(fn,1))
    x,y = [torch.tensor(v,dtype=torch.float64,requires_grad=True) for v in [.2,.1]]
    output = node(x,y)
    gx,gy = torch.autograd.grad(2*output["first"]+3*output["rest"][0],(x,y))
    expected = -2*np.sin(.4)+3*np.cos(.4)
    np.testing.assert_allclose([gx.item(),gy.item()],[expected,2*expected],atol=1e-12)


def test_torch_real_optimizer_step_lowers_the_transformed_energy():
    torch = pytest.importorskip("torch")
    node = fixed_node()
    x = torch.tensor(.37,dtype=torch.float64,requires_grad=True)
    optimizer = torch.optim.SGD([x],lr=.15)
    first = node(x).item()
    for _ in range(4):
        optimizer.zero_grad()
        node(x).backward()
        optimizer.step()
    assert node(x).item() < first-.1


def test_autograd_shared_parameter_coefficients_and_keyword_inputs():
    autograd = pytest.importorskip("autograd")
    import autograd.numpy as anp
    def fn(tape,*,theta):
        tape.ry(anp.sin(theta)+2*theta,0)
        return tape.expval(Hamiltonian([(theta*theta,PauliZ(0))]))
    node = split_non_commuting(QNode(fn,1,interface="autograd"))
    expected = .6*np.cos(np.sin(.3)+.6)-.09*np.sin(np.sin(.3)+.6)*(np.cos(.3)+2)
    assert autograd.grad(lambda x:node(theta=x))(.3) == pytest.approx(expected,abs=1e-12)


def test_autograd_vector_input_and_multiple_measurement_cost():
    autograd = pytest.importorskip("autograd")
    import autograd.numpy as anp
    def fn(tape,x):
        tape.ry(x[0]+2*x[1],0)
        return (tape.expval(PauliZ(0)),tape.expval(PauliX(0)))
    node = split_non_commuting(QNode(fn,1,interface="autograd"))
    def cost(x):
        z,local = node(x)
        return 2*z+3*local
    gradient = autograd.grad(cost)(anp.array([.2,.1]))
    expected = -2*np.sin(.4)+3*np.cos(.4)
    np.testing.assert_allclose(gradient,[expected,2*expected],atol=1e-12)


def test_torch_higher_order_requests_are_rejected_instead_of_detached():
    torch = pytest.importorskip("torch")
    x = torch.tensor(.3,dtype=torch.float64,requires_grad=True)
    with pytest.raises(UnsupportedFeature,match="higher-order"):
        torch.autograd.grad(fixed_node()(x),x,create_graph=True)


def test_torch_scalar_graphs_survive_tape_copy_and_hamiltonian_scaling():
    torch = pytest.importorskip("torch")
    def fn(tape,x):
        tape.h(0)
        return tape.expval(Hamiltonian([(x*x,PauliX(0))])*x)
    x = torch.tensor(.3,dtype=torch.float64,requires_grad=True)
    output = split_non_commuting(QNode(fn,1))(x)
    output.backward()
    assert output.item() == pytest.approx(.3**3,abs=1e-12)
    assert x.grad.item() == pytest.approx(3*.3**2,abs=1e-12)


def test_sampled_shift_receipts_have_independent_streams_and_exact_physical_counts():
    spy = SampleSpy()
    node = fixed_node(device=spy,shots=101,seed=5,diff_method="parameter-shift")
    assert abs(node.gradient(.37)-.9*np.cos(.37)) < .25
    runs = gradient_runs(node.last_metadata)
    shifts = [run for run in runs if run["kind"] == "shift"]
    assert len(shifts) == 2 and len({run["root_seed"] for run in shifts}) == 2
    assert sum(call["shots"] for call in spy.samples) == node.last_metadata["gradient_physical_shots"] == 404
    assert len({row["execution_id"] for row in joint_receipts(node.last_metadata)}) == len(spy.samples) == 4
    assert node.last_metadata["gradient_semantics"] == "finite-shot estimate"


@pytest.mark.parametrize("policy",[None,"uniform","weighted"])
def test_sampled_multigroup_allocation_conserves_real_work_for_every_shift(policy):
    def fn(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(1.,PauliX(0)),(.3,PauliZ(0))]))
    spy = SampleSpy()
    node = split_non_commuting(QNode(fn,1,device=spy,shots=301,seed=6,diff_method="parameter-shift"),shot_dist=policy)
    node.gradient(.37)
    expected = 2408 if policy is None else 1204
    assert sum(call["shots"] for call in spy.samples) == node.last_metadata["gradient_physical_shots"] == expected
    shifted = [row for row in gradient_runs(node.last_metadata) if row["kind"] == "shift"]
    assert len(shifted) == node.last_metadata["shifted_evaluation_count"] == 4
    assert len({row["partitions"][0]["seed"] for row in shifted}) == 4


def test_shot_vector_partitions_have_distinct_derivatives_and_independent_copy_streams():
    spy = SampleSpy()
    node = fixed_node(device=spy,shots=[100,(200,2)],seed=17,diff_method="parameter-shift")
    gradient = node.jacobian(.37)
    assert len(gradient) == 3
    assert max(abs(value-.9*np.cos(.37)) for value in gradient) < .3
    assert sum(row["shots"] for row in spy.samples) == node.last_metadata["gradient_physical_shots"] == 2000
    shifted = [part for row in gradient_runs(node.last_metadata) if row["kind"] == "shift" for part in row["partitions"]]
    assert len(shifted) == len({row["seed"] for row in shifted}) == 6
    assert [row["shots"] for row in shifted] == [100,200,200]*2


def test_torch_sampled_backward_counts_forward_plus_all_real_derivative_work():
    torch = pytest.importorskip("torch")
    spy = SampleSpy()
    node = fixed_node(device=spy,shots=201,seed=21,diff_method="parameter-shift")
    x = torch.tensor(.37,dtype=torch.float64,requires_grad=True)
    node(x).backward()
    assert abs(x.grad.item()-.9*np.cos(.37)) < .25
    assert sum(row["shots"] for row in spy.samples) == node.last_metadata["total_physical_shots"] == 1005
    assert node.last_metadata["preceding_forward_physical_shots"] == 201


def test_seeded_gradient_estimates_replay_values_but_generate_new_execution_receipts():
    node = fixed_node(shots=131,seed=11,diff_method="parameter-shift")
    first = node.gradient(.37)
    ids = {row["execution_id"] for row in joint_receipts(node.last_metadata)}
    assert node.gradient(.37) == first
    assert ids.isdisjoint(row["execution_id"] for row in joint_receipts(node.last_metadata))


def test_sampled_group_variance_derivatives_reject_before_sampling():
    spy = SampleSpy()
    def fn(tape,x):
        tape.ry(x,0)
        return tape.var(PauliZ(0))
    for function in [split_non_commuting,split_to_single_terms,merge_rotations]:
        node = function(QNode(fn,1,device=spy,shots=101,seed=3))
        with pytest.raises(UnsupportedFeature,match="variance"): node.gradient(.3)
    assert spy.samples == []


def test_fixed_local_seed_cannot_silently_reuse_samples_across_shifts():
    from dataclasses import replace
    def fn(tape,x):
        tape.ry(x,0)
        request = replace(tape.expval(PauliZ(0)),shots=17,seed=8)
        tape.measurements[-1] = request
        return request
    with pytest.raises(UnsupportedFeature,match="independent"):
        split_to_single_terms(QNode(fn,1)).gradient(.3)


def test_gradient_shot_and_retained_sample_budgets_preflight_before_any_sampling():
    for limits in [TransformLimits(max_total_shots=300),TransformLimits(max_sample_values=500)]:
        spy = SampleSpy()
        node = fixed_node(device=spy,shots=101,seed=3)
        node.transform_program = TransformProgram([split_non_commuting],limits=limits)
        with pytest.raises(MemoryError): node.gradient(.3)
        assert spy.samples == []


def test_sampled_uncertainty_metadata_is_not_a_differentiable_result_leaf():
    node = fixed_node(shots=101,seed=3,diff_method="parameter-shift")
    value,gradient = node.execute_and_compute_derivatives(.37)
    assert np.isscalar(value) and np.isscalar(gradient)
    assert "postprocessing_chain_rule" in node.last_metadata
    assert node.last_metadata["gradient_semantics"] == "finite-shot estimate"
    assert joint_receipts(node.last_metadata)[0]["sample_covariance"] is not None


def test_noise_channel_group_gradient_uses_native_shift_not_noisy_adjoint():
    from quantumbridge.devices import DensityMatrixDevice
    def fn(tape,x):
        tape.ry(x,0)
        tape.amplitude_damping(.2,0)
        return tape.expval(PauliZ(0))
    node = split_non_commuting(QNode(fn,1,device=DensityMatrixDevice(),diff_method="parameter-shift"))
    assert node.gradient(.3) == pytest.approx(-.8*np.sin(.3),abs=1e-12)
    with pytest.raises(UnsupportedFeature,match="Adjoint"): node.gradient(.3,method="adjoint")


def test_zero_weight_trainable_group_does_not_lose_its_coefficient_derivative():
    def fn(tape,x):
        tape.h(0)
        return tape.expval(Hamiltonian([(x,PauliX(0))]))
    node = split_non_commuting(QNode(fn,1),shot_dist="weighted")
    with pytest.raises(TransformError,match="coefficient derivatives"):
        node.gradient(0.)


def test_hundred_qubit_mps_template_transform_gradient_is_really_non_dense(monkeypatch):
    from quantumbridge.devices import MatrixProductStateDevice,DensityMatrixDevice
    from quantumbridge.information.matrix_product_state import MatrixProductState
    def forbidden(*args,**kwargs): raise AssertionError("Dense expansion forbidden")
    monkeypatch.setattr(StatevectorDevice,"statevector",forbidden)
    monkeypatch.setattr(DensityMatrixDevice,"density_matrix",forbidden)
    monkeypatch.setattr(MatrixProductState,"statevector",forbidden)
    monkeypatch.setattr(MatrixProductState,"reduced_density_matrix",forbidden)
    def fn(tape,x):
        tape.h(0)
        for wire in range(99): tape.cx(wire,wire+1)
        templates.AngleEmbedding([x],[99],rotation="Y").apply(tape)
        return tape.expval(Hamiltonian([(1.,PauliZ(0).tensor(PauliZ(99))),(.2,PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2,max_bond_dim=4,cutoff=0)
    node = TransformProgram([merge_rotations,split_non_commuting])(QNode(fn,100,device=device,diff_method="parameter-shift"))
    assert node(.3) == pytest.approx(np.cos(.3),abs=1e-11)
    assert node.gradient(.3) == pytest.approx(-np.sin(.3),abs=1e-10)
    assert node.last_metadata["transform_count"] == 2
    assert node.last_metadata["shifted_evaluation_count"] == 2
    assert node.last_metadata["total_physical_shots"] == 0
    resources = node.last_metadata["executions"][0]["partitions"][0]["resources"]
    assert resources["available"] and resources["max_bond_observed"] == 2
    assert resources["max_tensor_bytes"] == 12672
    assert resources["max_discarded_weight"] == 0


def test_geometry_h2_transform_gradient_and_optimizer_reuse_the_real_hamiltonian(monkeypatch):
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr"))
    def forbidden(*args,**kwargs): raise AssertionError("Fixed geometry integrals must not be recomputed per child or angle")
    monkeypatch.setattr(qchem,"molecular_hamiltonian_native",forbidden)
    def fn(tape,x):
        tape.x(0)
        tape.x(1)
        qchem.apply_fermionic_excitation(tape,x,[0,1,2,3])
        return tape.expval(problem.hamiltonian)
    original = QNode(fn,4)
    node = TransformProgram([cancel_inverses,decompose(gate_set={"RX","RZ","CNOT"}),split_non_commuting])(original)
    x = .3
    for method in ["adjoint","parameter-shift"]:
        assert node.gradient(x,method=method) == pytest.approx(original.gradient(x,method=method),abs=2e-11)
    first = node(x)
    for _ in range(5): x -= .3*node.gradient(x)
    assert node(x) < first-.01
    assert node(x) == pytest.approx(original(x),abs=2e-11)
