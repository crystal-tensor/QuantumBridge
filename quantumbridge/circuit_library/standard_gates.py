# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from quantumbridge.core import Circuit


_ONE_QUBIT = {"id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "t", "tdg", "rx", "ry", "rz", "phase"}
_TWO_QUBIT = {"cx", "cz", "swap", "iswap", "crx", "cry", "crz", "cp", "cphase", "rxx", "ryy", "rzz"}
_THREE_QUBIT = {"ccx"}


def standard_gate(name: str, *params, num_qubits: int | None = None) -> Circuit:
    """Build a circuit containing a single standard gate operation."""

    gate = name.lower()
    if gate in _ONE_QUBIT:
        circuit = Circuit(num_qubits or 1)
        _append_one_qubit(circuit, gate, params, 0)
        return circuit
    if gate in _TWO_QUBIT:
        circuit = Circuit(num_qubits or 2)
        _append_two_qubit(circuit, gate, params, 0, 1)
        return circuit
    if gate in _THREE_QUBIT:
        circuit = Circuit(num_qubits or 3)
        circuit.ccx(0, 1, 2)
        return circuit
    raise ValueError(f"QuantumBridge standard gate {name!r} is not registered.")


def _append_one_qubit(circuit: Circuit, gate: str, params: tuple, wire: int) -> None:
    if gate in {"rx", "ry", "rz", "phase"}:
        if not params:
            raise ValueError(f"QuantumBridge {gate} requires one parameter.")
        getattr(circuit, gate)(params[0], wire)
    else:
        getattr(circuit, gate)(wire)


def _append_two_qubit(circuit: Circuit, gate: str, params: tuple, left: int, right: int) -> None:
    if gate in {"cx", "cz"}:
        getattr(circuit, gate)(left, right)
    elif gate in {"swap", "iswap"}:
        getattr(circuit, gate)(left, right)
    elif gate in {"crx", "cry", "crz", "cp", "cphase"}:
        if not params:
            raise ValueError(f"QuantumBridge {gate} requires one parameter.")
        getattr(circuit, gate)(params[0], left, right)
    elif gate in {"rxx", "ryy", "rzz"}:
        if not params:
            raise ValueError(f"QuantumBridge {gate} requires one parameter.")
        getattr(circuit, gate)(params[0], left, right)
    else:
        raise ValueError(f"QuantumBridge standard gate {gate!r} is not a two-qubit gate.")
