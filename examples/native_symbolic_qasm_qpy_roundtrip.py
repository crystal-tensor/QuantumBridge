# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real QASM3 source and QPY v13 binary preserve supported native functions."""

import json
import numpy as np

from quantumbridge import Circuit, Parameter, MatrixProductStateDevice
from quantumbridge.information import Operator
from quantumbridge.serialization import qasm3_dumps, qasm3_loads, qpy_dumps, qpy_loads


def main():
    p, q = Parameter("theta"), Parameter("phi")
    circuit = Circuit(2).ry((p*q+p*p).sin()+(2*p-q).exp(), 0).rx(q.log(), 1).cz(0, 1)
    circuit.global_phase = p.sin()/7
    source, binary = qasm3_dumps(circuit), qpy_dumps(circuit)
    assert binary.startswith(b"QISKIT")
    expected = Operator(circuit.bind({p: .4, q: .2})).data
    for restored in (qasm3_loads(source), qpy_loads(binary)[0]):
        bound = restored.assign_parameters({"theta": .4}).assign_parameters({"phi": .2})
        np.testing.assert_allclose(Operator(bound).data, expected, atol=5e-15, rtol=0)
        state = MatrixProductStateDevice().statevector(bound)
        np.testing.assert_allclose(state, expected[:, 0], atol=5e-15, rtol=0)
    print(json.dumps({"qasm3": source, "qpy_bytes": len(binary), "full_complex_matrix_max_error":
                     float(np.max(np.abs(Operator(qpy_loads(binary)[0].bind({"theta": .4, "phi": .2})).data-expected)))}))


if __name__ == "__main__": main()
