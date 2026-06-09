from quantumbridge.core import Circuit
from quantumbridge.compat.mqt import (
    export_mqt_core_like_qasm_subset,
    import_mqt_core_like_qasm_subset,
    quantumbridge_ir_to_mqt_core_like_dict,
)


def test_mqt_core_like_qasm_subset_exports_and_imports():
    circuit = Circuit(2, 2).h(0).rx(0.25, 1).cx(0, 1).measure(0, 0).measure(1, 1)
    data = quantumbridge_ir_to_mqt_core_like_dict(circuit)

    qasm = export_mqt_core_like_qasm_subset(data)
    restored = import_mqt_core_like_qasm_subset(qasm)

    assert "OPENQASM 2.0" in qasm
    assert restored["num_qubits"] == 2
    assert [op["name"] for op in restored["operations"]] == ["h", "rx", "cx"]
    assert len(restored["measurements"]) == 2
