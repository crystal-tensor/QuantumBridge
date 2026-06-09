from pathlib import Path

from quantumbridge.compat.torchquantum.training_native import run_torchquantum_like_classifier_native


def test_torchquantum_paths_do_not_access_cloud_tokens_or_hardware():
    result = run_torchquantum_like_classifier_native()
    assert result.metadata["cloud_access"] is False
    assert result.metadata["token_read"] is False
    assert result.metadata["hardware_access"] is False
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("quantumbridge/compat/torchquantum").glob("*.py")
    )
    forbidden = ["IBM_TOKEN", "QISKIT_IBM_TOKEN", "os.environ.get(\"TOKEN\"", "requests.", "urllib.request"]
    assert not any(item in source for item in forbidden)
