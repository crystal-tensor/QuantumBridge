import json
import numpy as np
import pytest
from quantumbridge import (Circuit,Parameter,PauliX,PauliZ,DensityMatrixDevice,StatevectorDevice,Hamiltonian)
from quantumbridge.simulator import NativeAerSimulator,AerExecutionLimits,AerResult
from quantumbridge.noise import NoiseModel,ReadoutError,pauli_error,amplitude_damping_error
from quantumbridge.providers import JobError,JobStatus
from quantumbridge.serialization import qasm2_dumps,qasm3_dumps,qpy_dumps,SerializationError


def run(circuit,method='statevector',shots=None,**options):
    return NativeAerSimulator(method=method,shots=shots,**options).run(circuit).result()


def test_intermediate_states_and_result_copy_are_not_final_state_aliases():
    c=Circuit(1).h(0).save_statevector(label='a').z(0).save_statevector(label='b')
    result=run(c);data=result.data()
    np.testing.assert_allclose(data['a'],np.array([1,1])/np.sqrt(2))
    np.testing.assert_allclose(data['b'],np.array([1,-1])/np.sqrt(2))
    data['a'][:]=0
    assert np.linalg.norm(result.data()['a'])==pytest.approx(1.)


def test_save_density_matrix_and_subsystem_order():
    data=run(Circuit(3).h(0).cx(0,2).save_density_matrix([2],label='local'),'density_matrix').data()
    np.testing.assert_allclose(data['local'],np.eye(2)/2)


def test_probabilities_and_probability_dictionary_have_native_wire_order():
    c=Circuit(2).x(0).save_probabilities(label='array').save_probabilities_dict(label='dict')
    data=run(c).data()
    np.testing.assert_allclose(data['array'],[0,0,1,0]);assert data['dict']=={'0x2':1.}


def test_amplitudes_and_squared_amplitudes():
    c=Circuit(2).h(0).save_amplitudes([0,2],label='amplitudes').save_amplitudes_squared([0,1,2],label='squared')
    data=run(c).data()
    np.testing.assert_allclose(data['amplitudes'],[1/np.sqrt(2)]*2)
    np.testing.assert_allclose(data['squared'],[.5,0,.5])


def test_expectation_variance_is_nonzero_and_second_moment_is_used():
    data=run(Circuit(1).h(0).save_expectation_value_variance(PauliZ(0),label='z')).data()
    np.testing.assert_allclose(data['z'],[0,1],atol=1e-12)


def test_hamiltonian_second_moment_includes_cross_terms():
    observable=Hamiltonian([(1.,PauliZ(0)),(.5,PauliX(0))])
    value=run(Circuit(1).save_expectation_value_variance(observable)).data()['expectation_value_variance']
    np.testing.assert_allclose(value,[1.,.25])


def test_set_statevector_actually_replaces_prepared_state():
    data=run(Circuit(1).x(0).set_statevector([1.,0.]).h(0).save_statevector()).data()
    np.testing.assert_allclose(data['statevector'],np.ones(2)/np.sqrt(2))


def test_set_density_matrix_replaces_state_and_preserves_mixture():
    c=Circuit(1).x(0).set_density_matrix(np.diag([.3,.7])).x(0).save_density_matrix()
    np.testing.assert_allclose(run(c,'density_matrix').data()['density_matrix'],np.diag([.7,.3]))


def test_pure_set_can_feed_density_method():
    c=Circuit(1).set_statevector([0,1]).save_density_matrix()
    np.testing.assert_allclose(run(c,'density_matrix').data()['density_matrix'],np.diag([0,1]))


def test_native_result_json_retains_complex_snapshots_and_labels():
    c=Circuit(1).h(0).phase(.3,0).save_statevector()
    original=run(c)
    restored=AerResult.from_json(original.to_json())
    np.testing.assert_allclose(original.data()['statevector'],restored.data()['statevector'])


def test_native_ir_retains_save_set_semantics():
    from quantumbridge.ir import IRProgram
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    c=Circuit(1).x(0).set_statevector([1.,0.]).h(0).save_statevector()
    restored=circuit_from_ir(IRProgram.from_json(c.to_ir().to_json()))
    np.testing.assert_allclose(run(restored).data()['statevector'],run(c).data()['statevector'])


def test_unsupported_standard_serialization_never_discards_save_set():
    c=Circuit(1).set_statevector([1.,0.]).save_statevector()
    for writer in (qasm2_dumps,qasm3_dumps,qpy_dumps):
        with pytest.raises((SerializationError,ValueError)):writer(c)


def test_conditional_pershot_density_groups_match_memory():
    c=Circuit(1,1).h(0).measure(0,0).save_density_matrix(conditional=True,pershot=True)
    result=run(c,'density_matrix',shots=32,seed_simulator=7,memory=True)
    groups=result.data()['density_matrix'];counts=result.get_counts()
    assert len(groups['0x0'])==counts['0'] and len(groups['0x1'])==counts['1']
    assert len(result.get_memory())==32
    for key,values in groups.items():
        for rho in values:np.testing.assert_allclose(rho,np.diag([1,0]) if key=='0x0' else np.diag([0,1]))


def test_conditional_average_density_renormalizes_each_group():
    c=Circuit(1,1).h(0).measure(0,0).save_density_matrix(conditional=True)
    groups=run(c,'density_matrix').data()['density_matrix']
    np.testing.assert_allclose(groups['0x0'],np.diag([1,0]));np.testing.assert_allclose(groups['0x1'],np.diag([0,1]))


def test_unnormalized_snapshot_retains_group_weight():
    c=Circuit(1,1).h(0).measure(0,0).save_density_matrix(conditional=True,unnormalized=True)
    groups=run(c,'density_matrix').data()['density_matrix']
    assert np.trace(groups['0x0'])==pytest.approx(.5)


def test_mixed_analytic_branch_cannot_masquerade_as_one_statevector():
    c=Circuit(1,1).h(0).measure(0,0).save_statevector()
    with pytest.raises(JobError,match='mixed ensemble'):run(c)


def test_dynamic_readout_changes_feedback_not_physical_projection():
    model=NoiseModel().add_readout_error(ReadoutError([[0,1],[0,1]]),[0])
    c=Circuit(2,2).measure(0,0).if_test((0,1),Circuit(2,2).x(1)).measure(1,1).save_density_matrix()
    result=run(c,'density_matrix',noise_model=model)
    assert result.results[0].probabilities()=={'11':1.}
    np.testing.assert_allclose(result.data()['density_matrix'],np.diag([0,1,0,0]))


def test_correlated_readout_uses_joint_mapping():
    matrix=np.zeros((4,4));matrix[:,2]=1
    model=NoiseModel().add_readout_error(ReadoutError(matrix),[0,1])
    c=Circuit(2,2).measure(0,1).measure(1,0).save_density_matrix()
    result=run(c,'density_matrix',shots=8,noise_model=model)
    assert result.get_counts()=={'10':8}
    np.testing.assert_allclose(result.data()['density_matrix'],np.diag([1,0,0,0]))


def test_repeated_noisy_gate_inside_for_is_not_applied_once_at_end():
    body=Circuit(1).x(0)
    c=Circuit(1).for_loop([0,1,2],body).save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    np.testing.assert_allclose(run(c,'density_matrix',noise_model=model).data()['density_matrix'],np.diag([1,0]))


def test_while_feedback_with_noise_and_snapshot_uses_runtime_state():
    from quantumbridge.serialization import qasm3_loads
    c=qasm3_loads('OPENQASM 3.0;include "stdgates.inc";qubit q;bit c;x q;c=measure q;while(c){reset q;c=measure q;}')
    c.save_density_matrix()
    np.testing.assert_allclose(run(c,'density_matrix').data()['density_matrix'],np.diag([1,0]))


def test_set_state_inside_true_branch_executes():
    c=Circuit(1,1).x(0).measure(0,0).if_test((0,1),Circuit(1,1).set_statevector([1,0])).save_statevector()
    np.testing.assert_allclose(run(c).data()['statevector'],[1,0])


def test_loop_repeated_save_aggregates_execution_points():
    c=Circuit(1).for_loop([0,1],Circuit(1).x(0).save_probabilities()).save_statevector()
    np.testing.assert_allclose(run(c).data()['probabilities'],[.5,.5])


def test_multi_circuit_results_and_seed_are_independent():
    simulator=NativeAerSimulator(shots=32,seed_simulator=9,memory=True)
    circuits=[Circuit(1,1).h(0).measure(0,0),Circuit(1,1).x(0).measure(0,0)]
    a,b=simulator.run(circuits).result(),simulator.run(circuits).result()
    assert a.get_counts()==b.get_counts() and a.get_counts(1)=={'1':32}
    assert len(a.get_memory(0))==32


def test_failed_experiment_makes_real_job_error_status():
    simulator=NativeAerSimulator(method='stabilizer')
    job=simulator.run([Circuit(1).h(0),Circuit(1).t(0)])
    assert job.status()==JobStatus.ERROR
    with pytest.raises(JobError):job.result()


def test_automatic_selection_records_actual_supported_method():
    c=Circuit(1).h(0).save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(.2),'h')
    result=run(c,'automatic',noise_model=model)
    assert result.results[0].metadata()['method']=='density_matrix'


def test_unitary_method_accumulates_gates_phase_and_replacement():
    c=Circuit(2).h(0).cx(0,1);c.global_phase=.23
    from quantumbridge.information import Operator
    expected=Operator.from_circuit(c).data
    c.save_unitary()
    np.testing.assert_allclose(run(c,'unitary').data()['unitary'],expected,atol=1e-12)
    c=Circuit(1).x(0).set_unitary(np.eye(2)).h(0).save_unitary()
    np.testing.assert_allclose(run(c,'unitary').data()['unitary'],np.array([[1,1],[1,-1]])/np.sqrt(2))


def test_superoperator_is_full_channel_not_single_density():
    c=Circuit(1).h(0).reset(0).save_superop()
    channel=run(c,'superop').data()['superop']
    assert channel.shape==(4,4)
    for rho in (np.diag([1,0]),np.diag([0,1]),np.array([[.5,-.5j],[.5j,.5]])):
        np.testing.assert_allclose((channel@rho.reshape(-1,order='F')).reshape(2,2,order='F'),np.diag([1,0]),atol=1e-12)


def test_superop_gate_noise_agrees_with_density_evolution():
    model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(.3),'h')
    channel=run(Circuit(1).h(0).save_superop(),'superop',noise_model=model).data()['superop']
    rho=(channel@np.array([1,0,0,0])).reshape(2,2,order='F')
    reference=DensityMatrixDevice(noise_model=model).density_matrix(Circuit(1).h(0))
    np.testing.assert_allclose(rho,reference,atol=1e-12)


def test_tableau_save_set_and_clifford_measurement_are_native():
    from quantumbridge.information import StabilizerState
    initial=StabilizerState(Circuit(2).h(0).cx(0,1))
    c=Circuit(2).set_stabilizer(initial).save_stabilizer().save_expectation_value(PauliZ(0))
    data=run(c,'stabilizer').data()
    assert data['stabilizer']['stabilizer'] and data['expectation_value']==pytest.approx(0.)


def test_hundred_qubit_mps_snapshots_and_local_observations_never_dense(monkeypatch):
    from quantumbridge.information import MatrixProductState
    def forbidden(*args,**kwargs):raise AssertionError('Dense expansion forbidden.')
    monkeypatch.setattr(MatrixProductState,'statevector',forbidden)
    monkeypatch.setattr(StatevectorDevice,'statevector',forbidden)
    monkeypatch.setattr(DensityMatrixDevice,'density_matrix',forbidden)
    c=Circuit(100).h(0)
    for wire in range(99):c.cx(wire,wire+1)
    c.save_matrix_product_state(label='mps').z(99).save_amplitudes([0,(1<<100)-1],label='after_z')
    c.save_expectation_value(PauliZ(99),label='z').save_density_matrix([99],label='local')
    data=run(c,'matrix_product_state').data()
    assert data['mps']['peak_bond_dimension']==2 and len(data['mps']['tensors'])==100
    assert data['z']==pytest.approx(0.,abs=1e-12)
    np.testing.assert_allclose(data['after_z'],np.array([1,-1])/np.sqrt(2),atol=1e-12)
    np.testing.assert_allclose(data['local'],np.eye(2)/2,atol=1e-12)


def test_set_mps_restores_compact_tensor_execution():
    from quantumbridge.information import MatrixProductState
    c=Circuit(3).x(0).set_matrix_product_state(MatrixProductState.zero(3)).x(2).save_matrix_product_state().save_probabilities()
    data=run(c,'matrix_product_state').data()
    assert data['probabilities'][1]==pytest.approx(1.)


def test_physical_target_noise_binds_after_real_compilation():
    from quantumbridge.compiler import Target,native_transpile
    from quantumbridge.noise import depolarizing_error
    c=native_transpile(Circuit(3).h(0).cx(0,2),target=Target(3,('h','cx'),[(0,1),(1,0),(1,2),(2,1)]),optimization_level=0)
    ideal=DensityMatrixDevice().density_matrix(c)
    reference=c.copy_empty_like();error=depolarizing_error(.23,2)
    for operation in c.operations:
        reference.append(operation.name,operation.targets,controls=operation.controls,params=operation.params,metadata=operation.metadata)
        if operation.name=='cx':reference.kraus(error.kraus(),tuple(reversed(operation.wires)))
    c.save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(error,'cx')
    actual=run(c,'density_matrix',noise_model=model).data()['density_matrix']
    assert np.trace(actual)==pytest.approx(1.)
    np.testing.assert_allclose(actual,DensityMatrixDevice().density_matrix(reference),atol=1e-12)
    assert np.linalg.norm(actual-ideal)>.01
    assert any(op.name=='cx' for op in c.operations) and 'routing' in c.metadata


def test_fixed_gate_noise_parameter_shift_is_not_ideal_gradient():
    from quantumbridge.qml import QNode
    p=Parameter('theta');model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(.3),'ry')
    node=QNode.from_circuit(Circuit(1).ry(p,0),PauliZ(0),device=DensityMatrixDevice(noise_model=model))
    assert node.gradient(.4,method='parameter-shift')==pytest.approx(-.7*np.sin(.4),abs=1e-10)
    assert node.gradient(.4,method='finite-diff')==pytest.approx(-.7*np.sin(.4),abs=1e-8)
    from quantumbridge.core.classical import UnsupportedFeature
    with pytest.raises(UnsupportedFeature):node.gradient(.4,method='adjoint')


def test_analytic_pershot_is_explicitly_unsupported():
    with pytest.raises(JobError,match='finite-shot'):run(Circuit(1).save_statevector(pershot=True))


def test_snapshot_byte_budget_fails_without_returning_empty_data():
    with pytest.raises(JobError,match='snapshot'):run(Circuit(3).save_statevector(),aer_limits=AerExecutionLimits(max_snapshot_bytes=10))


def test_pershot_snapshot_budget_limits_actual_storage():
    with pytest.raises(JobError,match='snapshot'):run(Circuit(1).save_statevector(pershot=True),shots=10,aer_limits=AerExecutionLimits(max_pershot_snapshot_bytes=100))


def test_duplicate_labels_and_missing_lookup_are_errors():
    with pytest.raises(JobError,match='duplicate'):run(Circuit(1).save_statevector().save_statevector())
    with pytest.raises(KeyError):run(Circuit(1).save_statevector()).results[0].data('missing')


def test_invalid_set_shapes_normalization_and_density_are_rejected():
    for action in (lambda:Circuit(2).set_statevector([1,0]),lambda:Circuit(1).set_statevector([1,1]),lambda:Circuit(1).set_density_matrix([[1,1],[0,0]]),lambda:Circuit(1).set_density_matrix([[2,0],[0,-1]])):
        with pytest.raises(ValueError):action()


def test_unsupported_gpu_method_precision_and_options_reject():
    for options in ({'device':'GPU'},{'method':'extended_stabilizer'},{'method':'tensor_network'},{'precision':'single'},{'fusion_enable':True}):
        with pytest.raises(ValueError):NativeAerSimulator(**options)


def test_oversized_dense_execution_is_rejected_before_allocation():
    with pytest.raises(JobError,match='max_qubits_dense'):run(Circuit(100).save_statevector())


def test_excessive_shots_and_noise_qargs_reject():
    with pytest.raises(MemoryError):NativeAerSimulator(shots=100001)
    model=NoiseModel().add_quantum_error(pauli_error([('X',1.)]),'x',[2])
    with pytest.raises(JobError):run(Circuit(1).x(0),noise_model=model)


def test_unitary_does_not_accept_measure_reset_or_noise():
    for circuit in (Circuit(1).reset(0),Circuit(1,1).measure(0,0)):
        with pytest.raises(JobError):run(circuit,'unitary')


def test_malformed_result_array_is_not_accepted():
    value=run(Circuit(1).save_statevector()).to_dict()
    value['results'][0]['metadata']['saved_snapshots']['statevector']['imag']=[0.]
    with pytest.raises(ValueError):AerResult.from_dict(value)
