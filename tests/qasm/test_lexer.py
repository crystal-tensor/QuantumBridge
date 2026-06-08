from quantumbridge.qasm import lex


def test_qasm_lexer_skips_comments_and_tokenizes():
    tokens = lex('OPENQASM 2.0; // comment\nqreg q[2];\nrx(pi/2) q[0];')
    values = [token.value for token in tokens]
    assert "OPENQASM" in values
    assert "comment" not in values
    assert "rx" in values
    assert "pi" in values
