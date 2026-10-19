# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Optional Torch supplies the optimizer/graph, not the quantum execution.

import torch
from quantumbridge import PauliZ
from quantumbridge.qml import NativeQNode


def program(tape, angles):
    tape.ry(angles[0], 0)
    tape.ry(angles[1], 1)
    tape.cx(0, 1)
    return tape.expval(PauliZ(1))


def main():
    node = NativeQNode(program, 2, interface="torch", diff_method="parameter-shift")
    angles = torch.tensor([1., .7], dtype=torch.float64, requires_grad=True)
    optimizer = torch.optim.SGD([angles], lr=.15)
    initial, trace = node(angles).detach().item(), []
    for _ in range(30):
        optimizer.zero_grad()
        loss = node(angles)
        loss.backward()
        trace.append(angles.grad.tolist())
        optimizer.step()
    final = node(angles).detach().item()
    print({"provenance": "QuantumBridge native parameter-shift VJP + Torch SGD",
           "initial_loss": initial, "final_loss": final, "angles": angles.detach().tolist(),
           "first_gradient": trace[0], "last_gradient": trace[-1], "steps": len(trace)})
    assert final < initial - 1


if __name__ == "__main__": main()
