from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import create_line_topology, map_quantumbridge_ir_to_topology, mapping_cost


def test_qmap_like_routing_inserts_swaps_for_unavailable_cnot():
    circuit = Circuit(3, 3).h(0).cx(0, 2).measure(0, 0).measure(1, 1).measure(2, 2)

    result = map_quantumbridge_ir_to_topology(circuit, create_line_topology(3))
    cost = mapping_cost(result)

    assert result.swap_count == 2
    assert any(op["name"] == "swap" for op in result.operations)
    assert result.final_layout == {0: 0, 1: 1, 2: 2}
    assert cost["swap_count"] == 2
