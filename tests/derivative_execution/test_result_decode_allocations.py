# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Keep the established Result/snapshot codecs while owning numeric imports."""

import gc
import json

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.results import Result
from quantumbridge.serialization.errors import ResourceLimitError as SerializationResourceLimit
from quantumbridge.serialization.limits import SerializationLimits
from quantumbridge.simulator.snapshots import decode, encode


def test_result_json_state_denied_before_complex_array_conversion(monkeypatch):
    text = Result(state=np.array([1., 0., 0., 0.], complex)).to_json()
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("Result import allocated before reservation"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Result import allocated before reservation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):Result.from_json(text)


def test_density_import_has_one_owned_root_after_scope_and_result_destruction():
    payload = Result(density=np.array([[.6, .2j], [-.2j, .4]])).to_dict()
    ledger = Ledger()
    with ResourceScope(ledger):result = Result.from_dict(payload)
    view = result.density[:, ::-1]
    assert ledger.receipt()["live_memory_bytes"] == 64
    del result
    gc.collect()
    np.testing.assert_array_equal(view, np.array([[.2j, .6], [.4, -.2j]]))
    assert ledger.receipt()["live_memory_bytes"] == 64
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_snapshot_decode_denies_before_component_arrays(monkeypatch):
    value = encode(np.eye(4, dtype=complex))
    ledger = Ledger(Limits(max_total_memory_bytes=255))
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("Snapshot decode coerced before reservation"))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Snapshot decode allocated before reservation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):decode(value)


def test_result_json_byte_limit_rejects_before_decoder(monkeypatch):
    text = " "*(16*1024*1024+1)+"{}"
    monkeypatch.setattr(json, "loads", lambda *a, **k: pytest.fail("Oversized JSON reached decoder"))
    with pytest.raises(SerializationResourceLimit):Result.from_json(text)


def test_result_json_depth_rejects_before_numeric_conversion(monkeypatch):
    payload = Result(state=np.array([1., 0.], complex)).to_dict()
    nested = 0
    for _ in range(300):nested = [nested]
    payload["trace"] = nested
    text = json.dumps(payload)
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("Deep JSON reached numeric conversion"))
    with pytest.raises(SerializationResourceLimit):Result.from_json(text)


def test_result_json_label_count_rejects_before_numeric_conversion(monkeypatch):
    payload = Result(state=np.array([1., 0.], complex),
        metadata_data={"saved_snapshots": {str(i): 0 for i in range(1025)}}).to_dict()
    text = json.dumps(payload)
    monkeypatch.setattr(np, "asarray", lambda *a, **k: pytest.fail("Excess labels reached numeric conversion"))
    with pytest.raises(SerializationResourceLimit):Result.from_json(text)


@pytest.mark.parametrize("complex_values", [False, True])
def test_snapshot_import_retains_one_numeric_root_without_changing_values(complex_values):
    source = np.arange(8., dtype=float).reshape(2, 4)[:, ::-1]
    if complex_values:source = source+1j*source[::-1]
    payload, ledger = encode(source), Ledger()
    with ResourceScope(ledger):actual = decode(payload)
    np.testing.assert_array_equal(actual, source)
    assert actual.dtype == (np.dtype(complex) if complex_values else np.dtype(float))
    assert ledger.receipt()["live_memory_bytes"] == actual.nbytes
    view = actual[:, ::2]
    del actual
    assert ledger.receipt()["live_memory_bytes"] == source.nbytes
    del view
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_import_valid_overbudget_valid_keeps_correct_root_lifetime():
    payload = Result(state=np.array([1., 0., 0., 0.], complex)).to_dict()
    ledger = Ledger(Limits(max_total_memory_bytes=80))
    with ResourceScope(ledger):
        first = Result.from_dict(payload)
        with pytest.raises(MemoryError):Result.from_dict(payload)
        assert ledger.receipt()["live_memory_bytes"] == 64
        del first
        second = Result.from_dict(payload)
        np.testing.assert_array_equal(second.state, [1., 0., 0., 0.])
    del second
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_serialization_limits_use_utf8_bytes_and_configurable_labels():
    from quantumbridge.schema.serialization import to_json, from_json
    nonascii = chr(0x4E2D)*8
    with pytest.raises(SerializationResourceLimit):to_json({"text": nonascii}, limits=SerializationLimits(max_input_bytes=20))
    with pytest.raises(SerializationResourceLimit):from_json('"'+nonascii+'"', limits=SerializationLimits(max_input_bytes=20))
    payload = Result(metadata_data={"saved_snapshots": {"a": 1, "b": 2}}).to_dict()
    text = json.dumps(payload)
    with pytest.raises(SerializationResourceLimit):Result.from_json(text, serialization_limits=SerializationLimits(max_result_labels=1))
    assert Result.from_json(text, serialization_limits=SerializationLimits(max_result_labels=2)).data() == {"a": 1, "b": 2}
    nested = 0
    for _ in range(40):nested = [nested]
    with pytest.raises(SerializationResourceLimit):from_json(json.dumps(nested), limits=SerializationLimits(max_json_depth=32))


def test_mps_numeric_export_bound_precedes_tolist_materialization(monkeypatch):
    from quantumbridge.information import MatrixProductState
    state = MatrixProductState.zero(3)
    class NeverSerialize:
        def __call__(self, *args, **kwargs):pytest.fail("Export proceeded beyond scalar count preflight")
    from quantumbridge.schema import serialization
    monkeypatch.setattr(serialization, "_note_python_heap", NeverSerialize())
    with pytest.raises(SerializationResourceLimit):state.to_dict(serialization_limits=SerializationLimits(max_numeric_elements=3))


def test_json_cycles_depth_elements_and_decoder_failures_are_explicit():
    from quantumbridge.schema.serialization import to_json, from_json
    cyclic = {};cyclic["self"] = cyclic
    with pytest.raises(ValueError):to_json(cyclic)
    with pytest.raises(SerializationResourceLimit):to_json([1, 2, 3], limits=SerializationLimits(max_numeric_elements=2))
    with pytest.raises(SerializationResourceLimit):from_json("["*1100+"0"+"]"*1100)
    with pytest.raises(ValueError):from_json('{"broken":')


def test_result_import_rejects_opaque_component_hooks_before_dispatch():
    from quantumbridge.core.classical import UnsupportedFeature
    calls = []
    class Opaque:
        def __complex__(self):calls.append(1);return 1j
        def __len__(self):calls.append(1);return 2
    payload = Result().to_dict();payload["statevector"] = [Opaque()]
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):Result.from_dict(payload)
    assert calls == []


def test_serialization_resource_error_maps_to_existing_resource_status():
    from quantumbridge.execution.derivative_status import classify_derivative_error
    error = SerializationResourceLimit("too many JSON values", format="json")
    assert classify_derivative_error(error, stage="execution").code == 3


def test_compiler_comparison_keeps_legacy_normalization_without_wire_policy(monkeypatch):
    from quantumbridge import Circuit
    from quantumbridge.compiler import PassManager, AnalysisPass, PassResult
    from quantumbridge.ir.qb_ir import IRProgram
    class NoChange(AnalysisPass):
        def run(self, circuit):return PassResult(circuit)
    class MetadataMutation(AnalysisPass):
        def run(self, circuit):
            circuit.metadata["number"] = 1
            return PassResult(circuit)
    monkeypatch.setattr(IRProgram, "to_json", lambda *a, **k: pytest.fail("Internal compiler used transport limits"))
    assert not PassManager([NoChange()]).run(Circuit(1).h(0)).changed
    circuit = Circuit(1, metadata={"number": 1.0})
    with pytest.raises(ValueError, match="mutate"):PassManager([MetadataMutation()]).run(circuit)
    assert type(circuit.metadata["number"]) is float
