# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from math import pi

import numpy as np

from quantumbridge import Circuit, GradientDescentOptimizer, NumPyEigensolver, PauliZ, estimate_amplitude, estimate_phase
from quantumbridge.algorithms import eigensolver_result
from quantumbridge.utils.math import gate_matrix


def test_exact_amplitude_estimation_marks_good_state_probability():
    result = estimate_amplitude(Circuit(1).h(0), good_states=["1"])

    assert abs(result.good_probability - 0.5) < 1e-12
    assert abs(result.amplitude - np.sqrt(0.5)) < 1e-12
    assert result.to_result().metadata()["algorithm"] == "AmplitudeEstimation"


def test_exact_phase_estimation_returns_qiskit_style_cycle_phase():
    state_one = np.array([0.0, 1.0], dtype=complex)

    result = estimate_phase(gate_matrix("phase", (pi / 2,)), state=state_one, precision_bits=6)

    assert abs(result.phase - 0.25) < 1e-12
    assert result.overlap > 0.999
    assert result.to_result().metadata()["algorithm"] == "PhaseEstimation"


def test_numpy_eigensolver_computes_ordered_eigenpairs_for_pauli_z():
    result = NumPyEigensolver(k=1).compute_eigenvalues(PauliZ(0))

    assert result.eigenvalues.shape == (1,)
    assert abs(result.eigenvalue + 1.0) < 1e-12
    assert result.eigenstate.shape == (2,)
    assert eigensolver_result([[1, 0], [0, -1]], k=2).to_dict()["algorithm"] == "NumPyEigensolver"


def test_gradient_descent_optimizer_minimize_with_native_result():
    optimizer = GradientDescentOptimizer(learning_rate=0.2, steps=80, tolerance=1e-10)

    result = optimizer.minimize(lambda x: float((x[0] - 2.0) ** 2), x0=[0.0])

    assert abs(result.x[0] - 2.0) < 1e-3
    assert result.fun < 1e-6
    assert result.to_dict()["nfev"] >= 1
