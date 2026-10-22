# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Retain literal public observations, not claims of native implementation."""

import json
from pathlib import Path
import sys


def main():
    destination, *sources = sys.argv[1:]
    versions = {}
    for source in sources:
        lines = [json.loads(line) for line in Path(source).read_text().splitlines() if line]
        version = lines[0]["qiskit_version"]
        records = lines[1:]
        if len({item["scenario"] for item in records}) != len(records):
            raise ValueError("Public scenario names must be distinct.")
        versions[version] = {"scenario_count": len(records), "records": records}
    if set(versions) != {"2.4.1", "2.6.0"}: raise ValueError("Both target public versions are required.")
    document = {"status": "PUBLIC_OBSERVED_NOT_FULL_PARITY", "reference_mode": "public_calls_only",
                "notes": "Literal outcomes are not newly implemented SDK functions; native bool/error/annotation/structure differences remain Partial.",
                "versions": versions}
    Path(destination).write_text(json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True)+"\n")
    print(json.dumps({version: item["scenario_count"] for version, item in versions.items()}, sort_keys=True))


if __name__ == "__main__": main()
