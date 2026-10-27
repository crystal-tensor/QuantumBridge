"""Independent physical-wire and measurement-map diagnostic tests."""

import numpy as np
import pytest

from quantumbridge.finance.compiled_diagnostics import compiled_probabilities, qlisp_probabilities


def test_sparse_physical_qasm_respects_classical_output_order():
    source = '''OPENQASM 2.0;
include "qelib1.inc";
qreg q[256]; creg c[2];
x q[151];
barrier q;
measure q[151] -> c[0];
measure q[14] -> c[1];'''
    result = compiled_probabilities(source)
    assert result["active_physical_qubits"] == [14, 151]
    assert result["physical_measurement_map"] == {0: 151, 1: 14}
    assert result["probabilities"] == pytest.approx([0, 0, 1, 0])


def test_independent_qlisp_u_cz_bell_state():
    h = ("U", np.pi / 2, 0.0, np.pi)
    raw = [(h, "Q11"), (h, "Q4"), ("CZ", ("Q11", "Q4")),
           (h, "Q4"), ("Barrier", ("Q11", "Q4")),
           (("Measure", 0), "Q11"), (("Measure", 1), "Q4")]
    result = qlisp_probabilities(repr(raw))
    np.testing.assert_allclose(result["probabilities"], [.5, 0, 0, .5], atol=1e-14)
    assert result["physical_measurement_map"] == {0: 11, 1: 4}


@pytest.mark.parametrize("source", [
    "__import__('os').system('echo forbidden')",
    "[(('Measure', 0), 'Q4'), (('U', 0, 0, 0), 'Q4')]",
    "[(('Measure', 0), 'Q4'), (('Measure', 0), 'Q11')]",
    "[(('U', True, 0, 0), 'Q4'), (('Measure', 0), 'Q4')]",
    "[('UNSUPPORTED', 'Q4'), (('Measure', 0), 'Q4')]",
    "[(('U', 0, 0, 0), 'bad-wire'), (('Measure', 0), 'bad-wire')]",
])
def test_malformed_qlisp_refused_without_execution(source):
    with pytest.raises(ValueError):
        qlisp_probabilities(source)


def test_unmeasured_active_qubit_remains_in_quantum_evolution():
    source = '''OPENQASM 2.0; include "qelib1.inc";
qreg q[50]; creg c[1]; h q[40]; cx q[40],q[4]; measure q[4] -> c[0];'''
    result = compiled_probabilities(source)
    assert result["active_physical_qubits"] == [4, 40]
    assert result["probabilities"] == pytest.approx([.5, .5])


def test_more_than_six_active_qubits_refuses_before_dense_simulation():
    source = 'OPENQASM 2.0; include "qelib1.inc"; qreg q[8]; creg c[1]; h q; measure q[0] -> c[0];'
    with pytest.raises(ValueError, match="active"):
        compiled_probabilities(source)
