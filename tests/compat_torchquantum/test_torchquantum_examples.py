from quantumbridge.compat.torchquantum.examples import (
    run_torchquantum_like_batch_forward_example,
    run_torchquantum_like_classifier_example,
    run_torchquantum_like_layer_example,
)


def test_torchquantum_examples_run():
    layer = run_torchquantum_like_layer_example()
    assert layer["native"].forward_outputs
    batch = run_torchquantum_like_batch_forward_example()
    assert len(batch["native"].forward_outputs) == 3
    classifier = run_torchquantum_like_classifier_example()
    assert classifier["native"].accuracy is not None
