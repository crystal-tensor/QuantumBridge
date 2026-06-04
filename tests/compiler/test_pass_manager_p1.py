# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.compiler import (
    DepthAnalysisPass,
    MergeAdjacentRotationPass,
    PassManager,
    RemoveZeroRotationPass,
    SimpleGateCancellationPass,
    SingleQubitMergePlaceholderPass,
    TwoQubitCountAnalysisPass,
)


def test_pass_manager_analysis_and_cancellation():
    circuit = Circuit(2).h(0).h(0).x(1).x(1).cx(0, 1)
    result = PassManager([SimpleGateCancellationPass(), DepthAnalysisPass(), TwoQubitCountAnalysisPass()]).run(circuit)
    assert [op.name for op in result.circuit.operations] == ["cx"]
    assert result.analyses["depth"] == 1
    assert result.analyses["two_qubit_gate_count"] == 1
    assert abs(StatevectorDevice().probabilities(result.circuit)["00"] - 1.0) < 1e-12


def test_pass_manager_unsupported_pass_and_merge_placeholder():
    with pytest.raises(TypeError, match="CompilerPass"):
        PassManager([object()]).run(Circuit(1))
    result = PassManager([SingleQubitMergePlaceholderPass()]).run(Circuit(1).rx(0.1, 0).ry(0.2, 0))
    assert result.analyses["single_qubit_merge"] == "placeholder-not-implemented"


def test_real_rotation_optimization_passes():
    circuit = Circuit(1).rx(0.0, 0).ry(0.1, 0).ry(0.2, 0).rz(0.3, 0).rz(-0.3, 0)
    result = PassManager([RemoveZeroRotationPass(), MergeAdjacentRotationPass()]).run(circuit)
    assert [op.name for op in result.circuit.operations] == ["ry"]
    assert abs(result.circuit.operations[0].params[0] - 0.3) < 1e-12
