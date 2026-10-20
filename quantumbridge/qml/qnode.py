# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import Hamiltonian, PauliString
from .measurements import ClassicalShadowResult, MeasurementRequest
from .tape import Tape


class QNode:
    def __init__(self, fn, num_qubits: int, device=None, shots=None, seed: int | None = None,
                 interface="auto", diff_method="best", gradient_kwargs=None, max_diff=1):
        self.fn = fn
        self.num_qubits = num_qubits
        self.device = device or StatevectorDevice()
        self.shots = shots
        self.seed = seed
        self.interface, self.diff_method = interface, diff_method
        self.gradient_kwargs = dict(gradient_kwargs or {})
        self.max_diff = max_diff
        self.last_metadata = {}
        self.compiler_options = None
        self.transform_program = None
        from .shot_vector import ShotSpec
        ShotSpec.parse(shots)
        if interface not in {None, "auto", "numpy", "torch", "autograd", "jax", "tf", "tensorflow"}:
            raise ValueError("Unknown QuantumBridge QNode interface.")

    def _construct(self, args, kwargs):
        from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan, measurement_tree
        if self.transform_program is not None:
            from quantumbridge.interfaces.qnode_autodiff import _leaves
            from quantumbridge.transforms.program import _reject_live
            _reject_live(_leaves((args, kwargs)))
        recorder = AngleRecorder()
        tape = Tape(self.num_qubits, recorder, shots=self.shots, seed=self.seed)
        returned = self.fn(tape, *args, **kwargs)
        if self.compiler_options is not None:
            from quantumbridge.compiler import native_transpile
            from quantumbridge.diff.compiled_parameters import record_compiled_parameters
            from quantumbridge.core.classical import UnsupportedFeature
            compiled = native_transpile(tape.circuit, **self.compiler_options)
            identity = dict(enumerate(range(self.num_qubits)))
            if compiled.num_qubits != self.num_qubits or compiled.metadata.get("initial_layout") != identity or compiled.metadata.get("routing", {}).get("final_layout", identity) != identity:
                raise UnsupportedFeature("compiled_qnode_layout", "QNode measurements currently require equal width and restored identity layout.")
            tape.circuit, recorder = record_compiled_parameters(compiled, recorder)
        tree = measurement_tree(returned, tape)
        if self.transform_program is None:
            plan = ExecutionPlan(self, tape, tree, recorder)
        else:
            from quantumbridge.transforms.program import TransformedExecutionPlan
            tape.output_tree = tree
            plan = TransformedExecutionPlan(self, tape, recorder, self.transform_program)
        plan.input_values = (args, kwargs)
        return plan

    def with_transform(self, transform, *, limits=None):
        """Return an independent QNode using a fresh transformed batch per call."""
        from copy import copy
        from quantumbridge.transforms.program import TransformProgram
        previous = self.transform_program
        prefix = () if previous is None else previous.transforms
        stages = transform.transforms if isinstance(transform, TransformProgram) else (transform,)
        if limits is None:
            limits = getattr(transform, "limits", None) if previous is None else previous.limits
        result = copy(self)
        result.last_metadata = {}
        result.transform_program = TransformProgram(prefix + stages, limits=limits)
        return result

    def compile(self, **options):
        from copy import copy
        result = copy(self)
        result.compiler_options, result.last_metadata = dict(options), {}
        return result

    @classmethod
    def from_circuit(cls,circuit,observable,**options):
        """Execute a native parameterized Circuit; Python callables are not serialized."""
        from quantumbridge.diff.qnode_engine import AngleRecorder
        from quantumbridge.diff.compiled_parameters import record_compiled_parameters
        parameters = circuit.parameters
        def program(tape,*values):
            if len(values) == 1 and isinstance(values[0],(tuple,list)):
                values = tuple(values[0])
            elif len(values) == 1 and hasattr(values[0],"shape") and values[0].shape:
                values = tuple(values[0].reshape(-1))
            if len(values) != len(parameters): raise ValueError("Circuit QNode argument count must match its free parameter count.")
            source = AngleRecorder()
            source.parameters,source.angles = list(parameters),list(values)
            prepared,recorded = record_compiled_parameters(circuit,source)
            mapping = {parameter:tape.parameter_transform(value) for parameter,value in zip(recorded.parameters,recorded.angles)}
            tape.circuit = prepared.assign_parameters(mapping)
            return tape.expval(observable)
        return cls(program,circuit.num_qubits,**options)

    def __call__(self, *args, **kwargs):
        from quantumbridge.interfaces.qnode_autodiff import execute_interface, infer_interface
        interface = infer_interface(args, kwargs) if self.interface == "auto" else self.interface
        plan = self._construct(args, kwargs)
        if interface in {None, "numpy"}:
            result = plan.evaluate(plan.recorder.native_values())
        else: result = execute_interface(plan, interface)
        self.last_metadata = plan.metadata
        return result

    def _differentiate(self, args, kwargs, argnums=0, argnames=(), method=None):
        from quantumbridge.core.classical import UnsupportedFeature
        from quantumbridge.diff.trace import trace_arguments
        if self.max_diff != 1: raise UnsupportedFeature("higher_order_derivatives", "Native QNode currently validates first derivatives only.")
        if isinstance(argnums, str): argnames, argnums = (argnums,), ()
        if argnums == 0 and not args and not argnames:
            import inspect
            name = next(iter(tuple(inspect.signature(self.fn).parameters)[1:]), None)
            if name not in kwargs: raise ValueError("No first trainable QNode argument was supplied.")
            argnames, argnums = (name,), ()
        traced_args, traced_kwargs, layout, single, size = trace_arguments(args, kwargs, argnums, argnames)
        plan = self._construct(traced_args, traced_kwargs)
        base, matrix, spec = plan.jacobian(plan.recorder.native_values(), method, **self.gradient_kwargs)
        classical = plan.recorder.classical_jacobian(size)
        matrix = matrix @ classical
        self.last_metadata = {**plan.metadata, "classical_chain_rule": True, "input_parameter_count": size,
                              "gate_parameter_count": len(plan.recorder.parameters),
                              "trainable_gate_occurrences": np.flatnonzero(np.any(classical != 0, axis=1)).tolist()}
        return base, matrix, spec, layout, single

    @staticmethod
    def _input_results(values, layout, single):
        results = [values[indices].reshape(shape) for shape, indices in layout]
        results = [value.item() if not value.shape else value for value in results]
        return results[0] if single else tuple(results)

    def compute_jacobian(self, *args, argnums=0, argnames=(), method=None, **kwargs):
        from quantumbridge.diff.trace import unflatten_tree
        _, matrix, spec, layout, single = self._differentiate(args, kwargs, argnums, argnames, method)
        result = [unflatten_tree(matrix[:, indices], spec, shape) for shape, indices in layout]
        return result[0] if single else tuple(result)

    jacobian = compute_jacobian

    def gradient(self, *args, argnums=0, argnames=(), method=None, **kwargs):
        base, matrix, spec, layout, single = self._differentiate(args, kwargs, argnums, argnames, method)
        if len(matrix) != 1: raise ValueError("QNode.gradient requires a scalar output; use jacobian for multiple outputs.")
        return self._input_results(matrix[0], layout, single)

    def compute_vjp(self, cotangent, *args, argnums=0, argnames=(), method=None, **kwargs):
        return self.execute_and_compute_vjp(cotangent, *args, argnums=argnums, argnames=argnames, method=method, **kwargs)[1]

    def execute_and_compute_vjp(self, cotangent, *args, argnums=0, argnames=(), method=None, **kwargs):
        from quantumbridge.diff.trace import flatten_tree
        base, matrix, spec, layout, single = self._differentiate(args, kwargs, argnums, argnames, method)
        vector, cotangent_spec = flatten_tree(cotangent)
        if spec != cotangent_spec: raise ValueError("Cotangent tree/shape must match the QNode output.")
        return base, self._input_results(vector @ matrix, layout, single)

    def compute_jvp(self, tangent, *args, argnums=0, argnames=(), method=None, **kwargs):
        return self.execute_and_compute_jvp(tangent, *args, argnums=argnums, argnames=argnames, method=method, **kwargs)[1]

    def execute_and_compute_jvp(self, tangent, *args, argnums=0, argnames=(), method=None, **kwargs):
        from quantumbridge.diff.trace import unflatten_tree
        base, matrix, spec, layout, single = self._differentiate(args, kwargs, argnums, argnames, method)
        tangents = [tangent] if single else list(tangent)
        if len(tangents) != len(layout) or any(np.asarray(value).shape != shape for value, (shape, _) in zip(tangents, layout)):
            raise ValueError("Tangent shapes must match the trainable arguments.")
        if any(np.iscomplexobj(value) for value in tangents): raise TypeError("Real inputs require real tangents.")
        vector = np.concatenate([np.asarray(value, dtype=float).reshape(-1) for value in tangents])
        return base, unflatten_tree(matrix @ vector, spec)

    def execute_and_compute_derivatives(self, *args, argnums=0, argnames=(), method=None, **kwargs):
        from quantumbridge.diff.trace import unflatten_tree
        base, matrix, spec, layout, single = self._differentiate(args, kwargs, argnums, argnames, method)
        result = [unflatten_tree(matrix[:, indices], spec, shape) for shape, indices in layout]
        return base, result[0] if single else tuple(result)

    def _execute_measurement(self, tape: Tape, request: MeasurementRequest):
        wires = _validate_wires(request.wires, self.num_qubits)
        if request.kind == "expval":
            return self.device.expectation(tape.circuit, request.observable)
        if request.kind == "var":
            return self.device.variance(tape.circuit, request.observable)
        if request.kind == "probs":
            return self.device.probabilities(tape.circuit, wires=wires)
        if request.kind == "state":
            if hasattr(self.device, "state"):
                return self.device.state(tape.circuit)
            return self.device.statevector(tape.circuit)
        if request.kind == "density_matrix":
            if hasattr(self.device, "reduced_density_matrix"):
                return self.device.reduced_density_matrix(tape.circuit, wires=wires)
            matrix = self.device.density_matrix(tape.circuit)
            return matrix if wires is None else _partial_density_matrix(matrix, self.num_qubits, wires)
        if request.kind == "sample":
            shots = _resolve_shots(request.shots, self.shots, "sample")
            seed = request.seed if request.seed is not None else self.seed
            return self.device.sample(tape.circuit, wires=wires, shots=shots, seed=seed)
        if request.kind == "counts":
            shots = _resolve_shots(request.shots, self.shots, "counts")
            seed = request.seed if request.seed is not None else self.seed
            return self.device.counts(tape.circuit, wires=wires, shots=shots, seed=seed)
        if request.kind == "classical_shadow":
            shots = _resolve_shots(request.shots, self.shots, "classical_shadow")
            seed = request.seed if request.seed is not None else self.seed
            return _classical_shadow(self.device, tape.circuit, self.num_qubits, wires, shots, seed)
        if request.kind == "shadow_expval":
            shots = _resolve_shots(request.shots, self.shots, "shadow_expval")
            seed = request.seed if request.seed is not None else self.seed
            shadow = _classical_shadow(self.device, tape.circuit, self.num_qubits, wires, shots, seed)
            k = None if request.metadata is None else request.metadata.get("k")
            return _shadow_expectation(shadow, request.observable, k=k)
        raise ValueError(f"Unsupported QuantumBridge QML measurement kind: {request.kind!r}")


def _returned_measurements(returned) -> tuple[MeasurementRequest, ...]:
    if isinstance(returned, MeasurementRequest):
        return (returned,)
    if isinstance(returned, (list, tuple)) and all(isinstance(item, MeasurementRequest) for item in returned):
        return tuple(returned)
    return ()


def _validate_wires(wires: tuple[int, ...] | None, num_qubits: int) -> tuple[int, ...] | None:
    if wires is None:
        return None
    selected = tuple(wires)
    if len(set(selected)) != len(selected):
        raise ValueError("QuantumBridge QML measurement wires must be unique.")
    if any(wire < 0 or wire >= num_qubits for wire in selected):
        raise ValueError(f"QuantumBridge QML measurement wires must be in [0, {num_qubits}).")
    return selected


def _resolve_shots(request_shots, node_shots, measurement: str) -> int:
    shots = request_shots if request_shots is not None else node_shots
    if isinstance(shots, bool) or not isinstance(shots, (int, np.integer)) or shots <= 0:
        raise ValueError(f"QuantumBridge QML {measurement} requires a positive integer number of shots.")
    return int(shots)


def _partial_density_matrix(matrix: np.ndarray, num_qubits: int, wires: tuple[int, ...]) -> np.ndarray:
    selected = tuple(wires)
    traced = tuple(wire for wire in range(num_qubits) if wire not in selected)
    size = 1 << len(selected)
    reduced = np.zeros((size, size), dtype=complex)
    for row in range(1 << num_qubits):
        for col in range(1 << num_qubits):
            if all(_bit(row, wire, num_qubits) == _bit(col, wire, num_qubits) for wire in traced):
                reduced[
                    _project_index(row, selected, num_qubits),
                    _project_index(col, selected, num_qubits),
                ] += matrix[row, col]
    return reduced


def _bit(index: int, wire: int, num_qubits: int) -> int:
    return (index >> (num_qubits - 1 - wire)) & 1


def _project_index(index: int, wires: tuple[int, ...], num_qubits: int) -> int:
    out = 0
    for wire in wires:
        out = (out << 1) | _bit(index, wire, num_qubits)
    return out


def _classical_shadow(device, circuit, num_qubits: int, wires: tuple[int, ...] | None, shots: int, seed: int | None):
    selected = tuple(range(num_qubits)) if wires is None else tuple(wires)
    rng = np.random.default_rng(seed)
    recipes = rng.integers(0, 3, size=(shots, len(selected)), dtype=np.int8)
    bits = np.zeros((shots, len(selected)), dtype=np.int8)
    unique_recipes, groups = np.unique(recipes, axis=0, return_inverse=True)
    for group, recipe_row in enumerate(unique_recipes):
        indices = np.flatnonzero(groups == group)
        rotated = circuit.copy()
        for wire, recipe_value in zip(selected, recipe_row):
            recipe = int(recipe_value)
            if recipe == 0:
                rotated.h(wire)
            elif recipe == 1:
                rotated.sdg(wire)
                rotated.h(wire)
        group_seed = int(rng.integers(0, 2**32 - 1))
        samples = device.sample(rotated, wires=selected, shots=len(indices), seed=group_seed)
        for index, bitstring in zip(indices, samples):
            bits[index] = np.fromiter((int(bit) for bit in bitstring), dtype=np.int8, count=len(selected))
    return ClassicalShadowResult(
        bits=bits,
        recipes=recipes,
        wires=selected,
        metadata={
            "measurement": "classical_shadow",
            "shots": shots,
            "seed": seed,
            "recipe_encoding": {"X": 0, "Y": 1, "Z": 2},
        },
    )


def _shadow_expectation(shadow: ClassicalShadowResult, observable, k=None):
    if isinstance(observable, (list, tuple)):
        return np.asarray([_shadow_expectation(shadow, item, k=k) for item in observable], dtype=float)
    per_shot = _shadow_observable_samples(shadow, observable)
    partitions = _resolve_shadow_partitions(k, len(per_shot))
    means = [float(np.mean(partition)) for partition in np.array_split(per_shot, partitions)]
    return float(np.median(means))


def _shadow_observable_samples(shadow: ClassicalShadowResult, observable) -> np.ndarray:
    if hasattr(observable, "to_hamiltonian"):
        observable = observable.to_hamiltonian()
    if isinstance(observable, PauliString):
        return _shadow_pauli_samples(shadow, observable)
    if isinstance(observable, Hamiltonian):
        estimate = np.zeros(len(shadow.bits), dtype=float)
        for coefficient, pauli in observable.terms:
            estimate += coefficient * _shadow_pauli_samples(shadow, pauli)
        return estimate
    raise TypeError("QuantumBridge shadow_expval supports PauliString and Hamiltonian observables.")


def _shadow_pauli_samples(shadow: ClassicalShadowResult, observable: PauliString) -> np.ndarray:
    wire_positions = {wire: offset for offset, wire in enumerate(shadow.wires)}
    seen: set[int] = set()
    estimate = np.ones(len(shadow.bits), dtype=float)
    recipe_for = {"X": 0, "Y": 1, "Z": 2}
    for wire, label in observable.terms:
        if label == "I":
            continue
        if wire in seen:
            raise ValueError("QuantumBridge shadow_expval Pauli terms must use unique wires.")
        seen.add(wire)
        if wire not in wire_positions:
            raise ValueError(f"Observable wire {wire} is not present in the classical shadow wires.")
        offset = wire_positions[wire]
        matches = shadow.recipes[:, offset] == recipe_for[label]
        eigenvalues = 1.0 - 2.0 * shadow.bits[:, offset]
        estimate *= np.where(matches, 3.0 * eigenvalues, 0.0)
    return estimate


def _resolve_shadow_partitions(k, shots: int) -> int:
    if k is None:
        return 1
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k <= 0 or k > shots:
        raise ValueError("QuantumBridge shadow_expval k must be a positive integer no larger than shots.")
    return int(k)
