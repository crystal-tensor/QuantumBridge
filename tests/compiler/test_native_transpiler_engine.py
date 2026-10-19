# Independent native compiler invariants and mathematical oracles.
from dataclasses import replace
import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice, PauliZ, Hamiltonian
from quantumbridge.core import Operation
from quantumbridge.core.classical import UnsupportedFeature, bit, UInt
from quantumbridge.compiler import (native_transpile, circuit_to_dag, dag_to_circuit, DAGCircuit,
    CouplingMap, Target, Layout, InstructionProperties, CompilationLimits, SchedulingPass,
    PassManager, AnalysisPass, TransformationPass, PassResult, StagedPassManager)
from quantumbridge.compiler.decomposition import GateDecompositionPass
from quantumbridge.compiler.optimization import CircuitOptimizationPass
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir import IRProgram
from quantumbridge.qml import QNode

BASIS = ("rz", "sx", "x", "cx")
TEACHING = ("rx", "ry", "rz", "cx")


def equivalent(a, b):
    np.testing.assert_allclose(Operator.from_circuit(a).data, Operator.from_circuit(b).data, atol=2e-12)


@pytest.mark.parametrize("name", ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "sx", "sxdg", "rx", "ry", "rz", "phase", "u", "u2", "u3", "cx", "cz", "swap", "crx", "cry", "crz", "cp", "rxx", "ryy", "rzz"])
@pytest.mark.parametrize("basis", [BASIS, TEACHING])
def test_algebraic_translation_preserves_full_operator_not_just_probability(name, basis):
    circuit = Circuit(2)
    if name in {"rx", "ry", "rz", "phase"}: getattr(circuit, name)(.37, 0)
    elif name in {"u", "u3"}: circuit.append(name, [0], params=(.37, -.24, .51))
    elif name == "u2": circuit.append(name, [0], params=(-.24, .51))
    elif name in {"crx", "cry", "crz", "cp", "rxx", "ryy", "rzz"}: getattr(circuit, name)(.37, 0, 1)
    elif name in {"cx", "cz", "swap"}: getattr(circuit, name)(0, 1)
    else: getattr(circuit, name)(0)
    compiled = native_transpile(circuit, basis_gates=basis, optimization_level=0)
    assert {op.name for op in compiled.operations} <= set(basis)
    equivalent(circuit, compiled)


def test_phase_survives_compose_inverse_power_and_control():
    c = Circuit(1).h(0).phase(.47, 0)
    compiled = native_transpile(c, basis_gates=BASIS)
    equivalent(c.inverse(), compiled.inverse())
    equivalent(c.power(3), compiled.power(3))
    equivalent(c.control(), compiled.control())
    equivalent(c.compose(c), compiled.compose(compiled))


def test_symbolic_phase_and_angles_roundtrip_executable_ir():
    p = Parameter("theta")
    c = Circuit(2).phase(p/3, 0).cry(p, 0, 1)
    compiled = native_transpile(c, basis_gates=BASIS, optimization_level=2)
    restored = circuit_from_ir(IRProgram.from_json(compiled.to_ir().to_json()))
    assert restored.parameters == compiled.parameters
    equivalent(c.bind({p: .6}), restored.bind({p: .6}))


def test_dag_quantum_parallelism_and_depth():
    dag = circuit_to_dag(Circuit(3).h(0).x(1).cx(0,2))
    nodes = dag.topological_op_nodes()
    assert dag.size() == 3 and dag.width() == 3 and dag.depth() == 2
    assert dag.count_ops() == {"h": 1, "x": 1, "cx": 1}
    assert nodes[0] in dag.predecessors(nodes[-1])
    assert nodes[-1] in dag.successors(nodes[0])
    equivalent(dag_to_circuit(dag), Circuit(3).h(0).x(1).cx(0,2))


def test_dag_measurement_classical_condition_dependency():
    c = Circuit(2,1).h(0).measure(0,0).if_else((0,1), Circuit(2,1).x(1))
    dag = circuit_to_dag(c)
    nodes = dag.topological_op_nodes()
    assert nodes[1].name == "measure" and nodes[1] in dag.predecessors(nodes[2])
    assert DensityMatrixDevice().run(dag_to_circuit(dag)).probabilities() == DensityMatrixDevice().run(c).probabilities()


def test_dag_insert_substitute_remove_and_stable_ids():
    dag = DAGCircuit(1)
    first = dag.apply_operation_front(Operation("h", (0,)))
    last = dag.apply_operation_back(Operation("x", (0,)))
    new = dag.substitute_node(last, Operation("z", (0,)))
    assert new.node_id == last.node_id
    dag.remove_op_node(first)
    assert dag.validate() and dag.count_ops() == {"z": 1}


def test_dag_substitute_with_subgraph():
    dag = circuit_to_dag(Circuit(1).z(0))
    dag.substitute_node_with_dag(dag.topological_op_nodes()[0], circuit_to_dag(Circuit(1).s(0).s(0)))
    assert dag.validate()
    equivalent(dag_to_circuit(dag), Circuit(1).z(0))


def test_dag_replace_contiguous_block_and_reject_wrong_interface():
    dag = circuit_to_dag(Circuit(2).x(0).x(0).h(1))
    nodes = sorted(dag.topological_op_nodes(), key=lambda node: node.node_id)
    dag.replace_block(nodes[:2], Operation("id", (0,)))
    assert dag.validate()
    with pytest.raises(ValueError): dag.substitute_node(dag.topological_op_nodes()[0], Operation("x", (1,)))
    other = circuit_to_dag(Circuit(1).x(0).h(0).x(0))
    noncontiguous = other.topological_op_nodes()[::2]
    with pytest.raises(UnsupportedFeature): other.replace_block(noncontiguous, Operation("x", (0,)))


def test_dag_cycle_malformed_reference_and_missing_dependency_rejected():
    dag = circuit_to_dag(Circuit(1).h(0).x(0))
    a,b = dag.topological_op_nodes()
    dag.add_dependency(b,a)
    with pytest.raises(ValueError, match="cycle"): dag.validate()
    dag = circuit_to_dag(Circuit(1).h(0).x(0)); a,b = dag.topological_op_nodes()
    dag.edges[b.node_id].remove(a.node_id)
    with pytest.raises(ValueError, match="ordering"): dag.validate()
    dag.edges[b.node_id].add(10000)
    with pytest.raises(ValueError, match="references"): dag.validate()


def test_dag_invalid_wire_index_and_budget_rollback():
    dag = DAGCircuit(1, limits=CompilationLimits(max_dag_nodes=3))
    dag.apply_operation_back(Operation("x", (0,)))
    with pytest.raises(MemoryError): dag.apply_operation_back(Operation("h", (0,)))
    assert dag.size() == 1 and dag.validate()
    with pytest.raises(ValueError): dag.insert_operation(-1, Operation("x", (0,)))
    with pytest.raises(ValueError): dag.apply_operation_back(Operation("x", (2,)))
    with pytest.raises(TypeError): dag.apply_operation_back("x")


def test_control_structural_depth_not_runtime_loop_depth():
    c = Circuit(1).for_loop(range(4), Circuit(1).x(0))
    dag = circuit_to_dag(c)
    assert dag.depth(structural=True) == 1
    with pytest.raises(UnsupportedFeature): dag.depth()
    with pytest.raises(MemoryError): circuit_to_dag(Circuit(1).x(0).x(0), CompilationLimits(max_compilation_depth=1))


class Count(AnalysisPass):
    def run(self, circuit): return PassResult(circuit, {"count": len(circuit.operations)})


class AppendX(TransformationPass):
    def run(self, circuit): return PassResult(circuit.copy().x(0), changed=True)


class NeedsCount(AnalysisPass):
    requires = ("count",)
    def run(self, circuit): return PassResult(circuit, {"seen": self.property_set["count"]})


def test_pass_analysis_properties_and_requirements():
    pm = PassManager([Count(), NeedsCount()])
    assert pm.run(Circuit(1)).analyses["seen"] == 0
    with pytest.raises(ValueError, match="requirements"): PassManager([NeedsCount()]).run(Circuit(1))


def test_pass_transformation_invalidates_stale_analysis():
    with pytest.raises(ValueError, match="invalidated"):
        PassManager([Count(), AppendX(), NeedsCount()]).run(Circuit(1))
    class Preserving(AppendX): preserves = ("count",)
    assert PassManager([Count(), Preserving(), NeedsCount()]).run(Circuit(1)).analyses["seen"] == 0


def test_analysis_mutation_is_detected_without_changing_input():
    class Bad(AnalysisPass):
        def run(self, circuit): return PassResult(circuit.x(0))
    c = Circuit(1)
    with pytest.raises(ValueError, match="mutate"): PassManager([Bad()]).run(c)
    assert not c.operations


def test_pass_callbacks_seed_trace_and_bounded_repetition():
    calls = []
    pm = PassManager([AppendX()], seed=73, callback=lambda **value: calls.append(value), max_iterations=2)
    result = pm.run(Circuit(1))
    assert len(result.circuit.operations) == 2 and len(calls) == 2
    assert pm.passes[0].seed == 73 and result.analyses["pass_trace"][1]["iteration"] == 1
    with pytest.raises(MemoryError): PassManager([AppendX(), Count()], limits=CompilationLimits(max_pass_iterations=1)).run(Circuit(1))
    with pytest.raises(ValueError): PassManager(max_iterations=0)


def test_staged_pass_execution_and_invalid_pass_results():
    staged = StagedPassManager({"init": PassManager([AppendX()]), "analysis": PassManager([Count()])})
    assert staged.run(Circuit(1)).analyses["stages"]["analysis"]["count"] == 1
    with pytest.raises(TypeError): PassManager([object()]).run(Circuit(1))
    class Bad(TransformationPass):
        def run(self, circuit): return circuit
    with pytest.raises(TypeError): PassManager([Bad()]).run(Circuit(1))
    with pytest.raises(TypeError): StagedPassManager({"bad": object()}).run(Circuit(1))


def test_target_directed_qargs_and_instruction_properties():
    t = Target(3, ("h",), coupling_map=[(0,1),(1,2)], dt=1e-9)
    t.add_instruction("cx", {(0,1): InstructionProperties(8e-9, .02)})
    assert t.instruction_supported("cx", (0,1)) and not t.instruction_supported("cx", (1,0))
    assert not t.instruction_supported("h", (0,1))
    assert t.duration("cx", (0,1)) == 8
    assert t.to_dict()["instruction_properties"][-1]["error"] == .02
    with pytest.raises(ValueError): t.add_instruction("cx")
    with pytest.raises(ValueError): t.add_instruction("z", {(9,): None})
    with pytest.raises(TypeError): t.add_instruction("x", {(0,): .1})


def test_target_measurement_availability_and_missing_durations():
    t = Target(2, ("x",), reset=False)
    t.add_instruction("measure", {(1,): InstructionProperties(.3)})
    assert t.instruction_supported("measure", (1,)) and not t.instruction_supported("measure", (0,))
    assert not t.instruction_supported("reset", (1,))
    with pytest.raises(ValueError, match="Missing"): t.duration("x", (0,))
    with pytest.raises(ValueError): t.duration("cx", (0,1))


@pytest.mark.parametrize("kwargs", [{"num_qubits": -1}, {"num_qubits": True}, {"num_qubits": 2, "dt": 0}, {"num_qubits": 2, "pulse_alignment": 0}, {"num_qubits": 2, "conditional": 1}, {"num_qubits": 2, "coupling_map": [(0,2)]}])
def test_malformed_target_rejected(kwargs):
    with pytest.raises((ValueError, TypeError)): Target(**kwargs)


def test_layout_user_inverse_capacity_and_ancillas():
    layout = Layout([2,0]); target = Target(3, BASIS)
    assert layout.inverse() == {2: 0, 0: 1}
    out = native_transpile(Circuit(2).x(0).cx(0,1), target=target, initial_layout=layout)
    assert StatevectorDevice().probabilities(out)["101"] == pytest.approx(1.)
    with pytest.raises(ValueError): Layout([1,1])
    with pytest.raises(ValueError): Layout([-1])
    with pytest.raises(ValueError): native_transpile(Circuit(2), target=target, initial_layout={0:0})
    with pytest.raises(ValueError): native_transpile(Circuit(4), target=target)


def test_topology_aware_layout_is_explicit_and_bijective():
    c = Circuit(3).cx(0,1).cx(0,2)
    out = native_transpile(c, target=Target(4, BASIS, [(0,1),(1,2),(1,3)]), initial_layout="topology")
    assert out.metadata["initial_layout"][0] == 1
    assert len(set(out.metadata["initial_layout"].values())) == 3


@pytest.mark.parametrize("edges", [[(0,1),(1,2),(2,3)], [(0,1),(1,2),(2,3),(3,0)], [(0,1),(0,2),(0,3)], [(a,b) for a in range(4) for b in range(4) if a != b]])
def test_route_line_ring_star_full_preserves_operator_and_target(edges):
    c = Circuit(4).h(0).x(3).cx(0,3).ry(.21,2).cx(3,2).swap(1,3)
    out = native_transpile(c, target=Target(4, BASIS, edges))
    equivalent(c,out)
    assert all(len(op.wires) < 2 or (op.wires in edges) for op in out.operations)


def test_original_nonlocal_route_regression_is_fixed():
    c = Circuit(3).x(0).cx(0,2)
    out, report = native_transpile(c, coupling_map=[(0,1),(1,2)], optimization_level=0, return_report=True)
    assert StatevectorDevice().probabilities(out)["101"] == pytest.approx(1.)
    assert report["analyses"]["total_routing_swaps"] == 2
    equivalent(c,out)


def test_unrestored_layout_and_measurement_decode():
    c = Circuit(3,3).x(0).cx(0,2).measure(0,0).measure(1,1).measure(2,2)
    out = native_transpile(c, basis_gates=BASIS, coupling_map=CouplingMap.from_line(3), restore_layout=False)
    assert out.metadata["routing"]["final_layout"] == {0:1,1:0,2:2}
    assert [m.wire for m in out.measurements] == [1,0,2]
    assert StatevectorDevice().run_shots(c, shots=16, seed=4).counts() == StatevectorDevice().run_shots(out, shots=16, seed=4).counts()


def test_disconnected_topology_and_swap_growth_fail_explicitly():
    with pytest.raises(ValueError, match="disconnected"): native_transpile(Circuit(3).cx(0,2), coupling_map=[(0,1)])
    with pytest.raises(MemoryError, match="max_routing_swaps"):
        native_transpile(Circuit(3).cx(0,2), coupling_map=[(0,1),(1,2)], limits=CompilationLimits(max_routing_swaps=1))


def test_directed_cx_reversal_and_unavailable_edge():
    c = Circuit(2).h(0).cx(0,1)
    out = native_transpile(c, target=Target(2, BASIS, [(1,0)]))
    equivalent(c,out)
    assert all(op.wires == (1,0) for op in out.operations if op.name == "cx")
    target = Target(2, ("h",), [(0,1)])
    target.add_instruction("cx", {})
    with pytest.raises(UnsupportedFeature): native_transpile(c, target=target)


def test_optimization_parameter_expressions_not_cast_or_dropped():
    p = Parameter("p")
    c = Circuit(1).ry(p,0).ry(2*p,0).x(0).x(0)
    out = native_transpile(c, optimization_level=2)
    assert [op.name for op in out.operations] == ["ry"] and out.parameters == (p,)
    equivalent(c.bind({p:.3}), out.bind({p:.3}))


def test_optimization_cannot_cross_measure_reset_barrier_or_condition():
    c = Circuit(1,1).x(0).barrier().x(0).measure(0,0).x(0).reset(0).x(0)
    out = native_transpile(c, optimization_level=3)
    assert sum(op.name == "x" for op in out.operations) == 4
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(c), DensityMatrixDevice().density_matrix(out))


def test_optimization_levels_have_actual_distinct_behavior():
    c = Circuit(1).id(0).x(0).x(0)
    assert len(native_transpile(c, optimization_level=0).operations) == 3
    assert len(native_transpile(c, optimization_level=1).operations) == 2
    assert len(native_transpile(c, optimization_level=2).operations) == 0


def timed_target(**kwargs):
    return Target(3, ("x", "h", "cx"), [(0,1),(1,2)], dt=1e-9,
                  durations={"x": 4e-9, "h": 4e-9, "cx": 12e-9, "measure": 8e-9}, **kwargs)


def test_asap_parallelism_critical_path_and_no_overlap():
    c = Circuit(3).x(0).h(1).cx(0,1).x(2)
    result = SchedulingPass(timed_target()).run(c)
    records = result.analyses["schedule"]["operations"]
    assert [r["start"] for r in records] == [0,0,0,4]
    assert result.analyses["schedule"]["makespan"] == 16
    equivalent(c,result.circuit)


def test_alap_moves_slack_later_without_breaking_dependencies():
    c = Circuit(3).x(0).h(1).cx(0,1).x(2)
    records = SchedulingPass(timed_target(), "alap").run(c).analyses["schedule"]["operations"]
    assert next(r for r in records if r["wires"] == [2])["start"] == 12
    assert max(r["end"] for r in records) == 16


def test_schedule_alignment_and_delay_padding_execute_same_state():
    c = Circuit(3,1).x(0).cx(0,1).measure(0,0)
    result = SchedulingPass(timed_target(pulse_alignment=4, acquire_alignment=8), insert_delays=True).run(c)
    assert all(r["start"] % (8 if r["operation"] == "measure" else 4) == 0 for r in result.analyses["schedule"]["operations"])
    np.testing.assert_allclose(StatevectorDevice().statevector(c), StatevectorDevice().statevector(result.circuit))


def test_schedule_explicit_delay_units_and_seconds_mode():
    c = Circuit(1).delay(4,0,unit="ns").x(0)
    result = SchedulingPass(Target(1,("x",), durations={"x":2e-9})).run(c)
    assert result.analyses["schedule"]["makespan"] == pytest.approx(6e-9)


def test_schedule_rejects_missing_duration_granularity_and_alignment_dt():
    with pytest.raises(ValueError, match="Missing"): SchedulingPass(Target(1,("x",))).run(Circuit(1).x(0))
    with pytest.raises(ValueError, match="granularity"): SchedulingPass(Target(1,("x",),dt=1,durations={"x":3},granularity=2)).run(Circuit(1).x(0))
    with pytest.raises(ValueError, match="explicit target dt"): SchedulingPass(Target(1,("x",),pulse_alignment=2)).run(Circuit(1).x(0))
    with pytest.raises(ValueError, match="Delay in dt"): SchedulingPass(Target(1,("x",))).run(Circuit(1).delay(1,0))


def test_schedule_rejects_global_dynamic_and_resource_overflow():
    c = Circuit(1).if_else(True, Circuit(1).x(0))
    with pytest.raises(UnsupportedFeature, match="path-dependent"): SchedulingPass(timed_target()).run(c)
    with pytest.raises(MemoryError): SchedulingPass(timed_target(),limits=CompilationLimits(max_schedule_makespan=2)).run(Circuit(3).x(0))


def test_density_channel_target_capability_is_not_implicit():
    from quantumbridge.noise import AmplitudeDampingChannel
    c = Circuit(1).h(0).channel(AmplitudeDampingChannel(.2),[0])
    with pytest.raises(UnsupportedFeature): native_transpile(c, target=Target(1,("h",)))
    out = native_transpile(c, target=Target(1,("h",),allow_channels=True))
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(c), DensityMatrixDevice().density_matrix(out))


def test_offline_devicespec_and_backend_target_compile_execute():
    from quantumbridge.compat.qos_uqci.devicespec_adapter import build_devicespec, validate_devicespec
    spec = build_devicespec(num_qubits=3)
    assert validate_devicespec(spec)
    target = Target.from_device_spec(spec)
    c = Circuit(3).h(0).cx(0,2)
    equivalent(c, native_transpile(c, target=target))
    class Offline:
        def configuration(self): return {"n_qubits":3,"basis_gates":BASIS,"coupling_map":[(0,1),(1,2)]}
    equivalent(c, native_transpile(c, target=Target.from_backend(Offline())))


@pytest.mark.parametrize("kind", ["if_true", "if_false", "if_else", "nested", "for", "while", "switch", "break", "continue", "store"])
def test_dynamic_compile_and_execute_preserves_classical_quantum_semantics(kind):
    c = Circuit(3,3).h(0).measure(0,0)
    body = Circuit(3,3).cx(0,2).ry(.37,1)
    if kind in {"if_true", "if_false", "if_else"}:
        c = c.if_else(True if kind == "if_true" else False if kind == "if_false" else bit(0), body, Circuit(3,3).rx(.2,2))
    elif kind == "nested": c = c.if_else(bit(0), Circuit(3,3).if_else(True,body))
    elif kind == "for": c = c.for_loop(range(3),body)
    elif kind == "while": c = c.while_loop(bit(0), body.store(bit(0),0))
    elif kind == "switch": c = c.switch(bit(0), {1:body}, Circuit(3,3).rx(.2,2))
    elif kind == "break": c = c.for_loop(range(3),body.break_loop().x(2))
    elif kind == "continue": c = c.for_loop(range(3),body.continue_loop().x(2))
    else:
        var = c.add_var("counter",UInt(3),0)
        c = c.for_loop(range(3),body.store(var,var+1)).if_else(var.eq(3),Circuit(3,3).x(2))
    c.measure(0,0).measure(1,1).measure(2,2)
    target = Target(3,BASIS,[(0,1),(1,2)])
    out = native_transpile(c,target=target,optimization_level=2)
    assert out.metadata["transpile"]["analyses"]["target_validated"]
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(c),DensityMatrixDevice().density_matrix(out),atol=2e-12)
    expected, actual = DensityMatrixDevice().run(c).probabilities(), DensityMatrixDevice().run(out).probabilities()
    labels = sorted(set(expected) | set(actual))
    np.testing.assert_allclose([expected.get(label,0) for label in labels],[actual.get(label,0) for label in labels],atol=2e-12)


@pytest.mark.parametrize("scenario", ["rx", "ry", "shared", "nonlinear", "hamiltonian"])
@pytest.mark.parametrize("method", ["adjoint", "parameter-shift", "finite-diff"])
def test_compiled_qnode_gradients_retain_chain_rule(scenario,method):
    observable = Hamiltonian([(1.,PauliZ(0)),(.4,PauliZ(2))])
    def fn(t,x):
        if scenario in {"rx","ry"}: getattr(t,scenario)(x,0)
        elif scenario == "shared": t.ry(x,0); t.ry(x,0)
        elif scenario == "nonlinear": t.ry(2*x+np.sin(x),0)
        else: t.ry(x,0); t.rx(2*x,2); t.cx(0,2)
        return t.expval(observable)
    node = QNode(fn,3)
    compiled = node.compile(basis_gates=BASIS,coupling_map=[(0,1),(1,2)],optimization_level=2)
    assert compiled(.31) == pytest.approx(node(.31),abs=2e-12)
    assert compiled.gradient(.31,method=method) == pytest.approx(node.gradient(.31,method=method),abs=2e-8)


def test_compiled_qnode_rejects_unmapped_measurement_layout():
    node = QNode(lambda t,x:(t.ry(x,0),t.expval(PauliZ(0)))[-1],2)
    with pytest.raises(UnsupportedFeature,match="identity layout"): node.compile(initial_layout=[1,0])(.3)


def test_compiled_mps_100_qubits_has_no_dense_state_fallback(monkeypatch):
    from quantumbridge.information import MatrixProductState
    def forbidden(*args,**kwargs): raise AssertionError("Dense expansion is forbidden.")
    monkeypatch.setattr(MatrixProductState,"statevector",forbidden)
    monkeypatch.setattr(StatevectorDevice,"statevector",forbidden)
    c = Circuit(100).h(0)
    for wire in range(99): c.cx(wire,wire+1)
    out = native_transpile(c,target=Target(100,BASIS,CouplingMap.from_line(100)))
    result = MatrixProductStateDevice().run(out)
    assert result.mps.peak_bond_dimension == 2
    assert max(result.mps.bond_dimensions) == 2
    assert MatrixProductStateDevice().expectation(out,PauliZ(99)) == pytest.approx(0,abs=1e-12)
