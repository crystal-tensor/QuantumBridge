# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Measure native frozen-plan execution without caching parameter values.

This is a diagnostic, not an allocator guarantee or an SDK acceptance gate.
Run each case in its own process for comparable allocator/RSS observations.
"""

import argparse
import gc
import json
from pathlib import Path
import resource
import sys
from time import perf_counter
import weakref

import numpy as np
import tensorflow as tf

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.qml import QNode


ROOT = Path(__file__).resolve().parents[1]


def case_data(name):
    if name == "eight_parameter_hvp":
        data = json.loads((ROOT / "tests/information/data/native_mps_power_oracles.json").read_text())["eight"]
        parameters = qb.ParameterVector("angles", 8)
        source = qb.QuantumCircuit(1)
        for index in range(0, 8, 2):
            body = qb.Circuit(1).rx(parameters[index], 0).rz(parameters[index + 1], 0)
            source.append(body.to_gate().power(0.5, annotated=True), (0,))
        return source, tuple(parameters), (qb.PauliZ(0),), data
    data = next(item for item in json.loads(
        (ROOT / "tests/information/data/tf_whole_qnode_oracles.json").read_text())["cases"]
        if item["name"] == ("full_entangling" if name == "four_qubit_entangling" else "requested_reverse"))
    parameters = qb.ParameterVector("angles", 2)
    p, q = parameters
    gate = qb.Circuit(1).ry(-p, 0).rz(q*q + 0.4, 0).rx(p, 0).to_gate().power(0.5, annotated=True)
    source = qb.QuantumCircuit(4 if name == "four_qubit_entangling" else 1)
    if source.num_qubits == 4:
        source.h(0)
        source.global_phase = 0.17*p*q
        source.cx(0, 3)
        source.append(gate, (2,))
        source.ry(p*q, 0)
        source.cx(2, 1)
        source.rz(p-q, 3)
        other = qb.Hamiltonian([(1., qb.PauliString(((0, "X"), (3, "X")))),
            (0.2, qb.PauliString(((1, "Y"), (2, "Z"))))])
        observables = (qb.PauliZ(2), other)
    else:
        source.append(gate, (0,))
        observables = (qb.PauliZ(0), qb.PauliX(0)) if name == "two_outputs" else (qb.PauliZ(0),)
    return source, tuple(parameters), observables, data


def observe_memory():
    try:
        result = dict(tf.config.experimental.get_memory_info("CPU:0"))
        return dict(available=True, allocator="TensorFlow CPU:0", **result)
    except (ValueError, RuntimeError) as error:
        return dict(available=False, current=None, peak=None, reason=f"{type(error).__name__}: {error}")


def timed(function, point):
    started = perf_counter()
    result = function(point)
    arrays = [np.asarray(value.numpy()) for value in tf.nest.flatten(result)]
    return result, arrays, perf_counter() - started


def graph_info(function):
    graph = function.get_concrete_function().graph.as_graph_def()
    nodes = list(graph.node) + [node for item in graph.library.function for node in item.node_def]
    callbacks = [node.op for node in nodes if node.op in {"PyFunc", "PyFuncStateless", "EagerPyFunc"}]
    assert not callbacks, callbacks
    return dict(top_level_nodes=len(graph.node), function_definitions=len(graph.library.function),
        total_function_nodes=sum(len(item.node_def) for item in graph.library.function),
        callback_ops=callbacks, trace_count=function.experimental_get_tracing_count())


def run(name, repeats):
    source, parameters, observables, data = case_data(name)
    first_builder = QNode.from_circuit(source, observables[0]).fn

    def program(tape, point):
        first = first_builder(tape, point)
        return (first, tape.expval(observables[1])) if len(observables) == 2 else first

    node = QNode(program, source.num_qubits, interface="tensorflow", diff_method="adjoint", max_diff=2,
        higher_order_limits=HigherOrderLimits(max_adjoint_operations=1_000_000_000,
            max_hessian_elements=1 if name == "eight_parameter_hvp" else 1_000_000),
        unified_limits=UnifiedExecutionLimits(max_derivative_work=1_000_000_000))
    signature = [tf.TensorSpec((len(parameters),), tf.float64)]
    before_memory = observe_memory()
    started = perf_counter()
    handle = node.compile_tensorflow_inline(parameters=parameters, input_signature=signature)
    creation = perf_counter() - started
    point = tf.constant(data["point"], tf.float64)
    direction_array = data["direction"] if name == "eight_parameter_hvp" else [0.4, -0.3]
    direction = tf.constant(direction_array, tf.float64)
    expected_values = np.atleast_1d(data["value"]) if name == "eight_parameter_hvp" else np.asarray(data["outputs"])[:len(observables)]
    weights = np.array([0.7, -0.2])[:len(observables)]
    if name == "eight_parameter_hvp":
        expected_hvp = np.asarray(data["hvp"])
    else:
        jacobian = np.asarray(data["jacobian"])[:len(observables)]
        hessian = np.asarray(data["hessians"])[:len(observables)]
        slope = np.exp(expected_values) + 0.6*expected_values**2
        curve = np.exp(expected_values) + 1.2*expected_values
        expected_hvp = jacobian.T @ (weights*curve*(jacobian @ direction_array)) + np.einsum(
            "o,oij,j->i", weights*slope, hessian, direction_array)

    def values(x):
        return tf.reshape(tf.stack(tf.nest.flatten(handle(x))), (-1,))

    def loss(x):
        y = values(x)
        return y[0] if name == "eight_parameter_hvp" else tf.reduce_sum(
            tf.constant(weights, tf.float64)*(tf.exp(y) + 0.2*y**3))

    def second(mode):
        def execute(x):
            if mode == "for":
                with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                    with tf.GradientTape() as reverse:
                        reverse.watch(x)
                        value = loss(x)
                    gradient = reverse.gradient(value, x)
                return forward.jvp(gradient)
            if mode == "rof":
                with tf.GradientTape() as reverse:
                    reverse.watch(x)
                    with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                        value = loss(x)
                    tangent = forward.jvp(value)
                return reverse.gradient(tangent, x)
            with tf.GradientTape() as outer:
                outer.watch(x)
                with tf.GradientTape() as inner:
                    inner.watch(x)
                    value = loss(x)
                gradient = inner.gradient(value, x)
                projected = tf.reduce_sum(gradient*direction)
            return outer.gradient(projected, x)
        return execute

    records = {}
    retained = None
    for mode, eager, expected in [("value", values, expected_values)] + [
            (mode, second(mode), expected_hvp) for mode in ("for", "rof", "tape_tape")]:
        result, arrays, eager_time = timed(eager, point)
        np.testing.assert_allclose(arrays[0], expected, atol=2e-9, rtol=0)
        traced = tf.function(eager, input_signature=signature, autograph=False, jit_compile=False)
        result, arrays, first_time = timed(traced, point)
        np.testing.assert_allclose(arrays[0], expected, atol=2e-9, rtol=0)
        cached_times = []
        for _ in range(repeats):
            result, arrays, duration = timed(traced, point)
            np.testing.assert_allclose(arrays[0], expected, atol=2e-9, rtol=0)
            cached_times.append(duration)
        records[mode] = dict(eager_seconds=eager_time, first_outer_trace_and_call_seconds=first_time,
            subsequent_cached_call_seconds=cached_times, graph=graph_info(traced),
            max_absolute_oracle_error=float(np.max(np.abs(arrays[0] - expected))))
        retained = result
        del result, arrays, traced
        gc.collect()
    while_retained = observe_memory()
    output_ref = weakref.ref(retained)
    retained_output_bytes = int(np.prod(retained.shape))*retained.dtype.size
    del retained
    gc.collect()
    after_release = observe_memory()
    started = perf_counter()
    for _ in range(20):
        handle._fingerprint()
    fingerprint = (perf_counter() - started)/20
    return dict(case=name, tensorflow_version=tf.__version__, tensorflow_origin=tf.__file__,
        python=sys.version, python_executable=sys.executable, width=source.num_qubits,
        parameter_count=len(parameters), output_count=len(observables), handle_creation_seconds=creation,
        repeated_static_fingerprint_seconds=fingerprint, modes=records,
        memory_before=before_memory, memory_while_retained=while_retained, memory_after_output_release=after_release,
        python_output_collected=output_ref() is None, retained_output_payload_bytes=retained_output_bytes,
        python_collection_scope="Python Tensor object only; not proof of backend allocator release",
        process_cumulative_maxrss_raw=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        process_maxrss_scope="Cumulative process RSS, raw OS units; not tensor workspace",
        static_estimated_workspace_bytes=handle.metadata["budget"]["workspace_bytes"],
        observed_per_operation_peak_workspace=None,
        workspace_scope="Allocator observation is process-wide if available, not per-operation workspace",
        optimization="NONE: measurement only; no parameter-dependent tensor cache",
        timing_scope="Single process diagnostic with concurrent local regression workloads; not isolated benchmark")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("one_qubit_noncommuting", "two_outputs", "four_qubit_entangling", "eight_parameter_hvp"), required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20:
        parser.error("repeats must be between one and twenty")
    result = run(args.case, args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
