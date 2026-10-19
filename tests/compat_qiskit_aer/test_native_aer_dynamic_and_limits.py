import numpy as np
import pytest
from quantumbridge import Circuit,PauliZ,StatevectorDevice
from quantumbridge.noise import NoiseModel,pauli_error,ReadoutError,amplitude_damping_error
from quantumbridge.simulator import NativeAerSimulator,AerExecutionLimits
from quantumbridge.providers import JobError
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.serialization import qasm3_loads


def result(c,method='density_matrix',shots=None,model=None,**options):
    return NativeAerSimulator(method,shots=shots,noise_model=model,**options).run(c).result()


def test_noisy_if_only_applies_error_on_actually_executed_gate():
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    c=Circuit(1).if_else(False,Circuit(1).x(0),Circuit(1).h(0)).save_expectation_value(PauliZ(0))
    assert result(c,model=model).data()['expectation_value']==pytest.approx(0.,abs=1e-12)


def test_noisy_classical_counter_while_and_store():
    c=qasm3_loads('OPENQASM 3.0;include "stdgates.inc";qubit q;uint[4] n=0;while(n<3){x q;n+=1;}')
    c.save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    np.testing.assert_allclose(result(c,model=model).data()['density_matrix'],np.diag([1,0]))


def test_noisy_switch_path_is_executed_not_flattened_all_cases():
    c=qasm3_loads('OPENQASM 3.1;include "stdgates.inc";qubit q;int[4] n=1;switch(n){case 0{h q;}case 1{x q;}default{z q;}}')
    c.save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    np.testing.assert_allclose(result(c,model=model).data()['density_matrix'],np.diag([1,0]))


def test_noisy_loop_saves_capture_each_iteration_after_its_error():
    body=Circuit(1).x(0).save_probabilities()
    c=Circuit(1).for_loop([0,1,2],body)
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    np.testing.assert_allclose(result(c,model=model).data()['probabilities'],[1,0])


def test_noisy_break_does_not_execute_later_gates_or_errors():
    body=Circuit(1).x(0).break_loop().h(0)
    c=Circuit(1).for_loop([0,1,2],body).save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(1.),'x')
    np.testing.assert_allclose(result(c,model=model).data()['density_matrix'],np.diag([1,0]))


def test_quantum_error_on_measure_runs_before_projection():
    c=Circuit(1,1).measure(0,0).save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'measure')
    value=result(c,model=model)
    assert value.results[0].probabilities()=={'1':1.}
    np.testing.assert_allclose(value.data()['density_matrix'],np.diag([0,1]))


def test_quantum_error_on_reset_runs_after_state_reset():
    c=Circuit(1,1).x(0).reset(0).measure(0,0)
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'reset')
    assert result(c,shots=8,model=model).get_counts()=={'1':8}


def test_correlated_readout_controls_subsequent_dynamic_gate():
    from quantumbridge.core.classical import register
    matrix=np.zeros((4,4));matrix[:,3]=1.
    model=NoiseModel().add_readout_error(ReadoutError(matrix),[0,1])
    c=Circuit(3,2).measure(0,0).measure(1,1).if_else(register((0,1)).eq(3),Circuit(3,2).x(2)).save_expectation_value(PauliZ(2))
    assert result(c,model=model).data()['expectation_value']==pytest.approx(-1.)


def test_hundred_qubit_mps_pershot_tensor_saves_noise_and_counts_no_dense(monkeypatch):
    from quantumbridge.information import MatrixProductState
    def forbidden(*args,**kwargs):raise AssertionError('No dense fallback allowed.')
    monkeypatch.setattr(MatrixProductState,'statevector',forbidden)
    monkeypatch.setattr(StatevectorDevice,'statevector',forbidden)
    c=Circuit(100,2).h(0)
    for wire in range(99):c.cx(wire,wire+1)
    c.save_matrix_product_state(pershot=True).measure(0,0).measure(99,1)
    model=NoiseModel().add_quantum_error(pauli_error([('X',1.)]),'h',[0])
    actual=result(c,'matrix_product_state',shots=8,model=model,seed_simulator=2,memory=True)
    assert len(actual.data()['matrix_product_state'])==8
    assert set(actual.get_counts())<= {'00','11'}
    metadata=actual.results[0].metadata()
    assert metadata['max_bond_observed']==2 and metadata['snapshot_storage_bytes']>0


def test_thermal_and_amplitude_models_are_not_supported_by_tableau_if_non_clifford():
    c=Circuit(1).h(0).save_stabilizer()
    model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(.3),'h')
    with pytest.raises(JobError,match='Clifford|Kraus'):result(c,'stabilizer',model=model)


def test_analytic_memory_and_non_mps_specific_options_are_not_silently_ignored():
    with pytest.raises(JobError):result(Circuit(1),memory=True)
    with pytest.raises(JobError):result(Circuit(1),max_bond_dim=2)


def test_snapshot_count_and_conditional_group_budgets():
    with pytest.raises(JobError,match='max_snapshot_count'):
        result(Circuit(1).save_probabilities(label='a').save_probabilities(label='b'),aer_limits=AerExecutionLimits(max_snapshot_count=1))
    c=Circuit(1,1).h(0).measure(0,0).save_density_matrix(conditional=True)
    with pytest.raises(JobError,match='max_conditional_groups'):result(c,aer_limits=AerExecutionLimits(max_conditional_groups=1))


def test_map_dimension_and_kraus_channel_budgets():
    with pytest.raises(JobError,match='max_matrix_dimension'):result(Circuit(3).save_superop(),'superop',aer_limits=AerExecutionLimits(max_matrix_dimension=4))
    model=NoiseModel().add_all_qubit_quantum_error(amplitude_damping_error(.3),'x')
    with pytest.raises(JobError,match='max_noise_kraus_ops'):result(Circuit(1).x(0),model=model,aer_limits=AerExecutionLimits(max_noise_kraus_ops=1))
    model=NoiseModel().add_readout_error(ReadoutError(np.eye(2)),[0]).add_readout_error(ReadoutError(np.eye(2)),[1])
    with pytest.raises(JobError,match='max_noise_channels'):result(Circuit(2),model=model,aer_limits=AerExecutionLimits(max_noise_channels=1))
    from quantumbridge.core.control_flow import ExecutionLimits
    c=Circuit(1,1).h(0).measure(0,0)
    with pytest.raises(JobError,match='max_branches'):result(c,aer_limits=AerExecutionLimits(max_dynamic_branches=1),execution_limits=ExecutionLimits(max_branches=100))


def test_replacement_superoperator_is_actual_channel_not_state_metadata():
    identity=np.eye(4)
    c=Circuit(1).x(0).set_superop(identity).h(0).save_superop()
    h=np.array([[1,1],[1,-1]])/np.sqrt(2)
    np.testing.assert_allclose(result(c,'superop').data()['superop'],np.kron(h,h),atol=1e-12)


def test_invalid_correlated_partial_group_is_explicitly_rejected():
    model=NoiseModel().add_readout_error(ReadoutError(np.eye(4)),[0,1])
    with pytest.raises(JobError,match='complete'):result(Circuit(2,1).measure(0,0),model=model)


def test_seed_and_options_validation_boundaries():
    for fields in ({'seed_simulator':-1},{'shots':True},{'max_memory_mb':float('nan')},{'max_bond_dim':0},{'cutoff':1.},{'memory':1},{'noise_model':{}},{'execution_limits':{}},{'aer_limits':{}}):
        with pytest.raises((ValueError,TypeError)):NativeAerSimulator(**fields)


def test_large_vector_pauli_moments_never_construct_density_or_dense_pauli(monkeypatch):
    from quantumbridge.simulator.snapshots import SnapshotContext
    from quantumbridge.operators import SparsePauliOperator
    def forbidden(*args,**kwargs):raise AssertionError('Sparse Pauli observation expanded densely.')
    monkeypatch.setattr(SnapshotContext,'_density',forbidden)
    monkeypatch.setattr(SparsePauliOperator,'matrix',forbidden)
    c=Circuit(16).h(0).save_expectation_value_variance(PauliZ(0))
    np.testing.assert_allclose(result(c,'statevector').data()['expectation_value_variance'],[0,1],atol=1e-12)


def test_density_pauli_row_contraction_retains_y_sign_and_cross_terms():
    from quantumbridge.operators import SparsePauliOperator
    observable=SparsePauliOperator([('Y',.7),('Z',.2)])
    c=Circuit(1).h(0).s(0).save_expectation_value_variance(observable)
    np.testing.assert_allclose(result(c).data()['expectation_value_variance'],[.7,.04],atol=1e-12)


def test_implicit_correlated_readout_is_rejected_not_silently_discarded():
    from quantumbridge.devices import DensityMatrixDevice
    model=NoiseModel().add_readout_error(ReadoutError(np.eye(4)),[0,1])
    with pytest.raises(JobError,match='explicit complete'):result(Circuit(2),shots=2,model=model)
    with pytest.raises(UnsupportedFeature,match='explicit complete'):DensityMatrixDevice(noise_model=model).sample(Circuit(2),shots=2)


def test_direct_density_sampling_honors_new_attached_noise():
    from quantumbridge.devices import DensityMatrixDevice
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    assert DensityMatrixDevice(noise_model=model).sample(Circuit(1).x(0),shots=3)==['0']*3


def test_compact_tableau_local_density_and_vector_saves_agree():
    c=Circuit(2).h(0).cx(0,1).save_density_matrix([0]).save_statevector().save_amplitudes([0,3])
    data=result(c,'stabilizer').data()
    np.testing.assert_allclose(data['density_matrix'],np.eye(2)/2)
    np.testing.assert_allclose(data['statevector'],[1/np.sqrt(2),0,0,1/np.sqrt(2)])
    np.testing.assert_allclose(data['amplitudes'],[1/np.sqrt(2)]*2)


def test_dense_observable_snapshot_and_compact_mps_amplitude_query():
    c=Circuit(1).h(0).save_expectation_value_variance(np.diag([2.,-1.]))
    np.testing.assert_allclose(result(c).data()['expectation_value_variance'],[.5,2.25])
    m=Circuit(30).h(0).save_amplitudes([0,1<<29]).save_density_matrix([29])
    data=result(m,'matrix_product_state').data()
    np.testing.assert_allclose(data['amplitudes'],[1/np.sqrt(2)]*2)
    np.testing.assert_allclose(data['density_matrix'],np.diag([1,0]),atol=1e-12)


def test_set_tableau_and_pure_mps_replacements_then_propagate():
    from quantumbridge.information import Clifford
    c=Circuit(1).x(0).set_stabilizer(Clifford(Circuit(1).h(0))).z(0).save_expectation_value(PauliZ(0))
    assert result(c,'stabilizer').data()['expectation_value']==pytest.approx(0.,abs=1e-12)
    m=Circuit(1).x(0).set_statevector([1,0]).h(0).save_matrix_product_state()
    from quantumbridge.information import MatrixProductState
    np.testing.assert_allclose(MatrixProductState.from_dict(result(m,'matrix_product_state').data()['matrix_product_state']).statevector(),np.ones(2)/np.sqrt(2))


def test_deterministic_map_metadata_does_not_claim_sampled_shots():
    value=result(Circuit(1).h(0).save_unitary(),'unitary',shots=1024).results[0].metadata()
    assert value['shots'] is None and value['requested_shots']==1024


def test_deserialized_snapshot_payloads_reject_nonfinite_and_inconsistent_types():
    from quantumbridge.simulator.snapshots import encode,decode
    from quantumbridge.simulator import AerResult
    assert decode(encode(np.complex128(1+2j)))==1+2j
    for value in ({'qb_simulator_complex':[float('nan'),0]},
                  {'qb_simulator_array':True,'real':[0.],'imag':[1.],'complex':False},
                  {'qb_simulator_array':True,'real':[0.],'imag':[0.],'complex':'no'}):
        with pytest.raises(ValueError):decode(value)
    with pytest.raises(ValueError):AerResult.from_dict({'format':'qb-aer-result-v1','success':True,'status':'COMPLETED','results':[]})


def test_ir_snapshot_paulis_and_amplitude_indices_are_revalidated():
    c=Circuit(1).save_expectation_value(PauliZ(0))
    c.operations[0].metadata['simulator_instruction']['paulis']=[['ZZ',1.]]
    with pytest.raises(JobError,match='Pauli'):result(c)
    c=Circuit(1).save_amplitudes([0])
    c.operations[0].metadata['simulator_instruction']['indices']=[2]
    with pytest.raises(JobError,match='indices'):result(c,'statevector')


def test_correlated_group_cannot_reorder_overwriting_classical_destinations():
    model=NoiseModel().add_readout_error(ReadoutError(np.eye(4)),[0,1])
    c=Circuit(3,2).measure(2,0).measure(0,0).measure(1,1)
    with pytest.raises(JobError,match='distinct classical'):result(c,model=model)


def test_map_and_tableau_respect_requested_memory_before_allocation():
    with pytest.raises(JobError,match='max_memory_mb'):result(Circuit(3).save_unitary(),'unitary',max_memory_mb=.001)
    with pytest.raises(JobError,match='max_memory_mb'):result(Circuit(100).save_stabilizer(),'stabilizer',max_memory_mb=.001)
    with pytest.raises(JobError,match='max_state_bytes'):result(Circuit(100).save_stabilizer(),'stabilizer',aer_limits=AerExecutionLimits(max_state_bytes=1000))
    assert NativeAerSimulator().configuration()['conditional'] is True


def test_large_vector_probability_save_is_not_a_full_density_allocation(monkeypatch):
    from quantumbridge.simulator.snapshots import SnapshotContext
    def forbidden(*args,**kwargs):raise AssertionError('Probability query constructed density.')
    monkeypatch.setattr(SnapshotContext,'_density',forbidden)
    c=Circuit(13).h(0).save_probabilities()
    values=result(c,'statevector').data()['probabilities']
    assert len(values)==8192 and values[0]==pytest.approx(.5) and values[4096]==pytest.approx(.5)


def test_mixed_density_squared_amplitudes_and_automatic_clifford_save():
    c=Circuit(1).set_density_matrix(np.diag([.3,.7])).save_amplitudes_squared([1,0])
    np.testing.assert_allclose(result(c).data()['amplitudes_squared'],[.7,.3])
    saved=result(Circuit(1).h(0).save_clifford(),'automatic')
    assert saved.results[0].metadata()['method']=='stabilizer' and 'clifford' in saved.data()
