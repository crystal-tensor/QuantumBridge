# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native dynamic feedback and its actual coherent record circuit."""

import numpy as np
from quantumbridge.qml import QNode
from quantumbridge.transforms import defer_measurements
from quantumbridge.utils.math import PauliZ


def main():
    def circuit(t, theta):
        t.ry(theta, 0)
        record = t.measure(0)
        t.cond(record, lambda branch: branch.x(1))
        return {"energy": t.expval(PauliZ(1)), "record_and_target": t.probs([1], records=record)}
    original = QNode(circuit, 2)
    deferred = defer_measurements(QNode(circuit, 2))
    before, after = original(.37), deferred(.37)
    assert abs(before["energy"] - after["energy"]) < 1e-12
    assert tuple(after["record_and_target"]) == tuple(before["record_and_target"])
    np.testing.assert_allclose(list(after["record_and_target"].values()), list(before["record_and_target"].values()), atol=1e-12, rtol=0)
    gradient = deferred.jacobian(.37)["energy"]
    assert abs(gradient + np.sin(.37)) < 1e-12
    print({"dynamic": before, "coherent": after, "native_gradient": gradient,
           "record_mapping": deferred.last_metadata["deferred_measurements"][0]})


if __name__ == "__main__":
    main()
