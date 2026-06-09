from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import (
    create_line_topology,
    map_quantumbridge_ir_to_topology,
    run_ddsim_like_counts_native,
)


def test_mqt_native_paths_do_not_access_cloud_tokens_or_hardware():
    circuit = Circuit(3, 3).h(0).cx(0, 2).measure(0, 0).measure(1, 1).measure(2, 2)
    simulation = run_ddsim_like_counts_native(circuit, shots=16, seed=1)
    mapping = map_quantumbridge_ir_to_topology(circuit, create_line_topology(3))

    for result in (simulation, mapping):
        assert result.metadata["cloud_access"] is False
        assert result.metadata["token_read"] is False
        assert result.metadata["hardware_access"] is False
