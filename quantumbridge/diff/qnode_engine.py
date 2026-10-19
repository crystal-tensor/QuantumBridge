# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native gate-occurrence derivatives and executable QNode plans.

from dataclasses import replace
from types import SimpleNamespace
import warnings
import numpy as np

from quantumbridge.core import Parameter
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.qml.measurements import MeasurementRequest
from quantumbridge.qml.shot_vector import ShotSpec
from quantumbridge.utils.math import Hamiltonian, PauliString, observable_matrix
from .adjoint import adjoint_rows, gate_derivative
from .trace import Dual, flatten_tree, unflatten_tree


class AngleRecorder:
    def __init__(self):
        self.parameters, self.angles = [], []

    def __call__(self, value):
        if len(self.angles) >= 4096: raise MemoryError("Native QNode exceeds the 4096 gate-angle budget.")
        parameter = Parameter(f"__qb_angle_{len(self.angles)}")
        self.parameters.append(parameter)
        self.angles.append(value)
        return parameter

    def native_values(self):
        values = np.asarray([angle.value if isinstance(angle, Dual) else angle for angle in self.angles], dtype=float)
        if values.shape != (len(self.angles),): raise ValueError("Quantum gate angles must be real scalars; parameter broadcasting is not implemented.")
        if not np.all(np.isfinite(values)): raise ValueError("Native QNode angles must be finite real scalars.")
        return values

    def classical_jacobian(self, size):
        result = np.asarray([angle.derivative if isinstance(angle, Dual) else np.zeros(size) for angle in self.angles]).reshape(len(self.angles), size)
        if not np.all(np.isfinite(result)): raise ValueError("Classical preprocessing has a nonfinite derivative.")
        return result


def measurement_tree(returned, tape):
    def valid(value):
        if isinstance(value, MeasurementRequest): return True
        if isinstance(value, dict): return bool(value) and all(valid(child) for child in value.values())
        return isinstance(value, (tuple, list)) and bool(value) and all(valid(child) for child in value)
    if valid(returned): return returned
    if isinstance(returned, dict): raise UnsupportedFeature("mixed_output_tree", "QNode return dictionaries must contain measurement requests, not discarded constants.")
    if tape.measurements:
        return tape.measurements[0] if len(tape.measurements) == 1 else tuple(tape.measurements)
    return MeasurementRequest(tape.measurement or "expval", observable=tape.observable if tape.observable is not None else returned)


def map_measurements(tree, function):
    if isinstance(tree, MeasurementRequest): return function(tree)
    if isinstance(tree, dict): return {key: map_measurements(child, function) for key, child in tree.items()}
    children = [map_measurements(child, function) for child in tree]
    return tuple(children) if isinstance(tree, tuple) else children


class ExecutionPlan:
    def __init__(self, node, tape, tree, recorder):
        self.node, self.circuit, self.tree, self.recorder = node, tape.circuit, tree, recorder
        self.requests = []
        map_measurements(tree, lambda request: self.requests.append(request))
        self.shots = ShotSpec.parse(node.shots)
        self.legacy_state_queries = any(request.kind in {"state", "density_matrix"} for request in self.requests)
        if self.legacy_state_queries and any(shots is not None for shots in self.shots.partitions):
            warnings.warn("Legacy QNode state queries keep state/expval/var/probs analytic; shots apply only to sampled measurements. Prefer local sample/counts shots with an analytic QNode.", FutureWarning, stacklevel=3)
        from quantumbridge.core.control_flow import ExecutionLimits
        self.limits = getattr(node.device, "execution_limits", None) or ExecutionLimits()
        if sum(shots or 0 for shots in self.shots.partitions) > self.limits.max_shots:
            raise ValueError("QNode shot vector exceeds the total max_shots budget.")
        self.metadata = {}
        self.last_spec = None
        self.resource_history = []

    def _sampling(self, circuit, request, shots, seed):
        device, width = self.node.device, circuit.num_qubits
        observable = request.observable
        if hasattr(observable, "to_hamiltonian"): observable = observable.to_hamiltonian()
        if request.kind == "expval" and isinstance(observable, Hamiltonian):
            return sum(coefficient * self._sampling(circuit, replace(request, observable=pauli), shots, None if seed is None else seed + index)[0]
                       for index, (coefficient, pauli) in enumerate(observable.terms)), None
        if isinstance(observable, PauliString):
            rotated, wires = circuit.copy(), []
            for wire, label in observable.terms:
                if label == "I": continue
                wires.append(wire)
                if label == "X": rotated.h(wire)
                elif label == "Y": rotated.sdg(wire).h(wire)
            if not wires: samples = np.ones(shots)
            else:
                labels = device.sample(rotated, wires=wires, shots=shots, seed=seed)
                samples = np.asarray([(-1.) ** label.count("1") for label in labels])
        else:
            if width > 10: raise UnsupportedFeature("finite_shot_observable", "Large finite-shot observables require Pauli/Hamiltonian form.")
            matrix = observable_matrix(observable, width)
            if matrix.shape != (1 << width, 1 << width) or not np.allclose(matrix, matrix.conj().T): raise ValueError("Sampled observable must be Hermitian.")
            eigenvalues, vectors = np.linalg.eigh(matrix)
            rotated = circuit.copy().unitary(vectors.conj().T, list(range(width)))
            labels = device.sample(rotated, shots=shots, seed=seed)
            samples = eigenvalues[[int(label, 2) for label in labels]]
        return (float(np.mean(samples)) if request.kind == "expval" else float(np.var(samples))), float(np.mean(samples))

    def evaluate(self, values, linear=False):
        if len(values) != len(self.recorder.parameters): raise ValueError("QNode angle shape mismatch.")
        bound = self.circuit.bind(dict(zip(self.recorder.parameters, values)))
        outputs, partitions, corrections = [], [], []
        for shots, seed in zip(self.shots.partitions, self.shots.seeds(self.node.seed)):
            statistics, spans, offset, measurement_metadata = [], [], 0, []
            def execute(request):
                nonlocal offset
                effective_shots = request.shots if request.shots is not None else shots
                if self.legacy_state_queries and request.kind in {"state", "density_matrix", "expval", "var", "probs"}:
                    effective_shots = None
                effective_seed = request.seed if request.seed is not None else seed
                if effective_shots is not None and (isinstance(effective_shots, bool) or not isinstance(effective_shots, (int, np.integer)) or effective_shots < 1):
                    raise ValueError("QNode measurement shots must be positive integers.")
                if effective_shots is not None and effective_shots > self.limits.max_shots:
                    raise ValueError("QNode shots exceed max_shots.")
                measurement_metadata.append({"kind": request.kind, "shots": effective_shots, "seed": effective_seed})
                if request.kind == "probs" and len(request.wires if request.wires is not None else range(bound.num_qubits)) > 16:
                    raise UnsupportedFeature("probability_output_size", "QNode probability output exceeds the native budget.")
                if request.kind in {"expval", "var"} and effective_shots is not None:
                    value, mean = self._sampling(bound, request, effective_shots, effective_seed)
                else:
                    request_bound = replace(request, shots=effective_shots, seed=effective_seed)
                    value = self.node._execute_measurement(SimpleNamespace(circuit=bound), request_bound)
                    mean = self.node.device.expectation(bound, request.observable) if request.kind == "var" else None
                if request.kind == "probs":
                    wires = tuple(range(bound.num_qubits)) if request.wires is None else request.wires
                    labels = [format(index, f"0{len(wires)}b") if wires else "" for index in range(1 << len(wires))]
                    if effective_shots is not None:
                        counts = self.node.device.counts(bound, wires=wires, shots=effective_shots, seed=effective_seed)
                        value = {label: counts.get(label, 0) / effective_shots for label in labels}
                    else: value = {label: value.get(label, 0.) for label in labels}
                if linear and request.kind == "var":
                    statistics.append(mean)
                    spans.append((offset, len(statistics) - 1, mean))
                    value += mean ** 2
                try: size = flatten_tree(value)[0].size
                except UnsupportedFeature:
                    size = 0
                offset += size
                return value
            output = map_measurements(self.tree, execute)
            if linear:
                vector, spec = flatten_tree(output)
                output = np.concatenate([vector, statistics])
                corrections.append((len(vector), spans, spec))
            outputs.append(output)
            partition = {"shots": shots, "seed": seed, "measurements": measurement_metadata,
                         "simulation": getattr(self.node.device, "simulation", "statevector")}
            if getattr(self.node.device, "simulation", None) == "matrix_product_state":
                resource_shots = max((item["shots"] or 0 for item in measurement_metadata), default=0)
                result = self.node.device.run_shots(bound, shots=resource_shots, seed=seed) if resource_shots else self.node.device.run(bound)
                resource = result.metadata()
                partition["resources"] = {key: value for key, value in resource.items() if key not in {"mps_ensemble", "classical_ensemble"}}
                if result.mps is not None:
                    partition["resources"]["bond_dimensions"] = list(result.mps.bond_dimensions)
                else:
                    partition["resources"]["ensemble_bond_dimensions"] = [
                        [len(tensor["real"][0][0]) for tensor in item["state"]["tensors"][:-1]]
                        for item in resource.get("mps_ensemble", ())]
                partition["approximation_warning"] = "MPS truncation may bias values/gradients; discarded weights are not a final infidelity bound."
                self.resource_history.append(partition)
            partitions.append(partition)
        self.metadata = {"partitions": partitions, "native_execution": True, "legacy_analytic_state_queries": self.legacy_state_queries}
        if linear:
            return outputs, corrections
        result = tuple(outputs) if self.shots.is_vector else outputs[0]
        try: _, self.last_spec = flatten_tree(result)
        except UnsupportedFeature: self.last_spec = None
        return result

    def gradient_capability(self, method):
        if getattr(self.node.device, "simulation", None) == "exact_stabilizer": raise UnsupportedFeature("tableau_continuous_gradient")
        if any(request.kind not in {"expval", "var", "probs"} for request in self.requests): raise UnsupportedFeature("gradient_measurement")
        if method == "backprop": raise UnsupportedFeature("simulator_backprop", "Framework VJPs are available; differentiable simulator backprop is not implemented.")
        if method not in {"parameter-shift", "finite-diff", "adjoint", "best"}: raise UnsupportedFeature("gradient_method", f"Unknown native gradient method {method}.")
        from quantumbridge.devices import StatevectorDevice
        analytic = all(shots is None for shots in self.shots.partitions) and all(request.shots is None for request in self.requests)
        adjoint_ok = type(self.node.device) is StatevectorDevice and not self.circuit.has_dynamic_operations and analytic
        if method == "best": method = "adjoint" if adjoint_ok else "parameter-shift"
        if method == "adjoint" and not adjoint_ok: raise UnsupportedFeature("adjoint_capability", "Adjoint requires analytic unitary Statevector execution.")
        return method

    def _occurrences(self):
        found = {}
        def walk(circuit, in_loop=False):
            for operation in circuit.operations:
                node = operation.metadata.get("control_node")
                if node is not None:
                    for body in node.bodies: walk(body, in_loop or node.kind in {"for", "while"})
                for index, parameter in enumerate(operation.params):
                    if isinstance(parameter, Parameter) and parameter in self.recorder.parameters:
                        if in_loop: raise UnsupportedFeature("parameterized_loop_gradient", "A reused loop-body occurrence needs a loop-aware gradient rule.")
                        if parameter in found: raise UnsupportedFeature("reused_gate_occurrence", "Shared inputs must retain separate gate occurrences.")
                        if index or len(operation.params) != 1: raise UnsupportedFeature("gate_gradient_recipe")
                        found[parameter] = operation
        walk(self.circuit)
        return found

    def jacobian(self, values, method=None, step=1e-6):
        method = self.gradient_capability(method or self.node.diff_method)
        base = self.evaluate(values)
        flat, spec = flatten_tree(base)
        if flat.size * max(1, len(values)) > 2000000: raise MemoryError("QNode Jacobian exceeds the output budget.")
        evaluations = 0
        if method == "adjoint":
            matrix = adjoint_rows(self.node.device, self.circuit, tuple(self.recorder.parameters), values, self.requests)
            evaluations = 1
        else:
            if not np.isfinite(step) or step <= 0: raise ValueError("Finite-difference step must be positive and finite.")
            occurrences = self._occurrences()
            base_linear, corrections = self.evaluate(values, linear=True)
            rows = sum(len(part) for part in base_linear)
            matrix_linear = np.zeros((rows, len(values)))
            for index, parameter in enumerate(self.recorder.parameters):
                operation = occurrences.get(parameter)
                if operation is None: continue
                if method == "finite-diff": recipes = [(1 / (2 * step), step)]
                else:
                    gate_derivative(operation, (values[index],))
                    if operation.name in {"crx", "cry", "crz"}:
                        shifts = np.asarray([np.pi / 2, 3 * np.pi / 2])
                        frequencies = np.asarray([.5, 1.])
                        coefficients = np.linalg.solve(2 * np.sin(frequencies[:, None] * shifts), frequencies)
                        recipes = zip(coefficients, shifts)
                    else: recipes = [(.5, np.pi / 2)]
                for coefficient, shift in recipes:
                    plus, minus = np.array(values, copy=True), np.array(values, copy=True)
                    plus[index] += shift; minus[index] -= shift
                    upper, _ = self.evaluate(plus, linear=True)
                    lower, _ = self.evaluate(minus, linear=True)
                    matrix_linear[:, index] += coefficient * (np.concatenate(upper) - np.concatenate(lower))
                    evaluations += 2
            matrix, offset = [], 0
            for length, spans, _ in corrections:
                part = matrix_linear[offset:offset + length].copy()
                for row, mean_index, mean in spans: part[row] -= 2 * mean * matrix_linear[offset + length + mean_index]
                matrix.append(part)
                offset += length + len(spans)
            matrix = np.concatenate(matrix, axis=0)
        if matrix.shape != (len(flat), len(values)): raise ValueError("Native Jacobian shape does not match executed outputs.")
        self.metadata.update(gradient_method=method, shifted_evaluation_count=evaluations if method == "parameter-shift" else 0,
                             derivative_evaluation_count=evaluations, derivative_order=1,
                             gradient_semantics="finite-shot estimate" if any(shots is not None for shots in self.shots.partitions) or any(request.shots is not None for request in self.requests) else "analytic")
        if self.resource_history: self.metadata["gradient_resource_evaluations"] = list(self.resource_history)
        return base, matrix, spec
