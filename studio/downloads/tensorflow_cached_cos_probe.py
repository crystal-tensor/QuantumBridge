# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Observe cached TensorFlow curvature; this is not a Native acceptance gate."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import tensorflow as tf


def observe(profile):
    rows = []
    for cached_value in (False, True):
        for cached_derivative in (False, True):
            for mode in ("for", "rof"):
                function = tf.function(tf.cos, autograph=False) if cached_value else tf.cos

                def execute(point):
                    direction = tf.constant(.4, tf.float64)
                    if mode == "for":
                        with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                            with tf.GradientTape() as reverse:
                                reverse.watch(point)
                                value = function(point)
                            first = reverse.gradient(value, point)
                        return forward.jvp(first)
                    with tf.GradientTape() as reverse:
                        reverse.watch(point)
                        with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                            value = function(point)
                        first = forward.jvp(value)
                    return reverse.gradient(first, point)

                call = tf.function(execute, autograph=False) if cached_derivative else execute
                results = []
                for point in (.37, 0., -.25):
                    actual = call(tf.constant(point, tf.float64))
                    expected = float(-.4*np.cos(point))
                    value = None if actual is None else float(actual)
                    results.append(dict(point=point, actual=value, expected=expected,
                        matches_formula=value is not None and abs(value-expected) < 3e-12))
                rows.append(dict(cached_value=cached_value, cached_derivative=cached_derivative,
                                 mode=mode, results=results))
    assert not any(name.split(".")[0] in {"quantumbridge", "qiskit", "pennylane"} for name in sys.modules)
    return dict(profile=profile, tensorflow=tf.__version__,
        recorded_at=datetime.now(timezone.utc).isoformat(), quantumbridge_or_sdks_imported=False,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope="raw TensorFlow cos second directional derivative; observation only",
        native_accepted=False, rows=rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="standalone")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = observe(args.profile)
    body = json.dumps(report, indent=2)+"\n"
    if args.output:
        args.output.write_text(body)
    print(body)
