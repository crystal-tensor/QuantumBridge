# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Framework-free host planning shared by optional autodiff graph bridges."""

from copy import copy, deepcopy
from dataclasses import replace
from numbers import Integral

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan, map_measurements
from quantumbridge.diff.trace import Dual, flatten_tree
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.qml.tape import Tape
from quantumbridge.utils.math import Hamiltonian, PauliString


class MissingOptionalDependency(ImportError):
    """The requested optional framework is not installed."""


def _shape_tree(tree, width, shots, limits, interface):
    elements = 0
    def shape(request):
        nonlocal elements
        if request.kind in {"expval", "var"}:
            elements += 1
            limits.check("max_output_elements", elements)
            return 0.
        if request.kind != "probs":
            raise UnsupportedFeature(interface + "_measurement", "framework derivatives currently require real expval/var/probs outputs.")
        records = (request.metadata or {}).get("measurement_records", ())
        count = len(records) + len(request.wires or ()) if records else width if request.wires is None else len(request.wires)
        if count > 16:
            raise UnsupportedFeature("probability_output_size")
        elements += 1 << count
        limits.check("max_output_elements", elements)
        return {format(index, f"0{count}b") if count else "": 0. for index in range(1 << count)}
    result = map_measurements(tree, shape)
    if shots.is_vector:
        limits.check("max_output_elements", elements * len(shots.partitions))
        return tuple(deepcopy(result) for _ in shots.partitions)
    return result


class NativeHostKernel:
    """A tracer-free source description; every call builds fresh native plans."""

    def __init__(self, node, source, recorder, program, limits, *, interface="jax"):
        self.interface = interface
        prefixes = ("jax", "jaxlib") if interface == "jax" else ("tensorflow",)
        self.node, self.limits = copy(node), limits
        self.node.fn = None
        self.node.device = deepcopy(node.device)
        self.node.gradient_kwargs = dict(node.gradient_kwargs)
        self.node.transform_program = self.node.compiler_options = None
        if program is None:
            self.program = None
        else:
            from quantumbridge.transforms.program import TransformProgram
            self.program = TransformProgram(tuple(deepcopy(stage) for stage in program.transforms), limits=program.limits)
        self.node.last_metadata = {}
        live = [index for index, value in enumerate(recorder.angles) if type(value).__module__.startswith(prefixes)]
        self.parameters = tuple(recorder.parameters[index] for index in live)
        self.angles = [recorder.angles[index] for index in live]
        frozen = {parameter: value for parameter, value in zip(recorder.parameters, recorder.angles)
                  if not type(value).__module__.startswith(prefixes)}
        pending = [source.circuit]
        while pending:
            circuit = pending.pop()
            values = [circuit.global_phase]
            for operation in circuit.operations:
                values.extend(operation.params)
                control = operation.metadata.get("control_node")
                if control is not None:
                    pending.extend(control.bodies)
            if any(type(value).__module__.startswith(prefixes) for value in values):
                raise UnsupportedFeature(interface + "_unrecorded_parameter", "Use native Tape parameter recording; raw live circuit parameters cannot enter a host callback.")
        for value in self.angles:
            if isinstance(value, (tuple, list)) or getattr(value, "shape", ()) != ():
                raise UnsupportedFeature(interface + "_gate_broadcast", "Native framework gate parameters must be scalar occurrences.")
            if isinstance(value, complex) or getattr(getattr(value, "dtype", None), "kind", None) == "c":
                raise UnsupportedFeature(interface + "_complex", "Native framework gate parameters must be real.")
        self.coefficients = []
        self.source = Tape(source.circuit.num_qubits, shots=ShotSpec.parse(source.shots), seed=source.seed)
        self.source.circuit = source.circuit.assign_parameters(frozen, strict=False)
        def clean(request):
            observable = request.observable
            if hasattr(observable, "to_quantumbridge"):
                observable = observable.to_quantumbridge()
            elif hasattr(observable, "to_hamiltonian"):
                observable = observable.to_hamiltonian()
            references = []
            if isinstance(observable, Hamiltonian):
                terms = []
                for value, word in observable.terms:
                    if type(value).__module__.startswith(prefixes):
                        references.append(len(self.angles))
                        self.angles.append(value)
                        terms.append((1., word))
                    else:
                        references.append(None)
                        terms.append((value, word))
                observable = Hamiltonian(terms)
            elif request.kind in {"expval", "var"} and not isinstance(observable, PauliString):
                raise UnsupportedFeature(interface + "_observable", "framework bridge observables require native Pauli/Hamiltonian form.")
            self.coefficients.append(tuple(references))
            return replace(request, observable=observable, metadata=deepcopy(request.metadata))
        self.source.output_tree = map_measurements(source.output_tree, clean)
        self.size = len(self.angles)
        limits.check("max_parameter_elements", self.size)
        self.shots = ShotSpec.parse(node.shots)
        self.node.shots = self.shots
        requests = []
        map_measurements(self.source.output_tree, lambda request: requests.append(request))
        finite = any(part is not None for part in self.shots.partitions) or any(request.shots is not None for request in requests)
        if finite and node.seed is None:
            raise UnsupportedFeature(interface + "_random_seed", "Finite-shot framework execution requires an explicit immutable seed.")
        if node.seed is not None and (isinstance(node.seed, bool) or not isinstance(node.seed, Integral) or node.seed < 0):
            raise UnsupportedFeature(interface + "_random_seed", "framework node seeds must be immutable nonnegative integers; dynamic PRNG keys are not implemented.")
        self.shape_tree = _shape_tree(self.source.output_tree, node.num_qubits, self.shots, limits, interface)
        flat, self.spec = flatten_tree(self.shape_tree)
        self.output_size = len(flat)
        limits.check("max_jacobian_elements", self.output_size * max(1, self.size))
        limits.check("max_jacobian_elements", self.size * self.size)
        if node.max_diff == 2:
            from quantumbridge.diff.higher_order_limits import resolve_higher_order_limits
            second_limits = resolve_higher_order_limits(node.higher_order_limits)
            second_limits.check("max_derivative_order", 2)
            second_limits.check("max_input_parameters", self.size)
            second_limits.check("max_output_elements", self.output_size)
            # Framework second rules return an output-by-parameter HVP, never a
            # packed Hessian. Bound even the checked-error NaN result here.
            second_limits.check("max_memory_bytes", 8*(self.output_size*(1+2*self.size)+self.size*self.size))
        # Preflight native capability and expansion without quantum execution.
        plan = self.plan(np.ones(self.size))
        limits.check("max_parameter_elements", len(plan.recorder.parameters))
        limits.check("max_jacobian_elements", len(plan.recorder.parameters) * max(1, self.size))
        children = getattr(plan, "child_plans", (plan,))
        limits.check("max_transform_tapes", len(children))
        for child in children:
            method = child.gradient_capability(node.diff_method)
            if method == "finite-diff":
                raise UnsupportedFeature(interface + "_gradient_method", "framework bridge requires native shift or adjoint, not finite differences.")
            from quantumbridge.diff.adjoint import gate_derivative
            for operation in child._occurrences().values():
                gate_derivative(operation, (1.,))
        self.forward_shot_bound, self.derivative_shot_bound = self._shot_work(plan)
        limits.check("max_total_shots", self.derivative_shot_bound + (self.forward_shot_bound if interface == "tensorflow" else 0))

    def _shot_work(self, plan):
        work, forward_work = 0, 0
        for child in getattr(plan, "child_plans", (plan,)):
            method = child.gradient_capability(self.node.diff_method)
            repetitions = 2 + sum(4 if operation.name in {"crx", "cry", "crz"} else 2
                                  for operation in child._occurrences().values()) if method != "adjoint" else 2
            for request in child.requests:
                if request.seed is not None and (request.shots is not None or any(self.shots.partitions)):
                    raise UnsupportedFeature("local_seed_gradient", "framework shifted sampling needs independent node-level seed streams.")
                effective = tuple(request.shots if request.shots is not None else x for x in child.shots.partitions)
                if request.kind == "var" and any(effective):
                    raise UnsupportedFeature("sampled_variance_gradient")
                terms = len(request.observable.terms) if isinstance(request.observable, Hamiltonian) else 1
                forward_work += sum(x or 0 for x in effective) * terms
                work += sum(x or 0 for x in effective) * terms * repetitions
        return forward_work, work

    def plan(self, values, *, derivative=False, direction=None):
        from quantumbridge.transforms.program import TransformedExecutionPlan
        if np.asarray(values).shape != (self.size,) or not np.all(np.isfinite(values)):
            raise ValueError("framework packed parameters must have the declared shape and finite real values.")
        if derivative == 2:
            from quantumbridge.diff.second_trace import SecondContext
            context = SecondContext(self.size, direction, limits=self.node.higher_order_limits)
            traced = [context.variable(value, index) for index, value in enumerate(values)]
        else:
            eye = np.eye(self.size) if derivative else None
            traced = [Dual(value, eye[index] if derivative else np.empty(0)) for index, value in enumerate(values)]
        source = self.source.copy()
        references = iter(self.coefficients)
        def restore(request):
            indices = next(references)
            observable = request.observable
            if isinstance(observable, Hamiltonian):
                observable = Hamiltonian([(coefficient if index is None else traced[index], word)
                                          for (coefficient, word), index in zip(observable.terms, indices)])
            return replace(request, observable=observable)
        source.output_tree = map_measurements(self.source.output_tree, restore)
        source.measurements = []
        map_measurements(source.output_tree, lambda request: source.measurements.append(request))
        recorder = AngleRecorder()
        recorder.parameters = list(self.parameters)
        recorder.angles = traced[:len(self.parameters)]
        owner = copy(self.node)
        owner.device = deepcopy(self.node.device)
        if self.program is None:
            return ExecutionPlan(owner, source, source.output_tree, recorder)
        return TransformedExecutionPlan(owner, source, recorder, self.program)

    def run(self, values, derivative, *, remaining_shots=None):
        plan = self.plan(values, derivative=derivative)
        self.limits.check("max_transform_tapes", len(getattr(plan, "child_plans", (plan,))))
        self.limits.check("max_parameter_elements", len(plan.recorder.parameters))
        self.limits.check("max_jacobian_elements", len(plan.recorder.parameters) * max(1, self.size))
        forward_work, derivative_work = self._shot_work(plan)
        self.limits.check("max_total_shots", derivative_work + (forward_work if self.interface == "tensorflow" else 0))
        if remaining_shots is not None and (derivative_work if derivative else forward_work) > remaining_shots:
            raise MemoryError("Native framework bridge exceeded cumulative max_total_shots before execution.")
        point = plan.recorder.native_values()
        if derivative:
            value, matrix, spec = plan.jacobian(point, **self.node.gradient_kwargs)
            matrix = matrix @ plan.recorder.classical_jacobian(self.size)
            self.limits.check("max_total_shots", plan.metadata.get("total_physical_shots", plan.metadata.get("gradient_physical_shots", 0)))
        else:
            value = plan.evaluate(point)
            matrix = None
            _, spec = flatten_tree(value)
        flat, actual = flatten_tree(value)
        if spec != self.spec or actual != self.spec or flat.shape != (self.output_size,):
            raise ValueError("Native execution changed the declared framework output structure.")
        if not np.all(np.isfinite(flat)) or matrix is not None and not np.all(np.isfinite(matrix)):
            raise ValueError("Native framework execution produced a nonfinite value or derivative.")
        return flat, matrix, {**plan.metadata, "interface": self.interface, "native_" + self.interface: True,
                              "native_quantum_derivative": bool(derivative), "higher_order": False}

    def prepare_second(self, values, *, direction=None, remaining_shots=None):
        from quantumbridge.diff.higher_order_limits import resolve_higher_order_limits
        from quantumbridge.diff.second_order import second_work, transformed_second_work
        limits = resolve_higher_order_limits(self.node.higher_order_limits)
        shot_limit = min(limits.max_total_physical_shots, self.limits.max_total_shots)
        if remaining_shots is not None:
            shot_limit = min(shot_limit, max(1, remaining_shots))
        limits = replace(limits, max_total_physical_shots=shot_limit)
        plan = self.plan(values, derivative=2, direction=direction)
        self.limits.check("max_transform_tapes", len(getattr(plan, "child_plans", (plan,))))
        self.limits.check("max_parameter_elements", len(plan.recorder.parameters))
        count = len(plan.recorder.parameters)
        columns = self.size if direction is None else 1
        limits.check("max_memory_bytes", 8*count*self.size*(1+columns))
        point = plan.recorder.native_values()
        classical = plan.recorder.classical_jacobian(self.size)
        second_map = plan.recorder.classical_second(self.size, columns)
        if hasattr(plan, "child_plans"):
            work = transformed_second_work(plan, point, classical, second_map, direction, limits)[0]
        else:
            work = second_work(plan, point, classical, second_map, direction, limits)[3]
        return plan, point, classical, second_map, limits, work

    def run_second(self, values, *, direction=None, remaining_shots=None):
        prepared = self.prepare_second(values, direction=direction, remaining_shots=remaining_shots)
        return self._execute_second(prepared, direction)

    def _execute_second(self, prepared, direction):
        plan, point, classical, second_map, limits, _ = prepared
        value, matrix, second, spec = plan.second_derivatives(point, direction=direction,
            classical=classical, classical_second=second_map, limits=limits)
        flat, actual = flatten_tree(value)
        if spec != self.spec or actual != self.spec or flat.shape != (self.output_size,):
            raise ValueError("Second-order framework execution changed its declared output structure.")
        if not all(np.all(np.isfinite(array)) for array in (flat, matrix, second)):
            raise ValueError("Native framework second derivatives produced a nonfinite value.")
        return flat, matrix, second, {**plan.metadata, "interface": self.interface, "higher_order": True,
                                    "native_"+self.interface: True, "native_quantum_derivative": True}

    def run_second_transpose(self, values, incoming):
        """Transpose the linear HVP map without building an output Hessian.

        Each output row has its own direction. Two streaming passes validate
        the total work before executing any row, without retaining all plans.
        """
        from quantumbridge.diff.higher_order_limits import resolve_higher_order_limits
        values = np.asarray(values)
        if values.shape != (self.size,) or values.dtype.kind not in "fiu" or not np.all(np.isfinite(values)):
            raise ValueError("Second-rule primal values must be finite real packed parameters.")
        incoming = np.asarray(incoming)
        if incoming.shape != (self.output_size, self.size) or incoming.dtype.kind not in "fiu" or not np.all(np.isfinite(incoming)):
            raise ValueError("Second-rule cotangents must match the real output-by-parameter Jacobian.")
        active = [index for index, row in enumerate(incoming) if np.any(row)]
        self.limits.check("max_callback_executions", len(active))
        limits = resolve_higher_order_limits(self.node.higher_order_limits)
        limits.check("max_memory_bytes", 8*(incoming.size+2*self.size))
        totals = dict.fromkeys(("shift_count", "tape_count", "physical_shots", "adjoint_operations"), 0)
        def check_totals(work):
            limits.check("max_shifted_circuits", work["shift_count"])
            limits.check("max_total_tapes", work["tape_count"])
            limits.check("max_total_physical_shots", work["physical_shots"])
            limits.check("max_adjoint_operations", work["adjoint_operations"])
            self.limits.check("max_total_shots", work["physical_shots"])
        for index in active:
            prepared = self.prepare_second(values, direction=incoming[index])
            work = prepared[-1]
            del prepared
            for key in totals: totals[key] += work.get(key, 0)
            check_totals(totals)
        result, receipts = np.zeros(self.size), []
        observed = dict.fromkeys(totals, 0)
        for index in active:
            prepared = self.prepare_second(values, direction=incoming[index])
            check_totals({key: observed[key]+prepared[-1].get(key, 0) for key in observed})
            _, _, product, metadata = self._execute_second(prepared, incoming[index])
            result += product[index, :, 0]
            for key in observed: observed[key] += metadata["second_order_work"].get(key, 0)
            receipts.append({"output_row": index, **metadata})
            del prepared
        if observed != totals:
            raise RuntimeError("Native second-rule transpose work changed after aggregate preflight.")
        return result, {"interface": self.interface, "hvp_streamed": True, "transpose_hvp": True,
                        "native_quantum_derivative": True, "derivative_order": 2,
                        "native_hvp_calls": len(receipts), "total_physical_shots": observed["physical_shots"],
                        "second_order_work": observed, "hvp_executions": receipts}
