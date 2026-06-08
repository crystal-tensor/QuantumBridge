from quantumbridge.qasm import loads


def test_qasm_importer_supported_p2_subset():
    circuit = loads(
        'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[3];\ncreg c[3];\nh q[0];\ns q[0];\ntdg q[1];\ncx q[0],q[1];\nccx q[0],q[1],q[2];\nmeasure q -> c;'
    )
    assert circuit.num_qubits == 3
    assert [op.name for op in circuit.operations] == ["h", "s", "tdg", "cx", "ccx"]
    assert len(circuit.measurements) == 3
