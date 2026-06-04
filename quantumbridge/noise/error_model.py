# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from .channels import _validate_probability


class ReadoutError:
    def __init__(self, p0_to_1: float, p1_to_0: float):
        self.p0_to_1 = _validate_probability(p0_to_1)
        self.p1_to_0 = _validate_probability(p1_to_0)


class NoiseModel:
    def __init__(self):
        self.channels = []
        self.readout_errors = {}

    def add_channel(self, channel, wires=None):
        self.channels.append({"channel": channel, "wires": None if wires is None else tuple(wires)})
        return self

    def add_readout_error(self, wire: int, error: ReadoutError):
        self.readout_errors[int(wire)] = error
        return self

    def summary(self):
        return {
            "channels": [entry["channel"].name for entry in self.channels],
            "readout_errors": sorted(self.readout_errors),
        }
