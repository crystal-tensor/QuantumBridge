# This file is independently implemented for QuantumBridge SDK.
# No Qiskit Nature tutorial code or upstream source was copied.
"""Run the Stage 9D LiH executable chemistry slice."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantumbridge.compat.qiskit_nature import run_lih_native, run_lih_upstream_passthrough


def main() -> None:
    native = run_lih_native()
    upstream = run_lih_upstream_passthrough()
    print("QuantumBridge native LiH result:")
    print(native.to_json())
    print("Warnings:")
    for warning in native.warnings:
        print(f"- {warning}")
    print("Provenance:")
    print(native.provenance)
    print("Optional upstream LiH passthrough:")
    print(upstream.to_json())
    print("No cloud, no token, no real hardware, not production chemistry.")


if __name__ == "__main__":
    main()
