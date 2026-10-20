"""Deterministic SDK-free training with a real two-qubit entangling template."""
import numpy as np
from quantumbridge import templates
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def program(tape,weights):
    templates.StronglyEntanglingLayers(weights,[0,1]).apply(tape)
    return tape.expval(PauliZ(1))


node=QNode(program,2)
weights=np.arange(12,dtype=float).reshape(2,2,3)/17+.1
initial=(node(weights)+1)**2
for _ in range(80):
    value=node(weights)
    weights-=.12*2*(value+1)*node.gradient(weights,method="adjoint")
final=(node(weights)+1)**2
assert final<initial/100
print({"initial_loss":initial,"final_loss":final,"steps":80,"gradient":"native adjoint","entangling_wires":2})
