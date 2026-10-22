# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native unitary definitions, structural expansion and coherent control."""

from numbers import Integral, Real
import fnmatch
import math
from itertools import islice

import numpy as np

from .operations import Instruction, Operation
from .parameters import Parameter, parameter_set, resolve_parameter, _coerce_expression
from .gate_limits import current_gate_limits


def _copy(value):
    from quantumbridge.execution.array_ownership import native_configuration_copy
    from quantumbridge.execution.resource_context import current_resources
    return native_configuration_copy(value, category="native_gate_definition_copy", strict=current_resources() is not None)


def _integer(value, label):
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(label + " must be an integer, not a boolean.")
    return int(value)


def _parameter_values(values):
    limits = current_gate_limits()
    from quantumbridge.execution.resource_context import current_resources
    if current_resources() is not None and type(values) not in (tuple, list, np.ndarray):
        from .classical import UnsupportedFeature
        raise UnsupportedFeature("managed_gate_parameter_container", "Managed Gate parameters require explicit native containers.")
    if isinstance(values, (tuple, list, np.ndarray)):
        limits.check("max_gate_parameters", len(values))
        return tuple(values)
    bounded = tuple(islice(iter(values), limits.max_gate_parameters+1))
    limits.check("max_gate_parameters", len(bounded))
    return bounded


def _validate_primitive_arity(name, params, metadata):
    seen = set()
    while "controlled_base" in metadata:
        if id(metadata) in seen: raise ValueError("Cyclic controlled primitive metadata.")
        seen.add(id(metadata))
        current_gate_limits().check("max_definition_depth", len(seen))
        description = metadata["controlled_base"]
        name, metadata = description["name"], description["metadata"]
    expected = (1 if name in {"rx", "ry", "rz", "phase", "p", "u1", "crx", "cry", "crz", "cp", "cphase", "rxx", "ryy", "rzz", "global_phase"}
                else 2 if name == "u2" else 3 if name in {"u", "u3"} else 0)
    if len(params) != expected: raise ValueError("Primitive gate parameter count does not match its operation.")


def validate_definition(circuit, *, owner=None):
    """Validate a whole definition graph before copying or allocating matrices."""
    from .circuit import Circuit
    from quantumbridge.utils.math import gate_matrix, validate_unitary_matrix
    from quantumbridge.execution.resource_context import current_resources
    if not isinstance(circuit, Circuit): raise TypeError("Gate definitions require a native Circuit.")
    if current_resources() is not None and type(circuit) is not Circuit:
        from .classical import UnsupportedFeature
        raise UnsupportedFeature("managed_gate_definition_type", "Managed Gate definitions require the exact native Circuit type.")
    limits = current_gate_limits()
    if owner is not None:
        if circuit.num_qubits != owner.num_qubits:
            raise ValueError("Gate definition width no longer matches its owner.")
        if not set(circuit.parameters) <= set(parameter_set(owner.params)):
            raise ValueError("Gate definition parameter namespace no longer matches its owner.")
    stack = [(circuit, 0, frozenset(() if owner is None else (id(owner),)))]
    operations = definitions = work = 0
    while stack:
        body, depth, ancestors = stack.pop()
        if not isinstance(body, Circuit): raise TypeError("Gate definitions require a native Circuit.")
        if current_resources() is not None and type(body) is not Circuit:
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("managed_gate_definition_type")
        if id(body) in ancestors: raise ValueError("Cyclic gate definition.")
        ancestors = ancestors | {id(body)}
        limits.check("max_definition_depth", depth)
        definitions += 1
        limits.check("max_custom_definitions", definitions)
        operations += len(body.operations)
        limits.check("max_total_operations", operations)
        if body.num_bits or body.measurements or body.has_dynamic_operations:
            raise ValueError("A Gate definition must be unitary and have no classical bits or measurements.")
        _coerce_expression(body.global_phase)
        if not parameter_set((body.global_phase,)):
            phase = resolve_parameter(body.global_phase, {})
            if not isinstance(phase, Real) or not math.isfinite(phase):
                raise ValueError("A unitary Gate definition requires a finite real global phase.")
        limits.check("max_gate_parameters", len(body.parameters))
        for op in body.operations:
            work += 1
            limits.check("max_decomposition_work", work)
            if op.metadata.get("directive") or op.metadata.get("requires_zero_input"):
                raise ValueError("Directive/state preparation instructions are not unitary Gate definitions.")
            if not op.wires or len(set(op.wires)) != len(op.wires) or any(type(w) is not int or not 0 <= w < body.num_qubits for w in op.wires):
                raise ValueError("Invalid gate definition wire mapping.")
            child = op.metadata.get("gate")
            if child is not None:
                if current_resources() is not None and type(child) not in (Gate, ControlledGate):
                    from .classical import UnsupportedFeature
                    raise UnsupportedFeature("managed_gate_type")
                if not isinstance(child, Gate) or child.num_qubits != len(op.wires):
                    raise ValueError("Invalid native gate node width or type.")
                if id(child) in ancestors: raise ValueError("Cyclic gate definition.")
                if child.definition is not None:
                    stack.append((child.definition, depth+1, ancestors | {id(child)}))
                    continue
            # Symbolic arguments need not be evaluated to check a primitive's
            # arity/unitarity. Numeric custom matrices still receive validation.
            metadata = child.metadata if child is not None else op.metadata
            name = child.name if child is not None else op.name
            params = child.params if child is not None else op.params
            _validate_primitive_arity(name, params, metadata)
            checked = []
            for value in params:
                _coerce_expression(value)
                checked.append(0. if parameter_set((value,)) else resolve_parameter(value, {}))
            matrix = gate_matrix(name, tuple(checked), metadata)
            if matrix.shape != (1 << len(op.wires),) * 2 or not validate_unitary_matrix(matrix):
                raise ValueError("Gate definition contains an invalid unitary primitive.")
    return operations


class Gate(Instruction):
    """A native unitary Instruction with owned, validated circuit structure.

    Parameters are immutable tuples. Explicit reassignment of direct formal
    parameters updates the owned definition atomically; free-form list mutation
    is not the public Qiskit mutable-list ABI.
    """

    def __init__(self, name, num_qubits, params=(), label=None, *, definition=None, metadata=None):
        if isinstance(num_qubits, bool): raise ValueError("A gate width cannot be a boolean.")
        if label is not None and (not isinstance(label, str) or not label): raise ValueError("Invalid gate label.")
        params = _parameter_values(params)
        for value in params: _coerce_expression(value)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "num_qubits", num_qubits)
        object.__setattr__(self, "num_bits", 0)
        object.__setattr__(self, "_params", tuple(params))
        object.__setattr__(self, "metadata", _copy(dict(metadata or {})))
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "_definition", None)
        Instruction.__post_init__(self)
        self.definition = definition

    def __setattr__(self, name, value):
        if name in {"definition", "params"}:
            return object.__setattr__(self, name, value)
        if name in {"name", "label"}:
            if value is not None and (not isinstance(value, str) or not value): raise ValueError("Invalid gate name or label.")
            if name == "name" and value is None: raise ValueError("A Gate needs a name.")
            return object.__setattr__(self, name, value)
        raise AttributeError("Use definition/params assignment or copy to update a native Gate.")

    @property
    def num_clbits(self): return 0

    @property
    def params(self): return self._params

    @params.setter
    def params(self, values):
        values = _parameter_values(values)
        for value in values: _coerce_expression(value)
        parameter_set(values)
        old = getattr(self, "_params", ())
        definition = getattr(self, "_definition", None)
        if definition is not None:
            validate_definition(definition, owner=self)
            if len(old) != len(values) or not all(isinstance(item, Parameter) for item in old):
                raise ValueError("Definition parameter reassignment requires direct formal Parameters and matching arity.")
            definition = definition.assign_parameters(dict(zip(old, values)))
            validate_definition(definition)
            if not set(definition.parameters) <= set(parameter_set(values)):
                raise ValueError("Assigned definition has an inconsistent parameter namespace.")
        object.__setattr__(self, "_params", values)
        object.__setattr__(self, "_definition", definition)

    @property
    def definition(self): return self._definition

    @definition.setter
    def definition(self, value):
        if value is not None:
            validate_definition(value, owner=self)
        object.__setattr__(self, "_definition", _copy(value))

    def copy(self, name=None):
        copied = _copy(self)
        if name is not None: copied.name = name
        return copied

    def is_parameterized(self): return bool(parameter_set(self.params))

    def assign_parameters(self, mapping, *, strict=True):
        from .circuit import _parameter_mapping_from_values
        ordered = tuple(sorted(parameter_set(self.params), key=lambda p: (p.name, p.uuid)))
        values = _parameter_mapping_from_values(ordered, mapping, strict)
        definition = None if self.definition is None else self.definition.assign_parameters(values, strict=False)
        params = tuple(resolve_parameter(value, values, allow_partial=True) for value in self.params)
        return Gate(self.name, self.num_qubits, params, self.label, definition=definition, metadata=self.metadata)

    def to_matrix(self):
        from quantumbridge.utils.math import gate_matrix
        from quantumbridge.information import Operator
        limits = current_gate_limits()
        if self.num_qubits > limits.max_matrix_dimension.bit_length()-1:
            raise MemoryError("Gate matrix exceeds max_matrix_dimension before allocation.")
        if self.is_parameterized(): raise ValueError("Bind gate parameters before requesting a matrix.")
        if self.definition is not None:
            validate_definition(self.definition, owner=self)
            return Operator.from_circuit(self.definition.lowered()).data
        _validate_primitive_arity(self.name, self.params, self.metadata)
        return _copy(gate_matrix(self.name, self.params, self.metadata))

    def inverse(self, annotated=False):
        if annotated:
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("annotated_gate_inverse", "Lazy annotation objects are not implemented yet.")
        from .circuit import Circuit
        body = self.definition if self.definition is not None else Circuit(self.num_qubits).append(self.name, range(self.num_qubits), params=self.params, metadata=self.metadata)
        return body.inverse().to_gate(label=self.label, _name=self.name+"_dg")

    def repeat(self, n):
        from .circuit import Circuit
        n = _integer(n, "Gate repetition count")
        if n < 1: raise ValueError("Gate.repeat requires a strictly positive count.")
        current_gate_limits().check("max_repeat_count", n)
        count = 1 if self.definition is None else validate_definition(self.definition, owner=self)
        current_gate_limits().check("max_total_operations", n*max(1, count))
        body = Circuit(self.num_qubits)
        for _ in range(n): body.append(self, range(self.num_qubits))
        return body.to_gate(_name=self.name+"*"+str(n))

    def power(self, exponent, annotated=False):
        from .circuit import Circuit
        from .classical import UnsupportedFeature
        if annotated: raise UnsupportedFeature("annotated_gate_power")
        if isinstance(exponent, bool) or not isinstance(exponent, Real) or not math.isfinite(exponent):
            raise ValueError("Gate powers require a finite real exponent.")
        if float(exponent).is_integer():
            n = int(exponent)
            if not n: return Circuit(self.num_qubits).to_gate(_name=self.name+"^0")
            base = self.inverse() if n < 0 else self
            return base.repeat(abs(n))
        if self.is_parameterized(): raise UnsupportedFeature("symbolic_fractional_gate_power")
        from quantumbridge.execution.resource_context import current_resources
        if current_resources() is not None: raise UnsupportedFeature("managed_fractional_gate_power", "Spectral solver workspace is not a managed native buffer contract.")
        matrix = self.to_matrix()
        eigenvalues, vectors = np.linalg.eig(matrix)
        if np.linalg.cond(vectors) > 1e8: raise ValueError("Gate spectral basis is ill-conditioned.")
        powered = (vectors * np.exp(1j*float(exponent)*np.angle(eigenvalues))) @ np.linalg.inv(vectors)
        return Circuit(self.num_qubits).unitary(powered, range(self.num_qubits)).to_gate(_name=self.name+"^"+str(exponent))

    def control(self, num_ctrl_qubits=1, label=None, ctrl_state=None, annotated=False):
        if annotated:
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("annotated_gate_control")
        return ControlledGate(self, num_ctrl_qubits, ctrl_state, label)


class ControlledGate(Gate):
    @property
    def params(self): return self._params

    @params.setter
    def params(self, values):
        values = _parameter_values(values)
        base = getattr(self, "base_gate", None)
        updated = None
        if base is not None:
            updated = base.copy()
            updated.params = values
        Gate.params.fset(self, values)
        if updated is not None: object.__setattr__(self, "base_gate", updated)

    def assign_parameters(self, mapping, *, strict=True):
        from .circuit import _parameter_mapping_from_values
        ordered = tuple(sorted(parameter_set(self.params), key=lambda p: (p.name, p.uuid)))
        values = _parameter_mapping_from_values(ordered, mapping, strict)
        result = ControlledGate(self.base_gate.assign_parameters(values, strict=False),
                                self.num_ctrl_qubits, self.ctrl_state, self.label)
        result.name = self.name
        if self.definition is not None:
            result.definition = self.definition.assign_parameters(values, strict=False)
        return result

    def __init__(self, base_gate, num_ctrl_qubits=1, ctrl_state=None, label=None):
        from .circuit import Circuit
        n = _integer(num_ctrl_qubits, "Control width")
        if n < 1: raise ValueError("Control width must be positive.")
        current_gate_limits().check("max_control_qubits", n)
        if isinstance(ctrl_state, str):
            if len(ctrl_state) != n or set(ctrl_state)-{"0", "1"}: raise ValueError("Invalid control bitstring.")
            ctrl_state = int(ctrl_state, 2)
        state = (1 << n)-1 if ctrl_state is None else _integer(ctrl_state, "Control state")
        if not 0 <= state < (1 << n): raise ValueError("Control state is outside its register.")
        if not isinstance(base_gate, Gate): raise TypeError("ControlledGate requires a native Gate.")
        from quantumbridge.execution.resource_context import current_resources
        if current_resources() is not None and type(base_gate) not in (Gate, ControlledGate):
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("managed_gate_type")
        base = base_gate.definition
        if base is None:
            base = Circuit(base_gate.num_qubits).append(base_gate.name, range(base_gate.num_qubits), params=base_gate.params, metadata=base_gate.metadata)
        validate_definition(base)
        base = base.lowered()
        current_gate_limits().check("max_total_operations", len(base.operations)+2*n+1)
        out = Circuit(n+base.num_qubits)
        # ctrl_state uses the public integer convention: bit zero names the
        # first control wire, while native state tensors are wire-major.
        opened = [wire for wire in range(n) if not (state >> wire) & 1]
        for wire in opened: out.x(wire)
        if parameter_set((base.global_phase,)) or base.global_phase != 0:
            _append_controlled(out, "phase", (n-1,), base.global_phase, tuple(range(n-1)), {})
        for op in base.operations:
            _append_controlled(out, op.name, tuple(n+w for w in op.wires), op.params, tuple(range(n)), op.metadata)
        for wire in reversed(opened): out.x(wire)
        name = "c"+base_gate.name if n == 1 else "c"+str(n)+base_gate.name
        if opened: name += "_o"+str(state)
        super().__init__(name, out.num_qubits, base_gate.params, label, definition=out)
        object.__setattr__(self, "base_gate", base_gate.copy())
        object.__setattr__(self, "num_ctrl_qubits", n)
        object.__setattr__(self, "ctrl_state", state)


def _append_controlled(out, name, wires, params, controls, metadata):
    params = params if isinstance(params, tuple) else (params,)
    if not controls:
        out.append(name, wires, params=params, metadata=metadata)
        return
    names = {"x": "cx", "y": "cy", "z": "cz", "h": "ch", "sx": "csx", "sxdg": "csxdg",
             "rx": "crx", "ry": "cry", "rz": "crz", "p": "cp", "phase": "cp", "u1": "cp"}
    if len(controls) == 1 and len(wires) == 1 and name in names:
        out.append(names[name], wires, controls=controls, params=params)
    else:
        width = len(controls)+len(wires)
        if width > current_gate_limits().max_matrix_dimension.bit_length()-1:
            raise MemoryError("Controlled primitive matrix exceeds max_matrix_dimension.")
        out.append("native_controlled", wires, controls=controls, params=params,
                   metadata={"controlled_base": {"name": name, "metadata": _copy(metadata), "controls": len(controls)}})


def decompose(circuit, selected=None, reps=1, *, _work=None):
    from .circuit import Circuit, _remap_operation
    from .measurements import Measurement
    from quantumbridge.compiler.traversal import append_item
    reps = _integer(reps, "Decomposition repetitions")
    limits = current_gate_limits()
    limits.check("max_decomposition_work", max(0, reps))
    names = None if selected is None else (selected,) if isinstance(selected, (str, type)) else tuple(selected)
    def matches(gate):
        return names is None or any(isinstance(gate, value) if isinstance(value, type) else
            any(fnmatch.fnmatchcase(text, value) for text in (gate.name, gate.label) if text is not None) for value in names)
    limits.check("max_total_operations", len(circuit.operations))
    result = circuit.copy()
    work = [0] if _work is None else _work
    for _ in range(max(0, reps)):
        predicted = 0
        for item in result.operations:
            gate = item.metadata.get("gate")
            predicted += len(gate.definition.operations) if gate is not None and gate.definition is not None and matches(gate) else 1
        limits.check("max_total_operations", predicted)
        out = Circuit(result.num_qubits, result.num_bits, result.name, _copy(result.metadata))
        changed = False
        for item in result.iter_instructions():
            work[0] += 1
            limits.check("max_decomposition_work", work[0])
            gate = None if isinstance(item, Measurement) else item.metadata.get("gate")
            if gate is None or gate.definition is None or not matches(gate):
                append_item(out, item)
                continue
            validate_definition(gate.definition, owner=gate)
            limits.check("max_total_operations", len(out.operations)+len(gate.definition.operations))
            extra = {key: value for key, value in item.metadata.items() if key not in {"gate", "label"}}
            if any(key in extra for key in ("condition", "gate_condition", "control_flow_stack")) and (
                    parameter_set((gate.definition.global_phase,)) or gate.definition.global_phase != 0):
                from .classical import UnsupportedFeature
                raise UnsupportedFeature("conditional_gate_phase", "Conditional definition phase needs a scoped execution node.")
            out.global_phase = out.global_phase + gate.definition.global_phase
            mapping = dict(enumerate(item.wires))
            for child in gate.definition.operations:
                mapped = _remap_operation(child, mapping, {}, out.num_qubits, out.num_bits)
                mapped.metadata.update(_copy(extra))
                out.operations.append(mapped)
            changed = True
        limits.check("max_total_operations", len(out.operations))
        result = out
        if not changed: break
    return result


def lower(circuit, *, _ancestors=(), _work=None):
    if id(circuit) in _ancestors: raise ValueError("Cyclic circuit/control definition.")
    current_gate_limits().check("max_definition_depth", len(_ancestors))
    work = [0] if _work is None else _work
    if any("control_node" in op.metadata for op in circuit.operations):
        from .control_flow import ControlBlock
        ancestors = (*_ancestors, id(circuit))
        transformed = []
        changed = False
        for op in circuit.operations:
            node = op.metadata.get("control_node")
            if node is None:
                transformed.append(op)
                continue
            replacements = {id(body): lower(body, _ancestors=ancestors, _work=work) for body in node.bodies}
            if all(replacements[id(body)] is body for body in node.bodies): transformed.append(op)
            else:
                data = dict(node.data)
                for field in ("body", "alternate", "default"):
                    if data.get(field) is not None: data[field] = replacements[id(data[field])]
                if "cases" in data:
                    data["cases"] = tuple((values, replacements[id(body)]) for values, body in data["cases"])
                transformed.append(Operation(op.name, op.targets, op.controls, op.params,
                    {**_copy(op.metadata), "control_node": ControlBlock(node.kind, data)}))
                changed = True
        if changed:
            circuit = circuit.copy()
            circuit.operations = transformed
    if not any("gate" in op.metadata for op in circuit.operations): return circuit
    result = circuit
    limits = current_gate_limits()
    # Definitions are acyclic and depth bounded before entering expansion.
    for op in circuit.operations:
        if "gate" in op.metadata and op.metadata["gate"].definition is not None:
            validate_definition(op.metadata["gate"].definition, owner=op.metadata["gate"])
    result = decompose(result, reps=limits.max_definition_depth+1, _work=work)
    if any("gate" in op.metadata for op in result.operations):
        from .classical import UnsupportedFeature
        raise UnsupportedFeature("opaque_gate_definition", "An opaque Gate needs an executable definition.")
    return result
