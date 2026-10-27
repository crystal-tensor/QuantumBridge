# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent whole-circuit70-digit scalar/state fixtures; stdout only."""

import json
import sys

import mpmath as mp

from scripts.probe_tf_tensor_execution_oracles import encode, rotation


def apply(state, matrix, wires, width):
    output = mp.matrix(1 << width, 1)
    for column in range(1 << width):
        local_column = sum(((column >> (width-1-wire)) & 1) << (len(wires)-1-index) for index, wire in enumerate(wires))
        for local_row in range(1 << len(wires)):
            row = column
            for index, wire in enumerate(wires):
                mask = 1 << (width-1-wire)
                row = (row & ~mask) | (((local_row >> (len(wires)-1-index)) & 1) << (width-1-wire))
            output[row] += matrix[local_row, local_column]*state[column]
    return output


def local_root(p, q):
    matrix = rotation("x", p)*rotation("z", q*q+mp.mpf(".4"))*rotation("y", -p)
    return (mp.eye(2)+matrix)/mp.sqrt(2+mp.re(matrix[0, 0]+matrix[1, 1]))


def state(p, q, case):
    width = case["width"]
    psi = mp.matrix([1]+[0]*((1 << width)-1))
    root = local_root(p, q)
    h = mp.matrix([[1, 1], [1, -1]])/mp.sqrt(2)
    x = mp.matrix([[0, 1], [1, 0]])
    cx = mp.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    if case["name"] == "requested_reverse":
        return apply(psi, root, [1], width)
    psi = apply(psi, h, [0], width)
    if case["name"] == "full_entangling":
        psi = apply(psi, cx, [0, 3], width)
        psi = apply(psi, root, [2], width)
        psi = apply(psi, rotation("y", p*q), [0], width)
        psi = apply(psi, cx, [2, 1], width)
        psi = apply(psi, rotation("z", p-q), [3], width)
    else:
        psi = apply(psi, x, [2], width)
        controlled = mp.eye(8)
        prefix = 2 if case["name"] == "open_control" else 3
        for row in range(2):
            for column in range(2):
                controlled[2*prefix+row, 2*prefix+column] = root[row, column]
        psi = apply(psi, controlled, [2, 0, 3], width)
        psi = apply(psi, cx, [3, 1], width)
    return mp.exp(mp.mpf(".17")*1j*p*q)*psi


def outputs(p, q, case):
    psi = state(p, q, case)
    x, y, z = mp.matrix([[0, 1], [1, 0]]), mp.matrix([[0, -1j], [1j, 0]]), mp.diag([1, -1])
    target = 1 if case["name"] == "requested_reverse" else 2 if case["name"] == "full_entangling" else 3
    first = apply(psi, z, [target], case["width"])
    other = apply(psi, x, [0], case["width"])
    if case["name"] == "requested_reverse":
        other = apply(psi, x, [1], case["width"])
    elif case["name"] == "full_entangling":
        other = apply(other, x, [3], case["width"])
        extra = apply(apply(psi, y, [1], case["width"]), z, [2], case["width"])
        other += mp.mpf(".2")*extra
    return [mp.re((psi.transpose_conj()*value)[0]) for value in (first, other)]


def main():
    cases = [dict(name=name, width=2 if name == "requested_reverse" else 4, point=[0.37, 0.82])
        for name in ("requested_reverse", "full_entangling", "open_control", "closed_control")]
    for case in cases:
        point = tuple(mp.mpf(str(value)) for value in case["point"])
        root = local_root(*point)
        original = rotation("x", point[0])*rotation("z", point[1]**2+mp.mpf(".4"))*rotation("y", -point[0])
        assert mp.norm(root*root-original) < mp.mpf("1e-50")
        psi = state(*point, case)
        assert abs(mp.norm(psi)-1) < mp.mpf("1e-50")
        case["state"] = encode(psi)
        case["outputs"] = [float(value) for value in outputs(*point, case)]
        case["jacobian"], case["hessians"] = [], []
        for index in range(2):
            def value(p, q):
                return outputs(p, q, case)[index]
            case["jacobian"].append([float(mp.diff(value, point, order)) for order in ((1, 0), (0, 1))])
            case["hessians"].append([[float(mp.diff(value, point, order)) for order in row]
                for row in (((2, 0), (1, 1)), ((1, 1), (0, 2)))])
        case["state_jacobian"], case["state_hessians"] = [], []
        for component in range(2*len(psi)):
            def entry(p, q):
                value = state(p, q, case)[component % len(psi)]
                return mp.re(value) if component < len(psi) else mp.im(value)
            case["state_jacobian"].append([float(mp.diff(entry, point, order)) for order in ((1, 0), (0, 1))])
            case["state_hessians"].append([[float(mp.diff(entry, point, order)) for order in row]
                for row in (((2, 0), (1, 1)), ((1, 1), (0, 2)))])
    assert not any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane", "tensorflow"} for name in sys.modules)
    print(json.dumps(dict(provenance="Independent70-digit SU(2) principal square root and explicit basis-state wire maps; no QB/SDK/TF import; test-only differentiation.", cases=cases)))


if __name__ == "__main__":
    with mp.workdps(70):
        main()
