# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free custom-definition transport and independent derivative checks."""

import json
import warnings

import numpy as np

from quantumbridge import Circuit, Parameter, PauliX
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir import IRProgram
from quantumbridge.qml import QNode
from quantumbridge.serialization import qasm2_dumps, qasm3_dumps, qasm3_loads, qpy_dumps, qpy_loads, UnsupportedFeature


def main():
    theta = Parameter("theta")
    f = theta.sin()+2*theta
    inner = Circuit(1, name="inner").rz(f, 0)
    inner.global_phase = f/3
    outer = Circuit(1, name="outer").append(inner.to_gate(), [0])
    source = Circuit(2).h(0).append(outer.to_gate().control(), [0, 1])
    with warnings.catch_warnings(record=True) as messages:
        warnings.simplefilter("always")
        text = qasm3_dumps(source, allow_metadata_loss=True)
    restored = {
        "ir": circuit_from_ir(IRProgram.from_json(source.to_ir().to_json())),
        "qasm3": qasm3_loads(text),
        "qpy13": qpy_loads(qpy_dumps(source))[0],
    }
    x = .37
    value = np.sin(x)+2*x
    first = np.cos(x)+2
    second = -np.sin(x)
    expected_gradient = -np.sin(value/6)*first/6
    expected_hessian = -np.cos(value/6)*first*first/36-np.sin(value/6)*second/6
    h = np.array([[1, 1], [1, -1]])/np.sqrt(2)
    expected_operator = np.diag([1, 1, np.exp(-1j*value/6), np.exp(5j*value/6)])@np.kron(h, np.eye(2))
    results = {}
    for format, circuit in restored.items():
        bound = circuit.bind({"theta": x})
        error = float(np.max(np.abs(Operator(bound).data-expected_operator)))
        assert error < 2e-12
        node = QNode.from_circuit(circuit, PauliX(0), diff_method="parameter-shift", max_diff=2)
        gradient = float(np.asarray(node.compute_jacobian(x)))
        hvp = float(np.asarray(node.compute_hvp(.3, x)))
        assert abs(float(node(x))-np.cos(value/6)) < 2e-12
        assert abs(gradient-expected_gradient) < 1e-10
        assert abs(hvp-.3*expected_hessian) < 2e-10
        results[format] = {"operator_max_error": error, "gradient": gradient, "hvp": hvp}
    phase_gate = Circuit(1).x(0)
    phase_gate.global_phase = .3
    try: qasm2_dumps(Circuit(1).append(phase_gate.to_gate(), [0]))
    except UnsupportedFeature: qasm2_phase = "UNSUPPORTED: nonzero internal global phase"
    else: raise AssertionError("QASM2 must not silently drop internal phase.")
    print(json.dumps({"results": results, "qasm3_metadata_warnings": [str(item.message) for item in messages],
                      "qasm2_boundary": qasm2_phase, "full_sdk_parity": False}, sort_keys=True))


if __name__ == "__main__": main()
