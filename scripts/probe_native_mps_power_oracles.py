# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent test-only 70-digit 2x2 math; prints JSON, never writes files."""

import json

import mpmath as mp


def rotation(axis, angle):
    c, s = mp.cos(angle/2), mp.sin(angle/2)
    if axis == "x":
        return mp.matrix([[c, -1j*s], [-1j*s, c]])
    if axis == "y":
        return mp.matrix([[c, -s], [s, c]])
    return mp.diag([mp.exp(-0.5j*angle), mp.exp(0.5j*angle)])


def power(matrix, exponent):
    # Closed SU(2) identity, independent of block-Frechet implementations.
    center = mp.re(matrix[0, 0]+matrix[1, 1])/2
    angle = mp.acos(center)
    return mp.cos(exponent*angle)*mp.eye(2)+mp.sin(exponent*angle)/mp.sin(angle)*(matrix-center*mp.eye(2))


def requested(p, q, exponent):
    return power(rotation("y", -p)*rotation("z", q*q+mp.mpf(".4"))*rotation("x", p), exponent)


def moment(matrix):
    return mp.re(abs(matrix[0, 0])**2-abs(matrix[1, 0])**2)


def derivatives(function, point):
    return dict(value=float(function(*point)),
        gradient=[float(mp.diff(function, point, order)) for order in ((1, 0), (0, 1))],
        hessian=[[float(mp.diff(function, point, order)) for order in row]
                 for row in (((2, 0), (1, 1)), ((1, 1), (0, 2)))])


def chain(point):
    value = mp.eye(2)
    for i in range(0, len(point), 2):
        value = power(rotation("z", point[i+1])*rotation("x", point[i]), mp.mpf(".5"))*value
    return moment(value)


def main():
    point = [mp.mpf(".37"), mp.mpf(".82")]
    output = dict(provenance="Independent SU(2) closed powers; mpmath 1.3.0 at70 digits; test-only numerical derivatives; no SDK/native imports.", point=[float(p) for p in point], requested=[])
    for exponent in [mp.mpf(".5"), mp.mpf("-.5"), mp.mpf("1.5")]:
        matrix = requested(*point, exponent)
        output["requested"].append(dict(power=float(exponent),
            matrix=[[[float(mp.re(matrix[i, j])), float(mp.im(matrix[i, j]))] for j in range(2)] for i in range(2)],
            **derivatives(lambda p, q: moment(requested(p, q, exponent)), point)))
    x = [mp.mpf(i)/10 for i in range(2, 10)]
    direction = [mp.mpf(s) for s in [".2", "-.1", ".3", ".4", "-.2", ".1", ".5", "-.3"]]
    hvp = []
    for index in range(8):
        def directional(t):
            return mp.diff(lambda r: chain([a+t*b+(r if j == index else 0)
                for j, (a, b) in enumerate(zip(x, direction))]), 0)
        hvp.append(float(mp.diff(directional, 0)))
    output["eight"] = dict(point=[float(v) for v in x], direction=[float(v) for v in direction], value=float(chain(x)), hvp=hvp)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    with mp.workdps(70):
        main()
