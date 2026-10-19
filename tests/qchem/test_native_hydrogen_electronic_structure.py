from math import pi, sqrt, exp
import numpy as np
import pytest
from quantumbridge import Circuit, qchem
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.chemistry.basis import build_basis
from quantumbridge.chemistry.gaussian_integrals import (
    ContractedSGaussian, primitive_normalization, boys0, primitive_overlap,
    primitive_kinetic, primitive_attraction, primitive_repulsion, overlap,
)


def molecule(distance=1.4):
    return qchem.Molecule(['H', 'H'], [(0, 0, 0), (0, 0, distance)], unit='bohr')


@pytest.fixture(scope='module')
def problem():
    return qchem.molecular_hamiltonian_native(molecule())


def test_s_primitive_normalization_from_analytic_integral():
    alpha = .73
    assert primitive_normalization(alpha) ** 2 * (pi / (2 * alpha)) ** 1.5 == pytest.approx(1.)


def test_displaced_primitive_overlap_matches_gaussian_product_theorem():
    a, b = .7, 1.2
    expected = primitive_normalization(a) * primitive_normalization(b) * (pi / (a+b)) ** 1.5 * exp(-a*b/(a+b)*4)
    assert primitive_overlap(a, b, (0, 0, 0), (0, 0, 2)) == pytest.approx(expected)


def test_primitive_kinetic_same_center_has_correct_dimensions():
    assert primitive_kinetic(.8, .8, (0, 0, 0), (0, 0, 0)) == pytest.approx(1.2)


def test_nuclear_attraction_at_center_is_analytic_not_fitted():
    alpha = .8
    expected = -2 * primitive_normalization(alpha) ** 2 * pi / (2 * alpha)
    assert primitive_attraction(alpha, alpha, (0, 0, 0), (0, 0, 0), (0, 0, 0)) == pytest.approx(expected)


def test_equal_center_repulsion_matches_coulomb_self_integral():
    alpha = .8
    assert primitive_repulsion(alpha, alpha, alpha, alpha, *((0, 0, 0),) * 4) == pytest.approx(2 * sqrt(alpha/pi))


def test_boys_zero_series_and_general_values_match_independent_quadrature():
    nodes, weights = np.polynomial.legendre.leggauss(100)
    for value in (0., 1e-12, 1e-6, .7, 30.):
        expected = np.dot(weights/2, np.exp(-value*((nodes+1)/2)**2))
        assert boys0(value) == pytest.approx(expected, abs=2e-14)


def test_contraction_is_normalized_even_with_rescaled_input_coefficients():
    basis = ContractedSGaussian((1, 2, 3), (.2, .8), (2., 4.))
    assert overlap(basis, basis) == pytest.approx(1., abs=1e-12)


def test_ao_integrals_are_translation_and_rotation_invariant():
    a = qchem.molecular_integrals(molecule())
    b = qchem.molecular_integrals(qchem.Molecule(['H', 'H'], [(2, 3, 4), (3.4, 3, 4)], unit='bohr'))
    np.testing.assert_allclose(a.one_body, b.one_body, atol=1e-12)
    np.testing.assert_allclose(a.two_body, b.two_body, atol=1e-12)


def test_electron_repulsion_tensor_has_eightfold_chemist_symmetry(problem):
    eri = problem.scf_result.integrals.two_body
    for axes in ((1, 0, 2, 3), (0, 1, 3, 2), (2, 3, 0, 1)):
        np.testing.assert_allclose(eri, eri.transpose(axes), atol=1e-12)


def test_core_integrals_are_finite_hermitian_and_sum_kinetic_attraction(problem):
    ao = problem.scf_result.integrals
    np.testing.assert_allclose(ao.one_body, ao.kinetic + ao.nuclear_attraction)
    for matrix in (ao.overlap, ao.kinetic, ao.nuclear_attraction, ao.one_body):
        assert np.all(np.isfinite(matrix))
        np.testing.assert_allclose(matrix, matrix.T)


def test_nuclear_repulsion_and_geometry_conversion_have_explicit_units():
    from quantumbridge.chemistry.molecule import BOHR_TO_ANGSTROM
    bohr = qchem.molecular_integrals(molecule())
    angstrom = qchem.molecular_integrals(qchem.Molecule(['H', 'H'], [(0, 0, 0), (0, 0, 1.4*BOHR_TO_ANGSTROM)]))
    assert bohr.nuclear_repulsion_energy == pytest.approx(1/1.4)
    np.testing.assert_allclose(bohr.one_body, angstrom.one_body, atol=1e-12)


def test_molecule_records_atomic_numbers_electrons_and_alias():
    m = qchem.Molecule(symbols=['H', 'H'], coordinates=[(0, 0, 0), (0, 0, 1)])
    assert m.symbols == ('H', 'H') and m.atomic_numbers == (1, 1) and m.n_electrons == 2
    assert m.nuclear_charges == (1, 1)


def test_invalid_geometry_charge_spin_element_and_unit_are_explicit_errors():
    for fields in ({'atoms':['Xx','H']}, {'coordinates':[(0,0,0),(0,float('nan'),1)]}, {'charge':True},
                   {'charge':1}, {'spin':1}, {'multiplicity':0}, {'unit':'meters'}):
        arguments = dict(atoms=['H','H'], coordinates=[(0,0,0),(0,0,1)])
        with pytest.raises((ValueError, TypeError)):
            qchem.Molecule(**{**arguments, **fields})


def test_xyz_truncation_is_not_silently_accepted():
    with pytest.raises(ValueError, match='count'):
        qchem.Molecule.from_xyz('2\ncomment\nH 0 0 0\n')


def test_unsupported_basis_and_element_do_not_load_an_upstream_backend():
    with pytest.raises(NotImplementedError):
        build_basis(qchem.Molecule(['He'], [(0,0,0)]))
    with pytest.raises(NotImplementedError):
        build_basis(qchem.Molecule(['H','H'], [(0,0,0),(0,0,1)], basis='6-31g'))


def test_nuclear_collision_and_linear_dependence_reject():
    with pytest.raises(ValueError, match='separation'):
        qchem.molecular_integrals(molecule(0.))
    with pytest.raises(ValueError, match='linearly dependent'):
        qchem.run_restricted_hartree_fock(molecule(1e-5))


def test_rhf_density_occupations_and_orbitals_are_self_consistent(problem):
    r = problem.scf_result
    np.testing.assert_allclose(r.coefficients.T @ r.integrals.overlap @ r.coefficients, np.eye(2), atol=1e-12)
    np.testing.assert_allclose(r.density, 2*r.coefficients[:, :1] @ r.coefficients[:, :1].T, atol=1e-12)
    assert np.trace(r.density @ r.integrals.overlap) == pytest.approx(2)
    np.testing.assert_allclose(r.occupations, [2, 0])
    assert r.history[-1]['commutator_residual'] < 1e-9 and len(r.history) >= 2


def test_rhf_energy_uses_density_fock_and_nuclear_once(problem):
    r = problem.scf_result
    expected = .5*np.sum(r.density*(r.integrals.one_body+r.fock))
    assert r.electronic_energy == pytest.approx(expected)
    assert r.total_energy == pytest.approx(expected+1/1.4)


def test_scf_nonconvergence_is_failure_with_iteration_evidence():
    with pytest.raises(qchem.SCFConvergenceError) as error:
        qchem.run_restricted_hartree_fock(molecule(), max_iterations=1)
    assert len(error.value.history) == 1


def test_scf_damping_converges_to_same_variational_energy(problem):
    result = qchem.run_restricted_hartree_fock(molecule(), damping=.25)
    assert len(result.history) > len(problem.scf_result.history)
    assert result.total_energy == pytest.approx(problem.scf_result.total_energy, abs=1e-9)
    assert np.trace(result.density @ result.integrals.overlap) == pytest.approx(2,abs=1e-12)


def test_invalid_scf_controls_and_open_shell_reject():
    for options in ({'max_iterations':0}, {'energy_tolerance':0}, {'density_tolerance':float('nan')}, {'damping':1}):
        with pytest.raises(ValueError):
            qchem.run_restricted_hartree_fock(molecule(), **options)
    with pytest.raises(NotImplementedError):
        qchem.run_restricted_hartree_fock(qchem.Molecule(['H'], [(0,0,0)], multiplicity=2))


def test_computed_molecular_integrals_depend_on_geometry():
    a, b = qchem.molecular_integrals(molecule(1.4)), qchem.molecular_integrals(molecule(2.))
    assert np.linalg.norm(a.overlap-b.overlap) > .1
    assert np.linalg.norm(a.two_body-b.two_body) > .1
    assert a.nuclear_repulsion_energy != b.nuclear_repulsion_energy


def test_molecular_hamiltonian_is_four_untapered_spin_orbitals(problem):
    assert problem.num_qubits == 4 and problem.n_electrons == 2
    assert problem.metadata['nuclear_included_once'] and not problem.metadata['upstream_required']
    assert problem.to_dict()['metadata']['eri_convention'] == 'chemist (pq|rs)'


def test_generated_fermionic_and_pauli_operators_match_and_conserve_particles(problem):
    matrix = problem.hamiltonian.matrix()
    np.testing.assert_allclose(matrix, problem.fermionic_hamiltonian.to_matrix(), atol=1e-12)
    np.testing.assert_allclose(matrix, matrix.conj().T, atol=1e-12)
    number = np.diag([state.bit_count() for state in range(16)])
    np.testing.assert_allclose(matrix @ number, number @ matrix, atol=1e-12)


def test_hf_reference_expectation_matches_scf_total_energy(problem):
    matrix = problem.hamiltonian.matrix()
    assert matrix[12,12].real == pytest.approx(problem.scf_result.total_energy, abs=1e-10)
    assert problem.exact_ground_energy() < problem.scf_result.total_energy - .01


def test_geometry_driven_potential_curve_has_distinct_physical_energies():
    energies = [qchem.molecular_hamiltonian_native(molecule(r)).exact_ground_energy() for r in (.8,1.4,3.)]
    assert energies[1] < min(energies[0],energies[2])
    assert len(set(round(value,8) for value in energies)) == 3


def test_scf_results_cannot_be_reused_for_another_geometry(problem):
    with pytest.raises(ValueError, match='this molecule'):
        qchem.electron_integrals(molecule(2.), problem.scf_result)


def test_hf_state_excitations_and_custom_wire_mapping():
    np.testing.assert_array_equal(qchem.hf_state(2,4), [1,1,0,0])
    singles, doubles = qchem.excitations(2,4)
    assert singles == [[0,2],[1,3]] and doubles == [[0,1,2,3]]
    s, d = qchem.excitations_to_wires(singles,doubles,['a','b','c','d'])
    assert s == [['a','b','c'],['b','c','d']] and d == [[['a','b'],['c','d']]]


def test_excitation_circuit_is_exact_exponential_of_fermionic_generator():
    from quantumbridge.chemistry import FermionicOp
    a = FermionicOp({'+_2 +_3 -_1 -_0':1},4).to_matrix()
    generator = 1j*(a-a.conj().T)
    values, vectors = np.linalg.eigh(generator)
    expected = (vectors*np.exp(-.5j*.37*values)) @ vectors.conj().T
    c = qchem.apply_fermionic_excitation(Circuit(4),.37,[0,1,2,3])
    np.testing.assert_allclose(Operator.from_circuit(c).data,expected,atol=1e-12)


def test_fixed_generated_hamiltonian_has_real_native_shift_and_adjoint_gradients(problem):
    def program(t,theta):
        t.x(0);t.x(1);qchem.apply_fermionic_excitation(t,theta,[0,1,2,3])
        return t.expval(problem.hamiltonian.to_quantumbridge())
    node = QNode(program,4)
    expected = (node(.31+1e-6)-node(.31-1e-6))/2e-6
    for method in ('parameter-shift','adjoint'):
        assert node.gradient(.31,method=method) == pytest.approx(expected,abs=1e-8)


def test_vqe_optimization_changes_state_and_reaches_generated_exact_ground(problem):
    def program(t,theta):
        t.x(0);t.x(1);qchem.apply_fermionic_excitation(t,theta,[0,1,2,3])
        return t.expval(problem.hamiltonian.to_quantumbridge())
    node, theta = QNode(program,4), 0.
    initial = node(theta)
    for _ in range(70):
        theta -= .4*node.gradient(theta,method='adjoint')
    assert node(theta) < initial-.01
    assert node(theta) == pytest.approx(problem.exact_ground_energy(),abs=1e-7)


def test_basis_tensor_scf_and_hamiltonian_resource_budgets():
    for limits in (qchem.QChemLimits(max_atoms=1), qchem.QChemLimits(max_basis_functions=1),
                   qchem.QChemLimits(max_spin_orbitals=2),qchem.QChemLimits(max_integral_tensor_bytes=1),
                   qchem.QChemLimits(max_hamiltonian_terms=1),qchem.QChemLimits(max_scf_iterations=1)):
        with pytest.raises(MemoryError):
            qchem.molecular_hamiltonian_native(molecule(),limits=limits)


def test_bad_gaussian_boys_and_contraction_inputs_are_not_silent_nan():
    for value in (-1.,float('nan')):
        with pytest.raises(ValueError):
            boys0(value)
    with pytest.raises(ValueError):
        primitive_normalization(0.)
    with pytest.raises(ValueError):
        ContractedSGaussian((0,0,0),(.3,), (0.,))
    with pytest.raises(ValueError):
        ContractedSGaussian((0,0,float('inf')), (.3,), (1.,))


def test_invalid_hf_excitation_and_mapping_requests_reject():
    with pytest.raises(ValueError):
        qchem.hf_state(5,4)
    with pytest.raises(NotImplementedError):
        qchem.hf_state(2,4,basis='parity')
    with pytest.raises(ValueError):
        qchem.excitations_to_wires([[2,1]],[])
    with pytest.raises(ValueError):
        qchem.apply_fermionic_excitation(Circuit(4),.2,[0,1,1,3])
    with pytest.raises(NotImplementedError):
        qchem.molecular_hamiltonian_native(molecule(),mapping='bravyi_kitaev')


def test_single_excitation_has_correct_occupation_amplitudes_and_number():
    from quantumbridge import StatevectorDevice
    c = Circuit(3).x(0)
    qchem.apply_fermionic_excitation(c,.4,[0,2])
    state = StatevectorDevice().statevector(c)
    expected = np.zeros(8); expected[4],expected[1] = np.cos(.2),np.sin(.2)
    np.testing.assert_allclose(state,expected,atol=1e-12)


def test_geometry_energy_finite_difference_is_consistent_not_claimed_autodiff():
    def energy(r):
        return qchem.molecular_hamiltonian_native(molecule(r)).exact_ground_energy()
    a = (energy(1.4+.001)-energy(1.4-.001))/.002
    b = (energy(1.4+.0005)-energy(1.4-.0005))/.001
    assert a == pytest.approx(b,abs=1e-6)
    assert abs(a) > .001


def test_chemistry_invalid_limits_types_and_replacement_orbitals(problem):
    from dataclasses import replace
    with pytest.raises(ValueError):
        qchem.QChemLimits(max_atoms=0)
    with pytest.raises(TypeError):
        build_basis(molecule(),limits={})
    with pytest.raises(TypeError):
        qchem.run_restricted_hartree_fock(molecule(),limits={})
    with pytest.raises(TypeError):
        qchem.build_fermionic_hamiltonian(molecule(),problem.scf_result,limits={})
    with pytest.raises(TypeError):
        qchem.electron_integrals(molecule(),problem.scf_result,limits={})
    with pytest.raises(TypeError):
        qchem.molecular_hamiltonian_native(molecule(),scf_options=[])
    with pytest.raises(ValueError):
        qchem.electron_integrals(molecule(),replace(problem.scf_result,coefficients=np.zeros((2,2))))
    assert qchem.electron_integrals(molecule()).one_body.shape == (2,2)


def test_reused_scf_respects_limits_before_allocating_mo_tensor(problem, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('MO tensor contraction must not start after budget failure')
    monkeypatch.setattr(np, 'einsum', forbidden)
    for limits in (qchem.QChemLimits(max_atoms=1), qchem.QChemLimits(max_basis_functions=1),
                   qchem.QChemLimits(max_spin_orbitals=2), qchem.QChemLimits(max_integral_tensor_bytes=1)):
        with pytest.raises(MemoryError):
            qchem.electron_integrals(molecule(),problem.scf_result,limits=limits)


def test_molecule_and_excitation_invalid_aliases_and_shapes():
    with pytest.raises(ValueError):
        qchem.Molecule(['H','H'],[(0,0,0),(0,0,1)],symbols=['H','H'])
    with pytest.raises(ValueError):
        qchem.Molecule(['H','H'],[(0,0,0),(0,0,1j)])
    with pytest.raises(ValueError):
        qchem.excitations(2,4,delta_sz=.5)
    with pytest.raises(ValueError):
        qchem.excitations_to_wires([],[[0,1,1,2]])
    with pytest.raises(ValueError):
        qchem.excitations_to_wires([[0,2]],[],wires=['a'])


def test_torch_backward_through_generated_hamiltonian_excitation(problem):
    torch = pytest.importorskip('torch')
    def program(t,x):
        t.x(0);t.x(1);qchem.apply_fermionic_excitation(t,x*x,[0,1,2,3])
        return t.expval(problem.hamiltonian.to_quantumbridge())
    node = QNode(program,4,interface='torch')
    x = torch.tensor(.3,dtype=torch.float64,requires_grad=True)
    node(x).backward()
    reference = QNode(program,4).gradient(.3)
    assert x.grad.item() == pytest.approx(reference,abs=1e-10)


def test_autograd_through_generated_hamiltonian_excitation(problem):
    autograd = pytest.importorskip('autograd')
    def program(t,x):
        t.x(0);t.x(1);qchem.apply_fermionic_excitation(t,x*x,[0,1,2,3])
        return t.expval(problem.hamiltonian.to_quantumbridge())
    reference = QNode(program,4).gradient(.3)
    node = QNode(program,4,interface='autograd')
    assert autograd.grad(node)(.3) == pytest.approx(reference,abs=1e-10)
