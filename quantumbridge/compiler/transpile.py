# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .analysis import DepthAnalysisPass, GateCountAnalysisPass, TwoQubitCountAnalysisPass
from .config import PassManagerConfig
from .coupling import CouplingMap
from .decomposition import GateDecompositionPass
from .optimization import CircuitOptimizationPass, RemoveIdentityPass, TwoQubitGateReductionPass
from .pass_manager import PassManager
from .routing import BasicRoutingPass, SwapInsertionPass
from .target import Target


_DEFAULT_BASIS = (
    "id",
    "x",
    "y",
    "z",
    "h",
    "s",
    "sdg",
    "t",
    "tdg",
    "rx",
    "ry",
    "rz",
    "phase",
    "p",
    "u",
    "u1",
    "u2",
    "u3",
    "cx",
    "cy",
    "cz",
    "ch",
    "swap",
    "ccx",
)


def generate_preset_pass_manager(
    optimization_level: int = 1,
    *,
    basis_gates: Sequence[str] | None = None,
    coupling_map: CouplingMap | Sequence[tuple[int, int]] | None = None,
    target: Target | None = None,
) -> PassManager:
    """Build a small Qiskit-style preset pass manager.

    The native pipeline is intentionally compact, but it performs real analysis,
    basis decomposition, optional routing diagnostics/swap insertion, and
    optimization passes.
    """

    if not isinstance(optimization_level, int) or optimization_level < 0 or optimization_level > 3:
        raise ValueError("QuantumBridge optimization_level must be an integer in [0, 3].")
    resolved_target = _resolve_target(target, basis_gates, coupling_map)
    passes = []
    passes.append(GateDecompositionPass(resolved_target.basis_gates))
    if resolved_target.coupling_map is not None:
        passes.append(BasicRoutingPass(resolved_target.coupling_map))
        if optimization_level >= 1:
            passes.append(SwapInsertionPass(resolved_target.coupling_map))
    if optimization_level >= 1:
        passes.append(RemoveIdentityPass())
    if optimization_level >= 2:
        passes.append(CircuitOptimizationPass())
    if optimization_level >= 3:
        passes.append(TwoQubitGateReductionPass())
        passes.append(CircuitOptimizationPass())
    passes.extend([DepthAnalysisPass(), GateCountAnalysisPass(), TwoQubitCountAnalysisPass()])
    manager = PassManager(passes)
    manager.metadata = {
        "optimization_level": optimization_level,
        "basis_gates": list(resolved_target.basis_gates),
        "target": resolved_target.to_dict(),
    }
    return manager


def transpile(
    circuits,
    *,
    basis_gates: Sequence[str] | None = None,
    coupling_map: CouplingMap | Sequence[tuple[int, int]] | None = None,
    optimization_level: int = 1,
    target: Target | None = None,
    return_report: bool = False,
):
    """Transpile one circuit or a sequence of circuits with the native pipeline."""

    single = not isinstance(circuits, (list, tuple))
    items = [circuits] if single else list(circuits)
    manager = generate_preset_pass_manager(
        optimization_level=optimization_level,
        basis_gates=basis_gates,
        coupling_map=coupling_map,
        target=target,
    )
    outputs = []
    reports = []
    for circuit in items:
        result = manager.run(circuit)
        out = result.circuit.copy()
        out.metadata.setdefault("transpile", {})
        out.metadata["transpile"].update(
            {
                "optimization_level": optimization_level,
                "basis_gates": list(manager.metadata["basis_gates"]),
                "analyses": result.analyses,
                "changed": result.changed,
            }
        )
        outputs.append(out)
        reports.append(result.analyses.get("compiler_report", result.analyses))
    payload = outputs[0] if single else outputs
    if return_report:
        return payload, reports[0] if single else reports
    return payload


def _resolve_target(target: Target | None, basis_gates, coupling_map) -> Target:
    if target is not None:
        if basis_gates is not None or coupling_map is not None:
            raise ValueError("QuantumBridge transpile target cannot be combined with basis_gates or coupling_map.")
        return target
    normalized_coupling = None
    if coupling_map is not None:
        normalized_coupling = coupling_map if isinstance(coupling_map, CouplingMap) else CouplingMap(coupling_map)
    return Target(num_qubits=0, basis_gates=tuple(basis_gates or _DEFAULT_BASIS), coupling_map=normalized_coupling)


def pass_manager_config_from_options(**options: Any) -> PassManagerConfig:
    return PassManagerConfig(
        basis_gates=tuple(options.get("basis_gates") or _DEFAULT_BASIS),
        optimization_level=int(options.get("optimization_level", 1)),
        coupling_map=options.get("coupling_map"),
    )
