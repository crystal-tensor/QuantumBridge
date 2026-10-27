# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""I1 source audit only: inspect captured data, never import/execute its graph."""

import argparse
import hashlib
import json
from pathlib import Path

import tensorflow as tf

import quantumbridge as qb
from quantumbridge.core.operations import execution_operation
from quantumbridge.ir.qb_ir import _param_to_ir
from quantumbridge.qml import QNode


def inspect(kind):
    p, q = qb.ParameterVector("input", 2)
    source = qb.QuantumCircuit(1)
    source.ry(p*p+q, 0)
    builder, calls = QNode.from_circuit(source, qb.PauliZ(0)).fn, []
    def program(tape, point):
        calls.append("construct")
        if kind == "direct_tf":
            tape.ry(tf.sin(point[0])**2+point[1], 0)
            return tape.expval(qb.PauliZ(0))
        result = builder(tape, tf.reverse(point, [0]) if kind == "remapped_native" else point)
        if kind == "mixed_native":
            tape.rx(.2*point[0], 0)
        return result
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    concrete = handle._pack.get_concrete_function()
    graph = concrete.graph.as_graph_def(add_shapes=True)
    assert graph.ByteSize() < 65536 and len(graph.node) < 128
    scalars = []
    for operation in concrete.graph.get_operations():
        record = dict(name=operation.name, op=operation.type,
            inputs=[tensor.name for tensor in operation.inputs],
            controls=[op.name for op in operation.control_inputs],
            outputs=[dict(name=t.name, dtype=t.dtype.name, shape=t.shape.as_list()) for t in operation.outputs])
        if operation.type == "Const" and operation.outputs[0].shape.num_elements() <= 16:
            record["constant"] = tf.make_ndarray(operation.get_attr("value")).tolist()
        scalars.append(record)
    operations = [execution_operation(raw) for raw in handle._whole._circuit.operations]
    if kind == "mixed_native":
        assert operations[-1].name == "rx" and operations[-1].wires == (0,)
        assert len(operations[-1].params) == 1
    assert calls == ["construct"]
    assert handle._frozen_binding is None
    return dict(source=kind, user_function_constructions=len(calls), frozen_native_binding=False,
        pack_graph_bytes=graph.ByteSize(), pack_nodes=scalars,
        pack_graph_sha256=hashlib.sha256(graph.SerializeToString(deterministic=True)).hexdigest(),
        external_captures=len(concrete.captured_inputs), variables=len(concrete.variables),
        functions=len(graph.library.function), input_names=[t.name for t in concrete.inputs],
        output_names=[t.name for t in concrete.outputs],
        occurrence_uuids=[str(parameter.uuid) for parameter in handle._plan.recorder.parameters],
        compiled_global_phase=_param_to_ir(handle._whole._circuit.global_phase),
        compiled_quantum_operations=[dict(name=operation.name, wires=operation.wires,
            parameters=[_param_to_ir(p) for p in operation.params]) for operation in operations])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [inspect(kind) for kind in ("direct_tf", "remapped_native", "mixed_native")]
    result = dict(source_audit_completed=True, scalar_lowerer_implemented=False,
        tensorflow=tf.__version__, tensorflow_origin=tf.__file__, records=records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(source_audit_completed=True, summaries=[dict(source=r["source"],
        nodes=len(r["pack_nodes"]), operations=[o["name"] for o in r["compiled_quantum_operations"]],
        scalar_ops=sorted({n["op"] for n in r["pack_nodes"]})) for r in records])))


if __name__ == "__main__":
    main()
