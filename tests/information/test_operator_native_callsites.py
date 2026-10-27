# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real native Operator callsites, not unrelated same-name circuit methods."""

import numpy as np
import pytest

from quantumbridge.information import Operator, Kraus, Choi, SuperOp
from quantumbridge.information.channels import _embed_operator
from quantumbridge.execution import UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope


def matrix(width, seed=12101):
    rng = np.random.default_rng(seed)
    size = 1 << width
    value, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))
    return value * np.exp(.21j)


def embedded(data, wires, width):
    dims = (2,) * width
    result = np.zeros((1 << width, 1 << width), complex)
    for row in range(len(result)):
        a = np.unravel_index(row, dims)
        for column in range(len(result)):
            b = np.unravel_index(column, dims)
            if any(a[pos] != b[pos] for pos in range(width) if pos not in wires):continue
            local_row = sum(a[pos] << (len(wires) - 1 - k) for k, pos in enumerate(wires))
            local_column = sum(b[pos] << (len(wires) - 1 - k) for k, pos in enumerate(wires))
            result[row, column] = data[local_row, local_column]
    return result


@pytest.mark.parametrize("wires", [(0,), (2,), (2, 0), (0, 2)])
def test_channel_embedding_declares_both_dense_operands_native_before_compose(wires, monkeypatch):
    data = matrix(len(wires))
    expected = embedded(data, wires, 3)
    calls = []
    original = Operator.compose
    def observed(self, other, *args, **kwargs):
        assert self.__dict__.get("_arithmetic_convention") == "native"
        assert other.__dict__.get("_arithmetic_convention") == "native"
        calls.append(tuple(kwargs["qargs"]))
        return original(self, other, *args, **kwargs)
    monkeypatch.setattr(Operator, "compose", observed)
    result = _embed_operator(data, wires, 3)
    np.testing.assert_allclose(result, expected, atol=3e-12, rtol=0)
    assert calls == [wires]


@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("wires", [(2, 0), (0, 2)])
def test_channel_composition_and_choi_keep_native_physical_mapping(front, wires):
    a, b = matrix(3, 12102), matrix(2, 12103)
    local = embedded(b, wires, 3)
    expected = a @ local if front else local @ a
    first, second = Kraus([a]), Kraus([b])
    for managed in (False, True):
        if managed:
            with ResourceScope(UnifiedResourceLedger()):
                result = first.compose(second, qargs=wires, front=front)
        else: result = first.compose(second, qargs=wires, front=front)
        np.testing.assert_allclose(SuperOp(result).data, np.kron(expected.conj(), expected), atol=5e-12, rtol=0)
        vector = expected.reshape(-1, order="F")
        np.testing.assert_allclose(Choi(result).data, np.outer(vector, vector.conj()), atol=5e-12, rtol=0)


@pytest.mark.parametrize("wires", [(2, 0), (0, 2)])
@pytest.mark.parametrize("front", [False, True])
def test_explicit_native_mapped_product_has_legacy_and_independent_math(wires, front):
    a, b = matrix(3, 12104), matrix(2, 12105)
    local = embedded(b, wires, 3)
    expected = local @ a if front else a @ local
    legacy = Operator(a).compose(Operator(b), qargs=wires, front=front)
    native = Operator(a).as_native_operator().compose(Operator(b).as_native_operator(), qargs=wires, front=front)
    np.testing.assert_allclose(legacy.data, expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(native.data, expected, atol=3e-12, rtol=0)
    assert native.__dict__["_arithmetic_convention"] == "native"


def test_inventory_retains_unknown_receivers_and_does_not_type_prove_them():
    import ast
    import runpy
    from pathlib import Path
    probe = Path(__file__).resolve().parents[1] / "interfaces/probes/probe_operator_callsite_inventory.py"
    api = runpy.run_path(str(probe))
    source = "from quantumbridge.information import Operator as Op\na = Op([[1]])\nb = a.as_native_operator()\nb.compose(b)\nfactory().compose(a)\n"
    visitor = api["Candidates"]("quantumbridge/example.py", source)
    visitor.visit(ast.parse(source))
    calls = [item for item in visitor.records if item["method"] == "compose"]
    assert calls[0]["receiver_hint"] == "native_explicit"
    assert calls[1]["receiver_hint"] == "unresolved"
    assert api["migration_review"](calls[1])["status"] == "UNRESOLVED"


def test_inventory_does_not_migrate_an_unrelated_same_name_tensor():
    import ast
    import runpy
    from pathlib import Path
    probe = Path(__file__).resolve().parents[1] / "interfaces/probes/probe_operator_callsite_inventory.py"
    api = runpy.run_path(str(probe))
    text = "import torch\ntorch.tensor([1.0])\n"
    visitor = api["Candidates"]("quantumbridge/example.py", text)
    visitor.visit(ast.parse(text))
    assert len(visitor.records) == 1
    record = visitor.records[0]
    assert record["receiver_hint"] == "import:torch"
    assert api["migration_review"](record)["status"] == "NOT_APPLICABLE"
