# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


from copy import deepcopy

from quantumbridge.core import Measurement, Operation

from .pass_base import CompilerPass, PassResult
from .report import CompilerReport


class PassManager:
    def __init__(self, passes=None):
        self.passes = list(passes or [])

    def run(self, circuit):
        if circuit.has_dynamic_operations:
            return self._run_ordered(circuit)
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

    def _run_ordered(self, circuit):
        from .routing import SwapInsertionPass

        if any(isinstance(item, SwapInsertionPass) for item in self.passes):
            raise ValueError("QuantumBridge dynamic transpilation does not yet support coupling-map routing.")
        out = circuit.copy_empty_like()
        segment = circuit.copy_empty_like()
        reports = []
        changed = False

        def flush():
            nonlocal segment, changed
            if segment.operations:
                result = self.run(segment)
                out.operations.extend(result.circuit.operations)
                reports.append(result.analyses)
                changed = changed or result.changed
                segment = circuit.copy_empty_like()

        for item in circuit.iter_instructions():
            if isinstance(item, Measurement):
                flush()
                metadata = {**deepcopy(item.metadata), "operation_index": len(out.operations)}
                out.measurements.append(Measurement(item.wire, item.bit, item.kind, metadata))
            elif item.name in {"reset", "kraus"} or item.metadata.get("directive"):
                flush()
                out.operations.append(item)
            elif any(key in item.metadata for key in ("condition", "control_flow", "control_flow_stack")):
                flush()
                unit = circuit.copy_empty_like()
                metadata = {key: deepcopy(value) for key, value in item.metadata.items()
                            if key not in {"condition", "control_flow", "control_flow_stack", "gate_condition"}}
                unit.operations.append(Operation(item.name, item.targets, item.controls, item.params, metadata))
                result = self.run(unit)
                reports.append(result.analyses)
                changed = changed or result.changed
                for index, operation in enumerate(result.circuit.operations):
                    restored = {**deepcopy(operation.metadata), **deepcopy(item.metadata)}
                    if index:
                        for frame in restored.get("control_flow_stack", []):
                            frame["start"] = False
                    out.operations.append(Operation(operation.name, operation.targets, operation.controls, operation.params, restored))
            else:
                segment.operations.append(item)
        flush()
        analyses = {"dynamic_execution_order": True, "segment_analyses": reports}
        analyses["compiler_report"] = CompilerReport(len(circuit.operations), len(out.operations), analyses.copy(), changed).to_dict()
        return PassResult(out, analyses, changed)
