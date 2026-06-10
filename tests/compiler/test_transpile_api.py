# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

from quantumbridge import Circuit, transpile
from quantumbridge.compiler import CouplingMap, Target, generate_preset_pass_manager, pass_manager_config_from_options


def test_transpile_decomposes_to_requested_basis_and_returns_report():
    circuit = Circuit(1).phase(0.25, 0)

    out, report = transpile(circuit, basis_gates=("rz",), optimization_level=0, return_report=True)

    assert [op.name for op in out.operations] == ["rz"]
    assert out.metadata["transpile"]["basis_gates"] == ["rz"]
    assert out.metadata["transpile"]["changed"] is True
    assert report["changed"] is True


def test_transpile_optimization_level_runs_native_optimization_pipeline():
    circuit = Circuit(1).id(0).x(0).x(0).ry(0.1, 0).ry(0.2, 0)

    out = transpile(circuit, optimization_level=2)

    assert [op.name for op in out.operations] == ["ry"]
    assert abs(out.operations[0].params[0] - 0.3) < 1e-12
    assert out.metadata["transpile"]["optimization_level"] == 2


def test_transpile_routing_records_coupling_diagnostics_and_swaps():
    circuit = Circuit(3).cx(0, 2)

    out, report = transpile(circuit, coupling_map=CouplingMap([(0, 1), (1, 2)]), optimization_level=1, return_report=True)

    assert out.operations[0].name == "swap"
    assert out.metadata["transpile"]["analyses"]["routing_required"] is True
    assert out.metadata["transpile"]["analyses"]["inserted_swaps"] == 1
    assert report["analyses"]["inserted_swaps"] == 1


def test_transpile_accepts_target_and_sequences():
    target = Target(num_qubits=2, basis_gates=("x", "cx"), coupling_map=[(0, 1)])
    circuits = [Circuit(1).x(0), Circuit(2).cx(0, 1)]

    out = transpile(circuits, target=target, optimization_level=1)

    assert [item.metadata["transpile"]["basis_gates"] for item in out] == [["x", "cx"], ["x", "cx"]]
    assert target.supports_operation("cx")
    assert target.is_connected(0, 1)


def test_generate_preset_pass_manager_and_config_from_options():
    manager = generate_preset_pass_manager(optimization_level=3, basis_gates=("x", "h"))
    config = pass_manager_config_from_options(basis_gates=("x",), optimization_level=2)

    assert manager.metadata["optimization_level"] == 3
    assert manager.metadata["basis_gates"] == ["x", "h"]
    assert config.basis_gates == ("x",)
    assert config.optimization_level == 2
