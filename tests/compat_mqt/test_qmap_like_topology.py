from quantumbridge.compat.mqt import (
    create_coupling_graph,
    create_fully_connected_topology,
    create_line_topology,
    create_ring_topology,
    initial_layout_trivial,
    validate_coupling_graph,
)


def test_qmap_like_topologies_validate():
    line = create_line_topology(3)
    ring = create_ring_topology(3)
    full = create_fully_connected_topology(3)
    custom = create_coupling_graph([(0, 2), (1, 2)], 3)

    assert validate_coupling_graph(line)["topology"] == "line"
    assert len(ring["edges"]) == 3
    assert len(full["edges"]) == 3
    assert custom["num_qubits"] == 3
    assert initial_layout_trivial(2, 3) == {0: 0, 1: 1}
