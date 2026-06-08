# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


from .pass_base import CompilerPass, PassResult
from .report import CompilerReport


class PassManager:
    def __init__(self, passes=None):
        self.passes = list(passes or [])

    def run(self, circuit):
        input_operations = len(circuit.operations)
        current = circuit
        analyses = {}
        changed = False
        for compiler_pass in self.passes:
            if not isinstance(compiler_pass, CompilerPass):
                raise TypeError("QuantumBridge PassManager entries must be CompilerPass instances.")
            result = compiler_pass.run(current)
            if not isinstance(result, PassResult):
                raise TypeError("QuantumBridge compiler passes must return PassResult.")
            current = result.circuit
            analyses.update(result.analyses)
            changed = changed or result.changed
        analyses.setdefault("compiler_report", CompilerReport(input_operations, len(current.operations), analyses.copy(), changed).to_dict())
        return PassResult(current, analyses, changed)
