# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free 100-wire low-entanglement Device HVP; no general efficiency claim."""

import json

from quantumbridge import Hamiltonian, PauliZ, MatrixProductStateDevice
from quantumbridge.execution import DerivativeExecutionRequest, UnifiedExecutionLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


def main():
    def circuit(t, angle):
        t.h(0)
        for wire in range(99): t.cx(wire, wire+1)
        t.ry(angle, 99)
        return t.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_bond_dim=4, max_memory_mb=2, cutoff=0)
    node = TransformProgram((merge_rotations, split_non_commuting))(QNode(circuit, 100, device=device, max_diff=2))
    request = DerivativeExecutionRequest(node, (.3,), derivative_order=2, derivative_kind="hvp", tangent=1.,
        limits=UnifiedExecutionLimits(max_total_memory_bytes=2*1024*1024))
    result = device.execute_derivatives(request)
    output = {"energy": float(result.value), "hvp": float(result.derivative), "status": result.code,
        "tapes": result.receipt["consumed_tapes"], "shots": result.receipt["consumed_shots"],
        "peak_reserved_bytes": result.receipt["peak_memory_bytes"],
        "unavailable": result.receipt["unavailable"]}
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    main()
