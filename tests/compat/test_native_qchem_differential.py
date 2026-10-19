"""Independent native chemistry versus installed public APIs; no SDK source reads."""
import numpy as np
import pytest
qml = pytest.importorskip('pennylane')
from quantumbridge import qchem
from quantumbridge.chemistry import FermionicOp, JordanWignerMapper


@pytest.fixture(scope='module')
def pair():
    geometry = np.array([[0.,0.,0.],[0.,0.,1.4]])
    native = qchem.Molecule(['H','H'],geometry,unit='bohr')
    public = qml.qchem.Molecule(['H','H'],geometry,unit='bohr',basis_name='sto-3g')
    return qchem.molecular_hamiltonian_native(native), public


def test_public_molecule_electron_and_nuclear_properties(pair):
    native, public = pair
    assert native.n_electrons == public.n_electrons
    np.testing.assert_array_equal(native.molecule.nuclear_charges,public.nuclear_charges)
    np.testing.assert_allclose(native.molecule.coordinates_bohr,public.coordinates)


def test_public_hf_occupation_state():
    np.testing.assert_array_equal(qchem.hf_state(2,6),qml.qchem.hf_state(2,6))


def test_public_spin_conserving_single_double_excitations():
    assert qchem.excitations(2,6) == qml.qchem.excitations(2,6)


def test_public_excitation_to_custom_wires():
    singles, doubles = qchem.excitations(2,4)
    assert qchem.excitations_to_wires(singles,doubles,['a','b','c','d']) == qml.qchem.excitations_to_wires(singles,doubles,['a','b','c','d'])


def test_public_overlap_matrix(pair):
    native, public = pair
    np.testing.assert_allclose(native.scf_result.integrals.overlap,qml.qchem.overlap_matrix(public.basis_set)(),atol=1e-8,rtol=0)


def test_public_kinetic_matrix(pair):
    native, public = pair
    np.testing.assert_allclose(native.scf_result.integrals.kinetic,qml.qchem.kinetic_matrix(public.basis_set)(),atol=1e-8,rtol=0)


def test_public_nuclear_attraction_matrix(pair):
    native, public = pair
    expected = qml.qchem.attraction_matrix(public.basis_set,public.nuclear_charges,public.coordinates)()
    np.testing.assert_allclose(native.scf_result.integrals.nuclear_attraction,expected,atol=1e-8,rtol=0)


def test_public_electron_repulsion_tensor(pair):
    native, public = pair
    np.testing.assert_allclose(native.scf_result.integrals.two_body,qml.qchem.repulsion_tensor(public.basis_set)(),atol=1e-8,rtol=0)


def test_public_geometry_generated_pauli_hamiltonian(pair):
    native, public = pair
    expected, width = qml.qchem.molecular_hamiltonian(public)
    assert width == native.num_qubits == 4
    np.testing.assert_allclose(native.hamiltonian.matrix(),qml.matrix(expected,wire_order=range(width)),atol=1e-8,rtol=0)


def test_public_stretched_geometry_exact_energy_is_not_fixed_reference():
    geometry = np.array([[0.,0.,0.],[0.,0.,2.5]])
    native = qchem.molecular_hamiltonian_native(qchem.Molecule(['H','H'],geometry,unit='bohr'))
    public = qml.qchem.Molecule(['H','H'],geometry,unit='bohr',basis_name='sto-3g')
    operator, width = qml.qchem.molecular_hamiltonian(public)
    assert native.exact_ground_energy() == pytest.approx(np.linalg.eigvalsh(qml.matrix(operator,wire_order=range(width)))[0],abs=1e-8)


def _public_fermion(native):
    return qml.FermiSentence({qml.FermiWord({(position,int(token[2:])):token[0] for position,token in enumerate(label.split())}):coefficient for label,coefficient in native.terms})


def test_public_general_complex_jordan_wigner_with_spectator_modes():
    native = FermionicOp({'+_0 -_2':.3+.2j,'+_2 -_0':.3-.2j,'+_1':.4j},3)
    expected = qml.matrix(qml.jordan_wigner(_public_fermion(native)),wire_order=range(3))
    np.testing.assert_allclose(JordanWignerMapper().map(native).matrix(),expected,atol=1e-12,rtol=0)


def test_public_unordered_word_matches_native_car_normal_ordering():
    native = FermionicOp({'-_0 -_1 +_1 +_0':.3j},2)
    expected = qml.jordan_wigner(_public_fermion(native))
    np.testing.assert_allclose(native.normal_ordered().to_matrix(),qml.matrix(expected,wire_order=[0,1]),atol=1e-12,rtol=0)


@pytest.fixture(scope='module')
def pyscf_pair():
    pyscf = pytest.importorskip('pyscf')
    pyscf.lib.num_threads(1)
    molecule = pyscf.gto.M(atom='H 0 0 0; H 0 0 1.4',basis='sto-3g',unit='Bohr',verbose=0)
    rhf = pyscf.scf.RHF(molecule)
    rhf.conv_tol = 1e-12
    rhf.kernel()
    return pyscf, molecule, rhf


def test_pyscf_independent_ao_one_and_two_electron_integrals(pair,pyscf_pair):
    native, _ = pair
    _, public, _ = pyscf_pair
    for integral, actual in (('int1e_ovlp',native.scf_result.integrals.overlap),('int1e_kin',native.scf_result.integrals.kinetic),
                             ('int1e_nuc',native.scf_result.integrals.nuclear_attraction),('int2e',native.scf_result.integrals.two_body)):
        np.testing.assert_allclose(actual,public.intor(integral),atol=1e-8,rtol=0)


def test_pyscf_independent_rhf_total_energy(pair,pyscf_pair):
    native, _ = pair
    _, _, public = pyscf_pair
    assert native.scf_result.total_energy == pytest.approx(public.e_tot,abs=1e-8)


def test_pyscf_independent_full_configuration_interaction_energy(pair,pyscf_pair):
    native, _ = pair
    pyscf, _, rhf = pyscf_pair
    from pyscf import fci
    expected, _ = fci.FCI(rhf).kernel()
    assert native.exact_ground_energy() == pytest.approx(expected,abs=1e-8)
