# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


from dataclasses import dataclass, field


@dataclass
class PassResult:
    circuit: object
    analyses: dict = field(default_factory=dict)
    changed: bool = False


class CompilerPass:
    def run(self, circuit):
        raise NotImplementedError("QuantumBridge compiler passes must implement run().")


class AnalysisPass(CompilerPass):
    pass


class TransformationPass(CompilerPass):
    pass
