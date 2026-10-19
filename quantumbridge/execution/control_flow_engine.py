# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent structured interpreter over native quantum-state representations.

from copy import deepcopy
from dataclasses import dataclass, field
import numpy as np

from quantumbridge.core import Circuit, Measurement
from quantumbridge.core.classical import ClassicalStore, classical_eval, classical_assign, ClassicalExecutionError, UnsupportedFeature
from quantumbridge.core.control_flow import ExecutionLimits, validate_control_flow
from quantumbridge.core.parameters import resolve_parameter
from quantumbridge.devices.execution import prepare_program, condition_enabled, readout_probability
from quantumbridge.results import Result
from quantumbridge.utils.math import apply_unitary, apply_density_channel, gate_matrix, validate_kraus_operators


@dataclass
class Branch:
    state: object
    store: ClassicalStore
    weight: float = 1.0
    decisions: dict = field(default_factory=dict)
    signal: str = ""
    steps: int = 0
    iterations: int = 0

    def child(self, state, probability=1.0):
        return Branch(state, self.store.copy(), self.weight * probability, self.decisions.copy(), self.signal, self.steps, self.iterations)


class ExecutionRecords(list):
    pass


class QuantumStateAdapter:
    def __init__(self, device, width):
        self.device, self.width = device, width
        self.kind = getattr(device, "simulation", "statevector")

    def initial(self):
        if hasattr(self.device, "_initial"): return self.device._initial(self.width)
        raise UnsupportedFeature("dynamic_device", "QuantumBridge device lacks a native dynamic state protocol.")

    def gate(self, state, matrix, wires):
        if self.kind == "matrix_product_state": return state.apply(matrix, wires)
        if self.kind == "exact_density_matrix": return self.device._apply(state, "gate", matrix, wires, self.width)
        if self.kind == "exact_stabilizer":
            from quantumbridge.information import Clifford
            try: Clifford.from_matrix(matrix)
            except ValueError as exc: raise UnsupportedFeature("non_clifford_tableau", "QuantumBridge tableau execution requires Clifford gates.") from exc
            state.clifford._append_matrix(matrix, tuple(self.width - 1 - wire for wire in reversed(wires)))
            return state
        return apply_unitary(state, matrix, tuple(wires), self.width)

    def project(self, state, wire):
        results = []
        for outcome in (0, 1):
            if self.kind == "exact_density_matrix":
                child, probability = self.device._project(state, wire, outcome, self.width)
            elif self.kind == "matrix_product_state":
                child = state.copy()
                probability = child.project(wire, outcome)
            elif self.kind == "exact_stabilizer":
                child = state.copy()
                _, probability = child._measure_z(self.width - 1 - wire, forced=outcome)
            else:
                mask = ((np.arange(1 << self.width) >> (self.width - 1 - wire)) & 1) == outcome
                child = state * mask
                probability = float(np.vdot(child, child).real)
                if probability: child = child / np.sqrt(probability)
            if probability > 0: results.append((probability, child, outcome))
        return results

    def channel(self, state, operators, wires):
        if self.kind == "exact_density_matrix":
            return [(1.0, apply_density_channel(state, operators, wires, self.width))]
        results = []
        for operator in operators:
            if self.kind == "matrix_product_state":
                rho = state.reduced_density_matrix(wires)
                probability = float(np.trace(operator @ rho @ operator.conj().T).real)
                if probability > 0: results.append((probability, state.copy().apply(operator, wires)))
            elif self.kind == "exact_stabilizer":
                dimension = operator.shape[0]
                probability = float(np.trace(operator.conj().T @ operator).real / dimension)
                if probability <= 0: continue
                unitary = operator / np.sqrt(probability)
                if not np.allclose(unitary.conj().T @ unitary, np.eye(dimension), atol=1e-10, rtol=0):
                    raise UnsupportedFeature("tableau_kraus", "QuantumBridge tableau supports unitary Clifford mixtures, not arbitrary selective Kraus maps.")
                results.append((probability, self.gate(state.copy(), unitary, wires)))
            else:
                child = apply_unitary(state, operator, tuple(wires), self.width)
                probability = float(np.vdot(child, child).real)
                if probability > 0: results.append((probability, child / np.sqrt(probability)))
        return results

    def sample(self, state, rng):
        label = []
        for wire in range(self.width):
            choices = self.project(state, wire)
            weights = np.asarray([p for p, _, _ in choices])
            _, state, outcome = choices[int(rng.choice(len(choices), p=weights / weights.sum()))]
            p = readout_probability(getattr(self.device, "noise_model", None), wire, outcome)
            label.append(str(outcome ^ int(p > 0 and rng.random() < p)))
        return "".join(label)


class DynamicExecutionEngine:
    def __init__(self, device, circuit, parameters=None, limits=None):
        if not isinstance(circuit, Circuit): raise TypeError("QuantumBridge execution requires a native Circuit.")
        self.device = device
        self.circuit = circuit.bind(parameters) if parameters else circuit
        configured = limits or getattr(device, "execution_limits", None)
        self.limits = configured or ExecutionLimits(max_branches=getattr(device, "max_branches", 4096))
        if not isinstance(self.limits, ExecutionLimits): raise TypeError("QuantumBridge execution_limits requires ExecutionLimits.")
        if getattr(device, "max_qubits", None) is not None and circuit.num_qubits > device.max_qubits: raise ValueError("Circuit exceeds device qubit limit.")
        validate_control_flow(self.circuit, limits=self.limits)
        self.adapter = QuantumStateAdapter(device, circuit.num_qubits)
        self.noise_model = getattr(device, "noise_model", None)
        self.noise = []
        if self.noise_model is not None:
            if self.adapter.kind == "exact_stabilizer":
                for _, choices, wires, _ in device._noise_instructions(circuit.num_qubits):
                    self.noise.append(("channel", tuple(np.sqrt(p) * matrix for p, matrix in choices), tuple(circuit.num_qubits - 1 - wire for wire in reversed(wires)), {}))
            else:
                _, self.noise = prepare_program(Circuit(circuit.num_qubits, circuit.num_bits), noise_model=self.noise_model)

    def _program(self, circuit, top=False):
        result, inserted = [], False
        from quantumbridge.core import Operation
        from numbers import Real
        phase = circuit.global_phase
        if not isinstance(phase, Real) or phase != 0:
            result.append(Operation("global_phase", (0,), params=(phase,)))
        for item in circuit.iter_instructions():
            if top and isinstance(item, Measurement) and item.metadata.get("operation_index", len(circuit.operations)) == len(circuit.operations) and not inserted:
                result.extend(self.noise)
                inserted = True
            result.append(item)
        if top and not inserted: result.extend(self.noise)
        return result

    def _tick(self, branch):
        branch.steps += 1
        if branch.steps > self.limits.max_instruction_executions:
            raise ClassicalExecutionError("max_instruction_executions", "QuantumBridge dynamic instruction budget exhausted.")

    def _cap(self, branches):
        if len(branches) > self.limits.max_branches:
            raise ClassicalExecutionError("max_branches", "QuantumBridge analytic branches exceed max_branches; use finite-shot execution.")
        if branches and self.adapter.kind == "matrix_product_state":
            branches[0].state._guard(sum(tensor.size for branch in branches for tensor in branch.state._tensors) * 3)
        if branches and self.adapter.kind == "exact_density_matrix": self.device._check_memory(self.circuit.num_qubits, len(branches))
        if branches and self.adapter.kind == "statevector":
            limit = getattr(self.device, "max_memory_mb", None)
            if limit is not None and sum(branch.state.nbytes for branch in branches) * 8 > limit * 1024 ** 2:
                raise MemoryError("QuantumBridge dynamic statevector branches exceed max_memory_mb.")
        return branches

    @staticmethod
    def _choose(choices, rng):
        if rng is None: return choices
        weights = np.asarray([choice[0] for choice in choices], float)
        selected = choices[int(rng.choice(len(choices), p=weights / weights.sum()))]
        return [(1.0, *selected[1:])]

    def _quantum(self, branch, kind, value, wires, rng):
        if kind == "gate":
            branch.state = self.adapter.gate(branch.state, value, wires)
            return [branch]
        if kind == "channel":
            return [branch.child(state, p) for p, state in self._choose(self.adapter.channel(branch.state, value, wires), rng)]
        children = []
        for probability, state, outcome in self._choose(self.adapter.project(branch.state, value), rng):
            if kind == "reset":
                if outcome: state = self.adapter.gate(state, gate_matrix("x"), (value,))
                children.append(branch.child(state, probability))
                continue
            readout = readout_probability(self.noise_model, value, outcome)
            flips = self._choose([(1 - readout, 0), (readout, 1)], rng)
            for factor, flip in flips:
                if factor:
                    child = branch.child(state.copy(), probability * factor)
                    child.store.bits[wires] = outcome ^ flip
                    children.append(child)
        return children

    def _leaf(self, item, branch, rng, binding):
        if isinstance(item, tuple): return self._quantum(branch, *item[:3], rng)
        if not condition_enabled(item.metadata, branch.store.bits, branch.decisions): return [branch]
        if isinstance(item, Measurement): return self._quantum(branch, "measure", item.wire, item.bit, rng)
        if item.metadata.get("directive") and item.name in {"barrier", "delay"}: return [branch]
        if item.name == "reset": return self._quantum(branch, "reset", item.targets[0], None, rng)
        if item.name == "kraus":
            operators = validate_kraus_operators(item.metadata.get("kraus", ()), 1 << len(item.wires))
            return self._quantum(branch, "channel", operators, item.wires, rng)
        parameters = tuple(resolve_parameter(p, binding) for p in item.params)
        try: matrix = gate_matrix(item.name, parameters, item.metadata)
        except ValueError as exc: raise UnsupportedFeature("quantum_operation", str(exc)) from exc
        dimension = 1 << len(item.wires)
        if matrix.shape != (dimension, dimension) or not np.all(np.isfinite(matrix)) or not np.allclose(matrix.conj().T @ matrix, np.eye(dimension), atol=1e-10, rtol=0):
            raise ValueError("QuantumBridge dynamic gate must be a finite unitary matching its wires.")
        return self._quantum(branch, "gate", matrix, item.wires, rng)

    def _body(self, body, branches, rng, depth, binding):
        if body is None: return branches
        existing = [set(branch.store.types) for branch in branches]
        if not branches: return []
        # Every branch has the same lexical declarations on block entry.
        keep = existing[0]
        result = self._walk(self._program(body), branches, rng, depth + 1, binding)
        for branch in result:
            for key in set(branch.store.types) - keep:
                branch.store.types.pop(key)
                branch.store.values.pop(key, None)
                branch.store.names.pop(key, None)
        return result

    def _node(self, node, branch, rng, depth, binding):
        data, kind = node.data, node.kind
        if kind == "declare": branch.store.declare(data["target"], data["initial"])
        elif kind == "store": classical_assign(branch.store, data["target"], data["value"])
        elif kind in {"break", "continue"}: branch.signal = kind
        elif kind == "if":
            selected = data["body"] if classical_eval(data["condition"], branch.store) else data["alternate"]
            return self._body(selected, [branch], rng, depth, binding)
        elif kind == "switch":
            value = classical_eval(data["selector"], branch.store)
            selected = next((body for values, body in data["cases"] if value in values), data["default"])
            return self._body(selected, [branch], rng, depth, binding)
        elif kind in {"for", "while"}:
            active, finished, iteration = [branch], [], 0
            variable = data.get("variable")
            saved = None if variable is None else (variable.value[0], branch.store.types.get(variable.value[0]), branch.store.values.get(variable.value[0]), branch.store.names.get(variable.value[0]))
            if variable is not None and variable.value[0] not in branch.store.types: branch.store.declare(variable)
            while active:
                entering = []
                for current in active:
                    self._tick(current)
                    done = iteration >= len(data["values"]) if kind == "for" else not classical_eval(data["condition"], current.store)
                    if done: finished.append(current)
                    else: entering.append(current)
                if not entering: break
                if iteration >= self.limits.max_loop_iterations:
                    raise ClassicalExecutionError("max_loop_iterations", "QuantumBridge loop exceeds max_loop_iterations.")
                local = dict(binding)
                if kind == "for":
                    value = data["values"][iteration]
                    if data["parameter"] is not None: local[data["parameter"]] = value
                    if variable is not None:
                        for current in entering: classical_assign(current.store, variable, value)
                for current in entering: current.iterations += 1
                after = self._body(data["body"], entering, rng, depth, local)
                active = []
                for current in after:
                    if current.signal == "break":
                        current.signal = ""
                        finished.append(current)
                    else:
                        current.signal = ""
                        active.append(current)
                iteration += 1
                self._cap(active + finished)
            if saved is not None:
                key, dtype, value, name = saved
                for current in finished:
                    if dtype is None:
                        current.store.types.pop(key, None); current.store.values.pop(key, None); current.store.names.pop(key, None)
                    else:
                        current.store.types[key], current.store.names[key] = dtype, name
                        if value is None: current.store.values.pop(key, None)
                        else: current.store.values[key] = value
            return finished
        return [branch]

    def _walk(self, items, branches, rng, depth=0, binding=None):
        if depth > self.limits.max_control_depth: raise ClassicalExecutionError("max_control_depth", "QuantumBridge control depth exhausted.")
        for item in items:
            updated = []
            for branch in branches:
                if branch.signal: updated.append(branch); continue
                self._tick(branch)
                node = None if isinstance(item, (tuple, Measurement)) else item.metadata.get("control_node")
                if node is not None:
                    if condition_enabled(item.metadata, branch.store.bits, branch.decisions): updated.extend(self._node(node, branch, rng, depth, binding or {}))
                    else: updated.append(branch)
                else: updated.extend(self._leaf(item, branch, rng, binding or {}))
                self._cap(updated)
            branches = updated
        return branches

    def branches(self):
        result = self._walk(self._program(self.circuit, top=True), [Branch(self.adapter.initial(), ClassicalStore(self.circuit.num_bits))], None)
        records = ExecutionRecords((branch.state, branch.store.bits, branch.decisions, branch.weight) for branch in result)
        records.metadata = {"dynamic_control_flow": True, "max_instruction_executions_observed": max(branch.steps for branch in result),
            "execution_limits": dict(self.limits.__dict__),
            "classical_ensemble": [{"weight": branch.weight, **branch.store.to_dict()} for branch in result]}
        return records

    def trajectories(self, shots, seed=None):
        if isinstance(shots, bool) or not isinstance(shots, (int, np.integer)) or not 0 <= shots <= self.limits.max_shots:
            raise ValueError("QuantumBridge dynamic shots exceed max_shots or are invalid.")
        rng = np.random.default_rng(seed)
        for _ in range(shots):
            result = self._walk(self._program(self.circuit, top=True), [Branch(self.adapter.initial(), ClassicalStore(self.circuit.num_bits))], rng)
            yield result[0].state, result[0].store.bits, rng

    def quantum_samples(self, wires, shots, seed=None):
        from quantumbridge.devices.execution import validate_wires
        selected = validate_wires(wires, self.circuit.num_qubits)
        samples = []
        for state, _, rng in self.trajectories(shots, seed):
            label = []
            for wire in selected:
                choices = self._choose(self.adapter.project(state, wire), rng)
                _, state, outcome = choices[0]
                p = readout_probability(self.noise_model, wire, outcome)
                label.append(str(outcome ^ int(p > 0 and rng.random() < p)))
            samples.append("".join(label))
        return samples

    def shots(self, shots, seed=None, memory=False):
        if isinstance(shots, bool) or not isinstance(shots, (int, np.integer)) or not 0 < shots <= self.limits.max_shots:
            raise ValueError("QuantumBridge dynamic shots must be positive and within max_shots.")
        rng, samples, stores, peak, discarded, steps, loops = np.random.default_rng(seed), [], [], 1, 0.0, 0, 0
        bond_profile = [1] * max(0, self.circuit.num_qubits - 1)
        for _ in range(shots):
            branches = self._walk(self._program(self.circuit, top=True), [Branch(self.adapter.initial(), ClassicalStore(self.circuit.num_bits))], rng)
            branch = branches[0]
            if self.adapter.kind == "matrix_product_state":
                bond_profile = [max(old, current) for old, current in zip(bond_profile, branch.state.bond_dimensions)]
            label = "".join(map(str, branch.store.bits)) if self.circuit.has_measurements else self.adapter.sample(branch.state, rng)
            samples.append(label)
            if memory: stores.append(branch.store.to_dict())
            steps, loops = max(steps, branch.steps), max(loops, branch.iterations)
            if self.adapter.kind == "matrix_product_state":
                peak, discarded = max(peak, branch.state.peak_bond_dimension), max(discarded, branch.state.discarded_weight)
        counts = {}
        for label in samples: counts[label] = counts.get(label, 0) + 1
        metadata = {"device": type(self.device).__name__, "simulation": self.adapter.kind, "dynamic_control_flow": True,
            "execution_limits": dict(self.limits.__dict__),
            "shots": int(shots), "seed": seed, "num_bits": self.circuit.num_bits if self.circuit.has_measurements else self.circuit.num_qubits,
            "max_instruction_executions_observed": steps, "max_loop_iterations_observed": loops,
            "qubit_order": "q0-first bitstrings", "classical_order": "c0-first bitstrings"}
        if self.adapter.kind == "matrix_product_state": metadata.update(max_bond_observed=peak, max_discarded_weight=discarded,
            max_bond_dimensions_observed=bond_profile, **self.device.state_options)
        if memory: metadata.update(memory=samples, classical_memory=stores)
        return Result(counts_data=counts, probabilities_data={key: count / shots for key, count in counts.items()}, metadata_data=metadata)


def dynamic_branches(device, circuit, parameters=None):
    return DynamicExecutionEngine(device, circuit, parameters).branches()


def dynamic_shots(device, circuit, shots, seed=None, parameters=None, memory=False):
    return DynamicExecutionEngine(device, circuit, parameters).shots(shots, seed, memory)
