# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real classical custom i/a records retain operands, not fake unitary meaning."""
import io
from types import SimpleNamespace
import pytest
import quantumbridge as qb
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def api(public=False):
    if not public:return SimpleNamespace(QC=qb.QuantumCircuit,I=qb.Instruction,A=qb.AnnotatedOperation,
        inverse=qb.InverseModifier,control=lambda:qb.ControlModifier(1,0))
    sdk=pytest.importorskip("qiskit")
    from qiskit.circuit import Instruction,AnnotatedOperation,InverseModifier,ControlModifier
    return SimpleNamespace(QC=sdk.QuantumCircuit,I=Instruction,A=AnnotatedOperation,
        inverse=InverseModifier,control=lambda:ControlModifier(1,0))


def deferred(a,kind,modifier):
    if kind=="definition":
        body=a.QC(1,1,name="readout");body.reset(0);body.measure(0,0);base=body.to_instruction()
    else:base=a.I(kind,1,int(kind=="measure"),[])
    owner=a.A(base,getattr(a,modifier)())
    circuit=a.QC(owner.num_qubits,owner.num_clbits,metadata={"global_phase":"user"})
    circuit.append(owner,range(owner.num_qubits),range(owner.num_clbits),copy=False)
    return circuit,owner


@pytest.mark.parametrize("kind",["reset","measure","definition"])
@pytest.mark.parametrize("modifier",["inverse","control"])
def test_deferred_nonunitary_annotation_has_real_classical_abi_and_refuses_unitary_resolution(kind,modifier):
    native,owner=deferred(api(),kind,modifier)
    with pytest.raises(ValueError):qb.resolve_annotated_operation(owner)
    restored=circuit_from_ir(IRProgram.from_json(native.to_ir().to_json()))
    assert restored.operations[0].metadata.get("instruction_clbits",()) == tuple(range(native.num_clbits))
    with pytest.raises(ValueError):restored.lowered()


@pytest.mark.parametrize("kind",["reset","measure","definition"])
@pytest.mark.parametrize("modifier",["inverse","control"])
def test_actual_public_deferred_nonunitary_annotation_construction_abi(kind,modifier):
    native,_=deferred(api(),kind,modifier);public,_=deferred(api(True),kind,modifier)
    assert (native.num_qubits,native.num_clbits,len(native.data[0].clbits)) == (
        public.num_qubits,public.num_clbits,len(public.data[0].clbits))


@pytest.mark.parametrize("kind",["reset","measure","definition"])
@pytest.mark.parametrize("modifier",["inverse","control"])
@pytest.mark.parametrize("direction",["native-to-public","public-to-native"])
def test_real_qpy_bilateral_deferred_nonunitary_annotation_records(kind,modifier,direction):
    pytest.importorskip("qiskit")
    from qiskit import qpy
    source,_=deferred(api(direction=="public-to-native"),kind,modifier)
    if direction=="native-to-public":
        restored=qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        context=restored.data[0];owner=context.operation
        signature=(owner.num_qubits,owner.num_clbits,len(context.clbits))
    else:
        stream=io.BytesIO();qpy.dump(source,stream,version=13)
        restored=qpy_loads(stream.getvalue())[0]
        entry=restored.operations[0];owner=entry.metadata["annotated_operation"]
        signature=(owner.num_qubits,owner.num_clbits,len(entry.metadata.get("instruction_clbits",())))
        with pytest.raises(ValueError):restored.lowered()
    assert signature==(source.num_qubits,source.num_clbits,source.num_clbits)
    assert restored.metadata=={"global_phase":"user"}


def test_classical_custom_instruction_qpy_maps_real_operands_and_runs_four_native_devices():
    source=qb.QuantumCircuit(2,2,name="readout",global_phase=.2)
    source.reset(0);source.x(0);source.measure(0,1)
    parent=qb.QuantumCircuit(3,3);parent.append(source.to_instruction(),[2,0],[1,2])
    restored=qpy_loads(qpy_dumps(parent))[0]
    owner=restored.operations[0].metadata["instruction_object"]
    assert owner.num_clbits==2 and restored.operations[0].metadata["instruction_clbits"]==(1,2)
    assert owner.definition.global_phase==pytest.approx(.2)
    for device in (qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice):
        assert device().run_shots(restored,shots=3).counts()=={"001":3}


def test_custom_classical_qpy_refuses_inconsistent_definition_header():
    from quantumbridge.serialization.qpy import CUSTOM_INSTRUCTION
    from quantumbridge.serialization import FormatValidationError
    source=qb.QuantumCircuit(1,1,name="readout");source.measure(0,0)
    parent=qb.QuantumCircuit(1,1);parent.append(source.to_instruction(),[0],[0])
    wire=bytearray(qpy_dumps(parent))
    # Locate the real named custom record through its serialization-local key.
    marker=wire.index(b"readout_");offset=marker-CUSTOM_INSTRUCTION.size
    values=list(CUSTOM_INSTRUCTION.unpack_from(wire,offset));values[3]=2
    CUSTOM_INSTRUCTION.pack_into(wire,offset,*values)
    with pytest.raises(FormatValidationError):qpy_loads(bytes(wire))
