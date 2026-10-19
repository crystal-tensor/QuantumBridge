# Public API oracles only; the native implementation imports neither SDK.
import numpy as np
import pytest
pytest.importorskip('qiskit_aer')
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer import noise as upstream
from qiskit.quantum_info import DensityMatrix,Statevector,SuperOp,Pauli
from quantumbridge import Circuit,PauliX,PauliY,PauliZ
from quantumbridge import noise as native
from quantumbridge.simulator import NativeAerSimulator


ERRORS=(
    ('pauli',lambda n:n.pauli_error([('X',.2),('Z',.3),('I',.5)])),
    ('depolarizing',lambda n:n.depolarizing_error(.37,2)),
    ('mixed_unitary',lambda n:n.mixed_unitary_error([(np.array([[0,1],[1,0]]),.23),(np.eye(2),.77)])),
    ('coherent_unitary',lambda n:n.coherent_unitary_error(np.diag([1,np.exp(.27j)]))),
    ('reset',lambda n:n.reset_error(.3,.2)),
    ('amplitude',lambda n:n.amplitude_damping_error(.31,.2)),
    ('phase',lambda n:n.phase_damping_error(.37)),
    ('phase_amplitude',lambda n:n.phase_amplitude_damping_error(.2,.3,.1)),
    ('thermal',lambda n:n.thermal_relaxation_error(2.,3.,.7,.13)),
    ('kraus',lambda n:n.kraus_error([np.diag([1.,np.sqrt(.7)]),np.array([[0,np.sqrt(.3)],[0,0]])])),
)


@pytest.mark.parametrize('name,builder',ERRORS)
def test_public_quantum_error_constructor_channel(name,builder):
    ours=builder(native).to_quantumchannel().to_superop().data
    expected=SuperOp(builder(upstream).to_quantumchannel()).data
    np.testing.assert_allclose(ours,expected,atol=2e-12)


def result(circuit,method='statevector',shots=None,**options):
    return NativeAerSimulator(method,shots=shots,**options).run(circuit).result().data()


def sdk_result(circuit,method='statevector',shots=16,**options):
    return AerSimulator(method=method,**options).run(circuit,shots=shots,seed_simulator=7).result().data()


def test_public_error_composition_order_and_tensor():
    for front in (False,True):
        ours=native.coherent_unitary_error([[0,1],[1,0]]).compose(native.amplitude_damping_error(.3),front=front)
        expected=upstream.coherent_unitary_error([[0,1],[1,0]]).compose(upstream.amplitude_damping_error(.3),front=front)
        np.testing.assert_allclose(ours.to_quantumchannel().to_superop().data,SuperOp(expected.to_quantumchannel()).data,atol=1e-12)


def test_public_intermediate_statevector_phase_and_multiple_labels():
    c=Circuit(1).h(0).save_statevector(label='h').rz(.3,0).save_statevector(label='rz')
    q=QuantumCircuit(1);q.h(0);q.save_statevector(label='h');q.rz(.3,0);q.save_statevector(label='rz')
    ours,expected=result(c),sdk_result(q)
    for key in ('h','rz'):np.testing.assert_allclose(ours[key],np.asarray(expected[key]),atol=1e-12)


def test_public_bell_vector_phase_and_wire_order():
    c=Circuit(2).h(0).cx(0,1).phase(.31,0).save_statevector()
    q=QuantumCircuit(2);q.h(0);q.cx(0,1);q.p(.31,0);q.save_statevector()
    expected=Statevector(sdk_result(q)['statevector']).reverse_qargs().data
    np.testing.assert_allclose(result(c)['statevector'],expected,atol=1e-12)


def test_public_set_statevector_replaces_prior_state():
    c=Circuit(1).h(0).set_statevector([0,1j]).rx(.3,0).save_statevector()
    q=QuantumCircuit(1);q.h(0);q.set_statevector([0,1j]);q.rx(.3,0);q.save_statevector()
    np.testing.assert_allclose(result(c)['statevector'],np.asarray(sdk_result(q)['statevector']),atol=1e-12)


def test_public_set_mixed_density_and_evolution():
    c=Circuit(1).x(0).set_density_matrix(np.diag([.3,.7])).h(0).save_density_matrix()
    q=QuantumCircuit(1);q.x(0);q.set_density_matrix(np.diag([.3,.7]));q.h(0);q.save_density_matrix()
    np.testing.assert_allclose(result(c,'density_matrix')['density_matrix'],np.asarray(sdk_result(q,'density_matrix')['density_matrix']),atol=1e-12)


def test_public_attached_dephasing_without_counts():
    model=native.NoiseModel().add_all_qubit_quantum_error(native.phase_damping_error(.36),'h')
    reference=upstream.NoiseModel();reference.add_all_qubit_quantum_error(upstream.phase_damping_error(.36),'h')
    c=Circuit(1).h(0).save_density_matrix();q=QuantumCircuit(1);q.h(0);q.save_density_matrix()
    np.testing.assert_allclose(result(c,'density_matrix',noise_model=model)['density_matrix'],np.asarray(sdk_result(q,'density_matrix',noise_model=reference)['density_matrix']),atol=1e-12)


def test_public_specific_quantum_error_qarg_order():
    model=native.NoiseModel().add_quantum_error(native.pauli_error([('IX',1.)]),['cx'],[0,1])
    reference=upstream.NoiseModel();reference.add_quantum_error(upstream.pauli_error([('IX',1.)]),['cx'],[0,1])
    c=Circuit(2).cx(0,1).save_density_matrix();q=QuantumCircuit(2);q.cx(0,1);q.save_density_matrix()
    expected=DensityMatrix(sdk_result(q,'density_matrix',noise_model=reference)['density_matrix']).reverse_qargs().data
    np.testing.assert_allclose(result(c,'density_matrix',noise_model=model)['density_matrix'],expected,atol=1e-12)


def test_public_expectation_variance_and_noisy_xy():
    model=native.NoiseModel().add_all_qubit_quantum_error(native.amplitude_damping_error(.3),'h')
    reference=upstream.NoiseModel();reference.add_all_qubit_quantum_error(upstream.amplitude_damping_error(.3),'h')
    c=Circuit(1).h(0).save_expectation_value_variance(PauliZ(0),label='z').save_expectation_value(PauliX(0),label='x')
    q=QuantumCircuit(1);q.h(0);q.save_expectation_value_variance(Pauli('Z'),[0],label='z');q.save_expectation_value(Pauli('X'),[0],label='x')
    c.s(0).save_expectation_value(PauliY(0),label='y');q.s(0);q.save_expectation_value(Pauli('Y'),[0],label='y')
    ours=result(c,'density_matrix',noise_model=model);expected=sdk_result(q,'density_matrix',noise_model=reference)
    np.testing.assert_allclose(ours['z'],expected['z'],atol=1e-12);assert ours['x']==pytest.approx(expected['x'],abs=1e-12)
    assert ours['y']==pytest.approx(expected['y'],abs=1e-12)


def test_public_conditional_pershot_state_tracks_collapse():
    c=Circuit(1,1).h(0).measure(0,0).save_statevector(pershot=True,conditional=True)
    q=QuantumCircuit(1,1);q.h(0);q.measure(0,0);q.save_statevector(pershot=True,conditional=True)
    ours=result(c,shots=32,seed_simulator=7)['statevector'];expected=sdk_result(q,shots=32)['statevector']
    assert set(ours)==set(expected)=={'0x0','0x1'}
    for group in ours:
        for array in ours[group]+list(expected[group]):np.testing.assert_allclose(np.asarray(array),[1,0] if group=='0x0' else [0,1],atol=1e-12)


def test_public_mps_probabilities_and_subsystem_density():
    c=Circuit(3).h(0).cx(0,2).x(1).save_probabilities().save_density_matrix([0,2],label='rho')
    q=QuantumCircuit(3);q.h(0);q.cx(0,2);q.x(1);q.save_probabilities();q.save_density_matrix([0,2],label='rho')
    ours=result(c,'matrix_product_state');expected=sdk_result(q,'matrix_product_state')
    np.testing.assert_allclose(ours['probabilities'],np.asarray(expected['probabilities']).reshape(2,2,2).transpose(2,1,0).reshape(-1),atol=1e-12)
    np.testing.assert_allclose(ours['rho'],DensityMatrix(expected['rho']).reverse_qargs().data,atol=1e-12)


def test_public_stabilizer_clifford_observation():
    c=Circuit(2).h(0).cx(0,1).save_expectation_value(PauliZ(0),label='z')
    q=QuantumCircuit(2);q.h(0);q.cx(0,1);q.save_expectation_value(Pauli('Z'),[0],label='z')
    assert result(c,'stabilizer')['z']==pytest.approx(sdk_result(q,'stabilizer')['z'],abs=1e-12)


def test_public_unitary_method_exact_global_phase():
    c=Circuit(1).h(0).ry(.27,0);c.global_phase=.19;c.save_unitary()
    q=QuantumCircuit(1,global_phase=.19);q.h(0);q.ry(.27,0);q.save_unitary()
    np.testing.assert_allclose(result(c,'unitary')['unitary'],np.asarray(sdk_result(q,'unitary')['unitary']),atol=1e-12)


def test_public_superop_with_channel_and_reset():
    c=Circuit(1).h(0).reset(0).save_superop();q=QuantumCircuit(1);q.h(0);q.reset(0);q.save_superop()
    np.testing.assert_allclose(result(c,'superop')['superop'],np.asarray(sdk_result(q,'superop')['superop']),atol=1e-12)


def test_public_readout_feedback_uses_classical_record_not_true_collapse():
    model=native.NoiseModel().add_readout_error(native.ReadoutError([[0,1],[0,1]]),[0])
    reference=upstream.NoiseModel();reference.add_readout_error(upstream.ReadoutError([[0,1],[0,1]]),[0])
    c=Circuit(2,1).measure(0,0).if_test((0,1),Circuit(2,1).x(1)).save_density_matrix()
    q=QuantumCircuit(2,1);q.measure(0,0)
    with q.if_test((q.clbits[0],True)):q.x(1)
    q.save_density_matrix()
    expected=DensityMatrix(sdk_result(q,'density_matrix',noise_model=reference)['density_matrix']).reverse_qargs().data
    np.testing.assert_allclose(result(c,'density_matrix',noise_model=model)['density_matrix'],expected,atol=1e-12)
