# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent observable normalization, shaped PUBs and execution admission."""

import gc
import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, Pauli, SparsePauliOperator
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.primitives import BindingsArray, EstimatorPub, ObservablesArray
from quantumbridge.utils.math import PauliY


def test_observable_shapes_simplified_coefficients_and_native_types():
    value = ObservablesArray([["IZ"], [{"ZI": 2, "XX": -0.5}]])
    assert value.shape == (2, 1) and value.size == 2 and value.num_qubits == 2
    assert value.tolist() == [[{"IZ": 1.0}], [{"ZI": 2.0, "XX": -0.5}]]
    assert ObservablesArray(Pauli("-Z")).tolist() == {"Z": -1.0}
    # SparsePauliOperator is the existing q0-first native operator, not a
    # renamed public SparsePauliOp: preserve its physical wire interpretation.
    sparse = SparsePauliOperator.from_list([("XI", 1), ("XI", 2), ("IZ", -1)])
    assert ObservablesArray(sparse).tolist() == {"IX": 3.0, "ZI": -1.0}
    assert ObservablesArray(PauliY(2)).tolist() == {"YII": 1.0}
    assert ObservablesArray("-Z").tolist() == {"-Z": 1.0}
    assert ObservablesArray("-Z").num_qubits == 2
    with pytest.raises(ValueError, match="Empty"):
        ObservablesArray({"Z": 1e-8})


def test_observable_views_reshape_and_export_do_not_mutate_inputs():
    source = {"Z": 2.0}
    value = ObservablesArray([[source], ["X"]])
    source["Z"] = 99
    assert value.tolist() == [[{"Z": 2.0}], [{"X": 1.0}]]
    assert value.reshape(2).shape == (2,) and value.ravel().shape == (2,)
    assert value[0].shape == (1,)
    assert value[1, 0] == {"X": 1.0}
    exported = value.tolist()
    exported[0][0]["Z"] = 50
    assert value[0, 0] == {"Z": 2.0}
    assert value.copy().equivalent(value)


@pytest.mark.parametrize("value", [["Z", "IZ"], [["Z"], ["X", "I"]], {"Z": 1j}, {"Q": 1}, {"Z": 0}, {}])
def test_invalid_observable_width_shape_coefficient_and_empty_sum(value):
    with pytest.raises((ValueError, TypeError)):
        ObservablesArray(value)


def test_empty_observable_axes_and_finite_representation_boundary():
    empty = ObservablesArray(np.empty((3, 0), dtype=object), num_qubits=3)
    assert empty.shape == (3, 0) and empty.num_qubits == 3 and empty.tolist() == [[], [], []]
    value = ObservablesArray({"Z": float("nan")})
    assert np.isnan(value.tolist()["Z"])
    with pytest.raises(ValueError, match="finite"):
        value.validate_for_execution()


def test_estimator_pub_broadcast_coercion_and_precision_precedence():
    theta, phi = Parameter("theta"), Parameter("phi")
    circuit = Circuit(3).ry(theta, 2).rz(phi, 2)
    values = np.array([[[0.1, 0.2], [0.3, 0.4]], [[0.5, 0.6], [0.7, 0.8]]])
    pub = EstimatorPub.coerce((circuit, [[["ZII"]], [["XII"]], [["YII"]]], values, 0.2), precision=0.3)
    assert pub.shape == (3, 2, 2) and pub.size == 12 and pub.precision == 0.2
    assert pub.parameter_values.shape == (2, 2) and pub.observables.shape == (3, 1, 1)
    assert EstimatorPub.coerce(pub, precision=0.8) is pub
    assert EstimatorPub.coerce((circuit, "ZII", values), precision=0.3).precision == 0.3
    with pytest.raises(ValueError, match="broadcast"):
        EstimatorPub.coerce((circuit, ["ZII", "XII", "YII"], values))
    with pytest.raises(ValueError):
        EstimatorPub.coerce((circuit, "Z", values))
    assert isinstance(pub.parameter_values, BindingsArray)
    with pytest.raises(ValueError, match="width"):
        EstimatorPub.coerce((Circuit(1), []))


def test_observable_owned_shape_views_keep_the_same_payload_lease():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        value = ObservablesArray([["Z"], ["X"]])
        view = value.reshape(2)
    before = ledger.receipt()["live_memory_bytes"]
    assert before > 0
    del value
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == before
    assert view.tolist() == [{"Z": 1.0}, {"X": 1.0}]
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
