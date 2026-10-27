# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent complex matrix functions and actual public power observations."""

import cmath
import gc
import math

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedExecutionLimits as Limits,UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix,Operator,Statevector


DEFAULT_CUT=math.pi*1e-12


def scalar_power(value,n,cut=DEFAULT_CUT):
    if value==0:
        if n<0:raise np.linalg.LinAlgError("singular")
        return 1 if n==0 else 0
    if float(n).is_integer():return complex(value)**int(n)
    rotated=value*cmath.exp(-1j*cut)
    return cmath.exp(n*(math.log(abs(rotated))+1j*(cmath.phase(rotated)+cut)))


def jordan_power(size,value,coupling,n,cut=DEFAULT_CUT):
    result=np.zeros((size,size),complex)
    coefficient=scalar_power(value,n,cut)
    for distance in range(size):
        for row in range(size-distance):result[row,row+distance]=coefficient
        coefficient*=((n-distance)/(distance+1))*coupling/value
    return result


def fixed_unitary(size):
    rows=np.arange(size)
    return np.exp(2j*np.pi*np.outer(rows,rows)/size)/np.sqrt(size)


@pytest.mark.parametrize("n",[0,1,2,-1,3,.5,-.5,.25,1.3,-2.4])
@pytest.mark.parametrize("values",[[1,-1],[1j,-2j],[.1,3,2j,-1-1j]])
def test_complex_diagonal_real_powers_match_independent_scalar_functions(values,n):
    matrix=np.diag(values).astype(complex);owner=Operator(matrix)
    actual=owner.power(n)
    np.testing.assert_allclose(actual.data,np.diag([scalar_power(v,n) for v in values]),atol=3e-12,rtol=3e-13)
    assert type(actual) is Operator and actual.input_dims()==owner.input_dims() and actual.output_dims()==owner.output_dims()
    assert not np.shares_memory(actual.data,matrix)


@pytest.mark.parametrize("n",[.5,-.5,.3,1.3,-2.4])
@pytest.mark.parametrize("size,value,coupling",[(2,2,.7),(3,1+.4j,.3-.2j),(4,3,.8)])
@pytest.mark.parametrize("dense",[False,True])
def test_defective_jordan_matrix_power_uses_full_matrix_function(size,value,coupling,n,dense):
    matrix=np.eye(size,dtype=complex)*value+np.diag(np.full(size-1,coupling),1)
    expected=jordan_power(size,value,coupling,n)
    if dense:
        unitary=fixed_unitary(size);matrix=unitary@matrix@unitary.conj().T;expected=unitary@expected@unitary.conj().T
    np.testing.assert_allclose(Operator(matrix).power(n).data,expected,atol=3e-12,rtol=3e-13)


@pytest.mark.parametrize("cut",[0.,1e-3,-1e-3,.2,-.2,np.pi,-np.pi,2*np.pi,-2*np.pi,3*np.pi,-3*np.pi,.7])
@pytest.mark.parametrize("n",[.5,-.3])
@pytest.mark.parametrize("dense",[False,True])
def test_branch_cut_changes_complex_phase_without_modulo_discarding_global_winding(cut,n,dense):
    # Do not round an exact-axis oracle through a dense similarity on its cut.
    # Near-cut dense spectra also amplify that fixture rounding by 1/separation.
    on_axis=abs(math.sin(cut))<1e-14
    unitary=fixed_unitary(4) if dense and not on_axis else np.eye(4)
    separation=.05 if dense else 1e-10
    values=[1.,-1.,cmath.exp(1j*(cut+np.pi-separation)),cmath.exp(1j*(cut-np.pi+separation))]
    matrix=unitary@np.diag(values)@unitary.conj().T
    expected=unitary@np.diag([scalar_power(v,n,cut) for v in values])@unitary.conj().T
    np.testing.assert_allclose(Operator(matrix).power(n,branch_cut_rotation=cut).data,expected,atol=3e-12,rtol=0)


@pytest.mark.parametrize("delta",[0.,1e-10,-1e-10,1e-6,-1e-6])
@pytest.mark.parametrize("cut",[1e-3,-1e-3])
def test_near_coincident_triangular_eigenvalues_have_stable_divided_difference(delta,cut):
    a,b=2+1j,2+1j+delta
    matrix=np.array([[a,.7-.2j],[0,b]],complex)
    p=.37
    # Independent local derivative series, not the implementation's log/exp ratio.
    step=b-a
    divided=sum(math.prod(p-k for k in range(order+1))*scalar_power(a,p-order-1,cut)*step**order/math.factorial(order+1)
                for order in range(4))
    expected=np.array([[scalar_power(a,p,cut),(.7-.2j)*divided],[0,scalar_power(b,p,cut)]])
    np.testing.assert_allclose(Operator(matrix).power(p,branch_cut_rotation=cut).data,expected,atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[.5,.25,1.3])
def test_semisimple_singular_nonnormal_positive_powers_are_not_replaced_by_zero(n):
    matrix=np.array([[0,2.],[0,3.]],complex)
    expected=matrix*(3**(n-1))
    np.testing.assert_allclose(Operator(matrix).power(n).data,expected,atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[-1,-.5])
def test_negative_singular_power_has_explicit_error_not_nan_success(n):
    with pytest.raises(np.linalg.LinAlgError):Operator(np.diag([0,1])).power(n)


def test_nilpotent_fractional_root_refuses_an_undefined_matrix_function():
    with pytest.raises((UnsupportedFeature,np.linalg.LinAlgError)):
        Operator([[0,1],[0,0]]).power(.5)


@pytest.mark.parametrize("n",[np.int32(2),np.int64(-2),np.float32(.5),np.float64(.3),True])
def test_native_scalar_types_are_actual_callable_exponents(n):
    expected=np.diag([scalar_power(1j,float(n)),scalar_power(2,float(n))])
    np.testing.assert_allclose(Operator(np.diag([1j,2])).power(n).data,expected,atol=3e-12,rtol=0)


@pytest.mark.parametrize("value",[float("nan"),float("inf"),-float("inf")])
@pytest.mark.parametrize("argument",["n","branch_cut_rotation"])
def test_nonfinite_scalar_inputs_fail_before_numeric_factory(value,argument,monkeypatch):
    owner=Operator(np.eye(2,dtype=complex))
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("nonfinite input allocated"))
    kwargs={"n":.5,argument:value}
    with pytest.raises(ValueError):owner.power(**kwargs)


@pytest.mark.parametrize("value",[None,".5",1j,object()])
@pytest.mark.parametrize("argument",["n","branch_cut_rotation"])
def test_invalid_scalar_types_have_clear_type_error(value,argument):
    with pytest.raises(TypeError):Operator(np.eye(2)).power(**{"n":.5,argument:value})


@pytest.mark.parametrize("n",[0,1,.5])
def test_dimensions_and_owner_buffer_are_revalidated_before_new_output(n,monkeypatch):
    owner=Operator(np.eye(4,dtype=complex));owner.data.shape=(2,8)
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("invalid owner allocated"))
    with pytest.raises(ValueError):owner.power(n)


def test_matching_square_shape_does_not_override_mismatched_subsystem_domains():
    with pytest.raises(ValueError):Operator(np.eye(4),input_dims=(2,2),output_dims=(4,)).power(.5)


def test_assume_unitary_is_checked_for_normality_before_using_a_spectral_shortcut():
    nonnormal=Operator([[1,2],[0,3]])
    with pytest.raises(ValueError,match="normal|unitary"):nonnormal.power(.5,assume_unitary=True)
    matrix=fixed_unitary(4)@np.diag([.2,1j,2,-1])@fixed_unitary(4).conj().T
    np.testing.assert_allclose(Operator(matrix).power(.5,assume_unitary=True).data,Operator(matrix).power(.5).data,atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[0,1,-1,.5])
def test_power_result_isolated_from_borrowed_strided_owner_and_subsequent_mutation(n):
    storage=np.array([[2,0],[0,3]],complex);view=storage[::-1,::-1];owner=Operator(view)
    before=view.copy();actual=owner.power(n)
    np.testing.assert_array_equal(view,before)
    assert not np.shares_memory(actual.data,storage)
    view[0,0]=4
    np.testing.assert_allclose(owner.power(n).data,np.diag([scalar_power(4,n),scalar_power(2,n)]),atol=3e-12,rtol=0)
    np.testing.assert_allclose(actual.data,np.diag([scalar_power(3,n),scalar_power(2,n)]),atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[.5,-.3,1.3])
def test_complex_fractional_operator_really_evolves_statevector_and_density(n):
    unitary=fixed_unitary(4);values=[1.,1j,-1.,-1j]
    matrix=unitary@np.diag(values)@unitary.conj().T
    expected=unitary@np.diag([scalar_power(v,n) for v in values])@unitary.conj().T
    source=np.array([1,2j,-.7,.5j]);source/=np.linalg.norm(source)
    powered=Operator(matrix).power(n)
    np.testing.assert_allclose(Statevector(source).evolve(powered).data,expected@source,atol=3e-12,rtol=0)
    density=np.outer(source,source.conj())
    np.testing.assert_allclose(DensityMatrix(density).evolve(powered).data,expected@density@expected.conj().T,atol=3e-12,rtol=0)


@pytest.mark.parametrize("budget",["memory","dimension","work"])
@pytest.mark.parametrize("n",[2,-1,.5])
def test_power_preflight_precedes_copy_and_decomposition(budget,n,monkeypatch):
    matrix=np.array([[2,.3j],[.2,3]],complex);owner=Operator(matrix)
    def forbidden(*a,**k):pytest.fail("power factory ran before resource admission")
    for name in ("empty","array","asarray","copyto"):monkeypatch.setattr(np,name,forbidden)
    for name in ("eig","inv","solve","matrix_power"):monkeypatch.setattr(np.linalg,name,forbidden)
    logical=GateCircuitLimits(max_matrix_dimension=1) if budget=="dimension" else GateCircuitLimits(max_decomposition_work=1) if budget=="work" else GateCircuitLimits()
    with gate_circuit_scope(logical),ResourceScope(Ledger(Limits(max_total_memory_bytes=0 if budget=="memory" else 10**6))),pytest.raises(MemoryError):owner.power(n)


@pytest.mark.parametrize("kind",["exponent","cut","assumption","buffer"])
def test_managed_foreign_callbacks_cannot_execute(kind):
    class Foreign:
        def __float__(self):pytest.fail("foreign scalar conversion")
        def __int__(self):pytest.fail("foreign integer conversion")
        def __index__(self):pytest.fail("foreign index")
        def __bool__(self):pytest.fail("foreign truth")
        def __array__(self,*a,**k):pytest.fail("foreign array conversion")
    owner=Operator(np.eye(2,dtype=complex));kwargs={"n":.5}
    if kind=="buffer":owner.data=Foreign()
    else:kwargs[{"exponent":"n","cut":"branch_cut_rotation","assumption":"assume_unitary"}[kind]]=Foreign()
    with ResourceScope(Ledger()),pytest.raises((UnsupportedFeature,TypeError)):owner.power(**kwargs)


def test_managed_ndarray_subclass_cannot_dispatch_foreign_callbacks():
    class Hostile(np.ndarray):
        def __array_ufunc__(self,*a,**k):pytest.fail("foreign ufunc")
        def __array_function__(self,*a,**k):pytest.fail("foreign function")
        def __getitem__(self,*a,**k):pytest.fail("foreign indexing")
    owner=Operator(np.eye(2,dtype=complex));owner.data=np.diag([1j,2]).view(Hostile)
    with ResourceScope(Ledger()):result=owner.power(.5)
    np.testing.assert_allclose(result.data,np.diag([scalar_power(1j,.5),scalar_power(2,.5)]),atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[0,1,-1,.5])
def test_managed_output_lease_survives_scope_and_owner_then_releases_with_last_view(n):
    matrix=np.array([[2,.3],[0,2]],complex);owner=Operator(matrix);ledger=Ledger()
    with ResourceScope(ledger):result=owner.power(n)
    assert ledger.receipt()["live_memory_bytes"]==result.data.nbytes
    view=result.data[0];del owner,result;gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==matrix.nbytes
    del view;gc.collect();assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("n",[.5,-.3,1.3])
@pytest.mark.parametrize("kind",["normal","jordan","nonnormal","singular"])
@pytest.mark.parametrize("cut",[DEFAULT_CUT,1e-3,-1e-3])
def test_actual_public_operator_power_differential(kind,n,cut,record_property):
    public=pytest.importorskip("qiskit.quantum_info")
    if kind=="normal":
        unitary=fixed_unitary(4);matrix=unitary@np.diag([1,1j,-1,2]).astype(complex)@unitary.conj().T
    elif kind=="jordan":matrix=np.eye(4,dtype=complex)*2+np.diag(np.full(3,.3j),1)
    elif kind=="nonnormal":matrix=np.array([[1.,.4j],[0.,3.]])
    else:matrix=np.array([[0,2.],[0,3.]],complex)
    if kind=="singular" and n<0:
        with pytest.raises(np.linalg.LinAlgError):Operator(matrix).power(n,branch_cut_rotation=cut)
        assert not np.all(np.isfinite(public.Operator(matrix).power(n,branch_cut_rotation=cut).data))
        record_property("contract","INTENTIONAL_SAFETY_DIFFERENCE: explicit singular inverse failure, not public NaN matrix")
    else:
        expected=public.Operator(matrix).power(n,branch_cut_rotation=cut)
        actual=Operator(matrix).power(n,branch_cut_rotation=cut)
        np.testing.assert_allclose(actual.data,expected.data,atol=3e-12,rtol=3e-13)
        record_property("contract","MATCH: actual finite public complex matrix power")


@pytest.mark.parametrize("n",[0,1,-1,.5,-.3])
@pytest.mark.parametrize("cut",[DEFAULT_CUT,1e-3,-1e-3])
def test_scalar_one_by_one_operator_preserves_empty_subsystem_domains(n,cut):
    value=-.7+.4j;owner=Operator([[value]])
    result=owner.power(n,branch_cut_rotation=cut)
    assert result.input_dims()==result.output_dims()==()
    np.testing.assert_allclose(result.data,[[scalar_power(value,n,cut)]],atol=3e-12,rtol=0)


@pytest.mark.parametrize("n",[2**70+1,-(2**70+1),2**72+2])
def test_large_integer_powers_keep_exact_parity_and_do_not_convert_exponent_to_float(n):
    matrix=np.diag([-1,1j]).astype(complex)
    expected=np.diag([(-1)**(n%2),[1,1j,-1,-1j][n%4]])
    np.testing.assert_array_equal(Operator(matrix).power(n).data,expected)


@pytest.mark.parametrize("n",[0,1,.5])
def test_diagonal_power_needs_only_its_actual_output_storage(n):
    owner=Operator(np.diag([1j,2]).astype(complex));ledger=Ledger(Limits(max_total_memory_bytes=64))
    with ResourceScope(ledger):result=owner.power(n)
    assert ledger.receipt()["live_memory_bytes"]==result.data.nbytes==64


@pytest.mark.parametrize("value",[1e-300,1e300])
def test_extreme_nonzero_scalar_magnitudes_have_no_false_singularity(value):
    result=Operator(np.diag([value,2*value])).power(.5)
    np.testing.assert_allclose(result.data,np.diag([math.sqrt(value),math.sqrt(2*value)]),atol=0,rtol=3e-13)


@pytest.mark.parametrize("size",[6,8])
@pytest.mark.parametrize("n",[.5,-.3,1.3])
def test_larger_dense_defective_block_has_an_independent_analytic_matrix_oracle(size,n):
    source=np.eye(size,dtype=complex)*(2+.4j)+np.diag(np.full(size-1,.2j),1)
    unitary=fixed_unitary(size);expected=unitary@jordan_power(size,2+.4j,.2j,n)@unitary.conj().T
    np.testing.assert_allclose(Operator(unitary@source@unitary.conj().T).power(n).data,expected,atol=3e-12,rtol=3e-13)


@pytest.mark.parametrize("seed",range(20))
def test_actual_public_dense_nonnormal_and_independent_similarity_oracle(seed):
    public=pytest.importorskip("qiskit.quantum_info")
    rng=np.random.default_rng(seed);size=(2,4,8)[seed%3]
    change=np.eye(size)+.04*(rng.normal(size=(size,size))+1j*rng.normal(size=(size,size)))
    values=.7+rng.random(size)+.3j*rng.normal(size=size)
    p=(.5,-.3,.7,1.3,-1.4)[seed%5];cut=(1e-3,-1e-3)[seed%2]
    matrix=change@np.diag(values)@np.linalg.inv(change)
    expected=change@np.diag([scalar_power(v,p,cut) for v in values])@np.linalg.inv(change)
    actual=Operator(matrix).power(p,branch_cut_rotation=cut).data
    np.testing.assert_allclose(actual,expected,atol=3e-12,rtol=3e-13)
    np.testing.assert_allclose(actual,public.Operator(matrix).power(p,branch_cut_rotation=cut).data,atol=3e-12,rtol=3e-13)


@pytest.mark.parametrize("n",[0,1,.5,-1])
def test_rectangular_operator_power_refuses_its_actual_input_output_domains(n):
    with pytest.raises(ValueError):Operator(np.ones((2,3))).power(n)


def test_owner_dtype_replacement_cannot_execute_foreign_scalar_conversion():
    class Foreign:
        def __complex__(self):pytest.fail("object scalar conversion")
    owner=Operator(np.eye(2,dtype=complex));owner.data=np.full((2,2),Foreign(),dtype=object)
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):owner.power(.5)


def test_huge_integer_work_guard_runs_before_first_numeric_factory(monkeypatch):
    owner=Operator(np.eye(2,dtype=complex))
    monkeypatch.setattr(np,"empty",lambda *a,**k:pytest.fail("oversized exponent allocated"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=16)),pytest.raises(MemoryError):owner.power(1<<100)


def test_nearly_singular_dense_power_reports_numerical_limit_not_a_plausible_root():
    matrix=fixed_unitary(2)@np.diag([1e-20,1.])@fixed_unitary(2).conj().T
    with pytest.raises(np.linalg.LinAlgError,match="near-zero"):Operator(matrix).power(.5)


def test_faulting_decomposition_retains_no_output_or_workspace_after_exception_is_released(monkeypatch):
    owner=Operator([[2,.2],[.3,3]]);before=owner.data.copy();ledger=Ledger()
    def fail(*a,**k):raise np.linalg.LinAlgError("injected decomposition failure")
    monkeypatch.setattr(np.linalg,"eig",fail)
    with ResourceScope(ledger),pytest.raises(np.linalg.LinAlgError,match="injected"):owner.power(.5)
    gc.collect();assert ledger.receipt()["live_memory_bytes"]==0
    np.testing.assert_array_equal(owner.data,before)


@pytest.mark.parametrize("coupling",[1e-6,1e-8,1e-10])
def test_nearly_normal_jordan_block_cannot_lose_a_small_real_offdiagonal(coupling):
    matrix=np.array([[1.,coupling],[0,1.]])
    expected=np.array([[1.,coupling/2],[0,1.]])
    np.testing.assert_allclose(Operator(matrix).power(.5).data,expected,atol=2e-15,rtol=0)
    with pytest.raises(ValueError,match="normal|unitary"):Operator(matrix).power(.5,assume_unitary=True)
