# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Bounded native Tape batching; execution reuses the existing QNode plan."""

from copy import deepcopy
from dataclasses import dataclass
from itertools import islice
from numbers import Integral
from uuid import uuid4

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan, map_measurements
from quantumbridge.qml.measurements import MeasurementRequest
from quantumbridge.qml.qnode import QNode
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.qml.tape import Tape
from quantumbridge.utils.math import Hamiltonian


@dataclass(frozen=True)
class TransformLimits:
    max_transforms: int = 32
    max_tapes: int = 128
    max_operations_per_tape: int = 100000
    max_total_operations: int = 500000
    max_expansion_steps: int = 200000
    max_structure_depth: int = 64
    max_postprocessing_nodes: int = 100000
    max_total_shots: int = 1000000

    def __post_init__(self):
        if any(isinstance(value, bool) or not isinstance(value, Integral) or value < 1
               for value in self.__dict__.values()):
            raise ValueError("Transform limits must be positive integers.")

    def check(self, name, value):
        if value > getattr(self, name):
            raise MemoryError("Native transform exceeded " + name)


def resolve_limits(limits):
    if limits is None:
        return TransformLimits()
    if not isinstance(limits, TransformLimits):
        raise TypeError("Native transforms require TransformLimits.")
    return limits


def check_structure(tree, limits):
    pending, count = [(tree, 0)], 0
    while pending:
        item, depth = pending.pop()
        count += 1
        limits.check("max_structure_depth", depth)
        if isinstance(item, (tuple, list, dict)):
            values = item.values() if isinstance(item, dict) else item
            limits.check("max_postprocessing_nodes", count + len(item) + len(pending))
            pending.extend((value, depth + 1) for value in values)
        elif isinstance(item, np.ndarray):
            count += item.size
        limits.check("max_postprocessing_nodes", count)


def output_tree(tape):
    if tape.output_tree is not None:
        return tape.output_tree
    if not tape.measurements:
        raise ValueError("A transform Tape needs terminal measurements.")
    return tape.measurements[0] if len(tape.measurements) == 1 else tuple(tape.measurements)


def operation_count(circuit, limits):
    pending, count = [(circuit, 0, frozenset())], 0
    while pending:
        body, depth, ancestors = pending.pop()
        limits.check("max_structure_depth", depth)
        if id(body) in ancestors:
            raise ValueError("Cyclic native control bodies are unsupported.")
        count += len(body.operations) + len(body.measurements)
        limits.check("max_operations_per_tape", count)
        ancestors = ancestors | {id(body)}
        for operation in body.operations:
            node = operation.metadata.get("control_node")
            if node is not None:
                pending.extend((child, depth + 1, ancestors) for child in node.bodies)
    return count


def check_batch(tapes, limits):
    limits.check("max_tapes", len(tapes))
    operations, shots = 0, 0
    for tape in tapes:
        if not isinstance(tape, Tape):
            raise TypeError("Transform children must be native Tape objects.")
        operations += operation_count(tape.circuit, limits)
        limits.check("max_total_operations", operations)
        tree = output_tree(tape)
        check_structure(tree, limits)
        requests = []
        map_measurements(tree, lambda request: requests.append(request))
        if any(not isinstance(request, MeasurementRequest) for request in requests):
            raise TypeError("Transform outputs must contain measurement requests.")
        legacy_analytic = any(request.kind in {"state", "density_matrix"} for request in requests)
        for partition in ShotSpec.parse(tape.shots).partitions:
            for request in requests:
                count = request.shots if request.shots is not None else partition
                if legacy_analytic and request.kind in {"state", "density_matrix", "expval", "var", "probs"}:
                    count = None
                if count is not None:
                    if isinstance(count, bool) or not isinstance(count, Integral) or count < 1:
                        raise ValueError("Transform measurement shots must be positive integers.")
                    terms = len(request.observable.terms) if request.kind == "expval" and isinstance(request.observable, Hamiltonian) else 1
                    shots += count * terms
        limits.check("max_total_shots", shots)
    return operations, shots


class TransformError(RuntimeError):
    """A user transform, child execution or reconstruction failed at this stage."""


@dataclass(frozen=True)
class PreparedTransform:
    tapes: tuple
    processing_fn: object
    metadata: dict


class TransformProgram:
    """Compose Tape -> (Tapes, processor) functions with reverse reconstruction.

    Processors receive one result per child Tape, including that Tape's shot
    partitions. They must be pure result functions, not execute more circuits.
    B1 requires unchanged shot specifications across a transform boundary.
    """

    def __init__(self, transforms=(), *, limits=None):
        self.limits = resolve_limits(limits)
        self.transforms = tuple(islice(transforms, self.limits.max_transforms + 1))
        self.limits.check("max_transforms", len(self.transforms))
        if not all(callable(function) for function in self.transforms):
            raise TypeError("TransformProgram stages must be callable.")

    def prepare(self, tape):
        limits = self.limits
        check_batch((tape,), limits)
        batch, levels, trace, expansion = (tape.copy(),), [], [], 0
        for stage, function in enumerate(self.transforms):
            children, processors = [], []
            name = getattr(function, "__name__", type(function).__name__)
            for index, parent in enumerate(batch):
                context = f"transform stage {stage} ({name}), parent {index}"
                try:
                    returned = function(parent.copy())
                    if not isinstance(returned, (tuple, list)) or len(returned) != 2:
                        raise TypeError("A transform must return (tapes, processing_fn).")
                    emitted, processor = returned
                    if not callable(processor):
                        raise TypeError("A transform result processor must be callable.")
                    remaining = limits.max_tapes - len(children)
                    emitted = tuple(islice(emitted, remaining + 1))
                    limits.check("max_tapes", len(children) + len(emitted))
                    added_operations, _ = check_batch(emitted, limits)
                    expansion += added_operations + len(emitted)
                    limits.check("max_expansion_steps", expansion)
                    parent_shots = ShotSpec.parse(parent.shots)
                    if any(ShotSpec.parse(child.shots) != parent_shots for child in emitted):
                        raise UnsupportedFeature("transform_shot_allocation", "B1 transforms must preserve parent shot partitions; allocation is not implemented.")
                    start = len(children)
                    children.extend(child.copy() for child in emitted)
                    processors.append((start, len(children), processor))
                except MemoryError as exc:
                    raise MemoryError(context + ": " + str(exc)) from exc
                except Exception as exc:
                    raise TransformError(context + ": " + str(exc)) from exc
            operation_total, shot_total = check_batch(children, limits)
            trace.append({"stage": stage, "name": name, "input_tape_count": len(batch),
                          "output_tape_count": len(children), "operation_count": operation_total,
                          "sampled_shots": shot_total})
            levels.append(tuple(processors))
            batch = tuple(children)

        def process(results):
            if len(results) != len(batch):
                raise ValueError("Postprocessing result count must match executed Tapes.")
            current = tuple(results)
            check_structure(current, limits)
            for stage in reversed(range(len(levels))):
                reconstructed = []
                for parent, (start, stop, processor) in enumerate(levels[stage]):
                    try:
                        value = processor(current[start:stop])
                        check_structure(value, limits)
                        reconstructed.append(value)
                    except MemoryError:
                        raise
                    except Exception as exc:
                        raise TransformError(f"postprocessing stage {stage}, parent {parent}: {exc}") from exc
                current = tuple(reconstructed)
                check_structure(current, limits)
            if len(current) != 1:
                raise ValueError("TransformProgram must reconstruct one original Tape result.")
            return current[0]

        return PreparedTransform(batch, process, {"transform_count": len(self.transforms), "stages": trace,
                                                  "postprocessing_order": list(reversed(range(len(levels))))})

    def __call__(self, tape):
        prepared = self.prepare(tape)
        return prepared.tapes, prepared.processing_fn


_UNSET = object()


def execute_transform(tape, transform_fn, device=None, *, bindings=None, shots=_UNSET,
                      seed=_UNSET, limits=None, return_metadata=False):
    """Execute every transformed child with the existing native QNode plan.

    Returns its reconstructed QNode-style value. With return_metadata=True,
    returns (value, metadata). Execution IDs denote real child plan evaluations,
    not claims that a multi-measurement device uses only one simulator run.
    Native parameter bindings are supported; transformed autodiff is not yet.
    """
    if not isinstance(tape, Tape):
        raise TypeError("execute_transform requires a native Tape.")
    limits = resolve_limits(limits if limits is not None else getattr(transform_fn, "limits", None))
    check_batch((tape,), limits)
    source = tape.copy()
    if shots is not _UNSET:
        source.shots = shots
    if seed is not _UNSET:
        source.seed = seed
    if isinstance(transform_fn, TransformProgram):
        program = TransformProgram(transform_fn.transforms, limits=limits)
    else:
        program = TransformProgram((transform_fn,), limits=limits)
    prepared = program.prepare(source)
    plans = []
    seed_sequence = np.random.SeedSequence(source.seed)
    child_seeds = seed_sequence.spawn(len(prepared.tapes)) if source.seed is not None else [None] * len(prepared.tapes)
    for index, (child, child_seed) in enumerate(zip(prepared.tapes, child_seeds)):
        pending = [child.circuit]
        while pending:
            body = pending.pop()
            values = (body.global_phase,) + tuple(value for operation in body.operations for value in operation.params)
            if any(type(value).__module__.startswith(("torch", "autograd")) or hasattr(value, "derivative") for value in values):
                raise UnsupportedFeature("transform_autodiff", "B1 preserves parameter graphs but transformed framework/Dual execution is not implemented.")
            for operation in body.operations:
                node = operation.metadata.get("control_node")
                if node is not None:
                    pending.extend(node.bodies)
        mapping = dict(bindings or {})
        if any(type(value).__module__.startswith(("torch", "autograd")) or hasattr(value, "derivative") for value in mapping.values()):
            raise UnsupportedFeature("transform_autodiff", "B1 supports numeric bindings, not transformed input autodiff.")
        child.circuit = child.circuit.assign_parameters(mapping, strict=False)
        if child.circuit.parameters:
            raise ValueError(f"Transform child {index} has unbound parameters.")
        seed_value = child.seed if child.seed != source.seed else None if child_seed is None else int(child_seed.generate_state(1)[0])
        node = QNode(lambda _: None, child.circuit.num_qubits, device=device,
                     shots=child.shots, seed=seed_value)
        plans.append(ExecutionPlan(node, child, output_tree(child), AngleRecorder()))
    check_batch(prepared.tapes, limits)
    results, executions = [], []
    for index, plan in enumerate(plans):
        execution_id = str(uuid4())
        try:
            value = plan.evaluate(())
        except Exception as exc:
            raise TransformError(f"execution child {index} ({execution_id}): {exc}") from exc
        check_structure(value, limits)
        results.append(value)
        executions.append({"tape_index": index, "execution_id": execution_id,
                           "operation_count": operation_count(plan.circuit, limits), **deepcopy(plan.metadata)})
    value = prepared.processing_fn(tuple(results))
    metadata = {**deepcopy(prepared.metadata), "native_execution": True,
                "executed_tape_count": len(executions), "executions": executions,
                "execution_semantics": "one independent native ExecutionPlan evaluation per child Tape",
                "gradient_support": "not implemented for transformed execution in B1"}
    return (value, metadata) if return_metadata else value
