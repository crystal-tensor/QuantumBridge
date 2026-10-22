# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Execute native Instruction/Circuit contracts without either upstream SDK."""

import json
import numpy as np
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps, qpy_loads


def main():
    p = qb.Parameter("p")
    owner = qb.Circuit(1, name="rotation").ry(2*p+p.sin(), 0).to_instruction(label="display")
    repeated = owner.repeat(2)
    circuit = qb.Circuit.from_instruction(repeated)
    restored = qpy_loads(qpy_dumps(circuit))[0]
    assert len(restored.operations) == 2
    assert type(restored.operations[0].metadata["instruction_object"]) is qb.Instruction
    node = QNode.from_circuit(restored, qb.PauliZ(0), diff_method="parameter-shift", max_diff=2)
    x = .3
    angle, first, second = 4*x+2*np.sin(x), 4+2*np.cos(x), -2*np.sin(x)
    hessian = -np.cos(angle)*first*first-np.sin(angle)*second
    computed_hessian = float(node.compute_hessian(x))
    assert np.isclose(node(x), np.cos(angle), atol=2e-12, rtol=0)
    assert np.isclose(computed_hessian, hessian, atol=5e-10, rtol=0)
    assert np.isclose(node.compute_hvp(.3, x), .3*hessian, atol=5e-10, rtol=0)
    assert restored.assign_parameters({p: x}, inplace=True) is None
    inverse = repeated.assign_parameters({p: x}).inverse()
    assert type(inverse) is qb.Gate
    np.testing.assert_allclose(Operator(inverse).data @ Operator(restored).data, np.eye(2), atol=4e-13, rtol=0)
    target = qb.Circuit(1)
    assert target.compose(restored, inplace=True) is None
    assert target.inverse().name.endswith("_dg")
    nonunitary = qb.Circuit(1, 1).reset(0).x(0).measure(0, 0).to_instruction().repeat(2)
    sample = qb.StatevectorDevice().run_shots(qb.Circuit(3, 4).append(nonunitary, [2], clbits=[1]), shots=8, seed=7)
    assert sample.counts() == {"0100": 8}
    print(json.dumps({"native_instruction_example": "passed", "repeated_objects": 2,
        "hessian": computed_hessian, "counts": sample.counts(),
        "full_sdk_parity": False}, sort_keys=True))


if __name__ == "__main__": main()
