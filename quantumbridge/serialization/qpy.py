# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent public QPY v13 binary protocol implementation, not an SDK wrapper.

import io
import json
import math
import struct
from uuid import UUID, uuid5, NAMESPACE_URL
from numbers import Real, Integral

from quantumbridge.core import Circuit, Operation, Measurement, Parameter, ParameterExpression, ParameterVector, ParameterVectorElement
from quantumbridge.core.control_flow import validate_control_flow
from .limits import SerializationLimits
from .errors import SerializationError, FormatValidationError, UnsupportedFeature, UnsupportedVersion, ResourceLimitError
from .common import read_input, write_output, register_specs, BoundedParts

QPY_VERSION = 13
FILE_HEADER = struct.Struct("!6sBBBBQc")
CIRCUIT_HEADER = struct.Struct("!HcHIIQIQI")
REGISTER = struct.Struct("!c?IH?")
INSTRUCTION = struct.Struct("!HHHIIBHqII")
VALUE = struct.Struct("!cQ")
LAYOUT = struct.Struct("!ciiiIi")
OPS = {"id":("IGate",1,0), "x":("XGate",1,0), "y":("YGate",1,0), "z":("ZGate",1,0),
       "h":("HGate",1,0), "s":("SGate",1,0), "sdg":("SdgGate",1,0), "t":("TGate",1,0),
       "tdg":("TdgGate",1,0), "sx":("SXGate",1,0), "sxdg":("SXdgGate",1,0),
       "rx":("RXGate",1,1), "ry":("RYGate",1,1), "rz":("RZGate",1,1),
       "phase":("PhaseGate",1,1), "u":("UGate",1,3), "u1":("U1Gate",1,1),
       "u2":("U2Gate",1,2), "u3":("U3Gate",1,3),
       "cx":("CXGate",2,0), "cy":("CYGate",2,0), "cz":("CZGate",2,0), "ch":("CHGate",2,0),
       "crx":("CRXGate",2,1), "cry":("CRYGate",2,1), "crz":("CRZGate",2,1), "cp":("CPhaseGate",2,1),
       "swap":("SwapGate",2,0), "ccx":("CCXGate",3,0), "cswap":("CSwapGate",3,0),
       "rxx":("RXXGate",2,1), "ryy":("RYYGate",2,1), "rzz":("RZZGate",2,1),
       "reset":("Reset",1,0), "measure":("Measure",1,0), "barrier":("Barrier",None,0), "delay":("Delay",1,1)}
NAMES = {value[0]:name for name,value in OPS.items()}
CONTROLS = {"cx":1,"cy":1,"cz":1,"ch":1,"crx":1,"cry":1,"crz":1,"cp":1,"ccx":2,"cswap":1}


class Reader:
    def __init__(self,data,limits,base=0,depth=0,budget=None):
        self.data, self.pos, self.limits, self.base = memoryview(data), 0, limits, base
        self.instructions = 0
        self.parameters = {}
        self.vectors = {}
        self.depth,self.budget = depth,({"values":0} if budget is None else budget)
        self.bounded("max_nesting_depth",depth)

    def error(self,reason,cls=FormatValidationError):
        raise cls(reason,format="qpy",version=13,offset=self.base+self.pos)

    def take(self,size):
        if not isinstance(size,int) or size < 0 or size > len(self.data)-self.pos: self.error("Truncated or invalid binary payload length.")
        start = self.pos; self.pos += size
        return bytes(self.data[start:self.pos])

    def unpack(self,fmt):
        fmt = fmt if isinstance(fmt,struct.Struct) else struct.Struct(fmt)
        return fmt.unpack(self.take(fmt.size))

    def text(self,size):
        try: return self.take(size).decode("utf-8")
        except UnicodeDecodeError: self.error("Invalid UTF-8 payload.")

    def bounded(self,field,value): self.limits.check(field,value,format="qpy",version=13,offset=self.base+self.pos)

    def parameter_vector(self):
        name_size,length,identity,index=self.unpack("!HQ16sQ")
        name=self.text(name_size)
        if not name or not length or index>=length:self.error("Invalid parameter vector size or index.")
        self.bounded("max_parameter_nodes",length)
        identity=UUID(bytes=identity)
        root=UUID(int=(identity.int-index)%(1<<128))
        key=(name,str(root),length)
        if key not in self.vectors:
            count=self.budget.get("vector_elements",0)+length
            self.bounded("max_parameter_nodes",count)
            vector=ParameterVector(name)
            vector._root_uuid=str(root)
            vector.resize(length)
            self.vectors[key]=vector
            self.budget["vector_elements"]=count
        value=self.vectors[key][index]
        if value.name in self.parameters:
            previous=self.parameters[value.name]
            if type(previous) is not ParameterVectorElement or previous.uuid!=value.uuid:
                self.error("Conflicting parameter vector identities.",UnsupportedFeature)
            return previous
        object.__setattr__(value,"_uuid_explicit",True)
        self.parameters[value.name]=value
        return value

    def value(self,kind,size):
        self.budget["values"] += 1
        self.bounded("max_parameter_nodes",self.budget["values"])
        start = self.base+self.pos
        sub = Reader(self.take(size),self.limits,start,self.depth+1,self.budget)
        sub.parameters = self.parameters
        sub.vectors = self.vectors
        if kind == b"f":
            value, = sub.unpack("<d")
            if not math.isfinite(value): sub.error("Nonfinite numeric parameter.")
        elif kind == b"i": value, = sub.unpack("<q")
        elif kind == b"p":
            length,uid = sub.unpack("!H16s")
            name = sub.text(length)
            if not name: sub.error("Empty parameter name.")
            uid = str(UUID(bytes=uid))
            if name in self.parameters and (type(self.parameters[name]) is not Parameter or self.parameters[name].uuid != uid): sub.error("Distinct parameter identities sharing a name are not representable.",UnsupportedFeature)
            value = self.parameters.setdefault(name,Parameter(name,uid))
        elif kind == b"v": value=sub.parameter_vector()
        elif kind == b"s": value = sub.text(size)
        elif kind == b"z": value = None
        elif kind == b"e":
            from .qpy_expressions import read_expression
            value = read_expression(sub)
        else: sub.error(f"Unsupported parameter type {kind!r}.",UnsupportedFeature)
        if sub.pos != len(sub.data): sub.error("Invalid parameter payload size.")
        return value

    def circuit(self):
        self.parameters = {}
        self.vectors = {}
        name_size,phase_type,phase_size,nq,nc,metadata_size,nreg,ninst,nvars = self.unpack(CIRCUIT_HEADER)
        for field,value in (("max_qubits",nq),("max_clbits",nc),("max_metadata_bytes",metadata_size),("max_registers",nreg),("max_instructions",ninst)):
            self.bounded(field,value)
        if not nq: self.error("Zero-qubit circuits are not supported by the native Circuit.",UnsupportedFeature)
        if nvars: self.error("QPY standalone classical variables are not implemented.",UnsupportedFeature)
        name = self.text(name_size) if name_size else None
        self.instructions += ninst
        self.bounded("max_instructions",self.instructions)
        # Global-phase scalars use network order, unlike instruction scalars in v13.
        phase = self.unpack("!d")[0] if phase_type == b"f" and phase_size == 8 else self.value(phase_type,phase_size)
        def nonfinite(value): raise ValueError("Nonfinite metadata literal.")
        try: metadata = json.loads(self.text(metadata_size),parse_constant=nonfinite)
        except (ValueError,RecursionError): self.error("Invalid JSON circuit metadata.")
        if not isinstance(metadata,dict): self.error("Circuit metadata must be an object.")
        if set(metadata)&{"registers","global_phase"}: self.error("Metadata conflicts with native structural fields.",UnsupportedFeature)
        stack = [(metadata,0)]
        while stack:
            value,depth = stack.pop(); self.bounded("max_nesting_depth",depth)
            if isinstance(value,(dict,list)):
                stack.extend((child,depth+1) for child in (value.values() if isinstance(value,dict) else value))
        specs = []
        for _ in range(nreg):
            raw = self.take(REGISTER.size)
            if raw[1] not in (0,1) or raw[-1] not in (0,1): self.error("Invalid canonical register boolean flags.")
            kind,standalone,size,length,in_circuit = REGISTER.unpack(raw)
            if kind not in {b"q",b"c"}: self.error("Invalid register type.")
            self.bounded("max_qubits" if kind == b"q" else "max_clbits",size)
            reg_name = self.text(length)
            bits = list(self.unpack("!"+"q"*size))
            if not standalone or not in_circuit: self.error("Alias/external registers are not implemented.",UnsupportedFeature)
            specs.append({"kind":kind.decode(),"name":reg_name,"bits":bits})
        custom_count, = self.unpack("!Q")
        self.bounded("max_custom_definitions",custom_count)
        if custom_count: self.error("QPY custom instruction definitions are not implemented.",UnsupportedFeature)
        circuit = Circuit(nq,nc,name,metadata)
        circuit.global_phase = phase
        circuit.metadata["registers"] = specs
        register_specs(circuit)
        for _ in range(ninst):
            name_size,label_size,nparams,nqargs,ncargs,condition,condition_length,condition_value,nctrl,ctrl_state = self.unpack(INSTRUCTION)
            if nqargs > nq or ncargs > nc: self.error("Instruction arity exceeds circuit resources.")
            self.bounded("max_parameter_nodes",nparams)
            class_name, label = self.text(name_size), self.text(label_size)
            if condition or condition_length: self.error("QPY conditional instructions require an unimplemented protocol branch.",UnsupportedFeature)
            if class_name not in NAMES: self.error(f"Unknown instruction class {class_name!r}.",UnsupportedFeature)
            op_name = NAMES[class_name]
            qargs,cargs = [],[]
            for index in range(nqargs+ncargs):
                kind,wire = self.unpack("!cI")
                if kind != (b"q" if index < nqargs else b"c") or wire >= (nq if index < nqargs else nc): self.error("Invalid instruction argument mapping.")
                (qargs if index < nqargs else cargs).append(wire)
            if len(set(qargs)) != len(qargs): self.error("Repeated quantum instruction argument.")
            params = [self.value(*self.unpack(VALUE)) for _ in range(nparams)]
            expected = OPS[op_name]
            if (expected[1] is not None and nqargs != expected[1]) or nparams != expected[2] or ncargs != int(op_name == "measure"):
                self.error("Instruction signature differs from its standard gate.")
            expected_controls = CONTROLS.get(op_name,0)
            if nctrl not in (0,expected_controls) or ctrl_state != (1<<nctrl)-1: self.error("Nonstandard coherent control state is unsupported.",UnsupportedFeature)
            if any(not isinstance(value,(Real,Parameter,ParameterExpression)) or isinstance(value,bool) for value in params):
                self.error("Non-numeric standard instruction parameter.")
            if op_name == "measure": circuit.measure(qargs[0],cargs[0])
            elif op_name == "delay": circuit.delay(params[0],qargs[0],unit="dt")
            elif op_name == "barrier": circuit.barrier(*qargs)
            else:
                operation = Operation(op_name,tuple(qargs[expected_controls:]),tuple(qargs[:expected_controls]),tuple(params),{"label":label} if label else {})
                circuit.operations.append(operation)
            if label and op_name in {"measure","delay","barrier"}:
                item = circuit.measurements[-1] if op_name == "measure" else circuit.operations[-1]
                item.metadata["label"] = label
        calibrations, = self.unpack("!H")
        if calibrations: self.error("Pulse calibration payload is unsupported.",UnsupportedFeature)
        exists,initial,mapping,final,extra,input_count = self.unpack(LAYOUT)
        if exists != b"\x00" or extra or any(value != -1 for value in (initial,mapping,final)) or input_count not in (-1,0):
            self.error("Native QPY TranspileLayout fields are not implemented.",UnsupportedFeature)
        validate_control_flow(circuit)
        return circuit


def _uid(parameter): return UUID(parameter.uuid) if parameter.uuid else uuid5(NAMESPACE_URL,"quantumbridge:parameter:"+parameter.name)


def _parameter_value(value,limits=None):
    if isinstance(value,ParameterVectorElement):
        vector=value.vector
        if value.index>=len(vector):raise UnsupportedFeature("A QPY vector element index is outside its current vector.",format="qpy",version=13)
        (limits or SerializationLimits()).check("max_parameter_nodes",len(vector),format="qpy",version=13)
        name=vector.name.encode("utf-8")
        return b"v",struct.pack("!HQ16sQ",len(name),len(vector),_uid(value).bytes,value.index)+name
    if isinstance(value,Parameter):
        name = value.name.encode("utf-8")
        return b"p",struct.pack("!H16s",len(name),_uid(value).bytes)+name
    if isinstance(value,ParameterExpression):
        if value.op in {"const","parameter"}: return _parameter_value(value.args[0],limits)
        from .qpy_expressions import write_expression
        return b"e",write_expression(value,limits)
    if isinstance(value,bool): raise UnsupportedFeature("Boolean gate parameters are unsupported.",format="qpy",version=13)
    if isinstance(value,Integral): return b"i",struct.pack("<q",int(value))
    if isinstance(value,Real) and math.isfinite(value): return b"f",struct.pack("<d",float(value))
    if isinstance(value,str): return b"s",value.encode("utf-8")
    raise UnsupportedFeature("Unsupported QPY parameter value.",format="qpy",version=13)


def _circuit_bytes(circuit,limits):
    validate_control_flow(circuit)
    specs = register_specs(circuit)
    for field,value in (("max_qubits",circuit.num_qubits),("max_clbits",circuit.num_bits),("max_registers",len(specs))): limits.check(field,value,format="qpy",version=13)
    items = list(circuit.iter_instructions())
    limits.check("max_instructions",len(items),format="qpy",version=13)
    names,identities,nodes = {},{},0
    def parameter_identity(value,depth=0):
        nonlocal nodes
        nodes += 1
        limits.check("max_parameter_nodes",nodes,format="qpy",version=13)
        limits.check("max_symbolic_expression_depth",depth,format="qpy",version=13)
        if isinstance(value,Parameter):
            uid = _uid(value)
            if value.name in names and names[value.name] != uid or uid in identities and identities[uid] != value.name:
                raise UnsupportedFeature("Parameter names and UUIDs must identify one another uniquely.",format="qpy",version=13)
            names[value.name],identities[uid] = uid,value.name
        elif isinstance(value,ParameterExpression):
            for child in value.args: parameter_identity(child,depth+1)
    parameter_identity(circuit.global_phase)
    for item in items:
        for value in getattr(item,"params",()): parameter_identity(value)
    if circuit.name == "" or circuit.name is not None and not isinstance(circuit.name,str):
        raise UnsupportedFeature("Circuit names must be nonempty strings or absent.",format="qpy",version=13)
    name = (circuit.name or "").encode("utf-8")
    phase_type,phase = _parameter_value(circuit.global_phase,limits)
    if phase_type in {b"f",b"i"}: phase_type,phase = b"f",struct.pack("!d",float(circuit.global_phase))
    metadata = {key:value for key,value in circuit.metadata.items() if key not in {"global_phase","registers"}}
    def json_value(value,depth=0):
        limits.check("max_nesting_depth",depth,format="qpy",version=13)
        if isinstance(value,dict):
            if any(not isinstance(key,str) for key in value): raise UnsupportedFeature("JSON metadata keys must be strings; use an external sidecar.",format="qpy",version=13)
            for child in value.values(): json_value(child,depth+1)
        elif isinstance(value,list):
            for child in value: json_value(child,depth+1)
        elif value is not None and type(value) not in {str,int,float,bool}:
            raise UnsupportedFeature("Metadata must use exact JSON types; use an external sidecar.",format="qpy",version=13)
    json_value(metadata)
    try: encoded_metadata = json.dumps(metadata,ensure_ascii=True,allow_nan=False,separators=(",",":")).encode()
    except (TypeError,ValueError,RecursionError) as exc: raise UnsupportedFeature("Metadata must be finite JSON data.",format="qpy",version=13) from exc
    limits.check("max_metadata_bytes",len(encoded_metadata),format="qpy",version=13)
    parts = BoundedParts(limits,"qpy")
    parts.extend([CIRCUIT_HEADER.pack(len(name),phase_type,len(phase),circuit.num_qubits,circuit.num_bits,len(encoded_metadata),len(specs),len(items),0),name,phase,encoded_metadata])
    for spec in specs:
        reg_name = spec["name"].encode()
        parts.extend([REGISTER.pack(spec["kind"].encode(),True,len(spec["bits"]),len(reg_name),True),reg_name,struct.pack("!"+"q"*len(spec["bits"]),*spec["bits"])])
    parts.append(struct.pack("!Q",0))
    for item in items:
        if isinstance(item,Measurement) and item.kind != "computational":
            raise UnsupportedFeature("Only computational-basis measurement has a supported QPY instruction.",format="qpy",version=13)
        op_name = "measure" if isinstance(item,Measurement) else item.name
        if op_name not in OPS or any(key in item.metadata for key in ("condition","gate_condition","control_flow_stack","control_flow","control_node","matrix","kraus")):
            raise UnsupportedFeature(f"QPY does not yet support instruction {op_name!r} or its control/opaque metadata.",format="qpy",version=13)
        class_name = OPS[op_name][0].encode()
        label = item.metadata.get("label","").encode()
        if set(item.metadata)-{"label","operation_index","directive","duration","unit"}:
            raise UnsupportedFeature("Instruction metadata cannot be represented by this QPY subset.",format="qpy",version=13)
        qargs,cargs = ((item.wire,),(item.bit,)) if isinstance(item,Measurement) else (item.wires,())
        params = () if isinstance(item,Measurement) else item.params
        if op_name == "delay" and item.metadata.get("unit","dt") != "dt":
            raise UnsupportedFeature("The tested QPY v13 Delay payload cannot preserve non-dt units; use QASM3.",format="qpy",version=13)
        ctrl = CONTROLS.get(op_name,0)
        expected = OPS[op_name]
        if (expected[1] is not None and len(qargs) != expected[1]) or len(params) != expected[2] or not isinstance(item,Measurement) and len(item.controls) != ctrl:
            raise FormatValidationError("Instruction signature/control count differs from its standard gate.",format="qpy",version=13)
        parts.append(INSTRUCTION.pack(len(class_name),len(label),len(params),len(qargs),len(cargs),0,0,0,ctrl,(1<<ctrl)-1))
        parts.extend((class_name,label))
        parts.extend(struct.pack("!cI",b"q",wire) for wire in qargs)
        parts.extend(struct.pack("!cI",b"c",wire) for wire in cargs)
        for value in params:
            kind,payload = _parameter_value(value,limits)
            parts.extend((VALUE.pack(kind,len(payload)),payload))
    parts.extend((struct.pack("!H",0),LAYOUT.pack(b"\x00",-1,-1,-1,0,-1)))
    result = b"".join(parts)
    limits.check("max_input_bytes",len(result),format="qpy",version=13)
    return result


def qpy_dumps(circuits, *, version=13, limits=None):
    if version != 13: raise UnsupportedVersion("Only the tested QPY version 13 is supported.",format="qpy",version=version)
    limits = limits or SerializationLimits()
    from itertools import islice
    circuits = [circuits] if isinstance(circuits,Circuit) else list(islice(iter(circuits),limits.max_circuits+1))
    limits.check("max_circuits",len(circuits),format="qpy",version=13)
    parts = BoundedParts(limits,"qpy")
    parts.extend((FILE_HEADER.pack(b"QISKIT",13,0,0,0,len(circuits),b"p"),b"q"))
    try:
        count = 0
        for circuit in circuits:
            count += len(circuit.operations)+len(circuit.measurements)
            limits.check("max_instructions",count,format="qpy",version=13)
            parts.append(_circuit_bytes(circuit,limits))
    except (struct.error,OverflowError,RecursionError) as exc:
        raise FormatValidationError("Object fields exceed supported binary lengths or nesting.",format="qpy",version=13) from exc
    result = b"".join(parts)
    limits.check("max_input_bytes",len(result),format="qpy",version=13)
    return result


def qpy_loads(data, *, limits=None):
    limits = limits or SerializationLimits()
    if not isinstance(data,(bytes,bytearray,memoryview)): raise TypeError("QPY input must be binary data.")
    limits.check("max_input_bytes",len(data),format="qpy")
    reader = Reader(data,limits)
    magic,version,major,minor,patch,count,encoding = reader.unpack(FILE_HEADER)
    if magic != b"QISKIT": reader.error("Invalid QPY magic.")
    if version != 13: raise UnsupportedVersion("Only tested QPY version 13 is supported.",format="qpy",version=version,offset=6)
    if encoding != b"p": reader.error("Unsupported symbolic encoding.",UnsupportedFeature)
    reader.bounded("max_circuits",count)
    if reader.take(1) != b"q": reader.error("Only circuit program payloads are supported.",UnsupportedFeature)
    try: circuits = [reader.circuit() for _ in range(count)]
    except SerializationError: raise
    except (ValueError,TypeError,KeyError,OverflowError,RecursionError) as exc:
        reader.error(f"Invalid circuit payload: {type(exc).__name__}.")
    if reader.pos != len(reader.data): reader.error("Unexpected trailing binary data.")
    return circuits


def qpy_dump(circuits,stream,**options): write_output(stream,qpy_dumps(circuits,**options))
def qpy_load(stream,**options): return qpy_loads(read_input(stream,binary=True,limits=options.get("limits"),format="qpy"),**options)


def qpy_get_version(stream):
    if hasattr(stream,"read"):
        position = stream.tell()
        try: data = stream.read(FILE_HEADER.size)
        finally: stream.seek(position)
    else: data = read_input(stream,binary=True,format="qpy")[:FILE_HEADER.size]
    reader = Reader(data,SerializationLimits())
    magic,version,*_ = reader.unpack(FILE_HEADER)
    if magic != b"QISKIT": reader.error("Invalid QPY magic.")
    return version
