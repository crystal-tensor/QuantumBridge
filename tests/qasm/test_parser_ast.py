from math import pi

from quantumbridge.qasm import parse


def test_qasm_parser_ast_parameter_expression():
    program = parse('OPENQASM 2.0; include "qelib1.inc"; qreg q[1]; ry(-pi/4) q[0];')
    gate = program.statements[0]
    assert gate.name == "ry"
    assert abs(gate.params[0] + pi / 4) < 1e-12
