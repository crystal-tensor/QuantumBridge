# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This implementation is developed for the QuantumBridge native architecture.

from numbers import Integral


def validate_wires(wires, width):
    selected = tuple(range(width) if wires is None else wires)
    if len(set(selected)) != len(selected) or any(not isinstance(wire, Integral) or not 0 <= wire < width for wire in selected):
        raise ValueError("QuantumBridge wires must be distinct valid circuit wires.")
    return selected


def validate_conditions(metadata, num_bits):
    frames = metadata.get("control_flow_stack", [])
    if metadata.get("control_flow") and not frames:
        raise ValueError("QuantumBridge control flow requires ordered branch metadata; rebuild this block with Circuit.if_else.")
    conditions = [metadata.get("condition"), metadata.get("gate_condition")]
    for frame in frames:
        if frame.get("type") != "if_else" or frame.get("branch") not in {"true", "false"} or not frame.get("block_id"):
            raise ValueError("QuantumBridge execution supports if/else control-flow blocks only.")
        conditions.append(frame.get("condition"))
    for condition in conditions:
        if condition is None:
            continue
        bits = condition.get("bits", [])
        if not bits or len(set(bits)) != len(bits) or any(not isinstance(bit, Integral) or not 0 <= bit < num_bits for bit in bits):
            raise ValueError("QuantumBridge condition bits are outside the classical register.")
        value = condition.get("value")
        if not isinstance(value, Integral) or not 0 <= value < (1 << len(bits)):
            raise ValueError("QuantumBridge condition value is outside its bit width.")


def condition_enabled(metadata, bits, decisions):
    def matches(condition):
        return sum(bits[bit] << index for index, bit in enumerate(condition["bits"])) == condition["value"]

    frames = metadata.get("control_flow_stack", [])
    for frame in frames:
        key = frame["block_id"]
        # Snapshot at block entry, even when the body overwrites tested bits.
        if frame.get("start") or key not in decisions:
            decisions[key] = matches(frame["condition"])
        if decisions[key] != (frame["branch"] == "true"):
            return False
    condition = metadata.get("gate_condition") if frames else metadata.get("condition")
    return condition is None or matches(condition)


def decision_liveness(program):
    """Find branch snapshots that future events still need before their next entry."""
    live = set()
    result = [set() for _ in program]
    for index in range(len(program) - 1, -1, -1):
        result[index] = live.copy()
        for frame in reversed(program[index][3].get("control_flow_stack", [])):
            if frame.get("start"):
                live.discard(frame["block_id"])
            else:
                live.add(frame["block_id"])
    return result


def readout_probability(noise_model, wire, outcome):
    error = None if noise_model is None else noise_model.readout_errors.get(wire)
    return 0.0 if error is None else error.p1_to_0 if outcome else error.p0_to_1


def apply_readout_distribution(probabilities, noise_model, wires):
    result = dict(probabilities)
    if noise_model is None:
        return result
    for offset, wire in enumerate(wires):
        updated = {}
        for label, weight in result.items():
            probability = readout_probability(noise_model, wire, int(label[offset]))
            flipped = label[:offset] + ("0" if label[offset] == "1" else "1") + label[offset + 1:]
            for key, value in ((label, 1 - probability), (flipped, probability)):
                if value:
                    updated[key] = updated.get(key, 0.0) + weight * value
        result = updated
    return result
