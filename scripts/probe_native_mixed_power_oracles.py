# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Test-only 70-digit oracle generation; prints JSON, writes no files.

Uses the already installed mpmath, not any QuantumBridge or upstream SDK
implementation. High-precision numerical differentiation is an oracle only.
"""

import json

import mpmath as mp


def su2(p, q, power):
    w = mp.acos(mp.cos(p / 2) * mp.cos(q / 2))
    return 1 - 2 * mp.sin(p / 2) ** 2 * (mp.sin(power * w) / mp.sin(w)) ** 2


def two_wire_matrix(p, q, power):
    cp, sp = mp.cos(p / 2), mp.sin(p / 2)
    cq, sq = mp.cos(q / 2), mp.sin(q / 2)
    # RXX(p*q) * (RX(p) tensor RZ(q)), with a coherent global phase.
    rxrz = mp.matrix(
        [
            [cp * (cq - 1j * sq), 0, -1j * sp * (cq - 1j * sq), 0],
            [0, cp * (cq + 1j * sq), 0, -1j * sp * (cq + 1j * sq)],
            [-1j * sp * (cq - 1j * sq), 0, cp * (cq - 1j * sq), 0],
            [0, -1j * sp * (cq + 1j * sq), 0, cp * (cq + 1j * sq)],
        ]
    )
    cosine, sine = mp.cos(p * q / 2), -1j * mp.sin(p * q / 2)
    rxx = cosine * mp.eye(4)
    for row in range(4):
        rxx[row, row ^ 3] = sine
    matrix = mp.exp(1j * mp.mpf(".13") * p * q) * rxx * rxrz
    eigenvalues, eigenvectors = mp.eig(matrix)
    diagonal = mp.diag([mp.exp(power * mp.log(value)) for value in eigenvalues])
    return eigenvectors * diagonal * (eigenvectors**-1)


def two_wire(p, q, power, controlled):
    value = two_wire_matrix(p, q, power)
    if controlled:
        return mp.re(value[0, 0])
    return mp.re(
        sum((1 if row % 2 == 0 else -1) * abs(value[row, 0]) ** 2 for row in range(4))
    )


def derivatives(function, point):
    return {
        "value": float(function(*point)),
        "gradient": [
            float(mp.diff(function, point, order)) for order in ((1, 0), (0, 1))
        ],
        "hessian": [
            [float(mp.diff(function, point, order)) for order in row]
            for row in (((2, 0), (1, 1)), ((1, 1), (0, 2)))
        ],
    }


def main():
    point = (mp.mpf(".37"), mp.mpf(".82"))
    result = {
        "provenance": "Independent explicit SU(2)/4x4 matrices, mpmath 1.3.0, 70 decimal digits; test-only high-precision numerical differentiation, no SDK or native matrix-function imports.",
        "point": [float(value) for value in point],
        "su2": [],
        "two_wire": [],
    }
    for power in (mp.mpf(".5"), mp.mpf("-.5"), mp.mpf("1.5")):
        result["su2"].append(
            {"power": float(power), **derivatives(lambda p, q: su2(p, q, power), point)}
        )
        matrix = two_wire_matrix(*point, power)
        encoded = [
            [[float(mp.re(matrix[r, c])), float(mp.im(matrix[r, c]))] for c in range(4)]
            for r in range(4)
        ]
        result["two_wire"].append(
            {
                "power": float(power),
                "matrix": encoded,
                "ordinary": derivatives(
                    lambda p, q: two_wire(p, q, power, False), point
                ),
                "controlled": derivatives(
                    lambda p, q: two_wire(p, q, power, True), point
                ),
            }
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    with mp.workdps(70):
        main()
