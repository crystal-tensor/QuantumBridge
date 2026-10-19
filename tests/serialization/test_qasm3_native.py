# Real typed source programs are parsed and executed by native devices.
import io
import math
import numpy as np
import pytest
from quantumbridge import Circuit, Parameter, StatevectorDevice, DensityMatrixDevice
from quantumbridge.serialization import (qasm3_loads,qasm3_dumps,qasm3_load,qasm3_dump,
    SerializationError,UnsupportedFeature,ParseError,serialize_circuit,deserialize_circuit)
from quantumbridge.information import Operator

HEADER = 'OPENQASM 3.0;include "stdgates.inc";'


def run(body,version='3.0'):
    c = qasm3_loads(f'OPENQASM {version};include "stdgates.inc";'+body)
    device = DensityMatrixDevice()
    return c,device.run(c).probabilities()


@pytest.mark.parametrize('name,body,expected',[
    ('measurement_true','qubit[2] q;bit[2] c;x q[0];c[0]=measure q[0];if(c[0]){x q[1];}c=measure q;',{'11':1.}),
    ('measurement_false','qubit q;bit c;c=measure q;if(c){x q;}',{'0':1.}),
    ('if_else','qubit q;bit c;bool flag=false;if(flag){z q;}else{x q;}c=measure q;',{'1':1.}),
    ('nested_if','qubit q;bit c;bool a=true;uint[3] n=2;if(a){if(n==2){x q;}}c=measure q;',{'1':1.}),
    ('runtime_while','qubit q;bit c;uint[3] n=0;while(n<3){x q;n+=1;}c=measure q;',{'1':1.}),
    ('feedback_while','qubit q;bit c;x q;c=measure q;while(c){reset q;c=measure q;}',{'0':1.}),
    ('for_inclusive','qubit q;bit c;for uint[4] i in [0:2]{x q;}c=measure q;',{'1':1.}),
    ('for_step','qubit q;bit c;for int i in [0:2:4]{x q;}c=measure q;',{'1':1.}),
    ('for_angle','qubit q;bit c;for int i in {0,1,2}{ry(pi*i) q;}c=measure q;',{'1':1.}),
    ('break','qubit q;bit c;for uint i in [0:4]{x q;break;x q;}c=measure q;',{'1':1.}),
    ('continue','qubit q;bit c;for uint i in [0:2]{x q;continue;x q;}c=measure q;',{'1':1.}),
    ('counter_store','qubit q;bit c;uint[4] n=0;for uint i in {1,2,3}{n=n+1;}if(n==3){x q;}c=measure q;',{'1':1.}),
    ('shadowing','qubit q;bit c;uint[3] n=1;if(true){uint[3] n=2;if(n==2){x q;}}if(n==1){z q;}c=measure q;',{'1':1.}),
    ('signed_counter','qubit q;bit c;int[4] n=-2;while(n<0){n+=1;}if(n==0){x q;}c=measure q;',{'1':1.}),
])
def test_qasm3_dynamic_source_roundtrip_execute(name,body,expected):
    original,probabilities = run(body)
    labels = set(probabilities)|set(expected)
    np.testing.assert_allclose([probabilities.get(key,0) for key in labels],[expected.get(key,0) for key in labels],atol=1e-12)
    restored = qasm3_loads(qasm3_dumps(original))
    a,b = DensityMatrixDevice().run(original).probabilities(),DensityMatrixDevice().run(restored).probabilities()
    labels = set(a)|set(b)
    np.testing.assert_allclose([a.get(key,0) for key in labels],[b.get(key,0) for key in labels],atol=1e-12)
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(original),DensityMatrixDevice().density_matrix(restored),atol=1e-12)


def test_qasm3_scalar_and_array_declarations():
    c,p = run('qubit a;qubit[2] b;bit ca;bit[2] cb;x b[1];ca=measure a;cb=measure b;')
    assert (c.num_qubits,c.num_bits) == (3,3) and p == {'001':1.}


def test_qasm3_input_real_parameter_ast():
    c = qasm3_loads(HEADER+'input float[64] theta;qubit q;ry(theta*theta+2*theta) q;')
    assert [p.name for p in c.parameters] == ['theta']
    np.testing.assert_allclose(StatevectorDevice().statevector(c.bind({'theta':.2})),StatevectorDevice().statevector(Circuit(1).ry(.44,0)),atol=1e-12)


def test_qasm3_global_phase_operator_fidelity():
    c = qasm3_loads(HEADER+'input float[64] theta;qubit q;gphase(theta/2);rx(theta) q;')
    restored = qasm3_loads(qasm3_dumps(c))
    np.testing.assert_allclose(Operator.from_circuit(c.bind({'theta':.4})).data,Operator.from_circuit(restored.bind({'theta':.4})).data,atol=1e-12)


def test_qasm3_delay_is_instruction_not_comment():
    c = qasm3_loads(HEADER+'qubit q;delay[12ns] q;barrier q;x q;')
    source = qasm3_dumps(c)
    assert 'delay[12ns]' in source and [op.name for op in qasm3_loads(source).operations] == ['delay','barrier','x']


def test_qasm3_const_expression_controls_register_size():
    c = qasm3_loads(HEADER+'const uint[8] n=2;qubit[n+1] q;x q[2];')
    assert c.num_qubits == 3 and c.operations[0].targets == (2,)


def test_qasm3_explicit_classical_cast():
    _,p = run('qubit q;bit c;uint[3] n=2;bool b=bool(n);if(b){x q;}c=measure q;')
    assert p == {'1':1.}


def test_qasm3_bitwise_logical_expressions():
    _,p = run('qubit q;bit c;uint[3] n=5;bool a=((n&1)==1)&&!(n==0);if(a){x q;}c=measure q;')
    assert p == {'1':1.}


def test_qasm3_custom_gate_parameter_source():
    c = qasm3_loads(HEADER+'gate ent(t) a,b {ry(t) a;cx a,b;}qubit[2] q;ent(pi/3) q[0],q[1];')
    np.testing.assert_allclose(Operator.from_circuit(c).data,Operator.from_circuit(Circuit(2).ry(math.pi/3,0).cx(0,1)).data,atol=1e-12)


def test_qasm3_switch_case_and_default_standard_31():
    c,p = run('qubit q;bit c;int[4] n=-1;switch(n){case 0,2{z q;}case -1{x q;}default{h q;}}c=measure q;',version='3.1')
    assert p == {'1':1.}
    restored = qasm3_loads(qasm3_dumps(c,version='3.1'))
    assert DensityMatrixDevice().run(restored).probabilities() == p
    with pytest.raises(UnsupportedFeature): qasm3_dumps(c,version='3.0')


def test_qasm3_while_false_is_not_statically_executed():
    c,p = run('qubit q;bit c;uint[2] n=0;while(n>0){x q;n-=1;}c=measure q;')
    assert p == {'0':1.} and any(op.metadata.get('control_node') and op.metadata['control_node'].kind == 'while' for op in c.operations)


def test_qasm3_loop_runtime_nontermination_is_bounded():
    from quantumbridge.core.control_flow import ExecutionLimits
    c = qasm3_loads(HEADER+'qubit q;while(true){x q;}')
    with pytest.raises(ValueError,match='max_loop_iterations'): DensityMatrixDevice(execution_limits=ExecutionLimits(max_loop_iterations=3)).run(c)


def test_qasm3_scope_does_not_leak_variables():
    with pytest.raises(ParseError,match='Undefined'): qasm3_loads(HEADER+'qubit q;if(true){uint[3] inner=1;}if(inner==1){x q;}')


def test_qasm3_reassignment_to_const_is_rejected():
    with pytest.raises(ParseError,match='const'): qasm3_loads(HEADER+'const uint[3] n=1;qubit q;n=2;')


def test_qasm3_duplicate_declarations_and_cases_reject():
    with pytest.raises(ParseError): qasm3_loads(HEADER+'qubit q;bool a=true;bool a=false;')
    with pytest.raises(SerializationError): qasm3_loads(HEADER.replace('3.0','3.1')+'qubit q;uint[3] n=1;switch(n){case 1{}case 1{}}')


def test_qasm3_file_stream_apis(tmp_path):
    c = Circuit(1).rx(.3,0); path=tmp_path/'source.qasm'
    qasm3_dump(c,path)
    np.testing.assert_allclose(Operator.from_circuit(qasm3_load(path)).data,Operator.from_circuit(c).data)
    stream = io.StringIO();qasm3_dump(c,stream);stream.seek(0)
    assert qasm3_load(stream).operations[0].params == (.3,)


def test_qasm3_unsupported_nodes_are_not_dropped():
    for source in ('defcal x q {}','box {x q;}','stretch t;','extern f(int)->int;','array[int,2] a;'):
        with pytest.raises(SerializationError): qasm3_loads(HEADER+'qubit q;'+source)


def test_qasm3_malformed_source_locations():
    with pytest.raises(SerializationError) as error: qasm3_loads(HEADER+'qubit q;\nif(true){x q;')
    assert error.value.line == 2 and error.value.column > 1


def test_qasm3_metadata_loss_requires_explicit_external_sidecar():
    c = Circuit(1,name='named',metadata={'custom':'value'}).h(0)
    with pytest.raises(UnsupportedFeature,match='metadata'): qasm3_dumps(c)
    artifact = serialize_circuit(c,'qasm3',metadata_policy='external')
    assert 'custom' not in artifact.data and artifact.sidecar['metadata']['custom'] == 'value'
    restored = deserialize_circuit(artifact)
    assert restored.name == 'named' and restored.metadata['custom'] == 'value'


def test_qasm3_parameter_uuid_not_falsely_standard_field():
    p = Parameter('theta','00000000-0000-0000-0000-000000000001')
    c = Circuit(1).ry(p,0)
    with pytest.raises(UnsupportedFeature,match='UUID'): qasm3_dumps(c)
    restored = deserialize_circuit(serialize_circuit(c,'qasm3',metadata_policy='external'))
    assert restored.parameters[0].uuid == p.uuid
