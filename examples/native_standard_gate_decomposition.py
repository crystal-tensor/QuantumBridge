# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free phase-exact standard definition and explicit QASM Gate lowering."""

import numpy as np

from quantumbridge import AnnotatedOperation, Circuit, ControlModifier, InverseModifier, resolve_annotated_operation
from quantumbridge.circuit_library import standard_gate_object
from quantumbridge.information import Operator
from quantumbridge.serialization import qasm3_dumps, qasm3_loads


def main():
    gate = standard_gate_object("sx")
    expected = np.array([[1+1j, 1-1j], [1-1j, 1+1j]])/2
    np.testing.assert_allclose(gate.to_matrix(), expected, atol=2e-13)
    decomposed = Circuit(1).append(gate, [0]).decompose()
    assert [op.name for op in decomposed.operations] == ["rx"]
    assert abs(decomposed.global_phase-np.pi/4) < 1e-13
    np.testing.assert_allclose(Operator(decomposed).data, expected, atol=2e-13)
    annotated = AnnotatedOperation(gate, [InverseModifier(), ControlModifier(1, 0)])
    resolved = resolve_annotated_operation(annotated)
    source = Circuit(2).append(resolved, [0, 1])
    # This explicit conversion preserves executable Gate mathematics, not the
    # original AnnotatedOperation object type in OpenQASM source.
    restored = qasm3_loads(qasm3_dumps(source))
    controlled = np.eye(4, dtype=complex)
    controlled[:2, :2] = expected.conj().T
    np.testing.assert_allclose(Operator(restored).data, controlled, atol=3e-13)
    print("Native standard SX definition, phase and explicitly resolved QASM mathematics passed.")


if __name__ == "__main__": main()
