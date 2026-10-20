"""Independent mathematical and resource tests for real native templates."""
import numpy as np
import pytest
from quantumbridge import Circuit, StatevectorDevice, DensityMatrixDevice, templates as t
from quantumbridge.information import Operator
from quantumbridge.core import Parameter
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliY, PauliZ


def matrix(template):
    return Operator.from_circuit(template.to_circuit()).data


def rotation(axis, angle):
    p = {'X':np.array([[0,1],[1,0]]),'Y':np.array([[0,-1j],[1j,0]]),'Z':np.diag([1,-1])}[axis]
    return np.cos(angle/2)*np.eye(2)-1j*np.sin(angle/2)*p


def exponential(h, time):
    w,v = np.linalg.eigh(h)
    return (v*np.exp(1j*time*w))@v.conj().T


def test_angle_axes_full_complex_operator():
    for axis in ('X','Y','Z'):
        np.testing.assert_allclose(matrix(t.AngleEmbedding([.7],[0],rotation=axis)),rotation(axis,.7),atol=1e-12)


def test_angle_partial_features_leave_spectators_untouched():
    c = Circuit(3)
    t.angle_embedding(c,[.4],wires=[2,0],rotation='X')
    assert [(op.name,op.wires) for op in c.operations] == [('rx',(2,))]
    np.testing.assert_allclose(StatevectorDevice().statevector(c),np.kron([1,0,0,0],[np.cos(.2),-1j*np.sin(.2)]))


def test_legacy_angle_default_y_remains_compatible():
    c = t.angle_embedding(Circuit(1),[.3])
    np.testing.assert_allclose(Operator.from_circuit(c).data,rotation('Y',.3))


def test_angle_invalid_shape_axis_and_excess_features_fail_before_mutation():
    c = Circuit(2)
    for data,axis in (([[.1]],'X'),([.1,.2,.3],'Y'),([.1,float('nan')],'Z'),([.1],'phase')):
        with pytest.raises(ValueError): t.angle_embedding(c,data,rotation=axis)
        assert not c.operations


def test_template_wires_reject_duplicates_outside_and_boolean():
    for wires in ([0,0],[2],[True],[]):
        with pytest.raises(ValueError): t.angle_embedding(Circuit(2),[.3],wires=wires)


def test_named_template_wires_map_to_nonadjacent_physical_wires():
    template = t.AngleEmbedding([.2,.7],['left','right'],rotation='Y')
    c = template.apply(Circuit(4),wire_map={'left':3,'right':0})
    assert [op.wires for op in c.operations] == [(3,),(0,)]
    assert template.provenance['implementation'] == 'quantumbridge_native'


def test_template_decomposition_is_native_and_metadata_defensive():
    template = t.AngleEmbedding([.2,.7],[0,1])
    a,b = template.decomposition(),template.decomposition()
    a[0].metadata['modified'] = True
    assert 'modified' not in b[0].metadata
    np.testing.assert_allclose(Operator.from_circuit(template.apply(Circuit(2))).data,matrix(template))


def test_symbolic_template_preserves_native_parameter_expression():
    theta = Parameter('theta')
    c = t.AngleEmbedding([2*theta],[0],rotation='Y').to_circuit()
    assert c.parameters == (theta,)
    np.testing.assert_allclose(Operator.from_circuit(c.bind({theta:.3})).data,rotation('Y',.6))


def test_basis_integer_bitstring_vector_and_wire_order():
    for features in (5,'101',[1,0,1]):
        c = t.BasisEmbedding(features,[2,0,1]).apply(Circuit(3))
        expected = np.zeros(8);expected[3] = 1
        np.testing.assert_array_equal(StatevectorDevice().statevector(c),expected)


def test_basis_invalid_features_and_dimension():
    for data in (8,-1,'102',[1,0],[.5,0,1],[1j,0,1],True):
        with pytest.raises((ValueError,TypeError)):
            t.BasisEmbedding(data,[0,1,2])


def test_real_amplitude_vector_is_actually_prepared():
    state = np.array([1,2,-3,4],float);state /= np.linalg.norm(state)
    c = t.AmplitudeEmbedding(state,[0,1]).to_circuit()
    np.testing.assert_allclose(StatevectorDevice().statevector(c),state,atol=1e-12)
    assert c.operations and c.operations[0].metadata.get('matrix') is not None


def test_complex_amplitudes_preserve_relative_and_global_phase():
    state = np.array([1j,1,-2j,-.4],complex);state /= np.linalg.norm(state)
    np.testing.assert_allclose(StatevectorDevice().statevector(t.AmplitudeEmbedding(state,[0,1]).to_circuit()),state,atol=1e-12)


def test_amplitude_padding_precedes_normalization():
    c = t.AmplitudeEmbedding([2,1j],[0,1],pad_with=2j,normalize=True).to_circuit()
    expected = np.array([2,1j,2j,2j])/np.sqrt(13)
    np.testing.assert_allclose(StatevectorDevice().statevector(c),expected,atol=1e-12)


def test_amplitude_on_nonadjacent_permuted_wires_keeps_spectator_state():
    c = Circuit(3).x(1)
    t.AmplitudeEmbedding([1,2j,3,4j],[2,0],normalize=True).apply(c)
    expected = np.zeros(8,complex)
    for q,value in enumerate(np.array([1,2j,3,4j])/np.sqrt(30)):
        expected[((q&1)<<2)|2|(q>>1)] = value
    np.testing.assert_allclose(StatevectorDevice().statevector(c),expected,atol=1e-12)
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(c),np.outer(expected,expected.conj()),atol=1e-12)


def test_amplitude_invalid_norm_dimension_nan_and_zero_reject():
    for data,opts in (([1,1],{}),([1],{}),([0,0],{'normalize':True}),([float('nan'),0],{}),([[1,0]],{})):
        with pytest.raises(ValueError): t.AmplitudeEmbedding(data,[0],**opts)
    with pytest.raises(ValueError): t.AmplitudeEmbedding([1,0],[0,1],pad_with=float('nan'))


def test_amplitude_normalization_is_stable_for_extreme_finite_scale():
    for scale in (1e-300,1e300):
        c=t.AmplitudeEmbedding([scale,scale],[0],normalize=True).to_circuit()
        np.testing.assert_allclose(StatevectorDevice().statevector(c),np.ones(2)/np.sqrt(2),atol=1e-12)
    with pytest.raises(ValueError): t.AmplitudeEmbedding([1.000001,0],[0])


def test_amplitude_refuses_populated_or_measured_wires():
    template=t.AmplitudeEmbedding([1,0],[0])
    for c in (Circuit(1).h(0),Circuit(1,1).measure(0,0)):
        with pytest.raises(UnsupportedFeature): template.apply(c)


def test_amplitude_runtime_checks_initial_density_and_mps_subsystem():
    from quantumbridge import MatrixProductStateDevice
    c=t.AmplitudeEmbedding([1,1j],[0],normalize=True).to_circuit()
    for device in (DensityMatrixDevice(initial_state=[0,1]),MatrixProductStateDevice(initial_state=[0,1])):
        with pytest.raises(UnsupportedFeature,match='zero input'): device.probabilities(c)
        with pytest.raises(UnsupportedFeature): device.sample(c,shots=1)
    for device in (DensityMatrixDevice(initial_state=[1,0]),MatrixProductStateDevice(initial_state=[1,0])):
        assert device.probabilities(c)==pytest.approx({'0':.5,'1':.5})


def test_amplitude_runtime_precondition_survives_ir_and_dynamic_execution():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir import IRProgram
    c=t.AmplitudeEmbedding([1,0],[0]).to_circuit()
    c.operations.insert(0,Circuit(1).x(0).operations[0])
    restored=circuit_from_ir(IRProgram.from_json(c.to_ir().to_json()))
    with pytest.raises(UnsupportedFeature): StatevectorDevice().statevector(restored)
    from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
    with pytest.raises(UnsupportedFeature): DynamicExecutionEngine(StatevectorDevice(),restored).branches()


def test_amplitude_budget_rejects_before_state_synthesis(monkeypatch):
    import quantumbridge.qml.embeddings as module
    def forbidden(*args,**kwargs): raise AssertionError('Must reject before synthesis')
    monkeypatch.setattr(module,'amplitude_encoding',forbidden)
    with pytest.raises(MemoryError): t.AmplitudeEmbedding([1]*128,range(7))
    with pytest.raises(ValueError): t.AmplitudeEmbedding([1]*100,range(2))


def test_basic_one_two_three_four_wire_gate_order():
    for width,edges in ((1,[]),(2,[(0,1)]),(3,[(0,1),(1,2),(2,0)]),(4,[(0,1),(1,2),(2,3),(3,0)])):
        ops=t.BasicEntanglerLayers(np.zeros((1,width)),range(width)).decomposition()
        assert [op.name for op in ops[:width]] == ['rx']*width
        assert [op.wires for op in ops[width:]] == edges


def test_basic_configurable_rotation_and_multiple_layers():
    u=matrix(t.BasicEntanglerLayers([[.2],[.4]],[0],rotation='Y'))
    np.testing.assert_allclose(u,rotation('Y',.6),atol=1e-12)


def test_basic_shape_rejection_is_not_zip_truncation():
    for weights in ([.1,.2],[[.1]],[[.1,.2],[.3]],[[[.1,.2]]]):
        with pytest.raises(ValueError): t.BasicEntanglerLayers(weights,[0,1])


def test_strong_euler_order_is_rz_omega_ry_theta_rz_phi_matrix():
    phi,theta,omega=.2,.7,-.3
    expected=rotation('Z',omega)@rotation('Y',theta)@rotation('Z',phi)
    np.testing.assert_allclose(matrix(t.StronglyEntanglingLayers([[[phi,theta,omega]]],[0])),expected,atol=1e-12)


def test_strong_ranges_change_each_layer_and_custom_imprimitive():
    template=t.StronglyEntanglingLayers(np.zeros((2,3,3)),[0,1,2],imprimitive='cz')
    edges=[op.wires for op in template.decomposition() if op.name=='cz']
    assert edges == [(0,1),(1,2),(2,0),(0,2),(1,0),(2,1)]
    assert [op.wires for op in t.StronglyEntanglingLayers(np.zeros((1,3,3)),[0,1,2],ranges=[2]).decomposition() if op.name=='cx'] == edges[3:]


def test_strong_one_wire_has_no_entangler():
    assert [op.name for op in t.StronglyEntanglingLayers(np.zeros((2,1,3)),[0]).decomposition()] == ['rz','ry','rz']*2


def test_strong_bad_shapes_ranges_and_unsupported_entangler_reject():
    for data,options in ((np.zeros((2,3)),{}),(np.zeros((1,2,2)),{}),(np.zeros((1,2,3)),{'ranges':[0]}),
                         (np.zeros((1,2,3)),{'ranges':[2]}),(np.zeros((1,2,3)),{'ranges':[-1]})):
        with pytest.raises(ValueError): t.StronglyEntanglingLayers(data,[0,1],**options)
    with pytest.raises(NotImplementedError): t.StronglyEntanglingLayers(np.zeros((1,2,3)),[0,1],imprimitive='swap')


def test_iqp_operator_matches_independent_diagonal_feature_formula():
    features=np.array([.2,.4,-.6]);h=np.array([[1,1],[1,-1]])/np.sqrt(2)
    base=np.kron(np.kron(h,h),h)
    diagonal=[]
    for state in range(8):
        z=np.array([1-2*((state>>(2-q))&1) for q in range(3)])
        phase=features@z+sum(features[a]*features[b]*z[a]*z[b] for a in range(3) for b in range(a+1,3))
        diagonal.append(np.exp(-.5j*phase))
    layer=np.diag(diagonal)@base
    np.testing.assert_allclose(matrix(t.IQPEmbedding(features,range(3),n_repeats=2)),layer@layer,atol=1e-12)


def test_iqp_custom_pattern_and_wire_labels():
    template=t.IQPEmbedding([.2,.3,.4],['a','b','c'],pattern=[('c','a')])
    c=template.apply(Circuit(3),wire_map={'a':2,'b':0,'c':1})
    assert [op.wires for op in c.operations if op.name=='cx'] == [(1,2),(1,2)]


def test_iqp_invalid_pattern_repeats_and_shape():
    for options in ({'pattern':[(0,0)]},{'pattern':[(0,3)]},{'n_repeats':0},{'n_repeats':True}):
        with pytest.raises(ValueError): t.iqp_embedding(Circuit(3),[.1,.2,.3],**options)
    with pytest.raises(ValueError): t.IQPEmbedding([.1],[0,1])


def test_qft_complete_complex_fourier_matrix_for_one_through_four_wires():
    for width in (1,2,3,4):
        dim=1<<width;indices=np.arange(dim)
        expected=np.exp(2j*np.pi*np.outer(indices,indices)/dim)/np.sqrt(dim)
        np.testing.assert_allclose(matrix(t.QFT(range(width))),expected,atol=1e-12)


def test_qft_inverse_and_no_swaps_have_explicit_endian_semantics():
    u=matrix(t.QFT(range(3)))
    np.testing.assert_allclose(matrix(t.QFT(range(3),inverse=True)),u.conj().T,atol=1e-12)
    perm=[int(f'{q:03b}'[::-1],2) for q in range(8)]
    np.testing.assert_allclose(matrix(t.QFT(range(3),do_swaps=False)),u[perm],atol=1e-12)


def test_qft_selected_wire_operator_preserves_spectator():
    c=t.QFT([2,0]).apply(Circuit(3))
    state=StatevectorDevice().statevector(c)
    expected=np.zeros(8);expected[[0,1,4,5]]=.5
    np.testing.assert_allclose(state,expected,atol=1e-12)


def test_trotter_zero_time_identity_and_positive_time_convention():
    h=Hamiltonian([(.4,PauliX(0)),(.7,PauliZ(0))])
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,0,[0])),np.eye(2),atol=1e-12)
    expected=exponential(.4*np.array([[0,1],[1,0]]),.3)@exponential(.7*np.diag([1,-1]),.3)
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,.3,[0])),expected,atol=1e-12)


def test_commuting_trotter_is_exact_including_identity_global_phase():
    h=Hamiltonian([(.2,PauliString([])),(.3,PauliZ(0)),(-.7,PauliZ(1))])
    expected=exponential(.2*np.eye(4)+.3*np.diag([1,1,-1,-1])-.7*np.diag([1,-1,1,-1]),.6)
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,.6,[0,1],n=3)),expected,atol=1e-12)


def test_noncommuting_trotter_error_decreases_and_second_order_is_better():
    h=Hamiltonian([(.4,PauliX(0)),(.7,PauliZ(0))]);exact=exponential(np.array([[.7,.4],[.4,-.7]]),.8)
    errors=[np.linalg.norm(matrix(t.TrotterProduct(h,.8,[0],n=n))-exact) for n in (1,2,4,8)]
    assert all(a>b for a,b in zip(errors,errors[1:])) and errors[-1]<errors[0]/7
    assert np.linalg.norm(matrix(t.TrotterProduct(h,.8,[0],n=8,order=2))-exact)<errors[-1]/10


def test_second_order_trotter_negative_time_is_exact_adjoint_of_formula():
    h=Hamiltonian([(.3,PauliX(0)),(.2,PauliY(0)),(.7,PauliZ(0))])
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,-.5,[0],n=4,order=2)),matrix(t.TrotterProduct(h,.5,[0],n=4,order=2)).conj().T,atol=1e-12)


def test_trotter_pauli_string_basis_changes_and_nonadjacent_mapping():
    h=Hamiltonian([(.4,PauliString([(0,'Y'),(1,'X')]))])
    p=np.kron(np.array([[0,-1j],[1j,0]]),np.array([[0,1],[1,0]]))
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,.6,[4,1])),exponential(.4*p,.6),atol=1e-12)


def test_trotter_invalid_hamiltonian_formula_step_and_spin_wires():
    for h in ([],Hamiltonian([]),Hamiltonian([(float('inf'),PauliZ(0))]),Hamiltonian([(1,PauliZ(2))])):
        with pytest.raises((TypeError,ValueError)): t.TrotterProduct(h,.3,[0])
    h=Hamiltonian([(1,PauliZ(0))])
    with pytest.raises(ValueError): t.TrotterProduct(h,.3,[0],n=0)
    with pytest.raises(NotImplementedError): t.TrotterProduct(h,.3,[0],order=4)


def test_template_shape_wire_layer_operation_and_step_budgets():
    for construct in (
        lambda:t.AngleEmbedding([.1,.2],[0,1],limits=t.TemplateLimits(max_wires=1)),
        lambda:t.BasicEntanglerLayers([[.1],[.2]],[0],limits=t.TemplateLimits(max_layers=1)),
        lambda:t.StronglyEntanglingLayers(np.zeros((1,2,3)),[0,1],limits=t.TemplateLimits(max_parameter_elements=2)),
        lambda:t.QFT(range(3),limits=t.TemplateLimits(max_qft_wires=2)),
        lambda:t.QFT(range(3),limits=t.TemplateLimits(max_operations=2)),
        lambda:t.TrotterProduct(Hamiltonian([(1,PauliZ(0))]),.3,[0],n=3,limits=t.TemplateLimits(max_trotter_steps=2))):
        with pytest.raises(MemoryError): construct()


def test_invalid_limits_targets_and_native_template_mappings():
    with pytest.raises(ValueError): t.TemplateLimits(max_layers=0)
    with pytest.raises(TypeError): t.angle_embedding([], [.1])
    with pytest.raises(TypeError): t.angle_embedding(Circuit(1),[.1],limits={})
    with pytest.raises(ValueError): t.AngleEmbedding([.1,.2],['a','a'])
    with pytest.raises(ValueError): t.AngleEmbedding([.1],['a']).apply(Circuit(1))


def test_iterable_wires_patterns_and_ranges_have_finite_consumption():
    from itertools import count,repeat
    with pytest.raises(MemoryError): t.AngleEmbedding([.1],count(),limits=t.TemplateLimits(max_wires=2))
    with pytest.raises(MemoryError): t.IQPEmbedding([.1,.2],[0,1],pattern=repeat((0,1)),limits=t.TemplateLimits(max_operations=8))
    with pytest.raises(ValueError): t.StronglyEntanglingLayers(np.zeros((1,2,3)),[0,1],ranges=repeat(1))
    with pytest.raises(ValueError): t.IQPEmbedding([.1,.2],[0,1],pattern=[count()])


def test_qft_flags_rotation_and_normalization_control_types():
    with pytest.raises(TypeError): t.QFT([0],inverse=1)
    with pytest.raises(TypeError): t.AmplitudeEmbedding([1,0],[0],normalize=1)
    with pytest.raises(ValueError): t.AngleEmbedding([.1],[0],rotation='invalid')
    with pytest.raises(ValueError): t.AmplitudeEmbedding([1],[0],pad_with=[0,0])
    with pytest.raises(ValueError): t.basis_embedding(Circuit(1),[1j])


def test_trotter_accepts_native_qubit_hamiltonian_without_upstream_compute():
    from quantumbridge.chemistry import QubitHamiltonian
    h=QubitHamiltonian([(1.,PauliZ(0))])
    np.testing.assert_allclose(matrix(t.TrotterProduct(h,.3,[0])),np.diag(np.exp(.3j*np.array([1,-1]))),atol=1e-12)


def test_amplitude_ir_roundtrip_and_opaque_qasm_qpy_rejection():
    from quantumbridge.serialization import qpy_dumps,qpy_loads,qasm3_dumps,SerializationError
    c=t.AmplitudeEmbedding([1,1j,-.2,2],[0,1],normalize=True).to_circuit()
    from quantumbridge.ir import IRProgram
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    restored=circuit_from_ir(IRProgram.from_json(c.to_ir().to_json()))
    np.testing.assert_allclose(Operator.from_circuit(restored).data,Operator.from_circuit(c).data,atol=1e-12)
    with pytest.raises(SerializationError): qasm3_dumps(c)
    with pytest.raises(SerializationError): qpy_dumps(c)


def test_gate_templates_roundtrip_qasm2_qasm3_qpy_without_opaque_objects():
    from quantumbridge.serialization import qasm2_dumps,qasm2_loads,qasm3_dumps,qasm3_loads,qpy_dumps,qpy_loads
    c=t.StronglyEntanglingLayers(np.arange(12).reshape(2,2,3)/13,[0,1]).to_circuit()
    for restored in (qasm2_loads(qasm2_dumps(c)),qasm3_loads(qasm3_dumps(c)),qpy_loads(qpy_dumps(c))[0]):
        np.testing.assert_allclose(Operator.from_circuit(restored).data,Operator.from_circuit(c).data,atol=1e-12)
