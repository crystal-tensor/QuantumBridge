# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Run with PYTHONPATH=. python examples/native_symbolic_functions.py."""

import json
import math

from quantumbridge import Parameter


def main():
    p, q = Parameter("p"), Parameter("q")
    expression = (p*q+p*p).sin()+(2*p-q).exp()
    records = []
    for first, second in ((.4, -.2), (-.7, .5), (.8, 1.1)):
        a, b = first*second+first*first, 2*first-second
        partial = expression.bind({p: first})
        value = partial.bind({q: second})
        derivative = expression.gradient(p).bind({p: first, q: second})
        assert abs(value-(math.sin(a)+math.exp(b))) < 1e-13
        assert abs(derivative-((second+2*first)*math.cos(a)+2*math.exp(b))) < 1e-13
        records.append({"point": [first, second], "value": value, "dp": derivative})
    print(json.dumps(records))


if __name__ == "__main__": main()
