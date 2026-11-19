# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public state/count-metric keywords, sharing independent Native kernels."""
from __future__ import annotations

from .metrics import _hellinger_values
from .density_matrix import DensityMatrix
from .statevector import Statevector
from .operator import Operator
from .channels import _QuantumChannel

__all__ = ['hellinger_distance', 'hellinger_fidelity', 'purity', 'state_fidelity',
    'process_fidelity', 'average_gate_fidelity', 'gate_error', 'partial_trace']


def partial_trace(state: Statevector | DensityMatrix, qargs: list) -> DensityMatrix:
    from .public_partial_trace import public_partial_trace

    return public_partial_trace(state, qargs)


def hellinger_distance(dist_p: dict, dist_q: dict) -> float:
    return _hellinger_values(dist_p, dist_q)[0]


def hellinger_fidelity(dist_p: dict, dist_q: dict) -> float:
    return _hellinger_values(dist_p, dist_q)[1]


def purity(state: Statevector | DensityMatrix, validate: bool = True) -> float:
    from .public_fidelity import public_purity

    return public_purity(state, validate)


def state_fidelity(state1: Statevector | DensityMatrix, state2: Statevector | DensityMatrix, validate: bool = True) -> float:
    from .public_fidelity import public_state_fidelity

    return public_state_fidelity(state1, state2, validate)


def process_fidelity(channel: Operator | _QuantumChannel, target: Operator | _QuantumChannel | None = None,
                     require_cp: bool = True, require_tp: bool = True) -> float:
    from .public_channel_metrics import _metric

    return _metric(channel,target,require_cp,require_tp)


def average_gate_fidelity(channel: _QuantumChannel | Operator, target: Operator | None = None,
                          require_cp: bool = True, require_tp: bool = False) -> float:
    from .public_channel_metrics import _metric

    return _metric(channel,target,require_cp,require_tp,average=True)


def gate_error(channel: _QuantumChannel, target: Operator | None = None,
               require_cp: bool = True, require_tp: bool = False) -> float:
    return 1-average_gate_fidelity(channel,target,require_cp,require_tp)
