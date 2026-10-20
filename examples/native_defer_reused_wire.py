# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""A reused measured wire needs a separate quantum record, not naive deletion."""

import numpy as np
from quantumbridge.qml import QNode
from quantumbridge.transforms import defer_measurements


def main():
    def circuit(t):
        t.h(0)
        record = t.measure(0)
        t.h(0)
        t.cond(record, lambda branch: branch.x(1))
        return {"probs": t.probs([0, 1]), "reduced_density": t.density_matrix([0, 1])}
    def naive(t):
        t.h(0)
        t.h(0)
        t.cx(0, 1)
        return t.probs([0, 1])
    original, deferred = QNode(circuit, 2), defer_measurements(QNode(circuit, 2))
    before, after = original(), deferred()
    np.testing.assert_allclose(after["reduced_density"], before["reduced_density"], atol=1e-12)
    assert all(abs(value - .25) < 1e-12 for value in after["probs"].values())
    assert abs(QNode(naive, 2)()["00"] - 1.) < 1e-12
    child = deferred._construct((), {}).prepared.tapes[0].circuit
    print({"dynamic_probs": before["probs"], "deferred_probs": after["probs"],
           "incorrect_naive_probs": QNode(naive, 2)(),
           "actual_coherent_gates": [(op.name, op.wires) for op in child.operations],
           "reduced_density_error": float(np.max(np.abs(after["reduced_density"] - before["reduced_density"]))),
           "mixed_state_purity": float(np.trace(after["reduced_density"] @ after["reduced_density"]).real)})
    print("Logical reduced states agree; an expanded pure state is not the original nonselective mixed state.")


if __name__ == "__main__":
    main()
