import pytest

from quantumbridge.qasm import QASMParseError, loads


def test_qasm_error_message_is_clear():
    with pytest.raises(QASMParseError, match="Opaque gate"):
        loads("OPENQASM 2.0; qreg q[1]; opaque bad a; bad q[0];")
