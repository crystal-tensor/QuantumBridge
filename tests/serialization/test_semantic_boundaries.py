# Counterexamples for silent semantic loss and hostile numeric payloads.
import struct
import numpy as np
import pytest
from quantumbridge import Circuit, Parameter, DensityMatrixDevice
from quantumbridge.serialization import (
    qasm2_loads, qasm3_loads, qasm3_dumps, qpy_dumps, qpy_loads,
    serialize_circuit, deserialize_circuit, SerializationError, UnsupportedFeature,
    FormatValidationError,
)

HEADER = 'OPENQASM 3.0;include "stdgates.inc";'


def test_reserved_constants_cannot_be_shadowed_or_capture_gate_arguments():
    for source in ('const uint[4] pi=2;qubit q;', 'qubit tau;', 'gate local(pi) a {rx(pi) a;}qubit q;'):
        with pytest.raises(SerializationError): qasm3_loads(HEADER+source)


def test_library_names_cannot_be_global_variable_or_parameter_names():
    with pytest.raises(SerializationError): qasm3_loads(HEADER+'input float[64] x;qubit q;rx(x) q;')
    with pytest.raises(UnsupportedFeature): qasm3_dumps(Circuit(1).rx(Parameter('x'),0))


def test_inner_runtime_variable_can_shadow_outer_const_and_be_assigned():
    source = HEADER+'const uint[4] count=1;qubit q;bit c;if(true){uint[4] count=0;count+=1;if(count==1){x q;}}c=measure q;'
    circuit = qasm3_loads(source)
    assert DensityMatrixDevice().run(circuit).probabilities() == {'1':1.}


def test_inner_const_shadows_loop_gate_angle_without_using_outer_parameter():
    source = HEADER+'qubit q;bit c;for int i in {0,1}{const int i=0;ry(pi*i) q;}c=measure q;'
    circuit = qasm3_loads(source)
    assert DensityMatrixDevice().run(circuit).probabilities() == {'0':1.}
    assert DensityMatrixDevice().run(qasm3_loads(qasm3_dumps(circuit))).probabilities() == {'0':1.}


def test_runtime_shadow_of_loop_angle_is_rejected_instead_of_wrongly_bound():
    with pytest.raises(UnsupportedFeature,match='Runtime gate-angle'):
        qasm3_loads(HEADER+'qubit q;for int i in {0,1}{int i=0;ry(i) q;}')


def test_const_declared_width_and_type_are_checked():
    for declaration in ('const uint[2] count=4;', 'const int[2] count=-3;', 'const bool[8] flag=true;', 'const uint[8] count=1.5;'):
        with pytest.raises(SerializationError): qasm3_loads(HEADER+declaration+'qubit q;')


def test_unimplemented_float_and_fixed_angle_widths_are_not_treated_as_float64():
    for declaration in ('input float[32] theta;', 'input angle[32] theta;', 'const angle[8] theta=pi;', 'const float[32] theta=0.1;'):
        with pytest.raises(UnsupportedFeature): qasm3_loads(HEADER+declaration+'qubit q;')


def test_float64_constant_has_actual_gate_semantics():
    circuit = qasm3_loads(HEADER+'const float[64] theta=pi;qubit q;bit c;ry(theta) q;c=measure q;')
    assert DensityMatrixDevice().run(circuit).probabilities()['1'] == pytest.approx(1.)


def test_unused_gate_definitions_cannot_hide_recursion_or_unknown_calls():
    for definition in ('gate local a {local a;}', 'gate a q {b q;}gate b q {a q;}', 'gate local q {unknown q;}'):
        with pytest.raises(SerializationError): qasm2_loads('OPENQASM 2.0;include "qelib1.inc";'+definition+'qreg q[1];')


def test_instruction_metadata_is_not_silently_discarded():
    circuit = Circuit(1).h(0)
    circuit.operations[-1].metadata['purpose'] = 'retain me'
    with pytest.raises(UnsupportedFeature): qasm3_dumps(circuit)
    with pytest.raises(UnsupportedFeature): qpy_dumps(circuit)
    with pytest.warns(UserWarning,match='instruction metadata'):
        assert 'h q[0]' in qasm3_dumps(circuit,allow_metadata_loss=True)


def test_json_metadata_types_do_not_coerce_dictionary_keys_or_tuples():
    for metadata in ({'layout':{0:1}}, {'tuple':(1,2)}):
        circuit = Circuit(1,metadata=metadata).x(0)
        with pytest.raises(UnsupportedFeature): qpy_dumps(circuit)
        restored = deserialize_circuit(serialize_circuit(circuit,'qpy',metadata_policy='external'))
        assert all(restored.metadata[key] == value for key,value in metadata.items())


def test_absent_name_roundtrip_and_invalid_gate_signatures():
    assert qpy_loads(qpy_dumps(Circuit(1)))[0].name is None
    with pytest.raises(FormatValidationError): qpy_dumps(Circuit(2).append('x',(1,),controls=(0,)))
    with pytest.raises(FormatValidationError): qpy_dumps(Circuit(1).append('rx',(0,),params=()))


def test_qpy_labels_survive_gate_and_nonunitary_instruction_payloads():
    circuit = Circuit(1,1).h(0).barrier().delay(3,0,unit='dt').measure(0,0)
    for index,item in enumerate(circuit.iter_instructions()): item.metadata['label'] = 'event'+str(index)
    restored = qpy_loads(qpy_dumps(circuit))[0]
    assert [item.metadata.get('label') for item in restored.iter_instructions()] == ['event0','event1','event2','event3']


def test_numeric_power_budget_prevents_exponential_integer_allocation():
    with pytest.raises(SerializationError): qasm3_loads(HEADER+'qubit q;gphase((2**4096)**4096);')
    from quantumbridge.serialization.qpy import Reader
    from quantumbridge.serialization.limits import SerializationLimits
    from quantumbridge.serialization.qpy_expressions import RECORD,read_expression
    record = RECORD.pack(4,b'i',bytes(8)+struct.pack('!q',2),b'i',bytes(8)+struct.pack('!q',2**62))
    reader = Reader(struct.pack('!QQ',0,len(record))+record,SerializationLimits())
    with pytest.raises(SerializationError,match='budget'): read_expression(reader)


def test_legacy_branch_snapshot_survives_overwritten_condition_and_else():
    body = Circuit(2,2).reset(0).measure(0,0).x(1)
    circuit = Circuit(2,2).x(0).measure(0,0).if_else((0,1),body,Circuit(2,2).z(1))
    circuit.measure(1,1)
    restored = qasm3_loads(qasm3_dumps(circuit))
    assert DensityMatrixDevice().run(circuit).probabilities() == {'01':1.}
    assert DensityMatrixDevice().run(restored).probabilities() == {'01':1.}


def test_nested_legacy_condition_and_per_gate_condition_roundtrip():
    inner = Circuit(2,2).if_else((1,0),Circuit(2,2).x(1),Circuit(2,2).z(1))
    circuit = Circuit(2,2).x(0).measure(0,0).if_test((0,1),inner)
    circuit.measure(1,1)
    restored = qasm3_loads(qasm3_dumps(circuit))
    assert DensityMatrixDevice().run(circuit).probabilities() == DensityMatrixDevice().run(restored).probabilities()


def test_legacy_repeated_block_ids_keep_separate_entry_snapshots():
    block = Circuit(1,1).if_test((0,1),Circuit(1,1).reset(0).measure(0,0))
    circuit = Circuit(1,1).x(0).measure(0,0).compose(block).x(0).measure(0,0).compose(block)
    restored = qasm3_loads(qasm3_dumps(circuit))
    assert DensityMatrixDevice().run(restored).probabilities() == {'0':1.}


def test_qasm3_builtin_u_standard_phase_and_explicit_sdk_dialect():
    from quantumbridge.information import Operator
    source = HEADER+'qubit q;U(0.3,0.4,0.5) q;'
    standard, sdk = qasm3_loads(source),qasm3_loads(source,dialect='qiskit')
    expected = Operator.from_circuit(Circuit(1).u3(.3,.4,.5,0)).data
    np.testing.assert_allclose(Operator.from_circuit(standard).data,np.exp(.6j)*expected,atol=1e-12)
    np.testing.assert_allclose(Operator.from_circuit(sdk).data,expected,atol=1e-12)
    np.testing.assert_allclose(Operator.from_circuit(qasm3_loads(qasm3_dumps(standard))).data,np.exp(.6j)*expected,atol=1e-12)


def test_standard_library_does_not_reserve_unrelated_native_instruction_names():
    circuit = qasm3_loads(HEADER+'gate rxx(theta) a,b {rx(theta) a;rx(theta) b;}qubit[2] q;rxx(pi) q[0],q[1];')
    assert [op.name for op in circuit.operations] == ['rx','rx']
    with pytest.raises(UnsupportedFeature):qasm3_loads(HEADER+'qubit[2] q;rxx(pi) q[0],q[1];')


def test_non_dt_qpy_delay_is_rejected_rather_than_loaded_with_wrong_units():
    circuit = Circuit(1).delay(3,0,unit='ns')
    with pytest.raises(UnsupportedFeature,match='non-dt'):qpy_dumps(circuit)
    assert qasm3_loads(qasm3_dumps(circuit)).operations[0].metadata['unit'] == 'ns'


def test_qos_artifact_retains_external_native_metadata_and_validates_real_source():
    from quantumbridge.compat.qos_uqci.openqasm_bridge import build_openqasm_compatibility_artifact,validate_openqasm_compatibility_artifact
    artifact = build_openqasm_compatibility_artifact(Circuit(1,name='local',metadata={'provenance':'test'}).h(0))
    assert artifact['external_native_metadata']['name'] == 'local'
    assert artifact['external_native_metadata']['metadata']['provenance'] == 'test'
    assert validate_openqasm_compatibility_artifact(artifact)
    with pytest.raises(SerializationError):validate_openqasm_compatibility_artifact({**artifact,'qasm':'OPENQASM 2.0; invalid; '})


def test_qpy_conflicting_name_uuid_identity_is_rejected_before_binary_output():
    first = Parameter('theta','00000000-0000-0000-0000-000000000001')
    second = Parameter('theta','00000000-0000-0000-0000-000000000002')
    with pytest.raises(UnsupportedFeature,match='uniquely'):qpy_dumps(Circuit(1).ry(first+second,0))
    other = Parameter('phi',first.uuid)
    with pytest.raises(UnsupportedFeature,match='uniquely'):qpy_dumps(Circuit(1).ry(first,0).rx(other,0))


def test_noncomputational_measurement_is_not_misrepresented_as_z_measure():
    from quantumbridge.core import Measurement
    circuit = Circuit(1,1)
    circuit.measurements.append(Measurement(0,0,kind='unsupported-basis'))
    with pytest.raises(UnsupportedFeature):qpy_dumps(circuit)
    with pytest.raises(UnsupportedFeature):qasm3_dumps(circuit)
