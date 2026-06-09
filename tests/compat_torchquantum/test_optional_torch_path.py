import pytest

from quantumbridge.compat.torchquantum.torch_adapter import (
    is_torch_available,
    torch_forward_if_available,
)


def test_optional_torch_path_skips_or_runs_cleanly():
    result = torch_forward_if_available([[0.1, 0.2]], [0.0, 0.0, 0.0, 0.0])
    if not is_torch_available():
        assert result.unsupported_reason
        assert result.mode == "torch_optional"
    else:
        import torch

        torch_result = torch_forward_if_available(
            torch.tensor([[0.1, 0.2]], dtype=torch.float64),
            torch.tensor([0.0, 0.0, 0.0, 0.0], dtype=torch.float64),
        )
        assert torch_result.tensor_backend == "torch"
        assert len(torch_result.forward_outputs) == 1
