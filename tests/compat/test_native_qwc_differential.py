# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent public-API probes, not copied upstream implementations/tests."""

import inspect

import numpy as np
import pytest
qml = pytest.importorskip("pennylane")

from quantumbridge import qchem, Circuit
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.transforms import split_non_commuting, execute_transform
from quantumbridge.utils.math import PauliString, PauliX, PauliY, PauliZ, Hamiltonian


def converted(word):
    factors = [{"X":qml.X,"Y":qml.Y,"Z":qml.Z}[label](wire) for wire,label in word.terms if label != "I"]
    return qml.prod(*factors) if factors else qml.Identity(0)


def pair(words,coefficients=None,shots=None):
    tape = Tape(2,shots=shots,seed=5)
    tape.ry(.4,0)
    tape.circuit.rx(.3,1)
    if coefficients is None:
        native = [tape.expval(word) for word in words]
        public = [qml.expval(converted(word)) for word in words]
    else:
        native = [tape.expval(Hamiltonian(zip(coefficients,words)))]
        public = [qml.expval(qml.Hamiltonian(coefficients,[converted(word) for word in words]))]
    return tape,qml.tape.QuantumScript([qml.RY(.4,0),qml.RX(.3,1)],public,shots=shots)


def actual_public(script,**options):
    tapes,processor = qml.transforms.split_non_commuting(script,**options)
    return processor(qml.execute(tapes,qml.device("default.qubit",wires=script.wires,seed=5)))


def test_public_generally_commuting_xx_yy_cannot_share_a_qwc_group():
    native,public = pair([PauliX(0).tensor(PauliX(1)),PauliY(0).tensor(PauliY(1))])
    assert len(split_non_commuting(native,"qwc")[0]) == len(qml.transforms.split_non_commuting(public,grouping_strategy="qwc")[0]) == 2
    np.testing.assert_allclose(execute_transform(native,split_non_commuting),actual_public(public,grouping_strategy="qwc"),atol=1e-12)


def test_public_x_and_xz_share_one_local_basis_group():
    native,public = pair([PauliX(0),PauliX(0).tensor(PauliZ(1))])
    assert len(split_non_commuting(native,"qwc")[0]) == len(qml.transforms.split_non_commuting(public,grouping_strategy="qwc")[0]) == 1
    np.testing.assert_allclose(execute_transform(native,split_non_commuting),actual_public(public,grouping_strategy="qwc"),atol=1e-12)


def test_public_default_all_pauli_is_qwc_not_disjoint_wires():
    native,public = pair([PauliX(0),PauliX(0).tensor(PauliZ(1))])
    assert len(split_non_commuting(native)[0]) == len(qml.transforms.split_non_commuting(public)[0]) == 1
    np.testing.assert_allclose(execute_transform(native,split_non_commuting),actual_public(public),atol=1e-12)


def test_public_wires_separates_overlapping_individual_requests():
    native,public = pair([PauliX(0),PauliX(0).tensor(PauliZ(1))])
    assert len(split_non_commuting(native,"wires")[0]) == len(qml.transforms.split_non_commuting(public,grouping_strategy="wires")[0]) == 2
    np.testing.assert_allclose(execute_transform(native,split_non_commuting(grouping_strategy="wires")),actual_public(public,grouping_strategy="wires"),atol=1e-12)


def test_public_fresh_hamiltonian_wires_still_requires_disjoint_supports():
    native,public = pair([PauliX(0),PauliX(0).tensor(PauliZ(1))],[2.,3.])
    assert len(split_non_commuting(native,"wires")[0]) == len(qml.transforms.split_non_commuting(public,grouping_strategy="wires")[0]) == 2
    assert execute_transform(native,split_non_commuting(grouping_strategy="wires")) == pytest.approx(actual_public(public,grouping_strategy="wires"),abs=1e-12)


def test_public_no_grouping_retains_one_group_per_unique_term():
    native,public = pair([PauliX(0),PauliX(0),PauliZ(1)],[1.,2.,.3])
    assert len(split_non_commuting(native,None)[0]) == len(qml.transforms.split_non_commuting(public,grouping_strategy=None)[0]) == 2
    assert execute_transform(native,split_non_commuting(grouping_strategy=None)) == pytest.approx(actual_public(public,grouping_strategy=None),abs=1e-12)


def test_public_identity_offset_duplicates_and_retained_zero_terms():
    native,public = pair([PauliX(0),PauliX(0),PauliString([]),PauliZ(0)],[1.,2.,3.,0.])
    assert len(split_non_commuting(native)[0]) == len(qml.transforms.split_non_commuting(public)[0]) == 2
    assert execute_transform(native,split_non_commuting) == pytest.approx(actual_public(public),abs=1e-12)


def test_public_identity_only_has_no_executed_child_tape():
    native,public = pair([PauliString([])],[3.])
    tapes,processor = qml.transforms.split_non_commuting(public)
    assert len(tapes) == len(split_non_commuting(native)[0]) == 0
    assert execute_transform(native,split_non_commuting) == processor(()) == 3.


def test_public_variance_of_one_pauli_and_its_mean_are_reconstructed():
    native,public = pair([PauliZ(0)])
    variance = native.var(PauliZ(0))
    public = qml.tape.QuantumScript(public.operations,[qml.expval(qml.Z(0)),qml.var(qml.Z(0))])
    np.testing.assert_allclose(execute_transform(native,split_non_commuting),actual_public(public),atol=1e-12)


def test_public_undistributed_shot_vector_copies_and_nested_native_order():
    native,public = pair([PauliZ(0),PauliZ(1)],shots=[100,(200,2)])
    # Deterministic eigenstates separate shape/order from Monte Carlo tolerance.
    native.circuit.operations = []
    native.x(1)
    native.set_output({"local":[native.measurements[0],native.measurements[1]]})
    public = qml.tape.QuantumScript([qml.X(1)],public.measurements,shots=[100,(200,2)])
    tapes,_ = qml.transforms.split_non_commuting(public)
    assert tapes[0].shots.num_copies == len(ShotSpec.parse(native.shots).partitions) == 3
    actual,expected = execute_transform(native,split_non_commuting),actual_public(public)
    assert [value["local"] for value in actual] == [[float(x) for x in part] for part in expected] == [[1.,-1.]]*3


@pytest.mark.parametrize("policy,coefficients",[("uniform",[1.,3.,1.]),("weighted",[1.,3.,1.])])
def test_public_available_allocation_matches_individual_partitions_and_records_old_api_boundary(policy,coefficients):
    words = [PauliX(0),PauliZ(0),PauliY(0)]
    for shots in [29,101,200]:
        native,public = pair(words,coefficients,shots)
        children,_ = split_non_commuting(native,shot_dist=policy)
        if "shot_dist" in inspect.signature(qml.transforms.split_non_commuting).parameters:
            tapes,_ = qml.transforms.split_non_commuting(public,shot_dist=policy)
            assert [child.shots.partitions[0] for child in children] == [child.shots.total_shots for child in tapes]
        else:
            # PL 0.42.3 has no allocation API. This is a verified unsupported
            # upstream boundary, not a skipped or invented differential pass.
            with pytest.raises(TypeError,match="shot_dist"):
                qml.transforms.split_non_commuting(public,shot_dist=policy)
        assert sum(child.shots.partitions[0] for child in children) == shots


def test_public_distributed_shot_vector_flattening_is_an_explicit_native_extension_not_parity():
    native,public = pair([PauliX(0),PauliZ(0)],[3.,1.],shots=[100,(200,2)])
    children,_ = split_non_commuting(native,shot_dist="weighted")
    assert [child.shots.partitions for child in children] == [(75,150,150),(25,50,50)]
    if "shot_dist" in inspect.signature(qml.transforms.split_non_commuting).parameters:
        tapes,_ = qml.transforms.split_non_commuting(public,shot_dist="weighted")
        assert [child.shots.total_shots for child in tapes] == [375,125]
        assert not any(child.shots.has_partitioned_shots for child in tapes)
    else:
        with pytest.raises(TypeError): qml.transforms.split_non_commuting(public,shot_dist="weighted")


def test_public_transformed_qnode_rebinds_analytic_values_for_each_input():
    @qml.qnode(qml.device("default.qubit",wires=2))
    def public(theta):
        qml.RY(theta,0)
        return qml.expval(qml.X(0)+.2*qml.Z(0))
    oracle = qml.transforms.split_non_commuting(public,grouping_strategy="qwc")
    def native(tape,theta):
        tape.ry(theta,0)
        return tape.expval(Hamiltonian([(1.,PauliX(0)),(.2,PauliZ(0))]))
    node = split_non_commuting(QNode(native,2))
    for theta in [.2,.7,-.3]:
        assert node(theta) == pytest.approx(oracle(theta),abs=1e-12)


def test_public_finite_shot_qwc_energy_is_statistically_consistent_not_seed_equal():
    native,public = pair([PauliX(0),PauliX(0).tensor(PauliZ(1))],[2.,3.],shots=10001)
    value,metadata = execute_transform(native,split_non_commuting,return_metadata=True)
    standard_error = metadata["stages"][0]["postprocessing_metadata"][0]["partitions"][0]["source_measurements"][0]["standard_error"]
    assert abs(value-float(actual_public(public))) < 8*standard_error + .01


def test_public_generated_h2_group_expectations_match_native_geometry_computation():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr"))
    native = Tape(4)
    native.x(0)
    native.x(1)
    qchem.apply_fermionic_excitation(native,.2,[0,1,2,3])
    native.expval(problem.hamiltonian)
    hamiltonian = problem.hamiltonian.to_quantumbridge()
    # Native exp(theta/2*(A-A.dagger)) has the opposite public gate sign.
    # Verify the complete complex operator before using it as an oracle.
    unitary = qchem.apply_fermionic_excitation(Circuit(4),.2,[0,1,2,3])
    np.testing.assert_allclose(Operator.from_circuit(unitary).data,
                               qml.matrix(qml.DoubleExcitation(-.2,[0,1,2,3])),atol=1e-12,rtol=0)
    public = qml.tape.QuantumScript([qml.X(0),qml.X(1),qml.DoubleExcitation(-.2,[0,1,2,3])],
                                   [qml.expval(qml.Hamiltonian([c for c,_ in hamiltonian.terms],
                                   [converted(word) for _,word in hamiltonian.terms]))])
    assert execute_transform(native,split_non_commuting) == pytest.approx(actual_public(public),abs=2e-11)
