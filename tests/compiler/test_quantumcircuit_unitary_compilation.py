# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real public-entry circuits through existing native compilation/transport."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization import qpy_dumps, qpy_loads, qasm2_dumps, qasm3_dumps
from quantumbridge.serialization import UnsupportedFeature as UnsupportedFormat


def source_and_oracle(local_width):
    dimension = 1 << local_width
    indices = np.arange(dimension)
    matrix = np.exp(2j * np.pi * np.outer(indices, indices) / dimension) / np.sqrt(dimension)
    matrix *= np.exp(1j * (.17 + .29 * indices))[None, :]
    wires = (3,) if local_width == 1 else (3, 1)
    p = qb.Parameter("transport_angle")
    source = qb.QuantumCircuit(4, global_phase=.23 + p / 7)
    source.h(0)
    source.rx(p, 2)
    source.unitary(matrix, list(wires), label="actual-public-entry")
    point = .37
    state = np.zeros(16, complex)
    for first in (0, 1):
        for second in (0, 1):
            state[first * 8 + second * 2] = (np.cos(point / 2) if second == 0
                else -1j * np.sin(point / 2)) / np.sqrt(2)
    axes = list(reversed(wires)) + [wire for wire in range(4) if wire not in wires]
    value = matrix @ np.transpose(state.reshape((2,) * 4), axes).reshape(dimension, -1)
    expected = np.transpose(value.reshape((2,) * 4), np.argsort(axes)).reshape(-1)
    return source, p, expected * np.exp(1j * (.23 + point / 7))


@pytest.mark.parametrize("local_width", [1, 2])
@pytest.mark.parametrize("path", ["source", "lowered", "compiler", "ir", "qpy13"])
def test_public_unitary_transport_preserves_complex_math_uuid_and_source(local_width, path):
    source, p, expected = source_and_oracle(local_width)
    before = source.to_ir().to_json()
    if path == "source":
        restored = source
    elif path == "lowered":
        restored = source.lowered()
    elif path == "compiler":
        restored = qb.transpile(source, basis_gates=["h", "rx", "ry", "rz", "sx", "unitary"], optimization_level=1)
    elif path == "ir":
        restored = circuit_from_ir(IRProgram.from_json(before))
    else:
        restored = qpy_loads(qpy_dumps(source, version=13))[0]
    assert tuple(parameter.uuid for parameter in restored.parameters) == (p.uuid,)
    bound = restored.assign_parameters({p: .37})
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(bound), expected, atol=2e-12, rtol=0)
    mps = qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=16).matrix_product_state(bound)
    np.testing.assert_allclose(mps.statevector(), expected, atol=2e-12, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("writer", [qasm2_dumps, qasm3_dumps])
def test_public_arbitrary_matrix_keeps_existing_precise_text_export_refusal(writer, record_property):
    source, p, _ = source_and_oracle(2)
    source = source.assign_parameters({p: .37})
    source.global_phase = 0
    before = source.to_ir().to_json()
    with pytest.raises(UnsupportedFormat) as error:
        writer(source, allow_metadata_loss=True)
    record_property("actual_refusal", str(error.value))
    assert error.value.feature == "basis_translation"
    assert any(word in str(error.value).lower() for word in ("unitary", "matrix", "definition"))
    assert source.to_ir().to_json() == before
