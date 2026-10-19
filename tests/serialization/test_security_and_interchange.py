# Adversarial input must fail without executing code or opening includes.
import io
import struct
import numpy as np
import pytest
from quantumbridge import Circuit,Parameter,PauliZ,Hamiltonian,StatevectorDevice,MatrixProductStateDevice
from quantumbridge.qml import QNode
from quantumbridge.compiler import Target,CouplingMap,native_transpile
from quantumbridge.serialization import *


def test_network_and_traversal_includes_are_never_read(monkeypatch):
    import pathlib
    def forbidden(*args,**kwargs): raise AssertionError('Parser opened a file.')
    monkeypatch.setattr(pathlib.Path,'open',forbidden)
    for name in ('../../.env','/etc/passwd','https://example.test/a.inc','safe.inc'):
        for strict in (True,False):
            with pytest.raises(UnsafeInputError): qasm3_loads(f'OPENQASM 3.0;include "{name}";qubit q;',strict=strict)


def test_code_like_source_never_executes():
    for source in ('__import__("os");','eval("1");','exec("1");'):
        with pytest.raises(SerializationError): qasm3_loads('OPENQASM 3.0;qubit q;'+source)


def test_input_byte_and_token_limits_are_early():
    source='OPENQASM 3.0;qubit q;'
    with pytest.raises(ResourceLimitError):qasm3_loads(source,limits=SerializationLimits(max_input_bytes=10))
    with pytest.raises(ResourceLimitError):qasm3_loads(source,limits=SerializationLimits(max_tokens=3))


def test_ast_expression_and_control_nesting_limits():
    with pytest.raises(ResourceLimitError):qasm3_loads('OPENQASM 3.0;qubit q;',limits=SerializationLimits(max_ast_nodes=1))
    with pytest.raises(ResourceLimitError):qasm3_loads('OPENQASM 3.0;qubit q;gphase('+('('*10)+'1'+(')'*10)+');',limits=SerializationLimits(max_expression_depth=3))
    with pytest.raises(ResourceLimitError):qasm3_loads('OPENQASM 3.0;qubit q;if(true){if(true){if(true){}}}',limits=SerializationLimits(max_nesting_depth=2))


def test_gate_expansion_and_broadcast_are_bounded():
    source='OPENQASM 2.0;include "qelib1.inc";gate a q{x q;x q;}qreg q[4];a q;'
    with pytest.raises(ResourceLimitError):qasm2_loads(source,limits=SerializationLimits(max_gate_expansion=5))
    with pytest.raises(ResourceLimitError):qasm2_loads(source,limits=SerializationLimits(max_instructions=3))


def test_register_and_loop_construction_limits():
    with pytest.raises(ResourceLimitError):qasm3_loads('OPENQASM 3.0;qubit[100000] q;')
    with pytest.raises(ResourceLimitError):qasm3_loads('OPENQASM 3.0;qubit q;for int i in [0:100000]{}')
    with pytest.raises(SerializationError):qasm3_loads('OPENQASM 3.0;qubit q;for int i in [0:0:2]{}')


def test_nonfinite_arithmetic_and_dangerous_exponents():
    for value in ('1e999','1/0','2**1000000'):
        with pytest.raises(SerializationError):qasm3_loads('OPENQASM 3.0;qubit q;gphase('+value+');')


def test_qpy_bad_lengths_do_not_allocate_declared_buffers():
    from quantumbridge.serialization.qpy import FILE_HEADER,CIRCUIT_HEADER
    valid=qpy_dumps(Circuit(1).x(0)); start=FILE_HEADER.size+1
    fields=list(CIRCUIT_HEADER.unpack_from(valid,start));fields[5]=2**63
    corrupt=valid[:start]+CIRCUIT_HEADER.pack(*fields)+valid[start+CIRCUIT_HEADER.size:]
    with pytest.raises(ResourceLimitError):qpy_loads(corrupt)


def test_qpy_unknown_instruction_never_becomes_identity():
    valid=qpy_dumps(Circuit(1).h(0))
    with pytest.raises(UnsupportedFeature):qpy_loads(valid.replace(b'HGate',b'Zzzzz'))


def test_qpy_corrupt_layout_not_discarded():
    from quantumbridge.serialization.qpy import LAYOUT
    valid=qpy_dumps(Circuit(1).x(0))
    corrupt=valid[:-LAYOUT.size]+LAYOUT.pack(b'\x01',1,1,1,0,1)
    with pytest.raises(UnsupportedFeature):qpy_loads(corrupt)


def test_qpy_stream_mode_and_invalid_limits():
    with pytest.raises(FormatValidationError):qpy_load(io.StringIO('not binary'))
    with pytest.raises(ValueError):SerializationLimits(max_circuits=0)
    with pytest.raises(ValueError):SerializationLimits(max_tokens=True)


def test_cross_format_standard_payloads_and_external_metadata():
    c=Circuit(2).h(0).cx(0,1)
    two=serialize_circuit(c,'qasm2')
    binary=convert_circuit_format(two,'qasm2','qpy')
    assert isinstance(binary.data,bytes) and binary.data[:6] == b'QISKIT'
    three=convert_circuit_format(binary,'qpy','qasm3',target_options={'metadata_policy':'external'})
    assert validate_serialization_roundtrip(deserialize_circuit(three),'qasm3',metadata_policy='external',verify_execution=True)['execution_checked']
    with pytest.raises(FormatValidationError):deserialize_circuit(two,'qpy')


def test_dynamic_qasm3_cannot_silently_convert_to_qasm2():
    source='OPENQASM 3.0;include "stdgates.inc";qubit q;uint[3] i=0;while(i<2){x q;i+=1;}'
    with pytest.raises(UnsupportedFeature):convert_circuit_format(source,'qasm3','qasm2')


def test_ir_json_and_qasm3_semantic_roundtrip():
    c=Circuit(1).h(0).rx(.31,0)
    encoded=serialize_circuit(c,'ir-json')
    source=convert_circuit_format(encoded,'ir-json','qasm3')
    assert validate_serialization_roundtrip(deserialize_circuit(source),verify_execution=True)['execution_checked']
    with pytest.raises(FormatValidationError):deserialize_circuit('{','ir-json')


@pytest.mark.parametrize('scenario',['rx','ry','rz','shared','nonlinear','entangled_hamiltonian'])
@pytest.mark.parametrize('format',['qpy','qasm3'])
def test_serialized_circuit_restored_qnode_gradients(scenario,format):
    p=Parameter('theta'); c=Circuit(2)
    if scenario in {'rx','ry'}:getattr(c,scenario)(p,0)
    elif scenario=='rz':c.h(0).rz(p,0)
    elif scenario=='shared':c.ry(p,0).rx(2*p,1)
    elif scenario=='nonlinear':c.ry(p*p+2*p,0)
    else:c.ry(p,0).cx(0,1).rx(p/3,1)
    observable=Hamiltonian([(1.,PauliZ(0)),(.4,PauliZ(1))])
    restored=deserialize_circuit(serialize_circuit(c,format))
    original,roundtripped=QNode.from_circuit(c,observable),QNode.from_circuit(restored,observable)
    assert original(.37)==pytest.approx(roundtripped(.37),abs=1e-12)
    for method in ('adjoint','parameter-shift'):
        assert original.gradient(.37,method=method)==pytest.approx(roundtripped.gradient(.37,method=method),abs=1e-11)


@pytest.mark.parametrize('format',['qpy','qasm3'])
def test_compiled_parameters_layout_phase_and_schedule_preserved_externally(format):
    p=Parameter('theta');c=Circuit(3,3).h(0).ry(p,1).cx(0,2).measure(0,2).measure(1,1).measure(2,0)
    target=Target(3,('rz','sx','x','cx'),[(0,1),(1,2)],dt=1e-9,durations={'rz':0.,'sx':4e-9,'x':8e-9,'cx':12e-9,'measure':8e-9})
    compiled=native_transpile(c,target=target,optimization_level=0,scheduling_method='asap')
    artifact=serialize_circuit(compiled,format,metadata_policy='external')
    restored=deserialize_circuit(artifact)
    assert restored.metadata['initial_layout']==compiled.metadata['initial_layout']
    assert restored.metadata['schedule']==compiled.metadata['schedule']
    assert [(m.wire,m.bit) for m in restored.measurements]==[(m.wire,m.bit) for m in compiled.measurements]
    np.testing.assert_allclose(StatevectorDevice().statevector(restored.bind({'theta':.31})),StatevectorDevice().statevector(compiled.bind({'theta':.31})),atol=1e-12)
    assert artifact.sidecar and ('schedule' not in artifact.data if isinstance(artifact.data,str) else b'"schedule"' not in artifact.data)


@pytest.mark.parametrize('format',['qpy','qasm3'])
def test_hundred_qubit_mps_roundtrip_never_expands_dense(format,monkeypatch):
    from quantumbridge.information import MatrixProductState
    def forbidden(*args,**kwargs):raise AssertionError('Dense expansion forbidden.')
    monkeypatch.setattr(MatrixProductState,'statevector',forbidden)
    monkeypatch.setattr(StatevectorDevice,'statevector',forbidden)
    c=Circuit(100).h(0)
    for wire in range(99):c.cx(wire,wire+1)
    restored=deserialize_circuit(serialize_circuit(c,format))
    result=MatrixProductStateDevice().run(restored)
    assert restored.num_qubits==100 and len(restored.operations)==100
    assert result.mps.peak_bond_dimension==2 and max(result.mps.bond_dimensions)==2
    assert MatrixProductStateDevice().expectation(restored,PauliZ(99))==pytest.approx(0,abs=1e-12)
