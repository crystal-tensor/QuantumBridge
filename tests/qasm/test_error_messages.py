import pytest

from quantumbridge.qasm import QASMParseError, loads


def test_qasm_error_message_is_clear():
    with pytest.raises(QASMParseError, match="unsupported"):
        loads("OPENQASM 2.0; qreg q[1]; opaque bad q[0];")
