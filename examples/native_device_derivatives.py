# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free native Circuit -> Device directional second-adjoint example."""

import json

from quantumbridge import Circuit, Parameter, PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionRequest


def request():
    circuit = Circuit(1).ry(Parameter("theta"), 0)
    return DerivativeExecutionRequest(circuit, [.3], observable=PauliZ(0),
        derivative_order=2, derivative_kind="hvp", method="second_adjoint", tangent=[.4])


def main():
    result = StatevectorDevice().execute_derivatives(request())
    output = {"value": float(result.value), "hvp": result.derivative.tolist(),
        "status": result.code, "method": result.metadata["second_order_method"],
        "tapes": result.receipt["consumed_tapes"], "shots": result.receipt["consumed_shots"],
        "peak_reserved_bytes": result.receipt["peak_memory_bytes"],
        "memory_scope": result.receipt["scope"]}
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    main()
