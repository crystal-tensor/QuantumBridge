"""SDK-free template input preprocessing and native quantum differentiation."""
import numpy as np
from quantumbridge import templates
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def program(tape,theta):
    templates.AngleEmbedding([np.sin(theta),2*theta],[0,1],rotation="Y").apply(tape)
    tape.cx(0,1)
    return tape.expval(PauliZ(1))


node=QNode(program,2)
theta=.37
expected=-np.sin(np.sin(theta))*np.cos(theta)*np.cos(2*theta)-2*np.cos(np.sin(theta))*np.sin(2*theta)
assert abs(node.gradient(theta,method="adjoint")-expected)<1e-10
assert abs(node.gradient(theta,method="parameter-shift")-expected)<1e-10
print({"expectation":node(theta),"input_gradient":expected,"implementation":"native","shared_nonlinear_input":True})
