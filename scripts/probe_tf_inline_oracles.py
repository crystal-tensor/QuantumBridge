# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent70-digit second-point native-inline references; stdout only."""

import json
import sys

import mpmath as mp

from scripts.probe_tf_whole_qnode_oracles import encode, outputs, state


def main():
    cases = []
    for point in ((".37", ".82"), (".41", ".91")):
        p = tuple(mp.mpf(x) for x in point)
        case = dict(name="requested_reverse", width=2, point=[float(x) for x in p])
        case["outputs"] = [float(x) for x in outputs(*p, case)]
        case["state"] = encode(state(*p, case))
        functions = [lambda a, b, i=i: outputs(a, b, case)[i] for i in range(2)]
        parts = [lambda a, b, i=i: (mp.re if i < 4 else mp.im)(state(a, b, case)[i % 4]) for i in range(8)]
        for prefix, entries in (("", functions), ("state_", parts)):
            case[prefix+"jacobian"] = [[float(mp.diff(f, p, order)) for order in ((1, 0), (0, 1))] for f in entries]
            case[prefix+"hessians"] = [[[float(mp.diff(f, p, order)) for order in row]
                for row in (((2, 0), (1, 1)), ((1, 1), (0, 2)))] for f in entries]
        cases.append(case)
    assert not any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane", "tensorflow"} for name in sys.modules)
    print(json.dumps(dict(provenance="Independent70-digit SU(2) closed square root, explicit basis maps and test-only mpmath differentiation; no QB/SDK/TF imports.", cases=cases)))


if __name__ == "__main__":
    with mp.workdps(70):
        main()
