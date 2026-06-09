from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import (
    compare_ddsim_like_with_stage9f_simulator,
    run_ddsim_like_counts_native,
)


def test_ddsim_like_counts_executes_and_compares_with_stage9f():
    circuit = Circuit(2, 2).h(0).cx(0, 1).measure(0, 0).measure(1, 1)

    result = run_ddsim_like_counts_native(circuit, shots=64, seed=5)
    comparison = compare_ddsim_like_with_stage9f_simulator(circuit, shots=64, seed=5)

    assert sum(result.counts.values()) == 64
    assert set(result.counts) <= {"00", "11"}
    assert comparison.comparison["comparable"] is True
