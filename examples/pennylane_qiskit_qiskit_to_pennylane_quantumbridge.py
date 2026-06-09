# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.
"""Run the Stage 9H Qiskit-to-PennyLane bridge example."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.pennylane_qiskit.examples import run_qiskit_to_pennylane_example


def main() -> None:
    results = run_qiskit_to_pennylane_example()
    native = results["native"]
    upstream = results["upstream"]
    print("QuantumBridge native PennyLane-Qiskit bridge: Qiskit -> PennyLane")
    print(f"probabilities: {native.statevector_probabilities}")
    print(f"counts: {native.counts}")
    print(f"target_operations: {[op['operation'] for op in native.converted_target['operations']]}")
    print(f"upstream_available: {upstream.unsupported_reason is None}")
    print(f"cloud_access: {native.metadata['cloud_access']}")
    print(f"token_read: {native.metadata['token_read']}")
    print(f"hardware_access: {native.metadata['hardware_access']}")
    print(f"full_plugin_parity_claim: {native.metadata['full_plugin_parity_claim']}")
    print(f"production_ready: {native.production_ready}")
    print(native.to_json())


if __name__ == "__main__":
    main()
