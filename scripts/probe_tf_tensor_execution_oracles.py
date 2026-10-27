# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent 70-digit local quantum oracles; stdout only, no SDK imports."""

import json

import mpmath as mp


def rotation(axis, angle):
    c, s = mp.cos(angle/2), mp.sin(angle/2)
    if axis == "x":
        return mp.matrix([[c, -1j*s], [-1j*s, c]])
    if axis == "y":
        return mp.matrix([[c, -s], [s, c]])
    return mp.diag([mp.exp(-0.5j*angle), mp.exp(0.5j*angle)])


def kron(a, b):
    return mp.matrix([[a[i//b.rows, j//b.cols]*b[i%b.rows, j%b.cols]
        for j in range(a.cols*b.cols)] for i in range(a.rows*b.rows)])


def operator(p, q, case):
    body = rotation("z", q)*rotation("x", p) if case["body"] == "su2" else rotation("y", -p)*rotation("z", q*q+mp.mpf(".4"))*rotation("x", p)
    matrix = mp.exp(1j*(mp.mpf(str(case["phase_offset"]))+mp.mpf(str(case["phase_scale"]))*p*q))*body
    eigenvalues, basis = mp.eig(matrix)
    return basis*mp.diag([mp.exp(mp.mpf(str(case["power"]))*mp.log(value)) for value in eigenvalues])*(basis**-1)


def state(p, q, case):
    if case["body"] == "baseline":
        identity = mp.eye(2)
        cnot = mp.matrix([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]])
        return (mp.exp(1j*mp.mpf(".13")*p*q)*kron(rotation("y", q), rotation("x", p*q))*cnot
            *kron(rotation("z", q*q+mp.mpf(".4")), rotation("y", -p))*kron(identity, rotation("x", p))*mp.matrix([1, 0, 0, 0]))
    value = operator(p, q, case)
    if case.get("control") is None:
        return value*mp.matrix([1, 0])
    zero, one = mp.diag([1, 0]), mp.diag([0, 1])
    selected, other = (one, zero) if case["control"] else (zero, one)
    return (kron(selected, value)+kron(other, mp.eye(2)))*mp.matrix([1, 0, 1, 0])/mp.sqrt(2)


def outputs(p, q, case):
    psi = state(p, q, case)
    x, y, z = mp.matrix([[0, 1], [1, 0]]), mp.matrix([[0, -1j], [1j, 0]]), mp.diag([1, -1])
    observables = [z, x] if psi.rows == 2 else [kron(mp.eye(2), z), kron(x, mp.eye(2))]
    if case["body"] == "baseline":
        observables[1] += mp.mpf(".2")*kron(z, y)
    return [mp.re((psi.transpose_conj()*observable*psi)[0]) for observable in observables]


def encode(matrix):
    return [[[float(mp.re(matrix[i, j])), float(mp.im(matrix[i, j]))] for j in range(matrix.cols)] for i in range(matrix.rows)]


def main():
    cases = [dict(name="baseline", body="baseline", point=[0.37, 0.82])]
    for body in ["su2", "requested"]:
        cases.extend(dict(name=body+str(power), body=body, point=[0.37, 0.82], power=power,
            phase_offset=0., phase_scale=0.) for power in [0.5, -0.5, 1.5])
    cases.extend(dict(name="controlled"+str(control), body="requested", point=[0.37, 0.82], power=0.5,
        phase_offset=0., phase_scale=0.13, control=control) for control in [0, 1])
    cases.extend([
        dict(name="wrapped_phase", body="su2", point=[0.37, 0.82], power=0.5, phase_offset=2.9, phase_scale=0.13),
        dict(name="negative_trace", body="su2", point=[4.9, 0.3], power=1.5, phase_offset=0.7, phase_scale=0.13),
        dict(name="near_identity", body="su2", point=[1e-9, -2e-9], power=0.5, phase_offset=0., phase_scale=0.),
    ])
    for case in cases:
        point = tuple(mp.mpf(str(value)) for value in case["point"])
        psi = state(*point, case)
        assert abs(mp.norm(psi)-1) < mp.mpf("1e-50"), "Oracle state is not normalized"
        case["state"] = encode(state(*point, case))
        if case["body"] != "baseline":
            matrix = operator(*point, case)
            assert mp.norm(matrix.transpose_conj()*matrix-mp.eye(2)) < mp.mpf("1e-50"), "Oracle power is not unitary"
            case["operator"] = encode(matrix)
        case["outputs"] = [float(value) for value in outputs(*point, case)]
        case["jacobian"], case["hessians"] = [], []
        for index in range(2):
            def fn(p, q):
                return outputs(p, q, case)[index]
            case["jacobian"].append([float(mp.diff(fn, point, order)) for order in [(1, 0), (0, 1)]])
            case["hessians"].append([[float(mp.diff(fn, point, order)) for order in row]
                for row in [[(2, 0), (1, 1)], [(1, 1), (0, 2)]]])
        case["complex_jacobian"], case["complex_hessians"] = [], []
        for component in range(8):
            def complex_component(p, q):
                matrix = state(p, q, case) if case["body"] == "baseline" else operator(p, q, case)
                index = component % 4
                entry = matrix[index//matrix.cols, index%matrix.cols]
                return mp.re(entry) if component < 4 else mp.im(entry)
            case["complex_jacobian"].append([float(mp.diff(complex_component, point, order)) for order in [(1, 0), (0, 1)]])
            case["complex_hessians"].append([[float(mp.diff(complex_component, point, order)) for order in row]
                for row in [[(2, 0), (1, 1)], [(1, 1), (0, 2)]]])
    print(json.dumps(dict(provenance="Independent explicit 2x2/4x4 matrices and mpmath eig/principal log at70 digits; numerical test differentiation only; no SDK/native/TF import.", cases=cases)))


if __name__ == "__main__":
    with mp.workdps(70):
        main()
