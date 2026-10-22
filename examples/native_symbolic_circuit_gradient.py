# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native vector -> symbolic math -> Instruction -> state -> quantum calculus."""

import json
import numpy as np

from quantumbridge import Circuit, ParameterVector, PauliZ
from quantumbridge.information import Statevector, DensityMatrix
from quantumbridge.qml import QNode


def build():
    vector = ParameterVector("v", 2)
    p, q = vector
    angle = ((p*q+p*p).sin()+(2*p-q).exp()).log()
    child = Circuit(2).ry(angle, 0).rx(p*q, 1).cz(0, 1)
    child.global_phase = p.sin()/7
    return vector, Circuit(2).append(child.to_instruction(), (0, 1))


def reference(point):
    p, q = point
    a, b = p*q+p*p, 2*p-q
    da, db = np.array([q+2*p, p]), np.array([2., -1.])
    s = np.sin(a)+np.exp(b)
    ds = np.cos(a)*da+np.exp(b)*db
    hs = -np.sin(a)*np.outer(da, da)+np.cos(a)*np.array([[2., 1.], [1., 0.]])+np.exp(b)*np.outer(db, db)
    f, df, hf = np.log(s), ds/s, hs/s-np.outer(ds, ds)/s**2
    g, dg, hg = p*q, np.array([q, p]), np.array([[0., 1.], [1., 0.]])
    value = np.cos(f)*np.cos(g)
    gradient = -np.sin(f)*np.cos(g)*df-np.cos(f)*np.sin(g)*dg
    hessian = (-np.cos(f)*np.cos(g)*(np.outer(df, df)+np.outer(dg, dg))
               +np.sin(f)*np.sin(g)*(np.outer(df, dg)+np.outer(dg, df))
               -np.sin(f)*np.cos(g)*hf-np.cos(f)*np.sin(g)*hg)
    return value, gradient, hessian


def main():
    vector, circuit = build()
    point = np.array([.4, -.2])
    expected, gradient, _ = reference(point)
    node = QNode.from_circuit(circuit, PauliZ(0).tensor(PauliZ(1)), diff_method="adjoint", max_diff=2)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=8e-11, rtol=0)
    assert abs(node(point)-expected) < 2e-14
    bound = circuit.assign_parameters({vector[0]: point[0]}).assign_parameters({vector[1]: point[1]})
    state = Statevector(bound)
    density = DensityMatrix(bound)
    np.testing.assert_allclose(density.data, np.outer(state.data, state.data.conj()), atol=2e-15, rtol=0)
    print(json.dumps({"value": node(point), "jacobian": node.compute_jacobian(point).tolist(),
                     "state_real": state.data.real.tolist(), "state_imag": state.data.imag.tolist()}))


if __name__ == "__main__": main()
