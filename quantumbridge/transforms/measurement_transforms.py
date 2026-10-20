# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def measurement_count(circuit) -> int:
    return len(circuit.measurements)


def split_hamiltonian(tape):
    """Internal expval-to-term-Tapes prototype, not split_to_single_terms parity.

    Identity and duplicate nonzero terms execute independently. Zero terms are
    validated then omitted. Coefficients are static, finite and real. Shot
    partitions are per child, not a total-shot allocation or QWC grouping.
    """
    import numpy as np
    from dataclasses import replace
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.diff.qnode_engine import map_measurements
    from quantumbridge.qml.shot_vector import ShotSpec
    from quantumbridge.utils.math import Hamiltonian, PauliString
    from .program import TransformLimits, check_batch, output_tree

    limits = TransformLimits()
    check_batch((tape,), limits)
    children, slots = [], []
    tree = output_tree(tape)

    def expand(request):
        if request.kind != "expval":
            raise UnsupportedFeature("hamiltonian_split_measurement", "B1 Hamiltonian splitting supports expval only.")
        observable = request.observable
        if hasattr(observable, "to_quantumbridge"):
            observable = observable.to_quantumbridge()
        elif hasattr(observable, "to_hamiltonian"):
            observable = observable.to_hamiltonian()
        if isinstance(observable, PauliString):
            terms = ((1., observable),)
        elif isinstance(observable, Hamiltonian):
            terms = observable.terms
        else:
            raise UnsupportedFeature("hamiltonian_split_observable", "B1 splitting requires native Pauli/Hamiltonian form.")
        limits.check("max_expansion_steps", len(terms))
        positions = []
        for coefficient, pauli in terms:
            if not np.isfinite(coefficient) or np.iscomplexobj(coefficient):
                raise ValueError("Splitting requires finite real static coefficients.")
            wires = [wire for wire, _ in pauli.terms]
            if len(set(wires)) != len(wires) or any(wire < 0 or wire >= tape.circuit.num_qubits for wire in wires):
                raise ValueError("Split Pauli terms require unique in-register wires.")
            if coefficient == 0:
                continue
            limits.check("max_tapes", len(children) + 1)
            child = tape.copy()
            terminal = replace(request, observable=pauli)
            child.measurements, child.output_tree = [terminal], terminal
            child.observable, child.measurement = pauli, "expval"
            positions.append((len(children), coefficient))
            children.append(child)
        slots.append(tuple(positions))
        return request

    map_measurements(tree, expand)
    check_batch(children, limits)

    def one_partition(values):
        values_by_request = iter(sum(coefficient * values[index] for index, coefficient in positions)
                                 for positions in slots)
        return map_measurements(tree, lambda _: next(values_by_request))

    def process(results):
        if len(results) != len(children):
            raise ValueError("Hamiltonian split result count mismatch.")
        spec = ShotSpec.parse(tape.shots)
        if spec.is_vector:
            if any(not isinstance(result, tuple) or len(result) != len(spec.partitions) for result in results):
                raise ValueError("Hamiltonian split shot partition count mismatch.")
            return tuple(one_partition(tuple(result[index] for result in results)) for index in range(len(spec.partitions)))
        return one_partition(results)

    return tuple(children), process

