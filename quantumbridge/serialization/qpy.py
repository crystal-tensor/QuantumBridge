# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent public QPY v13 binary protocol implementation, not an SDK wrapper.

import io
import json
import math
import struct
from dataclasses import dataclass
from uuid import UUID, uuid5, NAMESPACE_URL
from numbers import Real, Integral
import numpy as np

from quantumbridge.core import Circuit, Instruction, Operation, Measurement, Parameter, ParameterExpression, ParameterVector, ParameterVectorElement
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
CUSTOM_INSTRUCTION = struct.Struct("!HcII?QIIQ")
MODIFIER = struct.Struct("!cIId")
OPS = {"id":("IGate",1,0), "x":("XGate",1,0), "y":("YGate",1,0), "z":("ZGate",1,0),
       "h":("HGate",1,0), "s":("SGate",1,0), "sdg":("SdgGate",1,0), "t":("TGate",1,0),
       "tdg":("TdgGate",1,0), "sx":("SXGate",1,0), "sxdg":("SXdgGate",1,0),
       "rx":("RXGate",1,1), "ry":("RYGate",1,1), "rz":("RZGate",1,1),
       "phase":("PhaseGate",1,1), "u":("UGate",1,3), "u1":("U1Gate",1,1),
       "u2":("U2Gate",1,2), "u3":("U3Gate",1,3),
       "cx":("CXGate",2,0), "cy":("CYGate",2,0), "cz":("CZGate",2,0), "ch":("CHGate",2,0), "csx":("CSXGate",2,0),
       "crx":("CRXGate",2,1), "cry":("CRYGate",2,1), "crz":("CRZGate",2,1), "cp":("CPhaseGate",2,1),
       "swap":("SwapGate",2,0), "ccx":("CCXGate",3,0), "cswap":("CSwapGate",3,0),
       "ccz":("CCZGate",3,0), "cu":("CUGate",2,4),
       "rxx":("RXXGate",2,1), "ryy":("RYYGate",2,1), "rzz":("RZZGate",2,1),
       "unitary":("UnitaryGate",None,1),
       "reset":("Reset",1,0), "measure":("Measure",1,0), "barrier":("Barrier",None,0), "delay":("Delay",1,1)}
NAMES = {value[0]:name for name,value in OPS.items()}
CONTROLS = {"cx":1,"cy":1,"cz":1,"ch":1,"csx":1,"crx":1,"cry":1,"crz":1,"cp":1,"ccx":2,"ccz":2,"cu":1,"cswap":1}
CONTROL_BASES = {"cx":"x", "cy":"y", "cz":"z", "ch":"h", "csx":"sx", "crx":"rx", "cry":"ry", "crz":"rz", "cp":"phase", "ccx":"x", "ccz":"z", "cu":"u", "cswap":"swap"}


@dataclass(frozen=True)
class _CustomRecord:
    name: str
    width: int
    kind: bytes
    definition: object
    controls: int
    state: int
    base: object
    payload_depth: int


class Reader:
    def __init__(self,data,limits,base=0,depth=0,budget=None):
        self.data, self.pos, self.limits, self.base = memoryview(data), 0, limits, base
        self.instructions = 0
        self.parameters = {}
        self.vectors = {}
        self.depth,self.budget = depth,({"values":0} if budget is None else budget)
        self.max_depth = depth
        self.bounded("max_nesting_depth",depth)

    def error(self,reason,cls=FormatValidationError):
        raise cls(reason,format="qpy",version=13,offset=self.base+self.pos)

    def canonical_parameter_graph(self, circuit):
        from quantumbridge.core.parameter_graph import canonical_parameter_graph
        return canonical_parameter_graph(circuit,self.parameters)

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

    def admit_standard_object(self):
        # The object and its owned executable definition both require work;
        # admit this minimum before invoking any formal-binding constructor.
        self.budget["expanded"] = self.budget.get("expanded",0)+2
        self.bounded("max_gate_expansion",self.budget["expanded"])

    def base_instruction(self):
        name_size,label_size,nparams,nq,nc,condition,condition_size,condition_value,nctrl,state = self.unpack(INSTRUCTION)
        self.bounded("max_parameter_nodes",nparams)
        self.bounded("max_qubits",nq)
        if nc or condition or condition_size: self.error("Unsupported custom base instruction classical fields.",UnsupportedFeature)
        name,label = self.text(name_size),self.text(label_size)
        # A base-gate record has the usual header and parameters, but no wire
        # argument records: it is not an invocation on a containing circuit.
        params = tuple(self.value(*self.unpack(VALUE)) for _ in range(nparams))
        if self.pos != len(self.data): self.error("Trailing bytes in custom base instruction.")
        return name,label,params,nq,nctrl,state

    def base_operation(self,description,table,ancestors):
        from quantumbridge.core.gates import Gate, ControlledGate
        key,label,params,width,nctrl,state = description
        if key in table:
            record = table[key]
            if width != record.width or (nctrl,state) != (record.controls,record.state):
                self.error("Custom base operation header differs from its referenced definition.")
            return self.custom_operation(key,params,label,table,ancestors)
        if key not in NAMES: self.error("Unresolved custom base operation reference.",UnsupportedFeature)
        name = NAMES[key]
        if (OPS[name][1] is not None and OPS[name][1] != width or OPS[name][2] != len(params)
                or nctrl != CONTROLS.get(name,0) or state >= 1<<nctrl):
            self.error("Standard base operation signature differs from its header.")
        if name in {"reset","measure","barrier","delay"}:
            self.error("Nonunitary or directive annotation bases are not native unitary operations.",UnsupportedFeature)
        from quantumbridge.core.standard_gates import STANDARD_GATE_TYPES, standard_from_record
        if key in {kind.__name__ for kind in STANDARD_GATE_TYPES}:
            self.admit_standard_object()
            result = standard_from_record(key, params, label or None, state if nctrl else None)
            if result.num_qubits != width: self.error("Standard base width differs from its parameters.")
            return result
        if nctrl:
            base_name = CONTROL_BASES[name]
            base_width = width-nctrl
            body = Circuit(base_width).append(base_name,range(base_width),params=params)
            result = ControlledGate(Gate(base_name,base_width,params,definition=body),nctrl,state,label or None)
            result.name = name+("_o"+str(state) if state != (1<<nctrl)-1 else "")
            return result
        body = Circuit(width).append(name,range(width),params=params)
        return Gate(name,width,params,label or None,definition=body)

    def custom_operation(self,key,params,label,table,ancestors=()):
        from quantumbridge.core.gates import Gate, ControlledGate, validate_definition
        if key in ancestors: self.error("Cyclic custom base-gate reference.")
        record = table[key]
        self.bounded("max_nesting_depth",self.depth+len(ancestors)+record.payload_depth)
        display,width,definition,nctrl,state,base = (record.name,record.width,record.definition,record.controls,record.state,record.base)
        if record.kind == b"a":
            from quantumbridge.core.annotated_operation import AnnotatedOperation, InverseModifier, ControlModifier, PowerModifier
            if label: self.error("Annotation labels are not represented by the native operation protocol.",UnsupportedFeature)
            if any(type(value) not in (InverseModifier,ControlModifier,PowerModifier) for value in params):
                self.error("An annotated invocation requires typed Modifier parameters.")
            self.budget["expanded"] = self.budget.get("expanded",0)+1+len(params)
            self.bounded("max_gate_expansion",self.budget["expanded"])
            result = AnnotatedOperation(self.base_operation(base,table,(*ancestors,key)),list(params))
            if result.num_qubits != width: self.error("Annotation modifier widths disagree with its definition header.")
            return result
        from quantumbridge.core.operations import instruction_definition_work
        work = (1 if definition is None else instruction_definition_work(definition)) if record.kind == b"i" else validate_definition(definition)
        self.budget["expanded"] = self.budget.get("expanded",0)+work
        self.bounded("max_gate_expansion",self.budget["expanded"])
        if record.kind == b"i" and definition is None:
            return Instruction(display, width, params=params, label=label or None)
        formal = definition.parameters
        from quantumbridge.core.parameters import parameter_set
        if not set(formal) <= set(parameter_set(params)):
            if len(formal) != len(params): self.error("Custom Gate formal parameter mapping is ambiguous.",UnsupportedFeature)
            definition = definition.assign_parameters(dict(zip(formal,params)))
        if record.kind == b"i":
            metadata = dict(definition.metadata)
            metadata.setdefault("definition_name",definition.name)
            return Instruction(display,width,params=params,label=label or None,definition=definition,metadata=metadata)
        if base is None: return Gate(display,width,params,label or None,definition=definition)
        base_gate = self.base_operation(base,table,(*ancestors,key))
        if not isinstance(base_gate,Gate): self.error("A ControlledGate base record must represent a Gate.")
        if base_gate.num_qubits+nctrl != width or not _same_parameters(base_gate.params,params):
            self.error("Controlled custom Gate base width/parameters differ from its header.")
        result = ControlledGate(base_gate,nctrl,state,label or None)
        # v13 stores the closed-control definition; ctrl_state is applied at
        # the object boundary, not already baked into that definition.
        actual = Circuit(width)
        opened = [wire for wire in range(nctrl) if not (state>>wire)&1]
        for wire in opened: actual.x(wire)
        actual = actual.compose(definition)
        for wire in reversed(opened): actual.x(wire)
        result.name = display
        result.definition = actual
        return result

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
        elif kind == b"n":
            stream = io.BytesIO(bytes(sub.data))
            try:
                version = np.lib.format.read_magic(stream)
                if version not in ((1,0),(2,0)): sub.error("Unsupported NumPy value format.",UnsupportedFeature)
                shape, order, dtype = (np.lib.format.read_array_header_1_0(stream) if version == (1,0)
                    else np.lib.format.read_array_header_2_0(stream))
            except (ValueError, EOFError) as exc: sub.error("Malformed NumPy value header: "+str(exc))
            if (len(shape) != 2 or any(type(x) is not int or x < 1 for x in shape)
                    or dtype.hasobject or dtype.kind not in "biufc"):
                sub.error("Only explicit numeric matrix parameter values are supported.",UnsupportedFeature)
            count = shape[0]*shape[1]
            total = self.budget.get("numeric_elements",0)+count
            sub.bounded("max_numeric_elements",total)
            self.budget["numeric_elements"] = total
            if stream.tell()+count*dtype.itemsize != len(sub.data): sub.error("NumPy value length differs from its matrix shape.")
            from quantumbridge.core.gate_limits import current_gate_limits
            current_gate_limits().check("max_matrix_dimension",max(shape))
            matrix = np.frombuffer(sub.data, dtype=dtype, offset=stream.tell()).reshape(shape, order="F" if order else "C")
            value = _unitary_wire_order(matrix)
            sub.pos = len(sub.data)
        elif kind == b"m":
            from quantumbridge.core.annotated_operation import InverseModifier, ControlModifier, PowerModifier
            modifier,nctrl,state,power = sub.unpack(MODIFIER)
            self.budget["modifiers"] = self.budget.get("modifiers",0)+1
            self.bounded("max_gate_expansion",self.budget["modifiers"])
            if modifier == b"i": value = InverseModifier()
            elif modifier == b"c":
                sub.bounded("max_qubits",nctrl)
                value = ControlModifier(nctrl,state)
            elif modifier == b"p":
                if not math.isfinite(power): sub.error("A modifier power must be finite.")
                value = PowerModifier(power)
            else: sub.error("Unknown QPY modifier type.",UnsupportedFeature)
        else: sub.error(f"Unsupported parameter type {kind!r}.",UnsupportedFeature)
        if sub.pos != len(sub.data): sub.error("Invalid parameter payload size.")
        self.max_depth = max(self.max_depth,sub.max_depth)
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
        self.budget["instructions"] = self.budget.get("instructions",0)+ninst
        self.bounded("max_instructions",self.budget["instructions"])
        # Global-phase scalars use network order, unlike instruction scalars in v13.
        phase = self.unpack("!d")[0] if phase_type == b"f" and phase_size == 8 else self.value(phase_type,phase_size)
        def nonfinite(value): raise ValueError("Nonfinite metadata literal.")
        try: metadata = json.loads(self.text(metadata_size),parse_constant=nonfinite)
        except (ValueError,RecursionError): self.error("Invalid JSON circuit metadata.")
        if not isinstance(metadata,dict): self.error("Circuit metadata must be an object.")
        if set(metadata)&{"registers","global_phase","classical_scope"}: self.error("Metadata conflicts with native structural fields or unsupported classical identifiers.",UnsupportedFeature)
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
        self.budget["definitions"] = self.budget.get("definitions",0)+custom_count
        self.bounded("max_custom_definitions",self.budget["definitions"])
        custom = {}
        for _ in range(custom_count):
            raw = self.take(CUSTOM_INSTRUCTION.size)
            if raw[11] not in (0,1): self.error("Invalid custom definition flag.")
            size,kind,width,clbits,has_definition,payload_size,nctrl,state,base_size = CUSTOM_INSTRUCTION.unpack(raw)
            self.bounded("max_qubits",width)
            self.bounded("max_clbits",clbits)
            key = self.text(size)
            if not key or key in custom or key in NAMES: self.error("Conflicting QPY custom definition identifier.")
            if kind not in {b"g",b"c",b"a",b"i"} or clbits:
                self.error("This QPY custom record type/control payload is not implemented.",UnsupportedFeature)
            if kind in {b"g",b"i"} and (nctrl or state or base_size):
                self.error("A non-controlled definition contains coherent control fields.")
            if kind == b"c" and (not 0 < nctrl < width or state >= 1<<nctrl or not base_size):
                self.error("Invalid custom ControlledGate control fields.")
            definition,payload_depth = None,0
            if kind == b"a":
                if has_definition or payload_size or nctrl or state or not base_size:
                    self.error("An annotation requires a base-operation payload, not a synthesized Gate definition.")
            elif kind == b"i" and not has_definition and not payload_size:
                pass
            else:
                if not has_definition or not payload_size:
                    self.error("Opaque custom QPY definitions are not executable.",UnsupportedFeature)
                offset = self.base+self.pos
                sub = Reader(self.take(payload_size),self.limits,offset,self.depth+1,self.budget)
                definition = sub.circuit()
                if sub.pos != len(sub.data): sub.error("Trailing bytes in QPY custom definition.")
                if definition.num_qubits != width or definition.num_bits:
                    self.error("Custom Gate definition width differs from its header.")
                from quantumbridge.core.gates import validate_definition
                from quantumbridge.core.operations import instruction_definition_work
                instruction_definition_work(definition) if kind == b"i" else validate_definition(definition)
                payload_depth = sub.max_depth-self.depth
                self.max_depth = max(self.max_depth,sub.max_depth)
            # Public v13 uses a UUID suffix for the serialization-local key;
            # it is not part of the user's Gate name.
            display, separator, suffix = key.rpartition("_")
            try: is_uuid = separator and len(suffix) in (32,36) and UUID(suffix)
            except ValueError: is_uuid = False
            display = display if is_uuid else key
            if kind == b"a" and display != "annotated": self.error("Nonstandard annotation display name.")
            base = None
            if base_size:
                offset = self.base+self.pos
                sub = Reader(self.take(base_size),self.limits,offset,self.depth+1,self.budget)
                sub.parameters,sub.vectors = self.parameters,self.vectors
                base = sub.base_instruction()
                payload_depth = max(payload_depth,sub.max_depth-self.depth)
                self.max_depth = max(self.max_depth,sub.max_depth)
            custom[key] = _CustomRecord(display,width,kind,definition,nctrl,state,base,payload_depth)
        for key in custom:
            seen = set()
            current = key
            while current in custom and custom[current].base is not None:
                if current in seen: self.error("Cyclic custom base-gate reference.")
                seen.add(current)
                self.budget["references"] = self.budget.get("references",0)+1
                self.bounded("max_gate_expansion",self.budget["references"])
                self.bounded("max_nesting_depth",self.depth+len(seen))
                current = custom[current].base[0]
            if current not in custom and current not in NAMES:
                self.error("Unresolved custom base-gate reference.",UnsupportedFeature)
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
            if class_name not in NAMES and class_name not in custom: self.error(f"Unknown instruction class {class_name!r}.",UnsupportedFeature)
            op_name = NAMES.get(class_name)
            qargs,cargs = [],[]
            for index in range(nqargs+ncargs):
                kind,wire = self.unpack("!cI")
                if kind != (b"q" if index < nqargs else b"c") or wire >= (nq if index < nqargs else nc): self.error("Invalid instruction argument mapping.")
                (qargs if index < nqargs else cargs).append(wire)
            if len(set(qargs)) != len(qargs): self.error("Repeated quantum instruction argument.")
            params = [self.value(*self.unpack(VALUE)) for _ in range(nparams)]
            if class_name in custom:
                record = custom[class_name]
                if nqargs != record.width or ncargs or (nctrl,ctrl_state) != (record.controls,record.state):
                    self.error("QPY custom Gate invocation differs from its definition.")
                if record.kind == b"i":
                    circuit._append_instruction_reference(self.custom_operation(class_name,tuple(params),label,custom), qargs)
                else: circuit.append(self.custom_operation(class_name,tuple(params),label,custom),qargs)
                continue
            expected = OPS[op_name]
            if (expected[1] is not None and nqargs != expected[1]) or nparams != expected[2] or ncargs != int(op_name == "measure"):
                self.error("Instruction signature differs from its standard gate.")
            expected_controls = CONTROLS.get(op_name,0)
            if nctrl not in (0,expected_controls) or not 0 <= ctrl_state < 1<<nctrl: self.error("Invalid coherent control fields.")
            if op_name != "unitary" and any(not isinstance(value,(Real,Parameter,ParameterExpression)) or isinstance(value,bool) for value in params):
                self.error("Non-numeric standard instruction parameter.")
            from quantumbridge.core.standard_gates import STANDARD_GATE_TYPES, standard_from_record
            if class_name in {kind.__name__ for kind in STANDARD_GATE_TYPES}:
                self.admit_standard_object()
                gate = standard_from_record(class_name, params, label or None, ctrl_state if nctrl else None)
                if gate.num_qubits != nqargs: self.error("Standard Gate width differs from its matrix or constructor.")
                circuit.append(gate, qargs)
                continue
            if ctrl_state != (1<<nctrl)-1: self.error("Unsupported open control standard type.",UnsupportedFeature)
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
        return self.canonical_parameter_graph(circuit)


def _uid(parameter): return UUID(parameter.uuid) if parameter.uuid else uuid5(NAMESPACE_URL,"quantumbridge:parameter:"+parameter.name)


def _same_parameters(left, right):
    if len(left) != len(right): return False
    for first, second in zip(left, right):
        if type(first) is np.ndarray or type(second) is np.ndarray:
            if type(first) is not np.ndarray or type(second) is not np.ndarray or first.shape != second.shape:
                return False
            if any(a != b for a, b in zip(first.flat, second.flat)): return False
        elif first != second: return False
    return True


def _unitary_wire_order(matrix):
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] < 2 or matrix.shape[0] & (matrix.shape[0]-1):
        raise FormatValidationError("A NumPy Gate parameter requires a square qubit matrix.",format="qpy",version=13)
    from quantumbridge.execution.array_ownership import retained_array
    from quantumbridge.execution.resource_context import current_resources
    from quantumbridge.core.gate_limits import current_gate_limits
    current_gate_limits().check("max_matrix_dimension",matrix.shape[0])
    width = matrix.shape[0].bit_length()-1
    scope = current_resources()
    result = retained_array(None if scope is None else scope.ledger,"qpy_matrix_wire_order",matrix.shape,complex)
    order = [int(format(index,"0"+str(width)+"b")[::-1],2) for index in range(matrix.shape[0])]
    for row, source_row in enumerate(order):
        for col, source_col in enumerate(order): result[row,col] = matrix[source_row,source_col]
    return result


def _parameter_value(value,limits=None,*,budget=None):
    if type(value) is np.ndarray:
        limits = limits or SerializationLimits()
        total = (0 if budget is None else budget.get("numeric_elements",0))+value.size
        limits.check("max_numeric_elements",total,format="qpy",version=13)
        limits.check("max_input_bytes",value.size*16,format="qpy",version=13)
        if budget is not None: budget["numeric_elements"] = total
        if value.dtype.hasobject or value.dtype.kind not in "biufc":
            raise UnsupportedFeature("Only numeric NumPy matrix parameters are supported.",format="qpy",version=13)
        payload = io.BytesIO()
        np.save(payload, _unitary_wire_order(value), allow_pickle=False)
        limits.check("max_input_bytes",payload.tell(),format="qpy",version=13)
        return b"n",payload.getvalue()
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
        if value.op in {"const","parameter"}: return _parameter_value(value.args[0],limits,budget=budget)
        from .qpy_expressions import write_expression
        return b"e",write_expression(value,limits)
    if isinstance(value,bool): raise UnsupportedFeature("Boolean gate parameters are unsupported.",format="qpy",version=13)
    if isinstance(value,Integral): return b"i",struct.pack("<q",int(value))
    if isinstance(value,Real) and math.isfinite(value): return b"f",struct.pack("<d",float(value))
    if isinstance(value,str): return b"s",value.encode("utf-8")
    raise UnsupportedFeature("Unsupported QPY parameter value.",format="qpy",version=13)


def _modifier_value(value,limits,budget):
    from quantumbridge.core.annotated_operation import InverseModifier, ControlModifier, PowerModifier
    from quantumbridge.core.parameters import parameter_set, resolve_parameter
    budget["modifiers"] = budget.get("modifiers",0)+1
    limits.check("max_gate_expansion",budget["modifiers"],format="qpy",version=13)
    if type(value) is InverseModifier: payload = MODIFIER.pack(b"i",0,0,0.)
    elif type(value) is ControlModifier:
        checked = ControlModifier(value.num_ctrl_qubits,value.ctrl_state)
        payload = MODIFIER.pack(b"c",checked.num_ctrl_qubits,checked.ctrl_state,0.)
    elif type(value) is PowerModifier:
        PowerModifier(value.power)
        if parameter_set((value.power,)):
            raise UnsupportedFeature("QPY v13 Modifier power is a float64 field, not a symbolic expression record.",format="qpy",version=13)
        power = resolve_parameter(value.power,{})
        if float(power) != power:
            raise UnsupportedFeature("This modifier power is not exactly representable as QPY float64.",format="qpy",version=13)
        payload = MODIFIER.pack(b"p",0,0,float(power))
    else: raise UnsupportedFeature("An annotation requires native typed modifiers.",format="qpy",version=13)
    return b"m",payload


def _object_parameters(operation):
    from quantumbridge.core.annotated_operation import AnnotatedOperation
    return operation.modifiers if type(operation) is AnnotatedOperation else operation.params


def _object_control_fields(operation,key):
    from quantumbridge.core.gates import ControlledGate
    if isinstance(operation, ControlledGate): return operation.num_ctrl_qubits,operation.ctrl_state
    if key.decode() in NAMES:
        count = CONTROLS.get(NAMES[key.decode()],0)
        return count,(1<<count)-1
    return 0,0


def _base_instruction_payload(operation,key,limits,budget):
    from quantumbridge.core.annotated_operation import AnnotatedOperation
    params = _object_parameters(operation)
    label = (getattr(operation,"label",None) or "").encode()
    nctrl,state = _object_control_fields(operation,key)
    data = BoundedParts(limits,"qpy")
    data.extend((INSTRUCTION.pack(len(key),len(label),len(params),operation.num_qubits,0,0,0,0,nctrl,state),key,label))
    for value in params:
        kind,payload = _modifier_value(value,limits,budget) if type(operation) is AnnotatedOperation else _parameter_value(value,limits,budget=budget)
        data.extend((VALUE.pack(kind,len(payload)),payload))
    return b"".join(data)


def _circuit_bytes(circuit,limits,*,_budget=None,_depth=0,_path="root"):
    budget = {} if _budget is None else _budget
    limits.check("max_nesting_depth",_depth,format="qpy",version=13)
    if "classical_scope" in circuit.metadata:
        raise UnsupportedFeature("QPY native classical identifier records are not implemented; metadata cannot substitute for their wire fields.",format="qpy",version=13)
    validate_control_flow(circuit)
    specs = register_specs(circuit)
    for field,value in (("max_qubits",circuit.num_qubits),("max_clbits",circuit.num_bits),("max_registers",len(specs))): limits.check(field,value,format="qpy",version=13)
    items = list(circuit.iter_instructions())
    budget["instructions"] = budget.get("instructions",0)+len(items)
    limits.check("max_instructions",budget["instructions"],format="qpy",version=13)
    names,identities,nodes = {},{},0
    def parameter_identity(value,depth=0):
        nonlocal nodes
        nodes += 1
        budget["parameter_nodes"] = budget.get("parameter_nodes",0)+1
        limits.check("max_parameter_nodes",budget["parameter_nodes"],format="qpy",version=13)
        limits.check("max_symbolic_expression_depth",depth,format="qpy",version=13)
        if isinstance(value,Parameter):
            uid = _uid(value)
            kind = "vector" if isinstance(value,ParameterVectorElement) else "scalar"
            if value.name in names and names[value.name] != (uid,kind) or uid in identities and identities[uid] != (value.name,kind):
                raise UnsupportedFeature("Parameter names and UUIDs must identify one another uniquely.",format="qpy",version=13)
            names[value.name],identities[uid] = (uid,kind),(value.name,kind)
        elif isinstance(value,ParameterExpression):
            for child in value.args: parameter_identity(child,depth+1)
    parameter_identity(circuit.global_phase)
    for item in items:
        for value in getattr(item,"params",()): parameter_identity(value)
    if circuit.name == "" or circuit.name is not None and not isinstance(circuit.name,str):
        raise UnsupportedFeature("Circuit names must be nonempty strings or absent.",format="qpy",version=13)
    name = (circuit.name or "").encode("utf-8")
    phase_type,phase = _parameter_value(circuit.global_phase,limits,budget=budget)
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
    custom,records = {},[]
    from quantumbridge.core.gates import Gate, ControlledGate, validate_definition
    from quantumbridge.core.annotated_operation import AnnotatedOperation, validate_annotated_structure
    def register_operation(operation,path,depth,ancestors=(),primitive_base=False):
        limits.check("max_nesting_depth",depth,format="qpy",version=13)
        if id(operation) in ancestors: raise FormatValidationError("Cyclic custom operation base graph.",format="qpy",version=13)
        from quantumbridge.core.standard_gates import standard_type_name, standard_from_record
        from quantumbridge.core.instruction_parameters import definition_signature
        standard = standard_type_name(operation)
        if standard is not None:
            expected = standard_from_record(standard, tuple(operation.params), operation.label,
                operation.ctrl_state if isinstance(operation, ControlledGate) else None)
            if (operation.metadata or operation.name != expected.name
                    or definition_signature(operation.definition) != definition_signature(expected.definition)):
                raise UnsupportedFeature("A changed standard object cannot masquerade as its canonical QPY class.",format="qpy",version=13)
            return standard.encode()
        if type(operation) is AnnotatedOperation:
            validate_annotated_structure(operation)
            work = 1+len(operation.modifiers)
            kind = b"a"
        elif type(operation) in (Gate,ControlledGate,Instruction):
            metadata = dict(operation.metadata)
            if type(operation) is Instruction and operation.definition is not None:
                # to_instruction duplicates circuit metadata and its name.
                # The definition record already transports those fields;
                # unrelated per-object metadata still cannot be discarded.
                expected = dict(operation.definition.metadata)
                expected.setdefault("definition_name",operation.definition.name)
                metadata = {key:value for key,value in metadata.items()
                    if key not in expected or value != expected[key]}
            if operation.num_bits or metadata:
                raise UnsupportedFeature("QPY unitary base records cannot carry classical bits or opaque object metadata.",format="qpy",version=13)
            if operation.definition is None and type(operation) is not Instruction:
                if primitive_base and type(operation) is Gate and operation.name in OPS:
                    if OPS[operation.name][1:] != (operation.num_qubits,len(operation.params)):
                        raise FormatValidationError("Primitive base signature differs from its operation.",format="qpy",version=13)
                    from quantumbridge.circuit_library import standard_gate
                    validate_definition(standard_gate(operation.name,*operation.params))
                    return OPS[operation.name][0].encode()
                raise UnsupportedFeature("A custom Gate/Instruction QPY base needs an executable definition.",format="qpy",version=13)
            from quantumbridge.core.operations import instruction_definition_work
            work = (1 if operation.definition is None else instruction_definition_work(operation.definition, owner=operation)) if type(operation) is Instruction else validate_definition(operation.definition,owner=operation)
            kind = b"c" if type(operation) is ControlledGate else b"i" if type(operation) is Instruction else b"g"
        else: raise UnsupportedFeature("Only native unitary operation objects have QPY custom records.",format="qpy",version=13)
        budget["expanded"] = budget.get("expanded",0)+work
        limits.check("max_gate_expansion",budget["expanded"],format="qpy",version=13)
        budget["definitions"] = budget.get("definitions",0)+1
        limits.check("max_custom_definitions",budget["definitions"],format="qpy",version=13)
        local_name = (operation.name+"_"+uuid5(NAMESPACE_URL,"quantumbridge:qpy13:"+path).hex).encode()
        base_key = None
        if kind in {b"a",b"c"}:
            base = operation.base_op if kind == b"a" else operation.base_gate
            base_key = register_operation(base,path+"/base",depth+1,(*ancestors,id(operation)),primitive_base=True)
        records.append((local_name,operation,base_key,kind,depth))
        return local_name
    for index,item in enumerate(items):
        gate,annotation = item.metadata.get("gate"),item.metadata.get("annotated_operation")
        instruction = item.metadata.get("instruction_object")
        if sum(value is not None for value in (gate, annotation, instruction)) > 1:
            raise FormatValidationError("One invocation cannot have multiple operation owners.",format="qpy",version=13)
        operation = instruction if instruction is not None else annotation if annotation is not None else gate
        if operation is None and not isinstance(item, Measurement) and item.name == "csxdg":
            if (len(item.controls) != 1 or len(item.targets) != 1 or item.params
                    or set(item.metadata)-{"label", "operation_index"}):
                raise UnsupportedFeature("Only the canonical controlled SX inverse has this QPY definition.",format="qpy",version=13)
            limits.check("max_gate_expansion",budget.get("expanded",0)+3,format="qpy",version=13)
            limits.check("max_custom_definitions",budget.get("definitions",0)+1,format="qpy",version=13)
            from quantumbridge.core.gate_limits import current_gate_limits
            current_gate_limits().check("max_total_operations",3)
            # SX has eigenvalues 1/i, so three controlled SX operations give
            # its exact inverse without inventing an unsupported class field.
            body = Circuit(2)
            for _ in range(3): body.append("csx", [1], controls=[0])
            operation = Gate("csxdg",2,label=item.metadata.get("label"),definition=body)
            item = Operation(operation.name,item.wires,params=(),metadata={**item.metadata,"gate":operation})
            items[index] = item
        if operation is None: continue
        custom[index] = (register_operation(operation,_path+":"+str(index),_depth),operation)
    parts.append(struct.pack("!Q",len(records)))
    for local_name,operation,base_key,kind,depth in records:
        controlled,annotated = kind == b"c",kind == b"a"
        body = None if annotated else operation.definition
        nctrl,state,base_payload = 0,0,b""
        if controlled:
            nctrl,state = operation.num_ctrl_qubits,operation.ctrl_state
            closed = Circuit(operation.num_qubits)
            opened = [wire for wire in range(nctrl) if not (state>>wire)&1]
            for wire in opened: closed.x(wire)
            body = closed.compose(body)
            for wire in reversed(opened): body.x(wire)
            if any(item.name == "native_controlled" and "matrix" in item.metadata.get("controlled_base",{}).get("metadata",{}) for item in body.operations):
                # A numeric matrix-controlled definition has no standard
                # primitive opcode. Bound its dense export before allocation;
                # execution itself still uses the structural controlled body.
                from quantumbridge.core.standard_gates import UnitaryGate
                limits.check("max_numeric_elements",budget.get("numeric_elements",0)+(1<<body.num_qubits)**2,format="qpy",version=13)
                body = Circuit(body.num_qubits).append(UnitaryGate(body.to_gate().to_matrix()),range(body.num_qubits))
        if controlled or annotated:
            base = operation.base_op if annotated else operation.base_gate
            base_payload = _base_instruction_payload(base,base_key,limits,budget)
        definition = b"" if body is None else _circuit_bytes(body,limits,_budget=budget,_depth=depth+1,_path=local_name.decode())
        parts.extend((CUSTOM_INSTRUCTION.pack(len(local_name),kind,operation.num_qubits,0,body is not None,len(definition),nctrl,state,len(base_payload)),local_name,definition,base_payload))
    for index,item in enumerate(items):
        if isinstance(item,Measurement) and item.kind != "computational":
            raise UnsupportedFeature("Only computational-basis measurement has a supported QPY instruction.",format="qpy",version=13)
        op_name = "measure" if isinstance(item,Measurement) else item.name
        if index in custom:
            class_name,operation = custom[index]
            annotated = type(operation) is AnnotatedOperation
            from quantumbridge.core.standard_gates import invocation_params
            if item.name != operation.name or item.controls or len(item.targets) != operation.num_qubits or item.params != invocation_params(operation):
                raise FormatValidationError("Custom Gate invocation and definition disagree.",format="qpy",version=13)
            allowed = {"annotated_operation","operation_index"} if annotated else {"gate","label","operation_index"}
            if type(operation) is Instruction:
                allowed = {"instruction_object", "instruction_clbits", "label", "operation_index"}
                if item.metadata.get("instruction_clbits", ()):
                    raise UnsupportedFeature("Classical custom Instruction invocation fields are not implemented in QPY.",format="qpy",version=13)
            if set(item.metadata)-allowed:
                raise UnsupportedFeature("Custom Gate instruction metadata is not representable in QPY v13.",format="qpy",version=13)
            label = item.metadata.get("label","").encode()
            ctrl = operation.num_ctrl_qubits if isinstance(operation, ControlledGate) else 0
            state = operation.ctrl_state if isinstance(operation, ControlledGate) else 0
            params = _object_parameters(operation)
            parts.extend((INSTRUCTION.pack(len(class_name),len(label),len(params),operation.num_qubits,0,0,0,0,ctrl,state),class_name,label))
            parts.extend(struct.pack("!cI",b"q",wire) for wire in item.targets)
            for value in params:
                kind,payload = _modifier_value(value,limits,budget) if annotated else _parameter_value(value,limits,budget=budget)
                parts.extend((VALUE.pack(kind,len(payload)),payload))
            continue
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
            kind,payload = _parameter_value(value,limits,budget=budget)
            parts.extend((VALUE.pack(kind,len(payload)),payload))
    parts.extend((struct.pack("!H",0),LAYOUT.pack(b"\x00",-1,-1,-1,0,-1)))
    result = b"".join(parts)
    limits.check("max_input_bytes",len(result),format="qpy",version=13)
    return result


def qpy_dumps(circuits, *, version=13, limits=None):
    if version != 13: raise UnsupportedVersion("Only the tested QPY version 13 is supported.",format="qpy",version=version)
    from quantumbridge.core.symbolic_limits import symbolic_serialization_limits
    limits = symbolic_serialization_limits(limits)
    from itertools import islice
    circuits = [circuits] if isinstance(circuits,Circuit) else list(islice(iter(circuits),limits.max_circuits+1))
    limits.check("max_circuits",len(circuits),format="qpy",version=13)
    parts = BoundedParts(limits,"qpy")
    parts.extend((FILE_HEADER.pack(b"QISKIT",13,0,0,0,len(circuits),b"p"),b"q"))
    try:
        budget = {}
        for index,circuit in enumerate(circuits):
            parts.append(_circuit_bytes(circuit,limits,_budget=budget,_path=str(index)))
    except (struct.error,OverflowError,RecursionError) as exc:
        raise FormatValidationError("Object fields exceed supported binary lengths or nesting.",format="qpy",version=13) from exc
    result = b"".join(parts)
    limits.check("max_input_bytes",len(result),format="qpy",version=13)
    return result


def qpy_loads(data, *, limits=None):
    from quantumbridge.core.symbolic_limits import symbolic_serialization_limits
    limits = symbolic_serialization_limits(limits)
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
