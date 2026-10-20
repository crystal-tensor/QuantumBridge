# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import pytest


def test_real_jax_mps_100_wires_forbids_dense_expansion():
    pytest.importorskip("jax")
    from examples.native_jax_mps_100qubits import main
    result = main()
    assert result["logical_wires"] == 100
    assert result["peak_bond"] == 2
    assert result["tensor_bytes"] < 2 * 1024 * 1024
    assert result["shifted_evaluations"] == 2 and result["transform_count"] == 2
    assert result["physical_shots"] == 0


def test_real_jax_qchem_optimization_builds_fixed_geometry_once(monkeypatch):
    pytest.importorskip("jax")
    from quantumbridge import qchem
    from examples.native_jax_qchem_h2 import main
    original = qchem.molecular_hamiltonian_native
    calls = []
    def build(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(qchem, "molecular_hamiltonian_native", build)
    result = main()
    assert len(calls) == 1
    assert result["final_energy"] < result["initial_energy"]


def test_real_jax_transformed_optimizer_executes_native_qwc_training():
    pytest.importorskip("jax")
    from examples.native_jax_transform_training import main
    result = main()
    assert result["native_postprocessing_derivative"] and result["qwc_children"] == 2


def test_real_jax_nonlinear_preprocessing_example():
    pytest.importorskip("jax")
    from examples.native_jax_qnode_gradient import main
    result = main()
    assert result["method"] == "parameter-shift"
