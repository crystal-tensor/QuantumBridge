# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free unified preflight failure with structured, released resources."""

import json

from quantumbridge import StatevectorDevice
from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
from examples.native_device_derivatives import request


def main():
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1))
    result = StatevectorDevice().execute_derivatives(request(), ledger=ledger, return_status=True)
    assert result.code == 3 and result.receipt["live_memory_bytes"] == 0
    output = {"status": result.code, "category": result.error.category,
        "estimated": result.error.estimated, "limit": result.error.limit,
        "consumed_shots": result.receipt["consumed_shots"],
        "live_bytes_after_failure": result.receipt["live_memory_bytes"]}
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    main()
