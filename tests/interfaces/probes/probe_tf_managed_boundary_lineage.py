# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Observe public function boundaries; no private TF gradient hooks."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import tensorflow as tf

import quantumbridge as qb
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode


def run(native):
    if native:
        p, q = qb.ParameterVector("input", 2)
        circuit = qb.QuantumCircuit(1)
        circuit.ry(p*p+q, 0)
        node = QNode.from_circuit(circuit, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint", max_diff=2)
    else:
        def program(tape, x):
            tape.ry(x[0]*x[0]+x[1], 0)
            return tape.expval(qb.PauliZ(0))
        node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    graphs = []
    for key, function in handle._graphs.items():
        concrete = function.get_concrete_function()
        graph = concrete.graph.as_graph_def()
        graphs.append(dict(kind=key[0], name=concrete.name.decode(),
            input_count=len(concrete.inputs), output_count=len(concrete.outputs),
            signature=[dict(name=t.name, shape=t.shape.as_list()) for t in concrete.inputs],
            graph_sha256=hashlib.sha256(graph.SerializeToString(deterministic=True)).hexdigest(),
            callback_ops=[n.op for n in list(graph.node)+[n for f in graph.library.function for n in f.node_def]
                if n.op in {"PyFunc", "EagerPyFunc", "PyFuncStateless"}]))
    calls, complete = [], handle._run_graph
    def observe(function, packet):
        calls.append(dict(cached_function=hasattr(function, "get_concrete_function"), name=function.__name__))
        return complete(function, packet)
    handle._run_graph = observe
    x, d = tf.constant([.37, .82], tf.float64), tf.constant([.4, -.3], tf.float64)
    a, slope = .37**2+.82, np.array([.74, 1.])
    value, gradient = np.cos(a), -np.sin(a)*slope
    hessian = -np.cos(a)*np.outer(slope, slope)-np.sin(a)*np.diag([2., 0.])
    expected = 2*gradient*(gradient @ [.4, -.3])+2*(value-.3)*(hessian @ [.4, -.3])
    ledger = UnifiedResourceLedger()
    observation = dict(native_source=native, frozen_binding=handle._frozen_binding is not None,
        cached_query_graphs=graphs, observed_invocations=calls, expected=expected.tolist())
    try:
        with ResourceScope(ledger):
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                with tf.autodiff.ForwardAccumulator(x, d) as forward:
                    loss = (handle(x)-.3)**2
                tangent = forward.jvp(loss)
            actual = reverse.gradient(tangent, x)
        observation.update(outcome="match" if actual is not None and np.allclose(actual, expected, atol=2e-10, rtol=0) else "mismatch",
            actual=None if actual is None else actual.numpy().tolist())
    except Exception as error:
        observation.update(outcome="error", error=type(error).__name__+": "+str(error))
    observation["receipt"] = ledger.receipt()
    return observation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    records = [run(native) for native in (False, True)]
    assert records[1]["outcome"] == "match"
    assert not any(call["cached_function"] for call in records[1]["observed_invocations"])
    result = dict(diagnostic_only=True, tensorflow=tf.__version__, tensorflow_origin=tf.__file__, records=records,
        private_generated_gradient_root_cause="NOT_PROVEN; only public signatures and actual call boundaries observed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(diagnostic_completed=True, outcomes=[r["outcome"] for r in records])))


if __name__ == "__main__":
    main()
