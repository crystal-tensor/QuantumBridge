from quantumbridge.core import Circuit
from quantumbridge.qasm import dumps, loads


def test_qasm_roundtrip_preserves_basic_structure():
    original = Circuit(2, 2).h(0).rx(0.25, 1).cx(0, 1).measure(0, 0).measure(1, 1)
    parsed = loads(dumps(original))
    assert parsed.num_qubits == original.num_qubits
    assert parsed.num_bits == original.num_bits
    assert [op.name for op in parsed.operations] == [op.name for op in original.operations]
    assert [(m.wire, m.bit) for m in parsed.measurements] == [(0, 0), (1, 1)]
