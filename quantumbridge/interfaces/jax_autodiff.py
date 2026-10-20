# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Optional CPU JAX graphs around existing native plans and quantum Jacobians."""

from copy import copy, deepcopy
from dataclasses import dataclass, replace
from numbers import Integral, Real

import numpy as np

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan, map_measurements
from quantumbridge.diff.trace import Dual, flatten_tree, unflatten_tree
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.qml.tape import Tape
from quantumbridge.utils.math import Hamiltonian, PauliString


class MissingOptionalDependency(ImportError):
    """The requested optional framework is not installed."""


@dataclass(frozen=True)
class JAXBridgeLimits:
    max_input_elements: int = 1024
    max_output_elements: int = 100000
    max_jacobian_elements: int = 2000000
    max_parameter_elements: int = 1024
    max_vmap_batch: int = 128
    max_callback_executions: int = 128
    max_total_shots: int = 1000000
    max_transform_tapes: int = 128

    def __post_init__(self):
        if any(isinstance(x, bool) or not isinstance(x, Integral) or x < 1 for x in self.__dict__.values()):
            raise ValueError("JAX bridge limits require positive integers.")

    def check(self, name, value):
        if value > getattr(self, name):
            raise MemoryError("Native JAX bridge exceeded " + name)


def _shape_tree(tree, width, shots, limits):
    elements = 0
    def shape(request):
        nonlocal elements
        if request.kind in {"expval", "var"}:
            elements += 1
            limits.check("max_output_elements", elements)
            return 0.
        if request.kind != "probs":
            raise UnsupportedFeature("jax_measurement", "JAX derivatives currently require real expval/var/probs outputs.")
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


class _NativeKernel:
    """A tracer-free source description; every call builds fresh native plans."""

    def __init__(self, node, source, recorder, program, limits):
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
        self.parameters = tuple(recorder.parameters)
        self.angles = list(recorder.angles)
        pending = [source.circuit]
        while pending:
            circuit = pending.pop()
            values = [circuit.global_phase]
            for operation in circuit.operations:
                values.extend(operation.params)
                control = operation.metadata.get("control_node")
                if control is not None:
                    pending.extend(control.bodies)
            if any(type(value).__module__.startswith(("jax", "jaxlib")) for value in values):
                raise UnsupportedFeature("jax_unrecorded_parameter", "Use native Tape parameter recording; raw live circuit parameters cannot enter a host callback.")
        for value in self.angles:
            if isinstance(value, (tuple, list)) or getattr(value, "shape", ()) != ():
                raise UnsupportedFeature("jax_gate_broadcast", "Native JAX gate parameters must be scalar occurrences.")
            if isinstance(value, complex) or getattr(getattr(value, "dtype", None), "kind", None) == "c":
                raise UnsupportedFeature("jax_complex", "Native JAX gate parameters must be real.")
        self.coefficients = []
        self.source = Tape(source.circuit.num_qubits, shots=ShotSpec.parse(source.shots), seed=source.seed)
        self.source.circuit = source.circuit.copy()
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
                    if type(value).__module__.startswith(("jax", "jaxlib")):
                        references.append(len(self.angles))
                        self.angles.append(value)
                        terms.append((1., word))
                    else:
                        references.append(None)
                        terms.append((value, word))
                observable = Hamiltonian(terms)
            elif request.kind in {"expval", "var"} and not isinstance(observable, PauliString):
                raise UnsupportedFeature("jax_observable", "JAX bridge observables require native Pauli/Hamiltonian form.")
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
            raise UnsupportedFeature("jax_random_seed", "Finite-shot JAX execution requires an explicit immutable seed.")
        if node.seed is not None and (isinstance(node.seed, bool) or not isinstance(node.seed, Integral) or node.seed < 0):
            raise UnsupportedFeature("jax_random_seed", "JAX node seeds must be immutable nonnegative integers; dynamic PRNG keys are not implemented.")
        self.shape_tree = _shape_tree(self.source.output_tree, node.num_qubits, self.shots, limits)
        flat, self.spec = flatten_tree(self.shape_tree)
        self.output_size = len(flat)
        limits.check("max_jacobian_elements", self.output_size * max(1, self.size))
        limits.check("max_jacobian_elements", self.size * self.size)
        # Preflight native capability and expansion without quantum execution.
        plan = self.plan(np.ones(self.size))
        limits.check("max_parameter_elements", len(plan.recorder.parameters))
        limits.check("max_jacobian_elements", len(plan.recorder.parameters) * max(1, self.size))
        children = getattr(plan, "child_plans", (plan,))
        limits.check("max_transform_tapes", len(children))
        for child in children:
            method = child.gradient_capability(node.diff_method)
            if method == "finite-diff":
                raise UnsupportedFeature("jax_gradient_method", "JAX bridge requires native shift or adjoint, not finite differences.")
            from quantumbridge.diff.adjoint import gate_derivative
            for operation in child._occurrences().values():
                gate_derivative(operation, (1.,))
        work = 0
        for child in children:
            method = child.gradient_capability(node.diff_method)
            repetitions = 2 + sum(4 if operation.name in {"crx", "cry", "crz"} else 2
                                  for operation in child._occurrences().values()) if method != "adjoint" else 2
            for request in child.requests:
                if request.seed is not None and (request.shots is not None or any(self.shots.partitions)):
                    raise UnsupportedFeature("local_seed_gradient", "JAX shifted sampling needs independent node-level seed streams.")
                effective = tuple(request.shots if request.shots is not None else x for x in child.shots.partitions)
                if request.kind == "var" and any(effective):
                    raise UnsupportedFeature("sampled_variance_gradient")
                terms = len(request.observable.terms) if isinstance(request.observable, Hamiltonian) else 1
                work += sum(x or 0 for x in effective) * terms * repetitions
        limits.check("max_total_shots", work)

    def plan(self, values, *, derivative=False):
        from quantumbridge.transforms.program import TransformedExecutionPlan
        if np.asarray(values).shape != (self.size,) or not np.all(np.isfinite(values)):
            raise ValueError("JAX packed parameters must have the declared shape and finite real values.")
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

    def run(self, values, derivative):
        plan = self.plan(values, derivative=derivative)
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
            raise ValueError("Native execution changed the declared JAX output structure.")
        if not np.all(np.isfinite(flat)) or matrix is not None and not np.all(np.isfinite(matrix)):
            raise ValueError("Native JAX execution produced a nonfinite value or derivative.")
        return flat, matrix, {**plan.metadata, "interface": "jax", "native_jax": True,
                              "native_quantum_derivative": bool(derivative), "higher_order": False}


def execute_jax(node, args, kwargs, *, return_status=False):
    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:
        raise MissingOptionalDependency("Native JAX QNode requires optional jax/jaxlib.") from exc
    if node.max_diff != 1:
        raise UnsupportedFeature("higher_order_derivatives", "Native JAX currently supports first derivatives only.")
    if set(node.gradient_kwargs) - {"step"}:
        raise UnsupportedFeature("jax_gradient_options", "Set the native gradient method through diff_method; JAX gradient_kwargs supports only a static step.")
    step = node.gradient_kwargs.get("step", 1e-6)
    if isinstance(step, bool) or not isinstance(step, Real) or not np.isfinite(step) or step <= 0:
        raise ValueError("Native JAX derivative step must be a finite positive real scalar.")
    if jax.default_backend() != "cpu":
        raise UnsupportedFeature("jax_device", "The native JAX bridge currently supports CPU host execution only.")
    from quantumbridge.devices import StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice
    if not isinstance(node.device, (StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice)):
        raise UnsupportedFeature("jax_device", "JAX execution requires a supported native vector/density/MPS device.")
    limits = JAXBridgeLimits() if node.jax_limits is None else node.jax_limits
    if not isinstance(limits, JAXBridgeLimits):
        raise TypeError("jax_limits requires JAXBridgeLimits.")
    leaves = jax.tree_util.tree_leaves((args, kwargs))
    numeric = [value for value in leaves if hasattr(value, "dtype") or isinstance(value, (float, int, bool))]
    if any(jnp.asarray(value).dtype.kind == "c" for value in numeric):
        raise UnsupportedFeature("jax_complex", "Complex inputs/outputs do not have a verified native JAX derivative contract.")
    floating = [jnp.asarray(value) for value in numeric if jnp.asarray(value).dtype.kind == "f"]
    limits.check("max_input_elements", sum(jnp.asarray(value).size for value in numeric))
    dtype = jnp.result_type(*floating) if floating else jnp.dtype("float32")
    if dtype not in (jnp.float32, jnp.float64):
        raise UnsupportedFeature("jax_dtype", "Native JAX supports float32/float64, respecting process x64 configuration.")
    source, recorder, program = node._construct(args, kwargs, prepare_only=True)
    kernel = _NativeKernel(node, source, recorder, program, limits)
    packed = jnp.stack([jnp.asarray(value, dtype=dtype) for value in kernel.angles]) if kernel.angles else jnp.empty(0, dtype=dtype)
    for value in floating:
        packed = packed + 0 * jnp.sum(value)
    # Callbacks capture only native source structure, never live JAX tracers.
    kernel.angles = []
    out_spec = jax.ShapeDtypeStruct((kernel.output_size,), dtype)
    jac_spec = jax.ShapeDtypeStruct((kernel.output_size, kernel.size), dtype)
    status_spec = jax.ShapeDtypeStruct((), dtype)
    def host(values, derivative):
        array = np.asarray(values, dtype=float)
        value, matrix, metadata = kernel.run(array, derivative)
        if derivative:
            return value.astype(dtype), matrix.astype(dtype), metadata
        return value.astype(dtype), metadata

    def checked(values, derivative):
        # The explicit status is returned as data, not a callback side effect.
        # It is nondifferentiable and always has zero tangent.
        try:
            result = host(values, derivative)
            outputs = result[:2] if derivative else result[:1]
            return (*outputs, np.asarray(0, dtype=dtype)), result[-1]
        except UnsupportedFeature:
            status = 2
        except MemoryError:
            status = 3
        except (ValueError, FloatingPointError):
            status = 1
        except Exception:
            status = 4
        flat = np.full(out_spec.shape, np.nan, dtype=dtype)
        outputs = (flat, np.full(jac_spec.shape, np.nan, dtype=dtype)) if derivative else (flat,)
        return (*outputs, np.asarray(status, dtype=dtype)), {"runtime_status": status, "interface": "jax"}

    def callback_function(derivative):
        from jax.custom_batching import custom_vmap
        specs = (out_spec, jac_spec, status_spec) if derivative else (out_spec, status_spec)
        @custom_vmap
        def callback(values):
            return jax.pure_callback(lambda x: checked(x, derivative)[0], specs, values, vmap_method="sequential")
        @callback.def_vmap
        def batched(axis_size, in_batched, values):
            limits.check("max_vmap_batch", axis_size)
            limits.check("max_callback_executions", axis_size)
            if not in_batched[0]:
                outputs = callback(values)
                return outputs, jax.tree_util.tree_map(lambda _: False, outputs)
            outputs = jax.lax.map(callback, values)
            return outputs, jax.tree_util.tree_map(lambda _: True, outputs)
        return callback

    callbacks = {False: callback_function(False), True: callback_function(True)}

    def evaluate(values, derivative):
        limits.check("max_callback_executions", 1)
        if isinstance(values, jax.core.Tracer):
            node.last_metadata = {"interface": "jax", "execution": "CPU pure host callback",
                                  "trace_configuration_only": True,
                                  "jit_callback_execution_count": "not guaranteed; no side-effect receipt",
                                  "callback_budget_semantics": "logical mapped expansion per axis, not a strict JIT scheduling count",
                                  "runtime_failure": "NaN output plus explicit jax_with_status code 1/2/3/4"}
            return callbacks[derivative](values)
        if return_status:
            outputs, metadata = checked(values, derivative)
        else:
            result = host(values, derivative)
            outputs, metadata = (*result[:-1], np.asarray(0, dtype=dtype)), result[-1]
        node.last_metadata = metadata
        return tuple(jnp.asarray(x) for x in outputs)

    @jax.custom_jvp
    def derivatives(values):
        return evaluate(values, True)

    @derivatives.defjvp
    def reject_higher_order(primals, tangents):
        raise UnsupportedFeature("higher_order_derivatives", "Native JAX second derivatives are not implemented.")

    @jax.custom_jvp
    def native(values):
        return evaluate(values, False)

    @native.defjvp
    def native_jvp(primals, tangents):
        value, matrix, status = derivatives(primals[0])
        return (value, status), (matrix @ tangents[0], jnp.zeros_like(status))

    flat, status = native(packed)
    result = unflatten_tree(flat, kernel.spec)
    return (result, status) if return_status else result
