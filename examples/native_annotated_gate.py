# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free deferred binding, ordered open controls and lossless native IR."""

import numpy as np

from quantumbridge import AnnotatedOperation, Circuit, ControlModifier, Parameter, resolve_annotated_operation
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator, Statevector
from quantumbridge.ir.qb_ir import IRProgram


def main():
    p = Parameter("p")
    body = Circuit(1).rz(p, 0)
    body.global_phase = p/3
    operation = AnnotatedOperation(body.to_gate(), ControlModifier(1, 0))
    source = Circuit(2).append(operation, [0, 1])
    restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert restored.parameters == (p,)
    bound = restored.assign_parameters({p: .4})
    expected = np.eye(4, dtype=complex)
    expected[:2, :2] = np.exp(.4j/3)*np.diag(np.exp(1j*np.array([-1, 1])*.2))
    np.testing.assert_allclose(Operator(bound).data, expected, atol=2e-13)
    gate = resolve_annotated_operation(operation.assign_parameters({p: .4}))
    np.testing.assert_allclose(Statevector(gate).data, expected[:, 0], atol=2e-13)
    print("Native annotation, UUID binding, open controlled phase and IR mathematics passed.")


if __name__ == "__main__": main()
