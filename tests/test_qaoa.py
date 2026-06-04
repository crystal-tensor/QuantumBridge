# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from quantumbridge import StatevectorDevice, maxcut_hamiltonian, qaoa_circuit, run_qaoa


def test_simple_qaoa_improves_two_node_maxcut_value():
    edges = [(0, 1)]
    device = StatevectorDevice()
    initial_params = [0.1, 0.1]
    hamiltonian = maxcut_hamiltonian(edges)
    initial_value = device.expectation(qaoa_circuit(2, edges, 1, initial_params), hamiltonian)
    result = run_qaoa(edges, depth=1, initial_parameters=initial_params, device=device, steps=25, step_size=0.3)
    assert result.metadata()["final_value"] > initial_value
    assert result.metadata()["final_value"] > 0.7

