from quantumbridge.compat.mqt.examples import (
    run_mqt_core_like_example,
    run_mqt_ddsim_like_example,
    run_mqt_qmap_like_example,
)


def test_mqt_examples_return_native_and_upstream_results():
    core = run_mqt_core_like_example()
    ddsim = run_mqt_ddsim_like_example(shots=32, seed=3)
    qmap = run_mqt_qmap_like_example(shots=32, seed=4)

    assert core["native"].to_json()
    assert ddsim["counts"].counts
    assert qmap["mapping"].swap_count == 2
    assert core["upstream"].mode == "upstream_passthrough"
