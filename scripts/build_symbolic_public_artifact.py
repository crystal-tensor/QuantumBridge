# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Package literal public-call JSON records without rewriting observed outcomes."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs=2, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    versions = {}
    for source in options.inputs:
        records = [json.loads(line) for line in source.read_text().splitlines()]
        version = records[0]["qiskit_version"]
        if version not in {"2.4.1", "2.6.0"} or version in versions:
            raise ValueError("Expected independent observations from 2.4.1 and 2.6.0.")
        names = [record["name"] for record in records[1:]]
        if len(names) != len(set(names)) or len(names) < 25:
            raise ValueError("Public records must have unique meaningful scenario names.")
        versions[version] = {"scenario_count": len(names), "records": records[1:]}
    if set(versions) != {"2.4.1", "2.6.0"}: raise ValueError("Missing public version.")
    result = {
        "classification": "literal_public_observations_not_upstream_source_or_complete_parity",
        "sources": ["https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.ParameterExpression",
                    "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qpy"],
        "native_boundaries": [
            "Native full bind returns a number, unlike the public constant expression result.",
            "Native constant gradients remain expressions so repeated gradient calls are defined.",
            "Native expression string-key binding and explicit allow_partial are extensions.",
            "Native sign has a guarded zero derivative away from zero; public sign gradient rejects.",
            "No public sqrt method exists in either observed version; use exponentiation.",
            "Native limits and error classes are not identical to the public exception ABI.",
            "SymPy export is optional/outward only and loses UUID identity.",
            "Guarded nonsmooth derivative nodes reject QPY/QASM export instead of dropping guards.",
        ],
        "versions": versions,
        "complete_parameter_expression_parity": False,
        "complete_core_replacement": False,
    }
    options.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({version: value["scenario_count"] for version, value in versions.items()}))


if __name__ == "__main__": main()
