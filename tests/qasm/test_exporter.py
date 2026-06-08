from quantumbridge.core import Circuit
from quantumbridge.qasm import dumps


def test_qasm_exporter_p2_gates():
    circuit = Circuit(3, 1).h(0).phase(0.5, 0).swap(0, 1).ccx(0, 1, 2).measure(2, 0)
    text = dumps(circuit)
    assert "phase(0.5) q[0];" in text
    assert "swap q[0],q[1];" in text
    assert "ccx q[0],q[1],q[2];" in text
