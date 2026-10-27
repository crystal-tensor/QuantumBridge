# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""The public ABI shares the native store, not a detached execution copy."""
import numpy as np
import quantumbridge as qb
from quantumbridge.core.standard_gates import XGate,RYGate
from quantumbridge.information import Operator


def ry(x):return np.array([[np.cos(x/2),-np.sin(x/2)],[np.sin(x/2),np.cos(x/2)]])


def test_native_fluent_and_public_append_have_distinct_real_return_contracts():
    native=qb.Circuit(1)
    assert native.append(XGate(),[0]) is native
    public=qb.QuantumCircuit(1)
    handle=public.append(XGate(),[0])
    assert isinstance(handle,qb.InstructionSet) and len(handle)==1
    assert len(public.data)==len(public.operations)==1
    assert public.data[0].operation is public.operations[0].metadata["gate"]


def test_public_builder_enters_the_existing_operator_and_device_without_a_surrogate():
    public=qb.QuantumCircuit(1)
    handle=public.h(0)
    assert isinstance(public,qb.Circuit) and isinstance(handle,qb.InstructionSet)
    np.testing.assert_allclose(Operator(public).data,np.array([[1,1],[1,-1]])/np.sqrt(2),atol=2e-13,rtol=0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(public),[1/np.sqrt(2)]*2,atol=2e-13,rtol=0)


def test_public_owner_reuse_does_not_replace_the_cached_standard_invocation_params():
    gate=RYGate(.3);native=qb.Circuit(1).append(gate,[0])
    public=qb.QuantumCircuit(1);handle=public.append(gate,[0],copy=False)
    gate.params[0]=.7
    assert public.data[0].operation is gate and handle.instructions[0] is gate
    assert public.data[0].params==[.3] and public.data[0].operation.params==[.7]
    np.testing.assert_allclose(Operator(native).data,ry(.3),atol=3e-13,rtol=0)
    np.testing.assert_allclose(Operator(public).data,ry(.3),atol=3e-13,rtol=0)
