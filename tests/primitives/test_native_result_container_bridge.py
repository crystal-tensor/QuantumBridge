# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""One public sequence protocol, distinct Legacy ABI, lossless native views."""
from copy import deepcopy
from dataclasses import fields
import inspect
import pickle

import numpy as np
import pytest

from quantumbridge import Circuit,ClassicalRegister,Parameter,StatevectorSampler
from quantumbridge.primitives import DataBin,PrimitiveResult,PubResult,LegacyPrimitiveResult
from quantumbridge.primitives import legacy_containers as legacy


def test_legacy_is_a_real_subclass_without_aliasing_or_changing_its_fields():
    assert LegacyPrimitiveResult is legacy.PrimitiveResult and LegacyPrimitiveResult is not PrimitiveResult
    assert issubclass(LegacyPrimitiveResult,PrimitiveResult)
    assert [item.name for item in fields(LegacyPrimitiveResult)] == ["pub_results","metadata","_job_id"]
    assert list(inspect.signature(LegacyPrimitiveResult).parameters) == ["pub_results","metadata","_job_id"]
    result = LegacyPrimitiveResult([legacy.PubResult(legacy.DataBin(evs=1.))])
    assert result.result() is result and result.job_id() == "quantumbridge-primitive-result"
    assert type(result[:]) is list and result.tolist()[0] is result[0]


@pytest.mark.parametrize("dtype",[np.float64,np.int16,np.complex128])
def test_public_dictionary_projection_preserves_native_array_shape_dtype_and_identity(dtype):
    values = np.arange(6,dtype=dtype).reshape(2,3)
    class Marker:
        shape = (2,3)
    marker = Marker()
    data = DataBin(shape=(2,3),evs=values,auxiliary=marker)
    pub = PubResult(data,{"tag":marker})
    result = PrimitiveResult([pub],{"origin":"native","opaque":marker})
    projected = result.to_dict()
    assert projected["results"][0]["data"]["evs"] is values
    assert projected["results"][0]["data"]["auxiliary"] is marker
    assert projected["results"][0]["metadata"]["tag"] is marker
    assert projected["metadata"]["opaque"] is marker
    assert result.tolist() == [pub] and result.tolist()[0] is pub


def test_projection_retains_real_batched_multi_register_packed_memory():
    theta = Parameter("theta")
    source = Circuit(2).ry(theta,0).x(1)
    alpha,beta = ClassicalRegister(9,"alpha"),ClassicalRegister(17,"beta")
    source.add_register(alpha,beta)
    source.measure(0,alpha[8]).measure(1,beta[16])
    values = np.array([[[0.],[np.pi],[0.]],[[np.pi],[0.],[np.pi]]])
    result = StatevectorSampler(default_shots=3,seed=42).run([(source,values)]).result()
    data = result.to_dict()["results"][0]["data"]
    assert data["alpha"] is result[0].data.alpha and data["beta"] is result[0].data.beta
    assert data["alpha"].shape == data["beta"].shape == (2,3)
    assert data["alpha"].num_shots == 3 and data["beta"].num_bits == 17
    for loc in np.ndindex((2,3)):
        bit = int(values[loc][0] > 1)
        assert data["alpha"].get_counts(loc) == {format(bit << 8,"09b"):3}
        assert data["beta"].get_counts(loc) == {"1"+"0"*16:3}


def test_projection_does_not_reserve_or_expand_numeric_payloads(monkeypatch):
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.array_reservations import ArrayReservation
    from quantumbridge.primitives import BitArray
    account = UnifiedResourceLedger()
    with ResourceScope(account):
        bits = BitArray.from_samples(["111000000","000000001"])
        result = PrimitiveResult([PubResult(DataBin(meas=bits))])
    before = account.receipt()["live_memory_bytes"]
    def forbidden(*args,**kwargs):pytest.fail("A dictionary view expanded/copied numeric storage.")
    monkeypatch.setattr(ArrayReservation,"create",forbidden)
    monkeypatch.setattr(BitArray,"get_bitstrings",forbidden)
    projected = result.to_dict()
    assert projected["results"][0]["data"]["meas"] is bits
    assert account.receipt()["live_memory_bytes"] == before == 4


def test_projection_copies_structure_but_explicitly_retains_nested_payload_aliases():
    nested = {"steps":[1,2]}
    result = PrimitiveResult([PubResult(DataBin(value=nested),{"nested":nested})],{"nested":nested})
    projected = result.to_dict()
    projected["metadata"]["added"] = True
    projected["results"][0]["data"]["added"] = True
    projected["results"][0]["metadata"]["added"] = True
    assert "added" not in result.metadata and "added" not in result[0].data and "added" not in result[0].metadata
    assert projected["metadata"]["nested"] is projected["results"][0]["data"]["value"] is nested


def test_projection_does_not_invoke_payload_conversion_or_reserve_data_field_names():
    class Opaque:
        def __array__(self,*args,**kwargs):pytest.fail("Foreign array coercion")
        def __iter__(self):pytest.fail("Foreign iterator")
        def to_dict(self):pytest.fail("Foreign serialization hook")
    value = Opaque()
    data = DataBin(to_dict=value,tolist=value,shape=())
    projected = PrimitiveResult([PubResult(data)]).to_dict()["results"][0]["data"]
    assert projected == {"to_dict":value,"tolist":value}
    assert data.to_dict is value and data.tolist is value


def test_legacy_recursive_dictionary_conversion_remains_distinct_from_native_view():
    bits = legacy.BitArray.from_counts({"01":2,"10":1},num_bits=2)
    result = LegacyPrimitiveResult([legacy.PubResult(legacy.DataBin(meas=bits))],{"tuple":(1,2)},"job-old")
    assert isinstance(result,PrimitiveResult) and type(result) is LegacyPrimitiveResult
    assert result.to_dict() == {"results":[{"data":{"meas":{"bitstrings":["01","01","10"],
        "num_bits":2,"num_shots":3}},"metadata":{}}],"metadata":{"tuple":[1,2]}}
    assert result.job_id() == "job-old" and result.result() is result


@pytest.mark.parametrize("use_legacy",[False,True])
@pytest.mark.parametrize("method",[deepcopy,lambda value:pickle.loads(pickle.dumps(value))],ids=["deepcopy","pickle"])
def test_bridge_preserves_ordinary_copy_pickle_and_concrete_container_types(use_legacy,method):
    result = (LegacyPrimitiveResult([legacy.PubResult(legacy.DataBin(value=[1,2]))],{"tag":"old"})
        if use_legacy else PrimitiveResult([PubResult(DataBin(value=np.array([1.,2.])))],{"tag":"new"}))
    restored = method(result)
    assert type(restored) is type(result) and isinstance(restored,PrimitiveResult)
    assert type(restored[0]) is type(result[0]) and type(restored[0].data) is type(result[0].data)
    np.testing.assert_array_equal(restored[0].data.value,result[0].data.value)
    assert restored.metadata == result.metadata and restored[0].data.value is not result[0].data.value
    assert restored.tolist()[0] is restored[0]
    if use_legacy:assert restored.result() is restored


def test_empty_public_result_keeps_sequence_and_dictionary_extensions_separate_from_a_job():
    result = PrimitiveResult([], {"empty":True})
    assert result.to_dict() == {"results":[],"metadata":{"empty":True}} and result.tolist() == []
    assert len(result) == 0 and not hasattr(result,"result") and not hasattr(result,"job_id")


@pytest.mark.parametrize("metadata",[None,{}, {"calls":1}])
def test_native_public_metadata_keeps_the_documented_nonempty_mapping_reference(metadata):
    result = PrimitiveResult([],metadata)
    assert result.metadata == (metadata or {})
    assert (result.metadata is metadata) is bool(metadata)
    if metadata:metadata["calls"] = 2
    assert result.metadata == (metadata or {})


@pytest.mark.parametrize("index",[slice(None),slice(1,None),slice(None,None,-1),slice(0,0)])
def test_native_public_slices_return_lists_of_the_original_pubs(index):
    pubs = [PubResult(DataBin(value=value)) for value in [1,2,3]]
    result = PrimitiveResult(iter(pubs))
    selected = result[index]
    assert type(selected) is list
    assert len(selected) == len(pubs[index]) and all(left is right for left,right in zip(selected,pubs[index]))
