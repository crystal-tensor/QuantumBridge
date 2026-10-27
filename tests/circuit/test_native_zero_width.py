# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Zero quantum width still has one scalar quantum amplitude."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator


def test_empty_constructor_and_classical_only_circuit_are_distinct():
    assert (qb.Circuit().num_qubits,qb.Circuit().num_clbits)==(0,0)
    circuit=qb.Circuit(0,2)
    assert circuit.num_qubits==0 and circuit.num_clbits==2 and len(circuit.clbits)==2


def test_zero_qubit_phase_is_a_full_complex_scalar_operator_and_state():
    circuit=qb.Circuit(0);circuit.global_phase=.3
    np.testing.assert_allclose(Operator(circuit).data,[[np.exp(.3j)]],atol=2e-13,rtol=0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit),[np.exp(.3j)],atol=2e-13,rtol=0)
    np.testing.assert_allclose(qb.DensityMatrixDevice().density_matrix(circuit),[[1]],atol=2e-13,rtol=0)


def test_zero_qubit_gate_and_instruction_retain_executable_scalar_definitions():
    circuit=qb.Circuit(0,name="phase");circuit.global_phase=.3
    for operation in (circuit.to_gate(),circuit.to_instruction()):
        assert operation.num_qubits==0 and operation.definition.num_qubits==0
        np.testing.assert_allclose(Operator(operation).data,[[np.exp(.3j)]],atol=2e-13,rtol=0)


def test_zero_width_repeat_and_compose_preserve_coherent_phase():
    circuit=qb.Circuit(0);circuit.global_phase=.3
    for output in (circuit.repeat(2),circuit.compose(circuit),circuit.tensor(circuit)):
        np.testing.assert_allclose(Operator(output).data,[[np.exp(.6j)]],atol=3e-13,rtol=0)
    assert len(circuit.repeat(2).operations)==2


def test_zero_width_inverse_is_complex_conjugation_not_an_empty_noop():
    circuit=qb.Circuit(0);circuit.global_phase=.3
    np.testing.assert_allclose(Operator(circuit.inverse()).data,[[np.exp(-.3j)]],atol=2e-13,rtol=0)


def test_zero_qubit_circuit_can_execute_a_real_classical_store():
    circuit=qb.Circuit(0,2);counter=circuit.add_var("counter",2)
    circuit.store(counter,counter+1)
    result=qb.StatevectorDevice().run_shots(circuit,shots=2,memory=True)
    # No explicit measurement: native implicit quantum sampling has zero bits.
    assert result.counts()=={"":2}
    assert all(row["variables"][counter.value[0]]["value"]==3 for row in result.metadata()["classical_memory"])


def test_phase_only_zero_width_gate_can_be_coherently_controlled():
    source=qb.Circuit(0);source.global_phase=.3
    gate=source.to_gate().control()
    np.testing.assert_allclose(Operator(gate).data,np.diag([1,np.exp(.3j)]),atol=3e-13,rtol=0)


def test_classical_width_does_not_make_an_instruction_unitary():
    source=qb.Circuit(0,2)
    assert source.to_instruction().num_clbits==2
    with pytest.raises(ValueError):source.to_gate()


def test_zero_width_repeated_gate_is_itself_a_valid_unitary_definition():
    source=qb.Circuit(0);source.global_phase=.3
    gate=source.repeat(2).to_gate()
    np.testing.assert_allclose(Operator(gate).data,[[np.exp(.6j)]],atol=3e-13,rtol=0)


def test_zero_width_circuit_control_uses_a_real_scalar_phase_not_a_missing_target_wire():
    source=qb.Circuit(0);source.global_phase=.3
    out=source.control()
    np.testing.assert_allclose(Operator(out).data,np.diag([1,np.exp(.3j)]),atol=3e-13,rtol=0)
