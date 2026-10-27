# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Metadata contracts measured through actual installed public API calls."""
import pytest
import quantumbridge as qb


class Token:
    pass


class Dictionary(dict):
    pass


def outcome(kind, action):
    token = Token()
    data = {"nested": [1], "token": token, "again": token}
    source = kind(1, name="source", global_phase=.2, metadata=data)
    source.ry(.3, 0)
    other = kind(1, name="other", metadata={"other": [3]})
    other.x(0)
    if action == "construct": result = source
    elif action == "copy": result = source.copy()
    elif action == "empty": result = source.copy_empty_like()
    elif action == "inverse": result = source.inverse()
    elif action == "decompose": result = source.decompose()
    elif action == "compose": result = source.compose(other)
    elif action == "compose-inplace":
        source.compose(other, inplace=True)
        result = source
    elif action == "tensor": result = source.tensor(other)
    elif action == "repeat": result = source.repeat(2)
    elif action == "power": result = source.power(2)
    elif action == "bind": result = source.assign_parameters({})
    else: result = getattr(source, "to_" + action)().definition
    metadata = result.metadata
    return (tuple(sorted(metadata)), metadata is data, metadata is source.metadata,
        metadata.get("nested") is data["nested"], metadata.get("token") is token,
        metadata.get("token") is metadata.get("again"), source.metadata is data,
        )


@pytest.mark.parametrize("action", ["construct", "copy", "empty", "inverse", "decompose",
    "compose", "compose-inplace", "tensor", "repeat", "power", "bind", "gate", "instruction"])
def test_public_metadata_reference_copy_factory_contract(action, record_property):
    qiskit = pytest.importorskip("qiskit")
    native = outcome(qb.QuantumCircuit, action)
    public = outcome(qiskit.QuantumCircuit, action)
    if action == "decompose" and qiskit.__version__.startswith("2.6."):
        record_property("contract", "VERSIONED_SHALLOW_CONTAINER_DIFFERENCE")
        assert native[0] == public[0]
        assert native[3:] == public[3:]
        assert native[1:3] == (True, True) and public[1:3] == (False, False)
    else:
        record_property("contract", "MATCH")
        assert native == public


@pytest.mark.parametrize("value", [{}, Dictionary(), Dictionary({"run": 1}), None, [], 1, False, ""])
def test_public_metadata_constructor_and_setter_types_are_atomic(value):
    qiskit = pytest.importorskip("qiskit")
    results = []
    for kind in (qb.QuantumCircuit, qiskit.QuantumCircuit):
        source = kind(1, metadata={"old": 1})
        before = source.metadata
        try:
            source.metadata = value
            assigned = ("value", source.metadata is value, type(source.metadata).__name__)
        except Exception as error:
            assigned = (type(error).__name__, source.metadata is before)
        try:
            result = kind(1, metadata=value)
            constructed = ("value", result.metadata is value, type(result.metadata).__name__)
        except Exception as error: constructed = (type(error).__name__,)
        results.append((assigned, constructed))
    assert results[0] == results[1]
