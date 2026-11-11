# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual Public result-sequence observations, not Native extension claims."""
import numpy as np
import pytest

from quantumbridge.primitives import DataBin,PrimitiveResult,PubResult


@pytest.mark.parametrize("metadata",[None,{}, {"origin":"shared"}])
def test_actual_public_constructor_metadata_and_iteration_contract(metadata):
    pytest.importorskip("qiskit")
    from qiskit.primitives import DataBin as PublicData,PrimitiveResult as PublicResult,PubResult as PublicPub
    payload = np.arange(6.).reshape(2,3)
    for result_type,pub_type,data_type in [(PrimitiveResult,PubResult,DataBin),(PublicResult,PublicPub,PublicData)]:
        pubs = [pub_type(data_type(shape=(2,3),evs=payload)) for _ in range(2)]
        result = result_type(iter(pubs),metadata)
        assert len(result) == 2 and all(left is right for left,right in zip(result,pubs))
        assert result[0].data.evs is payload and result[-1] is pubs[-1]
        assert (result.metadata is metadata) is bool(metadata)
        assert not hasattr(result,"result") and not hasattr(result,"job_id")
    assert not hasattr(PublicResult([]),"to_dict") and not hasattr(PublicResult([]),"tolist")


@pytest.mark.parametrize("index",[slice(None),slice(1,None),slice(None,None,-1),slice(0,0)])
def test_actual_public_slice_types_and_item_identity(index):
    pytest.importorskip("qiskit")
    from qiskit.primitives import PrimitiveResult as PublicResult
    pubs = [object(),object(),object()]
    for result in [PrimitiveResult(pubs),PublicResult(pubs)]:
        selected = result[index]
        assert type(selected) is list
        assert len(selected) == len(pubs[index]) and all(left is right for left,right in zip(selected,pubs[index]))
