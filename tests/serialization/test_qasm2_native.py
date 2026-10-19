# Independent mathematical and language behavior tests, no SDK dependency.
import io
import math
import numpy as np
import pytest
from quantumbridge import Circuit, StatevectorDevice, DensityMatrixDevice, Parameter
from quantumbridge.information import Operator
from quantumbridge.serialization import (qasm2_loads,qasm2_load,qasm2_dumps,qasm2_dump,
    SerializationLimits,SerializationError,UnsupportedFeature,ParseError,ResourceLimitError)

HEADER = 'OPENQASM 2.0; include "qelib1.inc"; '


def load(body): return qasm2_loads(HEADER+body)
def equivalent(left,right): np.testing.assert_allclose(Operator.from_circuit(left).data,Operator.from_circuit(right).data,atol=1e-12)


def test_qasm2_header_primitives_without_include():
    equivalent(qasm2_loads('OPENQASM 2.0;qreg q[2];U(pi/2,0,pi) q[0];CX q[0],q[1];'),Circuit(2).h(0).cx(0,1))


def test_qasm2_multi_register_mapping():
    c = load('qreg a[1];qreg b[2];creg ca[1];creg cb[2];x b[1];measure a -> ca;measure b -> cb;')
    assert c.operations[0].targets == (2,) and [(m.wire,m.bit) for m in c.measurements] == [(0,0),(1,1),(2,2)]
    assert 'qreg b[2];' in qasm2_dumps(c)


def test_qasm2_standard_gate_families():
    c = load('qreg q[2];h q[0];x q[1];y q[0];z q[1];s q[0];sdg q[0];t q[1];tdg q[1];cy q[0],q[1];cz q[0],q[1];')
    equivalent(c,Circuit(2).h(0).x(1).y(0).z(1).s(0).sdg(0).t(1).tdg(1).cy(0,1).cz(0,1))


def test_qasm2_rotations_pi_and_precedence():
    c = load('qreg q[1];rx(-pi/4+2*0.1) q[0];ry(2**3/16) q[0];rz(-(pi/2)) q[0];')
    equivalent(c,Circuit(1).rx(-math.pi/4+.2,0).ry(.5,0).rz(-math.pi/2,0))


def test_qasm2_numeric_math_functions():
    c = load('qreg q[1];ry(sin(pi/2)+sqrt(4)-ln(exp(1))) q[0];')
    assert c.operations[0].params == pytest.approx((2.,))


def test_qasm2_euler_phase_gate_export_is_standard():
    c = Circuit(1).phase(.31,0).u3(.2,.3,.4,0)
    assert 'u1(' in qasm2_dumps(c)
    equivalent(c,qasm2_loads(qasm2_dumps(c)))


def test_qasm2_custom_gate_definition_expands_symbolic_formals():
    c = load('gate ent(theta) a,b {ry(theta/2) a;cx a,b;ry(-theta/2) a;}qreg q[2];ent(pi/3) q[0],q[1];')
    equivalent(c,Circuit(2).ry(math.pi/6,0).cx(0,1).ry(-math.pi/6,0))


def test_qasm2_nested_custom_definitions():
    c = load('gate half(t) a {rx(t/2) a;}gate double(t) a{half(t) a;half(t) a;}qreg q[1];double(.4) q[0];')
    equivalent(c,Circuit(1).rx(.4,0))


def test_qasm2_recursive_gate_is_rejected():
    with pytest.raises(SerializationError,match='Recursive'): load('gate bad a{bad a;}qreg q[1];bad q[0];')


def test_qasm2_opaque_declaration_not_identity():
    assert not load('opaque external a;qreg q[1];').operations
    with pytest.raises(UnsupportedFeature,match='Opaque'): load('opaque external a;qreg q[1];external q[0];')


def test_qasm2_undefined_gate_error_has_location():
    with pytest.raises(UnsupportedFeature) as error: load('qreg q[1];\nmissing q[0];')
    assert error.value.line == 2 and error.value.column == 1 and error.value.to_dict()['format'] == 'qasm2'


def test_qasm2_whole_register_broadcast():
    c = load('qreg q[3];h q;')
    equivalent(c,Circuit(3).h(0).h(1).h(2))


def test_qasm2_two_register_broadcast():
    c = load('qreg a[2];qreg b[2];cx a,b;')
    equivalent(c,Circuit(4).cx(0,2).cx(1,3))


def test_qasm2_broadcast_width_mismatch_rejects():
    with pytest.raises(ParseError,match='broadcast'): load('qreg a[2];qreg b[3];cx a,b;')


def test_qasm2_whole_register_measurement_bit_order():
    c = load('qreg q[3];creg c[3];x q[0];measure q -> c;')
    assert DensityMatrixDevice().run(c).probabilities() == {'100':1.}


def test_qasm2_reset_is_executed_not_ignored():
    c = load('qreg q[1];creg c[1];x q[0];reset q[0];measure q -> c;')
    assert DensityMatrixDevice().run(c).probabilities() == {'0':1.}


def test_qasm2_barrier_survives_roundtrip():
    c = load('qreg q[2];h q[0];barrier q[0],q[1];x q[1];')
    assert [op.name for op in qasm2_loads(qasm2_dumps(c)).operations] == ['h','barrier','x']


def test_qasm2_condition_evaluates_current_register():
    c = load('qreg q[2];creg c[2];x q[0];measure q[0] -> c[0];if(c==1) x q[1];measure q[1] -> c[1];')
    assert DensityMatrixDevice().run(c).probabilities() == {'11':1.}


def test_qasm2_condition_export_and_execution():
    c = Circuit(1,1).x(0).c_if(0,1)
    assert 'if(c==1)' in qasm2_dumps(c)
    assert DensityMatrixDevice().run(qasm2_loads(qasm2_dumps(c))).probabilities() == DensityMatrixDevice().run(c).probabilities()


def test_qasm2_comments_whitespace_and_exponents():
    c = qasm2_loads('/* leading */OPENQASM 2.0; include "qelib1.inc";\nqreg q[1]; // comment\nrx(2.5e-1) q[0];')
    assert c.operations[0].params == (.25,)


def test_qasm2_file_and_text_stream_apis(tmp_path):
    c = Circuit(2).h(0).cx(0,1); path = tmp_path/'roundtrip.qasm'
    qasm2_dump(c,path); equivalent(c,qasm2_load(path))
    stream = io.StringIO(); qasm2_dump(c,stream); stream.seek(0); equivalent(c,qasm2_load(stream))


def test_qasm2_duplicate_names_and_invalid_indices():
    for source in ('qreg q[1];qreg q[1];','qreg q[1];creg q[1];','qreg q[1];x q[1];','qreg q[1];x undefined[0];'):
        with pytest.raises(SerializationError): load(source)


def test_qasm2_global_phase_is_never_silently_dropped():
    c = Circuit(1).h(0); c.global_phase = .3
    with pytest.raises(UnsupportedFeature,match='global_phase'): qasm2_dumps(c)


def test_qasm2_unbound_parameters_and_delay_reject():
    with pytest.raises(UnsupportedFeature): qasm2_dumps(Circuit(1).ry(Parameter('theta'),0))
    with pytest.raises(UnsupportedFeature,match='delay'): qasm2_dumps(Circuit(1).delay(4,0))


def test_qasm2_dynamic_scope_cannot_be_downgraded():
    c = Circuit(1).while_loop(False,Circuit(1).x(0))
    with pytest.raises(UnsupportedFeature): qasm2_dumps(c)


def test_qasm2_sx_algebraic_export_preserves_phase_exactly():
    c = Circuit(1).sx(0).sxdg(0).sx(0)
    equivalent(c,qasm2_loads(qasm2_dumps(c)))


def test_qasm2_strict_include_and_budget_not_bypassed():
    with pytest.raises(UnsupportedFeature): qasm2_loads('OPENQASM 2.0;qreg q[1];h q[0];')
    assert qasm2_loads('OPENQASM 2.0;qreg q[1];h q[0];',strict=False).operations[0].name == 'h'
    with pytest.raises(ResourceLimitError): qasm2_loads(HEADER+'qreg q[10];h q;',limits=SerializationLimits(max_gate_expansion=4),strict=False)
