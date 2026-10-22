# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Owned repeated instruction objects and genuinely executable definitions."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps, qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def test_repeat_retains_real_owned_instruction_invocations_not_flattened_fragments():
    p = qb.Parameter("p")
    owner = qb.Circuit(1, name="source").rx(p, 0).h(0).to_instruction(label="display")
    result = owner.repeat(2)
    assert type(result) is qb.Instruction and result.name == "source*2"
    assert len(result.definition.operations) == 2
    first = result.definition.operations[0].metadata["instruction_object"]
    second = result.definition.operations[1].metadata["instruction_object"]
    assert type(first) is type(second) is qb.Instruction and first is not second and first is not owner
    owner.params[0] = .9
    assert first.params == [p] and second.params == [p] and result.params == [p]
    actual = qb.Circuit.from_instruction(result).bind({p: .3})
    expected = Operator(qb.Circuit(1).rx(.3, 0).h(0)).data
    np.testing.assert_allclose(Operator(actual).data, expected @ expected, atol=4e-13, rtol=0)


@pytest.mark.parametrize("opaque", [False, True])
@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_repeat_retains_instruction_type_params_and_lifetimes_across_formats(opaque, format):
    p = qb.ParameterVector("p", 2)[1]
    owner = qb.Instruction("opaque", 1, 0, [p], "display") if opaque else qb.Circuit(1, name="source").rx(p, 0).to_instruction(label="display")
    source = qb.Circuit.from_instruction(owner.repeat(2))
    restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json())) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    assert len(restored.operations) == 2
    for item in restored.operations:
        actual = item.metadata["instruction_object"]
        assert type(actual) is qb.Instruction and actual.name == owner.name and actual.params == [p]
        assert actual.label == owner.label
    if not opaque:
        np.testing.assert_allclose(Operator(restored.bind({p: .3})).data,
            Operator(qb.Circuit(1).rx(.6, 0)).data, atol=4e-13, rtol=0)
    else:
        with pytest.raises((ValueError, qb.UnsupportedFeature)): restored.bind({p: .3}).lowered()


@pytest.mark.parametrize("path", ["gate", "instruction", "circuit"])
@pytest.mark.parametrize("state", [0, 1])
def test_repeat_retains_existing_coherent_control_paths_and_exact_global_phase(path, state):
    body = qb.Circuit(1, name="rotation").ry(.3, 0)
    body.global_phase = .17
    repeated = body.to_instruction().repeat(2)
    source = qb.Circuit.from_instruction(repeated)
    controlled = source.to_gate().control(1, ctrl_state=state) if path == "gate" else repeated.control(1, ctrl_state=state) if path == "instruction" else source.control(1, ctrl_state=state)
    c, s = np.cos(.3), np.sin(.3)
    expected = np.eye(4, dtype=complex)
    expected[2*state:2*state+2, 2*state:2*state+2] = np.exp(.34j)*np.array([[c, -s], [s, c]])
    np.testing.assert_allclose(Operator(controlled).data, expected, atol=5e-13, rtol=0)


def test_control_after_instruction_qpy_import_rebuilds_width_dependent_registers():
    source = qb.Circuit.from_instruction(qb.Circuit(1).ry(.3, 0).to_instruction().repeat(2))
    restored = qpy_loads(qpy_dumps(source))[0]
    restored.metadata["tag"] = "owned"
    controlled = restored.control(1)
    assert controlled.metadata["tag"] == "owned" and controlled.num_qubits == 2
    encoded = qpy_loads(qpy_dumps(controlled))[0]
    expected = np.eye(4, dtype=complex)
    c, s = np.cos(.3), np.sin(.3)
    expected[2:, 2:] = [[c, -s], [s, c]]
    np.testing.assert_allclose(Operator(encoded).data, expected, atol=4e-13, rtol=0)
