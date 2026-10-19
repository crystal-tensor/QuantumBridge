import numpy as np
import pytest
from quantumbridge.noise import (QuantumError,pauli_error,depolarizing_error,mixed_unitary_error,
    coherent_unitary_error,reset_error,amplitude_damping_error,phase_damping_error,
    phase_amplitude_damping_error,thermal_relaxation_error,kraus_error,NoiseModel,ReadoutError)
from quantumbridge import Circuit,DensityMatrixDevice,MatrixProductStateDevice,StabilizerDevice,PauliX


def evolve(error,rho):
    expected=sum(k@rho@k.conj().T for k in error.kraus())
    # Also exercise the actual gate dispatcher, not just channel algebra.
    from quantumbridge.simulator import NativeAerSimulator
    width=error.num_qubits
    circuit=Circuit(width).set_density_matrix(rho).unitary(np.eye(1<<width),range(width)).save_density_matrix()
    model=NoiseModel().add_all_qubit_quantum_error(error,'unitary')
    actual=NativeAerSimulator('density_matrix',shots=None,noise_model=model).run(circuit).result().data()['density_matrix']
    if width>1:
        # The mathematical oracle uses little-endian qargs; native state axes are q0-first.
        order=np.arange(1<<width).reshape((2,)*width).transpose(tuple(reversed(range(width)))).reshape(-1)
        reference=sum(k@rho[np.ix_(order,order)]@k.conj().T for k in error.kraus())
        reference=reference[np.ix_(order,order)]
    else:reference=expected
    np.testing.assert_allclose(actual,reference,atol=1e-12)
    return expected


def test_amplitude_damping_excited_population_and_coherence():
    rho=np.array([[.5,.5],[.5,.5]],complex)
    result=evolve(amplitude_damping_error(.4,.2),rho)
    np.testing.assert_allclose(result,[[.62,.5*np.sqrt(.6)],[.5*np.sqrt(.6),.38]])


def test_phase_damping_is_sqrt_coherence_not_phase_flip():
    rho=np.full((2,2),.5,complex)
    np.testing.assert_allclose(evolve(phase_damping_error(.36),rho),[[.5,.4],[.4,.5]])


def test_phase_amplitude_damping_combines_distinct_physical_effects():
    result=evolve(phase_amplitude_damping_error(.2,.3),np.full((2,2),.5))
    np.testing.assert_allclose(result,[[.6,np.sqrt(.5)/2],[np.sqrt(.5)/2,.4]])


def test_depolarizing_uses_aer_lambda_convention_and_extended_domain():
    rho=np.diag([1.,0.])
    np.testing.assert_allclose(evolve(depolarizing_error(.6,1),rho),np.diag([.7,.3]))
    np.testing.assert_allclose(evolve(depolarizing_error(4/3,1),rho),np.diag([1/3,2/3]))


def test_two_qubit_depolarizing_is_full_mixed_not_independent_flip():
    rho=np.diag([1.,0.,0.,0.])
    np.testing.assert_allclose(evolve(depolarizing_error(1.,2),rho),np.eye(4)/4,atol=1e-12)


def test_pauli_and_mixed_unitary_channel():
    rho=np.diag([1.,0.]);x=np.array([[0,1],[1,0]])
    np.testing.assert_allclose(evolve(pauli_error([('X',.3),('I',.7)]),rho),np.diag([.7,.3]))
    np.testing.assert_allclose(evolve(mixed_unitary_error([(x,.3),(np.eye(2),.7)]),rho),np.diag([.7,.3]))


def test_error_compose_order_and_front_are_noncommuting():
    x=coherent_unitary_error([[0,1],[1,0]]);relax=amplitude_damping_error(.4)
    rho=np.diag([1.,0.])
    np.testing.assert_allclose(evolve(x.compose(relax),rho),np.diag([.4,.6]))
    np.testing.assert_allclose(evolve(x.compose(relax,front=True),rho),np.diag([0.,1.]))


def test_reset_error_handles_mixed_outputs():
    np.testing.assert_allclose(evolve(reset_error(.7,.3),np.full((2,2),.5)),np.diag([.7,.3]),atol=1e-12)


def test_thermal_population_and_t1_t2_coherence():
    t1,t2,time,p=2.,3.,.7,.15
    result=evolve(thermal_relaxation_error(t1,t2,time,p),np.full((2,2),.5))
    excited=p+(.5-p)*np.exp(-time/t1)
    np.testing.assert_allclose(result,[[1-excited,.5*np.exp(-time/t2)],[.5*np.exp(-time/t2),excited]],atol=1e-12)


def test_kraus_canonicalization_and_json_reconstruction():
    error=amplitude_damping_error(.27)
    canonical=kraus_error(error.kraus(),canonical_kraus=True)
    np.testing.assert_allclose(evolve(canonical,np.full((2,2),.5)),evolve(QuantumError.from_dict(error.to_dict()),np.full((2,2),.5)))


def test_error_tensor_and_expand_respect_matrix_order():
    x=coherent_unitary_error([[0,1],[1,0]]);identity=coherent_unitary_error(np.eye(2))
    np.testing.assert_allclose(x.tensor(identity).kraus()[0],np.kron([[0,1],[1,0]],np.eye(2)))
    np.testing.assert_allclose(x.expand(identity).kraus()[0],np.kron(np.eye(2),[[0,1],[1,0]]))


def test_invalid_channels_probabilities_and_thermal_domains_reject():
    for construct in (lambda:kraus_error([2*np.eye(2)]),lambda:pauli_error([('X',.2)]),lambda:depolarizing_error(1.5,1),lambda:thermal_relaxation_error(1,3,1),lambda:thermal_relaxation_error(0,1,1),lambda:amplitude_damping_error(float('nan')),lambda:phase_amplitude_damping_error(.7,.4)):
        with pytest.raises(ValueError):construct()


def test_gate_error_applied_after_every_execution_not_at_end():
    error=pauli_error([('X',1.)]);model=NoiseModel().add_all_qubit_quantum_error(error,['x'])
    device=DensityMatrixDevice(noise_model=model)
    np.testing.assert_allclose(device.run(Circuit(1).x(0)).density_matrix(),np.diag([1.,0.]))
    np.testing.assert_allclose(device.run(Circuit(1).x(0).x(0)).density_matrix(),np.diag([1.,0.]))


def test_specific_error_overrides_global_and_uses_public_qarg_order():
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('II',1.)]),'cx')
    model.add_quantum_error(pauli_error([('IX',1.)]),['cx'],[0,1])
    # IX acts on the first specified qarg, wire 0 in the physical circuit.
    np.testing.assert_allclose(DensityMatrixDevice(noise_model=model).run(Circuit(2).cx(0,1)).density_matrix(),np.diag([0.,0.,1.,0.]))


def test_gate_noise_operates_without_final_measurement_and_changes_x_expectation():
    model=NoiseModel().add_all_qubit_quantum_error(phase_damping_error(.36),'h')
    assert DensityMatrixDevice(noise_model=model).expectation(Circuit(1).h(0),PauliX(0))==pytest.approx(.8)


def test_noise_dispatch_reuses_mps_and_tableau_engines():
    model=NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'x')
    for device in (MatrixProductStateDevice(noise_model=model),StabilizerDevice(noise_model=model)):
        assert device.run_shots(Circuit(2,2).x(0).measure(0,0).measure(1,1),shots=4,seed=1).counts()=={'00':4}


def test_binding_validation_and_asymmetric_readout():
    model=NoiseModel().add_all_qubit_readout_error(ReadoutError([[0.,1.],[0.,1.]]))
    assert DensityMatrixDevice(noise_model=model).run_shots(Circuit(1,1).measure(0,0),shots=4).counts()=={'1':4}
    with pytest.raises(ValueError):NoiseModel().add_quantum_error(pauli_error([('XX',1.)]),'cx',[0])
    with pytest.raises(ValueError):NoiseModel().add_all_qubit_quantum_error(pauli_error([('X',1.)]),'save_state')
