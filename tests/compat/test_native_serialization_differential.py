# Optional public API interoperability; no upstream implementation/test access.
import io
from uuid import UUID
import numpy as np
import pytest
sdk=pytest.importorskip('qiskit')
from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister,qasm2,qasm3,qpy
from qiskit.circuit import Parameter as SDKParameter
from qiskit.quantum_info import Operator as SDKOperator
from quantumbridge import Circuit,Parameter
from quantumbridge.information import Operator
from quantumbridge.serialization import qasm2_loads,qasm2_dumps,qasm3_loads,qasm3_dumps,qpy_dumps,qpy_loads


SCENARIOS=('bell','phase','rotations','euler','swap','controlled','three_qubit','multiregister','custom_definition','measurements')


def pair(scenario):
    qb,reference=Circuit(3,3),QuantumCircuit(3,3)
    def gate(name,*args):getattr(qb,name)(*args);getattr(reference,'p' if name=='phase' else 'u' if name=='u3' else name)(*args)
    if scenario=='bell':gate('h',0);gate('cx',0,1)
    elif scenario=='phase':gate('h',0);gate('phase',.47,0)
    elif scenario=='rotations':gate('rx',.31,0);gate('ry',-.28,1);gate('rz',.21,2)
    elif scenario=='euler':gate('u3',.23,.31,-.49,0)
    elif scenario=='swap':gate('h',0);gate('swap',0,2);gate('phase',.33,2)
    elif scenario=='controlled':gate('h',0);gate('cy',0,1);gate('cz',1,2)
    elif scenario=='three_qubit':gate('x',0);gate('x',1);gate('ccx',0,1,2);gate('cswap',0,1,2)
    elif scenario=='multiregister':
        reference=QuantumCircuit(QuantumRegister(1,'a'),QuantumRegister(2,'b'),ClassicalRegister(3,'out'))
        reference.h(0);reference.cx(0,2);qb.h(0).cx(0,2)
    elif scenario=='custom_definition':
        definition=QuantumCircuit(2);definition.ry(.27,0);definition.cx(0,1)
        reference.append(definition.to_gate(label='local'),[0,2]);qb.ry(.27,0).cx(0,2)
    else:gate('h',0);gate('cx',0,2);qb.measure(0,2).measure(2,0);reference.measure(0,2);reference.measure(2,0)
    return qb,reference


def equivalent(native,reference):
    measurements=[(reference.find_bit(item.qubits[0]).index,reference.find_bit(item.clbits[0]).index)
        for item in reference.data if item.operation.name=='measure']
    assert [(item.wire,item.bit) for item in native.measurements]==measurements
    if measurements:
        with pytest.raises(ValueError):Operator.from_circuit(native)
    native=native.remove_final_measurements(inplace=False)
    reference=reference.remove_final_measurements(inplace=False)
    np.testing.assert_allclose(Operator.from_circuit(native).data,SDKOperator(reference.reverse_bits()).data,atol=2e-12)


@pytest.mark.parametrize('scenario',SCENARIOS)
def test_qasm2_public_bilateral_interoperability(scenario):
    native,reference=pair(scenario)
    # Explicitly flattened native primitives and actual imported SDK custom definitions.
    actual_sdk=qasm2.loads(qasm2_dumps(native))
    equivalent(native,actual_sdk)
    # Public SDK dumps emits legacy names (p/u/swap/cswap) not defined by strict qelib1.
    # Opt into that dialect explicitly; native exports above remain strict-loadable.
    restored=qasm2_loads(qasm2.dumps(reference),strict=False)
    equivalent(restored,reference)
    if scenario=='measurements':assert [(m.wire,m.bit) for m in restored.measurements]==[(0,2),(2,0)]


@pytest.mark.parametrize('scenario',SCENARIOS)
def test_qasm3_public_bilateral_interoperability(scenario):
    pytest.importorskip('qiskit_qasm3_import')
    native,reference=pair(scenario)
    actual_sdk=qasm3.loads(qasm3_dumps(native))
    equivalent(native,actual_sdk)
    # Qiskit 2.4/2.6 public import/export use the U3 phase convention for builtin U.
    restored=qasm3_loads(qasm3.dumps(reference),dialect='qiskit')
    equivalent(restored,reference)


@pytest.mark.parametrize('scenario',['bell','phase','rotations','controlled','three_qubit','multiregister','measurements','parameter','nonlinear_parameters','symbolic_global_phase'])
def test_qpy_v13_true_binary_bilateral_interoperability(scenario):
    if scenario in {'parameter','nonlinear_parameters','symbolic_global_phase'}:
        p,q=Parameter('p'),Parameter('q');sp,sq=SDKParameter('p'),SDKParameter('q')
        native,reference=Circuit(2,name='symbolic'),QuantumCircuit(2,name='symbolic')
        if scenario=='parameter':native.ry(p,0).rx(q,1);reference.ry(sp,0);reference.rx(sq,1)
        elif scenario=='nonlinear_parameters':native.ry((p+q)*(p-q)+p/2,0);reference.ry((sp+sq)*(sp-sq)+sp/2,0)
        else:native.ry(p,0);native.global_phase=p/3;reference.ry(sp,0);reference.global_phase=sp/3
    else:native,reference=pair(scenario)
    binary=qpy_dumps(native,version=13)
    sdk_restored=qpy.load(io.BytesIO(binary))[0]
    stream=io.BytesIO();qpy.dump(reference,stream,version=13)
    native_restored=qpy_loads(stream.getvalue())[0]
    if reference.parameters:
        mapping={p:.27 if p.name=='p' else -.13 for p in reference.parameters}
        expected=reference.assign_parameters(mapping)
        equivalent(native_restored.bind({p.name:v for p,v in mapping.items()}),expected)
        actual=sdk_restored.assign_parameters({p:.27 if p.name=='p' else -.13 for p in sdk_restored.parameters})
        equivalent(native.bind({p.name:.27 if p.name=='p' else -.13 for p in native.parameters}),actual)
        assert {p.name:p.uuid for p in reference.parameters}=={p.name:UUID(p.uuid) for p in native_restored.parameters}
    else:equivalent(native_restored,reference);equivalent(native,sdk_restored)
    assert binary[:6]==b'QISKIT' and binary[6]==13


def test_qpy_public_multicircuit_names_metadata_and_durations():
    native = [Circuit(1,name='first',metadata={'source':['native',13]}).x(0),Circuit(2,1,name='second').h(0).delay(3,1,unit='dt').measure(0,0)]
    restored = qpy.load(io.BytesIO(qpy_dumps(native)))
    assert [c.name for c in restored] == ['first','second']
    assert restored[0].metadata == {'source':['native',13]}
    assert restored[1].data[1].operation.duration == 3 and restored[1].data[1].operation.unit == 'dt'
    stream = io.BytesIO();qpy.dump(restored,stream,version=13)
    actual = qpy_loads(stream.getvalue())
    assert [c.name for c in actual] == ['first','second']
    assert actual[0].metadata['source'] == ['native',13]
    assert actual[1].operations[1].params == (3,) and actual[1].operations[1].metadata['unit'] == 'dt'
