# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import pytest


def test_actual_tensorflow_gradient_example():
    pytest.importorskip("tensorflow")
    from examples.native_tensorflow_qnode_gradient import main
    assert main()["method"] == "parameter-shift"


def test_actual_tensorflow_twenty_update_transform_training():
    pytest.importorskip("tensorflow")
    from examples.native_tensorflow_transform_training import main
    receipt = main()
    assert receipt["updates"] == len(receipt["trace"]) == 20
    assert receipt["qwc_children"] == 2 and receipt["native_postprocessing_derivative"]


def test_actual_tensorflow_100_qubit_mps_without_dense_conversion():
    pytest.importorskip("tensorflow")
    from examples.native_tensorflow_mps_100qubits import main
    result = main()
    assert result["logical_wires"] == 100 and result["peak_bond"] == 2
    assert result["tensor_bytes"] < 2*1024*1024
    assert result["shifted_evaluations"] == 2 and result["transform_count"] == 2
    assert result["discarded_weight"] == result["truncations"] == result["physical_shots"] == 0


def test_actual_tensorflow_geometry_h2_uses_one_scf_build(monkeypatch):
    pytest.importorskip("tensorflow")
    from quantumbridge import qchem
    from examples.native_tensorflow_qchem_h2 import main
    original, calls = qchem.molecular_hamiltonian_native, []
    def build(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(qchem, "molecular_hamiltonian_native", build)
    result = main()
    assert len(calls) == 1 and result["updates"] == 4
    assert result["final_energy"] < result["initial_energy"]-.01
