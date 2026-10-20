# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge import StatevectorDevice
from quantumbridge.qml.tape import Tape
from quantumbridge.transforms import execute_transform
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliY, PauliZ
from quantumbridge.utils.math import PauliString
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml import QNode
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.transforms import (split_non_commuting, TransformProgram, TransformLimits,
                                     TransformError, merge_rotations, compile, decompose)


def receipts(metadata):
    return [receipt for execution in metadata["executions"] for partition in execution["partitions"]
            for receipt in partition.get("joint_measurements", ())]


def stats(metadata):
    return metadata["stages"][0]["postprocessing_metadata"][0]


def source(words=None, coefficients=None, *, shots=None, seed=12, width=2):
    words = [PauliX(0), PauliZ(0)] if words is None else words
    coefficients = [1.] * len(words) if coefficients is None else coefficients
    tape = Tape(width, shots=shots, seed=seed)
    tape.ry(.61, 0)
    tape.expval(Hamiltonian(zip(coefficients, words)))
    return tape


class SampleCounter(StatevectorDevice):
    def __init__(self):
        super().__init__()
        self.calls = []

    def sample(self, circuit, wires=None, shots=1, seed=None, parameters=None):
        memory = super().sample(circuit, wires, shots, seed, parameters)
        self.calls.append((tuple(wires), shots, seed, tuple(memory)))
        return memory


def test_generally_commuting_xx_yy_are_not_qubitwise_commuting():
    from quantumbridge.transforms import split_non_commuting
    xx, yy = PauliX(0).tensor(PauliX(1)), PauliY(0).tensor(PauliY(1))
    np.testing.assert_allclose(xx.matrix() @ yy.matrix(), yy.matrix() @ xx.matrix(), atol=1e-12)
    tape = Tape(2)
    tape.expval(Hamiltonian([(1., xx), (1., yy)]))
    children, _ = split_non_commuting(tape, grouping_strategy="qwc")
    assert len(children) == 2
    assert [child.measurements[0].observable.basis for child in children] == [((0,"X"),(1,"X")), ((0,"Y"),(1,"Y"))]


def test_same_qwc_group_uses_one_actual_joint_sample_buffer():
    from quantumbridge.transforms import split_non_commuting
    device = SampleCounter()
    tape = Tape(2, shots=129, seed=14)
    tape.ry(np.pi/3, 0)
    tape.expval(PauliX(0))
    tape.expval(PauliX(0).tensor(PauliZ(1)))
    value, metadata = execute_transform(tape, split_non_commuting, device, return_metadata=True)
    assert len(device.calls) == 1 and device.calls[0][1] == 129
    receipt = metadata["executions"][0]["partitions"][0]["joint_measurements"][0]
    eigenvalues = np.asarray(receipt["eigenvalues"])
    np.testing.assert_array_equal(eigenvalues[:,0], eigenvalues[:,1])
    assert tuple(receipt["bitstrings"]) == device.calls[0][3]
    assert len(receipt["bitstrings"]) == 129
    assert receipt["basis"] == ((0,"X"),(1,"Z"))
    assert value[0] == value[1] == np.mean(eigenvalues[:,0])


def test_identity_factors_have_no_basis_but_validate_declared_wires():
    tape = source([PauliString([(0,"I"),(1,"X")]), PauliX(1)])
    children, _ = split_non_commuting(tape)
    assert len(children) == 1
    assert children[0].observable.words == (((1,"X"),),)
    assert execute_transform(tape, split_non_commuting) == 0.
    invalid = source([PauliString([(3,"I")])])
    with pytest.raises(ValueError, match="in-register"): split_non_commuting(invalid)


def test_deduplicated_terms_restore_all_source_positions_coefficients_and_nested_tree():
    tape = Tape(2)
    tape.ry(.3, 0)
    energy = tape.expval(Hamiltonian([(1.,PauliZ(0)),(2.,PauliZ(0)),(4.,PauliString([])),(.5,PauliX(1))]))
    z, same = tape.expval(PauliZ(0)), tape.expval(PauliZ(0))
    tape.set_output({"energy": energy, "local": [z, (same,)]})
    children, _ = split_non_commuting(tape)
    assert len(children) == 1 and len(children[0].observable.words) == 2
    value = execute_transform(tape, split_non_commuting)
    assert value == {"energy":pytest.approx(3*np.cos(.3)+4), "local":[pytest.approx(np.cos(.3)),(pytest.approx(np.cos(.3)),)]}


def test_common_basis_is_pairwise_qwc_for_deterministic_greedy_groups():
    words = [PauliX(0),PauliY(1),PauliX(0).tensor(PauliZ(1)),PauliZ(0),PauliY(0).tensor(PauliY(1))]
    tape = source(words)
    first, _ = split_non_commuting(tape)
    second, _ = split_non_commuting(tape)
    assert [child.observable for child in first] == [child.observable for child in second]
    assert len(first) == 4
    for child in first:
        basis = dict(child.observable.basis)
        for word in child.observable.words:
            assert all(basis[wire] == label for wire,label in word)


def test_no_grouping_still_deduplicates_repeated_identical_paulis():
    tape = source([PauliX(0),PauliX(0),PauliX(1)])
    children, _ = split_non_commuting(tape,grouping_strategy=None)
    assert len(children) == 2 and all(len(child.observable.words) == 1 for child in children)


def test_wires_strategy_separates_overlapping_source_measurements():
    tape = Tape(2)
    tape.expval(PauliX(0))
    tape.expval(PauliX(0).tensor(PauliZ(1)))
    assert len(split_non_commuting(tape,grouping_strategy="wires")[0]) == 2
    assert len(split_non_commuting(tape,grouping_strategy="qwc")[0]) == 1


def test_single_hamiltonian_wires_still_requires_disjoint_supports():
    tape = source([PauliX(0), PauliX(0).tensor(PauliZ(1))])
    assert len(split_non_commuting(tape,grouping_strategy="wires")[0]) == 2


def test_default_matches_explicit_qwc_for_all_native_pauli_measurements():
    tape = source([PauliX(0),PauliZ(0),PauliX(1)])
    assert [child.observable for child in split_non_commuting(tape)[0]] == [child.observable for child in split_non_commuting(tape,"qwc")[0]]


def test_none_shot_distribution_executes_full_budget_for_every_group():
    device = SampleCounter()
    tape = source(shots=33)
    _, metadata = execute_transform(tape,split_non_commuting,device,return_metadata=True)
    assert [call[1] for call in device.calls] == [33,33]
    assert stats(metadata)["partitions"][0]["total_physical_shots"] == 66
    assert metadata["stages"][0]["sampled_shots"] == 66


def test_uniform_total_budget_rounding_is_exact_and_deterministic():
    tape = source([PauliX(0),PauliZ(0),PauliY(0)],shots=101)
    children,_ = split_non_commuting(tape,shot_dist="uniform")
    assert [ShotSpec.parse(child.shots).partitions for child in children] == [(34,),(34,),(33,)]
    device = SampleCounter()
    _, metadata = execute_transform(tape,split_non_commuting(shot_dist="uniform"),device,return_metadata=True)
    assert sum(call[1] for call in device.calls) == 101
    assert stats(metadata)["partitions"][0]["total_physical_shots"] == 101


def test_weighted_uses_coefficient_l1_and_ordered_remainder_not_fraction_sorting():
    tape = source([PauliX(0),PauliZ(0),PauliY(0)],[-1.,3.,1.],shots=29)
    children,_ = split_non_commuting(tape,shot_dist="weighted")
    assert [child.shots.partitions for child in children] == [(6,),(18,),(5,)]


def test_weighted_group_uses_sum_over_terms_and_source_outputs():
    tape = source([PauliX(0),PauliX(1),PauliZ(0)],[-2.,3.,5.],shots=101)
    tape.expval(PauliZ(0))
    children,_ = split_non_commuting(tape,shot_dist="weighted")
    assert [child.observable.allocation.weights for child in children] == [(5.,6.),(5.,6.)]
    assert [child.shots.partitions for child in children] == [(46,),(55,)]


def test_weighted_zero_contributions_are_elided_without_losing_constant_or_nonzero_terms():
    tape = source([PauliX(0),PauliZ(0),PauliString([])],[0.,2.,3.],shots=10)
    children,_ = split_non_commuting(tape,shot_dist="weighted")
    assert len(children) == 1 and children[0].observable.words == (((0,"Z"),),)
    value,metadata = execute_transform(tape,split_non_commuting(shot_dist="weighted"),return_metadata=True)
    assert value == 3 + 2*receipts(metadata)[0]["means"][0]
    zero = source([PauliX(0),PauliZ(0)],[0.,0.],shots=1)
    device = SampleCounter()
    assert execute_transform(zero,split_non_commuting(shot_dist="weighted"),device) == 0.
    assert device.calls == []


def test_zero_coefficient_nonidentity_terms_remain_without_weighted_allocation():
    tape = source([PauliX(0),PauliZ(0)],[0.,1.],shots=10)
    assert len(split_non_commuting(tape)[0]) == 2
    assert len(split_non_commuting(tape,shot_dist="uniform")[0]) == 2


def test_identity_only_needs_no_device_samples_and_restores_vector_copies():
    tape = source([PauliString([(0,"I")])],[2.],shots=[100,(200,2)])
    device = SampleCounter()
    children,_ = split_non_commuting(tape,shot_dist="uniform")
    assert children == ()
    value, metadata = execute_transform(tape,split_non_commuting(shot_dist="uniform"),device,return_metadata=True)
    assert value == (2.,2.,2.) and device.calls == [] and metadata["executed_tape_count"] == 0
    assert [part["total_physical_shots"] for part in stats(metadata)["partitions"]] == [0,0,0]


@pytest.mark.parametrize("policy",["uniform","weighted"])
def test_insufficient_nonzero_group_shots_reject_before_any_execution(policy):
    tape = source([PauliX(0),PauliZ(0),PauliY(0)],[1.,10.,1.],shots=3 if policy == "weighted" else 2)
    device = SampleCounter()
    with pytest.raises(TransformError,match="insufficient"):
        execute_transform(tape,split_non_commuting(shot_dist=policy),device)
    assert device.calls == []


def test_shot_vector_conserves_each_partition_and_copy_independently():
    tape, device = source([PauliX(0),PauliZ(0),PauliY(0)],[1.,3.,1.],shots=[100,(200,2)]), SampleCounter()
    value,metadata = execute_transform(tape,split_non_commuting(shot_dist="weighted"),device,return_metadata=True)
    assert len(value) == 3
    assert [call[1] for call in device.calls] == [20,40,40,60,120,120,20,40,40]
    assert [part["total_physical_shots"] for part in stats(metadata)["partitions"]] == [100,200,200]
    assert sum(call[1] for call in device.calls) == 500
    assert len({call[2] for call in device.calls}) == 9
    assert len({item["execution_id"] for item in receipts(metadata)}) == 9


def test_seed_reproducibility_replays_values_but_not_execution_identity():
    tape,device = source(shots=[31,(47,2)]), SampleCounter()
    first,metadata1 = execute_transform(tape,split_non_commuting,device,return_metadata=True)
    previous = list(device.calls)
    second,metadata2 = execute_transform(tape,split_non_commuting,device,return_metadata=True)
    assert first == second and previous == device.calls[len(previous):]
    assert set(item["execution_id"] for item in receipts(metadata1)).isdisjoint(item["execution_id"] for item in receipts(metadata2))
    memories = [call[3] for call in previous]
    assert memories[1] != memories[2]


def test_deterministic_allocation_seed_is_not_the_measurement_seed():
    tape = source(shots=101)
    left,_ = split_non_commuting(tape,shot_dist="uniform",seed=1)
    right,_ = split_non_commuting(tape,shot_dist="uniform",seed=np.random.default_rng(8))
    assert [child.shots for child in left] == [child.shots for child in right]
    assert [child.seed for child in left] == [tape.seed]*2


def test_shared_samples_retain_positive_covariance_and_correct_energy_standard_error():
    tape,device = Tape(2,shots=501,seed=8), SampleCounter()
    tape.ry(np.pi/3,0)
    tape.expval(Hamiltonian([(2.,PauliX(0)),(3.,PauliX(0).tensor(PauliZ(1)))]))
    value,metadata = execute_transform(tape,split_non_commuting,device,return_metadata=True)
    data = receipts(metadata)[0]
    samples = np.asarray(data["eigenvalues"])
    energy_samples = samples @ np.array([2.,3.])
    measured = stats(metadata)["partitions"][0]["source_measurements"][0]
    assert value == pytest.approx(np.mean(energy_samples),abs=1e-12)
    assert data["source_expectation_contributions"] == pytest.approx([value],abs=1e-12)
    assert measured["variance"] == pytest.approx(np.var(energy_samples),abs=1e-12)
    assert measured["standard_error"] == pytest.approx(np.std(energy_samples,ddof=1)/np.sqrt(501),abs=1e-12)
    assert data["source_group_variances"] == pytest.approx([measured["variance"]],abs=1e-12)
    assert data["source_group_standard_errors"] == pytest.approx([measured["standard_error"]],abs=1e-12)
    covariance = np.asarray(data["covariance"])
    assert covariance[0,1] > .1
    assert measured["variance"] > 1.5 * (4*covariance[0,0]+9*covariance[1,1])


def test_anticorrelated_shared_terms_cancel_energy_and_uncertainty_exactly():
    tape = Tape(2,shots=113,seed=3)
    tape.ry(np.pi/3,0)
    tape.x(1)
    tape.expval(Hamiltonian([(1.,PauliX(0)),(1.,PauliX(0).tensor(PauliZ(1)))]))
    value,metadata = execute_transform(tape,split_non_commuting,return_metadata=True)
    data = receipts(metadata)[0]
    samples = np.asarray(data["eigenvalues"])
    np.testing.assert_array_equal(samples[:,0],-samples[:,1])
    measured = stats(metadata)["partitions"][0]["source_measurements"][0]
    assert value == 0. and measured["variance"] == 0. and measured["standard_error"] == 0.


def test_independent_groups_add_estimator_variance_not_quantum_cross_covariance():
    tape = source(coefficients=[2.,3.],shots=173)
    _,metadata = execute_transform(tape,split_non_commuting,return_metadata=True)
    measured = stats(metadata)["partitions"][0]["source_measurements"][0]
    expected = sum(coefficient**2*row["sample_covariance"][0][0]/row["shots"] for coefficient,row in zip([2.,3.],receipts(metadata)))
    assert measured["standard_error"]**2 == pytest.approx(expected,abs=1e-12)
    assert "not the full quantum variance" in measured["variance_semantics"]


def test_single_shot_uncertainty_is_unknown_not_falsely_zero():
    tape = source([PauliX(0)],shots=1)
    _,metadata = execute_transform(tape,split_non_commuting,return_metadata=True)
    assert stats(metadata)["partitions"][0]["source_measurements"][0]["standard_error"] is None
    assert receipts(metadata)[0]["sample_covariance"] is None


def test_analytic_covariance_is_exact_and_has_no_fabricated_samples():
    tape = Tape(2)
    tape.ry(np.pi/3,0)
    tape.expval(Hamiltonian([(2.,PauliX(0)),(3.,PauliX(0).tensor(PauliZ(1)))]))
    device = SampleCounter()
    value,metadata = execute_transform(tape,split_non_commuting,device,return_metadata=True)
    measured = stats(metadata)["partitions"][0]["source_measurements"][0]
    assert value == pytest.approx(5*np.sin(np.pi/3),abs=1e-12)
    assert measured["variance"] == pytest.approx(25*.25,abs=1e-12)
    assert measured["standard_error"] == 0.
    assert receipts(metadata)[0]["bitstrings"] is None and device.calls == []
    assert receipts(metadata)[0]["joint_sample_calls"] == 0


def test_y_basis_sign_and_nonmonotonic_source_wire_order():
    tape = Tape(3,shots=41,seed=4)
    tape.circuit.h(2).s(2)
    tape.x(0)
    tape.expval(PauliString([(2,"Y"),(0,"Z")]))
    tape.expval(PauliY(2))
    value,metadata = execute_transform(tape,split_non_commuting,return_metadata=True)
    assert value == (-1.,1.)
    assert receipts(metadata)[0]["basis"] == ((0,"Z"),(2,"Y"))
    assert set(receipts(metadata)[0]["bitstrings"]) == {"10"}


def test_variance_and_expval_of_one_pauli_share_the_same_measurement():
    tape = Tape(1,shots=97,seed=44)
    tape.ry(.8,0)
    tape.var(PauliZ(0))
    tape.expval(PauliZ(0))
    device = SampleCounter()
    value = execute_transform(tape,split_non_commuting,device)
    assert len(device.calls) == 1
    assert value[0] == pytest.approx(1-value[1]**2,abs=1e-12)
    identity = Tape(1)
    identity.var(PauliString([]))
    assert execute_transform(identity,split_non_commuting) == 0.


def test_dynamic_circuit_resets_preserve_true_joint_sample_correlations():
    tape = Tape(2,shots=37,seed=7)
    tape.h(0)
    bit = tape.measure(0)
    tape.cond(bit,lambda branch:branch.x(0))
    tape.x(1)
    tape.expval(PauliZ(0))
    tape.expval(PauliZ(0).tensor(PauliZ(1)))
    assert execute_transform(tape,split_non_commuting) == (1.,-1.)


def test_density_device_noise_still_uses_one_group_memory():
    from quantumbridge.devices import DensityMatrixDevice
    tape = Tape(2,shots=301,seed=6)
    tape.x(0)
    tape.amplitude_damping(.3,0)
    tape.expval(PauliZ(0))
    tape.expval(PauliZ(0).tensor(PauliZ(1)))
    value,metadata = execute_transform(tape,split_non_commuting,DensityMatrixDevice(),return_metadata=True)
    assert value[0] == value[1]
    assert receipts(metadata)[0]["joint_sample_calls"] == 1


def test_mps_joint_samples_do_not_execute_an_extra_resource_only_shot_job():
    from quantumbridge.devices import MatrixProductStateDevice
    class NoExtraRun(MatrixProductStateDevice):
        def run_shots(self,*args,**kwargs):
            raise AssertionError("Extra resource-only shot execution is not physical sampling reuse.")
    tape = Tape(30,shots=7,seed=5)
    tape.h(0)
    tape.expval(PauliX(0))
    tape.expval(PauliX(0).tensor(PauliZ(29)))
    value,metadata = execute_transform(tape,split_non_commuting,NoExtraRun(),return_metadata=True)
    assert value == (1.,1.)
    assert not metadata["executions"][0]["partitions"][0]["resources"]["available"]


def test_qnode_rebinding_after_compile_and_grouping_changes_actual_sampled_state():
    device = SampleCounter()
    def program(tape,theta):
        tape.ry(theta,0)
        tape.ry(2*theta,0)
        return {"energy":tape.expval(Hamiltonian([(1.,PauliX(0)),(.3,PauliZ(0))]))}
    node = TransformProgram([merge_rotations,compile(basis_set={"RY","RZ","CX"}),split_non_commuting(shot_dist="uniform")])(QNode(program,2,device=device,shots=101,seed=4))
    first,second = node(.1),node(.8)
    assert first != second and len(device.calls) == 4 and sum(call[1] for call in device.calls) == 202
    assert node.transform_program.transforms[-1].__name__ == "split_non_commuting"
    with pytest.raises(UnsupportedFeature,match="VJP"): node.gradient(.2)


def test_group_count_changes_get_fresh_allocation_and_no_old_processing_closure():
    def program(tape,theta):
        tape.ry(theta,0)
        return tape.expval(Hamiltonian([(1.,PauliX(0))]+([(1.,PauliZ(0))] if theta > .4 else [])))
    node = split_non_commuting(QNode(program,1,shots=101,seed=3),shot_dist="uniform")
    first = node(.2)
    assert node.last_metadata["executed_tape_count"] == 1
    node(.7)
    assert node.last_metadata["executed_tape_count"] == 2
    assert node(.2) == first


def test_shot_budget_is_physical_joint_draws_not_number_of_group_terms():
    tape = source([PauliX(0),PauliX(1),PauliX(0).tensor(PauliX(1))],shots=31)
    _,metadata = execute_transform(tape,split_non_commuting,limits=TransformLimits(max_total_shots=31),return_metadata=True)
    assert metadata["stages"][0]["sampled_shots"] == 31
    device = SampleCounter()
    with pytest.raises(MemoryError,match="max_total_shots"):
        execute_transform(source(shots=31),split_non_commuting,device,limits=TransformLimits(max_total_shots=61))
    assert device.calls == []


def test_sample_storage_and_grouping_work_budgets_fail_before_device_execution():
    tape,device = source(shots=100),SampleCounter()
    with pytest.raises(MemoryError,match="max_sample_values"):
        execute_transform(tape,split_non_commuting,device,limits=TransformLimits(max_sample_values=100))
    with pytest.raises(MemoryError,match="max_expansion_steps"):
        split_non_commuting(tape,limits=TransformLimits(max_expansion_steps=2))
    with pytest.raises(MemoryError,match="max_tapes"):
        split_non_commuting(tape,limits=TransformLimits(max_tapes=1))
    with pytest.raises(MemoryError,match="max_total_operations"):
        split_non_commuting(tape,limits=TransformLimits(max_total_operations=1))
    with pytest.raises(MemoryError,match="max_postprocessing_nodes"):
        split_non_commuting(tape,limits=TransformLimits(max_postprocessing_nodes=1))
    assert device.calls == []


@pytest.mark.parametrize("policy",["weighted_random","bad",lambda *_:[] ,3, []])
def test_unimplemented_distribution_is_rejected_not_silently_substituted(policy):
    with pytest.raises(UnsupportedFeature): split_non_commuting(source(),shot_dist=policy)


def test_unknown_strategy_seed_or_nonfinite_coefficients_are_rejected():
    with pytest.raises(ValueError): split_non_commuting(source(),grouping_strategy="commuting")
    for seed in [-1,True,"3"]:
        with pytest.raises(ValueError): split_non_commuting(source(),seed=seed)
    with pytest.raises(ValueError,match="finite"): split_non_commuting(source(coefficients=[np.inf,1.]))
    with pytest.raises(ValueError,match="finite"): split_non_commuting(source([PauliX(0)]*2,[1e308,1e308]))
    with pytest.raises(ValueError,match="distinct"): split_non_commuting(source([PauliString([(0,"X"),(0,"Y")])]))


def test_unsupported_measurements_sum_variance_and_local_overrides_fail_explicitly():
    from dataclasses import replace
    tape = source()
    tape.probs([0])
    with pytest.raises(UnsupportedFeature,match="terminal"): split_non_commuting(tape)
    tape = Tape(1)
    tape.var(Hamiltonian([(1.,PauliX(0)),(1.,PauliZ(0))]))
    with pytest.raises(UnsupportedFeature,match="not linear"): split_non_commuting(tape)
    tape = source()
    tape.measurements[0] = replace(tape.measurements[0],shots=13)
    with pytest.raises(UnsupportedFeature,match="Tape-level"): split_non_commuting(tape)
    tape = Tape(1)
    tape.expval(np.eye(2))
    with pytest.raises(UnsupportedFeature,match="PauliString"): split_non_commuting(tape)


def test_unproved_shot_rewrites_still_reject_and_native_receipt_cannot_be_truncated():
    from quantumbridge.transforms import transform
    @transform
    def bad(tape):
        children,process = split_non_commuting(tape,shot_dist="uniform")
        return children[:1],process
    with pytest.raises(TransformError,match="receipt"):
        execute_transform(source(shots=101),bad)


def test_invalid_device_joint_buffer_is_rejected_instead_of_fabricating_samples():
    class InvalidDevice(StatevectorDevice):
        def sample(self,*args,**kwargs): return ["2"]*kwargs["shots"]
    with pytest.raises(TransformError,match="invalid joint bitstring"):
        execute_transform(source([PauliX(0)],shots=10),split_non_commuting,InvalidDevice())


def test_processing_requires_real_matching_child_results_and_partition_width():
    tape = source(shots=[11,13])
    children,process = split_non_commuting(tape)
    with pytest.raises(ValueError,match="count"): process(())
    with pytest.raises(ValueError,match="partition"): process(((),()))
    with pytest.raises(TypeError,match="matching"): process(((0.,0.),(0.,0.)))


def test_geometry_derived_h2_is_actually_measured_and_reconstructed_with_uncertainty():
    from quantumbridge import qchem, templates
    molecule = qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr")
    problem = qchem.molecular_hamiltonian_native(molecule)
    tape = Tape(problem.num_qubits,shots=20001,seed=32)
    templates.BasisEmbedding([1,1,0,0],range(4)).apply(tape)
    qchem.apply_fermionic_excitation(tape,.2,[0,1,2,3])
    tape.expval(problem.hamiltonian)
    device = SampleCounter()
    actual,metadata = execute_transform(tape,split_non_commuting(shot_dist="weighted"),device,return_metadata=True)
    expected = StatevectorDevice().expectation(tape.circuit,problem.hamiltonian.to_quantumbridge())
    measured = stats(metadata)["partitions"][0]["source_measurements"][0]
    assert sum(call[1] for call in device.calls) == 20001
    assert len(device.calls) == len(receipts(metadata)) > 1
    assert abs(actual-expected) < 6*measured["standard_error"] + .002
    assert all(len(row["bitstrings"]) == row["shots"] for row in receipts(metadata))


def test_native_group_shape_basis_and_coefficient_invariants_are_validated():
    from dataclasses import replace
    from quantumbridge.qml.pauli_group import PauliGroup
    group = PauliGroup((((0,"X"),),),((0,"X"),),(0,),((1.,),))
    group.validate(1)
    for invalid in [replace(group,words=()),replace(group,basis=((0,"XY"),)),
                    replace(group,basis=((0,"X"),(1,"Z"))),replace(group,words=(((0,"Z"),),)),
                    replace(group,coefficients=()),replace(group,coefficients=((1.,2.),)),replace(group,coefficients=((1j,),))]:
        with pytest.raises(ValueError): invalid.validate(2)


def test_native_group_sample_guards_apply_even_outside_transform_program():
    from dataclasses import replace
    from quantumbridge.qml.pauli_group import measure_pauli_group
    group = split_non_commuting(source([PauliX(0)]))[0][0].observable
    device = SampleCounter()
    for shots in [0,True,-1]:
        with pytest.raises(ValueError,match="positive"): measure_pauli_group(device,Tape(2).circuit,group,shots,3)
    with pytest.raises(MemoryError,match="budget"):
        measure_pauli_group(device,Tape(2).circuit,replace(group,max_sample_values=1),2,3)
    two = split_non_commuting(source([PauliX(0),PauliX(1)]))[0][0].observable
    class NoAnalyticCalls(SampleCounter):
        def expectation(self,*args,**kwargs):
            raise AssertionError("Analytic budget must be checked before expectation evaluation.")
    with pytest.raises(MemoryError,match="budget"):
        measure_pauli_group(NoAnalyticCalls(),Tape(2).circuit,replace(two,max_sample_values=1),None,3)
    assert device.calls == []


def test_manual_joint_measurement_local_shots_cannot_bypass_transform_storage_budget():
    from dataclasses import replace
    from quantumbridge.transforms.program import check_batch
    children,_ = split_non_commuting(source([PauliX(0)]))
    child = children[0]
    child.measurements = [replace(child.measurements[0],shots=100)]
    child.output_tree = child.measurements[0]
    with pytest.raises(MemoryError,match="max_sample_values"):
        check_batch((child,),TransformLimits(max_sample_values=100))


def test_framework_only_coefficient_input_rejects_before_builder_can_detach_it():
    torch = pytest.importorskip("torch")
    called = []
    def builder(tape,x):
        called.append(True)
        return tape.expval(Hamiltonian([(float(x),PauliZ(0))]))
    node = split_non_commuting(QNode(builder,1,interface="numpy"))
    with pytest.raises(UnsupportedFeature,match="VJP"):
        node(torch.tensor(.4,requires_grad=True))
    assert called == []


def test_allocation_receipt_rejects_missing_wrong_parent_or_changed_shares():
    from copy import deepcopy
    from dataclasses import replace
    from quantumbridge.transforms.qwc import validate_shot_allocation, allocate_shots
    tape = source(shots=101)
    children,_ = split_non_commuting(tape,shot_dist="uniform")
    assert validate_shot_allocation(tape,children)
    assert not validate_shot_allocation(tape,())
    assert not validate_shot_allocation(tape,(tape,))
    wrong = deepcopy(children)
    wrong[0].shots = 50
    assert not validate_shot_allocation(tape,wrong)
    wrong = deepcopy(children)
    group = wrong[0].observable
    request = replace(wrong[0].measurements[0],observable=replace(group,allocation=replace(group.allocation,parent=ShotSpec.parse(100))))
    wrong[0].measurements = [request]
    assert not validate_shot_allocation(tape,wrong)
    with pytest.raises(ValueError,match="finite"): allocate_shots(ShotSpec.parse(100),(0.,0.),"weighted")
