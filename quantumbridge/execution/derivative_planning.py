# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Prepare existing native plans from reusable Device derivative requests."""

from copy import copy
from dataclasses import dataclass
from numbers import Integral

import numpy as np

from quantumbridge.core import Circuit
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.higher_order_limits import resolve_higher_order_limits
from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan
from quantumbridge.diff.trace import flatten_tree, trace_arguments
from quantumbridge.qml.qnode import QNode
from quantumbridge.qml.tape import Tape
from quantumbridge.utils.math import Hamiltonian, PauliString

from .derivative_request import DerivativeExecutionRequest


@dataclass
class PreparedDerivative:
    request: DerivativeExecutionRequest
    node: QNode
    plan: object
    point: np.ndarray
    classical: np.ndarray
    second: object
    direction: object
    size: int
    layout: object
    single: bool
    output_spec: object
    output_size: int
    work: dict
    buffer_bytes: int
    device_bytes: int


def _direction(request, args, size):
    if request.derivative_kind not in {"hvp", "jvp"}:
        return None
    raw = request.tangent
    selected = (raw,) if len(args) == 1 else tuple(raw) if isinstance(raw, (tuple, list)) else ()
    if len(selected) != len(args) or any(np.shape(x) != np.shape(y) for x, y in zip(selected, args)):
        raise ValueError("Derivative tangent must match each differentiated input shape.")
    arrays = [np.asarray(value) for value in selected]
    if any(value.dtype.kind not in "fiu" or not np.all(np.isfinite(value)) for value in arrays):
        raise ValueError("Derivative tangent must be finite and real.")
    return np.concatenate([value.astype(float).reshape(-1) for value in arrays]).reshape(size)


def device_working_bytes(device, circuit):
    """Conservative numerical buffers, not observed BLAS allocator memory."""
    width = circuit.num_qubits
    if getattr(device, "simulation", None) == "matrix_product_state":
        from .resource_context import current_resources
        resources = current_resources()
        if resources is not None:
            resources.ledger.unavailable("mps_svd_allocator_peak",
                "Conservative tensor/contraction/SVD reservation, not observed BLAS/LAPACK allocator peak.")
        bonds = [1]*(max(0, width-1))
        initial = getattr(device, "initial_state", None)
        if initial is not None:
            if not hasattr(initial, "tensors"):
                raise UnsupportedFeature("derivative_mps_dense_initial_state")
            bonds = [tensor.shape[-1] for tensor in initial.tensors[:-1]]
        cap = device.state_options["max_bond_dim"]
        largest = max(bonds, default=1)
        for operation in circuit.operations:
            wires = operation.controls+operation.targets
            if len(wires) > 1:
                for cut in range(min(wires), max(wires)):
                    rank = 2 if operation.name in {"cx", "cz"} else 4**min(sum(w <= cut for w in wires), sum(w > cut for w in wires))
                    bonds[cut] = min(bonds[cut]*rank, 1 << min(cut+1, width-cut-1))
                    if cap is not None:
                        bonds[cut] = min(bonds[cut], cap)
                    largest = max(largest, bonds[cut])
        dimensions = [1, *bonds, 1]
        stored = 16*sum(2*a*b for a, b in zip(dimensions, dimensions[1:]))
        return int(12*stored+128*(2*largest)**2)
    if getattr(device, "simulation", None) == "exact_stabilizer":
        raise UnsupportedFeature("tableau_continuous_gradient")
    from quantumbridge.devices.density_matrix_device import DensityMatrixDevice
    local_dimension = max((1 << len(op.wires) for op in circuit.operations if not op.metadata.get("directive")), default=1)
    return 16*(1 << (2*width if isinstance(device, DensityMatrixDevice) else width))*8+64*local_dimension**2


def _measurement_size(child):
    size, shots, samples = 0, 0, 0
    for request in child.requests:
        if request.kind in {"expval", "var"}:
            count = 1
        elif request.kind == "pauli_group":
            count = len(request.observable.words)
        elif request.kind == "probs":
            width = child.circuit.num_qubits if request.wires is None else len(request.wires)
            if width > 16: raise UnsupportedFeature("probability_output_size")
            count = 1 << width
        else:
            raise UnsupportedFeature("derivative_measurement")
        size += count*len(child.shots.partitions)
        for partition in child.shots.partitions:
            n = request.shots if request.shots is not None else partition
            multiplier = 1
            if request.kind in {"expval", "var"} and isinstance(request.observable, PauliString):
                multiplier = int(any(label != "I" for _, label in request.observable.terms))
            elif request.kind == "expval" and isinstance(request.observable, Hamiltonian):
                multiplier = sum(any(label != "I" for _, label in word.terms) for _, word in request.observable.terms)
            shots += (n or 0)*multiplier
            samples = max(samples, 16*(n or 0)*(child.circuit.num_qubits+count)+8*count*count)
    return size, shots, samples


def prepare_derivative(device, request):
    if not isinstance(request, DerivativeExecutionRequest):
        raise TypeError("Device derivatives require DerivativeExecutionRequest.")
    orders = {"value": 0, "jacobian": 1, "vjp": 1, "jvp": 1, "hessian": 2, "hvp": 2}
    if request.derivative_kind not in orders:
        raise ValueError("Unknown native derivative kind.")
    if isinstance(request.derivative_order, bool) or not isinstance(request.derivative_order, Integral) or request.derivative_order != orders[request.derivative_kind]:
        raise ValueError("Derivative order must match derivative kind.")
    method = request.method
    if method == "second_adjoint":
        if request.derivative_order != 2: raise ValueError("second_adjoint requires order two.")
        method = "adjoint"
    if method not in {"best", "adjoint", "parameter-shift"}:
        raise UnsupportedFeature("device_derivative_method")
    source = request.circuit_or_tape
    if isinstance(source, QNode):
        node = copy(source)
        args = request.parameters if isinstance(request.parameters, tuple) else (request.parameters,)
    elif isinstance(source, (Tape, Circuit)):
        tape = source.copy() if isinstance(source, Tape) else Tape(source.num_qubits)
        if isinstance(source, Circuit):
            tape.circuit = source.copy()
            if request.observable is None: raise ValueError("Circuit derivative requests require an observable.")
            tape.set_output(tape.expval(request.observable))
        parameters = tuple(tape.circuit.parameters)
        supplied = request.parameters
        if isinstance(supplied, dict):
            values = [supplied[p] if p in supplied else supplied[p.name] for p in parameters]
        else:
            values = np.asarray(supplied).reshape(-1)
        if len(values) != len(parameters): raise ValueError("Device parameter count does not match native circuit.")
        values = np.asarray(values)
        if values.dtype.kind not in "fiu" or not np.all(np.isfinite(values)):
            raise ValueError("Native circuit parameters must be finite and real.")
        args = (values.astype(float),)
        def program(target, values):
            from quantumbridge.diff.compiled_parameters import record_compiled_parameters
            from quantumbridge.diff.qnode_engine import map_measurements
            original = AngleRecorder()
            original.parameters, original.angles = list(parameters), list(values)
            circuit, recorder = record_compiled_parameters(tape.circuit, original)
            target.circuit = circuit.assign_parameters({p: target.parameter_transform(x) for p, x in zip(recorder.parameters, recorder.angles)})
            tree = tape.output_tree if tape.output_tree is not None else tape.measurements[0] if len(tape.measurements) == 1 else tuple(tape.measurements)
            if not tree: raise ValueError("Tape derivative requests require terminal measurements.")
            map_measurements(tree, lambda item: target.measurements.append(item))
            return tree
        node = QNode(program, tape.circuit.num_qubits, shots=tape.shots, seed=tape.seed, max_diff=2)
    else:
        raise TypeError("Derivative source must be a native Circuit, Tape or QNode.")
    if not args: raise ValueError("Derivative request requires explicit floating-point parameters.")
    arrays = [np.asarray(value) for value in args]
    if any(a.dtype.kind not in "f" or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("Derivative parameters must be finite real floating-point arrays.")
    node.device, node.interface, node.diff_method, node.last_metadata = device, "numpy", method, {}
    if request.shots is not None: node.shots = request.shots
    if request.seed is not None: node.seed = request.seed
    node.unified_limits = None
    size = sum(a.size for a in arrays)
    direction = _direction(request, args, size)
    limits = resolve_higher_order_limits(node.higher_order_limits)
    argnums = 0 if len(args) == 1 else tuple(range(len(args)))
    order = max(1, request.derivative_order)
    traced, _, layout, single, _ = trace_arguments(args, {}, argnums, order=order,
        direction=direction if order == 2 else None, limits=limits)
    tape, recorder, program = node._construct(traced, {}, prepare_only=True)
    if program is None:
        plan = ExecutionPlan(node, tape, tape.output_tree, recorder)
    else:
        from quantumbridge.transforms.program import TransformedExecutionPlan
        plan = TransformedExecutionPlan(node, tape, recorder, program)
    from quantumbridge.interfaces.native_host import _shape_tree
    from quantumbridge.qml.shot_vector import ShotSpec
    shape = _shape_tree(tape.output_tree, node.num_qubits, ShotSpec.parse(node.shots), limits, "native_device")
    flat, spec = flatten_tree(shape)
    if request.derivative_kind == "vjp":
        cotangent, cotangent_spec = flatten_tree(request.cotangent)
        if cotangent_spec != spec or not np.all(np.isfinite(cotangent)):
            raise ValueError("Derivative cotangent must match the output tree and be finite.")
    point = plan.recorder.native_values()
    columns = 1 if direction is not None else size
    from .resource_context import current_resources
    scope = current_resources()
    map_bytes = 8*len(point)*size*(1+(columns if order == 2 else 0))
    if scope is not None: scope.retain("classical_source_maps", map_bytes)
    classical = plan.recorder.classical_jacobian(size)
    second = plan.recorder.classical_second(size, columns) if order == 2 else None
    prepared = finish_derivative(request, node, plan, point, classical, second, direction,
        size, layout, single, spec, len(flat))
    if scope is not None: prepared.buffer_bytes -= map_bytes
    return prepared


def finish_derivative(request, node, plan, point, classical, second, direction, size, layout, single, spec, output_size):
    """Shared resource planning for direct Device and framework source maps."""
    device, method = node.device, node.diff_method
    limits = resolve_higher_order_limits(node.higher_order_limits)
    children = getattr(plan, "child_plans", (plan,))
    if any(child.circuit.has_simulator_instructions for child in children):
        raise UnsupportedFeature("derivative_simulator_instructions",
            "Managed derivative requests do not yet own save/set snapshot result lifetimes; simulator instructions require their dedicated execution API.")
    columns = 1 if direction is not None else size
    workspace = max((device_working_bytes(device, child.circuit) for child in children), default=0)
    if request.derivative_order == 2:
        from quantumbridge.diff.second_order import second_work, transformed_second_work
        work = transformed_second_work(plan, point, classical, second, direction, limits, method)[0] if hasattr(plan, "child_plans") else second_work(plan, point, classical, second, direction, limits, method)[3]
        buffers = work["derivative_buffer_bytes"]+8*(classical.size+second.size)+8*output_size*size*(1+columns)
        if method == "adjoint":
            # Include C2A local matrices/observables as well as state vectors.
            slices = getattr(plan, "parameter_slices", ((0, len(point)),))
            for child, (start, stop) in zip(children, slices):
                child_work = second_work(child, point[start:stop], classical[start:stop], second[start:stop], direction, limits, method)[3]
                workspace = max(workspace, child_work["combined_working_buffer_bytes"]-child_work["derivative_buffer_bytes"])
    else:
        evaluations = total_shots = samples = 0
        for child in children:
            selected = child.gradient_capability(method) if request.derivative_order else None
            n, shots, sample_bytes = _measurement_size(child)
            count = 1 if not request.derivative_order else 2 if selected == "adjoint" else 2+sum(
                2*len(child.shift_recipe(op, point[0] if len(point) else 0.)) for op in child._occurrences().values())
            evaluations += count*len(child.shots.partitions)
            total_shots += count*shots
            samples = max(samples, sample_bytes)
        work = {"tape_count": evaluations, "physical_shots": total_shots,
                "evaluation_count": evaluations, "derivative_buffer_bytes": 8*output_size*max(1, size)*4}
        buffers = work["derivative_buffer_bytes"]+8*classical.size
        workspace += samples
    work = dict(work)
    work["derivative_work"] = work.get("adjoint_operations", 0) or max(1, work["evaluation_count"])*sum(max(1, len(child.circuit.operations)) for child in children)
    return PreparedDerivative(request, node, plan, point, classical, second, direction, size,
        layout, single, spec, output_size, work, int(buffers), int(workspace))
