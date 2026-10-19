import numpy as np
import pytest
from quantumbridge.chemistry import FermionicOp, JordanWignerMapper, QubitHamiltonian


def test_normal_order_includes_same_mode_identity_contraction():
    op = FermionicOp({'-_0 +_0': 1}, 1)
    assert op.normal_ordered().to_dict() == {'+_0 -_0': -1, '': 1}
    np.testing.assert_allclose(op.to_matrix(), op.normal_ordered().to_matrix())


def test_distinct_mode_swap_is_negative_without_contraction():
    ordered = FermionicOp({'-_0 +_1': 2j}, 2).normal_ordered()
    assert ordered.to_dict() == {'+_1 -_0': -2j}


def test_nested_normal_order_expands_multiple_contractions():
    op = FermionicOp({'-_0 -_1 +_1 +_0': .7, '+_1 -_0 +_0 -_1': .2j}, 2)
    np.testing.assert_allclose(op.to_matrix(), op.normal_ordered().to_matrix(), atol=1e-14)
    assert len(op.normal_ordered().terms) > len(op.terms)


def test_equal_ladders_are_nilpotent_even_after_swapping():
    for label in ('+_0 +_0', '-_1 -_1', '+_0 +_1 +_0', '-_0 +_1 -_0'):
        assert not FermionicOp({label: 1}, 2).normal_ordered().terms


def test_occupation_action_has_fermionic_parity_sign():
    value = FermionicOp({'+_1': 1}, 2).to_matrix()
    assert value[1, 0] == 1 and value[3, 2] == -1
    assert np.count_nonzero(value) == 2


def test_complete_two_mode_canonical_anticommutators():
    identity = np.eye(4)
    for i in range(2):
        for j in range(2):
            a = FermionicOp({f'-_{i}': 1}, 2).to_matrix()
            b = FermionicOp({f'+_{j}': 1}, 2).to_matrix()
            np.testing.assert_allclose(a @ b + b @ a, identity if i == j else np.zeros((4, 4)))
            np.testing.assert_allclose(a @ b.conj().T + b.conj().T @ a, np.zeros((4, 4)))


def test_jordan_wigner_creation_has_z_string_and_complex_y():
    op = FermionicOp({'+_2': 1.2 - .4j}, 3)
    mapped = JordanWignerMapper().map(op)
    np.testing.assert_allclose(mapped.matrix(), op.to_matrix())
    assert mapped.num_qubits == 3
    with pytest.raises(ValueError, match='Non-Hermitian'):
        mapped.to_quantumbridge()


def test_jordan_wigner_hermitian_complex_hopping_preserves_current_sign():
    op = FermionicOp({'+_0 -_1': .4 + .3j, '+_1 -_0': .4 - .3j}, 2)
    mapped = JordanWignerMapper().map(op)
    np.testing.assert_allclose(mapped.matrix(), op.to_matrix())
    np.testing.assert_allclose(mapped.matrix(), mapped.matrix().conj().T)
    assert mapped.to_quantumbridge().terms


def test_jordan_wigner_quartic_words_match_independent_fock_action():
    op = FermionicOp({'+_0 +_2 -_3 -_1': .25, '-_1 +_1 -_2 +_2': -.3}, 4)
    np.testing.assert_allclose(JordanWignerMapper().map(op).matrix(), op.to_matrix())


def test_zero_coefficients_stay_zero_with_declared_register():
    mapped = JordanWignerMapper().map(FermionicOp({'+_0': 0}, 3))
    assert mapped.num_qubits == 3 and not mapped.terms
    np.testing.assert_array_equal(mapped.matrix(), np.zeros((8, 8)))


def test_fermionic_product_and_adjoint_are_actual_operator_algebra():
    a = FermionicOp({'+_0': .2j, '-_1': -.3}, 2)
    b = FermionicOp({'+_1 -_0': .7}, 2)
    np.testing.assert_allclose((a @ b).to_matrix(), a.to_matrix() @ b.to_matrix())
    np.testing.assert_allclose(a.adjoint().to_matrix(), a.to_matrix().conj().T)
    np.testing.assert_allclose((a - a + 2 * b).to_matrix(), 2 * b.to_matrix())


def test_identity_and_vacuum_sector_keep_dimension():
    op = FermionicOp({'I': 2, '': -1}, 0)
    np.testing.assert_array_equal(JordanWignerMapper().map(op).matrix(), [[1]])
    np.testing.assert_array_equal(op.to_matrix(), [[1]])


def test_fermionic_labels_and_bounds_are_validated():
    for args in (({'x_0': 1}, 1), ({'+_-1': 1}, 1), ({'+_2': 1}, 2), ({'': float('nan')}, 1), ({'': 1}, True)):
        with pytest.raises((ValueError, TypeError)):
            FermionicOp(*args)
    with pytest.raises(ValueError):
        FermionicOp([('',1e308),('I',1e308)])


def test_normal_order_mapping_and_dense_work_budgets_fail_explicitly():
    with pytest.raises(MemoryError):
        FermionicOp({'-_0 +_0': 1}, 1).normal_ordered(max_terms=1)
    with pytest.raises(MemoryError):
        JordanWignerMapper().map(FermionicOp({'+_0': 1}, 1), max_terms=1)
    with pytest.raises(MemoryError):
        FermionicOp({'': 1}, 11).to_matrix()
    with pytest.raises(MemoryError):
        QubitHamiltonian([], num_qubits=11).matrix()
    with pytest.raises(ValueError):
        FermionicOp({'':1}).normal_ordered(max_terms=0)
    with pytest.raises(TypeError):
        JordanWignerMapper().map([])
    with pytest.raises(ValueError):
        JordanWignerMapper().map(FermionicOp({'':1}),max_terms=True)


def test_number_mapping_retains_unoccupied_spectator_wires():
    op = FermionicOp({'+_0 -_0': 1}, 3)
    mapped = JordanWignerMapper().map(op)
    np.testing.assert_array_equal(mapped.matrix(), np.diag([0, 0, 0, 0, 1, 1, 1, 1]))
