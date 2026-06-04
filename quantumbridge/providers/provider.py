# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from .backend import Backend


class Provider:
    def __init__(self):
        self._backends = {"statevector": Backend()}

    def get_backend(self, name: str = "statevector") -> Backend:
        return self._backends[name]

