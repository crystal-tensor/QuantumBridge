# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""External installed-SDK observation only; never imported by QB execution."""

import json
import math
import platform
import warnings

import pennylane as qml
import tensorflow as tf


def main():
    tf.get_logger().setLevel("ERROR")
    records = []
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        for method in ("backprop", "adjoint", "parameter-shift"):
            for max_diff in (1, 2):
                for traced in (False, True):
                    for order in range(4):
                        record = dict(method=method, max_diff=max_diff, traced=traced, order=order)
                        try:
                            device = qml.device("default.qubit", wires=1)
                            @qml.qnode(device, interface="tf", diff_method=method, max_diff=max_diff)
                            def node(point):
                                qml.RY(point, wires=0)
                                return qml.expval(qml.PauliZ(0))
                            function = node
                            def differentiate(base):
                                def gradient(point):
                                    with tf.GradientTape() as tape:
                                        tape.watch(point)
                                        value = base(point)
                                    return None if value is None else tape.gradient(value, point)
                                return gradient
                            for _ in range(order):
                                function = differentiate(function)
                            if traced:
                                function = tf.function(function, autograph=False, jit_compile=False)
                            value = function(tf.constant(0.37, tf.float64))
                            expected = math.cos(0.37+order*math.pi/2)
                            if value is None:
                                record.update(outcome="disconnected", expected=expected)
                            else:
                                actual = float(value)
                                if math.isfinite(actual):
                                    record.update(outcome="match" if abs(actual-expected) < 2e-10 else "mismatch", actual=actual, expected=expected)
                                else:
                                    record.update(outcome="nonfinite", actual=repr(actual), expected=expected)
                        except Exception as error:
                            record.update(outcome="exception", error=type(error).__name__+": "+str(error))
                        records.append(record)
    print(json.dumps(dict(diagnostic_only=True, python=platform.python_version(), tensorflow=tf.__version__,
        pennylane=qml.__version__, tensorflow_origin=tf.__file__, pennylane_origin=qml.__file__,
        jit_compile=False, records=records, warnings=sorted(set(str(item.message) for item in captured))), allow_nan=False))


if __name__ == "__main__":
    main()
