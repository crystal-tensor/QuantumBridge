# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Simultaneous substitutions preserve native parameter/vector identities."""

import json

from quantumbridge import ParameterVector


def main():
    vector = ParameterVector("v", 2)
    p, q = vector
    expression = p-2*q
    swapped = expression.subs({p: q, q: p})
    crossed = expression.subs({p: p+q, q: p-q})
    values = {p: .4, q: -.2}
    assert swapped.bind(values) == -1.
    assert abs(crossed.bind(values)+1.) < 1e-15
    assert set(swapped.parameters) == set(vector)
    assert all(parameter.vector is vector for parameter in swapped.parameters)
    print(json.dumps({"original": expression.bind(values), "simultaneous_swap": swapped.bind(values),
                     "crossed": crossed.bind(values), "free_uuids": sorted(p.uuid for p in swapped.parameters)}))


if __name__ == "__main__": main()
