# Binary protocol tests use the native codec, not an SDK reader/writer.
import io
import struct
import numpy as np
import pytest
from quantumbridge import Circuit, Parameter, StatevectorDevice
from quantumbridge.information import Operator
from quantumbridge.ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import (qpy_dumps,qpy_loads,qpy_dump,qpy_load,qpy_get_version,
    SerializationLimits,SerializationError,UnsupportedVersion,UnsupportedFeature,ResourceLimitError)
from quantumbridge.serialization.qpy import FILE_HEADER,CIRCUIT_HEADER,LAYOUT,INSTRUCTION


def equivalent(a,b): np.testing.assert_allclose(Operator.from_circuit(a).data,Operator.from_circuit(b).data,atol=1e-12)


def test_qpy_binary_versioned_header_and_non_json_instructions():
    data = qpy_dumps(Circuit(2).h(0).cx(0,1))
    assert data[:6] == b'QISKIT' and data[6] == 13 and data[19:20] == b'q'
    assert b'HGate' in data and b'CXGate' in data
    assert b'"instructions"' not in data


def test_qpy_named_circuit_and_metadata_roundtrip():
    c = Circuit(1,name='named',metadata={'notes':['independent',3],'valid':True}).h(0)
    r = qpy_loads(qpy_dumps(c))[0]
    assert r.name == c.name and r.metadata['notes'] == c.metadata['notes']
    equivalent(c,r)


def test_qpy_multiple_circuits_no_padding():
    circuits = [Circuit(1,name='one').x(0),Circuit(3,name='three').h(0).cx(0,2)]
    restored = qpy_loads(qpy_dumps(circuits))
    assert [c.name for c in restored] == ['one','three']
    for a,b in zip(circuits,restored): equivalent(a,b)


def test_qpy_quantum_classical_register_mapping():
    c = Circuit(3,2,metadata={'registers':[{'kind':'q','name':'a','bits':[0]},{'kind':'q','name':'b','bits':[1,2]},{'kind':'c','name':'bits','bits':[0,1]}]}).x(2).measure(2,0)
    r = qpy_loads(qpy_dumps(c))[0]
    assert r.metadata['registers'] == c.metadata['registers'] and r.measurements[0].wire == 2


def test_qpy_instruction_order_measurement_barrier_reset_delay():
    c = Circuit(2,2).h(0).measure(0,1).barrier().reset(0).delay(3,1,unit='dt').x(1).measure(1,0)
    r = qpy_loads(qpy_dumps(c))[0]
    assert [type(item).__name__ for item in c.iter_instructions()] == [type(item).__name__ for item in r.iter_instructions()]
    assert [op.name for op in c.operations] == [op.name for op in r.operations]
    assert [(m.wire,m.bit) for m in r.measurements] == [(0,1),(1,0)]


def test_qpy_all_supported_basic_gate_signatures():
    c = Circuit(3).sx(0).sxdg(1).h(2).rx(.1,0).ry(.2,1).rz(.3,2).phase(.4,0).u3(.2,.3,.4,0)
    c.cx(0,1).cy(1,2).cz(0,2).ch(0,1).swap(1,2).ccx(0,1,2).cswap(0,1,2)
    c.crx(.2,0,1).cry(.3,0,1).crz(.4,0,1).cp(.5,0,1).rxx(.2,0,2).ryy(.3,0,2).rzz(.4,0,2)
    equivalent(c,qpy_loads(qpy_dumps(c))[0])


def test_qpy_numeric_global_phase_is_dedicated_binary_field():
    c = Circuit(1).h(0);c.global_phase=.417
    r = qpy_loads(qpy_dumps(c))[0]
    assert r.global_phase == c.global_phase
    equivalent(c.control(),r.control())


def test_qpy_parameter_uuid_survives_and_ir_preserves_it():
    p = Parameter('theta','a31d7737-bb6c-4632-8bb6-c0655072af55')
    c = Circuit(1).ry(p,0)
    r = qpy_loads(qpy_dumps(c))[0]
    assert r.parameters[0].uuid == p.uuid
    ir = circuit_from_ir(IRProgram.from_json(r.to_ir().to_json()))
    assert ir.parameters[0].uuid == p.uuid


def test_qpy_shared_and_nonlinear_arithmetic_replay():
    p,q = Parameter('p'),Parameter('q')
    c = Circuit(2).ry((p+q)*(p-q)+p/2,0).rx(p**2-2*q,1).cx(0,1)
    r = qpy_loads(qpy_dumps(c))[0]
    equivalent(c.bind({'p':.3,'q':-.2}),r.bind({'p':.3,'q':-.2}))


def test_qpy_symbolic_global_phase():
    p = Parameter('p');c=Circuit(1).ry(p,0);c.global_phase=p/3
    r=qpy_loads(qpy_dumps(c))[0]
    equivalent(c.bind({'p':.7}).control(),r.bind({'p':.7}).control())


def test_qpy_file_and_binary_stream_apis(tmp_path):
    path=tmp_path/'real.qpy';c=Circuit(1,name='file').rx(.2,0)
    qpy_dump(c,path);equivalent(c,qpy_load(path)[0])
    stream=io.BytesIO();qpy_dump(c,stream);stream.seek(0)
    assert qpy_get_version(stream)==13 and stream.tell()==0
    equivalent(c,qpy_load(stream)[0])
    assert qpy_get_version(path)==13


def test_qpy_format_version_is_not_sdk_version():
    c=Circuit(1).x(0)
    for version in (1,12,14,17,18):
        with pytest.raises(UnsupportedVersion):qpy_dumps(c,version=version)
    payload=bytearray(qpy_dumps(c));payload[6]=18
    with pytest.raises(UnsupportedVersion):qpy_loads(payload)


def test_qpy_truncation_at_each_binary_boundary():
    payload=qpy_dumps(Circuit(1).h(0))
    for length in (0,6,18,20,40,len(payload)-1):
        with pytest.raises(SerializationError):qpy_loads(payload[:length])


def test_qpy_invalid_magic_symbol_encoding_and_program_tag():
    payload=qpy_dumps(Circuit(1).x(0))
    for offset,value in ((0,0),(18,ord('e')),(19,ord('s'))):
        corrupt=bytearray(payload);corrupt[offset]=value
        with pytest.raises(SerializationError):qpy_loads(corrupt)


def test_qpy_corrupt_counts_and_trailing_bytes():
    payload=qpy_dumps(Circuit(1).x(0))
    corrupt=payload[:10]+struct.pack('!Q',2**63)+payload[18:]
    with pytest.raises(ResourceLimitError):qpy_loads(corrupt)
    with pytest.raises(SerializationError):qpy_loads(payload+b'garbage')


def test_qpy_limits_apply_to_writer_reader_and_generator():
    c=Circuit(1).x(0).x(0)
    with pytest.raises(ResourceLimitError):qpy_dumps(c,limits=SerializationLimits(max_instructions=1))
    with pytest.raises(ResourceLimitError):qpy_loads(qpy_dumps(c),limits=SerializationLimits(max_instructions=1))
    with pytest.raises(ResourceLimitError):qpy_dumps((Circuit(1) for _ in range(20)),limits=SerializationLimits(max_circuits=2))
    with pytest.raises(ResourceLimitError):qpy_dumps(c,limits=SerializationLimits(max_input_bytes=20))


def test_qpy_unsupported_dynamic_and_non_json_objects_reject():
    with pytest.raises(UnsupportedFeature):qpy_dumps(Circuit(1).if_else(True,Circuit(1).x(0)))
    with pytest.raises(UnsupportedFeature):qpy_dumps(Circuit(1,metadata={'bad':object()}))


def test_qpy_symbolic_depth_limit():
    p=Parameter('p');expr=p
    for _ in range(8):expr=expr+1
    with pytest.raises(ResourceLimitError):qpy_dumps(Circuit(1).ry(expr,0),limits=SerializationLimits(max_symbolic_expression_depth=4))
