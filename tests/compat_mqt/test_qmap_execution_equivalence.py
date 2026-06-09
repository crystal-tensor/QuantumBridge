from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import (
    compare_original_and_mapped_execution,
    create_line_topology,
    map_quantumbridge_ir_to_topology,
)


def test_qmap_like_original_and_mapped_execution_are_comparable():
    circuit = Circuit(3, 3).h(0).cx(0, 2).measure(0, 0).measure(1, 1).measure(2, 2)
    mapped = map_quantumbridge_ir_to_topology(circuit, create_line_topology(3))

    comparison = compare_original_and_mapped_execution(circuit, mapped, shots=64, seed=19)

    assert comparison.comparison["comparable"] is True
    assert comparison.comparison["l1_probability_distance"] == 0.0
