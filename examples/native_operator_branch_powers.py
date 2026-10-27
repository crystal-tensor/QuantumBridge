# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""SDK-free exact Jordan powers and real complex state/density evolution."""

import cmath
import json
import math

import numpy as np

from quantumbridge.information import DensityMatrix, Operator, Statevector


def main():
    nilpotent = .125*np.array([[1, 1], [-1, -1]], dtype=complex)
    source = -np.eye(2)+nilpotent
    point = np.array([1, 1j])/math.sqrt(2)
    density = np.outer(point, point.conj())
    errors = []
    for exponent in (.5, .3, -.3):
        for cut in (math.pi*1e-12, -math.pi*1e-12):
            log_value = 1j*(cmath.phase(-cmath.exp(-1j*cut))+cut)
            expected = cmath.exp(exponent*log_value)*(np.eye(2)-exponent*nilpotent)
            powered = Operator(source).power(exponent, branch_cut_rotation=cut)
            actual_state = Statevector(point).evolve(powered).data
            actual_density = DensityMatrix(density).evolve(powered).data
            np.testing.assert_allclose(powered.data, expected, atol=3e-12, rtol=3e-13)
            np.testing.assert_allclose(actual_state, expected@point, atol=3e-12, rtol=3e-13)
            np.testing.assert_allclose(actual_density, expected@density@expected.conj().T, atol=3e-12, rtol=3e-13)
            errors.append(float(np.max(abs(powered.data-expected))))
    print(json.dumps({"native_matrix_state_density_cases": len(errors), "maximum_matrix_error": max(errors),
                      "sdk_executor_used": False, "hardware_tasks": 0, "full_sdk_parity": False}))


if __name__ == "__main__":
    main()
